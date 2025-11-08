"""
Curvature computation for mesh surfaces.

This module provides mesh-based curvature estimation using discrete differential
geometry operators. Computes principal curvatures, mean curvature, and Gaussian
curvature via finite differences.

Mathematical Background:
- Principal curvatures κ₁, κ₂: max/min normal curvatures at a point
- Mean curvature H = (κ₁ + κ₂) / 2
- Gaussian curvature K = κ₁ × κ₂

Surface Classification:
- Elliptic (K > 0): Bowl-like (sphere, ellipsoid)
- Hyperbolic (K < 0): Saddle-like (hyperboloid, saddle)
- Parabolic (K ≈ 0): Cylindrical (cylinder, cone)
- Planar (K ≈ 0, H ≈ 0): Flat (plane)

Author: Ceramic Mold Analyzer
Date: November 2025
"""

import numpy as np
from typing import Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class CurvatureData:
    """Curvature information at a point on the mesh."""
    principal_min: float  # κ₁ (min principal curvature)
    principal_max: float  # κ₂ (max principal curvature)
    mean: float           # H = (κ₁ + κ₂) / 2
    gaussian: float       # K = κ₁ × κ₂

    @property
    def curvature_type(self) -> str:
        """Classify surface type based on curvatures."""
        K_threshold = 1e-6
        H_threshold = 1e-6

        if abs(self.gaussian) < K_threshold and abs(self.mean) < H_threshold:
            return "planar"
        elif abs(self.gaussian) < K_threshold:
            return "parabolic"
        elif self.gaussian > K_threshold:
            return "elliptic"
        else:  # K < 0
            return "hyperbolic"


class MeshCurvatureEstimator:
    """
    Estimates curvatures on triangular or quad meshes using discrete operators.

    Uses Meyer et al. (2003) "Discrete Differential-Geometry Operators for
    Triangulated 2-Manifolds" method.
    """

    def __init__(self, vertices: np.ndarray, faces: np.ndarray):
        """
        Initialize curvature estimator.

        Args:
            vertices: (N, 3) array of vertex positions
            faces: (M, 3 or 4) array of face vertex indices
        """
        self.vertices = vertices
        self.faces = faces
        self.num_vertices = len(vertices)
        self.num_faces = len(faces)

        # Cached computations
        self._face_normals: Optional[np.ndarray] = None
        self._vertex_normals: Optional[np.ndarray] = None
        self._vertex_areas: Optional[np.ndarray] = None

    def compute_face_normals(self) -> np.ndarray:
        """
        Compute face normals for all faces.

        Returns:
            (M, 3) array of normalized face normals
        """
        if self._face_normals is not None:
            return self._face_normals

        normals = np.zeros((self.num_faces, 3))

        for i, face in enumerate(self.faces):
            if len(face) == 3:
                # Triangle
                v0, v1, v2 = self.vertices[face[:3]]
                normal = np.cross(v1 - v0, v2 - v0)
            else:
                # Quad - use first 3 vertices for normal
                v0, v1, v2 = self.vertices[face[:3]]
                normal = np.cross(v1 - v0, v2 - v0)

            # Normalize
            norm = np.linalg.norm(normal)
            if norm > 1e-10:
                normals[i] = normal / norm
            else:
                normals[i] = np.array([0, 0, 1])  # Degenerate face

        self._face_normals = normals
        return normals

    def compute_vertex_normals(self) -> np.ndarray:
        """
        Compute vertex normals as area-weighted average of adjacent face normals.

        Returns:
            (N, 3) array of normalized vertex normals
        """
        if self._vertex_normals is not None:
            return self._vertex_normals

        face_normals = self.compute_face_normals()
        vertex_normals = np.zeros((self.num_vertices, 3))

        # Accumulate face normals (weighted by face area)
        for i, face in enumerate(self.faces):
            # Compute face area
            if len(face) == 3:
                v0, v1, v2 = self.vertices[face[:3]]
                area = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
            else:
                # Quad - split into two triangles
                v0, v1, v2, v3 = self.vertices[face[:4]]
                area1 = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
                area2 = 0.5 * np.linalg.norm(np.cross(v2 - v0, v3 - v0))
                area = area1 + area2

            # Add weighted normal to each vertex
            for v_idx in face:
                vertex_normals[v_idx] += face_normals[i] * area

        # Normalize
        for i in range(self.num_vertices):
            norm = np.linalg.norm(vertex_normals[i])
            if norm > 1e-10:
                vertex_normals[i] /= norm
            else:
                vertex_normals[i] = np.array([0, 0, 1])

        self._vertex_normals = vertex_normals
        return vertex_normals

    def compute_vertex_areas(self) -> np.ndarray:
        """
        Compute Voronoi area for each vertex (1/3 of adjacent face areas).

        Returns:
            (N,) array of vertex areas
        """
        if self._vertex_areas is not None:
            return self._vertex_areas

        vertex_areas = np.zeros(self.num_vertices)

        for face in self.faces:
            # Compute face area
            if len(face) == 3:
                v0, v1, v2 = self.vertices[face[:3]]
                area = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
                weight = area / 3.0  # Triangle
            else:
                # Quad
                v0, v1, v2, v3 = self.vertices[face[:4]]
                area1 = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
                area2 = 0.5 * np.linalg.norm(np.cross(v2 - v0, v3 - v0))
                area = area1 + area2
                weight = area / 4.0  # Quad

            # Distribute to vertices
            for v_idx in face:
                vertex_areas[v_idx] += weight

        self._vertex_areas = vertex_areas
        return vertex_areas

    def compute_principal_curvatures_at_vertex(self, vertex_idx: int) -> CurvatureData:
        """
        Compute principal curvatures at a vertex using Meyer et al. method.

        Estimates mean curvature H and Gaussian curvature K, then solves:
        κ₁ = H + sqrt(H² - K)
        κ₂ = H - sqrt(H² - K)

        Args:
            vertex_idx: Index of vertex

        Returns:
            CurvatureData with principal curvatures
        """
        vertex_normals = self.compute_vertex_normals()
        vertex_areas = self.compute_vertex_areas()

        v = self.vertices[vertex_idx]
        n = vertex_normals[vertex_idx]
        area = vertex_areas[vertex_idx]

        if area < 1e-10:
            # Degenerate case
            return CurvatureData(0.0, 0.0, 0.0, 0.0)

        # Find neighboring vertices (one-ring)
        neighbors = self._get_vertex_neighbors(vertex_idx)

        if len(neighbors) < 3:
            # Not enough neighbors for curvature estimation
            return CurvatureData(0.0, 0.0, 0.0, 0.0)

        # Estimate mean curvature using Laplace-Beltrami operator
        # H = (1 / 4A) * sum(cotangent_weights * edge_vectors)
        mean_curvature_vector = np.zeros(3)

        for n_idx in neighbors:
            edge = self.vertices[n_idx] - v
            # Simplified: use uniform weights (1.0) instead of cotangent
            # For production: implement cotangent weights
            mean_curvature_vector += edge

        mean_curvature_vector /= (4.0 * area)

        # Mean curvature magnitude
        H = np.linalg.norm(mean_curvature_vector)

        # Sign of mean curvature (based on normal direction)
        if np.dot(mean_curvature_vector, n) < 0:
            H = -H

        # Estimate Gaussian curvature using angle defect
        # K = (2π - sum(angles)) / area
        angle_sum = self._compute_angle_defect(vertex_idx, neighbors)
        K = (2.0 * np.pi - angle_sum) / area

        # Compute principal curvatures from H and K
        # κ₁ + κ₂ = 2H
        # κ₁ × κ₂ = K
        # Solving: κ₁,₂ = H ± sqrt(H² - K)

        discriminant = H * H - K

        if discriminant >= 0:
            sqrt_disc = np.sqrt(discriminant)
            k1 = H - sqrt_disc  # Min curvature
            k2 = H + sqrt_disc  # Max curvature
        else:
            # Numerical issue - fall back to H
            k1 = H
            k2 = H
            K = H * H  # Adjust K to be consistent

        return CurvatureData(
            principal_min=k1,
            principal_max=k2,
            mean=H,
            gaussian=K
        )

    def _get_vertex_neighbors(self, vertex_idx: int) -> list:
        """Get indices of neighboring vertices (one-ring)."""
        neighbors = set()

        for face in self.faces:
            face_list = list(face)
            if vertex_idx in face_list:
                idx = face_list.index(vertex_idx)
                n = len(face_list)
                # Add previous and next vertices in face
                neighbors.add(face_list[(idx - 1) % n])
                neighbors.add(face_list[(idx + 1) % n])

        return list(neighbors)

    def _compute_angle_defect(self, vertex_idx: int, neighbors: list) -> float:
        """Compute sum of angles at vertex for Gaussian curvature estimation."""
        v = self.vertices[vertex_idx]
        angle_sum = 0.0

        # Find faces containing this vertex
        for face in self.faces:
            face_list = list(face)
            if vertex_idx not in face_list:
                continue

            idx = face_list.index(vertex_idx)
            n = len(face_list)

            # Get adjacent vertices in this face
            v_prev = self.vertices[face_list[(idx - 1) % n]]
            v_next = self.vertices[face_list[(idx + 1) % n]]

            # Compute angle
            edge1 = v_prev - v
            edge2 = v_next - v

            norm1 = np.linalg.norm(edge1)
            norm2 = np.linalg.norm(edge2)

            if norm1 > 1e-10 and norm2 > 1e-10:
                cos_angle = np.dot(edge1, edge2) / (norm1 * norm2)
                # Clamp to [-1, 1] for numerical stability
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                angle = np.arccos(cos_angle)
                angle_sum += angle

        return angle_sum

    def compute_face_curvature(self, face_idx: int) -> CurvatureData:
        """
        Compute average curvature at face center.

        Uses average of vertex curvatures for simplicity.

        Args:
            face_idx: Index of face

        Returns:
            CurvatureData averaged over face vertices
        """
        face = self.faces[face_idx]

        # Compute curvature at each vertex
        curvatures = [self.compute_principal_curvatures_at_vertex(v_idx)
                      for v_idx in face]

        # Average
        k1_avg = np.mean([c.principal_min for c in curvatures])
        k2_avg = np.mean([c.principal_max for c in curvatures])
        H_avg = np.mean([c.mean for c in curvatures])
        K_avg = np.mean([c.gaussian for c in curvatures])

        return CurvatureData(
            principal_min=k1_avg,
            principal_max=k2_avg,
            mean=H_avg,
            gaussian=K_avg
        )

    def compute_all_face_curvatures(self) -> Dict[int, CurvatureData]:
        """
        Compute curvatures for all faces.

        Returns:
            Dictionary mapping face_idx → CurvatureData
        """
        curvatures = {}

        for face_idx in range(self.num_faces):
            curvatures[face_idx] = self.compute_face_curvature(face_idx)

        return curvatures


def test_curvature_on_sphere(radius: float = 1.0, subdivision: int = 2) -> None:
    """
    Test curvature computation on a sphere.
    Expected: κ₁ = κ₂ = 1/r, H = 1/r, K = 1/r²
    """
    from app.geometry.test_meshes import create_sphere_mesh

    vertices, faces = create_sphere_mesh(radius, subdivision)

    estimator = MeshCurvatureEstimator(vertices, faces)

    # Compute curvature at a few faces
    print(f"\n=== Sphere Curvature Test (r={radius}) ===")
    print(f"Expected: κ₁=κ₂={1/radius:.3f}, H={1/radius:.3f}, K={1/radius**2:.3f}")

    for face_idx in range(min(5, len(faces))):
        curv = estimator.compute_face_curvature(face_idx)
        print(f"Face {face_idx}: κ₁={curv.principal_min:.3f}, κ₂={curv.principal_max:.3f}, "
              f"H={curv.mean:.3f}, K={curv.gaussian:.3f}, type={curv.curvature_type}")


if __name__ == "__main__":
    # Run test
    test_curvature_on_sphere()
