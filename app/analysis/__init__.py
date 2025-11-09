"""
Mathematical analysis modules for SubD surfaces.

Includes:
- Differential geometry (curvature analysis)
- Spectral analysis (Laplace-Beltrami eigenfunctions)
- Region decomposition algorithms
"""

# Import differential lens (Day 4 - complete)
from .differential_lens import DifferentialLens
from .differential_decomposition import DifferentialDecomposition

# Try to import spectral components (Day 5 - may be incomplete)
try:
    from .laplacian import LaplacianBuilder, build_normalized_laplacian, verify_laplacian
    _LAPLACIAN_AVAILABLE = True
except (ImportError, AttributeError):
    _LAPLACIAN_AVAILABLE = False

try:
    from .spectral_decomposition import SpectralDecomposer, EigenMode
    from .spectral_lens import SpectralLens
    _SPECTRAL_AVAILABLE = True
except (ImportError, AttributeError):
    _SPECTRAL_AVAILABLE = False

# Try to import lens manager
try:
    from .lens_manager import LensManager, LensType, LensResult
    _LENS_MANAGER_AVAILABLE = True
except (ImportError, AttributeError):
    _LENS_MANAGER_AVAILABLE = False

# Build __all__ dynamically based on what's available
__all__ = [
    'DifferentialLens',
    'DifferentialDecomposition',
]

if _LAPLACIAN_AVAILABLE:
    __all__.extend(['LaplacianBuilder', 'build_normalized_laplacian', 'verify_laplacian'])

if _SPECTRAL_AVAILABLE:
    __all__.extend(['SpectralDecomposer', 'EigenMode', 'SpectralLens'])

if _LENS_MANAGER_AVAILABLE:
    __all__.extend(['LensManager', 'LensType', 'LensResult'])
