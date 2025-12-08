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
