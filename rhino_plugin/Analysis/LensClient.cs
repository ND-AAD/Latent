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
        /// NOTE: This is a simplified extraction that works with RhinoCommon 8.
        /// For a production implementation, Agent 3A should implement a proper C++ binding.
        /// </summary>
        private static ControlCage ExtractControlCage(SubD subd)
        {
            var cage = new ControlCage();

            // For now, create a simple placeholder cage
            // This will be replaced by proper C++ extraction in Agent 3A's domain
            // The actual topology extraction should be done via the C++ core

            // Add a warning that this is temporary
            System.Diagnostics.Debug.WriteLine(
                "WARNING: Using placeholder ExtractControlCage. " +
                "This should be replaced with proper C++ core extraction."
            );

            // Return minimal valid cage structure
            // The Python service will need valid data, so we provide a simple box
            cage.Vertices.Add(new List<double> { -1, -1, -1 });
            cage.Vertices.Add(new List<double> {  1, -1, -1 });
            cage.Vertices.Add(new List<double> {  1,  1, -1 });
            cage.Vertices.Add(new List<double> { -1,  1, -1 });
            cage.Vertices.Add(new List<double> { -1, -1,  1 });
            cage.Vertices.Add(new List<double> {  1, -1,  1 });
            cage.Vertices.Add(new List<double> {  1,  1,  1 });
            cage.Vertices.Add(new List<double> { -1,  1,  1 });

            // Add faces (box)
            cage.Faces.Add(new List<int> { 0, 1, 2, 3 }); // bottom
            cage.Faces.Add(new List<int> { 4, 5, 6, 7 }); // top
            cage.Faces.Add(new List<int> { 0, 1, 5, 4 }); // front
            cage.Faces.Add(new List<int> { 2, 3, 7, 6 }); // back
            cage.Faces.Add(new List<int> { 0, 3, 7, 4 }); // left
            cage.Faces.Add(new List<int> { 1, 2, 6, 5 }); // right

            // TODO: Replace this placeholder with actual SubD topology extraction
            // This requires proper RhinoCommon API usage or delegation to C++ core

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
