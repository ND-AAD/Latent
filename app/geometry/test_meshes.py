"""
Test mesh generation for curvature validation.

Provides simple analytical meshes with known curvatures for testing
the differential decomposition engine.
"""

import numpy as np
from typing import Tuple


def create_sphere_mesh(radius: float = 1.0, subdivisions: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a triangulated sphere using UV parameterization.

    Args:
        radius: Sphere radius
        subdivisions: Number of subdivision levels (higher = more faces)

    Returns:
        vertices: (N, 3) array of vertex positions
        faces: (M, 3) array of triangle indices
    """
    n_u = 2 ** (subdivisions + 2)  # Longitude divisions
    n_v = 2 ** (subdivisions + 1)  # Latitude divisions

    vertices = []
    faces = []

    # Generate vertices
    for i in range(n_v + 1):
        theta = np.pi * i / n_v  # Latitude angle [0, π]
        for j in range(n_u):
            phi = 2 * np.pi * j / n_u  # Longitude angle [0, 2π]

            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(theta)

            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Generate faces (triangles)
    for i in range(n_v):
        for j in range(n_u):
            # Current quad vertices
            v0 = i * n_u + j
            v1 = i * n_u + (j + 1) % n_u
            v2 = (i + 1) * n_u + (j + 1) % n_u
            v3 = (i + 1) * n_u + j

            # Skip degenerate triangles at poles
            if i > 0:  # Not north pole
                faces.append([v0, v1, v2])
            if i < n_v - 1:  # Not south pole
                faces.append([v0, v2, v3])

    faces = np.array(faces)

    return vertices, faces


def create_cylinder_mesh(radius: float = 1.0, height: float = 2.0,
                         subdivisions: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a triangulated cylinder.

    Expected curvatures:
    - Radial direction: κ = 1/r
    - Axial direction: κ = 0
    - Mean curvature: H = 1/(2r)
    - Gaussian curvature: K = 0 (parabolic surface)

    Args:
        radius: Cylinder radius
        height: Cylinder height
        subdivisions: Number of subdivision levels

    Returns:
        vertices: (N, 3) array of vertex positions
        faces: (M, 3) array of triangle indices
    """
    n_theta = 2 ** (subdivisions + 3)  # Circumference divisions
    n_z = 2 ** (subdivisions + 2)      # Height divisions

    vertices = []
    faces = []

    # Generate vertices
    for i in range(n_z + 1):
        z = -height / 2 + (height * i / n_z)
        for j in range(n_theta):
            theta = 2 * np.pi * j / n_theta

            x = radius * np.cos(theta)
            y = radius * np.sin(theta)

            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Generate faces
    for i in range(n_z):
        for j in range(n_theta):
            v0 = i * n_theta + j
            v1 = i * n_theta + (j + 1) % n_theta
            v2 = (i + 1) * n_theta + (j + 1) % n_theta
            v3 = (i + 1) * n_theta + j

            # Two triangles per quad
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    faces = np.array(faces)

    return vertices, faces


def create_saddle_mesh(scale: float = 1.0, subdivisions: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a hyperbolic paraboloid (saddle) mesh.

    Surface equation: z = (x² - y²) / scale

    Expected at origin:
    - κ₁ = -2/scale (negative curvature)
    - κ₂ = +2/scale (positive curvature)
    - Mean curvature: H = 0
    - Gaussian curvature: K < 0 (hyperbolic surface)

    Args:
        scale: Scaling factor
        subdivisions: Number of subdivision levels

    Returns:
        vertices: (N, 3) array of vertex positions
        faces: (M, 3) array of triangle indices
    """
    n = 2 ** (subdivisions + 3)  # Grid size

    vertices = []
    faces = []

    # Generate grid vertices
    for i in range(n + 1):
        for j in range(n + 1):
            x = -scale + (2 * scale * i / n)
            y = -scale + (2 * scale * j / n)
            z = (x * x - y * y) / scale

            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Generate faces
    for i in range(n):
        for j in range(n):
            v0 = i * (n + 1) + j
            v1 = i * (n + 1) + (j + 1)
            v2 = (i + 1) * (n + 1) + (j + 1)
            v3 = (i + 1) * (n + 1) + j

            # Two triangles per quad
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    faces = np.array(faces)

    return vertices, faces


def create_torus_mesh(major_radius: float = 2.0, minor_radius: float = 0.5,
                      subdivisions: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a triangulated torus.

    Expected curvatures vary by location:
    - Outer edge: κ₁ = 1/minor_radius, κ₂ = 1/(major_radius + minor_radius)
    - Inner edge: κ₁ = 1/minor_radius, κ₂ = 1/(major_radius - minor_radius)

    Args:
        major_radius: Distance from torus center to tube center
        minor_radius: Tube radius
        subdivisions: Number of subdivision levels

    Returns:
        vertices: (N, 3) array of vertex positions
        faces: (M, 3) array of triangle indices
    """
    n_major = 2 ** (subdivisions + 3)  # Major circle divisions
    n_minor = 2 ** (subdivisions + 2)  # Minor circle divisions

    vertices = []
    faces = []

    # Generate vertices
    for i in range(n_major):
        theta = 2 * np.pi * i / n_major  # Major circle angle

        for j in range(n_minor):
            phi = 2 * np.pi * j / n_minor  # Minor circle angle

            # Torus parameterization
            x = (major_radius + minor_radius * np.cos(phi)) * np.cos(theta)
            y = (major_radius + minor_radius * np.cos(phi)) * np.sin(theta)
            z = minor_radius * np.sin(phi)

            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Generate faces
    for i in range(n_major):
        for j in range(n_minor):
            v0 = i * n_minor + j
            v1 = i * n_minor + (j + 1) % n_minor
            v2 = ((i + 1) % n_major) * n_minor + (j + 1) % n_minor
            v3 = ((i + 1) % n_major) * n_minor + j

            # Two triangles per quad
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    faces = np.array(faces)

    return vertices, faces


if __name__ == "__main__":
    # Test mesh generation
    print("=== Test Mesh Generation ===\n")

    vertices, faces = create_sphere_mesh(radius=1.0, subdivisions=2)
    print(f"Sphere: {len(vertices)} vertices, {len(faces)} faces")

    vertices, faces = create_cylinder_mesh(radius=1.0, height=2.0, subdivisions=2)
    print(f"Cylinder: {len(vertices)} vertices, {len(faces)} faces")

    vertices, faces = create_saddle_mesh(scale=1.0, subdivisions=2)
    print(f"Saddle: {len(vertices)} vertices, {len(faces)} faces")

    vertices, faces = create_torus_mesh(major_radius=2.0, minor_radius=0.5, subdivisions=2)
    print(f"Torus: {len(vertices)} vertices, {len(faces)} faces")
