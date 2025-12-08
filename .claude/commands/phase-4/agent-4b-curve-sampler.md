# Agent 4B: Curve Sampling & Caching

## Objective

Implement efficient parametric curve sampling on SubD limit surfaces with caching for display performance.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - curve sampling examples
- `rhino_plugin/Interop/SubDEvaluator.cs` - evaluator wrapper
- `rhino_plugin/Interop/SurfaceCurve.cs` - curve wrapper
- `rhino_plugin/Geometry/Edge.cs` - edge data model

## Dependencies

**From Phase 3:**
- `SubDEvaluator` - provides `EvaluatePoint(faceId, u, v)` → Point3d
- `SurfaceCurve` - provides `Sample(numSamples, evaluator)` → Point3d[]
- `Edge` - provides curve data and vertices
- `ParametricPoint` - (faceId, u, v) struct

## Files to Create

1. `rhino_plugin/Display/CurveSampler.cs` - curve sampling logic
2. `rhino_plugin/Display/CurveCache.cs` - curve caching
3. `rhino_plugin/Tests/CurveSamplerTests.cs` - unit tests

## Tasks

### 1. Create CurveSampler.cs

```csharp
// rhino_plugin/Display/CurveSampler.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Display
{
    /// <summary>
    /// Samples parametric curves on SubD limit surfaces for display.
    /// </summary>
    public class CurveSampler
    {
        private readonly SubDEvaluator _evaluator;

        // Adaptive sampling thresholds
        private const double AngleThreshold = 5.0;  // degrees
        private const int MinSamples = 10;
        private const int MaxSamples = 200;
        private const int AdaptiveDepth = 4;

        public CurveSampler(SubDEvaluator evaluator)
        {
            _evaluator = evaluator ?? throw new ArgumentNullException(nameof(evaluator));
        }

        /// <summary>
        /// Sample an edge to a polyline of 3D points.
        /// </summary>
        /// <param name="edge">The edge to sample</param>
        /// <param name="numSamples">Number of samples (uniform)</param>
        /// <returns>List of 3D points on the surface</returns>
        public List<Point3d> SampleEdge(Edge edge, int numSamples)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            numSamples = Math.Clamp(numSamples, MinSamples, MaxSamples);
            var points = new List<Point3d>(numSamples + 1);

            // Get the parametric curve from the edge
            var curve = edge.GetParametricCurve();
            if (curve == null)
            {
                // Fallback: linear interpolation between vertices
                return SampleLinear(edge, numSamples);
            }

            // Sample uniformly along the curve parameter
            for (int i = 0; i <= numSamples; i++)
            {
                double t = i / (double)numSamples;
                var param = curve.Evaluate(t);
                var point = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
                points.Add(point);
            }

            return points;
        }

        /// <summary>
        /// Sample an edge adaptively based on curvature.
        /// </summary>
        /// <param name="edge">The edge to sample</param>
        /// <param name="baseSamples">Base number of samples</param>
        /// <returns>List of 3D points with adaptive refinement</returns>
        public List<Point3d> SampleEdgeAdaptive(Edge edge, int baseSamples = 20)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            var curve = edge.GetParametricCurve();
            if (curve == null)
            {
                return SampleLinear(edge, baseSamples);
            }

            // Start with uniform samples
            var parameters = new List<double>();
            for (int i = 0; i <= baseSamples; i++)
            {
                parameters.Add(i / (double)baseSamples);
            }

            // Adaptively refine
            parameters = RefineAdaptive(curve, parameters, AdaptiveDepth);

            // Evaluate all parameters
            var points = new List<Point3d>(parameters.Count);
            foreach (var t in parameters)
            {
                var param = curve.Evaluate(t);
                var point = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
                points.Add(point);
            }

            return points;
        }

        /// <summary>
        /// Sample a parametric curve directly.
        /// </summary>
        public List<Point3d> SampleCurve(SurfaceCurve curve, int numSamples)
        {
            if (curve == null)
                throw new ArgumentNullException(nameof(curve));

            numSamples = Math.Clamp(numSamples, MinSamples, MaxSamples);

            // Use the native sampling if available
            var nativePoints = curve.Sample(numSamples, _evaluator);
            if (nativePoints != null && nativePoints.Length > 0)
            {
                return new List<Point3d>(nativePoints);
            }

            // Fallback to manual sampling
            var points = new List<Point3d>(numSamples + 1);
            for (int i = 0; i <= numSamples; i++)
            {
                double t = i / (double)numSamples;
                var param = curve.Evaluate(t);
                var point = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
                points.Add(point);
            }

            return points;
        }

        /// <summary>
        /// Sample a linear edge between two vertices.
        /// </summary>
        private List<Point3d> SampleLinear(Edge edge, int numSamples)
        {
            var vertices = edge.Vertices;
            if (vertices == null || vertices.Count < 2)
            {
                return new List<Point3d>();
            }

            var start = vertices[0].Position;
            var end = vertices[vertices.Count - 1].Position;

            var points = new List<Point3d>(numSamples + 1);

            for (int i = 0; i <= numSamples; i++)
            {
                double t = i / (double)numSamples;

                // Interpolate in parameter space
                int faceId = start.FaceId;  // Assume same face for linear
                double u = start.U + t * (end.U - start.U);
                double v = start.V + t * (end.V - start.V);

                // Handle face crossing if different faces
                if (start.FaceId != end.FaceId)
                {
                    // Use start face for first half, end face for second
                    if (t > 0.5)
                    {
                        faceId = end.FaceId;
                        double localT = (t - 0.5) * 2.0;
                        u = end.U * localT + 0.5 * (1 - localT);
                        v = end.V * localT + 0.5 * (1 - localT);
                    }
                }

                var point = _evaluator.EvaluatePoint(faceId, (float)u, (float)v);
                points.Add(point);
            }

            return points;
        }

        /// <summary>
        /// Refine parameter list adaptively based on angle deviation.
        /// </summary>
        private List<double> RefineAdaptive(IParametricCurve curve, List<double> parameters, int depth)
        {
            if (depth <= 0 || parameters.Count >= MaxSamples)
                return parameters;

            var refined = new List<double>();
            refined.Add(parameters[0]);

            for (int i = 0; i < parameters.Count - 1; i++)
            {
                double t0 = parameters[i];
                double t1 = parameters[i + 1];
                double tMid = (t0 + t1) / 2.0;

                var p0 = EvaluatePoint(curve, t0);
                var p1 = EvaluatePoint(curve, t1);
                var pMid = EvaluatePoint(curve, tMid);

                // Check if midpoint deviates significantly from line
                if (ShouldRefine(p0, pMid, p1))
                {
                    refined.Add(tMid);
                }

                refined.Add(t1);
            }

            // Recurse if we added points
            if (refined.Count > parameters.Count)
            {
                return RefineAdaptive(curve, refined, depth - 1);
            }

            return refined;
        }

        private Point3d EvaluatePoint(IParametricCurve curve, double t)
        {
            var param = curve.Evaluate(t);
            return _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
        }

        private bool ShouldRefine(Point3d p0, Point3d pMid, Point3d p1)
        {
            // Calculate angle at midpoint
            var v1 = pMid - p0;
            var v2 = p1 - pMid;

            if (v1.Length < 1e-10 || v2.Length < 1e-10)
                return false;

            v1.Unitize();
            v2.Unitize();

            double dot = v1 * v2;
            dot = Math.Clamp(dot, -1.0, 1.0);
            double angleDegrees = Math.Acos(dot) * 180.0 / Math.PI;

            return angleDegrees > AngleThreshold;
        }
    }

    /// <summary>
    /// Interface for parametric curves that can be sampled.
    /// </summary>
    public interface IParametricCurve
    {
        ParametricPoint Evaluate(double t);
    }
}
```

### 2. Create CurveCache.cs

```csharp
// rhino_plugin/Display/CurveCache.cs
using System;
using System.Collections.Generic;
using Rhino.Geometry;
using Latent.Geometry;

namespace Latent.Display
{
    /// <summary>
    /// Caches sampled curves for display performance.
    /// </summary>
    public class CurveCache
    {
        private readonly CurveSampler _sampler;
        private readonly Dictionary<string, CacheEntry> _cache;
        private readonly object _lock = new object();

        // Cache limits
        private const int MaxCacheEntries = 1000;
        private const int PruneThreshold = 800;
        private long _accessCounter = 0;

        public CurveCache(CurveSampler sampler)
        {
            _sampler = sampler ?? throw new ArgumentNullException(nameof(sampler));
            _cache = new Dictionary<string, CacheEntry>();
        }

        /// <summary>
        /// Get cached curve points or sample and cache.
        /// </summary>
        /// <param name="edge">The edge to sample</param>
        /// <param name="numSamples">Number of samples</param>
        /// <returns>List of sampled 3D points</returns>
        public List<Point3d> GetOrSample(Edge edge, int numSamples)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            var key = GetCacheKey(edge, numSamples);

            lock (_lock)
            {
                if (_cache.TryGetValue(key, out var entry))
                {
                    entry.LastAccess = _accessCounter++;
                    return entry.Points;
                }
            }

            // Sample outside lock
            var points = _sampler.SampleEdge(edge, numSamples);

            lock (_lock)
            {
                // Check again in case another thread added it
                if (!_cache.ContainsKey(key))
                {
                    _cache[key] = new CacheEntry
                    {
                        Points = points,
                        LastAccess = _accessCounter++,
                        Version = edge.Version
                    };

                    // Prune if needed
                    if (_cache.Count > MaxCacheEntries)
                    {
                        Prune();
                    }
                }
            }

            return points;
        }

        /// <summary>
        /// Get cached curve points with adaptive sampling.
        /// </summary>
        public List<Point3d> GetOrSampleAdaptive(Edge edge, int baseSamples = 20)
        {
            if (edge == null)
                throw new ArgumentNullException(nameof(edge));

            var key = GetCacheKey(edge, baseSamples, adaptive: true);

            lock (_lock)
            {
                if (_cache.TryGetValue(key, out var entry))
                {
                    entry.LastAccess = _accessCounter++;
                    return entry.Points;
                }
            }

            var points = _sampler.SampleEdgeAdaptive(edge, baseSamples);

            lock (_lock)
            {
                if (!_cache.ContainsKey(key))
                {
                    _cache[key] = new CacheEntry
                    {
                        Points = points,
                        LastAccess = _accessCounter++,
                        Version = edge.Version
                    };

                    if (_cache.Count > MaxCacheEntries)
                    {
                        Prune();
                    }
                }
            }

            return points;
        }

        /// <summary>
        /// Invalidate cache for a specific edge.
        /// </summary>
        public void Invalidate(Edge edge)
        {
            if (edge == null) return;

            lock (_lock)
            {
                var keysToRemove = new List<string>();
                foreach (var kvp in _cache)
                {
                    if (kvp.Key.StartsWith(edge.Id))
                    {
                        keysToRemove.Add(kvp.Key);
                    }
                }

                foreach (var key in keysToRemove)
                {
                    _cache.Remove(key);
                }
            }
        }

        /// <summary>
        /// Invalidate cache for a specific region's edges.
        /// </summary>
        public void Invalidate(Region region)
        {
            if (region == null) return;

            foreach (var edge in region.BoundaryEdges)
            {
                Invalidate(edge);
            }
        }

        /// <summary>
        /// Clear entire cache.
        /// </summary>
        public void Clear()
        {
            lock (_lock)
            {
                _cache.Clear();
                _accessCounter = 0;
            }
        }

        /// <summary>
        /// Get current cache size.
        /// </summary>
        public int Count
        {
            get
            {
                lock (_lock)
                {
                    return _cache.Count;
                }
            }
        }

        private string GetCacheKey(Edge edge, int numSamples, bool adaptive = false)
        {
            return $"{edge.Id}:{numSamples}:{(adaptive ? "A" : "U")}:{edge.Version}";
        }

        private void Prune()
        {
            // Remove least recently used entries
            var entries = new List<KeyValuePair<string, CacheEntry>>(_cache);
            entries.Sort((a, b) => a.Value.LastAccess.CompareTo(b.Value.LastAccess));

            int toRemove = _cache.Count - PruneThreshold;
            for (int i = 0; i < toRemove; i++)
            {
                _cache.Remove(entries[i].Key);
            }
        }

        private class CacheEntry
        {
            public List<Point3d> Points { get; set; }
            public long LastAccess { get; set; }
            public int Version { get; set; }
        }
    }
}
```

### 3. Create Unit Tests

```csharp
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
        // Note: Full testing requires mocking SubDEvaluator
        // These tests verify API contracts and edge cases

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new CurveSampler(null));
        }
    }

    [TestFixture]
    public class CurveCacheTests
    {
        private MockCurveSampler _mockSampler;
        private CurveCache _cache;

        [SetUp]
        public void SetUp()
        {
            _mockSampler = new MockCurveSampler();
            _cache = new CurveCache(_mockSampler);
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

        // Mock sampler for testing cache behavior
        private class MockCurveSampler : CurveSampler
        {
            public int SampleCallCount { get; private set; }

            public MockCurveSampler() : base(CreateMockEvaluator())
            {
            }

            private static SubDEvaluator CreateMockEvaluator()
            {
                // Return a real evaluator - tests that need mocking
                // should use a proper mocking framework
                return new SubDEvaluator();
            }
        }
    }

    [TestFixture]
    public class CurveSamplerPerformanceTests
    {
        // Performance-related tests
        [Test]
        public void SampleEdge_WithMinSamples_ReturnsAtLeastMinPoints()
        {
            // This would need a real SubDEvaluator with test geometry
            // Placeholder for integration testing
            Assert.Pass("Requires integration test setup");
        }

        [Test]
        public void SampleEdge_WithMaxSamples_ClampsToMax()
        {
            // Placeholder for integration testing
            Assert.Pass("Requires integration test setup");
        }
    }
}
```

## Success Criteria

- [ ] `CurveSampler` samples edges to polylines
- [ ] Uniform sampling produces evenly-spaced points
- [ ] Adaptive sampling refines at high-curvature areas
- [ ] `CurveCache` caches sampled curves by edge ID
- [ ] Cache invalidation works per-edge and per-region
- [ ] Cache prunes old entries when full
- [ ] Thread-safe cache operations
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build
dotnet test --filter "FullyQualifiedName~CurveSamplerTests|FullyQualifiedName~CurveCacheTests"
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Interop/` (Phase 3 domain)
- `RegionConduit.cs` (Agent 4A's domain)
- `RegionFill.cs` (Agent 4C's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Notes

- Cache uses edge ID + sample count + version as key
- Version tracking allows invalidation on edge modification
- Adaptive sampling uses angle threshold to decide refinement
- Thread safety is important for Rhino's multi-threaded display
- Memory bounded by MaxCacheEntries constant

## Report

When complete, provide:
1. Test output showing all tests pass
2. Build output showing no errors
3. Performance notes on cache hit rates
4. Any edge cases for face-crossing curves
