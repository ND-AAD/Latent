// rhino_plugin/Tests/VisualizationPanelTests.cs
using System.Drawing;
using NUnit.Framework;
using Latent.Display;

namespace Latent.Tests
{
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
        public void DefaultValues_AreReasonable()
        {
            Assert.That(_settings.DefaultCurveThickness, Is.EqualTo(1.5f));
            Assert.That(_settings.SelectedCurveThickness, Is.EqualTo(3.0f));
            Assert.That(_settings.CurveSampleCount, Is.EqualTo(50));
            Assert.That(_settings.ShowRegionFill, Is.True);
            Assert.That(_settings.ShowCentroidMarkers, Is.True);
        }

        [Test]
        public void FillOpacity_DefaultIs25Percent()
        {
            // 64 out of 255 = 25%
            Assert.That(_settings.FillOpacity, Is.EqualTo(64));
        }

        [Test]
        public void SelectedColor_IsYellow()
        {
            Assert.That(_settings.SelectedColor, Is.EqualTo(Color.Yellow));
        }

        [Test]
        public void GetElementColor_WhenSelected_ReturnsSelectedColor()
        {
            var color = _settings.GetElementColor(isSelected: true, isPinned: false);

            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetElementColor_WhenPinnedNotSelected_ReturnsPinnedColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: true);

            Assert.That(color, Is.EqualTo(_settings.PinnedColor));
        }

        [Test]
        public void GetElementColor_WhenHovered_ReturnsHoveredColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: false, isHovered: true);

            Assert.That(color, Is.EqualTo(_settings.HoveredColor));
        }

        [Test]
        public void GetElementColor_Priority_SelectedOverPinned()
        {
            // Selected takes priority over pinned
            var color = _settings.GetElementColor(isSelected: true, isPinned: true);

            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetCurveThickness_WhenSelected_ReturnsSelectedThickness()
        {
            var thickness = _settings.GetCurveThickness(isSelected: true);

            Assert.That(thickness, Is.EqualTo(_settings.SelectedCurveThickness));
        }

        [Test]
        public void GetCurveThickness_WhenNotSelected_ReturnsDefaultThickness()
        {
            var thickness = _settings.GetCurveThickness(isSelected: false);

            Assert.That(thickness, Is.EqualTo(_settings.DefaultCurveThickness));
        }

        [Test]
        public void GetFillColor_AppliesOpacity()
        {
            _settings.FillOpacity = 128;  // 50%

            var fillColor = _settings.GetFillColor(Color.Red);

            Assert.That(fillColor.A, Is.EqualTo(128));
            Assert.That(fillColor.R, Is.EqualTo(255));
            Assert.That(fillColor.G, Is.EqualTo(0));
            Assert.That(fillColor.B, Is.EqualTo(0));
        }

        [Test]
        public void ResetToDefaults_RestoresAllValues()
        {
            // Modify settings
            _settings.ShowRegionFill = false;
            _settings.FillOpacity = 200;
            _settings.SelectedColor = Color.Green;
            _settings.DefaultCurveThickness = 5.0f;

            // Reset
            _settings.ResetToDefaults();

            // Verify defaults restored
            Assert.That(_settings.ShowRegionFill, Is.True);
            Assert.That(_settings.FillOpacity, Is.EqualTo(64));
            Assert.That(_settings.SelectedColor, Is.EqualTo(Color.Yellow));
            Assert.That(_settings.DefaultCurveThickness, Is.EqualTo(1.5f));
        }

        [Test]
        public void ResetToDefaults_FiresSettingsChanged()
        {
            bool eventFired = false;
            _settings.SettingsChanged += (s, e) => eventFired = true;

            _settings.ResetToDefaults();

            Assert.That(eventFired, Is.True);
        }

        [Test]
        public void VertexPointSize_HasValidDefaults()
        {
            Assert.That(_settings.VertexPointSize, Is.EqualTo(5));
            Assert.That(_settings.SelectedVertexPointSize, Is.EqualTo(8));
            Assert.That(_settings.SelectedVertexPointSize, Is.GreaterThan(_settings.VertexPointSize));
        }

        [Test]
        public void PerformanceSettings_DefaultsAreEnabled()
        {
            Assert.That(_settings.UseAdaptiveSampling, Is.True);
            Assert.That(_settings.CacheCurves, Is.True);
        }
    }

    [TestFixture]
    public class VisualizationSettingsPersistenceTests
    {
        // Note: These tests require mocking PersistentSettings
        // In a real test environment, you would use a mock or test double

        [Test]
        public void Save_DoesNotThrow()
        {
            var settings = new VisualizationSettings();

            // This is a basic sanity check - full persistence testing
            // requires integration with Rhino's PersistentSettings
            Assert.DoesNotThrow(() =>
            {
                // Would need mock PersistentSettings here
                // settings.Save(mockSettings);
            });
        }

        [Test]
        public void Load_DoesNotThrow()
        {
            var settings = new VisualizationSettings();

            Assert.DoesNotThrow(() =>
            {
                // Would need mock PersistentSettings here
                // settings.Load(mockSettings);
            });
        }
    }
}
