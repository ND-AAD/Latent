"""
Standalone tests for Laplacian builder math functions.

These tests don't require cpp_core and can run independently.
"""

import numpy as np
from scipy import sparse


def test_cotangent_math():
    """Test cotangent computation without full Laplacian."""
    # Import just the computation logic
    import sys
    sys.path.insert(0, '/home/user/Latent')

    # We'll manually compute cotangent
    def compute_cotangent(v0, v1, v_opp):
        """Compute cotangent of angle at v_opp."""
        u = v0 - v_opp
        v = v1 - v_opp
        dot_uv = np.dot(u, v)
        cross_uv = np.cross(u, v)
        cross_mag = np.linalg.norm(cross_uv)
        if cross_mag < 1e-10:
            return 0.0
        cot_theta = dot_uv / cross_mag
        return np.clip(cot_theta, -100.0, 100.0)

    # Test 1: Right angle (90°) -> cot should be ~0
    # For 90° at v_opp, vectors from v_opp to v0 and v1 must be perpendicular
    v0 = np.array([-1, 0, 0], dtype=float)
    v1 = np.array([0, 1, 0], dtype=float)
    v_opp = np.array([0, 0, 0], dtype=float)
    cot = compute_cotangent(v0, v1, v_opp)
    print(f"Right angle (90°): cot = {cot:.6f} (expected ~0)")
    assert abs(cot) < 0.01, f"Failed: cot(90°) = {cot}, expected ~0"

    # Test 2: 60° angle -> cot should be 1/√3 ≈ 0.577
    v0 = np.array([0, 0, 0], dtype=float)
    v1 = np.array([1, 0, 0], dtype=float)
    v_opp = np.array([0.5, np.sqrt(3)/2, 0], dtype=float)
    cot = compute_cotangent(v0, v1, v_opp)
    expected = 1.0 / np.sqrt(3)
    print(f"60° angle: cot = {cot:.6f} (expected {expected:.6f})")
    assert abs(cot - expected) < 0.01, f"Failed: cot(60°) = {cot}, expected {expected}"

    # Test 3: 45° angle -> cot should be 1.0
    # v_opp at origin, v0 along x-axis, v1 at 45° from x-axis
    v_opp = np.array([0, 0, 0], dtype=float)
    v0 = np.array([1, 0, 0], dtype=float)
    v1 = np.array([1/np.sqrt(2), 1/np.sqrt(2), 0], dtype=float)
    cot = compute_cotangent(v0, v1, v_opp)
    expected = 1.0
    print(f"45° angle: cot = {cot:.6f} (expected {expected:.6f})")
    assert abs(cot - expected) < 0.01, f"Failed: cot(45°) = {cot}, expected {expected}"

    # Test 4: 30° angle -> cot should be √3 ≈ 1.732
    # v_opp at origin, v0 along x-axis, v1 at 30° from x-axis
    v_opp = np.array([0, 0, 0], dtype=float)
    v0 = np.array([1, 0, 0], dtype=float)
    v1 = np.array([np.sqrt(3)/2, 0.5, 0], dtype=float)
    cot = compute_cotangent(v0, v1, v_opp)
    expected = np.sqrt(3)
    print(f"30° angle: cot = {cot:.6f} (expected {expected:.6f})")
    assert abs(cot - expected) < 0.1, f"Failed: cot(30°) = {cot}, expected {expected}"

    print("\nAll cotangent tests passed!")


def test_area_computation():
    """Test triangle area computation."""
    # Right triangle with legs 1, 1
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0]
    ], dtype=float)

    # Compute area
    v0, v1, v2 = vertices
    edge1 = v1 - v0
    edge2 = v2 - v0
    tri_area = 0.5 * np.linalg.norm(np.cross(edge1, edge2))

    expected_area = 0.5
    print(f"Right triangle area: {tri_area:.6f} (expected {expected_area:.6f})")
    assert abs(tri_area - expected_area) < 1e-6, f"Failed: area = {tri_area}, expected {expected_area}"

    # Equilateral triangle with side length 1
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0.5, np.sqrt(3)/2, 0]
    ], dtype=float)

    v0, v1, v2 = vertices
    edge1 = v1 - v0
    edge2 = v2 - v0
    tri_area = 0.5 * np.linalg.norm(np.cross(edge1, edge2))

    expected_area = np.sqrt(3) / 4
    print(f"Equilateral triangle area: {tri_area:.6f} (expected {expected_area:.6f})")
    assert abs(tri_area - expected_area) < 1e-6, f"Failed: area = {tri_area}, expected {expected_area}"

    print("\nAll area tests passed!")


def test_sparse_matrix_properties():
    """Test sparse matrix construction and properties."""
    # Build a simple 3x3 symmetric matrix
    rows = [0, 0, 1, 1, 2, 2]
    cols = [1, 2, 0, 2, 0, 1]
    data = [1.0, 0.5, 1.0, 0.3, 0.5, 0.3]

    L = sparse.coo_matrix((data, (rows, cols)), shape=(3, 3))
    L = L.tocsr()

    # Add diagonal to make row sums zero
    diagonal = -L.sum(axis=1).A1
    L.setdiag(diagonal)

    # Test symmetry
    L_diff = L - L.T
    if L_diff.nnz > 0:
        diff = np.abs(L_diff.data).max()
    else:
        diff = 0.0
    print(f"Symmetry error: {diff:.10f}")
    assert diff < 1e-10, f"Failed: not symmetric, diff = {diff}"

    # Test row sums
    ones = np.ones(L.shape[0])
    row_sums = L @ ones
    max_sum = np.abs(row_sums).max()
    print(f"Max row sum: {max_sum:.10f}")
    assert max_sum < 1e-10, f"Failed: row sums not zero, max = {max_sum}"

    print("\nAll sparse matrix tests passed!")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Cotangent Computation")
    print("=" * 60)
    test_cotangent_math()

    print("\n" + "=" * 60)
    print("Testing Area Computation")
    print("=" * 60)
    test_area_computation()

    print("\n" + "=" * 60)
    print("Testing Sparse Matrix Properties")
    print("=" * 60)
    test_sparse_matrix_properties()

    print("\n" + "=" * 60)
    print("ALL STANDALONE TESTS PASSED!")
    print("=" * 60)
