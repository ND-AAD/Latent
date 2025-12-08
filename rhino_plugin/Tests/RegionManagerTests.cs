// rhino_plugin/Tests/RegionManagerTests.cs
using System.Collections.Generic;
using NUnit.Framework;
using Latent.Geometry;
using Latent.Analysis;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class RegionManagerTests
    {
        private RegionManager _manager;

        [SetUp]
        public void SetUp()
        {
            _manager = new RegionManager();
        }

        [Test]
        public void UpdateFromAnalysis_PopulatesCollections()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            Assert.AreEqual(2, _manager.Vertices.Count);
            Assert.AreEqual(1, _manager.Edges.Count);
            Assert.AreEqual(1, _manager.Regions.Count);
        }

        [Test]
        public void GetVertex_ReturnsCorrectVertex()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            var vertex = _manager.GetVertex("v1");
            Assert.IsNotNull(vertex);
            Assert.AreEqual("v1", vertex!.Id);
        }

        [Test]
        public void SelectRegion_SetsSelected()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            _manager.SelectRegion("r1");

            var region = _manager.GetRegion("r1");
            Assert.IsTrue(region!.IsSelected);
        }

        [Test]
        public void SetPinned_UpdatesState()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            var vertex = _manager.GetVertex("v1");
            Assert.IsFalse(vertex!.IsPinned);

            _manager.SetPinned("v1", true);

            Assert.IsTrue(vertex.IsPinned);
        }

        [Test]
        public void Vertex_IsImplicit_WhenAtOriginalPosition()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos);

            Assert.IsTrue(vertex.IsImplicit);
        }

        [Test]
        public void Vertex_IsExplicit_WhenMoved()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var newPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", newPos, originalPos);

            Assert.IsFalse(vertex.IsImplicit);
        }

        [Test]
        public void Vertex_CannotRevert_WhenPinned()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var newPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", newPos, originalPos);
            vertex.IsPinned = true;

            Assert.IsFalse(vertex.CanRevert);
        }

        [Test]
        public void Vertex_CannotRevert_WhenFromCurveModification()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.CurveModification);

            Assert.IsFalse(vertex.CanRevert);
        }

        [Test]
        public void Edge_IsImplicit_WhenCurveTypeUnchanged()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" },
                CurveType.Bezier, 3, CurveType.Bezier, 3);

            Assert.IsTrue(edge.IsImplicit);
        }

        [Test]
        public void Edge_IsExplicit_WhenCurveTypeChanged()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" },
                CurveType.BSpline, 3, CurveType.Bezier, 3);

            Assert.IsFalse(edge.IsImplicit);
        }

        [Test]
        public void PinnedElements_PreservedOnReanalysis()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            // Pin a vertex
            _manager.SetPinned("v1", true);

            // Re-run analysis
            _manager.UpdateFromAnalysis(data);

            // Vertex should still be pinned
            var vertex = _manager.GetVertex("v1");
            Assert.IsTrue(vertex!.IsPinned);
        }

        [Test]
        public void ChangeEdgeCurveType_AddsVerticesWhenDegreeIncreases()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            // Increase degree from 3 to 5 (requires more control points)
            var addedIds = _manager.ChangeEdgeCurveType("e1", CurveType.Bezier, 5);

            // Should add vertices to make 6 control points (degree+1)
            Assert.That(addedIds.Count, Is.GreaterThan(0));

            var edge = _manager.GetEdge("e1");
            Assert.That(edge!.Degree, Is.EqualTo(5));
        }

        [Test]
        public void ChangeEdgeCurveType_AddedVertices_HaveParentEdgeId()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            var addedIds = _manager.ChangeEdgeCurveType("e1", CurveType.Bezier, 5);

            foreach (var id in addedIds)
            {
                var vertex = _manager.GetVertex(id);
                Assert.IsNotNull(vertex);
                Assert.That(vertex!.CreatedBy, Is.EqualTo(VertexOrigin.CurveModification));
                Assert.That(vertex.ParentEdgeId, Is.EqualTo("e1"));
            }
        }

        [Test]
        public void RevertEdgeCurveType_RemovesCurveModificationVertices()
        {
            var data = CreateTestAnalysisData();
            _manager.UpdateFromAnalysis(data);

            // Add curve modification vertices
            var addedIds = _manager.ChangeEdgeCurveType("e1", CurveType.Bezier, 5);
            Assert.That(addedIds.Count, Is.GreaterThan(0));

            // Revert the edge
            _manager.RevertEdgeCurveType("e1");

            // Curve modification vertices should be removed
            foreach (var id in addedIds)
            {
                var vertex = _manager.GetVertex(id);
                Assert.IsNull(vertex, $"Vertex {id} should have been removed on revert");
            }
        }

        private AnalysisResultData CreateTestAnalysisData()
        {
            return new AnalysisResultData
            {
                Vertices = new List<VertexData>
                {
                    new VertexData
                    {
                        Id = "v1",
                        Position = new List<double> { 0, 0.0, 0.0 },
                        CreatedBy = "lens"
                    },
                    new VertexData
                    {
                        Id = "v2",
                        Position = new List<double> { 0, 1.0, 1.0 },
                        CreatedBy = "lens"
                    }
                },
                Edges = new List<EdgeData>
                {
                    new EdgeData
                    {
                        Id = "e1",
                        VertexIds = new List<string> { "v1", "v2" },
                        CurveType = "bezier",
                        Degree = 3
                    }
                },
                Regions = new List<RegionData>
                {
                    new RegionData
                    {
                        Id = "r1",
                        BoundaryEdgeIds = new List<string> { "e1" },
                        UnityPrinciple = "Test",
                        ResonanceScore = 0.85
                    }
                }
            };
        }
    }
}
