# Manual Push Workflow - Setup Guide

## What Changed

We've **dramatically simplified** the geometry workflow:
- ❌ **REMOVED**: Automatic polling (caused infinite update loop)
- ❌ **REMOVED**: Hash-based change detection (caused spam)
- ✅ **ADDED**: Manual button-click push from Grasshopper
- ✅ **ADDED**: HTTP server in desktop app to receive geometry
- ✅ **FIXED**: Mouse controls (renderer initialization)
- ✅ **FIXED**: Right-click conflict (disabled Qt context menu)

## How It Works Now

**Grasshopper → Desktop App (One-Way Push)**

```
1. You edit SubD in Rhino
2. You click BUTTON in Grasshopper
3. Grasshopper converts SubD → Mesh
4. Grasshopper POSTs to desktop app (port 5000)
5. Desktop app displays geometry
6. DONE - no polling, no updates, no spam
```

## Setup Instructions

### Step 1: Grasshopper Component

1. Create a **GhPython component** in Grasshopper
2. **Copy the ENTIRE contents** of:
   ```
   rhino/grasshopper_manual_push.py
   ```
3. Paste into the GhPython component

4. **Set inputs**:
   - **`subd`** (required): Connect your SubD geometry
   - **`push_button`** (required): Add a **BUTTON** component (NOT a toggle!)

5. **Component should show**:
   ```
   ⏸️ Ready to send
   SubD: 26V, 24F
   Click button to push
   ```

### Step 2: Desktop Application

1. **Start the app**:
   ```bash
   cd ceramic_mold_analyzer
   python3 launch.py
   ```

2. **Check console output** - should see:
   ```
   ✅ Geometry receiver listening on port 5000
   🎨 Ceramic Mold Analyzer initialized
   📍 Controls: LEFT=Select | RIGHT or MIDDLE=Rotate | Shift+RIGHT=Pan | Wheel=Zoom
   📡 Listening for geometry on port 5000 (manual push mode)
   ```

3. **Connect to Grasshopper** (optional - just for status check):
   - Click: **File → Connect to Rhino**
   - Should see "● Connected" in bottom-right

### Step 3: Push Geometry

1. **In Grasshopper**: Click the BUTTON
2. **Grasshopper console should show**:
   ```
   📤 Sending geometry to desktop app...
   ✅ Sent: 216V, 96F
   ```

3. **Desktop app console should show**:
   ```
   📥 Geometry pushed from Grasshopper
   📥 Received geometry: 216 vertices, 96 faces
   ```

4. **Viewport should display** your SubD as a mesh

## Testing Mouse Controls

Once geometry is loaded:

### ✅ Expected to Work:
- **RIGHT drag**: Orbit/rotate camera
- **MIDDLE drag**: Orbit/rotate camera (alternative)
- **Shift + RIGHT drag**: Pan camera
- **Mouse wheel**: Zoom in/out
- **Keyboard shortcuts**:
  - `W`: Wireframe mode
  - `S`: Shaded mode
  - `F`: Frame/zoom to fit

### ❌ Not Yet Working:
- **LEFT click**: Selection (requires Edit Mode to be active)
  - Click toolbar button for Panel/Edge/Vertex mode first
  - Then left-click should work

## Troubleshooting

### "Desktop app not running or not listening on port 5000"

**Problem**: Desktop app not started, or port 5000 blocked

**Fix**:
1. Make sure `python3 launch.py` is running
2. Check console shows "Geometry receiver listening on port 5000"
3. Check no other app is using port 5000:
   ```bash
   lsof -i :5000
   ```

### "Port 8888 already in use"

**Problem**: Old Grasshopper server still running

**Fix**:
1. Disable any other GhPython components with HTTP servers
2. Restart Rhino if needed
3. Or change PORT in grasshopper_manual_push.py to 8889

### "No geometry appears in viewport"

**Problem**: Geometry sent but not displayed

**Fix**:
1. Check desktop console for "Received geometry" message
2. Try View → Show Test Cube to verify VTK works
3. Try clicking different viewport layout buttons
4. Check mesh has valid data (not empty)

### "Mouse controls still don't work"

**Problem**: Renderer not properly initialized

**Fix**: This should be fixed now, but if still broken:
1. Close and restart the app
2. Check console for any VTK errors
3. Try clicking on the viewport to give it focus
4. Report exact behavior - what DOES work?

## What to Expect

✅ **Working Now**:
- Manual push workflow
- Geometry display (as mesh approximation)
- Mouse camera controls (orbit, pan, zoom)
- Multi-viewport layouts
- Edit mode toolbar (UI only)

❌ **Not Working Yet**:
- Element selection (needs Edit Mode active)
- Mathematical analysis (no lenses implemented)
- Region discovery (no analysis yet)
- Exact SubD limit surface (using mesh for now)
- Constraint validation (UI shell only)

## Next Steps

Once this workflow is stable:

1. **Week 5**: Implement first mathematical lens (Differential/Curvature)
2. **Week 6**: Add OpenSubdiv for exact limit surface evaluation
3. **Week 7**: Implement region editing and boundary curves
4. **Week 8**: Add constraint validation

## Files Modified

### New Files:
- `rhino/grasshopper_manual_push.py` - Manual push server
- `app/bridge/geometry_receiver.py` - Desktop HTTP receiver
- `MANUAL_PUSH_SETUP.md` - This guide

### Modified Files:
- `app/bridge/rhino_bridge.py` - Removed polling, added receive_geometry()
- `app/ui/viewport_3d.py` - Fixed renderer init, disabled context menu
- `main.py` - Added geometry receiver, connected signals

## Architecture

```
┌─────────────────────────────────────┐
│  RHINO/GRASSHOPPER                  │
│  Port 8888                          │
│                                     │
│  GET /status → {"status": "ok"}    │
│  (No /subd or /check_update)       │
└─────────────────────────────────────┘
              │
              │ (Button click)
              ↓
         HTTP POST
    /receive_geometry
              │
              ↓
┌─────────────────────────────────────┐
│  DESKTOP APP                        │
│  Port 5000 (GeometryReceiver)      │
│                                     │
│  POST /receive_geometry             │
│  → Receives mesh data               │
│  → Displays in viewports            │
│  → NO automatic updates             │
└─────────────────────────────────────┘
```

**Key Point**: Completely one-way, manual workflow. Desktop app is PASSIVE - just waits for pushes. No polling, no checking, no auto-updates.

---

**Questions? Issues?** Check console output on both sides and compare to expected messages above.
