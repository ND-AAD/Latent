// rhino_plugin/Geometry/RegionManager.cs
using System;
using System.Collections.Generic;
using System.Linq;
using Rhino;
using Rhino.Geometry;
using Latent.Analysis;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// Manages the collection of regions, edges, and vertices for an analysis session.
    /// Provides state management, selection tracking, pin/unpin operations, and undo integration.
    /// </summary>
    /// <remarks>
    /// <para>
    /// The RegionManager is the central state container for all geometry elements.
    /// It maintains three collections (Regions, Edges, Vertices) and handles:
    /// </para>
    /// <list type="bullet">
    /// <item><description>Loading analysis results from the Python service</description></item>
    /// <item><description>Preserving pinned elements across reanalysis</description></item>
    /// <item><description>Selection management (single selection, mutually exclusive)</description></item>
    /// <item><description>State mutations (move, pin, revert) with undo support</description></item>
    /// <item><description>Change notification via the Changed event</description></item>
    /// </list>
    /// </remarks>
    /// <example>
    /// <code>
    /// var manager = new RegionManager();
    /// manager.UpdateFromAnalysis(analysisResult);
    /// manager.SelectVertex("v0");
    /// manager.SetPinned("v0", true);
    /// manager.MoveVertex("v1", newPosition);
    /// </code>
    /// </example>
    public class RegionManager
    {
        private readonly Dictionary<string, Region> _regions = new();
        private readonly Dictionary<string, Edge> _edges = new();
        private readonly Dictionary<string, Vertex> _vertices = new();
        private readonly HashSet<string> _selectedIds = new();

        public event EventHandler? Changed;

        public IReadOnlyCollection<Region> Regions => _regions.Values;
        public IReadOnlyCollection<Edge> Edges => _edges.Values;
        public IReadOnlyCollection<Vertex> Vertices => _vertices.Values;

        /// <summary>
        /// Clear all data.
        /// </summary>
        public void Clear()
        {
            _regions.Clear();
            _edges.Clear();
            _vertices.Clear();
            _selectedIds.Clear();
            OnChanged();
        }

        /// <summary>
        /// Update from analysis result.
        /// </summary>
        public void UpdateFromAnalysis(AnalysisResultData data)
        {
            // Clear existing non-pinned elements
            var pinnedVertices = _vertices.Values.Where(v => v.IsPinned).ToDictionary(v => v.Id);
            var pinnedEdges = _edges.Values.Where(e => e.IsPinned).ToDictionary(e => e.Id);
            var pinnedRegions = _regions.Values.Where(r => r.IsPinned).ToDictionary(r => r.Id);

            _vertices.Clear();
            _edges.Clear();
            _regions.Clear();

            // Add vertices from analysis
            foreach (var vData in data.Vertices)
            {
                if (pinnedVertices.TryGetValue(vData.Id, out var pinned))
                {
                    _vertices[vData.Id] = pinned;
                }
                else
                {
                    _vertices[vData.Id] = Vertex.FromData(vData);
                }
            }

            // Add edges from analysis
            foreach (var eData in data.Edges)
            {
                if (pinnedEdges.TryGetValue(eData.Id, out var pinned))
                {
                    _edges[eData.Id] = pinned;
                }
                else
                {
                    var edge = Edge.FromData(eData);
                    edge.Vertices = eData.VertexIds
                        .Where(id => _vertices.ContainsKey(id))
                        .Select(id => _vertices[id])
                        .ToList();
                    _edges[eData.Id] = edge;
                }
            }

            // Add regions from analysis
            foreach (var rData in data.Regions)
            {
                if (pinnedRegions.TryGetValue(rData.Id, out var pinned))
                {
                    _regions[rData.Id] = pinned;
                }
                else
                {
                    var region = Region.FromData(rData);
                    region.BoundaryEdges = rData.BoundaryEdgeIds
                        .Where(id => _edges.ContainsKey(id))
                        .Select(id => _edges[id])
                        .ToList();
                    _regions[rData.Id] = region;
                }
            }

            OnChanged();
        }

        #region Lookup

        public Vertex? GetVertex(string id) =>
            _vertices.TryGetValue(id, out var v) ? v : null;

        public Edge? GetEdge(string id) =>
            _edges.TryGetValue(id, out var e) ? e : null;

        public Region? GetRegion(string id) =>
            _regions.TryGetValue(id, out var r) ? r : null;

        public IGeometryElement? GetElement(string id)
        {
            if (_vertices.TryGetValue(id, out var v)) return v;
            if (_edges.TryGetValue(id, out var e)) return e;
            if (_regions.TryGetValue(id, out var r)) return r;
            return null;
        }

        /// <summary>
        /// Find the region containing the given parametric point.
        /// Uses winding number algorithm for point-in-polygon test in parametric space.
        /// </summary>
        /// <param name="faceId">The SubD face ID</param>
        /// <param name="u">U parameter [0,1]</param>
        /// <param name="v">V parameter [0,1]</param>
        /// <returns>The containing region, or null if not found</returns>
        public Region? FindRegionContaining(int faceId, float u, float v)
        {
            var testPoint = new ParametricPoint(faceId, u, v);
            return FindRegionContaining(testPoint);
        }

        /// <summary>
        /// Find the region containing the given parametric point.
        /// </summary>
        public Region? FindRegionContaining(ParametricPoint param)
        {
            if (!param.IsValid)
                return null;

            foreach (var region in _regions.Values)
            {
                if (RegionContainsPoint(region, param))
                    return region;
            }

            return null;
        }

        /// <summary>
        /// Test if a region contains a parametric point using winding number algorithm.
        /// </summary>
        private bool RegionContainsPoint(Region region, ParametricPoint testPoint)
        {
            if (region.BoundaryEdges.Count == 0)
                return false;

            // Collect all boundary vertices in order
            var boundaryPoints = new List<ParametricPoint>();
            foreach (var edge in region.BoundaryEdges)
            {
                foreach (var vertex in edge.Vertices)
                {
                    // Only include vertices on the same face for accurate 2D test
                    // For cross-face regions, this is an approximation
                    boundaryPoints.Add(vertex.Position);
                }
            }

            if (boundaryPoints.Count < 3)
                return false;

            // Filter to vertices on the same face as test point for 2D winding number
            var sameFacePoints = boundaryPoints
                .Where(p => p.FaceId == testPoint.FaceId)
                .ToList();

            if (sameFacePoints.Count < 3)
            {
                // Region doesn't have enough vertices on this face
                // Fall back to checking if test point's face has any region vertices
                return boundaryPoints.Any(p => p.FaceId == testPoint.FaceId);
            }

            // Winding number algorithm for point-in-polygon
            return CalculateWindingNumber(testPoint, sameFacePoints) != 0;
        }

        /// <summary>
        /// Calculate winding number of a point relative to a polygon.
        /// Non-zero winding number means point is inside.
        /// </summary>
        private int CalculateWindingNumber(ParametricPoint point, List<ParametricPoint> polygon)
        {
            int windingNumber = 0;
            int n = polygon.Count;

            for (int i = 0; i < n; i++)
            {
                var p1 = polygon[i];
                var p2 = polygon[(i + 1) % n];

                if (p1.V <= point.V)
                {
                    if (p2.V > point.V)
                    {
                        // Upward crossing
                        if (IsLeft(p1, p2, point) > 0)
                            windingNumber++;
                    }
                }
                else
                {
                    if (p2.V <= point.V)
                    {
                        // Downward crossing
                        if (IsLeft(p1, p2, point) < 0)
                            windingNumber--;
                    }
                }
            }

            return windingNumber;
        }

        /// <summary>
        /// Test if point is left of, on, or right of an infinite line.
        /// Returns: >0 for left, 0 for on, <0 for right
        /// </summary>
        private double IsLeft(ParametricPoint p0, ParametricPoint p1, ParametricPoint p2)
        {
            return (p1.U - p0.U) * (p2.V - p0.V) - (p2.U - p0.U) * (p1.V - p0.V);
        }

        [Obsolete("Use FindRegionContaining instead")]
        public Region? FindRegionAt(ParametricPoint param)
        {
            return FindRegionContaining(param);
        }

        public Edge? FindNearestEdge(ParametricPoint param)
        {
            // TODO: Implement proper proximity test
            return _edges.Values.FirstOrDefault();
        }

        public Vertex? FindNearestVertex(ParametricPoint param)
        {
            // TODO: Implement proper proximity test
            return _vertices.Values.FirstOrDefault();
        }

        #endregion

        #region Selection

        public void SelectRegion(string id)
        {
            ClearSelection();
            if (_regions.TryGetValue(id, out var region))
            {
                region.IsSelected = true;
                _selectedIds.Add(id);
            }
            OnChanged();
        }

        public void SelectEdge(string id)
        {
            ClearSelection();
            if (_edges.TryGetValue(id, out var edge))
            {
                edge.IsSelected = true;
                _selectedIds.Add(id);
            }
            OnChanged();
        }

        public void SelectVertex(string id)
        {
            ClearSelection();
            if (_vertices.TryGetValue(id, out var vertex))
            {
                vertex.IsSelected = true;
                _selectedIds.Add(id);
            }
            OnChanged();
        }

        public void ClearSelection()
        {
            foreach (var id in _selectedIds)
            {
                var element = GetElement(id);
                if (element != null)
                {
                    element.IsSelected = false;
                }
            }
            _selectedIds.Clear();
        }

        public List<IGeometryElement> GetSelection()
        {
            return _selectedIds
                .Select(id => GetElement(id))
                .Where(e => e != null)
                .Cast<IGeometryElement>()
                .ToList();
        }

        #endregion

        #region Mutations

        /// <summary>
        /// Move a vertex to a new position by vertex ID.
        /// </summary>
        public void MoveVertex(string vertexId, ParametricPoint newPosition)
        {
            var vertex = GetVertex(vertexId);
            if (vertex == null) return;

            MoveVertexInternal(vertex, newPosition);
        }

        /// <summary>
        /// Move a vertex to a new position.
        /// </summary>
        public void MoveVertex(Vertex vertex, ParametricPoint newPosition)
        {
            if (vertex == null)
                throw new ArgumentNullException(nameof(vertex));

            // Verify vertex is managed by this RegionManager
            if (!_vertices.ContainsKey(vertex.Id))
                throw new ArgumentException("Vertex is not managed by this RegionManager", nameof(vertex));

            MoveVertexInternal(vertex, newPosition);
        }

        private void MoveVertexInternal(Vertex vertex, ParametricPoint newPosition)
        {
            var oldPosition = vertex.Position;

            // Register undo
            var undoEvent = new MoveVertexUndoEvent(vertex.Id, oldPosition, newPosition);
            RhinoUndoHelper.RegisterUndo(RhinoDoc.ActiveDoc, undoEvent, this);

            vertex.Position = newPosition;
            InvalidateGeometry();
            OnChanged();
        }

        public void SetPinned(string elementId, bool pinned)
        {
            var element = GetElement(elementId);
            if (element == null) return;

            var wasPinned = element.IsPinned;
            if (wasPinned == pinned) return;

            // Register undo
            var undoEvent = new PinUndoEvent(elementId, wasPinned);
            RhinoUndoHelper.RegisterUndo(RhinoDoc.ActiveDoc, undoEvent, this);

            element.IsPinned = pinned;
            OnChanged();
        }

        public void Revert(string elementId)
        {
            var element = GetElement(elementId);
            if (element == null) return;

            if (element is Vertex vertex)
            {
                RevertVertex(vertex);
            }
            else if (element is Region region)
            {
                RevertRegion(region);
            }
        }

        private void RevertVertex(Vertex vertex)
        {
            if (!vertex.CanRevert) return;

            var oldPosition = vertex.Position;

            // Register undo
            var undoEvent = new RevertVertexUndoEvent(vertex.Id, oldPosition);
            RhinoUndoHelper.RegisterUndo(RhinoDoc.ActiveDoc, undoEvent, this);

            vertex.Revert();
            InvalidateGeometry();
            OnChanged();
        }

        public void RevertEdgeCurveType(string edgeId)
        {
            var edge = GetEdge(edgeId);
            if (edge == null || !edge.CanRevert) return;

            // Remove vertices that were added during curve modification for this edge
            var curveModVertices = _vertices.Values
                .Where(v => v.CreatedBy == VertexOrigin.CurveModification && v.ParentEdgeId == edgeId)
                .ToList();

            foreach (var vertex in curveModVertices)
            {
                _vertices.Remove(vertex.Id);
                edge.VertexIds.Remove(vertex.Id);
            }

            // Rebuild vertex references on edge
            edge.Vertices = edge.VertexIds
                .Where(id => _vertices.ContainsKey(id))
                .Select(id => _vertices[id])
                .ToList();

            // TODO: Register undo for curve type change
            edge.RevertCurveType();
            InvalidateGeometry();
            OnChanged();
        }

        /// <summary>
        /// Change the curve type of an edge, potentially adding control vertices.
        /// </summary>
        /// <param name="edgeId">The edge to modify</param>
        /// <param name="newCurveType">The new curve type</param>
        /// <param name="newDegree">The new degree</param>
        /// <returns>List of vertex IDs added (if any)</returns>
        public List<string> ChangeEdgeCurveType(string edgeId, CurveType newCurveType, int newDegree)
        {
            var edge = GetEdge(edgeId);
            if (edge == null) return new List<string>();

            var addedVertexIds = new List<string>();

            // If increasing degree, we may need to add control points
            int currentPointCount = edge.VertexIds.Count;
            int requiredPoints = newDegree + 1; // For Bezier: degree + 1 control points

            if (requiredPoints > currentPointCount)
            {
                // Add intermediate vertices
                int pointsToAdd = requiredPoints - currentPointCount;

                // Interpolate positions along the edge
                for (int i = 0; i < pointsToAdd; i++)
                {
                    float t = (float)(i + 1) / (pointsToAdd + 1);
                    var newPosition = InterpolateEdgePosition(edge, t);

                    var vertexId = $"{edgeId}_cv{i}";
                    var newVertex = new Vertex(
                        vertexId,
                        newPosition,
                        newPosition,
                        VertexOrigin.CurveModification,
                        edgeId // Track parent edge
                    );

                    _vertices[vertexId] = newVertex;
                    addedVertexIds.Add(vertexId);

                    // Insert into edge's vertex list at appropriate position
                    int insertIndex = Math.Min((int)((currentPointCount - 1) * t) + 1, edge.VertexIds.Count);
                    edge.VertexIds.Insert(insertIndex, vertexId);
                }

                // Rebuild vertex references
                edge.Vertices = edge.VertexIds
                    .Where(id => _vertices.ContainsKey(id))
                    .Select(id => _vertices[id])
                    .ToList();
            }

            edge.CurveType = newCurveType;
            edge.Degree = newDegree;
            edge.IncrementVersion();

            InvalidateGeometry();
            OnChanged();

            return addedVertexIds;
        }

        /// <summary>
        /// Interpolate a position along an edge based on parameter t.
        /// </summary>
        private ParametricPoint InterpolateEdgePosition(Edge edge, float t)
        {
            if (edge.Vertices.Count < 2)
                return edge.Vertices.FirstOrDefault()?.Position ?? new ParametricPoint(0, 0, 0);

            // Simple linear interpolation for now
            int segmentIndex = (int)(t * (edge.Vertices.Count - 1));
            segmentIndex = Math.Min(segmentIndex, edge.Vertices.Count - 2);

            var v1 = edge.Vertices[segmentIndex];
            var v2 = edge.Vertices[segmentIndex + 1];

            float localT = (t * (edge.Vertices.Count - 1)) - segmentIndex;

            return new ParametricPoint(
                v1.Position.FaceId,  // Assume same face for simplicity
                v1.Position.U + (v2.Position.U - v1.Position.U) * localT,
                v1.Position.V + (v2.Position.V - v1.Position.V) * localT
            );
        }

        public void RevertEdgeFully(string edgeId)
        {
            var edge = GetEdge(edgeId);
            if (edge == null || !edge.CanRevert) return;

            // Revert curve type
            edge.RevertCurveType();

            // Revert all vertices
            foreach (var vertex in edge.Vertices)
            {
                if (vertex.CanRevert)
                {
                    vertex.Revert();
                }
            }

            InvalidateGeometry();
            OnChanged();
        }

        private void RevertRegion(Region region)
        {
            if (!region.CanRevert) return;

            // Revert all edges (fully)
            foreach (var edge in region.BoundaryEdges)
            {
                if (edge.CanRevert)
                {
                    RevertEdgeFully(edge.Id);
                }
            }
        }

        #endregion

        public void InvalidateGeometry()
        {
            foreach (var region in _regions.Values)
            {
                region.InvalidateCache();
            }
        }

        protected virtual void OnChanged()
        {
            Changed?.Invoke(this, EventArgs.Empty);
        }
    }
}
