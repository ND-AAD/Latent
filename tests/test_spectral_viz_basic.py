"""
Basic tests for Spectral Visualization - No Qt/VTK required

These tests verify the core functionality without GUI/rendering components.

Author: Ceramic Mold Analyzer - Agent 36
Date: November 2025
"""

import pytest
import numpy as np
from app.analysis.spectral_decomposition import EigenMode


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

    def test_eigenmode_with_defaults(self):
        """Test eigenmode with default multiplicity."""
        mode = EigenMode(
            eigenvalue=1.0,
            eigenfunction=np.zeros(10),
            index=0
        )
        assert mode.multiplicity == 1

    def test_eigenmode_sine_wave(self):
        """Test eigenmode with sine wave eigenfunction."""
        n = 100
        eigenfunction = np.sin(np.linspace(0, 2*np.pi, n))
        mode = EigenMode(
            eigenvalue=2.0,
            eigenfunction=eigenfunction,
            index=1,
            multiplicity=1
        )

        # Should have zero crossings
        zero_crossings = np.sum(np.diff(np.sign(eigenfunction)) != 0)
        assert zero_crossings >= 2  # At least 2 zero crossings

        # Should have positive and negative values
        assert np.any(eigenfunction > 0)
        assert np.any(eigenfunction < 0)

    def test_eigenmode_properties(self):
        """Test eigenmode statistical properties."""
        n = 100
        eigenfunction = np.sin(np.linspace(0, 2*np.pi, n))
        mode = EigenMode(
            eigenvalue=2.0,
            eigenfunction=eigenfunction,
            index=1,
            multiplicity=1
        )

        # Check basic stats
        assert np.abs(np.mean(eigenfunction)) < 0.1  # Mean near zero for sine
        assert np.std(eigenfunction) > 0  # Non-zero std dev

    def test_multiple_modes(self):
        """Test creating multiple modes with different characteristics."""
        n = 100
        modes = [
            EigenMode(0.0, np.ones(n), 0, 1),  # Constant
            EigenMode(2.0, np.sin(np.linspace(0, 2*np.pi, n)), 1, 1),  # First mode
            EigenMode(6.0, np.sin(np.linspace(0, 4*np.pi, n)), 2, 2),  # Higher frequency, degenerate
        ]

        # Check ordering
        for i in range(len(modes) - 1):
            assert modes[i].eigenvalue <= modes[i+1].eigenvalue

        # Check mode 2 is degenerate
        assert modes[2].multiplicity == 2


class TestSpectralVisualizationModules:
    """Test that visualization modules can be imported."""

    def test_import_spectral_renderer(self):
        """Test that spectral_renderer module can be imported."""
        try:
            from app.geometry import spectral_renderer
            assert spectral_renderer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import spectral_renderer: {e}")

    def test_spectral_renderer_class_exists(self):
        """Test that SpectralRenderer class exists."""
        from app.geometry.spectral_renderer import SpectralRenderer
        assert SpectralRenderer is not None

    def test_spectral_renderer_docstring(self):
        """Test that SpectralRenderer has proper documentation."""
        from app.geometry.spectral_renderer import SpectralRenderer
        assert SpectralRenderer.__doc__ is not None
        assert "eigenfunction" in SpectralRenderer.__doc__.lower()


class TestEigenModeValidation:
    """Test EigenMode validation (if implemented)."""

    def test_eigenmode_accepts_numpy_array(self):
        """Test that eigenmode accepts numpy arrays."""
        ef = np.array([1.0, 2.0, 3.0])
        mode = EigenMode(1.0, ef, 0)
        assert isinstance(mode.eigenfunction, np.ndarray)

    def test_eigenmode_different_sizes(self):
        """Test eigenmodes with different vertex counts."""
        sizes = [10, 100, 1000]
        for size in sizes:
            ef = np.random.randn(size)
            mode = EigenMode(1.0, ef, 0)
            assert len(mode.eigenfunction) == size


class TestEigenModeOperations:
    """Test operations on eigenmodes."""

    def test_eigenmode_comparison(self):
        """Test comparing eigenmodes by eigenvalue."""
        mode1 = EigenMode(1.0, np.zeros(10), 0)
        mode2 = EigenMode(2.0, np.zeros(10), 1)

        assert mode1.eigenvalue < mode2.eigenvalue

    def test_eigenmode_sorting(self):
        """Test sorting eigenmodes."""
        modes = [
            EigenMode(6.0, np.zeros(10), 2),
            EigenMode(0.0, np.zeros(10), 0),
            EigenMode(2.0, np.zeros(10), 1),
        ]

        sorted_modes = sorted(modes, key=lambda m: m.eigenvalue)

        assert sorted_modes[0].eigenvalue == 0.0
        assert sorted_modes[1].eigenvalue == 2.0
        assert sorted_modes[2].eigenvalue == 6.0

    def test_eigenmode_list_comprehension(self):
        """Test creating eigenmodes with list comprehension."""
        n = 100
        modes = [
            EigenMode(
                eigenvalue=i * 2.0,
                eigenfunction=np.sin(np.linspace(0, i*np.pi, n)),
                index=i
            )
            for i in range(5)
        ]

        assert len(modes) == 5
        assert all(isinstance(m, EigenMode) for m in modes)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
