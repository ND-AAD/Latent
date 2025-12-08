// rhino_plugin/Interaction/EdgeDragHandler.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Rhino.Input;
using Rhino.Input.Custom;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Handles edge drag operations (moves all vertices together).
    /// Uses Latent.Interop.ParametricPoint throughout.
    /// </summary>
    public class EdgeDragHandler
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly DragPreview _preview;

        /// <summary>
        /// Event raised when drag starts.
        /// </summary>
        public event EventHandler<EdgeDragEventArgs> DragStarted;

        /// <summary>
        /// Event raised when drag completes.
        /// </summary>
        public event EventHandler<EdgeDragEventArgs> DragCompleted;

        /// <summary>
        /// Event raised when drag is canceled.
        /// </summary>
        public event EventHandler<EdgeDragEventArgs> DragCanceled;

        public EdgeDragHandler(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _preview = new DragPreview(evaluator);
        }

        /// <summary>
        /// Start an interactive drag operation for an edge.
        /// </summary>
        /// <param name="edge">The edge to drag</param>
        /// <returns>Result of the drag operation</returns>
        public DragResult StartDrag(Edge edge)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            // Check if edge is pinned
            if (edge.IsPinned)
            {
                RhinoApp.WriteLine("Cannot drag pinned edge. Unpin first.");
                return DragResult.Pinned;
            }

            // Check if any vertex is pinned
            foreach (var vertex in edge.Vertices)
            {
                if (vertex.IsPinned)
                {
                    RhinoApp.WriteLine($"Cannot drag: vertex {vertex.Id} is pinned.");
                    return DragResult.Pinned;
                }
            }

            // Calculate edge centroid in 3D
            var centroid = CalculateCentroid(edge);

            // Store original positions
            var originalPositions = new List<ParametricPoint>();
            foreach (var v in edge.Vertices)
            {
                originalPositions.Add(v.Position);
            }

            // Raise start event
            DragStarted?.Invoke(this, new EdgeDragEventArgs(edge, originalPositions));

            // Create GetPoint for drag
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt("Drag edge to new position (ESC to cancel)");
            gp.SetBasePoint(centroid, showDistanceInStatusBar: true);

            // Track preview positions
            var previewPositions = new List<ParametricPoint>(originalPositions);

            // Add dynamic draw for preview
            gp.DynamicDraw += (sender, e) =>
            {
                // Calculate displacement
                var displacement = e.CurrentPoint - centroid;

                // Project each vertex to new position
                previewPositions.Clear();
                foreach (var vertex in edge.Vertices)
                {
                    var original3d = _evaluator.EvaluatePoint(
                        vertex.Position.FaceId,
                        vertex.Position.U,
                        vertex.Position.V);
                    var new3d = original3d + displacement;

                    // Project back to surface
                    var newParam = _evaluator.ProjectPoint(new3d);
                    previewPositions.Add(newParam);  // May be invalid if projection fails
                }

                // Draw preview
                _preview.DrawEdgePreview(e.Display, edge, previewPositions);
            };

            // Run the interaction
            var result = gp.Get();

            if (result == GetResult.Point)
            {
                var displacement = gp.CurrentSurfacePoint - centroid;

                // Apply moves to all vertices
                bool allSucceeded = true;
                for (int i = 0; i < edge.Vertices.Count; i++)
                {
                    var vertex = edge.Vertices[i];
                    var original3d = _evaluator.EvaluatePoint(
                        vertex.Position.FaceId,
                        vertex.Position.U,
                        vertex.Position.V);
                    var new3d = original3d + displacement;

                    var newParam = _evaluator.ProjectPoint(new3d);
                    if (newParam.IsValid)
                    {
                        _regionManager.MoveVertex(vertex, newParam);
                    }
                    else
                    {
                        allSucceeded = false;
                    }
                }

                // Raise completion event
                DragCompleted?.Invoke(this, new EdgeDragEventArgs(edge, previewPositions));

                return allSucceeded ? DragResult.Success : DragResult.Failed;
            }

            // Canceled
            DragCanceled?.Invoke(this, new EdgeDragEventArgs(edge, originalPositions));
            return DragResult.Canceled;
        }

        /// <summary>
        /// Apply an edge drag programmatically.
        /// </summary>
        public DragResult ApplyDrag(Edge edge, Vector3d displacement)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            if (edge.IsPinned)
                return DragResult.Pinned;

            foreach (var vertex in edge.Vertices)
            {
                if (vertex.IsPinned)
                    return DragResult.Pinned;
            }

            bool allSucceeded = true;
            foreach (var vertex in edge.Vertices)
            {
                var original3d = _evaluator.EvaluatePoint(
                    vertex.Position.FaceId,
                    vertex.Position.U,
                    vertex.Position.V);
                var new3d = original3d + displacement;

                var newParam = _evaluator.ProjectPoint(new3d);
                if (newParam.IsValid)
                {
                    _regionManager.MoveVertex(vertex, newParam);
                }
                else
                {
                    allSucceeded = false;
                }
            }

            return allSucceeded ? DragResult.Success : DragResult.Failed;
        }

        /// <summary>
        /// Calculate the 3D centroid of an edge's vertices.
        /// </summary>
        private Point3d CalculateCentroid(Edge edge)
        {
            var sum = Point3d.Origin;
            int count = 0;

            foreach (var vertex in edge.Vertices)
            {
                var pt = _evaluator.EvaluatePoint(
                    vertex.Position.FaceId,
                    vertex.Position.U,
                    vertex.Position.V);
                sum += pt;
                count++;
            }

            if (count == 0)
                return Point3d.Origin;

            return sum / count;
        }
    }

    /// <summary>
    /// Event args for edge drag operations.
    /// </summary>
    public class EdgeDragEventArgs : EventArgs
    {
        public Edge Edge { get; }
        public IReadOnlyList<ParametricPoint> VertexPositions { get; }

        public EdgeDragEventArgs(Edge edge, IReadOnlyList<ParametricPoint> positions)
        {
            Edge = edge;
            VertexPositions = positions;
        }
    }
}
