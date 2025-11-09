"""
Parametric Region Definition
A region defined in parameter space (face_id, u, v) for lossless representation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import json
import uuid


@dataclass
class ParametricCurve:
    """
    A curve defined in the surface's parameter space (face_id, u, v).
    NOT in 3D coordinates - maintains exact mathematical representation.
    """
    points: List[Tuple[int, float, float]] = field(default_factory=list)  # (face_id, u, v)
    is_closed: bool = False
    length_parameter: Optional[float] = None
    curvature_integral: Optional[float] = None

    def evaluate(self, t: float) -> Tuple[int, float, float]:
        """
        Evaluate curve at parameter t ∈ [0,1]

        Args:
            t: Parameter value between 0 and 1

        Returns:
            (face_id, u, v) tuple at parameter t
        """
        if not self.points:
            raise ValueError("Cannot evaluate empty curve")

        if len(self.points) == 1:
            return self.points[0]

        # Interpolate between points
        segment_count = len(self.points) - (0 if self.is_closed else 1)
        if segment_count == 0:
            return self.points[0]

        t = max(0.0, min(1.0, t))  # Clamp to [0,1]
        segment = min(int(t * segment_count), segment_count - 1)
        local_t = (t * segment_count) - segment

        # Get segment endpoints
        p0 = self.points[segment]
        p1 = self.points[(segment + 1) % len(self.points)]

        # Linear interpolation (assuming same face for simplicity)
        face_id = p0[0]
        u = p0[1] + local_t * (p1[1] - p0[1])
        v = p0[2] + local_t * (p1[2] - p0[2])

        return (face_id, u, v)

    def to_json(self) -> Dict[str, Any]:
        """Serialize curve to JSON-compatible dict"""
        return {
            'points': self.points,
            'is_closed': self.is_closed,
            'length_parameter': self.length_parameter,
            'curvature_integral': self.curvature_integral
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ParametricCurve':
        """Deserialize curve from JSON-compatible dict"""
        return cls(
            points=[tuple(p) for p in data['points']],
            is_closed=data.get('is_closed', False),
            length_parameter=data.get('length_parameter'),
            curvature_integral=data.get('curvature_integral')
        )


@dataclass
class ParametricRegion:
    """
    A region defined in parameter space (face_id, u, v).

    Represents a collection of SubD faces that form a coherent region
    based on mathematical analysis (curvature, spectral, flow, etc.)

    Key principle: Regions are defined parametrically in (face_id, u, v) space
    to maintain exact mathematical representation until fabrication.
    """
    id: str
    faces: List[int]  # SubD face indices
    boundary: List[ParametricCurve] = field(default_factory=list)  # Curves in (face_id, u, v) space
    unity_principle: str = ""  # What unifies this region (mathematical lens)
    unity_strength: float = 0.0  # Resonance score [0.0, 1.0]
    pinned: bool = False  # Preserved across re-analysis
    metadata: Dict[str, Any] = field(default_factory=dict)  # Lens-specific data

    # Legacy fields for backward compatibility
    modified: bool = False  # Region has been manually edited
    surface: Optional[Any] = None  # Generated NURBS surface (future)
    constraints_passed: bool = True  # Draft angle, thickness constraints met

    def __hash__(self):
        """Make region hashable by its unique ID"""
        return hash(self.id)

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize region to JSON-compatible dictionary

        Returns:
            Dictionary representation of the region
        """
        return {
            'id': self.id,
            'faces': self.faces,
            'boundary': [curve.to_json() for curve in self.boundary],
            'unity_principle': self.unity_principle,
            'unity_strength': self.unity_strength,
            'pinned': self.pinned,
            'metadata': self.metadata,
            'modified': self.modified,
            'constraints_passed': self.constraints_passed,
            # Note: surface is not serialized - regenerated from parametric definition
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ParametricRegion':
        """
        Deserialize region from JSON-compatible dictionary

        Args:
            data: Dictionary containing region data

        Returns:
            ParametricRegion instance
        """
        boundary = []
        if 'boundary' in data:
            boundary = [ParametricCurve.from_json(curve_data) for curve_data in data['boundary']]

        return cls(
            id=data['id'],
            faces=data['faces'],
            boundary=boundary,
            unity_principle=data.get('unity_principle', ''),
            unity_strength=data.get('unity_strength', 0.0),
            pinned=data.get('pinned', False),
            metadata=data.get('metadata', {}),
            modified=data.get('modified', False),
            constraints_passed=data.get('constraints_passed', True),
        )

    # Legacy compatibility methods
    def to_dict(self) -> Dict[str, Any]:
        """Legacy method - use to_json() instead"""
        return self.to_json()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParametricRegion':
        """Legacy method - use from_json() instead"""
        return cls.from_json(data)

    def contains_point(self, face_id: int, u: float, v: float) -> bool:
        """
        Test if a point in parameter space is inside this region.

        For now, uses simple face membership test.
        Future: Implement proper point-in-polygon test using boundary curves.

        Args:
            face_id: SubD face index
            u: Parameter u coordinate [0,1]
            v: Parameter v coordinate [0,1]

        Returns:
            True if point is in region
        """
        # Simple implementation: check if face is in region
        # This assumes entire faces belong to regions (which is true for face-based segmentation)
        return face_id in self.faces

    def compute_area(self) -> float:
        """
        Compute approximate area in parameter space.

        For face-based regions, returns the number of faces as a proxy for area.
        Future: Integrate actual surface area from SubD evaluator.

        Returns:
            Approximate area (currently face count)
        """
        # Simple implementation: face count as area proxy
        # Each quad face in parameter space has area ~1.0
        return float(len(self.faces))

    def merge(self, other: 'ParametricRegion') -> 'ParametricRegion':
        """
        Merge this region with another region.

        Creates a new region combining faces from both regions.
        Metadata and boundaries are merged/recalculated.

        Args:
            other: Another ParametricRegion to merge with

        Returns:
            New merged ParametricRegion
        """
        # Combine faces (unique)
        merged_faces = list(set(self.faces + other.faces))
        merged_faces.sort()

        # Create new ID
        merged_id = f"merged_{uuid.uuid4().hex[:8]}"

        # Combine metadata
        merged_metadata = {**self.metadata, **other.metadata}

        # Take stronger unity principle
        if self.unity_strength >= other.unity_strength:
            unity_principle = self.unity_principle
            unity_strength = self.unity_strength
        else:
            unity_principle = other.unity_principle
            unity_strength = other.unity_strength

        # Merge boundaries (for now, take union - future: compute actual merged boundary)
        merged_boundary = self.boundary + other.boundary

        return ParametricRegion(
            id=merged_id,
            faces=merged_faces,
            boundary=merged_boundary,
            unity_principle=f"{self.unity_principle}+{other.unity_principle}" if self.unity_principle != other.unity_principle else unity_principle,
            unity_strength=(self.unity_strength + other.unity_strength) / 2.0,
            pinned=self.pinned or other.pinned,  # Preserve pinned status
            metadata=merged_metadata,
            modified=True,  # Mark as modified since it's a manual merge
            constraints_passed=self.constraints_passed and other.constraints_passed
        )

    def get_face_count(self) -> int:
        """Get number of faces in this region"""
        return len(self.faces)

    def contains_face(self, face_id: int) -> bool:
        """Check if region contains a specific face"""
        return face_id in self.faces

    def get_info(self) -> str:
        """Get human-readable description of the region"""
        status = "Pinned" if self.pinned else "Unpinned"
        return f"Region {self.id}: {len(self.faces)} faces, {self.unity_principle} lens, strength={self.unity_strength:.2f}, {status}"
