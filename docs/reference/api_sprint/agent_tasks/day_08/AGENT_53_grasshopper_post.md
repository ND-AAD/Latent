# Agent 53: Grasshopper POST Endpoint

**Day**: 8
**Duration**: 3-4 hours
**Cost**: $2-4 (60K tokens)

---

## Mission

Extend Grasshopper HTTP server with POST /molds endpoint to receive and import NURBS molds from desktop app.

---

## Context

Complete the bidirectional loop:
```
Rhino SubD → Desktop analysis → NURBS molds → POST to Grasshopper → Import to Rhino
```

**Dependencies**:
- Agent 52: NURBS serialization format
- Day 1: Grasshopper HTTP server base

---

## Deliverables

**File**: `rhino/grasshopper_http_server_control_cage.py` (enhance existing)

---

## Requirements

```python
# Add to grasshopper_http_server_control_cage.py

from http.server import BaseHTTPRequestHandler
import json
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg


class SubDHTTPHandler(BaseHTTPRequestHandler):
    # ... existing GET /subd handler ...
    
    def do_POST(self):
        """Handle POST requests for mold import."""
        if self.path == '/molds':
            self._handle_mold_import()
        else:
            self.send_error(404, f"POST endpoint not found: {self.path}")
    
    def _handle_mold_import(self):
        """
        Import NURBS molds sent from desktop app.
        
        Expected JSON:
        {
            "type": "ceramic_mold_set",
            "molds": [
                {
                    "name": "mold_1",
                    "degree_u": 3,
                    "degree_v": 3,
                    "control_points": [[x,y,z], ...],
                    "weights": [w, ...],
                    "count_u": n,
                    "count_v": m,
                    "knots_u": [u0, u1, ...],
                    "knots_v": [v0, v1, ...]
                },
                ...
            ]
        }
        """
        # Read POST body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate
            if data.get('type') != 'ceramic_mold_set':
                self.send_error(400, "Invalid data type")
                return
            
            # Import each mold
            imported_ids = []
            for mold_data in data['molds']:
                guid = self._import_nurbs_surface(mold_data)
                if guid:
                    imported_ids.append(str(guid))
            
            # Response
            response = {
                "status": "success",
                "imported_count": len(imported_ids),
                "guids": imported_ids
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
            print(f"Imported {len(imported_ids)} molds to Rhino")
            
        except Exception as e:
            self.send_error(500, f"Import failed: {str(e)}")
    
    def _import_nurbs_surface(self, mold_data):
        """
        Create Rhino NurbsSurface from serialized data.
        
        Returns:
            GUID of created surface
        """
        try:
            # Extract data
            degree_u = mold_data['degree_u']
            degree_v = mold_data['degree_v']
            count_u = mold_data['count_u']
            count_v = mold_data['count_v']
            
            # Create NurbsSurface
            surface = rg.NurbsSurface.Create(
                dimension=3,
                isRational=True,
                orderU=degree_u + 1,  # Rhino uses order = degree + 1
                orderV=degree_v + 1,
                controlPointCountU=count_u,
                controlPointCountV=count_v
            )
            
            # Set control points and weights
            points = mold_data['control_points']
            weights = mold_data['weights']
            
            idx = 0
            for i in range(count_u):
                for j in range(count_v):
                    x, y, z = points[idx]
                    w = weights[idx]
                    surface.Points.SetPoint(i, j, x, y, z, w)
                    idx += 1
            
            # Set knot vectors
            for i, knot in enumerate(mold_data['knots_u']):
                surface.KnotsU[i] = knot
            for i, knot in enumerate(mold_data['knots_v']):
                surface.KnotsV[i] = knot
            
            # Add to Rhino document
            guid = rs.AddSurface(surface)
            
            # Set name
            if 'name' in mold_data:
                rs.ObjectName(guid, mold_data['name'])
            
            return guid
            
        except Exception as e:
            print(f"Failed to import surface: {e}")
            return None
```

---

## Testing

Test with curl:
```bash
curl -X POST http://localhost:8888/molds \
  -H "Content-Type: application/json" \
  -d @test_mold.json
```

---

## Success Criteria

- [ ] POST /molds endpoint receives data
- [ ] NURBS imported to Rhino correctly
- [ ] Control points match original
- [ ] Knot vectors set correctly
- [ ] GUIDs returned in response
- [ ] Error handling robust

---

**Ready to begin!**
