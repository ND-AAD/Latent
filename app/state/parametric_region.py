"""
Parametric Region Definition
A region defined in parameter space (face_id, u, v) for lossless representation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ParametricRegion:
    """
    A region defined in parameter space

    Represents a collection of SubD faces that form a coherent region
    based on mathematical analysis (curvature, spectral, flow, etc.)

    Key principle: Regions are defined parametrically in (face_id, u, v) space
    to maintain exact mathematical representation until fabrication.
    """
    id: str
    faces: List[int]  # Face indices in SubD
    boundary: Optional[Any] = None  # Will be ParametricCurve (future)
    unity_principle: str = ""  # Mathematical lens that discovered this region
    unity_strength: float = 0.0  # Resonance score [0.0, 1.0]
    pinned: bool = False  # User has approved this region
    modified: bool = False  # Region has been manually edited
    surface: Optional[Any] = None  # Generated NURBS surface (future)
    constraints_passed: bool = True  # Draft angle, thickness constraints met

    def __hash__(self):
        """Make region hashable by its unique ID"""
        return hash(self.id)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize region to dictionary for JSON export

        Returns:
            Dictionary representation of the region
        """
        return {
            'id': self.id,
            'faces': self.faces,
            'unity_principle': self.unity_principle,
            'unity_strength': self.unity_strength,
            'pinned': self.pinned,
            'modified': self.modified,
            'constraints_passed': self.constraints_passed,
            # Note: boundary and surface are not serialized in v1
            # They will be regenerated from parametric definition
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParametricRegion':
        """
        Deserialize region from dictionary

        Args:
            data: Dictionary containing region data

        Returns:
            ParametricRegion instance
        """
        return cls(
            id=data['id'],
            faces=data['faces'],
            unity_principle=data.get('unity_principle', ''),
            unity_strength=data.get('unity_strength', 0.0),
            pinned=data.get('pinned', False),
            modified=data.get('modified', False),
            constraints_passed=data.get('constraints_passed', True),
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
