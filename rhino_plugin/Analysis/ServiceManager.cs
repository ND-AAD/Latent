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
        private Process? _process;
        private readonly string _pythonPath;
        private readonly string _servicePath;
        private readonly int _port;
        private bool _disposed;

        public ServiceManager(
            string pythonPath = "python3",
            string? servicePath = null,
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
                    _process.Kill();
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
