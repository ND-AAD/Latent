// rhino_plugin/Interaction/DragPreview.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino.Display;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Interaction
{
    /// <summary>
    /// Provides visual preview during drag operations.
    /// Uses Latent.Interop.ParametricPoint for all parametric coordinates.
    /// </summary>
    public class DragPreview
    {
        private readonly SubDEvaluator _evaluator;

        /// <summary>
        /// Color for preview points.
        /// </summary>
        public Color PreviewPointColor { get; set; } = Color.Yellow;

        /// <summary>
        /// Color for preview lines.
        /// </summary>
        public Color PreviewLineColor { get; set; } = Color.FromArgb(128, Color.Yellow);

        /// <summary>
        /// Size for preview points.
        /// </summary>
        public int PreviewPointSize { get; set; } = 8;

        /// <summary>
        /// Line thickness for preview curves.
        /// </summary>
        public int PreviewLineThickness { get; set; } = 2;

        /// <summary>
        /// Whether to show connection lines to original position.
        /// </summary>
        public bool ShowDisplacementLines { get; set; } = true;

        public DragPreview(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        }

        /// <summary>
        /// Draw a vertex preview at new position.
        /// </summary>
        public void DrawVertexPreview(DisplayPipeline display, Vertex vertex, ParametricPoint newPosition)
        {
            if (display == null || vertex == null || !newPosition.IsValid)
                return;

            // Get 3D positions
            var originalPos = GetPoint3d(vertex.Position);
            var newPos = GetPoint3d(newPosition);

            // Draw preview point at new position
            display.DrawPoint(newPos, PointStyle.RoundControlPoint, PreviewPointSize, PreviewPointColor);

            // Draw displacement line
            if (ShowDisplacementLines)
            {
                display.DrawLine(originalPos, newPos, PreviewLineColor, PreviewLineThickness);
            }

            // Draw ghost at original position
            display.DrawPoint(originalPos, PointStyle.Circle, PreviewPointSize - 2, Color.FromArgb(128, Color.Gray));
        }

        /// <summary>
        /// Draw an edge preview at displaced positions.
        /// </summary>
        public void DrawEdgePreview(
            DisplayPipeline display,
            Edge edge,
            IReadOnlyList<ParametricPoint> newVertexPositions)
        {
            if (display == null || edge == null || newVertexPositions == null)
                return;

            var vertices = edge.Vertices;
            if (vertices.Count != newVertexPositions.Count)
                return;

            // Draw preview vertices
            for (int i = 0; i < vertices.Count; i++)
            {
                DrawVertexPreview(display, vertices[i], newVertexPositions[i]);
            }

            // Draw preview edge curve (polyline through new positions)
            if (newVertexPositions.Count >= 2)
            {
                var points = new List<Point3d>();
                foreach (var param in newVertexPositions)
                {
                    if (param.IsValid)
                    {
                        points.Add(GetPoint3d(param));
                    }
                }

                if (points.Count >= 2)
                {
                    display.DrawPolyline(points, PreviewPointColor, PreviewLineThickness);
                }
            }
        }

        /// <summary>
        /// Draw multiple vertices at displaced positions.
        /// </summary>
        public void DrawMultiVertexPreview(
            DisplayPipeline display,
            IReadOnlyList<Vertex> vertices,
            IReadOnlyList<ParametricPoint> newPositions)
        {
            if (display == null || vertices == null || newPositions == null)
                return;

            int count = Math.Min(vertices.Count, newPositions.Count);
            for (int i = 0; i < count; i++)
            {
                DrawVertexPreview(display, vertices[i], newPositions[i]);
            }
        }

        /// <summary>
        /// Get 3D point from parametric coordinates.
        /// </summary>
        private Point3d GetPoint3d(ParametricPoint param)
        {
            if (!param.IsValid)
                return Point3d.Unset;

            return _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
        }
    }
}
