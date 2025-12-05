# Agent 3D: Data Model & State Management

## Objective

Create the region/vertex/edge data model and state management with Rhino undo integration.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-architecture-design.md` - data model spec
- `rhino_plugin/Analysis/AnalysisResult.cs` - analysis result structures

## Files to Create

1. `rhino_plugin/Geometry/Vertex.cs` - Vertex class
2. `rhino_plugin/Geometry/Edge.cs` - Edge class
3. `rhino_plugin/Geometry/Region.cs` - Region class
4. `rhino_plugin/Geometry/RegionManager.cs` - State management
5. `rhino_plugin/Geometry/UndoEvents.cs` - Rhino undo integration
6. `rhino_plugin/Geometry/IGeometryElement.cs` - Common interface
7. `rhino_plugin/Tests/RegionManagerTests.cs` - Unit tests

## Tasks

### 1. Create IGeometryElement.cs

```csharp
// rhino_plugin/Geometry/IGeometryElement.cs
namespace Latent.Geometry
{
    /// <summary>
    /// Common interface for geometry elements (vertices, edges, regions).
    /// </summary>
    public interface IGeometryElement
    {
        /// <summary>
        /// Unique identifier.
        /// </summary>
        string Id { get; }

        /// <summary>
        /// Whether this element is pinned (protected from changes).
        /// </summary>
        bool IsPinned { get; set; }

        /// <summary>
        /// Whether this element is at its implicit (lens-defined) state.
        /// </summary>
        bool IsImplicit { get; }

        /// <summary>
        /// Whether this element is currently selected.
        /// </summary>
        bool IsSelected { get; set; }

        /// <summary>
        /// Whether this element can be reverted to implicit state.
        /// </summary>
        bool CanRevert { get; }
    }
}
```

### 2. Create Vertex.cs

```csharp
// rhino_plugin/Geometry/Vertex.cs
using System;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// How this vertex was created.
    /// </summary>
    public enum VertexOrigin
    {
        Lens,              // Created by lens analysis
        CurveModification, // Added when changing curve degree
        UserAdded          // Explicitly added by user
    }

    /// <summary>
    /// A vertex in the region graph.
    /// </summary>
    public class Vertex : IGeometryElement
    {
        public string Id { get; }
        public ParametricPoint Position { get; set; }
        public ParametricPoint? ImplicitPosition { get; }
        public VertexOrigin CreatedBy { get; }
        public bool IsPinned { get; set; }
        public bool IsSelected { get; set; }

        public Vertex(
            string id,
            ParametricPoint position,
            ParametricPoint? implicitPosition = null,
            VertexOrigin createdBy = VertexOrigin.Lens)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            Position = position;
            ImplicitPosition = implicitPosition ?? position;
            CreatedBy = createdBy;
        }

        /// <summary>
        /// Whether the vertex is at its implicit position.
        /// </summary>
        public bool IsImplicit
        {
            get
            {
                if (!ImplicitPosition.HasValue)
                    return false;

                var imp = ImplicitPosition.Value;
                return Position.FaceId == imp.FaceId &&
                       Math.Abs(Position.U - imp.U) < 1e-6 &&
                       Math.Abs(Position.V - imp.V) < 1e-6;
            }
        }

        /// <summary>
        /// Whether this vertex can be reverted.
        /// </summary>
        public bool CanRevert
        {
            get
            {
                if (IsPinned) return false;
                if (CreatedBy == VertexOrigin.CurveModification) return false;
                if (!ImplicitPosition.HasValue) return false;
                return !IsImplicit;
            }
        }

        /// <summary>
        /// Revert this vertex to its implicit position.
        /// </summary>
        public void Revert()
        {
            if (!CanRevert)
                throw new InvalidOperationException("Cannot revert this vertex");

            Position = ImplicitPosition.Value;
        }

        /// <summary>
        /// Create from analysis data.
        /// </summary>
        public static Vertex FromData(Analysis.VertexData data)
        {
            var origin = data.CreatedBy switch
            {
                "lens" => VertexOrigin.Lens,
                "curve_modification" => VertexOrigin.CurveModification,
                "user_added" => VertexOrigin.UserAdded,
                _ => VertexOrigin.Lens
            };

            return new Vertex(
                data.Id,
                data.GetPosition(),
                data.GetImplicitPosition(),
                origin
            )
            {
                IsPinned = data.IsPinned
            };
        }
    }
}
```

### 3. Create Edge.cs

```csharp
// rhino_plugin/Geometry/Edge.cs
using System;
using System.Collections.Generic;
using System.Linq;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// An edge (boundary curve) in the region graph.
    /// </summary>
    public class Edge : IGeometryElement
    {
        public string Id { get; }
        public List<string> VertexIds { get; }
        public CurveType CurveType { get; set; }
        public int Degree { get; set; }
        public CurveType? ImplicitCurveType { get; }
        public int? ImplicitDegree { get; }
        public bool IsPinned { get; set; }
        public bool IsSelected { get; set; }

        // Reference to vertices (populated by RegionManager)
        public List<Vertex> Vertices { get; internal set; } = new();

        public Edge(
            string id,
            List<string> vertexIds,
            CurveType curveType = CurveType.Bezier,
            int degree = 3,
            CurveType? implicitCurveType = null,
            int? implicitDegree = null)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            VertexIds = vertexIds ?? throw new ArgumentNullException(nameof(vertexIds));
            CurveType = curveType;
            Degree = degree;
            ImplicitCurveType = implicitCurveType ?? curveType;
            ImplicitDegree = implicitDegree ?? degree;
        }

        /// <summary>
        /// Whether the edge is at its implicit curve type.
        /// </summary>
        public bool IsImplicit =>
            CurveType == ImplicitCurveType && Degree == ImplicitDegree;

        /// <summary>
        /// Whether this edge can be reverted.
        /// </summary>
        public bool CanRevert => !IsPinned && !IsImplicit;

        /// <summary>
        /// Revert only the curve type (keep vertex positions).
        /// </summary>
        public void RevertCurveType()
        {
            if (IsPinned)
                throw new InvalidOperationException("Cannot revert: edge is pinned");

            if (ImplicitCurveType.HasValue)
                CurveType = ImplicitCurveType.Value;

            if (ImplicitDegree.HasValue)
                Degree = ImplicitDegree.Value;
        }

        /// <summary>
        /// Get control points for curve creation.
        /// </summary>
        public List<ParametricPoint> GetControlPoints()
        {
            return Vertices.Select(v => v.Position).ToList();
        }

        /// <summary>
        /// Create from analysis data.
        /// </summary>
        public static Edge FromData(Analysis.EdgeData data)
        {
            var curveType = data.CurveType switch
            {
                "linear" => CurveType.Linear,
                "bezier" => CurveType.Bezier,
                "bspline" => CurveType.BSpline,
                _ => CurveType.Bezier
            };

            return new Edge(
                data.Id,
                data.VertexIds,
                curveType,
                data.Degree
            )
            {
                IsPinned = data.IsPinned
            };
        }
    }
}
```

### 4. Create Region.cs

```csharp
// rhino_plugin/Geometry/Region.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;

namespace Latent.Geometry
{
    /// <summary>
    /// A region bounded by edges.
    /// </summary>
    public class Region : IGeometryElement
    {
        public string Id { get; }
        public List<string> BoundaryEdgeIds { get; }
        public string UnityPrinciple { get; }
        public double ResonanceScore { get; }
        public bool IsPinned { get; set; }
        public bool IsSelected { get; set; }

        // Reference to edges (populated by RegionManager)
        public List<Edge> BoundaryEdges { get; internal set; } = new();

        // Cached geometry
        private Point3d? _centroid;
        private BoundingBox? _boundingBox;

        public Region(
            string id,
            List<string> boundaryEdgeIds,
            string unityPrinciple,
            double resonanceScore)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            BoundaryEdgeIds = boundaryEdgeIds ?? throw new ArgumentNullException(nameof(boundaryEdgeIds));
            UnityPrinciple = unityPrinciple ?? "";
            ResonanceScore = resonanceScore;
        }

        /// <summary>
        /// Whether all boundary elements are implicit.
        /// </summary>
        public bool IsImplicit =>
            BoundaryEdges.TrueForAll(e => e.IsImplicit);

        /// <summary>
        /// Whether this region can be reverted.
        /// </summary>
        public bool CanRevert => !IsPinned && !IsImplicit;

        /// <summary>
        /// Get or compute the region centroid.
        /// </summary>
        public Point3d Centroid
        {
            get => _centroid ?? Point3d.Origin;
            internal set => _centroid = value;
        }

        /// <summary>
        /// Get or compute the bounding box.
        /// </summary>
        public BoundingBox BoundingBox
        {
            get => _boundingBox ?? BoundingBox.Empty;
            internal set => _boundingBox = value;
        }

        /// <summary>
        /// Invalidate cached geometry (call after changes).
        /// </summary>
        public void InvalidateCache()
        {
            _centroid = null;
            _boundingBox = null;
        }

        /// <summary>
        /// Create from analysis data.
        /// </summary>
        public static Region FromData(Analysis.RegionData data)
        {
            return new Region(
                data.Id,
                data.BoundaryEdgeIds,
                data.UnityPrinciple,
                data.ResonanceScore
            )
            {
                IsPinned = data.IsPinned
            };
        }
    }
}
```

### 5. Create UndoEvents.cs

```csharp
// rhino_plugin/Geometry/UndoEvents.cs
using System;
using Rhino;
using Latent.Interop;

namespace Latent.Geometry
{
    /// <summary>
    /// Base class for undo events.
    /// </summary>
    public abstract class LatentUndoEvent
    {
        public abstract void Undo(RegionManager manager);
        public abstract void Redo(RegionManager manager);
        public abstract string Description { get; }
    }

    /// <summary>
    /// Undo event for moving a vertex.
    /// </summary>
    public class MoveVertexUndoEvent : LatentUndoEvent
    {
        private readonly string _vertexId;
        private readonly ParametricPoint _oldPosition;
        private readonly ParametricPoint _newPosition;

        public MoveVertexUndoEvent(string vertexId, ParametricPoint oldPos, ParametricPoint newPos)
        {
            _vertexId = vertexId;
            _oldPosition = oldPos;
            _newPosition = newPos;
        }

        public override string Description => $"Move vertex {_vertexId}";

        public override void Undo(RegionManager manager)
        {
            var vertex = manager.GetVertex(_vertexId);
            if (vertex != null)
            {
                vertex.Position = _oldPosition;
                manager.InvalidateGeometry();
            }
        }

        public override void Redo(RegionManager manager)
        {
            var vertex = manager.GetVertex(_vertexId);
            if (vertex != null)
            {
                vertex.Position = _newPosition;
                manager.InvalidateGeometry();
            }
        }
    }

    /// <summary>
    /// Undo event for pin/unpin operations.
    /// </summary>
    public class PinUndoEvent : LatentUndoEvent
    {
        private readonly string _elementId;
        private readonly bool _wasPinned;

        public PinUndoEvent(string elementId, bool wasPinned)
        {
            _elementId = elementId;
            _wasPinned = wasPinned;
        }

        public override string Description =>
            _wasPinned ? $"Unpin {_elementId}" : $"Pin {_elementId}";

        public override void Undo(RegionManager manager)
        {
            var element = manager.GetElement(_elementId);
            if (element != null)
            {
                element.IsPinned = _wasPinned;
            }
        }

        public override void Redo(RegionManager manager)
        {
            var element = manager.GetElement(_elementId);
            if (element != null)
            {
                element.IsPinned = !_wasPinned;
            }
        }
    }

    /// <summary>
    /// Undo event for revert operations.
    /// </summary>
    public class RevertVertexUndoEvent : LatentUndoEvent
    {
        private readonly string _vertexId;
        private readonly ParametricPoint _oldPosition;

        public RevertVertexUndoEvent(string vertexId, ParametricPoint oldPos)
        {
            _vertexId = vertexId;
            _oldPosition = oldPos;
        }

        public override string Description => $"Revert vertex {_vertexId}";

        public override void Undo(RegionManager manager)
        {
            var vertex = manager.GetVertex(_vertexId);
            if (vertex != null)
            {
                vertex.Position = _oldPosition;
                manager.InvalidateGeometry();
            }
        }

        public override void Redo(RegionManager manager)
        {
            var vertex = manager.GetVertex(_vertexId);
            if (vertex != null)
            {
                vertex.Revert();
                manager.InvalidateGeometry();
            }
        }
    }

    /// <summary>
    /// Helper to integrate with Rhino's undo system.
    /// </summary>
    public static class RhinoUndoHelper
    {
        /// <summary>
        /// Register an undo event with Rhino.
        /// </summary>
        public static void RegisterUndo(RhinoDoc doc, LatentUndoEvent undoEvent, RegionManager manager)
        {
            doc.AddCustomUndoEvent(
                undoEvent.Description,
                (sender, e) =>
                {
                    if (e.Type == Rhino.Commands.CustomUndoEventArgs.OperationType.Undo)
                    {
                        undoEvent.Undo(manager);
                    }
                    else
                    {
                        undoEvent.Redo(manager);
                    }
                    doc.Views.Redraw();
                }
            );
        }
    }
}
```

### 6. Create RegionManager.cs

```csharp
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

        public event EventHandler Changed;

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

        public Vertex GetVertex(string id) =>
            _vertices.TryGetValue(id, out var v) ? v : null;

        public Edge GetEdge(string id) =>
            _edges.TryGetValue(id, out var e) ? e : null;

        public Region GetRegion(string id) =>
            _regions.TryGetValue(id, out var r) ? r : null;

        public IGeometryElement GetElement(string id)
        {
            if (_vertices.TryGetValue(id, out var v)) return v;
            if (_edges.TryGetValue(id, out var e)) return e;
            if (_regions.TryGetValue(id, out var r)) return r;
            return null;
        }

        public Region FindRegionAt(ParametricPoint param)
        {
            // TODO: Implement proper point-in-region test
            // For now, return first region (placeholder)
            return _regions.Values.FirstOrDefault();
        }

        public Edge FindNearestEdge(ParametricPoint param)
        {
            // TODO: Implement proper proximity test
            return _edges.Values.FirstOrDefault();
        }

        public Vertex FindNearestVertex(ParametricPoint param)
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
```

### 7. Create RegionManagerTests.cs

```csharp
// rhino_plugin/Tests/RegionManagerTests.cs
using System.Collections.Generic;
using NUnit.Framework;
using Latent.Geometry;
using Latent.Analysis;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class RegionManagerTests
    {
        private RegionManager _manager;

        [SetUp]
        public void SetUp()
        {
            _manager = new RegionManager();
        }

        [Test]
        public void UpdateFromAnalysis_PopulatesCollections()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            Assert.AreEqual(2, _manager.Vertices.Count);
            Assert.AreEqual(1, _manager.Edges.Count);
            Assert.AreEqual(1, _manager.Regions.Count);
        }

        [Test]
        public void GetVertex_ReturnsCorrectVertex()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            var vertex = _manager.GetVertex("v1");
            Assert.IsNotNull(vertex);
            Assert.AreEqual("v1", vertex.Id);
        }

        [Test]
        public void SelectRegion_SetsSelected()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            _manager.SelectRegion("r1");

            var region = _manager.GetRegion("r1");
            Assert.IsTrue(region.IsSelected);
        }

        [Test]
        public void SetPinned_UpdatesState()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            var vertex = _manager.GetVertex("v1");
            Assert.IsFalse(vertex.IsPinned);

            _manager.SetPinned("v1", true);

            Assert.IsTrue(vertex.IsPinned);
        }

        [Test]
        public void Vertex_IsImplicit_WhenAtOriginalPosition()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos);

            Assert.IsTrue(vertex.IsImplicit);
        }

        [Test]
        public void Vertex_IsExplicit_WhenMoved()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var newPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", newPos, originalPos);

            Assert.IsFalse(vertex.IsImplicit);
        }

        [Test]
        public void Vertex_CannotRevert_WhenPinned()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var newPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", newPos, originalPos);
            vertex.IsPinned = true;

            Assert.IsFalse(vertex.CanRevert);
        }

        [Test]
        public void Vertex_CannotRevert_WhenFromCurveModification()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.CurveModification);

            Assert.IsFalse(vertex.CanRevert);
        }

        [Test]
        public void Edge_IsImplicit_WhenCurveTypeUnchanged()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" },
                CurveType.Bezier, 3, CurveType.Bezier, 3);

            Assert.IsTrue(edge.IsImplicit);
        }

        [Test]
        public void Edge_IsExplicit_WhenCurveTypeChanged()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" },
                CurveType.BSpline, 3, CurveType.Bezier, 3);

            Assert.IsFalse(edge.IsImplicit);
        }

        [Test]
        public void PinnedElements_PreservedOnReanalysis()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            // Pin a vertex
            _manager.SetPinned("v1", true);

            // Re-run analysis
            _manager.UpdateFromAnalysis(data);

            // Vertex should still be pinned
            var vertex = _manager.GetVertex("v1");
            Assert.IsTrue(vertex.IsPinned);
        }

        private AnalysisResultData CreateTestAnalysisData()
        {
            return new AnalysisResultData
            {
                Vertices = new List<VertexData>
                {
                    new VertexData
                    {
                        Id = "v1",
                        Position = new List<double> { 0, 0.0, 0.0 },
                        CreatedBy = "lens"
                    },
                    new VertexData
                    {
                        Id = "v2",
                        Position = new List<double> { 0, 1.0, 1.0 },
                        CreatedBy = "lens"
                    }
                },
                Edges = new List<EdgeData>
                {
                    new EdgeData
                    {
                        Id = "e1",
                        VertexIds = new List<string> { "v1", "v2" },
                        CurveType = "bezier",
                        Degree = 3
                    }
                },
                Regions = new List<RegionData>
                {
                    new RegionData
                    {
                        Id = "r1",
                        BoundaryEdgeIds = new List<string> { "e1" },
                        UnityPrinciple = "Test",
                        ResonanceScore = 0.85
                    }
                }
            };
        }
    }
}
```

## Success Criteria

- [ ] All data classes compile without errors
- [ ] Vertex tracks implicit/explicit state correctly
- [ ] Edge tracks curve type changes
- [ ] Region aggregates edge/vertex state
- [ ] RegionManager updates from analysis results
- [ ] Selection works correctly
- [ ] Pin/unpin integrates with Rhino undo
- [ ] Move/revert integrates with Rhino undo
- [ ] Pinned elements preserved on re-analysis
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run tests
dotnet test --filter "FullyQualifiedName~RegionManagerTests"
```

## Do Not Modify

- Files in `rhino_plugin/Interop/` (Agent 3A's domain)
- Files in `rhino_plugin/Analysis/` (Agent 3B's domain)
- Files in `rhino_plugin/Commands/` (Agent 3C's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests

## Report

When complete, provide:
1. Build output
2. Test results
3. Any edge cases discovered in state management
