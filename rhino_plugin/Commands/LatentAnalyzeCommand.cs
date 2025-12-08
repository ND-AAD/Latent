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
