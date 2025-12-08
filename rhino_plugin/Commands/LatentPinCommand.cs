// rhino_plugin/Commands/LatentPinCommand.cs
using Rhino;
using Rhino.Commands;
using Rhino.Input;
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
