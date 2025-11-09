#!/usr/bin/env python3
"""
Differential Lens Demo

Demonstrates the first mathematical lens - differential geometry region discovery.

This example shows how to:
1. Create a SubD control cage
2. Initialize the differential lens
3. Discover regions based on curvature
4. Examine region properties
5. Visualize curvature fields

Author: Agent 32
Date: November 2025
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cpp_core
    from app.analysis.differential_lens import DifferentialLens, DifferentialLensParams
    from app.state.parametric_region import ParametricRegion
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print("Make sure cpp_core is built and installed.")
    sys.exit(1)


def create_sphere_cage():
    """Create a simple sphere-like SubD control cage (octahedron)."""
    cage = cpp_core.SubDControlCage()

    # 6 vertices (octahedron)
    r = 1.0
    vertices = [
        (r, 0, 0), (-r, 0, 0),    # X axis
        (0, r, 0), (0, -r, 0),    # Y axis
        (0, 0, r), (0, 0, -r)     # Z axis
    ]

    for x, y, z in vertices:
        cage.vertices.append(cpp_core.Point3D(x, y, z))

    # 8 triangular faces (octahedron)
    cage.faces = [
        [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],  # Right hemisphere
        [1, 4, 2], [1, 3, 4], [1, 5, 3], [1, 2, 5]   # Left hemisphere
    ]

    return cage


def create_cylinder_cage():
    """Create a cylinder-like SubD control cage."""
    import numpy as np

    cage = cpp_core.SubDControlCage()

    # 8 vertices (4 bottom, 4 top)
    r = 1.0
    h = 2.0
    angles = [0, np.pi/2, np.pi, 3*np.pi/2]

    for z in [-h/2, h/2]:
        for angle in angles:
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            cage.vertices.append(cpp_core.Point3D(x, y, z))

    # 4 side faces + 2 caps
    cage.faces = [
        [0, 1, 5, 4],  # Side 1
        [1, 2, 6, 5],  # Side 2
        [2, 3, 7, 6],  # Side 3
        [3, 0, 4, 7],  # Side 4
        [0, 1, 2, 3],  # Bottom cap
        [4, 5, 6, 7]   # Top cap
    ]

    return cage


def analyze_geometry(name, cage):
    """Analyze a geometry with the differential lens."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {name}")
    print('='*60)

    # Initialize evaluator
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)

    print(f"Control cage: {cage.vertex_count()} vertices, {cage.face_count()} faces")

    # Create differential lens with default parameters
    lens = DifferentialLens(evaluator)

    # Discover regions
    print("\nDiscovering regions...")
    regions = lens.discover_regions()

    print(f"\n✓ Discovered {len(regions)} regions\n")

    # Display region information
    for idx, region in enumerate(regions, 1):
        print(f"Region {idx}: {region.id}")
        print(f"  Unity Principle: {region.unity_principle}")
        print(f"  Unity Strength: {region.unity_strength:.3f}")
        print(f"  Face Count: {len(region.faces)}")
        print(f"  Curvature Type: {region.metadata['curvature_type']}")
        print(f"  Is Ridge: {region.metadata['is_ridge']}")
        print(f"  Is Valley: {region.metadata['is_valley']}")
        print()

    # Display curvature field statistics
    curvature_field = lens.get_curvature_field()
    if curvature_field:
        print("Curvature Field Statistics:")

        K_values = [stats['mean_K'] for stats in curvature_field.values()]
        H_values = [stats['mean_H'] for stats in curvature_field.values()]

        import numpy as np
        print(f"  Gaussian Curvature (K):")
        print(f"    Range: [{np.min(K_values):.4f}, {np.max(K_values):.4f}]")
        print(f"    Mean: {np.mean(K_values):.4f}")
        print(f"    Std: {np.std(K_values):.4f}")

        print(f"  Mean Curvature (H):")
        print(f"    Range: [{np.min(H_values):.4f}, {np.max(H_values):.4f}]")
        print(f"    Mean: {np.mean(H_values):.4f}")
        print(f"    Std: {np.std(H_values):.4f}")


def demo_custom_parameters():
    """Demonstrate using custom parameters."""
    print(f"\n{'='*60}")
    print("Custom Parameters Demo")
    print('='*60)

    cage = create_sphere_cage()
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)

    # Create lens with custom parameters
    params = DifferentialLensParams(
        samples_per_face=16,              # Higher resolution
        mean_curvature_threshold=0.05,    # Stricter thresholds
        curvature_tolerance=0.2,          # Tighter coherence
        min_region_size=2,                # Merge tiny regions
        ridge_percentile=85.0,            # Top 15% ridges
        valley_percentile=15.0            # Bottom 15% valleys
    )

    print("Parameters:")
    print(f"  Samples per face: {params.samples_per_face}")
    print(f"  Curvature tolerance: {params.curvature_tolerance}")
    print(f"  Min region size: {params.min_region_size}")
    print(f"  Ridge percentile: {params.ridge_percentile}")

    lens = DifferentialLens(evaluator, params)
    regions = lens.discover_regions()

    print(f"\n✓ Discovered {len(regions)} regions with custom parameters")


def demo_pinned_faces():
    """Demonstrate pinning faces to exclude from analysis."""
    print(f"\n{'='*60}")
    print("Pinned Faces Demo")
    print('='*60)

    cage = create_cylinder_cage()
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)

    # Analyze with pinned faces
    pinned = {0, 1}  # Pin first two faces
    print(f"Pinning faces: {pinned}")

    lens = DifferentialLens(evaluator)
    regions = lens.discover_regions(pinned_faces=pinned)

    print(f"\n✓ Discovered {len(regions)} regions (excluding pinned faces)")

    # Verify pinned faces not in regions
    all_region_faces = set()
    for region in regions:
        all_region_faces.update(region.faces)

    if pinned.isdisjoint(all_region_faces):
        print("✓ Pinned faces successfully excluded from all regions")
    else:
        print("✗ Warning: Some pinned faces found in regions")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("DIFFERENTIAL LENS DEMONSTRATION")
    print("First Mathematical Lens for Ceramic Mold Analyzer")
    print("="*60)

    try:
        # Test 1: Sphere (uniform positive curvature)
        sphere_cage = create_sphere_cage()
        analyze_geometry("Sphere (Octahedron)", sphere_cage)

        # Test 2: Cylinder (parabolic sides + elliptic caps)
        cylinder_cage = create_cylinder_cage()
        analyze_geometry("Cylinder", cylinder_cage)

        # Test 3: Custom parameters
        demo_custom_parameters()

        # Test 4: Pinned faces
        demo_pinned_faces()

        print("\n" + "="*60)
        print("✓ All demos completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
