// rhino_plugin/Tests/IntegrationTests.cs
using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;
using Latent.Analysis;
using Latent.Display;

namespace Latent.Tests
{
    /// <summary>
    /// Integration tests verifying component interactions.
    /// </summary>
    [TestFixture]
    public class IntegrationTests
    {
        private SubDEvaluator? _evaluator;
        private RegionManager? _regionManager;
        private SubD? _testSubD;

        [SetUp]
        public void SetUp()
        {
            _testSubD = TestHelpers.CreateTestBoxSubD();
            _evaluator = new SubDEvaluator();
            _regionManager = new RegionManager();
        }

        [TearDown]
        public void TearDown()
        {
            _evaluator?.Dispose();
            _evaluator = null;
            _regionManager = null;
            _testSubD = null;
        }

        #region Evaluator Integration

        [Test]
        public void Evaluator_InitializeWithSubD_Succeeds()
        {
            _evaluator!.Initialize(_testSubD!);

            Assert.That(_evaluator.IsInitialized, Is.True);
            Assert.That(_evaluator.FaceCount, Is.GreaterThan(0));
        }

        [Test]
        public void Evaluator_ForwardAndInverseEvaluation_RoundTrips()
        {
            _evaluator!.Initialize(_testSubD!);

            // Forward evaluation at face center
            var point3d = _evaluator.EvaluatePoint(0, 0.5, 0.5);
            Assert.That(point3d.IsValid, Is.True, "Forward evaluation should return valid point");

            // Inverse evaluation (project back)
            var param = _evaluator.ProjectPoint(point3d);
            Assert.That(param.IsValid, Is.True, "Projection should return valid parametric point");

            // Re-evaluate and compare
            var reprojected = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
            TestHelpers.AssertPointsEqual(point3d, reprojected, 0.001);
        }

        [Test]
        public void Evaluator_MultiplePointsRoundTrip_AllSucceed()
        {
            _evaluator!.Initialize(_testSubD!);

            var testParams = new[]
            {
                (0, 0.25, 0.25),
                (0, 0.75, 0.25),
                (0, 0.25, 0.75),
                (0, 0.75, 0.75),
                (0, 0.5, 0.5)
            };

            foreach (var (faceId, u, v) in testParams)
            {
                var point3d = _evaluator.EvaluatePoint(faceId, u, v);
                var param = _evaluator.ProjectPoint(point3d);

                Assert.That(param.IsValid, Is.True,
                    $"Projection failed for ({faceId}, {u}, {v})");

                var reprojected = _evaluator.EvaluatePoint(param.FaceId, param.U, param.V);
                TestHelpers.AssertPointsEqual(point3d, reprojected, 0.01);
            }
        }

        [Test]
        public void Evaluator_NormalEvaluation_ReturnsUnitVector()
        {
            _evaluator!.Initialize(_testSubD!);

            var normal = _evaluator.EvaluateNormal(0, 0.5, 0.5);

            Assert.That(normal.IsValid, Is.True);
            Assert.That(normal.Length, Is.EqualTo(1.0).Within(0.001),
                "Normal should be unit length");
        }

        [Test]
        public void Evaluator_CurvatureComputation_ReturnsValidValues()
        {
            _evaluator!.Initialize(_testSubD!);

            var analyzer = new CurvatureAnalyzer(_evaluator);
            var curvature = analyzer.ComputeCurvature(0, 0.5, 0.5);

            Assert.That(double.IsNaN(curvature.K1), Is.False, "K1 should not be NaN");
            Assert.That(double.IsNaN(curvature.K2), Is.False, "K2 should not be NaN");
            Assert.That(double.IsInfinity(curvature.K1), Is.False, "K1 should not be infinite");
            Assert.That(double.IsInfinity(curvature.K2), Is.False, "K2 should not be infinite");
        }

        #endregion

        #region RegionManager Integration

        [Test]
        public void RegionManager_UpdateFromAnalysis_PopulatesCorrectly()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(3);

            _regionManager!.UpdateFromAnalysis(analysisResult);

            Assert.That(_regionManager.Regions.Count, Is.EqualTo(3));
            Assert.That(_regionManager.Vertices.Count, Is.EqualTo(12));
            Assert.That(_regionManager.Edges.Count, Is.EqualTo(12));
        }

        [Test]
        public void RegionManager_GetById_ReturnsCorrectElements()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.GetVertex("v0");
            var edge = _regionManager.GetEdge("e0");
            var region = _regionManager.GetRegion("r0");

            Assert.That(vertex, Is.Not.Null);
            Assert.That(vertex!.Id, Is.EqualTo("v0"));

            Assert.That(edge, Is.Not.Null);
            Assert.That(edge!.Id, Is.EqualTo("e0"));

            Assert.That(region, Is.Not.Null);
            Assert.That(region!.Id, Is.EqualTo("r0"));
        }

        [Test]
        public void RegionManager_GetByInvalidId_ReturnsNull()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.GetVertex("nonexistent");
            var edge = _regionManager.GetEdge("nonexistent");
            var region = _regionManager.GetRegion("nonexistent");

            Assert.That(vertex, Is.Null);
            Assert.That(edge, Is.Null);
            Assert.That(region, Is.Null);
        }

        [Test]
        public void RegionManager_PinnedElementsPreservedOnReanalysis()
        {
            // Initial analysis
            var result1 = TestHelpers.CreateMockAnalysisResult(3);
            _regionManager!.UpdateFromAnalysis(result1);

            // Pin a vertex and record position
            var vertex = _regionManager.GetVertex("v0");
            Assert.That(vertex, Is.Not.Null);
            _regionManager.SetPinned("v0", true);
            var originalPosition = vertex!.Position;

            // Re-analyze with modified data
            var result2 = TestHelpers.CreateMockAnalysisResult(3);
            result2.Vertices[0].Position = new List<double> { 0, 0.99, 0.99 }; // Changed
            _regionManager.UpdateFromAnalysis(result2);

            // Pinned vertex should retain original position
            var pinnedVertex = _regionManager.GetVertex("v0");
            Assert.That(pinnedVertex, Is.Not.Null);
            Assert.That(pinnedVertex!.IsPinned, Is.True);
            Assert.That(pinnedVertex.Position.FaceId, Is.EqualTo(originalPosition.FaceId));
        }

        [Test]
        public void RegionManager_Selection_WorksAcrossTypes()
        {
            var result = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(result);

            // Select region
            _regionManager.SelectRegion("r0");
            Assert.That(_regionManager.GetRegion("r0")!.IsSelected, Is.True);

            // Select edge (should clear previous selection)
            _regionManager.SelectEdge("e0");
            Assert.That(_regionManager.GetRegion("r0")!.IsSelected, Is.False);
            Assert.That(_regionManager.GetEdge("e0")!.IsSelected, Is.True);

            // Select vertex (should clear previous selection)
            _regionManager.SelectVertex("v0");
            Assert.That(_regionManager.GetEdge("e0")!.IsSelected, Is.False);
            Assert.That(_regionManager.GetVertex("v0")!.IsSelected, Is.True);
        }

        [Test]
        public void RegionManager_ClearSelection_ClearsAll()
        {
            var result = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(result);

            _regionManager.SelectVertex("v0");
            Assert.That(_regionManager.GetVertex("v0")!.IsSelected, Is.True);

            _regionManager.ClearSelection();
            Assert.That(_regionManager.GetVertex("v0")!.IsSelected, Is.False);
        }

        [Test]
        public void RegionManager_ChangedEvent_FiresOnMutation()
        {
            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(result);

            var eventFired = false;
            _regionManager.Changed += (s, e) => eventFired = true;

            // Mutate
            _regionManager.SetPinned("v0", true);

            Assert.That(eventFired, Is.True, "Changed event should fire on mutation");
        }

        #endregion

        #region Display Integration

        [Test]
        public void VisualizationSettings_ColorPriority_SelectedOverPinned()
        {
            var settings = new VisualizationSettings();

            // Selected takes priority over pinned
            var color = settings.GetElementColor(isSelected: true, isPinned: true);
            Assert.That(color, Is.EqualTo(settings.SelectedColor));
        }

        [Test]
        public void VisualizationSettings_ColorPriority_PinnedOverNormal()
        {
            var settings = new VisualizationSettings();

            var pinnedColor = settings.GetElementColor(isSelected: false, isPinned: true);
            var normalColor = settings.GetElementColor(isSelected: false, isPinned: false);

            Assert.That(pinnedColor, Is.EqualTo(settings.PinnedColor));
            Assert.That(normalColor, Is.EqualTo(settings.DefaultCurveColor));
            Assert.That(pinnedColor, Is.Not.EqualTo(normalColor));
        }

        [Test]
        public void VisualizationSettings_DefaultValues_AreReasonable()
        {
            var settings = new VisualizationSettings();

            Assert.That(settings.ShowRegionFill, Is.True, "Fill should be on by default");
            Assert.That(settings.ShowCentroidMarkers, Is.True, "Centroids should be on by default");
            Assert.That(settings.CurveSampleCount, Is.GreaterThan(10), "Sample count should be reasonable");
        }

        [Test]
        public void RegionConduit_ConstructsWithValidDependencies()
        {
            var settings = new VisualizationSettings();
            var conduit = new RegionConduit(_regionManager!, settings);

            Assert.That(conduit, Is.Not.Null);
            Assert.That(conduit.Enabled, Is.False, "Should not be enabled by default");
        }

        #endregion

        #region CurveSampler Integration

        [Test]
        public void CurveSampler_SamplesEdgeCorrectly()
        {
            _evaluator!.Initialize(_testSubD!);

            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(result);

            var sampler = new CurveSampler(_evaluator);
            var edge = _regionManager.GetEdge("e0");

            var points = sampler.SampleEdge(edge!, 10);

            Assert.That(points, Is.Not.Null);
            Assert.That(points.Count, Is.EqualTo(10));
            foreach (var pt in points)
            {
                Assert.That(pt.IsValid, Is.True, "All sampled points should be valid");
            }
        }

        [Test]
        public void CurveSampler_EndpointsMatchVertices()
        {
            _evaluator!.Initialize(_testSubD!);

            var result = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(result);

            var sampler = new CurveSampler(_evaluator);
            var edge = _regionManager.GetEdge("e0");

            var points = sampler.SampleEdge(edge!, 10);

            // First and last points should be close to vertex positions
            var startVertex = _regionManager.GetVertex(edge!.VertexIds[0]);
            var endVertex = _regionManager.GetVertex(edge.VertexIds[edge.VertexIds.Count - 1]);

            var startPos = _evaluator.EvaluatePoint(
                startVertex!.Position.FaceId,
                startVertex.Position.U,
                startVertex.Position.V);

            Assert.That(points[0].DistanceTo(startPos), Is.LessThan(0.1),
                "First sample should be near start vertex");
        }

        #endregion

        #region ParametricPoint Integration

        [Test]
        public void ParametricPoint_Unset_IsNotValid()
        {
            var unset = ParametricPoint.Unset;

            Assert.That(unset.IsValid, Is.False);
            Assert.That(unset.FaceId, Is.LessThan(0));
        }

        [Test]
        public void ParametricPoint_ValidConstruction_IsValid()
        {
            var point = new ParametricPoint(0, 0.5, 0.5);

            Assert.That(point.IsValid, Is.True);
            Assert.That(point.FaceId, Is.EqualTo(0));
            Assert.That(point.U, Is.EqualTo(0.5));
            Assert.That(point.V, Is.EqualTo(0.5));
        }

        [Test]
        public void ParametricPoint_Equality_WorksCorrectly()
        {
            var p1 = new ParametricPoint(0, 0.5, 0.5);
            var p2 = new ParametricPoint(0, 0.5, 0.5);
            var p3 = new ParametricPoint(1, 0.5, 0.5);

            Assert.That(p1.Equals(p2), Is.True);
            Assert.That(p1.Equals(p3), Is.False);
        }

        #endregion
    }
}
