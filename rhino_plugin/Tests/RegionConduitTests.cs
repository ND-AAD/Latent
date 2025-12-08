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
}
