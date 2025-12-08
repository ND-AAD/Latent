// rhino_plugin/Display/VisualizationSettings.cs
using System;
using System.Drawing;

namespace Latent.Display
{
    /// <summary>
    /// Configuration for region visualization.
    /// </summary>
    public class VisualizationSettings
    {
        // Curve display
        public float DefaultCurveThickness { get; set; } = 1.5f;
        public float SelectedCurveThickness { get; set; } = 3.0f;
        public int CurveSampleCount { get; set; } = 50;

        // Colors
        public Color DefaultCurveColor { get; set; } = Color.FromArgb(200, 200, 200);
        public Color SelectedColor { get; set; } = Color.Yellow;
        public Color PinnedColor { get; set; } = Color.FromArgb(100, 150, 255);
        public Color HoveredColor { get; set; } = Color.FromArgb(255, 200, 100);

        // Vertex display
        public int VertexPointSize { get; set; } = 5;
        public int SelectedVertexPointSize { get; set; } = 8;

        // Region fill
        public bool ShowRegionFill { get; set; } = true;
        public int FillOpacity { get; set; } = 64;  // 0-255, 25% default

        // Centroid markers
        public bool ShowCentroidMarkers { get; set; } = true;
        public Color CentroidTextColor { get; set; } = Color.Black;
        public Color CentroidBackgroundColor { get; set; } = Color.White;

        // Performance
        public bool UseAdaptiveSampling { get; set; } = true;
        public bool CacheCurves { get; set; } = true;

        /// <summary>
        /// Event fired when any setting changes.
        /// </summary>
        public event EventHandler? SettingsChanged;

        protected void OnSettingsChanged()
        {
            SettingsChanged?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Get the color for an element based on its state.
        /// </summary>
        public Color GetElementColor(bool isSelected, bool isPinned, bool isHovered = false)
        {
            if (isSelected) return SelectedColor;
            if (isHovered) return HoveredColor;
            if (isPinned) return PinnedColor;
            return DefaultCurveColor;
        }

        /// <summary>
        /// Get curve thickness based on selection state.
        /// </summary>
        public float GetCurveThickness(bool isSelected)
        {
            return isSelected ? SelectedCurveThickness : DefaultCurveThickness;
        }

        /// <summary>
        /// Get a fill color with appropriate transparency.
        /// </summary>
        public Color GetFillColor(Color baseColor)
        {
            return Color.FromArgb(FillOpacity, baseColor);
        }

        #region Persistence

        private const string SettingsSection = "Visualization";

        /// <summary>
        /// Save settings to plugin persistent storage.
        /// </summary>
        public void Save(Rhino.PlugIns.PlugIn plugin)
        {
            var settings = plugin.Settings;
            settings.SetDouble($"{SettingsSection}.DefaultCurveThickness", DefaultCurveThickness);
            settings.SetDouble($"{SettingsSection}.SelectedCurveThickness", SelectedCurveThickness);
            settings.SetInteger($"{SettingsSection}.CurveSampleCount", CurveSampleCount);

            settings.SetColor($"{SettingsSection}.DefaultCurveColor", DefaultCurveColor);
            settings.SetColor($"{SettingsSection}.SelectedColor", SelectedColor);
            settings.SetColor($"{SettingsSection}.PinnedColor", PinnedColor);
            settings.SetColor($"{SettingsSection}.HoveredColor", HoveredColor);

            settings.SetInteger($"{SettingsSection}.VertexPointSize", VertexPointSize);
            settings.SetInteger($"{SettingsSection}.SelectedVertexPointSize", SelectedVertexPointSize);

            settings.SetBool($"{SettingsSection}.ShowRegionFill", ShowRegionFill);
            settings.SetInteger($"{SettingsSection}.FillOpacity", FillOpacity);

            settings.SetBool($"{SettingsSection}.ShowCentroidMarkers", ShowCentroidMarkers);
            settings.SetColor($"{SettingsSection}.CentroidTextColor", CentroidTextColor);
            settings.SetColor($"{SettingsSection}.CentroidBackgroundColor", CentroidBackgroundColor);

            settings.SetBool($"{SettingsSection}.UseAdaptiveSampling", UseAdaptiveSampling);
            settings.SetBool($"{SettingsSection}.CacheCurves", CacheCurves);
        }

        /// <summary>
        /// Load settings from plugin persistent storage.
        /// </summary>
        public void Load(Rhino.PlugIns.PlugIn plugin)
        {
            var settings = plugin.Settings;
            DefaultCurveThickness = (float)settings.GetDouble($"{SettingsSection}.DefaultCurveThickness", DefaultCurveThickness);
            SelectedCurveThickness = (float)settings.GetDouble($"{SettingsSection}.SelectedCurveThickness", SelectedCurveThickness);
            CurveSampleCount = settings.GetInteger($"{SettingsSection}.CurveSampleCount", CurveSampleCount);

            DefaultCurveColor = settings.GetColor($"{SettingsSection}.DefaultCurveColor", DefaultCurveColor);
            SelectedColor = settings.GetColor($"{SettingsSection}.SelectedColor", SelectedColor);
            PinnedColor = settings.GetColor($"{SettingsSection}.PinnedColor", PinnedColor);
            HoveredColor = settings.GetColor($"{SettingsSection}.HoveredColor", HoveredColor);

            VertexPointSize = settings.GetInteger($"{SettingsSection}.VertexPointSize", VertexPointSize);
            SelectedVertexPointSize = settings.GetInteger($"{SettingsSection}.SelectedVertexPointSize", SelectedVertexPointSize);

            ShowRegionFill = settings.GetBool($"{SettingsSection}.ShowRegionFill", ShowRegionFill);
            FillOpacity = settings.GetInteger($"{SettingsSection}.FillOpacity", FillOpacity);

            ShowCentroidMarkers = settings.GetBool($"{SettingsSection}.ShowCentroidMarkers", ShowCentroidMarkers);
            CentroidTextColor = settings.GetColor($"{SettingsSection}.CentroidTextColor", CentroidTextColor);
            CentroidBackgroundColor = settings.GetColor($"{SettingsSection}.CentroidBackgroundColor", CentroidBackgroundColor);

            UseAdaptiveSampling = settings.GetBool($"{SettingsSection}.UseAdaptiveSampling", UseAdaptiveSampling);
            CacheCurves = settings.GetBool($"{SettingsSection}.CacheCurves", CacheCurves);
        }

        /// <summary>
        /// Reset all settings to defaults.
        /// </summary>
        public void ResetToDefaults()
        {
            DefaultCurveThickness = 1.5f;
            SelectedCurveThickness = 3.0f;
            CurveSampleCount = 50;

            DefaultCurveColor = Color.FromArgb(200, 200, 200);
            SelectedColor = Color.Yellow;
            PinnedColor = Color.FromArgb(100, 150, 255);
            HoveredColor = Color.FromArgb(255, 200, 100);

            VertexPointSize = 5;
            SelectedVertexPointSize = 8;

            ShowRegionFill = true;
            FillOpacity = 64;

            ShowCentroidMarkers = true;
            CentroidTextColor = Color.Black;
            CentroidBackgroundColor = Color.White;

            UseAdaptiveSampling = true;
            CacheCurves = true;

            OnSettingsChanged();
        }

        #endregion
    }
}
