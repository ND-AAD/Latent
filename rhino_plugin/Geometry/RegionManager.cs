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
    /// Manages regions, edges, and vertices for the current analysis session.
    /// </summary>
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

        public Region? FindRegionAt(ParametricPoint param)
        {
            // TODO: Implement proper point-in-region test
            // For now, return first region (placeholder)
            return _regions.Values.FirstOrDefault();
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

        public void MoveVertex(string vertexId, ParametricPoint newPosition)
        {
            var vertex = GetVertex(vertexId);
            if (vertex == null) return;

            var oldPosition = vertex.Position;

            // Register undo
            var undoEvent = new MoveVertexUndoEvent(vertexId, oldPosition, newPosition);
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

            // TODO: Register undo for curve type change
            edge.RevertCurveType();
            InvalidateGeometry();
            OnChanged();
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
