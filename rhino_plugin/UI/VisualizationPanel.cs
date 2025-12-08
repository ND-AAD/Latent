// rhino_plugin/UI/VisualizationPanel.cs
using System;
using Eto.Forms;
using Eto.Drawing;
using Rhino;
using Rhino.UI;
using Latent.Display;

namespace Latent.UI
{
    /// <summary>
    /// Panel for controlling visualization settings.
    /// </summary>
    [System.Runtime.InteropServices.Guid("C3D4E5F6-A7B8-9012-CDEF-345678901234")]
    public class VisualizationPanel : Panel, IPanel
    {
        // Display toggles
        private readonly CheckBox _showRegionFillCheck;
        private readonly CheckBox _showCentroidMarkersCheck;

        // Opacity slider
        private readonly Slider _fillOpacitySlider;
        private readonly Label _fillOpacityLabel;

        // Color pickers
        private readonly ColorPicker _selectedColorPicker;
        private readonly ColorPicker _pinnedColorPicker;
        private readonly ColorPicker _defaultColorPicker;
        private readonly ColorPicker _hoveredColorPicker;

        // Curve settings
        private readonly NumericStepper _defaultThicknessStepper;
        private readonly NumericStepper _selectedThicknessStepper;

        // Performance
        private readonly CheckBox _useAdaptiveSamplingCheck;
        private readonly CheckBox _cacheCurvesCheck;

        // Reset button
        private readonly Button _resetButton;

        private VisualizationSettings? _settings;
        private bool _isUpdating;

        public static Guid PanelId => typeof(VisualizationPanel).GUID;

        public VisualizationPanel()
        {
            // Display toggles
            _showRegionFillCheck = new CheckBox { Text = "Show region fill" };
            _showRegionFillCheck.CheckedChanged += OnSettingChanged;

            _showCentroidMarkersCheck = new CheckBox { Text = "Show centroid markers" };
            _showCentroidMarkersCheck.CheckedChanged += OnSettingChanged;

            // Fill opacity
            _fillOpacitySlider = new Slider
            {
                MinValue = 0,
                MaxValue = 255,
                Value = 64,
                TickFrequency = 32
            };
            _fillOpacitySlider.ValueChanged += OnOpacityChanged;

            _fillOpacityLabel = new Label { Text = "Opacity: 25%" };

            var opacityLayout = new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items = { _fillOpacitySlider, _fillOpacityLabel }
            };

            // Color pickers
            _selectedColorPicker = CreateColorPicker("Selected:", Colors.Yellow);
            _pinnedColorPicker = CreateColorPicker("Pinned:", Colors.LightBlue);
            _defaultColorPicker = CreateColorPicker("Default:", Colors.Gray);
            _hoveredColorPicker = CreateColorPicker("Hovered:", Colors.Orange);

            // Curve thickness
            _defaultThicknessStepper = new NumericStepper
            {
                MinValue = 0.5,
                MaxValue = 5.0,
                Increment = 0.5,
                Value = 1.5,
                DecimalPlaces = 1,
                Width = 60
            };
            _defaultThicknessStepper.ValueChanged += OnSettingChanged;

            _selectedThicknessStepper = new NumericStepper
            {
                MinValue = 1.0,
                MaxValue = 10.0,
                Increment = 0.5,
                Value = 3.0,
                DecimalPlaces = 1,
                Width = 60
            };
            _selectedThicknessStepper.ValueChanged += OnSettingChanged;

            var thicknessLayout = new TableLayout
            {
                Spacing = new Size(5, 5),
                Rows =
                {
                    new TableRow(new Label { Text = "Default:" }, _defaultThicknessStepper),
                    new TableRow(new Label { Text = "Selected:" }, _selectedThicknessStepper)
                }
            };

            // Performance
            _useAdaptiveSamplingCheck = new CheckBox { Text = "Use adaptive sampling" };
            _useAdaptiveSamplingCheck.CheckedChanged += OnSettingChanged;

            _cacheCurvesCheck = new CheckBox { Text = "Cache curves" };
            _cacheCurvesCheck.CheckedChanged += OnSettingChanged;

            // Reset button
            _resetButton = new Button { Text = "Reset to Defaults" };
            _resetButton.Click += OnResetClicked;

            // Main layout
            Content = new Scrollable
            {
                Content = new StackLayout
                {
                    Padding = new Padding(5),
                    Spacing = 10,
                    Items =
                    {
                        new GroupBox
                        {
                            Text = "Display",
                            Padding = new Padding(5),
                            Content = new StackLayout
                            {
                                Spacing = 5,
                                Items =
                                {
                                    _showRegionFillCheck,
                                    opacityLayout,
                                    _showCentroidMarkersCheck
                                }
                            }
                        },
                        new GroupBox
                        {
                            Text = "Colors",
                            Padding = new Padding(5),
                            Content = new StackLayout
                            {
                                Spacing = 5,
                                Items =
                                {
                                    CreateColorRow("Selected:", _selectedColorPicker),
                                    CreateColorRow("Pinned:", _pinnedColorPicker),
                                    CreateColorRow("Default:", _defaultColorPicker),
                                    CreateColorRow("Hovered:", _hoveredColorPicker)
                                }
                            }
                        },
                        new GroupBox
                        {
                            Text = "Curve Thickness",
                            Padding = new Padding(5),
                            Content = thicknessLayout
                        },
                        new GroupBox
                        {
                            Text = "Performance",
                            Padding = new Padding(5),
                            Content = new StackLayout
                            {
                                Spacing = 5,
                                Items =
                                {
                                    _useAdaptiveSamplingCheck,
                                    _cacheCurvesCheck
                                }
                            }
                        },
                        _resetButton
                    }
                }
            };

            // Load settings
            LoadSettings();
        }

        #region IPanel Implementation

        public void PanelShown(uint documentSerialNumber, ShowPanelReason reason)
        {
            LoadSettings();
        }

        public void PanelHidden(uint documentSerialNumber, ShowPanelReason reason)
        {
            SaveSettings();
        }

        public void PanelClosing(uint documentSerialNumber, bool onCloseDocument)
        {
            SaveSettings();
        }

        #endregion

        #region Helper Methods

        private ColorPicker CreateColorPicker(string label, Color defaultColor)
        {
            var picker = new ColorPicker { Value = defaultColor };
            picker.ValueChanged += OnColorChanged;
            return picker;
        }

        private StackLayout CreateColorRow(string label, ColorPicker picker)
        {
            return new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items =
                {
                    new Label { Text = label, Width = 70 },
                    picker
                }
            };
        }

        private static System.Drawing.Color ToDrawingColor(Color etoColor)
        {
            return System.Drawing.Color.FromArgb(
                (int)(etoColor.A * 255),
                (int)(etoColor.R * 255),
                (int)(etoColor.G * 255),
                (int)(etoColor.B * 255)
            );
        }

        private static Color ToEtoColor(System.Drawing.Color drawingColor)
        {
            return Color.FromArgb(
                drawingColor.R,
                drawingColor.G,
                drawingColor.B,
                drawingColor.A
            );
        }

        #endregion

        #region Settings Load/Save

        private void LoadSettings()
        {
            _settings = LatentPlugin.Instance?.VisualizationSettings;
            if (_settings == null)
            {
                _settings = new VisualizationSettings();
            }

            UpdateControlsFromSettings();
        }

        private void UpdateControlsFromSettings()
        {
            if (_settings == null) return;

            _isUpdating = true;
            try
            {
                _showRegionFillCheck.Checked = _settings.ShowRegionFill;
                _showCentroidMarkersCheck.Checked = _settings.ShowCentroidMarkers;
                _fillOpacitySlider.Value = _settings.FillOpacity;
                UpdateOpacityLabel();

                _selectedColorPicker.Value = ToEtoColor(_settings.SelectedColor);
                _pinnedColorPicker.Value = ToEtoColor(_settings.PinnedColor);
                _defaultColorPicker.Value = ToEtoColor(_settings.DefaultCurveColor);
                _hoveredColorPicker.Value = ToEtoColor(_settings.HoveredColor);

                _defaultThicknessStepper.Value = _settings.DefaultCurveThickness;
                _selectedThicknessStepper.Value = _settings.SelectedCurveThickness;

                _useAdaptiveSamplingCheck.Checked = _settings.UseAdaptiveSampling;
                _cacheCurvesCheck.Checked = _settings.CacheCurves;
            }
            finally
            {
                _isUpdating = false;
            }
        }

        private void SaveSettings()
        {
            if (_settings == null) return;

            var plugin = LatentPlugin.Instance;
            if (plugin != null)
            {
                _settings.Save(plugin);
            }
        }

        private void ApplySettingsToModel()
        {
            if (_settings == null || _isUpdating) return;

            _settings.ShowRegionFill = _showRegionFillCheck.Checked ?? true;
            _settings.ShowCentroidMarkers = _showCentroidMarkersCheck.Checked ?? true;
            _settings.FillOpacity = _fillOpacitySlider.Value;

            _settings.SelectedColor = ToDrawingColor(_selectedColorPicker.Value);
            _settings.PinnedColor = ToDrawingColor(_pinnedColorPicker.Value);
            _settings.DefaultCurveColor = ToDrawingColor(_defaultColorPicker.Value);
            _settings.HoveredColor = ToDrawingColor(_hoveredColorPicker.Value);

            _settings.DefaultCurveThickness = (float)_defaultThicknessStepper.Value;
            _settings.SelectedCurveThickness = (float)_selectedThicknessStepper.Value;

            _settings.UseAdaptiveSampling = _useAdaptiveSamplingCheck.Checked ?? true;
            _settings.CacheCurves = _cacheCurvesCheck.Checked ?? true;

            // Trigger redraw
            RhinoDoc.ActiveDoc?.Views.Redraw();
        }

        #endregion

        #region Event Handlers

        private void OnSettingChanged(object? sender, EventArgs e)
        {
            ApplySettingsToModel();
        }

        private void OnColorChanged(object? sender, EventArgs e)
        {
            ApplySettingsToModel();
        }

        private void OnOpacityChanged(object? sender, EventArgs e)
        {
            UpdateOpacityLabel();
            ApplySettingsToModel();
        }

        private void UpdateOpacityLabel()
        {
            int percent = (int)(_fillOpacitySlider.Value / 255.0 * 100);
            _fillOpacityLabel.Text = $"Opacity: {percent}%";
        }

        private void OnResetClicked(object? sender, EventArgs e)
        {
            if (_settings == null) return;

            var result = MessageBox.Show(
                "Reset all visualization settings to defaults?",
                "Confirm Reset",
                MessageBoxButtons.YesNo,
                MessageBoxType.Question
            );

            if (result == DialogResult.Yes)
            {
                _settings.ResetToDefaults();
                UpdateControlsFromSettings();
                RhinoDoc.ActiveDoc?.Views.Redraw();
            }
        }

        #endregion
    }
}
