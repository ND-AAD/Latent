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
                new RegionConduit(null!, _settings));
        }

        [Test]
        public void Constructor_WithNullSettings_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() =>
                new RegionConduit(_regionManager, null!));
        }

        [Test]
        public void Initialize_WithoutEvaluator_ThrowsInvalidOperation()
        {
            var conduit = new RegionConduit(_regionManager, _settings);
            Assert.Throws<InvalidOperationException>(() => conduit.Initialize());
        }

        [Test]
        public void Evaluator_CanBeSet()
        {
            var conduit = new RegionConduit(_regionManager, _settings);
            var evaluator = new SubDEvaluator();

            conduit.Evaluator = evaluator;

            Assert.That(conduit.Evaluator, Is.EqualTo(evaluator));
        }

        [Test]
        public void HoveredElementId_CanBeSet()
        {
            var conduit = new RegionConduit(_regionManager, _settings);

            conduit.HoveredElementId = "test-id";

            Assert.That(conduit.HoveredElementId, Is.EqualTo("test-id"));
        }

        [Test]
        public void GetBoundingBox_WithNoRegions_ReturnsEmpty()
        {
            var conduit = new RegionConduit(_regionManager, _settings);

            var bbox = conduit.GetBoundingBox();

            Assert.That(bbox.IsValid, Is.False);
        }

        [Test]
        public void InvalidateCache_DoesNotThrow()
        {
            var conduit = new RegionConduit(_regionManager, _settings);

            Assert.DoesNotThrow(() => conduit.InvalidateCache());
        }

        [Test]
        public void Cleanup_DoesNotThrow()
        {
            var conduit = new RegionConduit(_regionManager, _settings);

            Assert.DoesNotThrow(() => conduit.Cleanup());
        }

        [Test]
        public void RegionManagerChanged_InvalidatesCache()
        {
            var conduit = new RegionConduit(_regionManager, _settings);

            // Trigger change event
            _regionManager.Clear();

            // Should invalidate cache without throwing
            Assert.DoesNotThrow(() => conduit.GetBoundingBox());
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
        public void GetElementColor_SelectedTakesPriority_OverHovered()
        {
            var color = _settings.GetElementColor(isSelected: true, isPinned: false, isHovered: true);
            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetElementColor_HoveredTakesPriority_OverPinned()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: true, isHovered: true);
            Assert.That(color, Is.EqualTo(_settings.HoveredColor));
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
        public void GetFillColor_WithDifferentOpacity_AppliesCorrectly()
        {
            _settings.FillOpacity = 128;
            var baseColor = Color.Blue;
            var fillColor = _settings.GetFillColor(baseColor);

            Assert.That(fillColor.A, Is.EqualTo(128));
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

        [Test]
        public void DefaultSettings_ShowFlagsEnabled()
        {
            Assert.That(_settings.ShowRegionFill, Is.True);
            Assert.That(_settings.ShowCentroidMarkers, Is.True);
        }

        [Test]
        public void DefaultSettings_PerformanceFlagsEnabled()
        {
            Assert.That(_settings.UseAdaptiveSampling, Is.True);
            Assert.That(_settings.CacheCurves, Is.True);
        }

        [Test]
        public void SelectedVertexPointSize_IsLargerThanDefault()
        {
            Assert.That(_settings.SelectedVertexPointSize, Is.GreaterThan(_settings.VertexPointSize));
        }

        [Test]
        public void Colors_AreValid()
        {
            Assert.That(_settings.DefaultCurveColor, Is.Not.EqualTo(Color.Empty));
            Assert.That(_settings.SelectedColor, Is.Not.EqualTo(Color.Empty));
            Assert.That(_settings.PinnedColor, Is.Not.EqualTo(Color.Empty));
            Assert.That(_settings.HoveredColor, Is.Not.EqualTo(Color.Empty));
            Assert.That(_settings.CentroidTextColor, Is.Not.EqualTo(Color.Empty));
            Assert.That(_settings.CentroidBackgroundColor, Is.Not.EqualTo(Color.Empty));
        }
    }
}
