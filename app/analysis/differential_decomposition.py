"""
Differential Decomposition - Curvature-Based Region Discovery

This mathematical lens discovers natural coherent regions based on differential
geometry properties: principal curvatures, mean curvature, and Gaussian curvature.

Mathematical Basis:
- Surfaces naturally decompose into regions of similar curvature behavior
- Ridge and valley lines serve as natural boundaries
- Curvature coherence indicates geometric unity

Region Types Discovered:
- Elliptic regions (K > 0): Bowl-like, convex/concave
- Hyperbolic regions (K < 0): Saddle-like, anticlastic
- Parabolic regions (K ≈ 0): Cylindrical, developable
- Planar regions (K ≈ 0, H ≈ 0): Flat

Author: Ceramic Mold Analyzer
Date: November 2025
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import scipy.ndimage as ndimage
from collections import defaultdict

from app.geometry.curvature import MeshCurvatureEstimator, CurvatureData
from app.state.app_state import ParametricRegion


@dataclass
class DifferentialDecompositionParams:
    """Parameters for differential decomposition algorithm."""

    # Curvature classification thresholds
    gaussian_threshold: float = 0.01  # K threshold for parabolic/elliptic/hyperbolic
    mean_threshold: float = 0.01      # H threshold for planar

    # Region growing parameters
    min_region_size: int = 3  # Minimum faces in a region
    curvature_tolerance: float = 0.3  # Max curvature difference for region coherence

    # Advanced parameters
    merge_small_regions: bool = True  # Merge tiny regions into neighbors
    extract_boundaries: bool = True    # Extract ridge/valley boundaries


class DifferentialDecomposition:
    """
    Discovers regions based on curvature coherence.

    This is the first mathematical lens - the simplest and most intuitive.
    Regions are discovered by grouping faces with similar curvature behavior.
    """

    def __init__(self, params: Optional[DifferentialDecompositionParams] = None):
        """
        Initialize differential decomposition engine.

        Args:
            params: Algorithm parameters (uses defaults if None)
        """
        self.params = params if params is not None else DifferentialDecompositionParams()

    def analyze(self,
                vertices: np.ndarray,
                faces: np.ndarray,
                pinned_faces: Optional[List[int]] = None) -> List[ParametricRegion]:
        """
        Discover regions based on curvature analysis.

        Args:
            vertices: (N, 3) array of vertex positions
            faces: (M, 3 or 4) array of face indices
            pinned_faces: List of face indices to exclude from analysis

        Returns:
            List of discovered ParametricRegion objects
        """
        print(f"\n=== Differential Decomposition Analysis ===")
        print(f"Mesh: {len(vertices)} vertices, {len(faces)} faces")

        # Step 1: Compute curvatures at all faces
        print("Step 1: Computing curvatures...")
        estimator = MeshCurvatureEstimator(vertices, faces)
        curvatures = estimator.compute_all_face_curvatures()

        # Step 2: Classify faces by curvature type
        print("Step 2: Classifying faces by curvature type...")
        face_types = self._classify_faces(curvatures)

        # Count classification results
        type_counts = defaultdict(int)
        for face_type in face_types.values():
            type_counts[face_type] += 1

        print(f"  Elliptic (bowl-like): {type_counts['elliptic']} faces")
        print(f"  Hyperbolic (saddle-like): {type_counts['hyperbolic']} faces")
        print(f"  Parabolic (cylindrical): {type_counts['parabolic']} faces")
        print(f"  Planar (flat): {type_counts['planar']} faces")

        # Step 3: Build face adjacency graph
        print("Step 3: Building face adjacency...")
        adjacency = self._build_face_adjacency(faces)

        # Step 4: Grow regions from seeds
        print("Step 4: Growing regions from curvature coherence...")
        regions = self._discover_regions(
            faces=faces,
            curvatures=curvatures,
            face_types=face_types,
            adjacency=adjacency,
            pinned_faces=set(pinned_faces) if pinned_faces else set()
        )

        print(f"  Discovered {len(regions)} initial regions")

        # Step 5: Merge small regions
        if self.params.merge_small_regions:
            print("Step 5: Merging small regions...")
            regions = self._merge_small_regions(
                regions, adjacency, curvatures, min_size=self.params.min_region_size
            )
            print(f"  After merging: {len(regions)} regions")

        # Step 6: Convert to ParametricRegion objects
        print("Step 6: Creating ParametricRegion objects...")
        parametric_regions = self._create_parametric_regions(
            regions, curvatures, face_types
        )

        print(f"=== Analysis Complete: {len(parametric_regions)} regions discovered ===\n")

        return parametric_regions

    def _classify_faces(self, curvatures: Dict[int, CurvatureData]) -> Dict[int, str]:
        """
        Classify each face by curvature type.

        Returns:
            Dictionary mapping face_idx → curvature_type
        """
        face_types = {}

        for face_idx, curv in curvatures.items():
            # Use the curvature_type property from CurvatureData
            face_types[face_idx] = curv.curvature_type

        return face_types

    def _build_face_adjacency(self, faces: np.ndarray) -> Dict[int, Set[int]]:
        """
        Build face adjacency graph (which faces share edges).

        Returns:
            Dictionary mapping face_idx → set of adjacent face indices
        """
        adjacency = defaultdict(set)

        # Build edge→face mapping
        edge_to_faces = defaultdict(list)

        for face_idx, face in enumerate(faces):
            n = len(face)
            for i in range(n):
                # Edge from vertex i to vertex (i+1) % n
                v1, v2 = face[i], face[(i + 1) % n]
                # Canonical edge (smaller index first)
                edge = tuple(sorted([v1, v2]))
                edge_to_faces[edge].append(face_idx)

        # Build adjacency from shared edges
        for edge, face_list in edge_to_faces.items():
            if len(face_list) == 2:
                f1, f2 = face_list
                adjacency[f1].add(f2)
                adjacency[f2].add(f1)

        return adjacency

    def _discover_regions(self,
                          faces: np.ndarray,
                          curvatures: Dict[int, CurvatureData],
                          face_types: Dict[int, str],
                          adjacency: Dict[int, Set[int]],
                          pinned_faces: Set[int]) -> List[Dict]:
        """
        Discover regions via region growing from seeds.

        Algorithm:
        1. Seed regions from faces with extreme curvatures (local max/min)
        2. Grow regions by adding adjacent faces with similar curvature
        3. Continue until all faces are assigned

        Returns:
            List of region dictionaries: [{'faces': [...], 'type': str, 'coherence': float}, ...]
        """
        # Track which faces are already assigned
        assigned = pinned_faces.copy()  # Start with pinned faces excluded
        regions = []

        # Sort faces by curvature magnitude (seed from extremes)
        face_curvature_magnitudes = [
            (face_idx, abs(curv.gaussian))
            for face_idx, curv in curvatures.items()
            if face_idx not in pinned_faces
        ]
        face_curvature_magnitudes.sort(key=lambda x: x[1], reverse=True)

        # Seed-based region growing
        for seed_face, _ in face_curvature_magnitudes:
            if seed_face in assigned:
                continue

            # Start new region from this seed
            region_faces = self._grow_region_from_seed(
                seed_face=seed_face,
                curvatures=curvatures,
                face_types=face_types,
                adjacency=adjacency,
                assigned=assigned
            )

            if len(region_faces) > 0:
                # Compute region properties
                region_type = self._determine_region_type(region_faces, face_types)
                coherence = self._compute_coherence(region_faces, curvatures)

                regions.append({
                    'faces': region_faces,
                    'type': region_type,
                    'coherence': coherence
                })

                # Mark faces as assigned
                assigned.update(region_faces)

        # Handle any remaining unassigned faces
        unassigned = set(range(len(faces))) - assigned
        if unassigned:
            # Assign to nearest region or create singleton regions
            for face_idx in unassigned:
                regions.append({
                    'faces': [face_idx],
                    'type': face_types[face_idx],
                    'coherence': 1.0  # Singleton has perfect coherence
                })

        return regions

    def _grow_region_from_seed(self,
                                seed_face: int,
                                curvatures: Dict[int, CurvatureData],
                                face_types: Dict[int, str],
                                adjacency: Dict[int, Set[int]],
                                assigned: Set[int]) -> List[int]:
        """
        Grow a region from a seed face using curvature coherence.

        Returns:
            List of face indices in the grown region
        """
        region_faces = [seed_face]
        frontier = [seed_face]
        seed_type = face_types[seed_face]
        seed_curv = curvatures[seed_face]

        while frontier:
            current_face = frontier.pop(0)

            # Check adjacent faces
            for neighbor_face in adjacency[current_face]:
                if neighbor_face in assigned:
                    continue

                neighbor_type = face_types[neighbor_face]
                neighbor_curv = curvatures[neighbor_face]

                # Check if neighbor is compatible with region
                if self._is_compatible(seed_curv, neighbor_curv, seed_type, neighbor_type):
                    region_faces.append(neighbor_face)
                    frontier.append(neighbor_face)
                    assigned.add(neighbor_face)

        return region_faces

    def _is_compatible(self,
                       seed_curv: CurvatureData,
                       neighbor_curv: CurvatureData,
                       seed_type: str,
                       neighbor_type: str) -> bool:
        """
        Check if a neighbor face is compatible with the seed region.

        Compatibility criteria:
        1. Must have same curvature type (elliptic/hyperbolic/parabolic/planar)
        2. Curvature values must be within tolerance

        Returns:
            True if compatible, False otherwise
        """
        # Type must match
        if seed_type != neighbor_type:
            return False

        # Curvature values must be similar
        k_diff = abs(seed_curv.gaussian - neighbor_curv.gaussian)
        h_diff = abs(seed_curv.mean - neighbor_curv.mean)

        # Use relative tolerance
        k_avg = (abs(seed_curv.gaussian) + abs(neighbor_curv.gaussian)) / 2
        h_avg = (abs(seed_curv.mean) + abs(neighbor_curv.mean)) / 2

        if k_avg > 1e-6:
            k_relative = k_diff / k_avg
            if k_relative > self.params.curvature_tolerance:
                return False

        if h_avg > 1e-6:
            h_relative = h_diff / h_avg
            if h_relative > self.params.curvature_tolerance:
                return False

        return True

    def _determine_region_type(self,
                                region_faces: List[int],
                                face_types: Dict[int, str]) -> str:
        """
        Determine dominant curvature type for a region.

        Returns:
            Most common type in the region
        """
        type_counts = defaultdict(int)
        for face_idx in region_faces:
            type_counts[face_types[face_idx]] += 1

        # Return most common type
        return max(type_counts.items(), key=lambda x: x[1])[0]

    def _compute_coherence(self,
                           region_faces: List[int],
                           curvatures: Dict[int, CurvatureData]) -> float:
        """
        Compute coherence score for a region.

        Coherence = 1 - (curvature_variance / curvature_mean)
        High coherence means faces have similar curvatures.

        Returns:
            Coherence score [0, 1] (1 = perfect coherence)
        """
        if len(region_faces) == 1:
            return 1.0

        # Collect Gaussian curvatures
        gaussians = [curvatures[f].gaussian for f in region_faces]
        means = [curvatures[f].mean for f in region_faces]

        # Compute variance
        k_var = np.var(gaussians)
        h_var = np.var(means)

        # Compute mean absolute value
        k_mean = np.mean(np.abs(gaussians))
        h_mean = np.mean(np.abs(means))

        # Coherence (inverse of coefficient of variation)
        if k_mean > 1e-6:
            k_coherence = 1.0 / (1.0 + np.sqrt(k_var) / k_mean)
        else:
            k_coherence = 1.0

        if h_mean > 1e-6:
            h_coherence = 1.0 / (1.0 + np.sqrt(h_var) / h_mean)
        else:
            h_coherence = 1.0

        # Average coherence
        coherence = (k_coherence + h_coherence) / 2.0

        return float(np.clip(coherence, 0.0, 1.0))

    def _merge_small_regions(self,
                             regions: List[Dict],
                             adjacency: Dict[int, Set[int]],
                             curvatures: Dict[int, CurvatureData],
                             min_size: int) -> List[Dict]:
        """
        Merge regions smaller than min_size into adjacent neighbors.

        Returns:
            Merged list of regions
        """
        # Separate small and large regions
        small_regions = [r for r in regions if len(r['faces']) < min_size]
        large_regions = [r for r in regions if len(r['faces']) >= min_size]

        if not small_regions:
            return regions  # Nothing to merge

        # Build region adjacency (which regions share edges)
        face_to_region = {}
        for region_idx, region in enumerate(large_regions):
            for face_idx in region['faces']:
                face_to_region[face_idx] = region_idx

        # Merge each small region into best neighbor
        for small_region in small_regions:
            # Find adjacent large regions
            neighbor_regions = set()
            for face_idx in small_region['faces']:
                for neighbor_face in adjacency[face_idx]:
                    if neighbor_face in face_to_region:
                        neighbor_regions.add(face_to_region[neighbor_face])

            if neighbor_regions:
                # Merge into most compatible neighbor
                best_neighbor = min(
                    neighbor_regions,
                    key=lambda r_idx: abs(
                        large_regions[r_idx]['coherence'] - small_region['coherence']
                    )
                )

                # Add small region faces to best neighbor
                large_regions[best_neighbor]['faces'].extend(small_region['faces'])

                # Update face_to_region mapping
                for face_idx in small_region['faces']:
                    face_to_region[face_idx] = best_neighbor
            else:
                # No neighbors - keep as is
                large_regions.append(small_region)

        # Recompute coherence for merged regions
        for region in large_regions:
            region['coherence'] = self._compute_coherence(region['faces'], curvatures)

        return large_regions

    def _create_parametric_regions(self,
                                    regions: List[Dict],
                                    curvatures: Dict[int, CurvatureData],
                                    face_types: Dict[int, str]) -> List[ParametricRegion]:
        """
        Convert internal region representation to ParametricRegion objects.

        Returns:
            List of ParametricRegion objects for application state
        """
        parametric_regions = []

        for region_idx, region in enumerate(regions):
            # Create unity principle description
            region_type = region['type']
            num_faces = len(region['faces'])
            coherence = region['coherence']

            unity_principle = self._generate_unity_description(
                region_type, num_faces, coherence
            )

            # Create ParametricRegion
            parametric_region = ParametricRegion(
                id=f"differential_region_{region_idx}",
                faces=region['faces'],
                boundary=None,  # TODO: Extract boundary curves (future enhancement)
                unity_principle=unity_principle,
                unity_strength=coherence,
                pinned=False
            )

            parametric_regions.append(parametric_region)

        return parametric_regions

    def _generate_unity_description(self,
                                     region_type: str,
                                     num_faces: int,
                                     coherence: float) -> str:
        """
        Generate human-readable unity principle description.

        Returns:
            String describing what unifies this region
        """
        type_descriptions = {
            'elliptic': 'bowl-like curvature (convex/concave)',
            'hyperbolic': 'saddle-like curvature (anticlastic)',
            'parabolic': 'cylindrical curvature (developable)',
            'planar': 'flat/minimal curvature'
        }

        desc = type_descriptions.get(region_type, 'unknown curvature')

        return f"Similar {desc} across {num_faces} faces"


if __name__ == "__main__":
    # Test differential decomposition on simple geometries
    from app.geometry.test_meshes import create_sphere_mesh, create_torus_mesh

    print("\n=== Testing Differential Decomposition ===\n")

    # Test 1: Sphere (should be 1 elliptic region)
    print("Test 1: Sphere")
    vertices, faces = create_sphere_mesh(radius=1.0, subdivisions=2)
    engine = DifferentialDecomposition()
    regions = engine.analyze(vertices, faces)

    for region in regions:
        print(f"  {region.id}: {region.unity_principle}")
        print(f"    Strength: {region.unity_strength:.3f}, Faces: {len(region.faces)}")

    # Test 2: Torus (should have multiple regions - elliptic and hyperbolic)
    print("\nTest 2: Torus")
    vertices, faces = create_torus_mesh(major_radius=2.0, minor_radius=0.5, subdivisions=2)
    regions = engine.analyze(vertices, faces)

    for region in regions:
        print(f"  {region.id}: {region.unity_principle}")
        print(f"    Strength: {region.unity_strength:.3f}, Faces: {len(region.faces)}")
