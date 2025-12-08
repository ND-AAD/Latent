// rhino_plugin/Tests/CurveSamplerTests.cs
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
    public class CurveSamplerTests
    {
        private SubDEvaluator _evaluator;
        private CurveSampler _sampler;

        [SetUp]
        public void SetUp()
        {
            _evaluator = new SubDEvaluator();
            _sampler = new CurveSampler(_evaluator);
        }

        [TearDown]
        public void TearDown()
        {
            _evaluator?.Dispose();
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new CurveSampler(null));
        }

        [Test]
        public void SampleEdge_WithNullEdge_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => _sampler.SampleEdge(null, 50));
        }

        [Test]
        public void SampleEdgeAdaptive_WithNullEdge_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => _sampler.SampleEdgeAdaptive(null, 20));
        }

        [Test]
        public void SampleCurve_WithNullCurve_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => _sampler.SampleCurve(null, 50));
        }

        [Test]
        public void SampleEdge_WithNoVertices_ReturnsEmptyList()
        {
            var edge = new Edge("e1", new List<string>());
            var result = _sampler.SampleEdge(edge, 50);
            Assert.That(result, Is.Empty);
        }

        [Test]
        public void SampleEdgeAdaptive_WithNoVertices_ReturnsEmptyList()
        {
            var edge = new Edge("e1", new List<string>());
            var result = _sampler.SampleEdgeAdaptive(edge, 20);
            Assert.That(result, Is.Empty);
        }
    }

    [TestFixture]
    public class CurveCacheTests
    {
        private SubDEvaluator _evaluator;
        private CurveSampler _sampler;
        private CurveCache _cache;

        [SetUp]
        public void SetUp()
        {
            _evaluator = new SubDEvaluator();
            _sampler = new CurveSampler(_evaluator);
            _cache = new CurveCache(_sampler);
        }

        [TearDown]
        public void TearDown()
        {
            _evaluator?.Dispose();
        }

        [Test]
        public void Constructor_WithNullSampler_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new CurveCache(null));
        }

        [Test]
        public void GetOrSample_WithNullEdge_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => _cache.GetOrSample(null, 50));
        }

        [Test]
        public void GetOrSampleAdaptive_WithNullEdge_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => _cache.GetOrSampleAdaptive(null, 20));
        }

        [Test]
        public void Clear_ResetsCount()
        {
            _cache.Clear();
            Assert.That(_cache.Count, Is.EqualTo(0));
        }

        [Test]
        public void Invalidate_WithNullEdge_DoesNotThrow()
        {
            Assert.DoesNotThrow(() => _cache.Invalidate((Edge)null));
        }

        [Test]
        public void Invalidate_WithNullRegion_DoesNotThrow()
        {
            Assert.DoesNotThrow(() => _cache.Invalidate((Region)null));
        }

        [Test]
        public void Count_InitiallyZero()
        {
            Assert.That(_cache.Count, Is.EqualTo(0));
        }

        [Test]
        public void GetOrSample_CachesResults()
        {
            // Create edge with vertices
            var edge = new Edge("e1", new List<string> { "v1", "v2" })
            {
                Vertices = new List<Vertex>
                {
                    new Vertex("v1", new ParametricPoint(0, 0.0, 0.0)),
                    new Vertex("v2", new ParametricPoint(0, 1.0, 1.0))
                }
            };

            // First call should cache
            var result1 = _cache.GetOrSample(edge, 10);
            var count1 = _cache.Count;

            // Second call should use cache
            var result2 = _cache.GetOrSample(edge, 10);
            var count2 = _cache.Count;

            Assert.That(count1, Is.EqualTo(1));
            Assert.That(count2, Is.EqualTo(1));
            Assert.That(result1, Is.Not.Null);
            Assert.That(result2, Is.Not.Null);
        }

        [Test]
        public void Invalidate_RemovesEdgeFromCache()
        {
            // Create edge with vertices
            var edge = new Edge("e1", new List<string> { "v1", "v2" })
            {
                Vertices = new List<Vertex>
                {
                    new Vertex("v1", new ParametricPoint(0, 0.0, 0.0)),
                    new Vertex("v2", new ParametricPoint(0, 1.0, 1.0))
                }
            };

            // Cache the edge
            _cache.GetOrSample(edge, 10);
            Assert.That(_cache.Count, Is.EqualTo(1));

            // Invalidate
            _cache.Invalidate(edge);
            Assert.That(_cache.Count, Is.EqualTo(0));
        }

        [Test]
        public void VersionChange_InvalidatesCache()
        {
            // Create edge with vertices
            var edge = new Edge("e1", new List<string> { "v1", "v2" })
            {
                Vertices = new List<Vertex>
                {
                    new Vertex("v1", new ParametricPoint(0, 0.0, 0.0)),
                    new Vertex("v2", new ParametricPoint(0, 1.0, 1.0))
                }
            };

            // Cache the edge
            _cache.GetOrSample(edge, 10);
            Assert.That(_cache.Count, Is.EqualTo(1));

            // Increment version
            edge.IncrementVersion();

            // Cache with new version
            _cache.GetOrSample(edge, 10);
            
            // Should now have two entries (old version + new version)
            Assert.That(_cache.Count, Is.EqualTo(2));
        }

        [Test]
        public void GetOrSampleAdaptive_CachesSeparately()
        {
            // Create edge with vertices
            var edge = new Edge("e1", new List<string> { "v1", "v2" })
            {
                Vertices = new List<Vertex>
                {
                    new Vertex("v1", new ParametricPoint(0, 0.0, 0.0)),
                    new Vertex("v2", new ParametricPoint(0, 1.0, 1.0))
                }
            };

            // Cache uniform
            _cache.GetOrSample(edge, 10);
            Assert.That(_cache.Count, Is.EqualTo(1));

            // Cache adaptive
            _cache.GetOrSampleAdaptive(edge, 10);
            
            // Should have two entries (uniform + adaptive)
            Assert.That(_cache.Count, Is.EqualTo(2));
        }
    }

    [TestFixture]
    public class EdgeVersionTests
    {
        [Test]
        public void Version_InitiallyZero()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" });
            Assert.That(edge.Version, Is.EqualTo(0));
        }

        [Test]
        public void IncrementVersion_IncrementsValue()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" });
            Assert.That(edge.Version, Is.EqualTo(0));

            edge.IncrementVersion();
            Assert.That(edge.Version, Is.EqualTo(1));

            edge.IncrementVersion();
            Assert.That(edge.Version, Is.EqualTo(2));
        }

        [Test]
        public void RevertCurveType_IncrementsVersion()
        {
            var edge = new Edge(
                "e1",
                new List<string> { "v1", "v2" },
                CurveType.Linear,
                1,
                CurveType.Bezier,
                3
            );

            var initialVersion = edge.Version;
            edge.RevertCurveType();
            Assert.That(edge.Version, Is.EqualTo(initialVersion + 1));
        }
    }
}
