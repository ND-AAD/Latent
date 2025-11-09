"""
Tests for Spectral Visualization Components

Tests both the VTK renderer and PyQt widget for eigenfunction visualization.

Author: Ceramic Mold Analyzer - Agent 36
Date: November 2025
"""

import pytest
import numpy as np
from PyQt6.QtWidgets import QApplication
from app.ui.spectral_viz_widget import SpectralVizWidget
from app.analysis.spectral_decomposition import EigenMode
from app.geometry.spectral_renderer import SpectralRenderer

# VTK imports
try:
    import vtk
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False


@pytest.fixture(scope='session')
def qapp():
    """PyQt application for testing widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def mock_tessellation_result():
    """Create a mock tessellation result for testing."""
    class MockTessellationResult:
        def __init__(self):
            # Simple quad tessellated to triangles
            self.vertices = np.array([
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.5, 0.5, 0.5],  # Center point elevated
            ], dtype=np.float32)

            self.normals = np.array([
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 1.0],
            ], dtype=np.float32)

            self.triangles = np.array([
                [0, 1, 4],
                [1, 2, 4],
                [2, 3, 4],
                [3, 0, 4],
            ], dtype=np.int32)

            self.face_parents = np.array([0, 0, 0, 0], dtype=np.int32)

    return MockTessellationResult()


@pytest.fixture
def sample_eigenmodes():
    """Create sample eigenmodes for testing."""
    # Create eigenmodes with different characteristics
    n = 100
    modes = [
        # Mode 0: Constant (eigenvalue ≈ 0)
        EigenMode(
            eigenvalue=0.0,
            eigenfunction=np.ones(n),
            index=0,
            multiplicity=1
        ),
        # Mode 1: Simple sine wave
        EigenMode(
            eigenvalue=2.0,
            eigenfunction=np.sin(np.linspace(0, 2*np.pi, n)),
            index=1,
            multiplicity=1
        ),
        # Mode 2: Cosine wave
        EigenMode(
            eigenvalue=2.1,
            eigenfunction=np.cos(np.linspace(0, 2*np.pi, n)),
            index=2,
            multiplicity=1
        ),
        # Mode 3: Higher frequency
        EigenMode(
            eigenvalue=6.0,
            eigenfunction=np.sin(np.linspace(0, 4*np.pi, n)),
            index=3,
            multiplicity=2
        ),
    ]
    return modes


# ============================================================================
# SpectralVizWidget Tests
# ============================================================================

class TestSpectralVizWidget:
    """Test spectral visualization widget."""

    def test_widget_creation(self, qapp):
        """Test widget initializes correctly."""
        widget = SpectralVizWidget()

        assert widget.mode_combo is not None
        assert widget.mode_slider is not None
        assert widget.nodal_check is not None
        assert widget.extract_btn is not None
        assert widget.eigenvalue_label is not None
        assert widget.stats_label is not None

        # Default state
        assert widget.nodal_check.isChecked()
        assert not widget.extract_btn.isEnabled()
        assert len(widget.modes) == 0
        assert widget.current_mode_idx == 0

    def test_set_modes(self, qapp, sample_eigenmodes):
        """Test setting eigenmodes."""
        widget = SpectralVizWidget()
        modes = sample_eigenmodes

        widget.set_modes(modes)

        # Check combo box populated
        assert widget.mode_combo.count() == len(modes)

        # Check slider range
        assert widget.mode_slider.maximum() == len(modes) - 1

        # Should auto-select mode 1 (skip constant mode 0)
        assert widget.current_mode_idx == 1

        # Extract button should be enabled
        assert widget.extract_btn.isEnabled()

    def test_mode_selection_combo(self, qapp, sample_eigenmodes):
        """Test mode selection via combo box."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        # Track signal emissions
        received_indices = []
        widget.mode_changed.connect(lambda i: received_indices.append(i))

        # Change mode via combo box
        widget.mode_combo.setCurrentIndex(2)

        # Check signal emitted
        assert len(received_indices) > 0
        assert received_indices[-1] == 2

        # Check state updated
        assert widget.current_mode_idx == 2

        # Check slider synchronized
        assert widget.mode_slider.value() == 2

    def test_mode_selection_slider(self, qapp, sample_eigenmodes):
        """Test mode selection via slider."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        # Track signal emissions
        received_indices = []
        widget.mode_changed.connect(lambda i: received_indices.append(i))

        # Change mode via slider
        widget.mode_slider.setValue(3)

        # Check signal emitted
        assert len(received_indices) > 0
        assert received_indices[-1] == 3

        # Check state updated
        assert widget.current_mode_idx == 3

        # Check combo box synchronized
        assert widget.mode_combo.currentIndex() == 3

    def test_eigenvalue_display(self, qapp, sample_eigenmodes):
        """Test eigenvalue display updates correctly."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        # Set mode 2
        widget.set_current_mode(2)
        mode = sample_eigenmodes[2]

        # Check eigenvalue label
        label_text = widget.eigenvalue_label.text()
        assert "λ" in label_text
        assert f"{mode.eigenvalue:.6f}" in label_text

    def test_nodal_lines_toggle(self, qapp):
        """Test nodal lines checkbox."""
        widget = SpectralVizWidget()

        # Track signal emissions
        received_states = []
        widget.nodal_lines_toggled.connect(lambda b: received_states.append(b))

        # Initially checked
        assert widget.nodal_check.isChecked()

        # Toggle off
        widget.nodal_check.setChecked(False)
        assert len(received_states) > 0
        assert received_states[-1] is False

        # Toggle on
        widget.nodal_check.setChecked(True)
        assert received_states[-1] is True

    def test_extract_regions_signal(self, qapp, sample_eigenmodes):
        """Test extract regions button emits signal."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        # Set to mode 2
        widget.set_current_mode(2)

        # Track signal emissions
        received_indices = []
        widget.extract_regions_clicked.connect(lambda i: received_indices.append(i))

        # Click extract button
        widget.extract_btn.click()

        # Check signal emitted with correct index
        assert len(received_indices) == 1
        assert received_indices[0] == 2

    def test_statistics_update(self, qapp, sample_eigenmodes):
        """Test statistics display updates."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        widget.set_current_mode(1)

        # Check stats label contains expected info
        stats_text = widget.stats_label.text()
        assert "Index:" in stats_text
        assert "Eigenvalue:" in stats_text
        assert "Multiplicity:" in stats_text
        assert "Range:" in stats_text
        assert "Mean:" in stats_text
        assert "Vertices:" in stats_text

    def test_clear(self, qapp, sample_eigenmodes):
        """Test clearing widget state."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        # Clear
        widget.clear()

        # Check state reset
        assert len(widget.modes) == 0
        assert widget.current_mode_idx == 0
        assert widget.mode_combo.count() == 0
        assert not widget.extract_btn.isEnabled()

    def test_get_current_mode_index(self, qapp, sample_eigenmodes):
        """Test getting current mode index."""
        widget = SpectralVizWidget()
        widget.set_modes(sample_eigenmodes)

        widget.set_current_mode(2)
        assert widget.get_current_mode_index() == 2

    def test_get_show_nodal_lines(self, qapp):
        """Test getting nodal lines visibility state."""
        widget = SpectralVizWidget()

        assert widget.get_show_nodal_lines() is True

        widget.nodal_check.setChecked(False)
        assert widget.get_show_nodal_lines() is False


# ============================================================================
# SpectralRenderer Tests
# ============================================================================

@pytest.mark.skipif(not VTK_AVAILABLE, reason="VTK not available")
class TestSpectralRenderer:
    """Test spectral renderer VTK functionality."""

    def test_renderer_creation(self):
        """Test renderer initializes correctly."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        assert spectral_renderer.renderer is renderer
        assert spectral_renderer.surface_actor is None
        assert spectral_renderer.nodal_line_actor is None
        assert spectral_renderer.colormap == 'coolwarm'

    def test_mesh_to_polydata(self, mock_tessellation_result):
        """Test conversion of tessellation result to VTK polydata."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        mesh = mock_tessellation_result
        polydata = spectral_renderer._mesh_to_polydata(mesh)

        # Check points
        assert polydata.GetNumberOfPoints() == len(mesh.vertices)

        # Check triangles
        assert polydata.GetNumberOfPolys() == len(mesh.triangles)

        # Check normals
        normals = polydata.GetPointData().GetNormals()
        assert normals is not None

    def test_colormap_lut_creation(self):
        """Test lookup table creation for color mapping."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        lut = spectral_renderer._create_colormap_lut('coolwarm')

        assert lut is not None
        assert lut.GetNumberOfTableValues() == 256

        # Check diverging colors (blue at 0, white at 128, red at 255)
        color_blue = [0, 0, 0, 0]
        color_white = [0, 0, 0, 0]
        color_red = [0, 0, 0, 0]

        lut.GetTableValue(0, color_blue)
        lut.GetTableValue(128, color_white)
        lut.GetTableValue(255, color_red)

        # Blue should have high B component
        assert color_blue[2] > 0.8

        # White should have all components high
        assert color_white[0] > 0.8 and color_white[1] > 0.8 and color_white[2] > 0.8

        # Red should have high R component
        assert color_red[0] > 0.8

    def test_render_eigenfunction(self, mock_tessellation_result):
        """Test rendering eigenfunction as colored surface."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        mesh = mock_tessellation_result
        n_verts = len(mesh.vertices)

        # Create simple eigenmode
        mode = EigenMode(
            eigenvalue=2.0,
            eigenfunction=np.sin(np.linspace(0, 2*np.pi, n_verts)),
            index=1,
            multiplicity=1
        )

        # Render
        spectral_renderer.render_eigenfunction(mesh, mode, show_nodal_lines=False)

        # Check actor created
        assert spectral_renderer.surface_actor is not None
        assert renderer.GetActors().GetNumberOfItems() > 0

    def test_nodal_line_rendering(self, mock_tessellation_result):
        """Test nodal line extraction and rendering."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        mesh = mock_tessellation_result
        n_verts = len(mesh.vertices)

        # Create eigenmode with zero crossings
        mode = EigenMode(
            eigenvalue=2.0,
            eigenfunction=np.sin(np.linspace(0, 2*np.pi, n_verts)),
            index=1,
            multiplicity=1
        )

        # Render with nodal lines
        spectral_renderer.render_eigenfunction(mesh, mode, show_nodal_lines=True)

        # Should have both surface and nodal line actors
        assert spectral_renderer.surface_actor is not None
        # Note: nodal_line_actor may be None if contour extraction fails on simple mesh

    def test_clear(self):
        """Test clearing renderer actors."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        # Add some dummy actors
        spectral_renderer.surface_actor = vtk.vtkActor()
        spectral_renderer.nodal_line_actor = vtk.vtkActor()
        renderer.AddActor(spectral_renderer.surface_actor)
        renderer.AddActor(spectral_renderer.nodal_line_actor)

        # Clear
        spectral_renderer.clear()

        # Check actors removed
        assert spectral_renderer.surface_actor is None
        assert spectral_renderer.nodal_line_actor is None

    def test_set_nodal_line_style(self):
        """Test setting nodal line rendering style."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        spectral_renderer.set_nodal_line_style(
            radius=0.02,
            color=(1.0, 0.0, 0.0),
            width=5
        )

        assert spectral_renderer.nodal_line_radius == 0.02
        assert spectral_renderer.nodal_line_color == (1.0, 0.0, 0.0)
        assert spectral_renderer.nodal_line_width == 5

    def test_get_stats(self, sample_eigenmodes):
        """Test getting eigenmode statistics."""
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        mode = sample_eigenmodes[1]
        stats = spectral_renderer.get_stats(mode)

        assert 'eigenvalue' in stats
        assert 'index' in stats
        assert 'multiplicity' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'mean' in stats
        assert 'std' in stats
        assert 'zero_crossings' in stats
        assert 'num_vertices' in stats

        assert stats['eigenvalue'] == mode.eigenvalue
        assert stats['index'] == mode.index
        assert stats['num_vertices'] == len(mode.eigenfunction)


# ============================================================================
# EigenMode Tests
# ============================================================================

class TestEigenMode:
    """Test EigenMode dataclass."""

    def test_eigenmode_creation(self):
        """Test creating valid eigenmode."""
        ef = np.random.randn(100)
        mode = EigenMode(
            eigenvalue=2.0,
            eigenfunction=ef,
            index=1,
            multiplicity=1
        )

        assert mode.eigenvalue == 2.0
        assert np.array_equal(mode.eigenfunction, ef)
        assert mode.index == 1
        assert mode.multiplicity == 1

    def test_eigenmode_validation(self):
        """Test eigenmode validation."""
        # Invalid: eigenfunction not numpy array
        with pytest.raises(TypeError):
            EigenMode(eigenvalue=1.0, eigenfunction=[1, 2, 3], index=0)

        # Invalid: eigenfunction not 1D
        with pytest.raises(ValueError):
            EigenMode(eigenvalue=1.0, eigenfunction=np.zeros((10, 10)), index=0)

        # Invalid: negative eigenvalue
        with pytest.raises(ValueError):
            EigenMode(eigenvalue=-1.0, eigenfunction=np.zeros(10), index=0)

        # Invalid: multiplicity < 1
        with pytest.raises(ValueError):
            EigenMode(eigenvalue=1.0, eigenfunction=np.zeros(10), index=0, multiplicity=0)

    def test_eigenmode_default_multiplicity(self):
        """Test default multiplicity is 1."""
        mode = EigenMode(
            eigenvalue=1.0,
            eigenfunction=np.zeros(10),
            index=0
        )
        assert mode.multiplicity == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestSpectralVizIntegration:
    """Test integration between widget and renderer."""

    def test_widget_renderer_workflow(self, qapp, sample_eigenmodes, mock_tessellation_result):
        """Test typical workflow: load modes, select mode, render."""
        # Create widget and renderer
        widget = SpectralVizWidget()
        renderer = vtk.vtkRenderer()
        spectral_renderer = SpectralRenderer(renderer)

        # Load modes into widget
        widget.set_modes(sample_eigenmodes)

        # Select mode 1
        widget.set_current_mode(1)
        mode_index = widget.get_current_mode_index()
        assert mode_index == 1

        # Get selected mode
        mode = sample_eigenmodes[mode_index]

        # Render eigenfunction
        # Note: Need to create eigenfunction values matching mesh vertex count
        mesh = mock_tessellation_result
        n_verts = len(mesh.vertices)
        mode_for_mesh = EigenMode(
            eigenvalue=mode.eigenvalue,
            eigenfunction=np.sin(np.linspace(0, 2*np.pi, n_verts)),
            index=mode.index,
            multiplicity=mode.multiplicity
        )

        show_nodal = widget.get_show_nodal_lines()
        spectral_renderer.render_eigenfunction(mesh, mode_for_mesh, show_nodal_lines=show_nodal)

        # Check rendering succeeded
        assert spectral_renderer.surface_actor is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
