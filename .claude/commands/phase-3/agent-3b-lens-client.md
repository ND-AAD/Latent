# Agent 3B: Analysis Service Client

## Objective

Create C# client for communicating with the Python analysis service via JSON-RPC.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `analysis_service/protocol.py` - JSON-RPC protocol definitions
- `analysis_service/server.py` - server endpoints
- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - client design

## Files to Create

1. `rhino_plugin/Analysis/Protocol.cs` - JSON-RPC data classes
2. `rhino_plugin/Analysis/LensClient.cs` - HTTP client for analysis service
3. `rhino_plugin/Analysis/ServiceManager.cs` - Python subprocess management
4. `rhino_plugin/Analysis/AnalysisResult.cs` - Result data structures
5. `rhino_plugin/Tests/LensClientTests.cs` - Unit tests

## Tasks

### 1. Create Protocol.cs

```csharp
// rhino_plugin/Analysis/Protocol.cs
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Latent.Analysis
{
    /// <summary>
    /// JSON-RPC 2.0 request.
    /// </summary>
    public class JsonRpcRequest
    {
        [JsonPropertyName("jsonrpc")]
        public string JsonRpc { get; set; } = "2.0";

        [JsonPropertyName("method")]
        public string Method { get; set; }

        [JsonPropertyName("params")]
        public object Params { get; set; }

        [JsonPropertyName("id")]
        public string Id { get; set; }

        public static JsonRpcRequest Create(string method, object parameters)
        {
            return new JsonRpcRequest
            {
                Method = method,
                Params = parameters,
                Id = System.Guid.NewGuid().ToString()
            };
        }
    }

    /// <summary>
    /// JSON-RPC 2.0 response.
    /// </summary>
    public class JsonRpcResponse<T>
    {
        [JsonPropertyName("jsonrpc")]
        public string JsonRpc { get; set; }

        [JsonPropertyName("result")]
        public T Result { get; set; }

        [JsonPropertyName("error")]
        public JsonRpcError Error { get; set; }

        [JsonPropertyName("id")]
        public string Id { get; set; }

        public bool IsSuccess => Error == null;
    }

    /// <summary>
    /// JSON-RPC error.
    /// </summary>
    public class JsonRpcError
    {
        [JsonPropertyName("code")]
        public int Code { get; set; }

        [JsonPropertyName("message")]
        public string Message { get; set; }
    }

    /// <summary>
    /// Control cage for analysis.
    /// </summary>
    public class ControlCage
    {
        [JsonPropertyName("vertices")]
        public List<List<double>> Vertices { get; set; } = new();

        [JsonPropertyName("faces")]
        public List<List<int>> Faces { get; set; } = new();

        [JsonPropertyName("creases")]
        public List<List<double>> Creases { get; set; } = new();
    }

    /// <summary>
    /// Initialize request parameters.
    /// </summary>
    public class InitializeParams
    {
        [JsonPropertyName("cage")]
        public ControlCage Cage { get; set; }
    }

    /// <summary>
    /// Analyze request parameters.
    /// </summary>
    public class AnalyzeParams
    {
        [JsonPropertyName("lens")]
        public string Lens { get; set; }

        [JsonPropertyName("params")]
        public Dictionary<string, object> Parameters { get; set; } = new();

        [JsonPropertyName("pinned_regions")]
        public List<string> PinnedRegions { get; set; } = new();
    }

    /// <summary>
    /// Ping response.
    /// </summary>
    public class PingResult
    {
        [JsonPropertyName("status")]
        public string Status { get; set; }

        [JsonPropertyName("version")]
        public string Version { get; set; }
    }

    /// <summary>
    /// Initialize response.
    /// </summary>
    public class InitializeResult
    {
        [JsonPropertyName("status")]
        public string Status { get; set; }
    }
}
```

### 2. Create AnalysisResult.cs

```csharp
// rhino_plugin/Analysis/AnalysisResult.cs
using System.Collections.Generic;
using System.Text.Json.Serialization;
using Latent.Interop;

namespace Latent.Analysis
{
    /// <summary>
    /// A boundary curve from analysis.
    /// </summary>
    public class BoundaryCurveData
    {
        [JsonPropertyName("control_points")]
        public List<List<double>> ControlPoints { get; set; } = new();

        [JsonPropertyName("type")]
        public string Type { get; set; } = "bezier";

        [JsonPropertyName("degree")]
        public int Degree { get; set; } = 3;

        /// <summary>
        /// Convert to parametric points for SurfaceCurve creation.
        /// </summary>
        public List<ParametricPoint> ToParametricPoints()
        {
            var points = new List<ParametricPoint>();
            foreach (var cp in ControlPoints)
            {
                if (cp.Count >= 3)
                {
                    points.Add(new ParametricPoint((int)cp[0], cp[1], cp[2]));
                }
            }
            return points;
        }
    }

    /// <summary>
    /// A vertex from analysis.
    /// </summary>
    public class VertexData
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("position")]
        public List<double> Position { get; set; }

        [JsonPropertyName("implicit_position")]
        public List<double> ImplicitPosition { get; set; }

        [JsonPropertyName("created_by")]
        public string CreatedBy { get; set; }

        [JsonPropertyName("is_pinned")]
        public bool IsPinned { get; set; }

        public ParametricPoint GetPosition()
        {
            if (Position?.Count >= 3)
            {
                return new ParametricPoint((int)Position[0], Position[1], Position[2]);
            }
            return new ParametricPoint(-1, 0, 0);
        }

        public ParametricPoint? GetImplicitPosition()
        {
            if (ImplicitPosition?.Count >= 3)
            {
                return new ParametricPoint(
                    (int)ImplicitPosition[0],
                    ImplicitPosition[1],
                    ImplicitPosition[2]
                );
            }
            return null;
        }
    }

    /// <summary>
    /// An edge from analysis.
    /// </summary>
    public class EdgeData
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("vertex_ids")]
        public List<string> VertexIds { get; set; } = new();

        [JsonPropertyName("curve_type")]
        public string CurveType { get; set; } = "bezier";

        [JsonPropertyName("degree")]
        public int Degree { get; set; } = 3;

        [JsonPropertyName("is_pinned")]
        public bool IsPinned { get; set; }
    }

    /// <summary>
    /// A region from analysis.
    /// </summary>
    public class RegionData
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("boundary_edge_ids")]
        public List<string> BoundaryEdgeIds { get; set; } = new();

        [JsonPropertyName("boundary_curves")]
        public List<BoundaryCurveData> BoundaryCurves { get; set; } = new();

        [JsonPropertyName("unity_principle")]
        public string UnityPrinciple { get; set; }

        [JsonPropertyName("resonance_score")]
        public double ResonanceScore { get; set; }

        [JsonPropertyName("is_pinned")]
        public bool IsPinned { get; set; }

        [JsonPropertyName("is_implicit")]
        public bool IsImplicit { get; set; } = true;
    }

    /// <summary>
    /// Complete analysis result.
    /// </summary>
    public class AnalysisResultData
    {
        [JsonPropertyName("regions")]
        public List<RegionData> Regions { get; set; } = new();

        [JsonPropertyName("vertices")]
        public List<VertexData> Vertices { get; set; } = new();

        [JsonPropertyName("edges")]
        public List<EdgeData> Edges { get; set; } = new();
    }
}
```

### 3. Create ServiceManager.cs

```csharp
// rhino_plugin/Analysis/ServiceManager.cs
using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

namespace Latent.Analysis
{
    /// <summary>
    /// Manages the Python analysis service subprocess.
    /// </summary>
    public class ServiceManager : IDisposable
    {
        private Process _process;
        private readonly string _pythonPath;
        private readonly string _servicePath;
        private readonly int _port;
        private bool _disposed;

        public ServiceManager(
            string pythonPath = "python",
            string servicePath = null,
            int port = 5555)
        {
            _pythonPath = pythonPath;
            _servicePath = servicePath ?? FindServicePath();
            _port = port;
        }

        public int Port => _port;
        public bool IsRunning => _process != null && !_process.HasExited;

        /// <summary>
        /// Start the analysis service.
        /// </summary>
        public async Task StartAsync(CancellationToken cancellationToken = default)
        {
            if (IsRunning)
            {
                return;
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = _pythonPath,
                Arguments = $"-m analysis_service --port {_port}",
                WorkingDirectory = _servicePath,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            _process = Process.Start(startInfo);

            // Wait for service to be ready
            await WaitForServiceAsync(cancellationToken);
        }

        /// <summary>
        /// Stop the analysis service.
        /// </summary>
        public void Stop()
        {
            if (_process != null && !_process.HasExited)
            {
                try
                {
                    _process.Kill(entireProcessTree: true);
                }
                catch
                {
                    // Ignore errors during shutdown
                }
                _process.Dispose();
                _process = null;
            }
        }

        /// <summary>
        /// Wait for the service to respond to ping.
        /// </summary>
        private async Task WaitForServiceAsync(
            CancellationToken cancellationToken,
            int maxRetries = 30,
            int delayMs = 200)
        {
            using var httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromSeconds(2);

            var request = JsonRpcRequest.Create("ping", new { });
            var url = $"http://localhost:{_port}";

            for (int i = 0; i < maxRetries; i++)
            {
                cancellationToken.ThrowIfCancellationRequested();

                try
                {
                    var content = System.Text.Json.JsonSerializer.Serialize(request);
                    var response = await httpClient.PostAsync(
                        url,
                        new StringContent(content, System.Text.Encoding.UTF8, "application/json"),
                        cancellationToken
                    );

                    if (response.IsSuccessStatusCode)
                    {
                        var body = await response.Content.ReadAsStringAsync();
                        if (body.Contains("\"ok\""))
                        {
                            return; // Service is ready
                        }
                    }
                }
                catch (HttpRequestException)
                {
                    // Service not ready yet
                }
                catch (TaskCanceledException)
                {
                    // Timeout, service not ready
                }

                await Task.Delay(delayMs, cancellationToken);
            }

            throw new TimeoutException("Analysis service failed to start");
        }

        /// <summary>
        /// Find the analysis service directory.
        /// </summary>
        private static string FindServicePath()
        {
            // Look relative to the plugin assembly
            var assemblyPath = typeof(ServiceManager).Assembly.Location;
            var dir = Path.GetDirectoryName(assemblyPath);

            // Walk up to find analysis_service directory
            while (!string.IsNullOrEmpty(dir))
            {
                var candidate = Path.Combine(dir, "analysis_service");
                if (Directory.Exists(candidate))
                {
                    return dir;
                }
                dir = Path.GetDirectoryName(dir);
            }

            throw new DirectoryNotFoundException("Could not find analysis_service directory");
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
                    Stop();
                }
                _disposed = true;
            }
        }

        ~ServiceManager()
        {
            Dispose(false);
        }
    }
}
```

### 4. Create LensClient.cs

```csharp
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
        private readonly ServiceManager _serviceManager;
        private readonly int _port;
        private bool _disposed;

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        public LensClient(int port = 5555, ServiceManager serviceManager = null)
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
            Dictionary<string, object> parameters = null,
            List<string> pinnedRegions = null,
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
        /// </summary>
        private static ControlCage ExtractControlCage(SubD subd)
        {
            var cage = new ControlCage();
            var vertexMap = new Dictionary<uint, int>();

            // Extract vertices
            int idx = 0;
            foreach (var v in subd.Vertices)
            {
                var pt = v.ControlNetPoint;
                cage.Vertices.Add(new List<double> { pt.X, pt.Y, pt.Z });
                vertexMap[v.Id] = idx++;
            }

            // Extract faces
            foreach (var f in subd.Faces)
            {
                var faceVerts = new List<int>();
                foreach (var vid in f.VertexIds)
                {
                    faceVerts.Add(vertexMap[vid]);
                }
                cage.Faces.Add(faceVerts);
            }

            // Extract creases
            foreach (var e in subd.Edges)
            {
                if (e.IsCrease)
                {
                    cage.Creases.Add(new List<double>
                    {
                        vertexMap[e.Vertex(0).Id],
                        vertexMap[e.Vertex(1).Id],
                        e.CreaseWeight
                    });
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
```

### 5. Create LensClientTests.cs

```csharp
// rhino_plugin/Tests/LensClientTests.cs
using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Analysis;

namespace Latent.Tests
{
    [TestFixture]
    public class LensClientTests
    {
        private ServiceManager _serviceManager;
        private LensClient _client;

        [OneTimeSetUp]
        public async Task SetUp()
        {
            // Start analysis service for tests
            try
            {
                _serviceManager = new ServiceManager();
                await _serviceManager.StartAsync();
                _client = new LensClient(serviceManager: _serviceManager);
            }
            catch
            {
                // Service may not be available in CI
            }
        }

        [OneTimeTearDown]
        public void TearDown()
        {
            _client?.Dispose();
            _serviceManager?.Dispose();
        }

        [Test]
        public async Task Ping_ReturnsOk()
        {
            if (_client == null)
            {
                Assert.Ignore("Analysis service not available");
            }

            var result = await _client.PingAsync();
            Assert.IsTrue(result);
        }

        [Test]
        public async Task Initialize_Succeeds()
        {
            if (_client == null)
            {
                Assert.Ignore("Analysis service not available");
            }

            // Create a simple SubD
            var box = new Box(
                Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1)
            );
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            await _client.InitializeAsync(subd);
            // No exception = success
        }

        [Test]
        public async Task AnalyzeDifferential_ReturnsResult()
        {
            if (_client == null)
            {
                Assert.Ignore("Analysis service not available");
            }

            // Initialize first
            var box = new Box(
                Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1)
            );
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);
            await _client.InitializeAsync(subd);

            // Run analysis
            var result = await _client.AnalyzeDifferentialAsync(0.3);

            Assert.IsNotNull(result);
            // Result may be empty if lens not fully implemented yet
        }

        [Test]
        public void ControlCage_ExtractsCorrectly()
        {
            var box = new Box(
                Plane.WorldXY,
                new Interval(-1, 1),
                new Interval(-1, 1),
                new Interval(-1, 1)
            );
            var mesh = Mesh.CreateFromBox(box, 1, 1, 1);
            var subd = SubD.CreateFromMesh(mesh);

            // Use reflection to test private method
            var method = typeof(LensClient).GetMethod(
                "ExtractControlCage",
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static
            );

            var cage = (ControlCage)method.Invoke(null, new object[] { subd });

            Assert.AreEqual(8, cage.Vertices.Count); // Box has 8 vertices
            Assert.AreEqual(6, cage.Faces.Count);    // Box has 6 faces
        }
    }
}
```

## Success Criteria

- [ ] Protocol classes serialize/deserialize correctly
- [ ] ServiceManager starts and stops Python process
- [ ] LensClient pings successfully
- [ ] LensClient.InitializeAsync works with SubD
- [ ] LensClient.AnalyzeAsync returns valid results
- [ ] All tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build the plugin
dotnet build

# Run tests
dotnet test
```

## Do Not Modify

- Files in `rhino_plugin/Interop/` (Agent 3A's domain)
- Files in `rhino_plugin/Commands/` (Agent 3C's domain)
- Files in `rhino_plugin/Geometry/` (Agent 3D's domain)
- Files in `analysis_service/` (Phase 2)

## Skills to Use

- `superpowers:verification-before-completion` - verify client works end-to-end

## Report

When complete, provide:
1. Build output
2. Test results
3. Sample JSON-RPC request/response
