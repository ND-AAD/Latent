// rhino_plugin/Interaction/RegionPicker.cs
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
    /// Interactive picker for selecting regions on the SubD surface.
    /// </summary>
    public class RegionPicker
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly ElementPicker _elementPicker;

        /// <summary>
        /// Color to highlight regions during hover.
        /// </summary>
        public Color HoverColor { get; set; } = Color.FromArgb(128, Color.Yellow);

        /// <summary>
        /// Whether to highlight regions on hover.
        /// </summary>
        public bool HighlightOnHover { get; set; } = true;

        public RegionPicker(RegionManager regionManager, SubDEvaluator evaluator, SubD subd)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));

            // Create element picker with region-only mode
            var settings = new PickSettings
            {
                Mode = PickMode.Regions
            };
            _elementPicker = new ElementPicker(regionManager, evaluator, settings);
        }

        /// <summary>
        /// Interactively pick a region.
        /// </summary>
        /// <returns>The picked region, or null if canceled</returns>
        public Latent.Geometry.Region PickRegion()
        {
            return PickRegion("Pick point on region");
        }

        /// <summary>
        /// Interactively pick a region with custom prompt.
        /// </summary>
        public Latent.Geometry.Region PickRegion(string prompt)
        {
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt(prompt);

            Latent.Geometry.Region hoveredRegion = null;

            // Add hover highlighting
            if (HighlightOnHover)
            {
                gp.DynamicDraw += (sender, e) =>
                {
                    var param = gp.CurrentParametricPosition;
                    if (!param.IsValid) return;

                    // Find region at current point
                    var region = _regionManager.FindRegionContaining(
                        param.FaceId, (float)param.U, (float)param.V);

                    hoveredRegion = region;

                    if (region != null)
                    {
                        DrawRegionHighlight(e.Display, region);
                    }
                };
            }

            var result = gp.Get();

            if (result == GetResult.Point)
            {
                var param = gp.CurrentParametricPosition;
                if (param.IsValid)
                {
                    return _regionManager.FindRegionContaining(
                        param.FaceId, (float)param.U, (float)param.V);
                }
            }

            return null;
        }

        /// <summary>
        /// Interactively pick multiple regions.
        /// </summary>
        public Latent.Geometry.Region[] PickMultipleRegions(string prompt = "Pick regions (Enter to finish)")
        {
            var selected = new System.Collections.Generic.List<Latent.Geometry.Region>();

            while (true)
            {
                var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
                gp.SetCommandPrompt($"{prompt} [{selected.Count} selected]");
                gp.AcceptNothing(true);

                Latent.Geometry.Region hoveredRegion = null;

                if (HighlightOnHover)
                {
                    gp.DynamicDraw += (sender, e) =>
                    {
                        // Draw already selected regions
                        foreach (var r in selected)
                        {
                            DrawRegionHighlight(e.Display, r, Color.Green);
                        }

                        // Draw hovered region
                        var param = gp.CurrentParametricPosition;
                        if (param.IsValid)
                        {
                            var region = _regionManager.FindRegionContaining(
                                param.FaceId, (float)param.U, (float)param.V);

                            if (region != null && !selected.Contains(region))
                            {
                                hoveredRegion = region;
                                DrawRegionHighlight(e.Display, region, HoverColor);
                            }
                        }
                    };
                }

                var result = gp.Get();

                if (result == GetResult.Nothing)
                {
                    // User pressed Enter - done
                    break;
                }

                if (result == GetResult.Point)
                {
                    var param = gp.CurrentParametricPosition;
                    if (param.IsValid)
                    {
                        var region = _regionManager.FindRegionContaining(
                            param.FaceId, (float)param.U, (float)param.V);

                        if (region != null)
                        {
                            if (selected.Contains(region))
                            {
                                // Toggle off
                                selected.Remove(region);
                                RhinoApp.WriteLine($"Deselected region {region.Id}");
                            }
                            else
                            {
                                // Toggle on
                                selected.Add(region);
                                RhinoApp.WriteLine($"Selected region {region.Id}");
                            }
                        }
                    }
                }
                else
                {
                    // Cancel
                    break;
                }
            }

            return selected.ToArray();
        }

        /// <summary>
        /// Draw a highlight around a region's boundary.
        /// </summary>
        private void DrawRegionHighlight(DisplayPipeline display, Latent.Geometry.Region region, Color? color = null)
        {
            var highlightColor = color ?? HoverColor;

            // Draw boundary edges with thick lines
            foreach (var edge in region.BoundaryEdges)
            {
                var points = new System.Collections.Generic.List<Point3d>();

                foreach (var vertex in edge.Vertices)
                {
                    var pt = _evaluator.EvaluatePoint(
                        vertex.Position.FaceId,
                        vertex.Position.U,
                        vertex.Position.V);
                    points.Add(pt);
                }

                if (points.Count >= 2)
                {
                    display.DrawPolyline(points, highlightColor, 3);
                }
            }
        }
    }

    /// <summary>
    /// Interactive picker for any element type.
    /// </summary>
    public class InteractiveElementPicker
    {
        private readonly RegionManager _regionManager;
        private readonly SubDEvaluator _evaluator;
        private readonly SubD _subd;
        private readonly ElementPicker _picker;
        private readonly PickSettings _settings;

        public InteractiveElementPicker(
            RegionManager regionManager,
            SubDEvaluator evaluator,
            SubD subd,
            PickSettings? settings = null)
        {
            _regionManager = regionManager ?? throw new ArgumentNullException(nameof(regionManager));
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
            _subd = subd ?? throw new ArgumentNullException(nameof(subd));
            _settings = settings ?? new PickSettings();
            _picker = new ElementPicker(regionManager, evaluator, _settings);
        }

        /// <summary>
        /// Interactively pick an element.
        /// </summary>
        public PickResult Pick(string prompt = "Pick element")
        {
            var gp = new SurfaceConstrainedGetPoint(_subd, _evaluator);
            gp.SetCommandPrompt(prompt);

            PickResult currentResult = null;

            gp.DynamicDraw += (sender, e) =>
            {
                var param = gp.CurrentParametricPosition;
                if (!param.IsValid) return;

                var point3d = gp.CurrentSurfacePoint;
                currentResult = _picker.PickAtPoint(param, point3d);

                // Draw highlight based on pick type
                if (currentResult.Success)
                {
                    DrawPickHighlight(e.Display, currentResult);
                }
            };

            var result = gp.Get();

            if (result == GetResult.Point && currentResult?.Success == true)
            {
                return currentResult;
            }

            return PickResult.Empty;
        }

        private void DrawPickHighlight(DisplayPipeline display, PickResult result)
        {
            switch (result.Type)
            {
                case PickType.Vertex:
                    display.DrawPoint(result.PickPoint3d, PointStyle.RoundControlPoint, 10, Color.Yellow);
                    break;

                case PickType.Edge:
                    if (result.Edge != null)
                    {
                        var points = new System.Collections.Generic.List<Point3d>();
                        foreach (var v in result.Edge.Vertices)
                        {
                            points.Add(_evaluator.EvaluatePoint(v.Position.FaceId, v.Position.U, v.Position.V));
                        }
                        if (points.Count >= 2)
                        {
                            display.DrawPolyline(points, Color.Yellow, 3);
                        }
                    }
                    break;

                case PickType.Region:
                    if (result.Region != null)
                    {
                        foreach (var edge in result.Region.BoundaryEdges)
                        {
                            var points = new System.Collections.Generic.List<Point3d>();
                            foreach (var v in edge.Vertices)
                            {
                                points.Add(_evaluator.EvaluatePoint(v.Position.FaceId, v.Position.U, v.Position.V));
                            }
                            if (points.Count >= 2)
                            {
                                display.DrawPolyline(points, Color.FromArgb(128, Color.Yellow), 2);
                            }
                        }
                    }
                    break;
            }
        }
    }
}
