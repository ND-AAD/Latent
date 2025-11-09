# Agent 52: NURBS Serialization for Rhino Export

**Day**: 8
**Phase**: Phase 1b - Complete Pipeline
**Duration**: 4-5 hours
**Estimated Cost**: $5-8 (80K tokens, Sonnet)

---

## Mission

Implement serialization of OpenCASCADE NURBS surfaces to Rhino-compatible format for bidirectional exchange.

---

## Context

**Critical**: Close the loop - molds generated in standalone app must return to Rhino for fabrication export.

**Data Flow**:
```
Desktop NURBS molds → JSON serialization → HTTP POST → Grasshopper → Rhino import
```

**Rhino NURBS Format**:
- Control points (P_ij)
- Weights (w_ij)
- Knot vectors (U, V)
- Degrees (p, q)

**Dependencies**:
- Day 7: NURBS generation (OpenCASCADE Geom_BSplineSurface)
- Day 1: HTTP bridge infrastructure

---

## Deliverables

**Files to Create**:
1. `app/export/nurbs_serializer.py` - Main serialization
2. `app/export/rhino_formats.py` - Rhino data structures
3. `tests/test_nurbs_export.py` - Export validation

---

## Requirements

### 1. NURBS Data Extraction from OpenCASCADE

```python
# app/export/nurbs_serializer.py

import numpy as np
from typing import Dict, List, Tuple
import cpp_core
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
                         occt_surface: 'Handle(Geom_BSplineSurface)',
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
                      surface: 'Handle(Geom_BSplineSurface)',
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
                          molds: List[Tuple['Handle(Geom_BSplineSurface)', int]],
                          metadata: Dict = None) -> Dict:
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
```

---

### 2. Rhino Format Utilities

```python
# app/export/rhino_formats.py

import json
from typing import Dict, Any


def validate_nurbs_data(data: Dict) -> bool:
    """
    Validate NURBS data before export.
    
    Checks:
    - Required fields present
    - Array dimensions consistent
    - Knot vector validity
    """
    required = ['degree_u', 'degree_v', 'control_points', 'weights',
                'count_u', 'count_v', 'knots_u', 'knots_v']
    
    for field in required:
        if field not in data:
            return False
    
    # Check dimensions
    num_points = len(data['control_points'])
    expected = data['count_u'] * data['count_v']
    if num_points != expected:
        return False
    
    if len(data['weights']) != num_points:
        return False
    
    # Check knot vector lengths
    # For degree p, with n control points:
    # knot vector has n + p + 1 entries
    expected_u_knots = data['count_u'] + data['degree_u'] + 1
    expected_v_knots = data['count_v'] + data['degree_v'] + 1
    
    if len(data['knots_u']) != expected_u_knots:
        return False
    if len(data['knots_v']) != expected_v_knots:
        return False
    
    return True


def write_json_export(data: Dict, filepath: str, pretty: bool = True):
    """Write NURBS data to JSON file."""
    with open(filepath, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)
```

---

## Testing

```python
# tests/test_nurbs_export.py

import pytest
import json
import cpp_core
from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
from app.export.rhino_formats import validate_nurbs_data


class TestNURBSExport:
    """Test NURBS serialization for Rhino export."""
    
    def test_serialize_simple_surface(self):
        """Test serialization of simple NURBS surface."""
        # Create test geometry
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        
        # Generate NURBS
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], sample_density=20)
        
        # Serialize
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs, name="test_mold")
        
        # Validate structure
        assert rhino_surf.degree_u > 0
        assert rhino_surf.degree_v > 0
        assert len(rhino_surf.control_points) > 0
        assert len(rhino_surf.weights) == len(rhino_surf.control_points)
        assert len(rhino_surf.knots_u) > 0
        assert len(rhino_surf.knots_v) > 0
    
    def test_knot_vector_validity(self):
        """Test knot vector extraction and validation."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)
        
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)
        
        # Knot vectors should be non-decreasing
        assert all(rhino_surf.knots_u[i] <= rhino_surf.knots_u[i+1]
                  for i in range(len(rhino_surf.knots_u) - 1))
        assert all(rhino_surf.knots_v[i] <= rhino_surf.knots_v[i+1]
                  for i in range(len(rhino_surf.knots_v) - 1))
    
    def test_json_serialization(self):
        """Test conversion to JSON."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)
        
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs)
        
        # Convert to dict
        data = rhino_surf.to_dict()
        
        # Validate
        assert validate_nurbs_data(data)
        
        # Should be JSON-serializable
        json_str = json.dumps(data)
        assert len(json_str) > 0
        
        # Round-trip
        recovered = json.loads(json_str)
        assert recovered['degree_u'] == data['degree_u']
        assert recovered['degree_v'] == data['degree_v']
    
    def test_mold_set_export(self):
        """Test exporting complete mold set."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        
        # Generate multiple molds
        molds = [
            (generator.fit_nurbs_surface([0], 20), 1),
            (generator.fit_nurbs_surface([0], 20), 2),
        ]
        
        serializer = NURBSSerializer()
        export_data = serializer.serialize_mold_set(
            molds,
            metadata={'draft_angle': 2.0, 'wall_thickness': 40.0}
        )
        
        # Validate structure
        assert export_data['type'] == 'ceramic_mold_set'
        assert 'version' in export_data
        assert len(export_data['molds']) == 2
        assert 'metadata' in export_data
        assert export_data['metadata']['draft_angle'] == 2.0
    
    def _create_simple_cage(self):
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Success Criteria

- [ ] OpenCASCADE NURBS data extracted correctly
- [ ] Control points, weights, knots serialized
- [ ] Knot vectors flattened (multiplicities expanded)
- [ ] JSON validation passes
- [ ] Round-trip serialization works
- [ ] Mold set export complete
- [ ] All tests pass

---

## Performance Notes

**Expected**:
- Serialization: <10ms per surface
- JSON encoding: <50ms for typical mold set
- Memory: ~1KB per surface

---

## Integration Notes

**Used by**:
- Agent 53: Grasshopper POST endpoint (receives this data)
- Agent 55: Mold workflow orchestration

**Provides**:
- Rhino-compatible NURBS format
- Complete mold set packaging
- Metadata preservation

**File Placement**:
```
app/
├── export/
│   ├── __init__.py
│   ├── nurbs_serializer.py    ← YOU CREATE THIS
│   └── rhino_formats.py        ← YOU CREATE THIS
tests/
└── test_nurbs_export.py        ← YOU CREATE THIS
```

---

**Ready to begin!**
