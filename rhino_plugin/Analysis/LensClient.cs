// rhino_plugin/Analysis/LensClient.cs
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Rhino.Geometry;

namespace Latent.Analysis
{
    /// <summary>
    /// Client for the Python analysis service.
    /// </summary>
    public class LensClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly ServiceManager? _serviceManager;
        private readonly int _port;
        private bool _disposed;

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        public LensClient(int port = 5555, ServiceManager? serviceManager = null)
        {
            _port = port;
            _serviceManager = serviceManager;
            _httpClient = new HttpClient
            {
                BaseAddress = new Uri($"http://localhost:{port}"),
                Timeout = TimeSpan.FromSeconds(60)
            };
        }

        /// <summary>
        /// Start the analysis service if not already running.
        /// </summary>
        public async Task StartServiceAsync(CancellationToken cancellationToken = default)
        {
            if (_serviceManager != null)
            {
                await _serviceManager.StartAsync(cancellationToken);
            }
        }

        /// <summary>
        /// Ping the service to check availability.
        /// </summary>
        public async Task<bool> PingAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                var response = await SendRequestAsync<PingResult>(
                    "ping", new { }, cancellationToken
                );
                return response?.Status == "ok";
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Initialize the service with a SubD geometry.
        /// </summary>
        public async Task InitializeAsync(
            SubD subd,
            CancellationToken cancellationToken = default)
        {
            var cage = ExtractControlCage(subd);
            var parameters = new InitializeParams { Cage = cage };

            var result = await SendRequestAsync<InitializeResult>(
                "initialize", parameters, cancellationToken
            );

            if (result?.Status != "initialized")
            {
                throw new InvalidOperationException("Failed to initialize analysis service");
            }
        }

        /// <summary>
        /// Run lens analysis.
        /// </summary>
        public async Task<AnalysisResultData> AnalyzeAsync(
            string lensType,
            Dictionary<string, object>? parameters = null,
            List<string>? pinnedRegions = null,
            CancellationToken cancellationToken = default)
        {
            var analyzeParams = new AnalyzeParams
            {
                Lens = lensType,
                Parameters = parameters ?? new Dictionary<string, object>(),
                PinnedRegions = pinnedRegions ?? new List<string>()
            };

            return await SendRequestAsync<AnalysisResultData>(
                "analyze", analyzeParams, cancellationToken
            );
        }

        /// <summary>
        /// Run differential (curvature) lens analysis.
        /// </summary>
        public async Task<AnalysisResultData> AnalyzeDifferentialAsync(
            double curvatureTolerance = 0.3,
            CancellationToken cancellationToken = default)
        {
            var parameters = new Dictionary<string, object>
            {
                ["curvature_tolerance"] = curvatureTolerance
            };

            return await AnalyzeAsync("differential", parameters, null, cancellationToken);
        }

        /// <summary>
        /// Run spectral (eigenfunction) lens analysis.
        /// </summary>
        public async Task<AnalysisResultData> AnalyzeSpectralAsync(
            int numEigenfunctions = 3,
            CancellationToken cancellationToken = default)
        {
            var parameters = new Dictionary<string, object>
            {
                ["num_eigenfunctions"] = numEigenfunctions
            };

            return await AnalyzeAsync("spectral", parameters, null, cancellationToken);
        }

        /// <summary>
        /// Send a JSON-RPC request and parse the response.
        /// </summary>
        private async Task<T> SendRequestAsync<T>(
            string method,
            object parameters,
            CancellationToken cancellationToken)
        {
            var request = JsonRpcRequest.Create(method, parameters);
            var json = JsonSerializer.Serialize(request, JsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var httpResponse = await _httpClient.PostAsync("", content, cancellationToken);
            httpResponse.EnsureSuccessStatusCode();

            var responseBody = await httpResponse.Content.ReadAsStringAsync();
            var response = JsonSerializer.Deserialize<JsonRpcResponse<T>>(responseBody, JsonOptions);

            if (response?.Error != null)
            {
                throw new InvalidOperationException(
                    $"JSON-RPC error {response.Error.Code}: {response.Error.Message}"
                );
            }

            return response.Result;
        }

        /// <summary>
        /// Extract control cage from Rhino SubD.
        /// Uses RhinoCommon's SubD API to extract control net - NO mesh conversion.
        ///
        /// Note: RhinoCommon SubD uses linked-list iteration (.First/.Next pattern),
        /// not array-based access like meshes.
        /// </summary>
        private static ControlCage ExtractControlCage(SubD subd)
        {
            if (subd == null)
                throw new ArgumentNullException(nameof(subd));

            var cage = new ControlCage();

            // Build vertex index mapping: SubD vertex ID -> sequential index
            // SubD vertices use linked-list iteration: .First property, then .Next
            var vertexMap = new Dictionary<uint, int>();
            int idx = 0;

            SubDVertex? vertex = subd.Vertices.First;
            while (vertex != null)
            {
                // Use ControlNetPoint - exact control cage position (NOT limit surface)
                var pt = vertex.ControlNetPoint;
                cage.Vertices.Add(new List<double> { pt.X, pt.Y, pt.Z });
                vertexMap[vertex.Id] = idx++;
                vertex = vertex.Next;
            }

            // Extract face topology from control net
            // Use foreach which works with SubDFaceList's IEnumerable implementation
            foreach (SubDFace face in subd.Faces)
            {
                int edgeCount = face.EdgeCount;
                var faceVertexIndices = new List<int>();

                // Collect vertex IDs using the proper VertexAt API
                for (int i = 0; i < edgeCount; i++)
                {
                    var faceVertex = face.VertexAt(i);
                    if (faceVertex != null && vertexMap.TryGetValue(faceVertex.Id, out int vertexIndex))
                    {
                        faceVertexIndices.Add(vertexIndex);
                    }
                }

                cage.Faces.Add(faceVertexIndices);
            }

            // Extract crease edges
            // Use foreach which works with SubDEdgeList's IEnumerable implementation
            foreach (SubDEdge edge in subd.Edges)
            {
                // Check if edge is a crease using Tag property
                if (edge.Tag == SubDEdgeTag.Crease)
                {
                    // Get vertices at ends of edge using VertexFrom/VertexTo properties
                    var v0 = edge.VertexFrom;
                    var v1 = edge.VertexTo;

                    if (v0 != null && v1 != null &&
                        vertexMap.TryGetValue(v0.Id, out int idx0) &&
                        vertexMap.TryGetValue(v1.Id, out int idx1))
                    {
                        // Crease edges are sharp (weight 1.0)
                        cage.Creases.Add(new List<double> { idx0, idx1, 1.0 });
                    }
                }
            }

            return cage;
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    _httpClient.Dispose();
                }
                _disposed = true;
            }
        }

        ~LensClient()
        {
            Dispose(false);
        }
    }
}
