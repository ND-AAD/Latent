# Rhino HTTP Bridge Setup Guide

## Overview

The Rhino HTTP Bridge enables **EXACT SubD transfer** between Rhino and the Ceramic Mold Analyzer desktop application. This maintains the **"Lossless Until Fabrication"** principle - your SubD geometry is transferred with perfect mathematical fidelity, not converted to mesh.

## Key Features

- ✅ **Exact SubD Representation** - No mesh conversion
- ✅ **Live Updates** - Changes in Rhino appear instantly in the app
- ✅ **Bidirectional** - Send molds back to Rhino
- ✅ **Automatic Polling** - Detects geometry changes
- ✅ **HTTP Protocol** - Simple, reliable connection

## Setup Instructions

### Step 1: Prepare Your SubD Model in Rhino

1. Open Rhino 8 or later
2. Create or load your SubD surface
3. Ensure it's a valid SubD (use `SubDDisplayToggle` to verify)

### Step 2: Setup Grasshopper Component

1. Open Grasshopper in Rhino
2. Create a new **GhPython** component:
   - Double-click canvas → type "Python" → select GhPython Script

3. Configure the component inputs:
   - Right-click the component → Manage Inputs/Outputs
   - Add one input named `subd`
   - Set Type Hint to `SubD` (scroll down in the list)
   - Set Access to `Item Access`

4. Configure the output:
   - Add one output named `status`
   - Type can remain as generic

### Step 3: Load the Server Script

1. Double-click the GhPython component to open the editor

2. Copy the entire contents of:
   ```
   ceramic_mold_analyzer/rhino/grasshopper_http_server.py
   ```

3. Paste into the Python editor

4. Click "OK" to close the editor

### Step 4: Connect Your SubD

1. Connect your SubD surface to the `subd` input of the Python component
   - Use a SubD parameter or direct reference from Rhino
   - The component should show "✅ Server running on http://localhost:8888"

2. Check the output - it should display:
   ```
   ✅ Server running on http://localhost:8888
   📦 SubD ready: [N] vertices
   🔄 Exact transfer mode (lossless)
   ```

### Step 5: Connect from Desktop App

1. Launch the Ceramic Mold Analyzer:
   ```bash
   cd ceramic_mold_analyzer
   python3 launch.py
   ```

2. Click **File → Connect to Rhino** in the app

3. If successful, you'll see:
   - Status bar: "Connected to Rhino"
   - Connection indicator: Green dot "● Connected"
   - Your SubD appears in all viewports

## Troubleshooting

### "Could not connect to Rhino HTTP server"

**Cause**: Server not running in Grasshopper

**Solution**:
- Verify the Python component shows "Server running"
- Check that port 8888 is not blocked by firewall
- Ensure you're using `grasshopper_http_server.py` (not the old version)

### SubD not appearing in app

**Cause**: No SubD connected to input

**Solution**:
- Verify SubD is connected to the `subd` input
- Check that it's a valid SubD (not a mesh or Brep)
- Try reconnecting the wire in Grasshopper

### "Failed to serialize SubD"

**Cause**: Invalid SubD geometry

**Solution**:
- Run `SubDRepair` on your geometry
- Ensure SubD has no naked edges
- Try simplifying complex SubDs

### Server stops when switching Rhino files

**Cause**: Grasshopper components reset on file change

**Solution**:
- Simply reconnect your SubD to restart the server
- The desktop app will automatically reconnect

## How It Works

### The Lossless Pipeline

```
Rhino SubD (Exact Geometry)
    ↓
Grasshopper (grasshopper_http_server.py)
    ↓
Serialization to 3dm format (NO MESH CONVERSION)
    ↓
Base64 encoding for transport
    ↓
HTTP Transfer (port 8888)
    ↓
Desktop App (rhino_bridge.py)
    ↓
rhino3dm deserialization
    ↓
Exact SubD in Application
```

### What Gets Transferred

- **Control vertices** - Exact positions
- **Face topology** - Connectivity information
- **Edge creases** - Sharp edge data
- **Vertex tags** - Corner/smooth information
- **Subdivision level** - Display quality settings

### What Does NOT Happen

- ❌ NO conversion to mesh
- ❌ NO approximation
- ❌ NO loss of precision
- ❌ NO tessellation until final export

## Advanced Usage

### Multiple SubD Objects

To handle multiple SubDs:
1. Create multiple GhPython components
2. Run servers on different ports (8888, 8889, etc.)
3. Connect to each from the app

### Custom Port Configuration

Edit line 30 in `grasshopper_http_server.py`:
```python
PORT = 8888  # Change to your desired port
```

And update the connection in the desktop app:
```python
bridge = RhinoBridge(port=8888)  # Match your port
```

### Debugging

Enable debug output in Grasshopper:
1. Add a Panel component
2. Connect it to the `status` output
3. Watch for error messages

## Performance Notes

- **Update Rate**: Checks for changes every second
- **Transfer Size**: ~100KB for typical SubD (1000 vertices)
- **Latency**: <100ms on local connection
- **Memory**: Minimal - uses streaming

## Security Note

The server runs on `localhost` only - not accessible from other machines. For network access, modify the `HOST` variable (not recommended for production).

## Next Steps

Once connected, you can:
1. Apply mathematical decomposition lenses
2. Pin/unpin regions
3. Adjust boundaries
4. Generate molds
5. Send molds back to Rhino

The connection maintains throughout your session - geometry updates automatically as you modify it in Rhino!