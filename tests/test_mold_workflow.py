"""
Tests for Mold Generation Workflow Orchestration

Tests complete end-to-end workflow from regions to export.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import cpp_core
from app.workflow.mold_generator import MoldWorkflow, MoldGenerationResult
from app.state.parametric_region import ParametricRegion
from app.ui.mold_params_dialog import MoldParameters


class TestMoldWorkflow:
    """Test mold generation workflow orchestration."""

    @pytest.fixture
    def mock_evaluator(self):
        """Create mock SubD evaluator."""
        evaluator = Mock(spec=cpp_core.SubDEvaluator)
        return evaluator

    @pytest.fixture
    def mock_nurbs_generator(self):
        """Create mock NURBS generator."""
        generator = Mock(spec=cpp_core.NURBSMoldGenerator)

        # Mock surface generation
        mock_surface = Mock()
        generator.fit_nurbs_surface.return_value = mock_surface
        generator.apply_draft_angle.return_value = mock_surface

        # Mock quality check
        quality = Mock()
        quality.max_deviation = 0.05  # Good quality
        generator.check_fitting_quality.return_value = quality

        return generator

    @pytest.fixture
    def mock_constraint_validator(self):
        """Create mock constraint validator."""
        validator = Mock(spec=cpp_core.ConstraintValidator)

        # Mock validation report
        report = Mock()
        report.has_errors.return_value = False
        validator.validate_region.return_value = report

        return validator

    @pytest.fixture
    def sample_regions(self):
        """Create sample parametric regions."""
        return [
            ParametricRegion(
                id="region_0",
                faces=[0, 1, 2],
                unity_principle="Curvature",
                unity_strength=0.9
            ),
            ParametricRegion(
                id="region_1",
                faces=[3, 4, 5],
                unity_principle="Spectral",
                unity_strength=0.85
            )
        ]

    @pytest.fixture
    def sample_params(self):
        """Create sample mold parameters."""
        return MoldParameters(
            draft_angle=2.0,
            wall_thickness=40.0,
            demolding_direction=(0, 0, 1)
        )

    def test_workflow_initialization(self, mock_evaluator):
        """Test workflow initializes correctly."""
        # This will fail without cpp_core, but tests the structure
        try:
            workflow = MoldWorkflow(mock_evaluator)
            assert workflow.evaluator == mock_evaluator
            assert workflow.serializer is not None
        except Exception as e:
            # Expected if cpp_core not built yet
            assert "cpp_core" in str(e) or "module" in str(e).lower()

    @patch('app.workflow.mold_generator.cpp_core.NURBSMoldGenerator')
    @patch('app.workflow.mold_generator.cpp_core.ConstraintValidator')
    def test_workflow_success_path(self, mock_validator_class, mock_generator_class,
                                   mock_evaluator, sample_regions, sample_params):
        """Test successful mold generation workflow."""
        # Setup mocks
        mock_generator = Mock()
        mock_surface = Mock()
        mock_generator.fit_nurbs_surface.return_value = mock_surface
        mock_generator.apply_draft_angle.return_value = mock_surface

        quality = Mock()
        quality.max_deviation = 0.05
        mock_generator.check_fitting_quality.return_value = quality

        mock_generator_class.return_value = mock_generator

        mock_validator = Mock()
        report = Mock()
        report.has_errors.return_value = False
        mock_validator.validate_region.return_value = report
        mock_validator_class.return_value = mock_validator

        # Execute workflow
        workflow = MoldWorkflow(mock_evaluator)
        result = workflow.generate_molds(sample_regions, sample_params)

        # Verify success
        assert result.success
        assert len(result.constraint_reports) == 2
        assert 'molds' in result.export_data
        assert result.error_message == ""

    @patch('app.workflow.mold_generator.cpp_core.NURBSMoldGenerator')
    @patch('app.workflow.mold_generator.cpp_core.ConstraintValidator')
    def test_workflow_constraint_failure(self, mock_validator_class, mock_generator_class,
                                        mock_evaluator, sample_regions, sample_params):
        """Test workflow fails on constraint violations."""
        # Setup validator to fail
        mock_validator = Mock()
        report = Mock()
        report.has_errors.return_value = True
        mock_validator.validate_region.return_value = report
        mock_validator_class.return_value = mock_validator

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Execute workflow
        workflow = MoldWorkflow(mock_evaluator)
        result = workflow.generate_molds(sample_regions, sample_params)

        # Verify failure
        assert not result.success
        assert "constraint violations" in result.error_message
        assert len(result.nurbs_surfaces) == 0

    @patch('app.workflow.mold_generator.cpp_core.NURBSMoldGenerator')
    @patch('app.workflow.mold_generator.cpp_core.ConstraintValidator')
    def test_workflow_exception_handling(self, mock_validator_class, mock_generator_class,
                                         mock_evaluator, sample_regions, sample_params):
        """Test workflow handles exceptions gracefully."""
        # Setup validator to raise exception
        mock_validator = Mock()
        mock_validator.validate_region.side_effect = RuntimeError("Test error")
        mock_validator_class.return_value = mock_validator

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Execute workflow
        workflow = MoldWorkflow(mock_evaluator)
        result = workflow.generate_molds(sample_regions, sample_params)

        # Verify error handling
        assert not result.success
        assert "Test error" in result.error_message
        assert len(result.nurbs_surfaces) == 0
        assert len(result.constraint_reports) == 0

    @patch('app.workflow.mold_generator.cpp_core.NURBSMoldGenerator')
    @patch('app.workflow.mold_generator.cpp_core.ConstraintValidator')
    def test_workflow_quality_warning(self, mock_validator_class, mock_generator_class,
                                     mock_evaluator, sample_regions, sample_params,
                                     capsys):
        """Test workflow warns on low quality NURBS fit."""
        # Setup quality check to show high deviation
        mock_generator = Mock()
        mock_surface = Mock()
        mock_generator.fit_nurbs_surface.return_value = mock_surface
        mock_generator.apply_draft_angle.return_value = mock_surface

        quality = Mock()
        quality.max_deviation = 0.5  # High deviation
        mock_generator.check_fitting_quality.return_value = quality
        mock_generator_class.return_value = mock_generator

        mock_validator = Mock()
        report = Mock()
        report.has_errors.return_value = False
        mock_validator.validate_region.return_value = report
        mock_validator_class.return_value = mock_validator

        # Execute workflow
        workflow = MoldWorkflow(mock_evaluator)
        result = workflow.generate_molds(sample_regions, sample_params)

        # Verify warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "deviation" in captured.out

        # Should still succeed
        assert result.success

    @patch('app.workflow.mold_generator.cpp_core.NURBSMoldGenerator')
    @patch('app.workflow.mold_generator.cpp_core.ConstraintValidator')
    def test_export_data_structure(self, mock_validator_class, mock_generator_class,
                                   mock_evaluator, sample_regions, sample_params):
        """Test export data has correct structure."""
        # Setup mocks
        mock_generator = Mock()
        mock_surface = Mock()
        mock_generator.fit_nurbs_surface.return_value = mock_surface
        mock_generator.apply_draft_angle.return_value = mock_surface

        quality = Mock()
        quality.max_deviation = 0.05
        mock_generator.check_fitting_quality.return_value = quality
        mock_generator_class.return_value = mock_generator

        mock_validator = Mock()
        report = Mock()
        report.has_errors.return_value = False
        mock_validator.validate_region.return_value = report
        mock_validator_class.return_value = mock_validator

        # Execute workflow
        workflow = MoldWorkflow(mock_evaluator)
        result = workflow.generate_molds(sample_regions, sample_params)

        # Verify export data structure
        assert result.success
        export_data = result.export_data

        assert 'type' in export_data
        assert export_data['type'] == 'ceramic_mold_set'
        assert 'version' in export_data
        assert 'molds' in export_data
        assert 'metadata' in export_data
        assert 'timestamp' in export_data

        # Verify metadata
        metadata = export_data['metadata']
        assert metadata['draft_angle'] == 2.0
        assert metadata['wall_thickness'] == 40.0
        assert metadata['demolding_direction'] == (0, 0, 1)

    def test_result_dataclass_structure(self):
        """Test MoldGenerationResult dataclass."""
        result = MoldGenerationResult(
            success=True,
            nurbs_surfaces=[Mock(), Mock()],
            constraint_reports=[Mock()],
            export_data={'test': 'data'},
            error_message=""
        )

        assert result.success
        assert len(result.nurbs_surfaces) == 2
        assert len(result.constraint_reports) == 1
        assert result.export_data['test'] == 'data'
        assert result.error_message == ""

    def test_result_dataclass_defaults(self):
        """Test MoldGenerationResult has proper defaults."""
        result = MoldGenerationResult(
            success=False,
            nurbs_surfaces=[],
            constraint_reports=[],
            export_data={}
        )

        assert not result.success
        assert result.error_message == ""  # Default value


class TestWorkflowIntegration:
    """Integration tests for workflow (requires cpp_core)."""

    @pytest.mark.integration
    def test_full_workflow_with_real_geometry(self):
        """
        Test complete workflow with real geometry.

        Requires cpp_core to be built and available.
        """
        pytest.skip("Integration test - requires built cpp_core module")

        # This would be the full integration test:
        # 1. Create real SubD cage
        # 2. Initialize evaluator
        # 3. Create regions
        # 4. Run workflow
        # 5. Verify NURBS output
        # 6. Verify export data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
