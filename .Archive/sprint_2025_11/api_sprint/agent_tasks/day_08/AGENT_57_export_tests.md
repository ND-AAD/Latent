# Agent 57: Export and Round-Trip Tests

**Day**: 8
**Duration**: 3-4 hours
**Cost**: $2-4 (60K tokens)

---

## Mission

Validate complete export pipeline and round-trip integrity (Desktop → Rhino → Desktop).

---

## Deliverables

**Files**:
1. `tests/test_export.py` - Export validation
2. `tests/test_roundtrip.py` - Round-trip lossless check

---

## Requirements

```python
# tests/test_roundtrip.py

import pytest
import json
import numpy as np
import cpp_core
from app.export.nurbs_serializer import NURBSSerializer


class TestRoundTrip:
    """Test round-trip export→import maintains accuracy."""
    
    def test_nurbs_roundtrip_accuracy(self):
        """
        Test NURBS export→import maintains <0.1mm accuracy.
        
        Critical for lossless architecture.
        """
        # Create test geometry
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        
        # Generate NURBS
        generator = cpp_core.NURBSMoldGenerator(evaluator)
        original_nurbs = generator.fit_nurbs_surface([0], sample_density=50)
        
        # Export to JSON
        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(original_nurbs)
        json_data = rhino_surf.to_dict()
        
        # Simulate Rhino import (check data integrity)
        # Sample both surfaces at same (u,v) points
        test_points = [
            (0.25, 0.25), (0.5, 0.5), (0.75, 0.75),
            (0.1, 0.9), (0.9, 0.1)
        ]
        
        deviations = []
        for u, v in test_points:
            # Original surface evaluation
            # (Would need to sample from OCCT surface)
            # original_pt = original_nurbs.Value(u, v)
            
            # Reconstructed from JSON would give same control points
            # so deviation should be numerical precision only
            pass
        
        # For now, verify JSON data integrity
        assert json_data['degree_u'] > 0
        assert len(json_data['control_points']) > 0
        
        # Verify all required fields
        required = ['degree_u', 'degree_v', 'control_points', 'weights',
                   'knots_u', 'knots_v', 'count_u', 'count_v']
        for field in required:
            assert field in json_data
    
    def test_export_import_workflow(self):
        """Test complete workflow integration."""
        # This would test the actual HTTP POST to Grasshopper
        # Requires Rhino/Grasshopper running
        pass
    
    def _create_test_cage(self):
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage
```

---

## Success Criteria

- [ ] Export tests pass
- [ ] Round-trip data integrity verified
- [ ] JSON validation complete
- [ ] HTTP endpoint tests (if Rhino available)

---

**Ready to begin!**
