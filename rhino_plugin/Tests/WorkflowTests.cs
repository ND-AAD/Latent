// rhino_plugin/Tests/WorkflowTests.cs
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using NUnit.Framework;
using Rhino.Geometry;
using Latent.Geometry;
using Latent.Interop;
using Latent.Analysis;
using Latent.Interaction;

namespace Latent.Tests
{
    /// <summary>
    /// Tests for complete user workflows.
    /// </summary>
    [TestFixture]
    public class WorkflowTests
    {
        private SubDEvaluator? _evaluator;
        private RegionManager? _regionManager;
        private SubD? _testSubD;

        [SetUp]
        public void SetUp()
        {
            _testSubD = TestHelpers.CreateTestBoxSubD();
            _evaluator = new SubDEvaluator();
            _evaluator.Initialize(_testSubD);
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

        #region Workflow: Analyze -> Select -> Edit -> Revert

        [Test]
        public void Workflow_AnalyzeSelectEditRevert_CompletesSuccessfully()
        {
            // Step 1: Load analysis results
            var analysisResult = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(analysisResult);
            Assert.That(_regionManager.Regions.Count, Is.EqualTo(2), "Should have 2 regions");

            // Step 2: Select a vertex
            var vertex = _regionManager.Vertices.First();
            _regionManager.SelectVertex(vertex.Id);
            Assert.That(vertex.IsSelected, Is.True, "Vertex should be selected");

            // Step 3: Move the vertex (explicit edit)
            var originalPosition = vertex.Position;
            var newPosition = new ParametricPoint(
                originalPosition.FaceId,
                Math.Min(originalPosition.U + 0.1, 1.0),
                originalPosition.V
            );
            _regionManager.MoveVertex(vertex.Id, newPosition);

            // Verify vertex is now explicit
            Assert.That(vertex.IsImplicit, Is.False, "Edited vertex should be explicit");
            Assert.That(vertex.CanRevert, Is.True, "Edited vertex should be revertable");

            // Step 4: Revert the vertex
            _regionManager.Revert(vertex.Id);

            // Verify vertex is back to implicit state
            Assert.That(vertex.IsImplicit, Is.True, "Reverted vertex should be implicit");
        }

        [Test]
        public void Workflow_PinPreventsDrag()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();

            // Pin the vertex
            _regionManager.SetPinned(vertex.Id, true);
            Assert.That(vertex.IsPinned, Is.True, "Vertex should be pinned");

            // Verify that CanRevert is false for pinned element
            Assert.That(vertex.CanRevert, Is.False, "Pinned vertex should not be revertable");
        }

        [Test]
        public void Workflow_UnpinAllowsRevert()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPosition = vertex.Position;

            // Edit vertex
            var newPosition = new ParametricPoint(
                originalPosition.FaceId,
                originalPosition.U + 0.1,
                originalPosition.V
            );
            _regionManager.MoveVertex(vertex.Id, newPosition);

            // Pin it
            _regionManager.SetPinned(vertex.Id, true);
            Assert.That(vertex.CanRevert, Is.False, "Pinned vertex cannot revert");

            // Unpin it
            _regionManager.SetPinned(vertex.Id, false);
            Assert.That(vertex.CanRevert, Is.True, "Unpinned explicit vertex can revert");

            // Now revert should work
            _regionManager.Revert(vertex.Id);
            Assert.That(vertex.IsImplicit, Is.True, "Should be back to implicit");
        }

        [Test]
        public void Workflow_RevertHierarchy_RegionRevertsEdgesAndVertices()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            // Move multiple vertices in the region
            var region = _regionManager.Regions.First();
            var modifiedVertexIds = new List<string>();

            foreach (var edgeId in region.BoundaryEdgeIds)
            {
                var edge = _regionManager.GetEdge(edgeId);
                if (edge == null) continue;

                foreach (var vertexId in edge.VertexIds)
                {
                    var vertex = _regionManager.GetVertex(vertexId);
                    if (vertex == null || !vertex.CanRevert) continue;

                    var newPos = new ParametricPoint(
                        vertex.Position.FaceId,
                        Math.Min(vertex.Position.U + 0.05, 1.0),
                        Math.Min(vertex.Position.V + 0.05, 1.0)
                    );
                    _regionManager.MoveVertex(vertex.Id, newPos);
                    modifiedVertexIds.Add(vertex.Id);
                }
            }

            // Verify region is now explicit
            Assert.That(region.IsImplicit, Is.False, "Region should be explicit after vertex edits");
            Assert.That(modifiedVertexIds.Count, Is.GreaterThan(0), "Should have modified some vertices");

            // Revert the entire region
            _regionManager.Revert(region.Id);

            // Verify all vertices are back to implicit
            foreach (var vertexId in modifiedVertexIds)
            {
                var vertex = _regionManager.GetVertex(vertexId);
                if (vertex?.ImplicitPosition != null)
                {
                    Assert.That(vertex.IsImplicit, Is.True,
                        $"Vertex {vertexId} should be implicit after region revert");
                }
            }
        }

        #endregion

        #region Workflow: Multi-Lens Analysis

        [Test]
        public void Workflow_ChangeLens_PreservesPinnedElements()
        {
            // First analysis (differential lens simulation)
            var result1 = TestHelpers.CreateMockAnalysisResult(2);
            result1.Regions[0].UnityPrinciple = "curvature_continuity";
            _regionManager!.UpdateFromAnalysis(result1);

            // Pin first region and record state
            var pinnedRegionId = result1.Regions[0].Id;
            _regionManager.SetPinned(pinnedRegionId, true);
            var originalPrinciple = _regionManager.GetRegion(pinnedRegionId)!.UnityPrinciple;

            // Second analysis (spectral lens simulation) - different regions
            var result2 = TestHelpers.CreateMockAnalysisResult(3);
            result2.Regions[0].Id = pinnedRegionId; // Same ID, different content
            result2.Regions[0].UnityPrinciple = "eigenfunction_nodal";
            _regionManager.UpdateFromAnalysis(result2);

            // Pinned region should be preserved with original principle
            var pinnedRegion = _regionManager.GetRegion(pinnedRegionId);
            Assert.That(pinnedRegion, Is.Not.Null, "Pinned region should still exist");
            Assert.That(pinnedRegion!.IsPinned, Is.True, "Region should still be pinned");
            Assert.That(pinnedRegion.UnityPrinciple, Is.EqualTo(originalPrinciple),
                "Pinned region should preserve original unity principle");
        }

        [Test]
        public void Workflow_UnpinnedElementsUpdateOnReanalysis()
        {
            var result1 = TestHelpers.CreateMockAnalysisResult(2);
            _regionManager!.UpdateFromAnalysis(result1);

            // Don't pin anything
            var region = _regionManager.GetRegion("r0");
            var originalScore = region!.ResonanceScore;

            // Re-analyze with different score
            var result2 = TestHelpers.CreateMockAnalysisResult(2);
            result2.Regions[0].ResonanceScore = 0.99;
            _regionManager.UpdateFromAnalysis(result2);

            // Unpinned region should update
            var updatedRegion = _regionManager.GetRegion("r0");
            Assert.That(updatedRegion!.ResonanceScore, Is.EqualTo(0.99).Within(0.001),
                "Unpinned region should update on reanalysis");
        }

        #endregion

        #region Workflow: Edge Curve Type Changes

        [Test]
        public void Workflow_ChangeCurveType_MarksEdgeExplicit()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            Assert.That(edge.IsImplicit, Is.True, "Edge should start implicit");

            // Change curve type using the actual API method
            _regionManager.ChangeEdgeCurveType(edge.Id, CurveType.BSpline, 4);

            Assert.That(edge.IsImplicit, Is.False, "Edge should be explicit after type change");
            Assert.That(edge.CurveType, Is.EqualTo(CurveType.BSpline));
            Assert.That(edge.Degree, Is.EqualTo(4));
        }

        [Test]
        public void Workflow_RevertEdgeCurveType_PreservesVertexPositions()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            var vertexId = edge.VertexIds.First();
            var vertex = _regionManager.GetVertex(vertexId)!;

            // Move vertex
            var newPos = new ParametricPoint(
                vertex.Position.FaceId,
                vertex.Position.U + 0.1,
                vertex.Position.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);

            // Change curve type
            _regionManager.ChangeEdgeCurveType(edge.Id, CurveType.BSpline, 4);

            // Revert only curve type (not positions)
            _regionManager.RevertEdgeCurveType(edge.Id);

            // Curve type should be reverted
            Assert.That(edge.CurveType, Is.EqualTo(edge.ImplicitCurveType),
                "Curve type should be reverted");

            // Vertex position should NOT be reverted
            Assert.That(vertex.IsImplicit, Is.False,
                "Vertex should still be explicit after curve-type-only revert");
        }

        [Test]
        public void Workflow_RevertEdgeFully_RevertsEverything()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var edge = _regionManager.Edges.First();
            var vertexId = edge.VertexIds.First();
            var vertex = _regionManager.GetVertex(vertexId)!;

            // Move vertex
            var newPos = new ParametricPoint(
                vertex.Position.FaceId,
                vertex.Position.U + 0.1,
                vertex.Position.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);

            // Change curve type
            _regionManager.ChangeEdgeCurveType(edge.Id, CurveType.BSpline, 4);

            // Fully revert edge
            _regionManager.RevertEdgeFully(edge.Id);

            // Both should be reverted
            Assert.That(edge.IsImplicit, Is.True, "Edge should be implicit");
            Assert.That(vertex.IsImplicit, Is.True, "Vertex should be implicit");
        }

        #endregion

        #region Performance Tests

        [Test]
        public void Performance_LargeAnalysisResult_LoadsQuickly()
        {
            var watch = Stopwatch.StartNew();

            // Create large analysis result (100 regions)
            var analysisResult = TestHelpers.CreateMockAnalysisResult(100);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(1000),
                $"Loading 100 regions should complete in under 1 second (took {watch.ElapsedMilliseconds}ms)");
            Assert.That(_regionManager.Regions.Count, Is.EqualTo(100));
        }

        [Test]
        public void Performance_SelectionChange_IsImmediate()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(50);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var watch = Stopwatch.StartNew();

            // Perform 100 selection changes
            for (int i = 0; i < 100; i++)
            {
                _regionManager.SelectRegion($"r{i % 50}");
            }

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(100),
                $"100 selection changes should complete in under 100ms (took {watch.ElapsedMilliseconds}ms)");
        }

        [Test]
        public void Performance_ManyPinOperations_AreEfficient()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(50);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var watch = Stopwatch.StartNew();

            // Pin/unpin all vertices
            foreach (var vertex in _regionManager.Vertices)
            {
                _regionManager.SetPinned(vertex.Id, true);
                _regionManager.SetPinned(vertex.Id, false);
            }

            watch.Stop();

            Assert.That(watch.ElapsedMilliseconds, Is.LessThan(500),
                $"Pin/unpin operations should be efficient (took {watch.ElapsedMilliseconds}ms)");
        }

        #endregion

        #region State Consistency Tests

        [Test]
        public void StateConsistency_ImplicitVertex_HasMatchingPosition()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            foreach (var vertex in _regionManager.Vertices)
            {
                if (vertex.IsImplicit && vertex.ImplicitPosition != null)
                {
                    Assert.That(vertex.Position.FaceId, Is.EqualTo(vertex.ImplicitPosition.Value.FaceId));
                    Assert.That(vertex.Position.U, Is.EqualTo(vertex.ImplicitPosition.Value.U).Within(0.0001));
                    Assert.That(vertex.Position.V, Is.EqualTo(vertex.ImplicitPosition.Value.V).Within(0.0001));
                }
            }
        }

        [Test]
        public void StateConsistency_ExplicitVertex_HasDifferentPosition()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPos = vertex.Position;

            // Move it
            var newPos = new ParametricPoint(
                originalPos.FaceId,
                originalPos.U + 0.2,
                originalPos.V
            );
            _regionManager.MoveVertex(vertex.Id, newPos);

            Assert.That(vertex.IsImplicit, Is.False);
            Assert.That(vertex.Position.U, Is.Not.EqualTo(vertex.ImplicitPosition!.Value.U).Within(0.0001));
        }

        [Test]
        public void StateConsistency_RegionImplicitness_DependsOnEdges()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var region = _regionManager.Regions.First();
            Assert.That(region.IsImplicit, Is.True, "Fresh region should be implicit");

            // Modify an edge's curve type
            var edgeId = region.BoundaryEdgeIds.First();
            _regionManager.ChangeEdgeCurveType(edgeId, CurveType.BSpline, 4);

            Assert.That(region.IsImplicit, Is.False, "Region with modified edge should be explicit");
        }

        #endregion

        #region Edge Cases

        [Test]
        public void EdgeCase_MoveVertexToSamePosition_RemainsImplicit()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalPos = vertex.Position;

            // "Move" to same position
            _regionManager.MoveVertex(vertex.Id, originalPos);

            // Should still be implicit since position didn't actually change
            Assert.That(vertex.IsImplicit, Is.True);
        }

        [Test]
        public void EdgeCase_PinUnpinCycle_PreservesState()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            var originalImplicit = vertex.IsImplicit;
            var originalPosition = vertex.Position;

            // Pin/unpin cycle
            _regionManager.SetPinned(vertex.Id, true);
            _regionManager.SetPinned(vertex.Id, false);

            Assert.That(vertex.IsImplicit, Is.EqualTo(originalImplicit));
            Assert.That(vertex.Position.FaceId, Is.EqualTo(originalPosition.FaceId));
            Assert.That(vertex.Position.U, Is.EqualTo(originalPosition.U));
            Assert.That(vertex.Position.V, Is.EqualTo(originalPosition.V));
        }

        [Test]
        public void EdgeCase_RevertAlreadyImplicit_NoChange()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            var vertex = _regionManager.Vertices.First();
            Assert.That(vertex.IsImplicit, Is.True);
            Assert.That(vertex.CanRevert, Is.False, "Implicit vertex should not be revertable");

            // Attempting revert on implicit vertex should not throw
            Assert.DoesNotThrow(() => _regionManager.Revert(vertex.Id));
        }

        [Test]
        public void EdgeCase_SelectNonexistent_NoException()
        {
            var analysisResult = TestHelpers.CreateMockAnalysisResult(1);
            _regionManager!.UpdateFromAnalysis(analysisResult);

            // Should not throw
            Assert.DoesNotThrow(() => _regionManager.SelectVertex("nonexistent"));
            Assert.DoesNotThrow(() => _regionManager.SelectEdge("nonexistent"));
            Assert.DoesNotThrow(() => _regionManager.SelectRegion("nonexistent"));
        }

        #endregion
    }
}
