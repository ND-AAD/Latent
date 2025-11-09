"""
NURBS Serialization for Rhino Export

Extracts NURBS data from OpenCASCADE surfaces and serializes to Rhino-compatible format.

CRITICAL: Maintains exact mathematical representation during transfer.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class RhinoNURBSSurface:
    """
    Rhino-compatible NURBS surface representation.

    Matches Rhino's NurbsSurface structure for import.
    """
    degree_u: int
    degree_v: int

    # Control points as flat list: [P_00, P_01, ..., P_nm]
    control_points: List[Tuple[float, float, float]]  # (x, y, z)
    weights: List[float]  # w_ij (rational NURBS)

    # Point array dimensions
    count_u: int  # Number of points in U direction
    count_v: int  # Number of points in V direction

    # Knot vectors
    knots_u: List[float]
    knots_v: List[float]

    # Optional metadata
    name: str = ""
    region_id: int = -1
    draft_angle: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)


class NURBSSerializer:
    """
    Extract NURBS data from OpenCASCADE and serialize for Rhino.

    CRITICAL: Maintains exact mathematical representation during transfer.
    """

    def __init__(self):
        pass

    def serialize_surface(self,
                         occt_surface,  # Handle(Geom_BSplineSurface)
                         name: str = "mold",
                         region_id: int = -1) -> RhinoNURBSSurface:
        """
        Extract NURBS data from OpenCASCADE surface.

        Args:
            occt_surface: OpenCASCADE B-spline surface handle
            name: Surface identifier
            region_id: Associated region ID

        Returns:
            RhinoNURBSSurface ready for JSON export
        """
        # Extract degrees
        degree_u = occt_surface.UDegree()
        degree_v = occt_surface.VDegree()

        # Extract control points and weights
        num_u_poles = occt_surface.NbUPoles()
        num_v_poles = occt_surface.NbVPoles()

        control_points = []
        weights = []

        for i in range(1, num_u_poles + 1):  # OCC is 1-indexed
            for j in range(1, num_v_poles + 1):
                pole = occt_surface.Pole(i, j)
                weight = occt_surface.Weight(i, j)

                control_points.append((pole.X(), pole.Y(), pole.Z()))
                weights.append(weight)

        # Extract knot vectors
        knots_u = self._extract_knots(occt_surface, is_u_direction=True)
        knots_v = self._extract_knots(occt_surface, is_u_direction=False)

        return RhinoNURBSSurface(
            degree_u=degree_u,
            degree_v=degree_v,
            control_points=control_points,
            weights=weights,
            count_u=num_u_poles,
            count_v=num_v_poles,
            knots_u=knots_u,
            knots_v=knots_v,
            name=name,
            region_id=region_id
        )

    def _extract_knots(self,
                      surface,  # Handle(Geom_BSplineSurface)
                      is_u_direction: bool) -> List[float]:
        """
        Extract knot vector from OpenCASCADE surface.

        OpenCASCADE stores knots with multiplicities separate.
        Rhino expects flattened knot vector.
        """
        if is_u_direction:
            num_knots = surface.NbUKnots()
            knots = []
            for i in range(1, num_knots + 1):
                knot_value = surface.UKnot(i)
                multiplicity = surface.UMultiplicity(i)
                knots.extend([knot_value] * multiplicity)
        else:
            num_knots = surface.NbVKnots()
            knots = []
            for i in range(1, num_knots + 1):
                knot_value = surface.VKnot(i)
                multiplicity = surface.VMultiplicity(i)
                knots.extend([knot_value] * multiplicity)

        return knots

    def serialize_mold_set(self,
                          molds: List[Tuple[object, int]],  # List[(Handle(Geom_BSplineSurface), region_id)]
                          metadata: Optional[Dict] = None) -> Dict:
        """
        Serialize complete set of molds for a decomposition.

        Args:
            molds: List of (surface, region_id) tuples
            metadata: Additional info (draft angles, demolding vectors, etc.)

        Returns:
            Complete JSON-serializable dict
        """
        serialized_molds = []

        for i, (surface, region_id) in enumerate(molds):
            rhino_surf = self.serialize_surface(
                surface,
                name=f"mold_{region_id}",
                region_id=region_id
            )
            serialized_molds.append(rhino_surf.to_dict())

        export_data = {
            "type": "ceramic_mold_set",
            "version": "1.0",
            "molds": serialized_molds,
            "metadata": metadata or {},
            "timestamp": self._get_timestamp()
        }

        return export_data

    def _get_timestamp(self) -> str:
        """ISO 8601 timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
