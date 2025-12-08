// rhino_plugin/Display/RegionConduit.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Latent.Interop;
using Latent.Geometry;
using GeometryRegion = Latent.Geometry.Region;

namespace Latent.Display
{
    /// <summary>
    /// DisplayConduit for rendering regions on SubD surfaces.
    /// </summary>
    public class RegionConduit : DisplayConduit
    {
        private readonly RegionManager _regionManager;
        private readonly VisualizationSettings _settings;

        private CurveSampler? _curveSampler;
        private CurveCache? _curveCache;
        private RegionFill? _regionFill;
        private CentroidMarker? _centroidMarker;

        // Cached bounding box
        private BoundingBox _boundingBox = BoundingBox.Empty;
        private bool _boundingBoxValid = false;

        /// <summary>
        /// The SubD evaluator for sampling curves on surface.
        /// Must be set before conduit is enabled.
        /// </summary>
        public SubDEvaluator? Evaluator { get; set; }

        /// <summary>
        /// Currently hovered element ID (for hover highlighting).
        /// </summary>
        public string? HoveredElementId { get; set; }

        public RegionConduit(RegionManager regionManager, VisualizationSettings settings)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _settings = settings ?? throw new ArgumentNullException(nameof(settings));

            // Subscribe to changes for cache invalidation
            _regionManager.Changed += OnRegionManagerChanged;
        }

        /// <summary>
        /// Initialize display helpers. Call after Evaluator is set.
        /// </summary>
        public void Initialize()
        {
            if (Evaluator == null)
                throw new InvalidOperationException("Evaluator must be set before Initialize()");

            _curveSampler = new CurveSampler(Evaluator);
            _curveCache = new CurveCache(_curveSampler);
            _regionFill = new RegionFill(_curveSampler);
            _centroidMarker = new CentroidMarker(Evaluator);
        }

        /// <summary>
        /// Invalidate all cached data. Call when regions change.
        /// </summary>
        public void InvalidateCache()
        {
            _curveCache?.Clear();
            _boundingBoxValid = false;
        }

        private void OnRegionManagerChanged(object? sender, EventArgs e)
        {
            InvalidateCache();
        }

        protected override void CalculateBoundingBox(CalculateBoundingBoxEventArgs e)
        {
            if (!_boundingBoxValid)
            {
                _boundingBox = BoundingBox.Empty;

                foreach (var region in _regionManager.Regions)
                {
                    if (region.BoundingBox.IsValid)
                    {
                        _boundingBox.Union(region.BoundingBox);
                    }
                }

                _boundingBoxValid = true;
            }

            if (_boundingBox.IsValid)
            {
                e.IncludeBoundingBox(_boundingBox);
            }
        }

        protected override void PostDrawObjects(DrawEventArgs e)
        {
            if (_curveSampler == null) return;

            // Draw boundary curves for all regions
            foreach (var region in _regionManager.Regions)
            {
                DrawRegionBoundaries(e.Display, region);
            }

            // Draw vertices
            foreach (var vertex in _regionManager.Vertices)
            {
                DrawVertex(e.Display, vertex);
            }
        }

        protected override void DrawForeground(DrawEventArgs e)
        {
            if (_regionFill == null) return;

            // Draw region fills (transparent)
            if (_settings.ShowRegionFill)
            {
                foreach (var region in _regionManager.Regions)
                {
                    DrawRegionFill(e.Display, region);
                }
            }

            // Draw centroid markers
            if (_settings.ShowCentroidMarkers)
            {
                foreach (var region in _regionManager.Regions)
                {
                    DrawCentroidMarker(e.Display, region);
                }
            }
        }

        private void DrawRegionBoundaries(DisplayPipeline display, GeometryRegion region)
        {
            var color = _settings.GetElementColor(
                region.IsSelected,
                region.IsPinned,
                region.Id == HoveredElementId);
            var thickness = (int)_settings.GetCurveThickness(region.IsSelected);

            foreach (var edge in region.BoundaryEdges)
            {
                // Get cached or sample new polyline
                var points = _settings.CacheCurves && _curveCache != null
                    ? _curveCache.GetOrSample(edge, _settings.CurveSampleCount)
                    : _curveSampler!.SampleEdge(edge, _settings.CurveSampleCount);

                if (points != null && points.Count > 1)
                {
                    display.DrawPolyline(points, color, thickness);
                }

                // Draw edge with its own selection state if different from region
                if (edge.IsSelected && !region.IsSelected)
                {
                    var edgeColor = _settings.GetElementColor(true, edge.IsPinned);
                    if (points != null && points.Count > 1)
                    {
                        display.DrawPolyline(points, edgeColor, (int)_settings.SelectedCurveThickness);
                    }
                }
            }
        }

        private void DrawVertex(DisplayPipeline display, Vertex vertex)
        {
            if (Evaluator == null) return;

            // Evaluate vertex position on surface
            var pos = vertex.Position;
            var point3d = Evaluator.EvaluatePoint(pos.FaceId, pos.U, pos.V);

            // Determine style based on state
            var style = vertex.IsPinned ? PointStyle.Pin : PointStyle.Circle;
            var isHovered = vertex.Id == HoveredElementId;
            var color = _settings.GetElementColor(vertex.IsSelected, vertex.IsPinned, isHovered);
            var size = vertex.IsSelected ? _settings.SelectedVertexPointSize : _settings.VertexPointSize;

            display.DrawPoint(point3d, style, size, color);
        }

        private void DrawRegionFill(DisplayPipeline display, GeometryRegion region)
        {
            if (_regionFill == null) return;

            var baseColor = _settings.GetElementColor(region.IsSelected, region.IsPinned);
            var fillColor = _settings.GetFillColor(baseColor);

            // Get fill mesh or hatch from RegionFill helper
            var fillMesh = _regionFill.GetFillMesh(region, _settings.CurveSampleCount);
            if (fillMesh != null)
            {
                display.DrawMeshShaded(fillMesh, new DisplayMaterial(fillColor));
            }
        }

        private void DrawCentroidMarker(DisplayPipeline display, GeometryRegion region)
        {
            if (_centroidMarker == null) return;

            var centroid = _centroidMarker.GetCentroid3d(region);
            if (centroid.HasValue)
            {
                display.DrawDot(
                    centroid.Value,
                    region.Id,
                    _settings.CentroidTextColor,
                    _settings.CentroidBackgroundColor);
            }
        }

        /// <summary>
        /// Get bounding box for external use.
        /// </summary>
        public BoundingBox GetBoundingBox()
        {
            if (!_boundingBoxValid)
            {
                // Recompute bounding box
                _boundingBox = BoundingBox.Empty;

                foreach (var region in _regionManager.Regions)
                {
                    if (region.BoundingBox.IsValid)
                    {
                        _boundingBox.Union(region.BoundingBox);
                    }
                }

                _boundingBoxValid = true;
            }
            return _boundingBox;
        }

        /// <summary>
        /// Cleanup resources. Call when conduit is no longer needed.
        /// </summary>
        public void Cleanup()
        {
            _regionManager.Changed -= OnRegionManagerChanged;
            _curveCache?.Clear();
            Enabled = false;
        }
    }
}
