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
        /// The handler is called on both undo and redo operations.
        /// CreatedByRedo indicates whether this is a redo (true) or undo (false) operation.
        /// </summary>
        public static void RegisterUndo(RhinoDoc doc, LatentUndoEvent undoEvent, RegionManager manager)
        {
            if (doc == null) return;

            doc.AddCustomUndoEvent(
                undoEvent.Description,
                (sender, e) =>
                {
                    // CreatedByRedo is true when this handler is being called due to a redo operation
                    if (e.CreatedByRedo)
                    {
                        undoEvent.Redo(manager);
                    }
                    else
                    {
                        undoEvent.Undo(manager);
                    }
                    doc.Views.Redraw();
                }
            );
        }
    }
}
