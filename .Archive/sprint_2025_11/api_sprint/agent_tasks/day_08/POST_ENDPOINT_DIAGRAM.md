# POST /molds Endpoint - Data Flow Diagram

## Complete Round-Trip Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         COMPLETE WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────┘

    Rhino/Grasshopper                Desktop App               Grasshopper
    ─────────────────                ───────────               ───────────

         ┌──────┐
         │ SubD │
         └──┬───┘
            │
            │ GET /geometry
    ┌───────▼────────┐
    │ HTTP Server    │
    │ Control Cage   │──────────────────────────────────┐
    │ Extraction     │                                   │
    └────────────────┘                                   │
                                                         │
                                        ┌────────────────▼──────────────┐
                                        │  Desktop App                  │
                                        │  - Receive control cage       │
                                        │  - Build OpenSubdiv surface   │
                                        │  - Run mathematical analysis  │
                                        │  - Discover parametric regions│
                                        │  - Generate NURBS molds       │
                                        └────────────────┬──────────────┘
                                                         │
                                                         │ Serialize molds
                                                         │
                                        ┌────────────────▼──────────────┐
                                        │  JSON Payload                 │
                                        │  {                            │
                                        │    "type": "ceramic_mold_set",│
                                        │    "molds": [...]             │
                                        │  }                            │
                                        └────────────────┬──────────────┘
                                                         │
                                                         │ POST /molds
    ┌────────────────┐                                   │
    │ HTTP Server    │◄──────────────────────────────────┘
    │ POST Endpoint  │
    └───────┬────────┘
            │
            │ Parse JSON
            │
    ┌───────▼────────┐
    │ For each mold  │
    │ ┌────────────┐ │
    │ │ Create     │ │
    │ │ NURBS      │ │
    │ │ Surface    │ │
    │ └────────────┘ │
    └───────┬────────┘
            │
    ┌───────▼────────┐
    │ Add to Rhino   │
    │ Document       │
    └───────┬────────┘
            │
         ┌──▼───┐
         │ Molds│
         │in Doc│
         └──────┘
```

## POST /molds Detailed Flow

```
                    Desktop App                    Grasshopper Server
                    ───────────                    ──────────────────

                   ┌──────────┐
                   │  Mold    │
                   │  Data    │
                   └────┬─────┘
                        │
                        │ HTTP POST
                        │ Content-Type: application/json
                        │
        ┌───────────────▼───────────────┐
        │ GeometryHandler.do_POST()     │
        │ ─────────────────────────     │
        │ if path == '/molds':          │
        │    _handle_mold_import()      │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │ _handle_mold_import()         │
        │ ────────────────────          │
        │ 1. Read POST body             │
        │ 2. Parse JSON                 │
        │ 3. Validate type              │
        │ 4. For each mold:             │
        │    _import_nurbs_surface()    │
        │ 5. Collect GUIDs              │
        │ 6. Send response              │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │ _import_nurbs_surface(mold)   │
        │ ──────────────────────────    │
        │ 1. Extract parameters         │
        │    - degree_u, degree_v       │
        │    - count_u, count_v         │
        │    - control_points           │
        │    - weights                  │
        │    - knots_u, knots_v         │
        │                               │
        │ 2. Create NurbsSurface        │
        │    order_u = degree_u + 1     │
        │    order_v = degree_v + 1     │
        │                               │
        │ 3. Set control points         │
        │    SetPoint(i, j, x, y, z, w) │
        │                               │
        │ 4. Set knot vectors           │
        │    KnotsU[i] = knot           │
        │    KnotsV[i] = knot           │
        │                               │
        │ 5. Add to document            │
        │    guid = rs.AddSurface()     │
        │                               │
        │ 6. Set name                   │
        │    rs.ObjectName(guid, name)  │
        │                               │
        │ 7. Return GUID                │
        └───────────────┬───────────────┘
                        │
                        │ GUID
                        │
        ┌───────────────▼───────────────┐
        │ Response JSON                 │
        │ ────────────                  │
        │ {                             │
        │   "status": "success",        │
        │   "imported_count": 2,        │
        │   "guids": ["...", "..."]     │
        │ }                             │
        └───────────────┬───────────────┘
                        │
                        │ HTTP 200 OK
                        │
                   ┌────▼─────┐
                   │ Desktop  │
                   │   App    │
                   └──────────┘
```

## NURBS Surface Construction Detail

```
Input:
  degree_u = 3
  degree_v = 3
  count_u = 4
  count_v = 4
  control_points = [
    [0,0,0], [1,0,0], [2,0,0], [3,0,0],  ← Row 0 (U=0)
    [0,1,0], [1,1,1], [2,1,1], [3,1,0],  ← Row 1 (U=1)
    [0,2,0], [1,2,1], [2,2,1], [3,2,0],  ← Row 2 (U=2)
    [0,3,0], [1,3,0], [2,3,0], [3,3,0]   ← Row 3 (U=3)
  ]
  weights = [1.0, 1.0, ..., 1.0]  (16 values)
  knots_u = [0,0,0,0, 1,1,1,1]    (count_u + degree_u + 1 = 8)
  knots_v = [0,0,0,0, 1,1,1,1]    (count_v + degree_v + 1 = 8)

Step 1: Create surface
  surface = rg.NurbsSurface.Create(
    dimension=3,
    isRational=True,
    orderU=4,          ← degree_u + 1
    orderV=4,          ← degree_v + 1
    controlPointCountU=4,
    controlPointCountV=4
  )

Step 2: Set control points (row-major order)
  idx = 0
  for i in range(4):      ← U direction
    for j in range(4):    ← V direction
      x, y, z = control_points[idx]
      w = weights[idx]
      surface.Points.SetPoint(i, j, x, y, z, w)
      idx += 1

  Control point grid:
            V=0      V=1      V=2      V=3
  U=0:   pt[0,0]  pt[0,1]  pt[0,2]  pt[0,3]
  U=1:   pt[1,0]  pt[1,1]  pt[1,2]  pt[1,3]
  U=2:   pt[2,0]  pt[2,1]  pt[2,2]  pt[2,3]
  U=3:   pt[3,0]  pt[3,1]  pt[3,2]  pt[3,3]

Step 3: Set knot vectors
  for i in range(8):
    surface.KnotsU[i] = knots_u[i]
    surface.KnotsV[i] = knots_v[i]

Step 4: Add to document
  guid = rs.AddSurface(surface)
  rs.ObjectName(guid, "mold_1")

Result: NURBS surface in Rhino document
```

## Error Handling Flow

```
┌─────────────────┐
│ POST /molds     │
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │ Read body  │
    └─────┬──────┘
          │
          ▼
     ┌─────────────┐      ┌──────────────┐
     │ Parse JSON  │─────►│ JSON Error   │─────► 500 Error
     └─────┬───────┘  ❌  └──────────────┘
           │ ✅
           ▼
     ┌─────────────┐      ┌──────────────┐
     │ Validate    │─────►│ Wrong type   │─────► 400 Error
     │ type field  │  ❌  └──────────────┘
     └─────┬───────┘
           │ ✅
           ▼
     ┌─────────────┐
     │ For each    │
     │ mold:       │
     └─────┬───────┘
           │
           ▼
     ┌─────────────┐      ┌──────────────┐
     │ Create      │─────►│ NURBS Error  │─────► Skip mold
     │ NURBS       │  ❌  │ Log error    │       Continue
     └─────┬───────┘      └──────────────┘
           │ ✅
           ▼
     ┌─────────────┐
     │ Add to doc  │
     └─────┬───────┘
           │
           ▼
     ┌─────────────┐
     │ Return      │
     │ success     │
     └─────────────┘
```

## Integration Points

### Agent 52 → Agent 53
- Agent 52 serializes molds to JSON format
- Agent 53 receives and imports JSON
- Format contract: grasshopper_mold_import_api.md

### Agent 53 → Agent 54
- Agent 53 provides POST endpoint
- Agent 54 implements client to send data
- Communication: HTTP POST with JSON payload

### Desktop App → Grasshopper
- Desktop serializes NURBS molds
- POST to http://localhost:8888/molds
- Receive GUIDs of imported surfaces
- User can see molds in Rhino
