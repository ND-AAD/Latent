// rhino_plugin/Tests/SurfaceGetPointTests.cs
using System;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Interaction;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class SurfaceConstrainedGetPointTests
    {
        [Test]
        public void Constructor_WithNullSubD_ThrowsArgumentNull()
        {
            var evaluator = new SubDEvaluator();
            Assert.Throws<ArgumentNullException>(() =>
                new SurfaceConstrainedGetPoint(null, evaluator));
        }

        [Test]
        public void Constructor_WithNullEvaluator_ThrowsArgumentNull()
        {
            var subd = CreateTestSubD();
            Assert.Throws<ArgumentNullException>(() =>
                new SurfaceConstrainedGetPoint(subd, null));
        }

        [Test]
        public void ShowNormal_DefaultsFalse()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            Assert.That(gp.ShowNormal, Is.False);
        }

        [Test]
        public void ShowParametricCoords_DefaultsTrue()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            Assert.That(gp.ShowParametricCoords, Is.True);
        }

        [Test]
        public void HasValidPosition_InitiallyFalse()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            Assert.That(gp.HasValidPosition, Is.False);
        }

        [Test]
        public void CurrentParametricPosition_InitiallyInvalid()
        {
            var subd = CreateTestSubD();
            var evaluator = new SubDEvaluator();
            var gp = new SurfaceConstrainedGetPoint(subd, evaluator);

            // FaceId of 0 (default int) with no projection done = check IsValid
            Assert.That(gp.CurrentParametricPosition.IsValid, Is.False);
        }

        private SubD CreateTestSubD()
        {
            // Create a simple box mesh and convert to SubD
            var mesh = Mesh.CreateFromBox(
                new BoundingBox(Point3d.Origin, new Point3d(1, 1, 1)),
                1, 1, 1);
            var options = new SubDCreationOptions();
            return SubD.CreateFromMesh(mesh, options);
        }
    }

    [TestFixture]
    public class SurfacePickResultTests
    {
        [Test]
        public void Success_WhenPointAndValidParam_ReturnsTrue()
        {
            var result = new SurfacePickResult
            {
                Result = Rhino.Input.GetResult.Point,
                ParametricPoint = new ParametricPoint(0, 0.5, 0.5)
            };

            Assert.That(result.Success, Is.True);
        }

        [Test]
        public void Success_WhenCanceled_ReturnsFalse()
        {
            var result = new SurfacePickResult
            {
                Result = Rhino.Input.GetResult.Cancel,
                ParametricPoint = new ParametricPoint(0, 0.5, 0.5)
            };

            Assert.That(result.Success, Is.False);
        }

        [Test]
        public void Success_WhenInvalidParam_ReturnsFalse()
        {
            var result = new SurfacePickResult
            {
                Result = Rhino.Input.GetResult.Point,
                ParametricPoint = ParametricPoint.Unset  // Invalid point
            };

            Assert.That(result.Success, Is.False);
        }
    }
}
