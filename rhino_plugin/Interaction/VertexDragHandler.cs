// rhino_plugin/Interaction/VertexDragHandler.cs
using System;
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
    /// Result from a vertex drag operation.
    /// </summary>
    public enum DragResult
    {
        Success,
        Canceled,
        Failed,
        Pinned   // Cannot drag pinned element
    }

    /// <summary>
    /// Handles vertex drag operations with surface constraint.
    /// Uses Latent.Interop.ParametricPoint throughout.
    /// </summary>
    public class VertexDragHandler
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly DragPreview _preview;

        /// <summary>
        /// Event raised when drag starts.
        /// </summary>
        public event EventHandler<VertexDragEventArgs> DragStarted;

        /// <summary>
        /// Event raised when drag completes.
        /// </summary>
        public event EventHandler<VertexDragEventArgs> DragCompleted;

        /// <summary>
        /// Event raised when drag is canceled.
        /// </summary>
        public event EventHandler<VertexDragEventArgs> DragCanceled;

        public VertexDragHandler(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _preview = new DragPreview(evaluator);
        }

        /// <summary>
        /// Start an interactive drag operation for a vertex.
        /// </summary>
        /// <param name="vertex">The vertex to drag</param>
        /// <returns>Result of the drag operation</returns>
        public DragResult StartDrag(Vertex vertex)
        {
            if (vertex == null)
                throw new ArgumentNullException(nameof(vertex));

            // Check if vertex is pinned
            if (vertex.IsPinned)
            {
                RhinoApp.WriteLine("Cannot drag pinned vertex. Unpin first.");
                return DragResult.Pinned;
            }

            // Get original position
            var originalParam = vertex.Position;
            var originalPos3d = _evaluator.EvaluatePoint(
                originalParam.FaceId,
                originalParam.U,
                originalParam.V);

            // Raise start event
            DragStarted?.Invoke(this, new VertexDragEventArgs(vertex, originalParam));

            // Create surface-constrained GetPoint
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt("Drag vertex to new position (ESC to cancel)");
            gp.SetBasePoint(originalPos3d, showDistanceInStatusBar: true);

            // Track the current preview position
            ParametricPoint previewParam = originalParam;

            // Add dynamic draw for preview
            gp.DynamicDraw += (sender, e) =>
            {
                previewParam = gp.CurrentParametricPosition;
                _preview.DrawVertexPreview(e.Display, vertex, previewParam);
            };

            // Run the interaction
            var result = gp.Get();

            if (result == GetResult.Point)
            {
                var newParam = gp.CurrentParametricPosition;

                if (newParam.IsValid)
                {
                    // Apply the move through RegionManager (creates undo record)
                    _regionManager.MoveVertex(vertex, newParam);

                    // Raise completion event
                    DragCompleted?.Invoke(this, new VertexDragEventArgs(vertex, newParam));

                    return DragResult.Success;
                }
            }

            // Canceled or failed
            DragCanceled?.Invoke(this, new VertexDragEventArgs(vertex, originalParam));
            return DragResult.Canceled;
        }

        /// <summary>
        /// Apply a drag programmatically (for testing or scripted operations).
        /// </summary>
        public DragResult ApplyDrag(Vertex vertex, Point3d newPosition3d)
        {
            if (vertex == null)
                throw new ArgumentNullException(nameof(vertex));

            if (vertex.IsPinned)
                return DragResult.Pinned;

            // Project 3D position to surface
            var newParam = _evaluator.ProjectPoint(newPosition3d);
            if (newParam.IsValid)
            {
                _regionManager.MoveVertex(vertex, newParam);
                return DragResult.Success;
            }

            return DragResult.Failed;
        }
    }

    /// <summary>
    /// Event args for vertex drag operations.
    /// </summary>
    public class VertexDragEventArgs : EventArgs
    {
        public Vertex Vertex { get; }
        public ParametricPoint Position { get; }

        public VertexDragEventArgs(Vertex vertex, ParametricPoint position)
        {
            Vertex = vertex;
            Position = position;
        }
    }
}
