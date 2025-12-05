# Agent 3C: Plugin Entry Point & Commands

## Objective

Create the Rhino plugin infrastructure with entry point and basic commands.

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `rhino_plugin/LatentPlugin.csproj` - project configuration
- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - plugin structure

## Files to Create

1. `rhino_plugin/LatentPlugin.cs` - Plugin entry point
2. `rhino_plugin/Commands/LatentAnalyzeCommand.cs` - Main analysis command
3. `rhino_plugin/Commands/LatentSelectCommand.cs` - Selection command
4. `rhino_plugin/Commands/LatentPinCommand.cs` - Pin/unpin command
5. `rhino_plugin/Commands/LatentRevertCommand.cs` - Revert command

## Tasks

### 1. Create LatentPlugin.cs

```csharp
// rhino_plugin/LatentPlugin.cs
using System;
using Rhino;
using Rhino.PlugIns;
using Latent.Analysis;
using Latent.Geometry;
using Latent.Interop;

namespace Latent
{
    /// <summary>
    /// Main plugin class for Latent - Ceramic Mold Analyzer.
    /// </summary>
    public class LatentPlugin : PlugIn
    {
        /// <summary>
        /// Singleton instance of the plugin.
        /// </summary>
        public static LatentPlugin Instance { get; private set; }

        /// <summary>
        /// The active SubD being analyzed.
        /// </summary>
        public Rhino.Geometry.SubD ActiveSubD { get; set; }

        /// <summary>
        /// The SubD evaluator for the active geometry.
        /// </summary>
        public SubDEvaluator Evaluator { get; private set; }

        /// <summary>
        /// Region manager for current analysis session.
        /// </summary>
        public RegionManager RegionManager { get; private set; }

        /// <summary>
        /// Client for the analysis service.
        /// </summary>
        public LensClient LensClient { get; private set; }

        /// <summary>
        /// Service manager for Python subprocess.
        /// </summary>
        public ServiceManager ServiceManager { get; private set; }

        public LatentPlugin()
        {
            Instance = this;
        }

        protected override LoadReturnCode OnLoad(ref string errorMessage)
        {
            try
            {
                // Initialize components
                RegionManager = new RegionManager();
                ServiceManager = new ServiceManager();
                LensClient = new LensClient(serviceManager: ServiceManager);

                RhinoApp.WriteLine("Latent Plugin loaded successfully.");
                return LoadReturnCode.Success;
            }
            catch (Exception ex)
            {
                errorMessage = $"Failed to load Latent plugin: {ex.Message}";
                return LoadReturnCode.ErrorShowDialog;
            }
        }

        protected override void OnShutdown()
        {
            // Clean up resources
            Evaluator?.Dispose();
            LensClient?.Dispose();
            ServiceManager?.Dispose();

            base.OnShutdown();
        }

        /// <summary>
        /// Initialize with a new SubD for analysis.
        /// </summary>
        public void InitializeWithSubD(Rhino.Geometry.SubD subd)
        {
            // Clean up previous session
            Evaluator?.Dispose();
            RegionManager.Clear();

            // Set up new session
            ActiveSubD = subd;
            Evaluator = new SubDEvaluator();
            Evaluator.Initialize(subd);

            RhinoApp.WriteLine($"Initialized with SubD: {Evaluator.FaceCount} faces");
        }

        /// <summary>
        /// Check if the plugin is ready for analysis.
        /// </summary>
        public bool IsReady => Evaluator != null && Evaluator.IsInitialized;
    }
}
```

### 2. Create LatentAnalyzeCommand.cs

```csharp
// rhino_plugin/Commands/LatentAnalyzeCommand.cs
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Rhino;
using Rhino.Commands;
using Rhino.Input;
using Rhino.Input.Custom;

namespace Latent.Commands
{
    /// <summary>
    /// Command to run lens analysis on a SubD.
    /// </summary>
    [CommandStyle(Style.ScriptRunner)]
    public class LatentAnalyzeCommand : Command
    {
        public override string EnglishName => "LatentAnalyze";

        protected override Result RunCommand(RhinoDoc doc, RunMode mode)
        {
            // Get or select SubD
            if (!GetSubD(doc, out var subdRef))
            {
                return Result.Cancel;
            }

            var subd = subdRef.SubD();
            if (subd == null)
            {
                RhinoApp.WriteLine("Selected object is not a SubD.");
                return Result.Failure;
            }

            // Get lens type
            var lensType = GetLensType();
            if (string.IsNullOrEmpty(lensType))
            {
                return Result.Cancel;
            }

            // Get parameters based on lens type
            var parameters = GetLensParameters(lensType);

            // Run analysis asynchronously
            var task = RunAnalysisAsync(subd, lensType, parameters);

            // Wait for completion (blocking for now)
            try
            {
                task.GetAwaiter().GetResult();
                doc.Views.Redraw();
                RhinoApp.WriteLine("Analysis complete.");
                return Result.Success;
            }
            catch (Exception ex)
            {
                RhinoApp.WriteLine($"Analysis failed: {ex.Message}");
                return Result.Failure;
            }
        }

        private bool GetSubD(RhinoDoc doc, out Rhino.DocObjects.ObjRef subdRef)
        {
            subdRef = null;

            // Check if we already have an active SubD
            if (LatentPlugin.Instance.ActiveSubD != null)
            {
                var result = RhinoGet.GetOneObject(
                    "Select SubD to analyze (Enter to use current)",
                    true,
                    Rhino.DocObjects.ObjectType.SubD,
                    out subdRef
                );

                if (result == Result.Nothing)
                {
                    // User pressed Enter - use existing
                    return true;
                }
                return result == Result.Success;
            }

            // No active SubD - must select one
            var getResult = RhinoGet.GetOneObject(
                "Select SubD to analyze",
                false,
                Rhino.DocObjects.ObjectType.SubD,
                out subdRef
            );

            return getResult == Result.Success;
        }

        private string GetLensType()
        {
            var go = new GetOption();
            go.SetCommandPrompt("Select lens type");
            go.AddOption("Differential");
            go.AddOption("Spectral");
            go.AddOption("CageAligned");

            var result = go.Get();
            if (result != GetResult.Option)
            {
                return null;
            }

            return go.Option().EnglishName.ToLower();
        }

        private Dictionary<string, object> GetLensParameters(string lensType)
        {
            var parameters = new Dictionary<string, object>();

            if (lensType == "differential")
            {
                var gn = new GetNumber();
                gn.SetCommandPrompt("Curvature tolerance");
                gn.SetDefaultNumber(0.3);
                gn.SetLowerLimit(0.01, false);
                gn.SetUpperLimit(1.0, false);

                if (gn.Get() == GetResult.Number)
                {
                    parameters["curvature_tolerance"] = gn.Number();
                }
            }
            else if (lensType == "spectral")
            {
                var gi = new GetInteger();
                gi.SetCommandPrompt("Number of eigenfunctions");
                gi.SetDefaultInteger(3);
                gi.SetLowerLimit(1, false);
                gi.SetUpperLimit(10, false);

                if (gi.Get() == GetResult.Number)
                {
                    parameters["num_eigenfunctions"] = gi.Number();
                }
            }

            return parameters;
        }

        private async Task RunAnalysisAsync(
            Rhino.Geometry.SubD subd,
            string lensType,
            Dictionary<string, object> parameters)
        {
            var plugin = LatentPlugin.Instance;

            // Initialize with SubD if changed
            if (plugin.ActiveSubD != subd)
            {
                plugin.InitializeWithSubD(subd);
            }

            // Ensure analysis service is running
            await plugin.LensClient.StartServiceAsync();

            // Initialize the service with geometry
            await plugin.LensClient.InitializeAsync(subd);

            // Run analysis
            var result = await plugin.LensClient.AnalyzeAsync(lensType, parameters);

            // Update region manager with results
            plugin.RegionManager.UpdateFromAnalysis(result);

            RhinoApp.WriteLine($"Found {result.Regions.Count} regions");
        }
    }
}
```

### 3. Create LatentSelectCommand.cs

```csharp
// rhino_plugin/Commands/LatentSelectCommand.cs
using Rhino;
using Rhino.Commands;
using Rhino.Input.Custom;

namespace Latent.Commands
{
    /// <summary>
    /// Command to select regions, edges, or vertices.
    /// </summary>
    [CommandStyle(Style.ScriptRunner)]
    public class LatentSelectCommand : Command
    {
        public override string EnglishName => "LatentSelect";

        protected override Result RunCommand(RhinoDoc doc, RunMode mode)
        {
            var plugin = LatentPlugin.Instance;

            if (!plugin.IsReady)
            {
                RhinoApp.WriteLine("No analysis active. Run LatentAnalyze first.");
                return Result.Cancel;
            }

            // Get selection mode
            var go = new GetOption();
            go.SetCommandPrompt("Select mode");
            go.AddOption("Region");
            go.AddOption("Edge");
            go.AddOption("Vertex");

            var result = go.Get();
            if (result != GetResult.Option)
            {
                return Result.Cancel;
            }

            var modeName = go.Option().EnglishName;

            switch (modeName)
            {
                case "Region":
                    return SelectRegion(doc, plugin);
                case "Edge":
                    return SelectEdge(doc, plugin);
                case "Vertex":
                    return SelectVertex(doc, plugin);
                default:
                    return Result.Cancel;
            }
        }

        private Result SelectRegion(RhinoDoc doc, LatentPlugin plugin)
        {
            // Pick a point on the SubD surface
            var gp = new GetPoint();
            gp.SetCommandPrompt("Pick point on region");
            gp.Constrain(plugin.ActiveSubD, false);

            if (gp.Get() != GetResult.Point)
            {
                return Result.Cancel;
            }

            var point = gp.Point();

            // Project to parametric space
            var param = plugin.Evaluator.ProjectPoint(point);
            if (!param.IsValid)
            {
                RhinoApp.WriteLine("Could not project point to surface.");
                return Result.Failure;
            }

            // Find containing region
            var region = plugin.RegionManager.FindRegionAt(param);
            if (region == null)
            {
                RhinoApp.WriteLine("No region found at this location.");
                return Result.Nothing;
            }

            // Select the region
            plugin.RegionManager.SelectRegion(region.Id);

            RhinoApp.WriteLine($"Selected region: {region.Id}");
            doc.Views.Redraw();

            return Result.Success;
        }

        private Result SelectEdge(RhinoDoc doc, LatentPlugin plugin)
        {
            var gp = new GetPoint();
            gp.SetCommandPrompt("Pick point near edge");
            gp.Constrain(plugin.ActiveSubD, false);

            if (gp.Get() != GetResult.Point)
            {
                return Result.Cancel;
            }

            var point = gp.Point();
            var param = plugin.Evaluator.ProjectPoint(point);

            var edge = plugin.RegionManager.FindNearestEdge(param);
            if (edge == null)
            {
                RhinoApp.WriteLine("No edge found near this location.");
                return Result.Nothing;
            }

            plugin.RegionManager.SelectEdge(edge.Id);

            RhinoApp.WriteLine($"Selected edge: {edge.Id}");
            doc.Views.Redraw();

            return Result.Success;
        }

        private Result SelectVertex(RhinoDoc doc, LatentPlugin plugin)
        {
            var gp = new GetPoint();
            gp.SetCommandPrompt("Pick point near vertex");
            gp.Constrain(plugin.ActiveSubD, false);

            if (gp.Get() != GetResult.Point)
            {
                return Result.Cancel;
            }

            var point = gp.Point();
            var param = plugin.Evaluator.ProjectPoint(point);

            var vertex = plugin.RegionManager.FindNearestVertex(param);
            if (vertex == null)
            {
                RhinoApp.WriteLine("No vertex found near this location.");
                return Result.Nothing;
            }

            plugin.RegionManager.SelectVertex(vertex.Id);

            RhinoApp.WriteLine($"Selected vertex: {vertex.Id}");
            doc.Views.Redraw();

            return Result.Success;
        }
    }
}
```

### 4. Create LatentPinCommand.cs

```csharp
// rhino_plugin/Commands/LatentPinCommand.cs
using Rhino;
using Rhino.Commands;
using Rhino.Input.Custom;

namespace Latent.Commands
{
    /// <summary>
    /// Command to pin or unpin selected elements.
    /// </summary>
    [CommandStyle(Style.ScriptRunner)]
    public class LatentPinCommand : Command
    {
        public override string EnglishName => "LatentPin";

        protected override Result RunCommand(RhinoDoc doc, RunMode mode)
        {
            var plugin = LatentPlugin.Instance;

            if (!plugin.IsReady)
            {
                RhinoApp.WriteLine("No analysis active. Run LatentAnalyze first.");
                return Result.Cancel;
            }

            // Check for selection
            var selection = plugin.RegionManager.GetSelection();
            if (selection.Count == 0)
            {
                RhinoApp.WriteLine("Nothing selected. Use LatentSelect first.");
                return Result.Cancel;
            }

            // Get action
            var go = new GetOption();
            go.SetCommandPrompt("Pin action");
            go.AddOption("Pin");
            go.AddOption("Unpin");
            go.AddOption("Toggle");

            var result = go.Get();
            if (result != GetResult.Option)
            {
                return Result.Cancel;
            }

            var action = go.Option().EnglishName;

            // Apply action to all selected elements
            int count = 0;
            foreach (var element in selection)
            {
                bool newState;
                switch (action)
                {
                    case "Pin":
                        newState = true;
                        break;
                    case "Unpin":
                        newState = false;
                        break;
                    case "Toggle":
                        newState = !element.IsPinned;
                        break;
                    default:
                        continue;
                }

                if (newState != element.IsPinned)
                {
                    plugin.RegionManager.SetPinned(element.Id, newState);
                    count++;
                }
            }

            RhinoApp.WriteLine($"{action}: {count} elements");
            doc.Views.Redraw();

            return Result.Success;
        }
    }
}
```

### 5. Create LatentRevertCommand.cs

```csharp
// rhino_plugin/Commands/LatentRevertCommand.cs
using Rhino;
using Rhino.Commands;
using Rhino.Input.Custom;
using Rhino.UI;
using Latent.Geometry;

namespace Latent.Commands
{
    /// <summary>
    /// Command to revert selected elements to implicit state.
    /// </summary>
    [CommandStyle(Style.ScriptRunner)]
    public class LatentRevertCommand : Command
    {
        public override string EnglishName => "LatentRevert";

        protected override Result RunCommand(RhinoDoc doc, RunMode mode)
        {
            var plugin = LatentPlugin.Instance;

            if (!plugin.IsReady)
            {
                RhinoApp.WriteLine("No analysis active. Run LatentAnalyze first.");
                return Result.Cancel;
            }

            // Check for selection
            var selection = plugin.RegionManager.GetSelection();
            if (selection.Count == 0)
            {
                RhinoApp.WriteLine("Nothing selected. Use LatentSelect first.");
                return Result.Cancel;
            }

            int reverted = 0;
            int skipped = 0;

            foreach (var element in selection)
            {
                // Check if pinned
                if (element.IsPinned)
                {
                    RhinoApp.WriteLine($"Cannot revert {element.Id}: element is pinned. Unpin first.");
                    skipped++;
                    continue;
                }

                // Check if already implicit
                if (element.IsImplicit)
                {
                    RhinoApp.WriteLine($"Skipping {element.Id}: already at implicit position.");
                    skipped++;
                    continue;
                }

                // Handle edge revert options
                if (element is Edge edge)
                {
                    var result = HandleEdgeRevert(edge, plugin);
                    if (result)
                    {
                        reverted++;
                    }
                    else
                    {
                        skipped++;
                    }
                    continue;
                }

                // Handle vertex with curve modification constraint
                if (element is Vertex vertex && vertex.CreatedBy == "curve_modification")
                {
                    RhinoApp.WriteLine($"Cannot revert {vertex.Id}: vertex was created by curve modification.");
                    RhinoApp.WriteLine("Revert the parent edge curve type first.");
                    skipped++;
                    continue;
                }

                // Perform revert
                plugin.RegionManager.Revert(element.Id);
                reverted++;
            }

            RhinoApp.WriteLine($"Reverted: {reverted}, Skipped: {skipped}");
            doc.Views.Redraw();

            return reverted > 0 ? Result.Success : Result.Nothing;
        }

        private bool HandleEdgeRevert(Edge edge, LatentPlugin plugin)
        {
            // Edge has two revert options: curve type only or full
            var go = new GetOption();
            go.SetCommandPrompt($"Revert edge {edge.Id}");
            go.AddOption("CurveTypeOnly", "Revert curve type, keep vertex positions");
            go.AddOption("Full", "Revert curve type and all vertex positions");
            go.AddOption("Cancel");

            var result = go.Get();
            if (result != GetResult.Option)
            {
                return false;
            }

            switch (go.Option().EnglishName)
            {
                case "CurveTypeOnly":
                    plugin.RegionManager.RevertEdgeCurveType(edge.Id);
                    return true;

                case "Full":
                    plugin.RegionManager.RevertEdgeFully(edge.Id);
                    return true;

                default:
                    return false;
            }
        }
    }
}
```

## Success Criteria

- [ ] Plugin loads without errors in Rhino
- [ ] LatentAnalyze command appears in command list
- [ ] LatentAnalyze selects SubD and runs analysis
- [ ] LatentSelect picks regions/edges/vertices
- [ ] LatentPin pins/unpins selected elements
- [ ] LatentRevert handles revert hierarchy correctly
- [ ] All commands integrate with RegionManager

## Verification Commands

```bash
cd /Users/NickDuch/.claude-worktrees/Latent/focused-robinson/rhino_plugin

# Build the plugin
dotnet build

# The plugin .rhp file should appear in bin/Debug
ls -la bin/Debug/net48/*.rhp
```

## Do Not Modify

- Files in `rhino_plugin/Interop/` (Agent 3A's domain)
- Files in `rhino_plugin/Analysis/` (Agent 3B's domain)
- Files in `rhino_plugin/Geometry/` (Agent 3D's domain)

## Skills to Use

- `superpowers:verification-before-completion` - verify commands work in Rhino

## Notes

**Async commands**: The analysis command runs async operations. For simplicity, we block with `.GetAwaiter().GetResult()`. A more sophisticated approach would use `Rhino.UI.Async` or display a progress dialog.

**Error handling**: Commands should gracefully handle missing analysis service, failed projections, and other edge cases.

## Report

When complete, provide:
1. Build output showing successful compilation
2. List of created command files
3. Any Rhino-specific issues encountered
