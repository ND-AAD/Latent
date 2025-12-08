// rhino_plugin/Commands/LatentSelectCommand.cs
using Rhino;
using Rhino.Commands;
using Rhino.Input;
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
            // Note: SubD constraint would require converting to Brep first
            // For now, just get a point and project it

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
            // Note: SubD constraint would require converting to Brep first

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
            // Note: SubD constraint would require converting to Brep first

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
