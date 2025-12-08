# Agent 6B: Lens Control Panel

## Objective

Implement an Eto.Forms panel for selecting mathematical lenses, configuring lens-specific parameters, running analysis, and displaying progress/results.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `rhino_plugin/Analysis/LensClient.cs` - lens analysis client with `AnalyzeDifferentialAsync`, `AnalyzeSpectralAsync`
- `rhino_plugin/Analysis/Protocol.cs` - `AnalyzeParams` with lens-specific parameters
- `rhino_plugin/Geometry/RegionManager.cs` - `UpdateFromAnalysis()` method
- `app/ui/analysis_panel.py` - Python reference implementation to port

## Dependencies

**From Prior Phases:**
- `LensClient` - provides async analysis methods
- `RegionManager` - receives analysis results
- `LatentPlugin.Instance` - provides access to services and `ActiveSubD`

## Files to Create

1. `rhino_plugin/UI/LensParameterControl.cs` - dynamic parameter controls
2. `rhino_plugin/UI/LensPanel.cs` - main lens control panel
3. `rhino_plugin/Tests/LensPanelTests.cs` - unit tests

## Files to Modify

1. `rhino_plugin/LatentPlugin.cs` - register panel

## Tasks

### 1. Create LensParameterControl.cs

```csharp
// rhino_plugin/UI/LensParameterControl.cs
using System;
using System.Collections.Generic;
using Eto.Forms;
using Eto.Drawing;

namespace Latent.UI
{
    /// <summary>
    /// Available lens types for analysis.
    /// </summary>
    public enum LensType
    {
        Differential,  // Curvature-based analysis
        Spectral       // Eigenfunction-based analysis
    }

    /// <summary>
    /// Metadata for a lens parameter.
    /// </summary>
    public class LensParameter
    {
        public string Name { get; set; } = "";
        public string DisplayName { get; set; } = "";
        public string Description { get; set; } = "";
        public double DefaultValue { get; set; }
        public double MinValue { get; set; }
        public double MaxValue { get; set; }
        public double Step { get; set; } = 0.1;
        public bool IsInteger { get; set; }
    }

    /// <summary>
    /// Registry of lens parameters for each lens type.
    /// </summary>
    public static class LensParameterRegistry
    {
        public static Dictionary<LensType, List<LensParameter>> Parameters { get; } = new()
        {
            {
                LensType.Differential,
                new List<LensParameter>
                {
                    new LensParameter
                    {
                        Name = "curvature_tolerance",
                        DisplayName = "Curvature Tolerance",
                        Description = "Threshold for curvature change detection (lower = more regions)",
                        DefaultValue = 0.3,
                        MinValue = 0.01,
                        MaxValue = 1.0,
                        Step = 0.05
                    }
                }
            },
            {
                LensType.Spectral,
                new List<LensParameter>
                {
                    new LensParameter
                    {
                        Name = "num_eigenfunctions",
                        DisplayName = "Eigenfunctions",
                        Description = "Number of vibration modes to analyze (more = finer decomposition)",
                        DefaultValue = 3,
                        MinValue = 1,
                        MaxValue = 10,
                        Step = 1,
                        IsInteger = true
                    }
                }
            }
        };

        public static List<LensParameter> GetParameters(LensType lens)
        {
            return Parameters.TryGetValue(lens, out var list) ? list : new List<LensParameter>();
        }
    }

    /// <summary>
    /// Control for editing a single lens parameter.
    /// </summary>
    public class LensParameterControl : Panel
    {
        private readonly LensParameter _parameter;
        private readonly NumericStepper _stepper;
        private readonly Slider _slider;

        public event EventHandler? ValueChanged;

        public double Value
        {
            get => _stepper.Value;
            set
            {
                _stepper.Value = value;
                UpdateSlider();
            }
        }

        public string ParameterName => _parameter.Name;

        public LensParameterControl(LensParameter parameter)
        {
            _parameter = parameter ?? throw new ArgumentNullException(nameof(parameter));

            // Label
            var label = new Label
            {
                Text = parameter.DisplayName,
                ToolTip = parameter.Description
            };

            // Numeric stepper
            _stepper = new NumericStepper
            {
                MinValue = parameter.MinValue,
                MaxValue = parameter.MaxValue,
                Increment = parameter.Step,
                Value = parameter.DefaultValue,
                DecimalPlaces = parameter.IsInteger ? 0 : 2,
                Width = 80
            };
            _stepper.ValueChanged += OnStepperChanged;

            // Slider for visual feedback
            _slider = new Slider
            {
                MinValue = (int)(parameter.MinValue * 100),
                MaxValue = (int)(parameter.MaxValue * 100),
                Value = (int)(parameter.DefaultValue * 100),
                TickFrequency = (int)(parameter.Step * 100),
                SnapToTick = true
            };
            _slider.ValueChanged += OnSliderChanged;

            // Description tooltip
            var helpLabel = new Label
            {
                Text = "?",
                ToolTip = parameter.Description,
                TextColor = Colors.Gray,
                Font = new Font(SystemFont.Default, 10)
            };

            // Layout
            var topRow = new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items = { label, null, _stepper, helpLabel }
            };

            Content = new StackLayout
            {
                Spacing = 2,
                Items = { topRow, _slider }
            };
        }

        private void OnStepperChanged(object? sender, EventArgs e)
        {
            UpdateSlider();
            ValueChanged?.Invoke(this, EventArgs.Empty);
        }

        private void OnSliderChanged(object? sender, EventArgs e)
        {
            double newValue = _slider.Value / 100.0;
            if (Math.Abs(newValue - _stepper.Value) > 0.001)
            {
                _stepper.Value = _parameter.IsInteger ? Math.Round(newValue) : newValue;
                ValueChanged?.Invoke(this, EventArgs.Empty);
            }
        }

        private void UpdateSlider()
        {
            int sliderValue = (int)(_stepper.Value * 100);
            if (_slider.Value != sliderValue)
            {
                _slider.Value = sliderValue;
            }
        }

        public void Reset()
        {
            Value = _parameter.DefaultValue;
        }
    }
}
```

### 2. Create LensPanel.cs

```csharp
// rhino_plugin/UI/LensPanel.cs
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Eto.Forms;
using Eto.Drawing;
using Rhino;
using Rhino.UI;
using Latent.Analysis;
using Latent.Geometry;

namespace Latent.UI
{
    /// <summary>
    /// Panel for selecting lenses, configuring parameters, and running analysis.
    /// </summary>
    [System.Runtime.InteropServices.Guid("B2C3D4E5-F6A7-8901-BCDE-F23456789012")]
    public class LensPanel : Panel, IPanel
    {
        private readonly DropDown _lensSelector;
        private readonly DynamicLayout _parameterContainer;
        private readonly Button _analyzeButton;
        private readonly Button _resetButton;
        private readonly ProgressBar _progressBar;
        private readonly Label _statusLabel;

        private readonly List<LensParameterControl> _parameterControls = new();
        private LensType _currentLens = LensType.Differential;
        private CancellationTokenSource? _analysisCts;
        private bool _isAnalyzing;

        public static Guid PanelId => typeof(LensPanel).GUID;

        public LensPanel()
        {
            // Lens selector
            _lensSelector = new DropDown();
            _lensSelector.Items.Add("Differential (Curvature)");
            _lensSelector.Items.Add("Spectral (Eigenfunction)");
            _lensSelector.SelectedIndex = 0;
            _lensSelector.SelectedIndexChanged += OnLensChanged;

            // Parameter container (dynamic)
            _parameterContainer = new DynamicLayout
            {
                Padding = new Padding(5),
                Spacing = new Size(5, 5)
            };

            // Analyze button
            _analyzeButton = new Button
            {
                Text = "🔍 Analyze",
                Enabled = false
            };
            _analyzeButton.Click += OnAnalyzeClicked;

            // Reset button
            _resetButton = new Button { Text = "Reset" };
            _resetButton.Click += OnResetClicked;

            // Progress bar
            _progressBar = new ProgressBar
            {
                Visible = false,
                Indeterminate = true
            };

            // Status label
            _statusLabel = new Label
            {
                Text = "Load geometry to enable analysis",
                TextColor = Colors.Gray,
                Wrap = WrapMode.Word
            };

            // Button row
            var buttonRow = new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items = { _analyzeButton, _resetButton }
            };

            // Main layout
            Content = new StackLayout
            {
                Padding = new Padding(5),
                Spacing = 10,
                Items =
                {
                    new GroupBox
                    {
                        Text = "Mathematical Lens",
                        Content = _lensSelector,
                        Padding = new Padding(5)
                    },
                    new GroupBox
                    {
                        Text = "Parameters",
                        Content = _parameterContainer,
                        Padding = new Padding(5)
                    },
                    buttonRow,
                    _progressBar,
                    _statusLabel
                }
            };

            // Initialize parameter controls for default lens
            RebuildParameterControls();

            // Check if ready
            UpdateAnalyzeButtonState();
        }

        #region IPanel Implementation

        public void PanelShown(uint documentSerialNumber, ShowPanelReason reason)
        {
            UpdateAnalyzeButtonState();
        }

        public void PanelHidden(uint documentSerialNumber, ShowPanelReason reason)
        {
            // Cancel any running analysis
            _analysisCts?.Cancel();
        }

        public void PanelClosing(uint documentSerialNumber, bool onCloseDocument)
        {
            _analysisCts?.Cancel();
            _analysisCts?.Dispose();
        }

        #endregion

        #region Event Handlers

        private void OnLensChanged(object? sender, EventArgs e)
        {
            _currentLens = _lensSelector.SelectedIndex switch
            {
                0 => LensType.Differential,
                1 => LensType.Spectral,
                _ => LensType.Differential
            };

            RebuildParameterControls();
            UpdateStatus($"Ready to analyze with {_currentLens} lens");
        }

        private async void OnAnalyzeClicked(object? sender, EventArgs e)
        {
            if (_isAnalyzing)
            {
                // Cancel running analysis
                _analysisCts?.Cancel();
                return;
            }

            await RunAnalysisAsync();
        }

        private void OnResetClicked(object? sender, EventArgs e)
        {
            foreach (var control in _parameterControls)
            {
                control.Reset();
            }
            UpdateStatus("Parameters reset to defaults");
        }

        #endregion

        #region Analysis

        private async Task RunAnalysisAsync()
        {
            var plugin = LatentPlugin.Instance;
            if (plugin == null || !plugin.IsReady)
            {
                UpdateStatus("❌ No geometry loaded", isError: true);
                return;
            }

            var lensClient = plugin.LensClient;
            var regionManager = plugin.RegionManager;

            if (lensClient == null || regionManager == null)
            {
                UpdateStatus("❌ Services not available", isError: true);
                return;
            }

            // Start analysis
            _isAnalyzing = true;
            _analysisCts = new CancellationTokenSource();
            var token = _analysisCts.Token;

            SetAnalyzingState(true);
            UpdateStatus($"Analyzing with {_currentLens} lens...");

            try
            {
                // Ensure service is running
                await lensClient.StartServiceAsync(token);

                // Initialize with current SubD
                await lensClient.InitializeAsync(plugin.ActiveSubD, token);

                // Run analysis with collected parameters
                var parameters = GetCurrentParameters();
                AnalysisResultData result;

                if (_currentLens == LensType.Differential)
                {
                    double tolerance = parameters.TryGetValue("curvature_tolerance", out var t) ? t : 0.3;
                    result = await lensClient.AnalyzeDifferentialAsync(tolerance, token);
                }
                else
                {
                    int numEigen = parameters.TryGetValue("num_eigenfunctions", out var n) ? (int)n : 3;
                    result = await lensClient.AnalyzeSpectralAsync(numEigen, token);
                }

                // Update region manager
                regionManager.UpdateFromAnalysis(result);

                // Update status
                int regionCount = result.Regions?.Count ?? 0;
                UpdateStatus($"✅ Found {regionCount} regions");

                // Redraw viewports
                RhinoDoc.ActiveDoc?.Views.Redraw();
            }
            catch (OperationCanceledException)
            {
                UpdateStatus("Analysis canceled");
            }
            catch (Exception ex)
            {
                UpdateStatus($"❌ Analysis failed: {ex.Message}", isError: true);
                RhinoApp.WriteLine($"Lens analysis error: {ex}");
            }
            finally
            {
                SetAnalyzingState(false);
                _isAnalyzing = false;
                _analysisCts?.Dispose();
                _analysisCts = null;
            }
        }

        private Dictionary<string, double> GetCurrentParameters()
        {
            var result = new Dictionary<string, double>();
            foreach (var control in _parameterControls)
            {
                result[control.ParameterName] = control.Value;
            }
            return result;
        }

        #endregion

        #region UI Updates

        private void RebuildParameterControls()
        {
            _parameterControls.Clear();
            _parameterContainer.Clear();

            var parameters = LensParameterRegistry.GetParameters(_currentLens);

            if (parameters.Count == 0)
            {
                _parameterContainer.Add(new Label
                {
                    Text = "No parameters for this lens",
                    TextColor = Colors.Gray
                });
            }
            else
            {
                foreach (var param in parameters)
                {
                    var control = new LensParameterControl(param);
                    _parameterControls.Add(control);
                    _parameterContainer.Add(control);
                }
            }

            _parameterContainer.Create();
        }

        private void SetAnalyzingState(bool analyzing)
        {
            Application.Instance.Invoke(() =>
            {
                _progressBar.Visible = analyzing;
                _lensSelector.Enabled = !analyzing;
                _resetButton.Enabled = !analyzing;

                if (analyzing)
                {
                    _analyzeButton.Text = "⏹ Cancel";
                }
                else
                {
                    _analyzeButton.Text = "🔍 Analyze";
                }

                foreach (var control in _parameterControls)
                {
                    control.Enabled = !analyzing;
                }
            });
        }

        private void UpdateAnalyzeButtonState()
        {
            var plugin = LatentPlugin.Instance;
            bool isReady = plugin?.IsReady ?? false;

            Application.Instance.Invoke(() =>
            {
                _analyzeButton.Enabled = isReady && !_isAnalyzing;

                if (!isReady)
                {
                    UpdateStatus("Load geometry to enable analysis");
                }
            });
        }

        private void UpdateStatus(string message, bool isError = false)
        {
            Application.Instance.Invoke(() =>
            {
                _statusLabel.Text = message;
                _statusLabel.TextColor = isError ? Colors.Red : Colors.Gray;
            });
        }

        #endregion
    }
}
```

### 3. Create Unit Tests

```csharp
// rhino_plugin/Tests/LensPanelTests.cs
using System.Collections.Generic;
using NUnit.Framework;
using Latent.UI;

namespace Latent.Tests
{
    [TestFixture]
    public class LensParameterRegistryTests
    {
        [Test]
        public void GetParameters_Differential_ReturnsCurvatureTolerance()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Differential);

            Assert.That(parameters, Has.Count.GreaterThan(0));
            Assert.That(parameters[0].Name, Is.EqualTo("curvature_tolerance"));
        }

        [Test]
        public void GetParameters_Spectral_ReturnsNumEigenfunctions()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Spectral);

            Assert.That(parameters, Has.Count.GreaterThan(0));
            Assert.That(parameters[0].Name, Is.EqualTo("num_eigenfunctions"));
        }

        [Test]
        public void CurvatureTolerance_HasValidRange()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Differential);
            var param = parameters.Find(p => p.Name == "curvature_tolerance");

            Assert.That(param, Is.Not.Null);
            Assert.That(param!.MinValue, Is.GreaterThan(0));
            Assert.That(param.MaxValue, Is.LessThanOrEqualTo(1.0));
            Assert.That(param.DefaultValue, Is.InRange(param.MinValue, param.MaxValue));
        }

        [Test]
        public void NumEigenfunctions_IsInteger()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Spectral);
            var param = parameters.Find(p => p.Name == "num_eigenfunctions");

            Assert.That(param, Is.Not.Null);
            Assert.That(param!.IsInteger, Is.True);
        }

        [Test]
        public void NumEigenfunctions_HasValidRange()
        {
            var parameters = LensParameterRegistry.GetParameters(LensType.Spectral);
            var param = parameters.Find(p => p.Name == "num_eigenfunctions");

            Assert.That(param, Is.Not.Null);
            Assert.That(param!.MinValue, Is.GreaterThanOrEqualTo(1));
            Assert.That(param.MaxValue, Is.GreaterThan(param.MinValue));
            Assert.That(param.DefaultValue, Is.InRange(param.MinValue, param.MaxValue));
        }
    }

    [TestFixture]
    public class LensParameterTests
    {
        [Test]
        public void LensParameter_DefaultValues()
        {
            var param = new LensParameter();

            Assert.That(param.Name, Is.EqualTo(""));
            Assert.That(param.Step, Is.EqualTo(0.1));
            Assert.That(param.IsInteger, Is.False);
        }

        [Test]
        public void LensParameter_CanSetAllProperties()
        {
            var param = new LensParameter
            {
                Name = "test_param",
                DisplayName = "Test Parameter",
                Description = "A test parameter",
                DefaultValue = 5.0,
                MinValue = 0.0,
                MaxValue = 10.0,
                Step = 0.5,
                IsInteger = false
            };

            Assert.That(param.Name, Is.EqualTo("test_param"));
            Assert.That(param.DisplayName, Is.EqualTo("Test Parameter"));
            Assert.That(param.Description, Is.EqualTo("A test parameter"));
            Assert.That(param.DefaultValue, Is.EqualTo(5.0));
            Assert.That(param.MinValue, Is.EqualTo(0.0));
            Assert.That(param.MaxValue, Is.EqualTo(10.0));
            Assert.That(param.Step, Is.EqualTo(0.5));
        }
    }

    [TestFixture]
    public class LensTypeTests
    {
        [Test]
        public void LensType_HasExpectedValues()
        {
            Assert.That(LensType.Differential, Is.EqualTo((LensType)0));
            Assert.That(LensType.Spectral, Is.EqualTo((LensType)1));
        }

        [Test]
        public void AllLensTypes_HaveParameters()
        {
            foreach (LensType lens in System.Enum.GetValues(typeof(LensType)))
            {
                var parameters = LensParameterRegistry.GetParameters(lens);
                Assert.That(parameters, Is.Not.Null,
                    $"LensType.{lens} should have parameters defined");
            }
        }

        [Test]
        public void AllParameters_HaveValidDefaults()
        {
            foreach (LensType lens in System.Enum.GetValues(typeof(LensType)))
            {
                var parameters = LensParameterRegistry.GetParameters(lens);
                foreach (var param in parameters)
                {
                    Assert.That(param.DefaultValue, Is.InRange(param.MinValue, param.MaxValue),
                        $"{lens}.{param.Name} default value out of range");
                }
            }
        }
    }
}
```

### 4. Update LatentPlugin.cs for Panel Registration

Add this to the `OnLoad` method in `LatentPlugin.cs`:

```csharp
// Add to rhino_plugin/LatentPlugin.cs in OnLoad method

// Register Lens Panel
Rhino.UI.Panels.RegisterPanel(
    this,
    typeof(UI.LensPanel),
    "Latent Lens",
    System.Drawing.SystemIcons.Application.ToBitmap()
);
```

## Success Criteria

- [ ] Lens selector shows Differential and Spectral options
- [ ] Parameter controls update dynamically when lens changes
- [ ] Curvature tolerance slider/stepper works correctly
- [ ] Eigenfunctions parameter shows integer values only
- [ ] Analyze button disabled when no geometry loaded
- [ ] Progress bar visible during analysis
- [ ] Analyze button changes to Cancel during analysis
- [ ] Cancel stops running analysis
- [ ] Reset button restores default parameter values
- [ ] Status shows success with region count
- [ ] Status shows error message on failure
- [ ] RegionManager receives analysis results
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run tests
dotnet test --filter "FullyQualifiedName~LensParameter|FullyQualifiedName~LensType"

# Verify files exist
ls UI/LensPanel.cs
ls UI/LensParameterControl.cs
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Analysis/` except for panel integration
- Files in `Display/` (Phase 4 domain)
- Files in `Interaction/` (Phase 5 domain)
- `UI/GeometryListPanel.cs` (Agent 6A's domain)
- `UI/VisualizationPanel.cs` (Agent 6C's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests before reporting

## Notes

- Use `CancellationTokenSource` for cancellable async operations
- Always marshal UI updates with `Application.Instance.Invoke()`
- `LensClient.StartServiceAsync()` starts the Python subprocess if needed
- Panel GUID must be unique and consistent across sessions
- Python `analysis_panel.py` provides additional features (histogram, export) that could be added later

## Report

When complete, provide:
1. Build output showing no errors
2. Test output showing all tests pass
3. Description of parameter control behavior
4. Any async/threading considerations
