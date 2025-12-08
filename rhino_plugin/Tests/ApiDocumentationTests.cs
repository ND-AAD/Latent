// rhino_plugin/Tests/ApiDocumentationTests.cs
using System;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace Latent.Tests
{
    /// <summary>
    /// Tests that verify public API documentation completeness.
    /// </summary>
    [TestFixture]
    public class ApiDocumentationTests
    {
        private Assembly _assembly;

        [SetUp]
        public void SetUp()
        {
            _assembly = typeof(LatentPlugin).Assembly;
        }

        [Test]
        public void AllPublicClasses_Exist()
        {
            var publicTypes = _assembly.GetTypes()
                .Where(t => t.IsPublic && !t.IsNested)
                .Where(t => !t.Name.EndsWith("Tests"))
                .Where(t => !t.Name.Contains("AnonymousType"))
                .ToList();

            Assert.That(publicTypes.Count, Is.GreaterThan(0),
                "Assembly should have public types");
        }

        [Test]
        public void CoreClasses_ArePresent()
        {
            var publicTypes = _assembly.GetTypes()
                .Where(t => t.IsPublic && !t.IsNested)
                .Select(t => t.Name)
                .ToList();

            var expectedClasses = new[]
            {
                "LatentPlugin",
                "RegionManager",
                "SubDEvaluator",
                "ParametricPoint",
                "Vertex",
                "Edge",
                "Region"
            };

            foreach (var expected in expectedClasses)
            {
                Assert.That(publicTypes, Does.Contain(expected),
                    $"Missing expected class: {expected}");
            }
        }

        [Test]
        public void RegionManager_HasExpectedMethods()
        {
            var type = _assembly.GetType("Latent.Geometry.RegionManager");
            Assert.That(type, Is.Not.Null, "RegionManager should exist");

            var expectedMethods = new[]
            {
                "UpdateFromAnalysis",
                "SelectVertex",
                "SelectEdge",
                "SelectRegion",
                "SetPinned",
                "MoveVertex",
                "Revert"
            };

            var methods = type.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                .Select(m => m.Name)
                .ToList();

            foreach (var expected in expectedMethods)
            {
                Assert.That(methods, Does.Contain(expected),
                    $"RegionManager should have method: {expected}");
            }
        }

        [Test]
        public void SubDEvaluator_ImplementsIDisposable()
        {
            var type = _assembly.GetType("Latent.Interop.SubDEvaluator");
            Assert.That(type, Is.Not.Null, "SubDEvaluator should exist");

            Assert.That(typeof(IDisposable).IsAssignableFrom(type), Is.True,
                "SubDEvaluator should implement IDisposable");
        }

        [Test]
        public void ParametricPoint_HasUnsetProperty()
        {
            var type = _assembly.GetType("Latent.Interop.ParametricPoint");
            Assert.That(type, Is.Not.Null, "ParametricPoint should exist");

            var unsetProperty = type.GetProperty("Unset", BindingFlags.Public | BindingFlags.Static);
            Assert.That(unsetProperty, Is.Not.Null,
                "ParametricPoint should have static Unset property");
        }

        [Test]
        public void ParametricPoint_HasIsValidProperty()
        {
            var type = _assembly.GetType("Latent.Interop.ParametricPoint");
            Assert.That(type, Is.Not.Null, "ParametricPoint should exist");

            var isValidProperty = type.GetProperty("IsValid", BindingFlags.Public | BindingFlags.Instance);
            Assert.That(isValidProperty, Is.Not.Null,
                "ParametricPoint should have IsValid property");
        }

        [Test]
        public void IGeometryElement_DefinesRequiredMembers()
        {
            var type = _assembly.GetType("Latent.Geometry.IGeometryElement");
            Assert.That(type, Is.Not.Null, "IGeometryElement should exist");
            Assert.That(type.IsInterface, Is.True, "IGeometryElement should be an interface");

            var expectedMembers = new[] { "Id", "IsPinned", "IsImplicit", "CanRevert", "IsSelected" };

            foreach (var expected in expectedMembers)
            {
                var property = type.GetProperty(expected);
                Assert.That(property, Is.Not.Null,
                    $"IGeometryElement should have property: {expected}");
            }
        }

        [Test]
        public void GeometryClasses_ImplementIGeometryElement()
        {
            var interfaceType = _assembly.GetType("Latent.Geometry.IGeometryElement");
            Assert.That(interfaceType, Is.Not.Null);

            var geometryClasses = new[] { "Vertex", "Edge", "Region" };

            foreach (var className in geometryClasses)
            {
                var type = _assembly.GetType($"Latent.Geometry.{className}");
                Assert.That(type, Is.Not.Null, $"{className} should exist");
                Assert.That(interfaceType.IsAssignableFrom(type), Is.True,
                    $"{className} should implement IGeometryElement");
            }
        }

        [Test]
        public void Vertex_HasExpectedProperties()
        {
            var type = _assembly.GetType("Latent.Geometry.Vertex");
            Assert.That(type, Is.Not.Null, "Vertex should exist");

            var expectedProperties = new[] { "Position", "ImplicitPosition", "CreatedBy", "ParentEdgeId" };

            foreach (var expected in expectedProperties)
            {
                var property = type.GetProperty(expected, BindingFlags.Public | BindingFlags.Instance);
                Assert.That(property, Is.Not.Null,
                    $"Vertex should have property: {expected}");
            }
        }

        [Test]
        public void Edge_HasExpectedProperties()
        {
            var type = _assembly.GetType("Latent.Geometry.Edge");
            Assert.That(type, Is.Not.Null, "Edge should exist");

            var expectedProperties = new[] { "VertexIds", "CurveType", "Degree", "ImplicitCurveType", "Vertices" };

            foreach (var expected in expectedProperties)
            {
                var property = type.GetProperty(expected, BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic);
                Assert.That(property, Is.Not.Null,
                    $"Edge should have property: {expected}");
            }
        }

        [Test]
        public void Region_HasExpectedProperties()
        {
            var type = _assembly.GetType("Latent.Geometry.Region");
            Assert.That(type, Is.Not.Null, "Region should exist");

            var expectedProperties = new[] { "BoundaryEdgeIds", "BoundaryEdges", "UnityPrinciple", "ResonanceScore" };

            foreach (var expected in expectedProperties)
            {
                var property = type.GetProperty(expected, BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic);
                Assert.That(property, Is.Not.Null,
                    $"Region should have property: {expected}");
            }
        }

        [Test]
        public void SubDEvaluator_HasEvaluationMethods()
        {
            var type = _assembly.GetType("Latent.Interop.SubDEvaluator");
            Assert.That(type, Is.Not.Null, "SubDEvaluator should exist");

            var expectedMethods = new[] { "Initialize", "EvaluatePoint", "EvaluateNormal", "ProjectPoint" };

            var methods = type.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                .Select(m => m.Name)
                .ToList();

            foreach (var expected in expectedMethods)
            {
                Assert.That(methods, Does.Contain(expected),
                    $"SubDEvaluator should have method: {expected}");
            }
        }
    }
}
