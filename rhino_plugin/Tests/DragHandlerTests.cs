// rhino_plugin/Tests/DragHandlerTests.cs
using System;
using System.Collections.Generic;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Interaction;
using Latent.Geometry;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class DragPreviewTests
    {
        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            Assert.Throws<ArgumentNullException>(() => new DragPreview(null));
        }

        [Test]
        public void DefaultSettings_HaveReasonableValues()
        {
            var evaluator = new SubDEvaluator();
            var preview = new DragPreview(evaluator);

            Assert.That(preview.PreviewPointSize, Is.GreaterThan(0));
            Assert.That(preview.PreviewLineThickness, Is.GreaterThan(0));
            Assert.That(preview.ShowDisplacementLines, Is.True);
        }
    }

    [TestFixture]
    public class VertexDragHandlerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new VertexDragHandler(null, evaluator, subd));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new VertexDragHandler(manager, null, subd));
        }

        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();

            Assert.Throws<ArgumentNullException>(() =>
                new VertexDragHandler(manager, evaluator, null));
        }

        [Test]
        public void StartDrag_WithNullVertex_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() => handler.StartDrag(null));
        }

        [Test]
        public void ApplyDrag_WithNullVertex_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() =>
                handler.ApplyDrag(null, Point3d.Origin));
        }

        [Test]
        public void ApplyDrag_WithPinnedVertex_ReturnsPinned()
        {
            var handler = CreateHandler();
            // Use Latent.Interop.ParametricPoint
            var vertex = new Vertex("v1", new ParametricPoint(0, 0.5, 0.5))
            {
                IsPinned = true
            };

            var result = handler.ApplyDrag(vertex, Point3d.Origin);
            Assert.That(result, Is.EqualTo(DragResult.Pinned));
        }

        private VertexDragHandler CreateHandler()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();
            return new VertexDragHandler(manager, evaluator, subd);
        }

        private SubD CreateTestSubD()
        {
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            return SubD.CreateFromMesh(mesh);
        }
    }

    [TestFixture]
    public class EdgeDragHandlerTests
    {
        [Test]
        public void Constructor_WithNullRegionManager_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new EdgeDragHandler(null, evaluator, subd));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var subd = CreateTestSubD();

            Assert.Throws<ArgumentNullException>(() =>
                new EdgeDragHandler(manager, null, subd));
        }

        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();

            Assert.Throws<ArgumentNullException>(() =>
                new EdgeDragHandler(manager, evaluator, null));
        }

        [Test]
        public void StartDrag_WithNullEdge_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() => handler.StartDrag(null));
        }

        [Test]
        public void ApplyDrag_WithNullEdge_ThrowsArgumentNull()
        {
            var handler = CreateHandler();
            Assert.Throws<ArgumentNullException>(() =>
                handler.ApplyDrag(null, Vector3d.Zero));
        }

        [Test]
        public void ApplyDrag_WithPinnedEdge_ReturnsPinned()
        {
            var handler = CreateHandler();
            // Edge constructor takes List<string> (vertex IDs)
            // Vertices list is populated separately by RegionManager
            var edge = new Edge("e1", new List<string> { "v1", "v2" })
            {
                IsPinned = true
            };

            var result = handler.ApplyDrag(edge, Vector3d.Zero);
            Assert.That(result, Is.EqualTo(DragResult.Pinned));
        }

        private EdgeDragHandler CreateHandler()
        {
            var manager = new RegionManager();
            var evaluator = new SubDEvaluator();
            var subd = CreateTestSubD();
            return new EdgeDragHandler(manager, evaluator, subd);
        }

        private SubD CreateTestSubD()
        {
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            return SubD.CreateFromMesh(mesh);
        }
    }

    [TestFixture]
    public class DragResultTests
    {
        [Test]
        public void DragResult_HasExpectedValues()
        {
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Success), Is.True);
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Canceled), Is.True);
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Failed), Is.True);
            Assert.That(Enum.IsDefined(typeof(DragResult), DragResult.Pinned), Is.True);
        }
    }

    [TestFixture]
    public class VertexDragEventArgsTests
    {
        [Test]
        public void Constructor_SetsProperties()
        {
            // Use Latent.Interop.ParametricPoint
            var vertex = new Vertex("v1", new ParametricPoint(0, 0.5, 0.5));
            var position = new ParametricPoint(0, 0.6, 0.6);

            var args = new VertexDragEventArgs(vertex, position);

            Assert.That(args.Vertex, Is.SameAs(vertex));
            Assert.That(args.Position.FaceId, Is.EqualTo(position.FaceId));
        }
    }

    [TestFixture]
    public class EdgeDragEventArgsTests
    {
        [Test]
        public void Constructor_SetsProperties()
        {
            // Edge constructor takes List<string> (vertex IDs)
            var edge = new Edge("e1", new List<string> { "v1", "v2" });
            var positions = new List<ParametricPoint>
            {
                new ParametricPoint(0, 0.1, 0.1),
                new ParametricPoint(0, 1.1, 0.1)
            };

            var args = new EdgeDragEventArgs(edge, positions);

            Assert.That(args.Edge, Is.SameAs(edge));
            Assert.That(args.VertexPositions.Count, Is.EqualTo(positions.Count));
        }
    }
}
