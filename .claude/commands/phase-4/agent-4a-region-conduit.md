# Agent 4A: Region Display Conduit

## Objective

Implement DisplayConduit for visualizing regions, boundaries, and vertices on the SubD limit surface in Rhino 8.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - conduit code examples
- `rhino_plugin/Geometry/RegionManager.cs` - data model for regions
- `rhino_plugin/Geometry/Region.cs` - region class
- `rhino_plugin/Geometry/Edge.cs` - edge class
- `rhino_plugin/Geometry/Vertex.cs` - vertex class

## Dependencies

**From Phase 3:**
- `RegionManager` - provides `Regions`, `Edges`, `Vertices` collections
- `Region` - provides `BoundaryEdges`, `BoundingBox`, `IsSelected`, `IsPinned`
- `Edge` - provides `Vertices`, curve data
- `Vertex` - provides `Position`, `IsPinned`, `IsSelected`

**From This Phase:**
- `CurveSampler` (Agent 4B) - samples parametric curves to polylines
- `RegionFill` (Agent 4C) - renders region fills

## Files to Create

1. `rhino_plugin/Display/RegionConduit.cs` - main display conduit
2. `rhino_plugin/Display/VisualizationSettings.cs` - display settings
3. `rhino_plugin/Tests/RegionConduitTests.cs` - unit tests

## Tasks

### 1. Create VisualizationSettings.cs

```csharp
// rhino_plugin/Display/VisualizationSettings.cs
using System;
using System.Drawing;

namespace Latent.Display
{
    /// <summary>
    /// Configuration for region visualization.
    /// </summary>
    public class VisualizationSettings
    {
        // Curve display
        public float DefaultCurveThickness { get; set; } = 1.5f;
        public float SelectedCurveThickness { get; set; } = 3.0f;
        public int CurveSampleCount { get; set; } = 50;

        // Colors
        public Color DefaultCurveColor { get; set; } = Color.FromArgb(200, 200, 200);
        public Color SelectedColor { get; set; } = Color.Yellow;
        public Color PinnedColor { get; set; } = Color.FromArgb(100, 150, 255);
        public Color HoveredColor { get; set; } = Color.FromArgb(255, 200, 100);

        // Vertex display
        public int VertexPointSize { get; set; } = 5;
        public int SelectedVertexPointSize { get; set; } = 8;

        // Region fill
        public bool ShowRegionFill { get; set; } = true;
        public int FillOpacity { get; set; } = 64;  // 0-255, 25% default

        // Centroid markers
        public bool ShowCentroidMarkers { get; set; } = true;
        public Color CentroidTextColor { get; set; } = Color.Black;
        public Color CentroidBackgroundColor { get; set; } = Color.White;

        // Performance
        public bool UseAdaptiveSampling { get; set; } = true;
        public bool CacheCurves { get; set; } = true;

        /// <summary>
        /// Get the color for an element based on its state.
        /// </summary>
        public Color GetElementColor(bool isSelected, bool isPinned, bool isHovered = false)
        {
            if (isSelected) return SelectedColor;
            if (isHovered) return HoveredColor;
            if (isPinned) return PinnedColor;
            return DefaultCurveColor;
        }

        /// <summary>
        /// Get curve thickness based on selection state.
        /// </summary>
        public float GetCurveThickness(bool isSelected)
        {
            return isSelected ? SelectedCurveThickness : DefaultCurveThickness;
        }

        /// <summary>
        /// Get a fill color with appropriate transparency.
        /// </summary>
        public Color GetFillColor(Color baseColor)
        {
            return Color.FromArgb(FillOpacity, baseColor);
        }
    }
}
```

### 2. Create RegionConduit.cs

```csharp
// rhino_plugin/Display/RegionConduit.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using Rhino;
using Rhino.Display;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Display
{
    /// <summary>
    /// DisplayConduit for rendering regions on SubD surfaces.
    /// </summary>
    public class RegionConduit : DisplayConduit
    {
        private readonly RegionManager _regionManager;
        private readonly VisualizationSettings _settings;

        private CurveSampler _curveSampler;
        private CurveCache _curveCache;
        private RegionFill _regionFill;
        private CentroidMarker _centroidMarker;

        // Cached bounding box
        private BoundingBox _boundingBox = BoundingBox.Empty;
        private bool _boundingBoxValid = false;

        /// <summary>
        /// The SubD evaluator for sampling curves on surface.
        /// Must be set before conduit is enabled.
        /// </summary>
        public SubDEvaluator Evaluator { get; set; }

        /// <summary>
        /// Currently hovered element ID (for hover highlighting).
        /// </summary>
        public string HoveredElementId { get; set; }

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

        private void OnRegionManagerChanged(object sender, EventArgs e)
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

        private void DrawRegionBoundaries(DisplayPipeline display, Region region)
        {
            var color = _settings.GetElementColor(
                region.IsSelected,
                region.IsPinned,
                region.Id == HoveredElementId);
            var thickness = (int)_settings.GetCurveThickness(region.IsSelected);

            foreach (var edge in region.BoundaryEdges)
            {
                // Get cached or sample new polyline
                var points = _settings.CacheCurves
                    ? _curveCache.GetOrSample(edge, _settings.CurveSampleCount)
                    : _curveSampler.SampleEdge(edge, _settings.CurveSampleCount);

                if (points != null && points.Count > 1)
                {
                    display.DrawPolyline(points, color, thickness);
                }

                // Draw edge with its own selection state if different from region
                if (edge.IsSelected && !region.IsSelected)
                {
                    var edgeColor = _settings.GetElementColor(true, edge.IsPinned);
                    display.DrawPolyline(points, edgeColor, (int)_settings.SelectedCurveThickness);
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

        private void DrawRegionFill(DisplayPipeline display, Region region)
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

        private void DrawCentroidMarker(DisplayPipeline display, Region region)
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
                CalculateBoundingBox(null);
            }
            return _boundingBox;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _regionManager.Changed -= OnRegionManagerChanged;
                _curveCache?.Clear();
            }
            base.Dispose(disposing);
        }
    }
}
```

### 3. Create Unit Tests

```csharp
// rhino_plugin/Tests/RegionConduitTests.cs
using System;
using System.Collections.Generic;
using System.Drawing;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Display;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class RegionConduitTests
    {
        private RegionManager _regionManager;
        private VisualizationSettings _settings;

        [SetUp]
        public void SetUp()
        {
            _regionManager = new RegionManager();
            _settings = new VisualizationSettings();
        }

        [Test]
        public void Constructor_WithValidParameters_Succeeds()
        {
            var conduit = new RegionConduit(_regionManager, _settings);
            Assert.That(conduit, Is.Not.Null);
        }

        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() =>
                new RegionConduit(null, _settings));
        }

        [Test]
        public void Constructor_WithNullSettings_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() =>
                new RegionConduit(_regionManager, null));
        }

        [Test]
        public void Initialize_WithoutEvaluator_ThrowsInvalidOperation()
        {
            var conduit = new RegionConduit(_regionManager, _settings);
            Assert.Throws<InvalidOperationException>(() => conduit.Initialize());
        }
    }

    [TestFixture]
    public class VisualizationSettingsTests
    {
        private VisualizationSettings _settings;

        [SetUp]
        public void SetUp()
        {
            _settings = new VisualizationSettings();
        }

        [Test]
        public void GetElementColor_Selected_ReturnsSelectedColor()
        {
            var color = _settings.GetElementColor(isSelected: true, isPinned: false);
            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetElementColor_Pinned_ReturnsPinnedColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: true);
            Assert.That(color, Is.EqualTo(_settings.PinnedColor));
        }

        [Test]
        public void GetElementColor_Hovered_ReturnsHoveredColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: false, isHovered: true);
            Assert.That(color, Is.EqualTo(_settings.HoveredColor));
        }

        [Test]
        public void GetElementColor_Default_ReturnsDefaultColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: false);
            Assert.That(color, Is.EqualTo(_settings.DefaultCurveColor));
        }

        [Test]
        public void GetElementColor_SelectedTakesPriority_OverPinned()
        {
            var color = _settings.GetElementColor(isSelected: true, isPinned: true);
            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetCurveThickness_Selected_ReturnsSelectedThickness()
        {
            var thickness = _settings.GetCurveThickness(isSelected: true);
            Assert.That(thickness, Is.EqualTo(_settings.SelectedCurveThickness));
        }

        [Test]
        public void GetCurveThickness_NotSelected_ReturnsDefaultThickness()
        {
            var thickness = _settings.GetCurveThickness(isSelected: false);
            Assert.That(thickness, Is.EqualTo(_settings.DefaultCurveThickness));
        }

        [Test]
        public void GetFillColor_SetsCorrectOpacity()
        {
            var baseColor = Color.Red;
            var fillColor = _settings.GetFillColor(baseColor);

            Assert.That(fillColor.A, Is.EqualTo(_settings.FillOpacity));
            Assert.That(fillColor.R, Is.EqualTo(baseColor.R));
            Assert.That(fillColor.G, Is.EqualTo(baseColor.G));
            Assert.That(fillColor.B, Is.EqualTo(baseColor.B));
        }

        [Test]
        public void DefaultSettings_HaveReasonableValues()
        {
            Assert.That(_settings.DefaultCurveThickness, Is.GreaterThan(0));
            Assert.That(_settings.SelectedCurveThickness, Is.GreaterThan(_settings.DefaultCurveThickness));
            Assert.That(_settings.CurveSampleCount, Is.GreaterThan(10));
            Assert.That(_settings.VertexPointSize, Is.GreaterThan(0));
            Assert.That(_settings.FillOpacity, Is.InRange(1, 255));
        }
    }
}
```

## Success Criteria

- [ ] `RegionConduit` extends `DisplayConduit` correctly
- [ ] `CalculateBoundingBox` includes all region geometry
- [ ] `PostDrawObjects` draws curves and vertices
- [ ] `DrawForeground` draws fills and centroids when enabled
- [ ] Selection highlighting works (yellow for selected)
- [ ] Pinned elements display in blue
- [ ] Hover highlighting works
- [ ] Cache invalidation triggers on region changes
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build
dotnet test --filter "FullyQualifiedName~RegionConduitTests|FullyQualifiedName~VisualizationSettingsTests"
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Interop/` (Phase 3 domain)
- Files in `Commands/` (Phase 3 domain)
- `LatentPlugin.cs` (will be updated in consolidation)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

- `DisplayConduit` is a Rhino SDK class for custom drawing
- `PostDrawObjects` is called during normal geometry drawing
- `DrawForeground` is called after all objects, good for overlays
- Cache invalidation is critical for performance
- The conduit must be enabled (`conduit.Enabled = true`) to draw

## Report

When complete, provide:
1. Test output showing all tests pass
2. Build output showing no errors
3. Any edge cases discovered and handled
4. Notes on integration with CurveSampler and RegionFill
