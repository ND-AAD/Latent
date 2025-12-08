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
