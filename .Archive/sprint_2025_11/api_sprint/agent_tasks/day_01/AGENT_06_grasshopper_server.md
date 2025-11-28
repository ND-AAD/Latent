# Agent 6: Grasshopper HTTP Server

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 2-3 hours
**Estimated Cost**: $1-2 (20K tokens, Haiku)

---

## Mission

Create a Grasshopper Python component that serves SubD control cage data via HTTP for the desktop application.

---

## Context

You are creating a Grasshopper component that:
- Receives SubD geometry from Rhino/Grasshopper canvas
- Extracts control cage data (vertices, faces, creases)
- Serves data via HTTP on port 8888
- Responds to `/geometry` endpoint with JSON payload
- Allows desktop app to fetch exact SubD representation

**CRITICAL - REPLACEMENT NOTICE**:
This file REPLACES the existing `rhino/grasshopper_server_control.py` which currently uses **mesh transfer** (Week 3 workaround - INCORRECT for lossless architecture). The new implementation uses **control cage transfer** (CORRECT - preserves exact SubD topology).

**Why this matters**:
- Old approach: SubD → Mesh → JSON (introduces approximation ❌)
- New approach: SubD → Control Cage → JSON (exact, lossless ✅)

**Critical**: Transfer control cage topology, NOT mesh approximation. This preserves exact SubD structure and enables exact limit surface evaluation via OpenSubdiv.

**Platform**: Grasshopper in Rhino 8 with Python 3 support

---

## Deliverables

**File to Create**: `rhino/grasshopper_http_server_control_cage.py`

---

## Requirements

### 1. HTTP Server Setup
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import Rhino.Geometry as rg

# Global to hold current geometry
current_geometry = None

class GeometryHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for SubD geometry."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/geometry':
            self.serve_geometry()
        elif self.path == '/status':
            self.serve_status()
        else:
            self.send_error(404, "Not found")

    def serve_geometry(self):
        """Serve SubD control cage as JSON."""
        global current_geometry

        if current_geometry is None:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'No geometry available'
            }).encode())
            return

        # Extract control cage
        cage_data = extract_control_cage(current_geometry)

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = json.dumps(cage_data, indent=2)
        self.wfile.write(response.encode())

    def serve_status(self):
        """Serve server status."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        status = {
            'status': 'running',
            'port': 8888,
            'has_geometry': current_geometry is not None
        }

        self.wfile.write(json.dumps(status).encode())

    def log_message(self, format, *args):
        """Override to suppress console spam."""
        pass  # Silent logging
```

### 2. Control Cage Extraction
```python
def extract_control_cage(subd):
    """
    Extract control cage data from Rhino SubD object.

    Args:
        subd: Rhino.Geometry.SubD object

    Returns:
        dict: {
            'vertices': [[x,y,z], ...],
            'faces': [[i,j,k,...], ...],
            'creases': [[edge_i, edge_j, sharpness], ...],
            'metadata': {...}
        }
    """
    if not isinstance(subd, rg.SubD):
        return {'error': 'Not a SubD object'}

    # Get control vertices
    vertices = []
    vertex_map = {}  # Map vertex ID to index

    for idx, vertex in enumerate(subd.Vertices):
        pt = vertex.ControlNetPoint
        vertices.append([pt.X, pt.Y, pt.Z])
        vertex_map[vertex.Id] = idx

    # Get control faces
    faces = []

    for face in subd.Faces:
        # Get vertex indices for this face
        face_verts = []
        for edge in face.Edges:
            # Get vertices of edge, add to face
            # [IMPLEMENT FACE VERTEX EXTRACTION]
            pass

        if face_verts:
            faces.append(face_verts)

    # Get creases (sharp edges)
    creases = []

    for edge in subd.Edges:
        if edge.Sharpness > 0:
            # Get edge vertex indices
            v1_idx = vertex_map.get(edge.StartVertex.Id)
            v2_idx = vertex_map.get(edge.EndVertex.Id)

            if v1_idx is not None and v2_idx is not None:
                creases.append([v1_idx, v2_idx, edge.Sharpness])

    # Gather metadata
    metadata = {
        'vertex_count': len(vertices),
        'face_count': len(faces),
        'edge_count': subd.Edges.Count,
        'crease_count': len(creases)
    }

    return {
        'vertices': vertices,
        'faces': faces,
        'creases': creases,
        'metadata': metadata
    }
```

### 3. Server Management
```python
server = None
server_thread = None

def start_server(geometry):
    """Start HTTP server with geometry."""
    global server, server_thread, current_geometry

    current_geometry = geometry

    if server is None:
        # Create server
        server = HTTPServer(('localhost', 8888), GeometryHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("✅ Server started on http://localhost:8888")
    else:
        print("🔄 Geometry updated")

def stop_server():
    """Stop HTTP server."""
    global server

    if server is not None:
        server.shutdown()
        server = None
        print("🛑 Server stopped")
```

### 4. Grasshopper Component Interface
```python
"""
Grasshopper Python Component
Inputs:
  - SubD: SubD geometry to serve
  - Run: Boolean to start/stop server
Outputs:
  - Status: Server status message
  - URL: Server URL
"""

import Rhino.Geometry as rg

# Component code here
if Run:
    if SubD is not None and isinstance(SubD, rg.SubD):
        start_server(SubD)
        Status = "✅ Server running"
        URL = "http://localhost:8888"
    else:
        Status = "❌ No SubD geometry provided"
        URL = ""
else:
    stop_server()
    Status = "🛑 Server stopped"
    URL = ""
```

---

## Testing

### Test 1: Manual Testing in Grasshopper

**Setup**:
1. Create SubD sphere in Rhino: `_SubDSphere`
2. Reference SubD in Grasshopper (Params → Geometry → SubD)
3. Add Python component with server code
4. Connect SubD to component input
5. Set Run = True

**Expected Output**:
- Console shows: "✅ Server started on http://localhost:8888"
- Status output shows: "✅ Server running"

### Test 2: HTTP Client Test

**Python client** (`test_gh_server.py`):
```python
#!/usr/bin/env python3
"""Test Grasshopper HTTP server."""

import requests
import json

def test_status():
    """Test /status endpoint."""
    print("Testing /status endpoint...")

    try:
        response = requests.get('http://localhost:8888/status', timeout=2)
        response.raise_for_status()

        data = response.json()
        print(f"  Status: {data['status']}")
        print(f"  Has geometry: {data['has_geometry']}")
        print("  ✅ Status endpoint working\n")
        return True

    except Exception as e:
        print(f"  ❌ Failed: {e}\n")
        return False

def test_geometry():
    """Test /geometry endpoint."""
    print("Testing /geometry endpoint...")

    try:
        response = requests.get('http://localhost:8888/geometry', timeout=2)
        response.raise_for_status()

        data = response.json()

        # Check structure
        assert 'vertices' in data, "Missing vertices"
        assert 'faces' in data, "Missing faces"
        assert 'metadata' in data, "Missing metadata"

        meta = data['metadata']
        print(f"  Vertices: {meta['vertex_count']}")
        print(f"  Faces: {meta['face_count']}")
        print(f"  Edges: {meta['edge_count']}")
        print(f"  Creases: {meta['crease_count']}")

        # Validate data
        assert len(data['vertices']) == meta['vertex_count']
        assert len(data['faces']) == meta['face_count']

        # Check vertex format
        if data['vertices']:
            v = data['vertices'][0]
            assert len(v) == 3, "Vertex should be [x,y,z]"
            assert all(isinstance(c, (int, float)) for c in v)

        # Check face format
        if data['faces']:
            f = data['faces'][0]
            assert all(isinstance(i, int) for i in f)
            assert all(0 <= i < meta['vertex_count'] for i in f)

        print("  ✅ Geometry endpoint working\n")
        return True

    except Exception as e:
        print(f"  ❌ Failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Testing Grasshopper HTTP Server")
    print("=" * 60)
    print()

    # Test both endpoints
    status_ok = test_status()
    geometry_ok = test_geometry()

    print("=" * 60)
    if status_ok and geometry_ok:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

if __name__ == '__main__':
    main()
```

**Run Test**:
```bash
# In Grasshopper: Start server with SubD sphere
# In terminal:
python3 test_gh_server.py
```

**Expected Output**:
```
Testing /status endpoint...
  Status: running
  Has geometry: True
  ✅ Status endpoint working

Testing /geometry endpoint...
  Vertices: 386
  Faces: 384
  Edges: 768
  Creases: 0
  ✅ Geometry endpoint working

✅ ALL TESTS PASSED
```

### Test 3: Browser Test

Open in browser:
- `http://localhost:8888/status` - Should show JSON status
- `http://localhost:8888/geometry` - Should show SubD control cage JSON

---

## Success Criteria

- [ ] Server starts successfully on port 8888
- [ ] `/status` endpoint returns server status
- [ ] `/geometry` endpoint returns control cage data
- [ ] Vertices extracted correctly (3D coordinates)
- [ ] Faces extracted correctly (vertex indices)
- [ ] Creases extracted if present
- [ ] JSON response is valid and well-formed
- [ ] No errors in Grasshopper console
- [ ] Client test script passes all tests

---

## Example Output

**GET /geometry response**:
```json
{
  "vertices": [
    [0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0],
    [1.0, 0.0, 0.0],
    ...
  ],
  "faces": [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    ...
  ],
  "creases": [
    [0, 1, 0.8],
    [2, 3, 1.0]
  ],
  "metadata": {
    "vertex_count": 386,
    "face_count": 384,
    "edge_count": 768,
    "crease_count": 0
  }
}
```

---

## Integration Notes

**Used by**:
- Agent 8 (Desktop Bridge) will fetch from this endpoint
- Desktop app polls this server for geometry updates

**File Placement**:
```
rhino/
├── grasshopper_http_server_control_cage.py  (You create) ← REPLACES grasshopper_server_control.py
└── test_gh_server.py                        (You create) ← HERE
```

**IMPORTANT**: After creating `grasshopper_http_server_control_cage.py`, the old `grasshopper_server_control.py` can be archived or deleted. The new file provides the correct lossless control cage transfer required by the v5.0 specification.

**Usage in Desktop App**:
```python
import requests

response = requests.get('http://localhost:8888/geometry')
data = response.json()

# Convert to SubDControlCage
cage = cpp_core.SubDControlCage()

for v in data['vertices']:
    cage.vertices.append(cpp_core.Point3D(v[0], v[1], v[2]))

cage.faces = data['faces']
cage.creases = [(c[0], c[1], c[2]) for c in data['creases']]
```

---

## Common Issues and Solutions

**Issue**: "Port 8888 already in use"
- **Fix**: Stop previous server instance in Grasshopper
- **Fix**: Check for other apps using port: `lsof -i :8888`

**Issue**: "SubD.Vertices returns None"
- **Fix**: Ensure input is actually a SubD object, not a mesh
- **Fix**: Check Rhino version supports SubD (Rhino 7+)

**Issue**: "Face extraction produces wrong topology"
- **Fix**: Verify winding order (CCW vs CW)
- **Fix**: Check for n-gon faces (>4 vertices)

**Issue**: "JSON encoding error"
- **Fix**: Ensure all coordinates are float, not Rhino Point3d objects
- **Fix**: Convert to plain Python lists before json.dumps

---

## Output Format

Provide:
1. Complete `grasshopper_http_server_control_cage.py`
2. Complete `test_gh_server.py` client test
3. Screenshot or text output of successful test
4. Sample JSON response from `/geometry` endpoint
5. Integration notes for desktop app

---

**Ready to begin!**
