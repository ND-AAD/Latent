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
        public string JsonRpc { get; set; } = "2.0";

        [JsonPropertyName("result")]
        public T? Result { get; set; }

        [JsonPropertyName("error")]
        public JsonRpcError? Error { get; set; }

        [JsonPropertyName("id")]
        public string Id { get; set; } = "";

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
