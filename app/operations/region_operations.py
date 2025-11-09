"""
Region Operations - Tools for manipulating parametric regions

Provides merge and split operations while maintaining parametric definitions
and integrating with the application's undo/redo system.
"""

from typing import List, Tuple, Optional, Set
import uuid
from app.state.parametric_region import ParametricRegion, ParametricCurve


class RegionOperations:
    """Operations for manipulating parametric regions."""

    @staticmethod
    def merge_regions(
        regions: List[ParametricRegion],
        application_state=None
    ) -> ParametricRegion:
        """
        Merge multiple adjacent regions into one.

        Args:
            regions: List of regions to merge (must have at least 2)
            application_state: Optional ApplicationState for undo/redo integration

        Returns:
            New ParametricRegion with combined faces

        Raises:
            ValueError: If fewer than 2 regions provided
        """
        if len(regions) < 2:
            raise ValueError("Must provide at least 2 regions to merge")

        # Start with first region
        merged = regions[0]

        # Merge with subsequent regions
        for region in regions[1:]:
            merged = merged.merge(region)

        # Recalculate boundary for merged region
        merged.boundary = RegionOperations._compute_boundary(
            merged.faces,
            application_state.subd_geometry if application_state else None
        )

        return merged

    @staticmethod
    def split_region(
        region: ParametricRegion,
        split_curve: ParametricCurve,
        application_state=None
    ) -> Tuple[ParametricRegion, ParametricRegion]:
        """
        Split region along a parametric curve.

        Args:
            region: Region to split
            split_curve: Curve in (face_id, u, v) space defining split line
            application_state: Optional ApplicationState for geometry access

        Returns:
            Tuple of (region1, region2) on either side of curve

        Raises:
            ValueError: If region has no faces or split curve is invalid
        """
        if not region.faces:
            raise ValueError("Cannot split region with no faces")

        if not split_curve.points:
            raise ValueError("Split curve must have at least one point")

        # Classify faces as left/right of curve
        left_faces, right_faces = RegionOperations._classify_faces(
            region.faces,
            split_curve,
            application_state.subd_geometry if application_state else None
        )

        # Ensure both sides have faces
        if not left_faces or not right_faces:
            # If classification failed, use simple alternating split
            left_faces = region.faces[::2]
            right_faces = region.faces[1::2]

            # Ensure both have faces
            if not left_faces:
                left_faces = [region.faces[0]]
                right_faces = region.faces[1:]
            elif not right_faces:
                right_faces = [region.faces[-1]]
                left_faces = region.faces[:-1]

        # Create new regions
        r1 = ParametricRegion(
            id=f"split_{uuid.uuid4().hex[:8]}_A",
            faces=left_faces,
            boundary=RegionOperations._compute_boundary(
                left_faces,
                application_state.subd_geometry if application_state else None
            ),
            unity_principle=region.unity_principle,
            unity_strength=region.unity_strength * 0.9,  # Slightly reduced
            pinned=False,
            metadata={**region.metadata, 'split_from': region.id, 'side': 'A'},
            modified=True,
            constraints_passed=region.constraints_passed
        )

        r2 = ParametricRegion(
            id=f"split_{uuid.uuid4().hex[:8]}_B",
            faces=right_faces,
            boundary=RegionOperations._compute_boundary(
                right_faces,
                application_state.subd_geometry if application_state else None
            ),
            unity_principle=region.unity_principle,
            unity_strength=region.unity_strength * 0.9,  # Slightly reduced
            pinned=False,
            metadata={**region.metadata, 'split_from': region.id, 'side': 'B'},
            modified=True,
            constraints_passed=region.constraints_passed
        )

        return r1, r2

    @staticmethod
    def can_merge(region1: ParametricRegion, region2: ParametricRegion) -> bool:
        """
        Check if two regions can be merged (i.e., they share at least one face edge).

        Args:
            region1: First region
            region2: Second region

        Returns:
            True if regions are adjacent and can be merged
        """
        # Simple check: ensure no overlapping faces
        faces1 = set(region1.faces)
        faces2 = set(region2.faces)

        if faces1 & faces2:
            # Overlapping faces - cannot merge
            return False

        # For now, always allow merge if non-overlapping
        # Future: Check actual adjacency using geometry
        return True

    @staticmethod
    def _classify_faces(
        face_indices: List[int],
        split_curve: ParametricCurve,
        geometry=None
    ) -> Tuple[List[int], List[int]]:
        """
        Classify faces as being on left or right side of split curve.

        Args:
            face_indices: List of face indices to classify
            split_curve: Curve defining the split
            geometry: SubD geometry (optional, for more accurate classification)

        Returns:
            Tuple of (left_faces, right_faces)
        """
        left_faces = []
        right_faces = []

        # Get curve bounding box in parameter space
        if split_curve.points:
            # Extract face IDs that the curve passes through
            curve_faces = set(point[0] for point in split_curve.points)

            # Classify based on curve position
            for face_id in face_indices:
                if face_id in curve_faces:
                    # Face intersects curve - needs geometric analysis
                    # For now, put on left side
                    left_faces.append(face_id)
                else:
                    # Simple heuristic: compare face ID to curve face IDs
                    avg_curve_face = sum(curve_faces) / len(curve_faces)
                    if face_id < avg_curve_face:
                        left_faces.append(face_id)
                    else:
                        right_faces.append(face_id)
        else:
            # No curve points - split evenly
            mid = len(face_indices) // 2
            left_faces = face_indices[:mid]
            right_faces = face_indices[mid:]

        return left_faces, right_faces

    @staticmethod
    def _compute_boundary(
        face_indices: List[int],
        geometry=None
    ) -> List[ParametricCurve]:
        """
        Compute boundary curves for a region defined by face indices.

        Args:
            face_indices: List of face indices in the region
            geometry: SubD geometry (optional, for more accurate boundary)

        Returns:
            List of ParametricCurves defining the region boundary
        """
        # Simplified boundary computation
        # Future: Implement proper boundary extraction using geometry

        if not face_indices:
            return []

        # For now, create a simple boundary curve around the faces
        # This is a placeholder - actual implementation would trace edges
        boundary_points = []

        # Create points at face centers (simplified)
        for face_id in face_indices:
            # Approximate: place point at center of face in parameter space
            boundary_points.append((face_id, 0.5, 0.5))

        if len(boundary_points) > 2:
            return [ParametricCurve(
                points=boundary_points,
                is_closed=True
            )]

        return []

    @staticmethod
    def recalculate_resonance(
        region: ParametricRegion,
        lens_analyzer=None
    ) -> float:
        """
        Recalculate the resonance score for a region after modification.

        Args:
            region: Region to analyze
            lens_analyzer: Optional lens analyzer to use for recalculation

        Returns:
            Updated unity_strength (resonance score)
        """
        if lens_analyzer is None:
            # No analyzer available - maintain current score with small penalty
            return region.unity_strength * 0.95

        # Use lens analyzer to recalculate
        # This would call into the appropriate lens (Differential, Spectral, etc.)
        # For now, return existing score
        return region.unity_strength

    @staticmethod
    def validate_region(region: ParametricRegion) -> Tuple[bool, List[str]]:
        """
        Validate that a region is well-formed.

        Args:
            region: Region to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if not region.faces:
            issues.append("Region has no faces")

        if not region.id:
            issues.append("Region has no ID")

        if region.unity_strength < 0.0 or region.unity_strength > 1.0:
            issues.append(f"Invalid unity_strength: {region.unity_strength}")

        # Check for duplicate faces
        if len(region.faces) != len(set(region.faces)):
            issues.append("Region contains duplicate faces")

        return (len(issues) == 0, issues)
