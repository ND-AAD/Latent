# Grasshopper HTTP Server - Usage Guide

## Overview

This directory contains the Grasshopper HTTP server for control cage transfer. This is the **correct, lossless approach** for transferring SubD geometry from Rhino to the desktop application.

## Files

- **`grasshopper_http_server_control_cage.py`** - Main server component (use this in Grasshopper)
- **`test_gh_server.py`** - Test client to verify server is working
- **`grasshopper_server_control.py`** - OLD mesh-based transfer (deprecated, keep for reference)

## Quick Start

### Step 1: Setup in Grasshopper

1. Open Rhino 8 with Grasshopper
2. Create or reference a SubD object:
   - In Rhino: `_SubDSphere` or `_SubDBox`
   - In Grasshopper: Add **Params → Geometry → SubD** parameter
   - Right-click → "Set one SubD" and select your SubD object

3. Add Python component:
   - **Toolbox → Script → Python 3 Script**
   - Double-click to open editor

4. Copy/paste the code from `grasshopper_http_server_control_cage.py`

5. Set up inputs:
   - **Right-click component → Add input** (if needed)
   - Name: `SubD`, Type hint: `SubD`
   - Name: `Run`, Type hint: `bool`

6. Set up outputs:
   - **Right-click component → Add output** (if needed)
   - Name: `Status`
   - Name: `URL`

7. Connect:
   - Connect SubD parameter to `SubD` input
   - Add a **Boolean Toggle** and connect to `Run` input
   - Add **Panels** to `Status` and `URL` outputs to see results

8. Start server:
   - Set Boolean Toggle to **True**
   - Check Status panel shows: "✅ Server running"
   - Check URL panel shows: "http://localhost:8888"

### Step 2: Test the Server

In a terminal:

```bash
cd /home/user/Latent
python3 rhino/test_gh_server.py
```

Expected output:
```
============================================================
Testing Grasshopper HTTP Server - Control Cage Transfer
============================================================

Testing /status endpoint...
  Status: running
  Port: 8888
  Has geometry: True
  ✅ Status endpoint working

Testing /geometry endpoint...
  Vertices: 386
  Faces: 384
  Edges: 768
  Creases: 0
  Sample vertex: [0.000, 0.000, 1.000]
  Sample face: [0, 1, 2, 3] (4 vertices)
  No creases (smooth SubD)
  ✅ Geometry endpoint working

Testing data integrity...
  ✅ Data integrity validated

Sample JSON output:
{
  "vertices": [
    [0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0],
    [1.0, 0.0, 0.0]
  ],
  "faces": [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [8, 9, 10, 11]
  ],
  "creases": [],
  "metadata": {
    "vertex_count": 386,
    "face_count": 384,
    "edge_count": 768,
    "crease_count": 0
  }
}

============================================================
✅ ALL TESTS PASSED
============================================================
```

### Step 3: Test in Browser

Open these URLs in a web browser:

- **Status**: http://localhost:8888/status
- **Geometry**: http://localhost:8888/geometry

You should see JSON responses.

## API Endpoints

### GET /status

Returns server status.

**Response**:
```json
{
  "status": "running",
  "port": 8888,
  "has_geometry": true
}
```

### GET /geometry

Returns SubD control cage data.

**Response**:
```json
{
  "vertices": [
    [x, y, z],
    ...
  ],
  "faces": [
    [v0, v1, v2, ...],
    ...
  ],
  "creases": [
    [v_start, v_end, sharpness],
    ...
  ],
  "metadata": {
    "vertex_count": 386,
    "face_count": 384,
    "edge_count": 768,
    "crease_count": 0
  }
}
```

**Fields**:
- **vertices**: List of 3D points [x, y, z] (control cage vertices)
- **faces**: List of vertex index lists (face topology, n-gons supported)
- **creases**: List of [start_idx, end_idx, sharpness] for sharp edges
- **metadata**: Summary statistics

## Integration with Desktop App

The desktop app will fetch geometry like this:

```python
import requests
import cpp_core

# Fetch from Grasshopper
response = requests.get('http://localhost:8888/geometry')
data = response.json()

# Convert to C++ SubDControlCage
cage = cpp_core.SubDControlCage()

for v in data['vertices']:
    cage.vertices.append(cpp_core.Point3D(v[0], v[1], v[2]))

cage.faces = data['faces']
cage.creases = [(c[0], c[1], c[2]) for c in data['creases']]

# Build OpenSubdiv refiner
refiner = cpp_core.SubDEvaluator(cage)

# Evaluate limit surface at any (u, v)
point = refiner.evaluate_limit(face_id=0, u=0.5, v=0.5)
```

## Troubleshooting

### "Port 8888 already in use"

**Solution**:
1. Stop previous Grasshopper server (set Run = False)
2. Check for other apps: `lsof -i :8888`
3. Kill process if needed: `kill -9 <PID>`

### "No geometry available"

**Solution**:
1. Verify SubD is connected to component input
2. Check SubD is valid (not null/empty)
3. Verify component has both inputs defined

### "Not a SubD object"

**Solution**:
1. Ensure input is SubD, not Mesh or Brep
2. In Grasshopper, use **Params → Geometry → SubD** (not Surface/Mesh)
3. Set type hint on input to `SubD`

### Test client fails to connect

**Solution**:
1. Verify Grasshopper server is running (Run = True)
2. Check firewall isn't blocking port 8888
3. Try in browser: http://localhost:8888/status
4. Verify no other service using port 8888

### Face topology looks wrong

**Solution**:
1. Check SubD is valid in Rhino
2. Verify no naked edges or holes
3. Check vertex ordering is consistent

## Key Differences from Old Server

### ❌ OLD: grasshopper_server_control.py (DEPRECATED)
- Converts SubD → Mesh (approximation, lossy)
- Transfers triangle mesh
- Loses exact control cage topology
- Cannot evaluate exact limit surface

### ✅ NEW: grasshopper_http_server_control_cage.py (CORRECT)
- Extracts control cage directly (exact, lossless)
- Preserves SubD topology
- Enables exact limit surface evaluation via OpenSubdiv
- Aligns with v5.0 specification

## Why Control Cage Transfer Matters

The **lossless until fabrication** principle requires that we maintain exact mathematical representation throughout the pipeline:

```
Rhino SubD (exact)
  → Control Cage Transfer (exact) ✅
  → OpenSubdiv Evaluation (exact)
  → NURBS Generation (exact)
  → G-code Export (single approximation)
```

**Mesh transfer would break this**:
```
Rhino SubD (exact)
  → Mesh Approximation (FIRST APPROXIMATION - WRONG!) ❌
  → Further processing on approximate data
  → Accumulated errors
```

## Data Format Details

### Vertices
- Plain 3D coordinates as nested lists
- Example: `[[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], ...]`
- These are the **control vertices**, not limit surface points

### Faces
- Vertex index lists (0-indexed)
- Supports n-gons (quads, pentagons, etc.)
- Example: `[[0, 1, 2, 3], [4, 5, 6, 7, 8], ...]`
- Vertex order follows Rhino's edge traversal

### Creases
- Edge sharpness values
- Format: `[start_vertex_index, end_vertex_index, sharpness]`
- Sharpness: 0.0 (smooth) to 1.0 (hard crease)
- Example: `[[0, 1, 0.8], [5, 6, 1.0]]`

## Next Steps

After verifying the server works:

1. **Desktop Bridge** (Agent 8) will implement polling this endpoint
2. **C++ Integration** (Agents 1-3) provides `SubDControlCage` class
3. **OpenSubdiv** (Agent 4) evaluates exact limit surface

## References

- **Task file**: `docs/reference/api_sprint/agent_tasks/day_01/AGENT_06_grasshopper_server.md`
- **v5.0 Spec**: `docs/reference/subdivision_surface_ceramic_mold_generation_v5.md`
- **Tech Guide**: `docs/reference/technical_implementation_guide_v5.md`
