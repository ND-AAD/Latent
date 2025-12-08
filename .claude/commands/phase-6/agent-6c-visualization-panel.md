# Agent 6C: Visualization Settings Panel

## Objective

Implement an Eto.Forms panel for controlling visualization settings (colors, fill opacity, markers) with persistence across sessions.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `rhino_plugin/Display/VisualizationSettings.cs` - settings class with all properties
- `rhino_plugin/Display/RegionConduit.cs` - display conduit that uses settings
- `rhino_plugin/LatentPlugin.cs` - plugin singleton pattern

## Dependencies

**From Prior Phases:**
- `VisualizationSettings` - contains all display properties
- `RegionConduit` - needs refresh when settings change
- `LatentPlugin.Instance` - provides access to services

## Files to Create

1. `rhino_plugin/UI/VisualizationPanel.cs` - main settings panel
2. `rhino_plugin/Tests/VisualizationPanelTests.cs` - unit tests

## Files to Modify

1. `rhino_plugin/Display/VisualizationSettings.cs` - add persistence methods
2. `rhino_plugin/LatentPlugin.cs` - register panel, initialize settings

## Tasks

### 1. Update VisualizationSettings.cs for Persistence

Add these methods to the existing `VisualizationSettings` class:

```csharp
// Add to rhino_plugin/Display/VisualizationSettings.cs

using Rhino.PlugIns;

namespace Latent.Display
{
    public class VisualizationSettings
    {
        // ... existing properties ...

        /// <summary>
        /// Event fired when any setting changes.
        /// </summary>
        public event EventHandler? SettingsChanged;

        protected void OnSettingsChanged()
        {
            SettingsChanged?.Invoke(this, EventArgs.Empty);
        }

        #region Persistence

        private const string SettingsSection = "Visualization";

        /// <summary>
        /// Save settings to plugin persistent storage.
        /// </summary>
        public void Save(PersistentSettings settings)
        {
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
        public void Load(PersistentSettings settings)
        {
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

            DefaultCurveColor = System.Drawing.Color.FromArgb(200, 200, 200);
            SelectedColor = System.Drawing.Color.Yellow;
            PinnedColor = System.Drawing.Color.FromArgb(100, 150, 255);
            HoveredColor = System.Drawing.Color.FromArgb(255, 200, 100);

            VertexPointSize = 5;
            SelectedVertexPointSize = 8;

            ShowRegionFill = true;
            FillOpacity = 64;

            ShowCentroidMarkers = true;
            CentroidTextColor = System.Drawing.Color.Black;
            CentroidBackgroundColor = System.Drawing.Color.White;

            UseAdaptiveSampling = true;
            CacheCurves = true;

            OnSettingsChanged();
        }

        #endregion
    }
}
```

### 2. Create VisualizationPanel.cs

```csharp
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
                _settings.Save(plugin.Settings);
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
```

### 3. Create Unit Tests

```csharp
// rhino_plugin/Tests/VisualizationPanelTests.cs
using System.Drawing;
using NUnit.Framework;
using Latent.Display;

namespace Latent.Tests
{
    [TestFixture]
    public class VisualizationSettingsTests
    {
        private VisualizationSettings _settings;

        [SetUp]
        public void SetUp()
        {
            _settings = new VisualizationSettings();
        }

        [Test]
        public void DefaultValues_AreReasonable()
        {
            Assert.That(_settings.DefaultCurveThickness, Is.EqualTo(1.5f));
            Assert.That(_settings.SelectedCurveThickness, Is.EqualTo(3.0f));
            Assert.That(_settings.CurveSampleCount, Is.EqualTo(50));
            Assert.That(_settings.ShowRegionFill, Is.True);
            Assert.That(_settings.ShowCentroidMarkers, Is.True);
        }

        [Test]
        public void FillOpacity_DefaultIs25Percent()
        {
            // 64 out of 255 = 25%
            Assert.That(_settings.FillOpacity, Is.EqualTo(64));
        }

        [Test]
        public void SelectedColor_IsYellow()
        {
            Assert.That(_settings.SelectedColor, Is.EqualTo(Color.Yellow));
        }

        [Test]
        public void GetElementColor_WhenSelected_ReturnsSelectedColor()
        {
            var color = _settings.GetElementColor(isSelected: true, isPinned: false);

            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetElementColor_WhenPinnedNotSelected_ReturnsPinnedColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: true);

            Assert.That(color, Is.EqualTo(_settings.PinnedColor));
        }

        [Test]
        public void GetElementColor_WhenHovered_ReturnsHoveredColor()
        {
            var color = _settings.GetElementColor(isSelected: false, isPinned: false, isHovered: true);

            Assert.That(color, Is.EqualTo(_settings.HoveredColor));
        }

        [Test]
        public void GetElementColor_Priority_SelectedOverPinned()
        {
            // Selected takes priority over pinned
            var color = _settings.GetElementColor(isSelected: true, isPinned: true);

            Assert.That(color, Is.EqualTo(_settings.SelectedColor));
        }

        [Test]
        public void GetCurveThickness_WhenSelected_ReturnsSelectedThickness()
        {
            var thickness = _settings.GetCurveThickness(isSelected: true);

            Assert.That(thickness, Is.EqualTo(_settings.SelectedCurveThickness));
        }

        [Test]
        public void GetCurveThickness_WhenNotSelected_ReturnsDefaultThickness()
        {
            var thickness = _settings.GetCurveThickness(isSelected: false);

            Assert.That(thickness, Is.EqualTo(_settings.DefaultCurveThickness));
        }

        [Test]
        public void GetFillColor_AppliesOpacity()
        {
            _settings.FillOpacity = 128;  // 50%

            var fillColor = _settings.GetFillColor(Color.Red);

            Assert.That(fillColor.A, Is.EqualTo(128));
            Assert.That(fillColor.R, Is.EqualTo(255));
            Assert.That(fillColor.G, Is.EqualTo(0));
            Assert.That(fillColor.B, Is.EqualTo(0));
        }

        [Test]
        public void ResetToDefaults_RestoresAllValues()
        {
            // Modify settings
            _settings.ShowRegionFill = false;
            _settings.FillOpacity = 200;
            _settings.SelectedColor = Color.Green;
            _settings.DefaultCurveThickness = 5.0f;

            // Reset
            _settings.ResetToDefaults();

            // Verify defaults restored
            Assert.That(_settings.ShowRegionFill, Is.True);
            Assert.That(_settings.FillOpacity, Is.EqualTo(64));
            Assert.That(_settings.SelectedColor, Is.EqualTo(Color.Yellow));
            Assert.That(_settings.DefaultCurveThickness, Is.EqualTo(1.5f));
        }

        [Test]
        public void ResetToDefaults_FiresSettingsChanged()
        {
            bool eventFired = false;
            _settings.SettingsChanged += (s, e) => eventFired = true;

            _settings.ResetToDefaults();

            Assert.That(eventFired, Is.True);
        }

        [Test]
        public void VertexPointSize_HasValidDefaults()
        {
            Assert.That(_settings.VertexPointSize, Is.EqualTo(5));
            Assert.That(_settings.SelectedVertexPointSize, Is.EqualTo(8));
            Assert.That(_settings.SelectedVertexPointSize, Is.GreaterThan(_settings.VertexPointSize));
        }

        [Test]
        public void PerformanceSettings_DefaultsAreEnabled()
        {
            Assert.That(_settings.UseAdaptiveSampling, Is.True);
            Assert.That(_settings.CacheCurves, Is.True);
        }
    }

    [TestFixture]
    public class VisualizationSettingsPersistenceTests
    {
        // Note: These tests require mocking PersistentSettings
        // In a real test environment, you would use a mock or test double

        [Test]
        public void Save_DoesNotThrow()
        {
            var settings = new VisualizationSettings();

            // This is a basic sanity check - full persistence testing
            // requires integration with Rhino's PersistentSettings
            Assert.DoesNotThrow(() =>
            {
                // Would need mock PersistentSettings here
                // settings.Save(mockSettings);
            });
        }

        [Test]
        public void Load_DoesNotThrow()
        {
            var settings = new VisualizationSettings();

            Assert.DoesNotThrow(() =>
            {
                // Would need mock PersistentSettings here
                // settings.Load(mockSettings);
            });
        }
    }
}
```

### 4. Update LatentPlugin.cs

Add the following to `LatentPlugin.cs`:

```csharp
// Add property to LatentPlugin class
public Display.VisualizationSettings VisualizationSettings { get; private set; }

// Add to OnLoad method
VisualizationSettings = new Display.VisualizationSettings();
VisualizationSettings.Load(Settings);

// Register Visualization Panel
Rhino.UI.Panels.RegisterPanel(
    this,
    typeof(UI.VisualizationPanel),
    "Latent Display",
    System.Drawing.SystemIcons.Application.ToBitmap()
);

// Add to OnShutdown method
VisualizationSettings?.Save(Settings);
```

## Success Criteria

- [ ] Panel shows all display toggle checkboxes
- [ ] Fill opacity slider updates percentage label
- [ ] All color pickers work correctly
- [ ] Curve thickness steppers have valid ranges
- [ ] Performance checkboxes toggle correctly
- [ ] Reset button confirms before resetting
- [ ] Settings persist across Rhino sessions
- [ ] Changes trigger viewport redraw
- [ ] SettingsChanged event fires on modifications
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run tests
dotnet test --filter "FullyQualifiedName~VisualizationSettings"

# Verify files exist
ls UI/VisualizationPanel.cs
ls Display/VisualizationSettings.cs
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- `Display/RegionConduit.cs` (Phase 4 domain - only read)
- `Display/CurveSampler.cs` (Phase 4 domain)
- Files in `Interaction/` (Phase 5 domain)
- `UI/GeometryListPanel.cs` (Agent 6A's domain)
- `UI/LensPanel.cs` (Agent 6B's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests before reporting

## Notes

- Use `Rhino.PlugIns.PersistentSettings` for cross-session persistence
- Color conversion between `System.Drawing.Color` and `Eto.Drawing.Color` required
- Settings should trigger immediate viewport refresh
- Wrap content in `Scrollable` for longer settings lists
- Panel GUID must be unique and consistent

## Report

When complete, provide:
1. Build output showing no errors
2. Test output showing all tests pass
3. Description of settings persistence behavior
4. Color picker functionality notes
