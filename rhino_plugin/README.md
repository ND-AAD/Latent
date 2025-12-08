# Latent Rhino Plugin

Rhino 8 plugin for the Ceramic Mold Analyzer - discovers mathematical
decompositions of SubD surfaces for slip-casting molds.

## Requirements

- Rhino 8 (Windows or macOS)
- .NET Framework 4.8 or .NET 6+
- Python 3.8+ (for analysis service)

## Building

```bash
cd rhino_plugin
dotnet restore
dotnet build
```

## Testing

```bash
dotnet test
```

## Project Structure

```
rhino_plugin/
├── Analysis/           # LensClient, AnalysisResult, Protocol
│   ├── LensClient.cs
│   ├── AnalysisResult.cs
│   └── Protocol.cs
├── Commands/           # Rhino commands
│   ├── LatentAnalyzeCommand.cs
│   ├── LatentSelectCommand.cs
│   ├── LatentPinCommand.cs
│   └── LatentRevertCommand.cs
├── Display/            # RegionConduit, visualization
│   ├── RegionConduit.cs
│   ├── CurveSampler.cs
│   ├── CurveCache.cs
│   └── VisualizationSettings.cs
├── Geometry/           # Vertex, Edge, Region, RegionManager
│   ├── IGeometryElement.cs
│   ├── Vertex.cs
│   ├── Edge.cs
│   ├── Region.cs
│   └── RegionManager.cs
├── Interaction/        # GetPoint, drag handlers, pickers
│   ├── SurfaceConstrainedGetPoint.cs
│   ├── VertexDragHandler.cs
│   ├── EdgeDragHandler.cs
│   └── RegionPicker.cs
├── Interop/            # P/Invoke bindings to C++ core
│   ├── NativeCore.cs
│   ├── SubDEvaluator.cs
│   ├── SurfaceCurve.cs
│   └── ParametricPoint.cs
├── UI/                 # Eto.Forms panels
│   ├── GeometryListPanel.cs
│   ├── LensPanel.cs
│   └── VisualizationPanel.cs
├── Tests/              # Unit and integration tests
│   ├── TestHelpers.cs
│   ├── IntegrationTests.cs
│   ├── WorkflowTests.cs
│   └── ...
├── LatentPlugin.cs     # Plugin entry point
└── Latent.csproj
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Rhino 8       │     │  Analysis       │
│   (UI/Viewport) │────▶│  Service        │
└────────┬────────┘     │  (Python)       │
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Latent Plugin  │────▶│  C++ Core       │
│  (C#/.NET)      │     │  (liblatent)    │
└─────────────────┘     └─────────────────┘
```

## Commands

| Command | Description |
|---------|-------------|
| `LatentAnalyze` | Run lens analysis on selected SubD |
| `LatentSelect` | Select region/edge/vertex |
| `LatentPin` | Pin/unpin selected element |
| `LatentRevert` | Revert element to implicit state |

## Panels

| Panel | Description |
|-------|-------------|
| Latent Geometry | List of vertices, edges, regions with state management |
| Latent Lens | Lens selection and analysis parameters |
| Latent Display | Visualization settings (colors, fills, samples) |

## Key Classes

- **RegionManager**: Central state container for all geometry elements
- **SubDEvaluator**: Managed wrapper for native limit surface evaluation
- **ParametricPoint**: Coordinate type for positions on the limit surface
- **RegionConduit**: DisplayConduit for rendering boundaries and regions

## Documentation

- [User Guide](../docs/RHINO_PLUGIN_USER_GUIDE.md)
- [Architecture Design](../docs/plans/2025-12-04-rhino-plugin-architecture-design.md)
- [Implementation Plan](../docs/plans/2025-12-04-rhino-plugin-implementation-plan.md)

## License

Proprietary - All rights reserved
