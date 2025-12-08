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
    }
}
