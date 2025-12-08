// rhino_plugin/Commands/LatentRevertCommand.cs
using Rhino;
using Rhino.Commands;
using Rhino.Input;
using Rhino.Input.Custom;
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
                    var revertResult = HandleEdgeRevert(edge, plugin);
                    if (revertResult)
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
                if (element is Vertex vertex && vertex.CreatedBy == VertexOrigin.CurveModification)
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
