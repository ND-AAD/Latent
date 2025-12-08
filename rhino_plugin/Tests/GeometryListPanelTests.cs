// rhino_plugin/Tests/GeometryListPanelTests.cs
using System.Collections.Generic;
using NUnit.Framework;
using Latent.Geometry;
using Latent.UI;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class GeometryListItemTests
    {
        [Test]
        public void State_WhenImplicit_ReturnsImplicit()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.State, Is.EqualTo("implicit"));
        }

        [Test]
        public void State_WhenExplicit_ReturnsExplicit()
        {
            var originalPos = new ParametricPoint(0, 0.5f, 0.5f);
            var movedPos = new ParametricPoint(0, 0.6f, 0.5f);
            var vertex = new Vertex("v1", movedPos, originalPos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.State, Is.EqualTo("explicit"));
        }

        [Test]
        public void State_WhenPinned_ReturnsPinned()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos);
            vertex.IsPinned = true;

            var item = new GeometryListItem(vertex);

            Assert.That(item.State, Contains.Substring("pinned"));
        }

        [Test]
        public void CanRevert_WhenPinned_ReturnsFalse()
        {
            var originalPos = new ParametricPoint(0, 0.5f, 0.5f);
            var movedPos = new ParametricPoint(0, 0.6f, 0.5f);
            var vertex = new Vertex("v1", movedPos, originalPos);
            vertex.IsPinned = true;

            var item = new GeometryListItem(vertex);

            Assert.That(item.CanRevert, Is.False);
        }

        [Test]
        public void CanRevert_WhenExplicitAndNotPinned_ReturnsTrue()
        {
            var originalPos = new ParametricPoint(0, 0.5f, 0.5f);
            var movedPos = new ParametricPoint(0, 0.6f, 0.5f);
            var vertex = new Vertex("v1", movedPos, originalPos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.CanRevert, Is.True);
        }

        [Test]
        public void Details_ForVertex_ShowsOrigin()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.Lens);

            var item = new GeometryListItem(vertex);

            Assert.That(item.Details, Contains.Substring("Lens"));
        }

        [Test]
        public void Details_ForEdge_ShowsCurveType()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" },
                CurveType.Bezier, 3);

            var item = new GeometryListItem(edge);

            Assert.That(item.Details, Contains.Substring("Bezier"));
            Assert.That(item.Details, Contains.Substring("3"));
        }

        [Test]
        public void Details_ForRegion_ShowsResonanceScore()
        {
            var region = new Region("r1", new List<string> { "e1" },
                "High curvature", 0.85);

            var item = new GeometryListItem(region);

            Assert.That(item.Details, Contains.Substring("0.85"));
        }

        [Test]
        public void TypeName_ReturnsCorrectType()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos);
            var edge = new Edge("e1", new List<string>());
            var region = new Region("r1", new List<string>(), "test", 0.5);

            Assert.That(new GeometryListItem(vertex).TypeName, Is.EqualTo("Vertex"));
            Assert.That(new GeometryListItem(edge).TypeName, Is.EqualTo("Edge"));
            Assert.That(new GeometryListItem(region).TypeName, Is.EqualTo("Region"));
        }

        [Test]
        public void Id_MatchesElementId()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("test-vertex-123", pos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.Id, Is.EqualTo("test-vertex-123"));
        }
    }

    [TestFixture]
    public class GeometryListModeTests
    {
        [Test]
        public void Mode_HasExpectedValues()
        {
            Assert.That(GeometryListMode.Regions, Is.EqualTo((GeometryListMode)0));
            Assert.That(GeometryListMode.Edges, Is.EqualTo((GeometryListMode)1));
            Assert.That(GeometryListMode.Vertices, Is.EqualTo((GeometryListMode)2));
        }
    }

    [TestFixture]
    public class GeometrySortByTests
    {
        [Test]
        public void SortBy_HasExpectedValues()
        {
            Assert.That(GeometrySortBy.Id, Is.EqualTo((GeometrySortBy)0));
            Assert.That(GeometrySortBy.State, Is.EqualTo((GeometrySortBy)1));
            Assert.That(GeometrySortBy.Score, Is.EqualTo((GeometrySortBy)2));
        }
    }

    [TestFixture]
    public class ParentEdgeIdTrackingTests
    {
        [Test]
        public void Vertex_ParentEdgeId_WhenCurveModification_IsTracked()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.CurveModification, "edge_123");

            Assert.That(vertex.ParentEdgeId, Is.EqualTo("edge_123"));
        }

        [Test]
        public void Vertex_ParentEdgeId_WhenLens_IsNull()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.Lens);

            Assert.That(vertex.ParentEdgeId, Is.Null);
        }

        [Test]
        public void GeometryListItem_ParentEdgeId_ReturnsCurveModificationParent()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.CurveModification, "parent_edge");

            var item = new GeometryListItem(vertex);

            Assert.That(item.ParentEdgeId, Is.EqualTo("parent_edge"));
        }

        [Test]
        public void GeometryListItem_ParentEdgeId_ForNonCurveModification_ReturnsNull()
        {
            var pos = new ParametricPoint(0, 0.5f, 0.5f);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.Lens);

            var item = new GeometryListItem(vertex);

            Assert.That(item.ParentEdgeId, Is.Null);
        }

        [Test]
        public void GeometryListItem_ParentEdgeId_ForEdge_ReturnsNull()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" });

            var item = new GeometryListItem(edge);

            Assert.That(item.ParentEdgeId, Is.Null);
        }
    }
}
