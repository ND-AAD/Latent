# Latent - Rhino Plugin

Rhino 8 plugin for ceramic mold analysis - discovers mathematical decompositions of SubD surfaces.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RHINO 8                                  │
│                                                                  │
│  Latent Plugin (C#)                                              │
│  ├── Commands: LatentAnalyze, LatentEdit, LatentPin, LatentExport│
│  ├── EditMode: Constrained boundary manipulation                 │
│  ├── Display: Conduit for boundaries and region overlays        │
│  └── Communication: HTTP client to analysis engine              │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE                               │
│                                                                  │
│  server.py (Python HTTP wrapper)                                 │
│  ├── cpp_core.SubDEvaluator (OpenSubdiv)                        │
│  ├── DifferentialLens (curvature analysis)                       │
│  ├── SpectralLens (coming soon)                                  │
│  └── FlowLens (coming soon)                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Build the Plugin

```bash
cd rhino_plugin/Latent
dotnet build
```

### 2. Install in Rhino

Copy `Latent.rhp` to Rhino plugins folder:
- macOS: `~/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/`
- Windows: `%APPDATA%\McNeel\Rhinoceros\8.0\Plug-ins\`

Or drag-and-drop onto Rhino window.

### 3. Start Analysis Engine

```bash
# From project root
python server.py --port 5000
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `LatentAnalyze` | Run analysis on Form, generate boundaries |
| `LatentEdit` | Enter edit mode for boundary manipulation |
| `LatentPin` | Pin/unpin selected region or boundary |
| `LatentExport` | Generate mold geometry (coming soon) |

### Workflow

1. **Create Form in Rhino** - Model your SubD surface

2. **Run Analysis**
   ```
   > LatentAnalyze
   Select Form: [click SubD]
   Lens: Differential
   ```

3. **Edit Boundaries**
   ```
   > LatentEdit
   [click boundary to select]
   [drag to move - constrained to surface]
   [right-click for options]
   ESC to exit
   ```

4. **Pin Good Regions**
   - Select region/boundary
   - Use `Pin` option to preserve across re-analysis

5. **Iterate**
   - Run `LatentAnalyze` again with different lens
   - Pinned elements preserved

6. **Export**
   ```
   > LatentExport
   [generates mold geometry]
   ```

## Development

### Project Structure

```
Latent/
├── Latent.csproj           # Project file
├── LatentPlugin.cs         # Plugin entry point
├── Commands/
│   ├── LatentAnalyzeCommand.cs
│   ├── LatentEditCommand.cs
│   └── ...
├── EditMode/
│   └── BoundaryEditHandler.cs
├── Display/
│   └── LatentDisplayConduit.cs
├── State/
│   ├── LatentStateManager.cs
│   └── ParametricTypes.cs
└── Communication/
    └── AnalysisClient.cs
```

### Key Concepts

**Form**: The original SubD from Rhino. Immutable. Never modified.

**Boundaries**: The result of analysis - parting surfaces that divide the Form into mold pieces. These are what we edit.

**Parametric representation**: Boundaries are stored as `(face_id, u, v)` points, not 3D curves. The display curves are generated from these on demand.

**Constrained editing**: When user drags a boundary, mouse position is projected onto the Form surface. The boundary stays on the surface.
