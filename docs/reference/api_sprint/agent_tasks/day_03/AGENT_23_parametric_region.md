# Agent 23: Parametric Region Data Structure

**Day**: 3 | **Duration**: 3-4h | **Cost**: $3-5

## Mission
Implement ParametricRegion data class that stores regions in (face_id, u, v) parameter space (NOT as geometry).

## Deliverables
- `app/state/parametric_region.py` - ParametricRegion class
- `tests/test_parametric_region.py` - Region tests

## Requirements
**ParametricRegion Class**:
```python
@dataclass
class ParametricRegion:
    id: str
    faces: List[int]  # SubD face indices
    boundary: List[ParametricCurve]  # Curves in (face_id, u, v) space
    unity_principle: str  # What unifies this region
    unity_strength: float  # 0.0-1.0 resonance score
    pinned: bool  # Preserved across re-analysis
    metadata: Dict[str, Any]  # Lens-specific data
```

**Key Methods**:
- `to_json()` - Serialize to JSON
- `from_json()` - Deserialize from JSON
- `contains_point(face_id, u, v)` - Point-in-region test
- `compute_area()` - Area in parameter space
- `merge(other)` - Combine two regions

## Success Criteria
- [ ] ParametricRegion class complete
- [ ] Stored in parameter space (NOT geometry)
- [ ] JSON serialization working
- [ ] All methods implemented
- [ ] Tests pass

**Ready!**
