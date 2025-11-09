#!/usr/bin/env python3
"""
Demonstration script for region merge/split operations
Run with: python app/operations/demo_operations.py
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.state.parametric_region import ParametricRegion, ParametricCurve
from app.operations.region_operations import RegionOperations


def demo_merge():
    """Demonstrate region merging"""
    print("=" * 60)
    print("MERGE DEMONSTRATION")
    print("=" * 60)

    # Create three regions
    r1 = ParametricRegion(
        id="region_1",
        faces=[0, 1, 2, 3],
        boundary=[],
        unity_principle="differential_curvature",
        unity_strength=0.85
    )

    r2 = ParametricRegion(
        id="region_2",
        faces=[4, 5, 6],
        boundary=[],
        unity_principle="differential_curvature",
        unity_strength=0.78
    )

    r3 = ParametricRegion(
        id="region_3",
        faces=[7, 8],
        boundary=[],
        unity_principle="differential_curvature",
        unity_strength=0.92,
        pinned=True
    )

    print(f"Region 1: {len(r1.faces)} faces, strength={r1.unity_strength:.2f}")
    print(f"Region 2: {len(r2.faces)} faces, strength={r2.unity_strength:.2f}")
    print(f"Region 3: {len(r3.faces)} faces, strength={r3.unity_strength:.2f}, pinned={r3.pinned}")

    # Check if can merge
    print(f"\nCan merge r1 and r2? {RegionOperations.can_merge(r1, r2)}")
    print(f"Can merge r2 and r3? {RegionOperations.can_merge(r2, r3)}")

    # Merge all three
    print("\nMerging all three regions...")
    merged = RegionOperations.merge_regions([r1, r2, r3])

    print(f"\nMerged region:")
    print(f"  ID: {merged.id}")
    print(f"  Faces: {len(merged.faces)} ({sorted(merged.faces)})")
    print(f"  Unity strength: {merged.unity_strength:.2f}")
    print(f"  Pinned: {merged.pinned}")
    print(f"  Modified: {merged.modified}")


def demo_split():
    """Demonstrate region splitting"""
    print("\n" + "=" * 60)
    print("SPLIT DEMONSTRATION")
    print("=" * 60)

    # Create a region to split
    region = ParametricRegion(
        id="region_large",
        faces=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        boundary=[],
        unity_principle="spectral_harmonic",
        unity_strength=0.88
    )

    print(f"Original region: {len(region.faces)} faces, strength={region.unity_strength:.2f}")

    # Create split curve through the middle
    split_curve = ParametricCurve(
        points=[
            (3, 0.5, 0.5),  # Pass through face 3
            (4, 0.5, 0.5),  # Pass through face 4
            (5, 0.5, 0.5),  # Pass through face 5
        ],
        is_closed=False
    )

    print(f"\nSplit curve: {len(split_curve.points)} points")

    # Split the region
    print("\nSplitting region...")
    r1, r2 = RegionOperations.split_region(region, split_curve)

    print(f"\nRegion A:")
    print(f"  ID: {r1.id}")
    print(f"  Faces: {len(r1.faces)} ({sorted(r1.faces)})")
    print(f"  Unity strength: {r1.unity_strength:.2f}")
    print(f"  Modified: {r1.modified}")

    print(f"\nRegion B:")
    print(f"  ID: {r2.id}")
    print(f"  Faces: {len(r2.faces)} ({sorted(r2.faces)})")
    print(f"  Unity strength: {r2.unity_strength:.2f}")
    print(f"  Modified: {r2.modified}")

    # Validate both regions
    is_valid_1, issues_1 = RegionOperations.validate_region(r1)
    is_valid_2, issues_2 = RegionOperations.validate_region(r2)

    print(f"\nValidation:")
    print(f"  Region A valid: {is_valid_1}")
    print(f"  Region B valid: {is_valid_2}")


def demo_validation():
    """Demonstrate region validation"""
    print("\n" + "=" * 60)
    print("VALIDATION DEMONSTRATION")
    print("=" * 60)

    # Good region
    good_region = ParametricRegion(
        id="good_region",
        faces=[0, 1, 2],
        boundary=[],
        unity_principle="curvature",
        unity_strength=0.75
    )

    is_valid, issues = RegionOperations.validate_region(good_region)
    print(f"\nGood region: valid={is_valid}")

    # Bad region - empty faces
    bad_region_1 = ParametricRegion(
        id="bad_region_1",
        faces=[],
        boundary=[],
        unity_principle="curvature",
        unity_strength=0.75
    )

    is_valid, issues = RegionOperations.validate_region(bad_region_1)
    print(f"\nEmpty region: valid={is_valid}")
    if issues:
        print(f"  Issues: {issues}")

    # Bad region - invalid strength
    bad_region_2 = ParametricRegion(
        id="bad_region_2",
        faces=[0, 1],
        boundary=[],
        unity_principle="curvature",
        unity_strength=1.5  # Invalid
    )

    is_valid, issues = RegionOperations.validate_region(bad_region_2)
    print(f"\nInvalid strength: valid={is_valid}")
    if issues:
        print(f"  Issues: {issues}")

    # Bad region - duplicate faces
    bad_region_3 = ParametricRegion(
        id="bad_region_3",
        faces=[0, 1, 2, 1],  # Duplicate
        boundary=[],
        unity_principle="curvature",
        unity_strength=0.75
    )

    is_valid, issues = RegionOperations.validate_region(bad_region_3)
    print(f"\nDuplicate faces: valid={is_valid}")
    if issues:
        print(f"  Issues: {issues}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  REGION OPERATIONS DEMONSTRATION                         ║")
    print("║  Agent 37: Merge/Split Operations                        ║")
    print("╚" + "=" * 58 + "╝")
    print()

    demo_merge()
    demo_split()
    demo_validation()

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nAll operations maintain parametric representation!")
    print("Ready for integration with ApplicationState and UI.\n")
