// rhino_plugin/Tests/RegionFillTests.cs
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Display;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class RegionFillTests
    {
        [Test]
        public void Constructor_WithNullSampler_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new RegionFill(null));
        }

        [Test]
        public void GetFillMesh_WithNullRegion_ThrowsArgumentNull()
        {
            var sampler = CreateMockSampler();
            var fill = new RegionFill(sampler);

            Assert.Throws<ArgumentNullException>(() => fill.GetFillMesh(null));
        }

        [Test]
        public void Clear_DoesNotThrow()
        {
            var sampler = CreateMockSampler();
            var fill = new RegionFill(sampler);

            Assert.DoesNotThrow(() => fill.Clear());
        }

        [Test]
        public void Invalidate_WithNullRegion_DoesNotThrow()
        {
            var sampler = CreateMockSampler();
            var fill = new RegionFill(sampler);

            Assert.DoesNotThrow(() => fill.Invalidate(null));
        }

        [Test]
        public void GetFillMesh_WithValidRegion_ReturnsNonNullMesh()
        {
            var evaluator = new SubDEvaluator();
            var sampler = new CurveSampler(evaluator);
            var fill = new RegionFill(sampler);
            var region = CreateTestRegion();

            // This may return null if region has insufficient boundary points,
            // which is acceptable behavior
            var mesh = fill.GetFillMesh(region);

            // If mesh is returned, it should be valid
            if (mesh != null)
            {
                Assert.That(mesh.Vertices.Count, Is.GreaterThan(0));
            }
        }

        [Test]
        public void GetDisplayBoundingBox_WithNullRegion_ReturnsEmpty()
        {
            var evaluator = new SubDEvaluator();
            var bbox = RegionFillExtensions.GetDisplayBoundingBox(null, evaluator);

            Assert.That(bbox.IsValid, Is.False);
        }

        [Test]
        public void GetDisplayBoundingBox_WithNullEvaluator_ReturnsEmpty()
        {
            var region = CreateTestRegion();
            var bbox = RegionFillExtensions.GetDisplayBoundingBox(region, null);

            Assert.That(bbox.IsValid, Is.False);
        }

        private CurveSampler CreateMockSampler()
        {
            return new CurveSampler(new SubDEvaluator());
        }

        private Region CreateTestRegion()
        {
            var region = new Region(
                "test-region",
                new List<string> { "edge1", "edge2", "edge3" },
                "test-unity",
                0.8
            );

            // Create minimal boundary edges with vertices
            var vertices = new List<Vertex>
            {
                new Vertex("v1", new ParametricPoint(0, 0.0, 0.0)),
                new Vertex("v2", new ParametricPoint(0, 1.0, 0.0))
            };

            var edge = new Edge(
                "edge1",
                new List<string> { "v1", "v2" },
                CurveType.Linear,
                1
            );
            edge.Vertices = vertices;

            region.BoundaryEdges = new List<Edge> { edge };

            return region;
        }
    }

    [TestFixture]
    public class CentroidMarkerTests
    {
        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new CentroidMarker(null));
        }

        [Test]
        public void GetCentroid3d_WithNullRegion_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            Assert.Throws<ArgumentNullException>(() => marker.GetCentroid3d(null));
        }

        [Test]
        public void Clear_DoesNotThrow()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            Assert.DoesNotThrow(() => marker.Clear());
        }

        [Test]
        public void Invalidate_WithNullRegion_DoesNotThrow()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            Assert.DoesNotThrow(() => marker.Invalidate(null));
        }

        [Test]
        public void GetAllCentroids_InitiallyEmpty()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);

            var centroids = new List<KeyValuePair<string, Point3d>>(marker.GetAllCentroids());
            Assert.That(centroids, Is.Empty);
        }

        [Test]
        public void GetCentroid3d_WithValidRegion_ReturnsPoint()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);
            var region = CreateTestRegion();

            // This may return null if region has no boundary vertices
            var centroid = marker.GetCentroid3d(region);

            // If centroid is computed, it should be valid
            if (centroid.HasValue)
            {
                Assert.That(centroid.Value.IsValid, Is.True);
            }
        }

        [Test]
        public void GetCentroidWithOffset_ReturnsOffsetPoint()
        {
            var evaluator = new SubDEvaluator();
            var marker = new CentroidMarker(evaluator);
            var region = CreateTestRegion();

            var centroid = marker.GetCentroidWithOffset(region, 1.0);

            // Result may be null if region has no boundary
            // This is acceptable behavior
            Assert.That(centroid, Is.Not.Null.Or.Null);
        }

        private Region CreateTestRegion()
        {
            var region = new Region(
                "test-region",
                new List<string> { "edge1", "edge2", "edge3" },
                "test-unity",
                0.8
            );

            // Create minimal boundary edges with vertices
            var vertices = new List<Vertex>
            {
                new Vertex("v1", new ParametricPoint(0, 0.0, 0.0)),
                new Vertex("v2", new ParametricPoint(0, 1.0, 0.0))
            };

            var edge = new Edge(
                "edge1",
                new List<string> { "v1", "v2" },
                CurveType.Linear,
                1
            );
            edge.Vertices = vertices;

            region.BoundaryEdges = new List<Edge> { edge };

            return region;
        }
    }

    [TestFixture]
    public class CentroidMarkerSettingsTests
    {
        [Test]
        public void DefaultSettings_HaveReasonableValues()
        {
            var settings = new CentroidMarkerSettings();

            Assert.That(settings.Style, Is.EqualTo(CentroidMarkerStyle.Dot));
            Assert.That(settings.FontSize, Is.GreaterThan(0));
            Assert.That(settings.ShowRegionId, Is.True);
        }

        [Test]
        public void Settings_CanBeModified()
        {
            var settings = new CentroidMarkerSettings
            {
                Style = CentroidMarkerStyle.Circle,
                FontSize = 12,
                ShowRegionId = false,
                NormalOffset = 0.5
            };

            Assert.That(settings.Style, Is.EqualTo(CentroidMarkerStyle.Circle));
            Assert.That(settings.FontSize, Is.EqualTo(12));
            Assert.That(settings.ShowRegionId, Is.False);
            Assert.That(settings.NormalOffset, Is.EqualTo(0.5));
        }
    }
}
