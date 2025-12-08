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
