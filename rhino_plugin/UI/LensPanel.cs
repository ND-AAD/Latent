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
                Text = "Analyze",
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
                UpdateStatus("No geometry loaded", isError: true);
                return;
            }

            var lensClient = plugin.LensClient;
            var regionManager = plugin.RegionManager;

            if (lensClient == null || regionManager == null)
            {
                UpdateStatus("Services not available", isError: true);
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
                UpdateStatus($"Found {regionCount} regions");

                // Redraw viewports
                RhinoDoc.ActiveDoc?.Views.Redraw();
            }
            catch (OperationCanceledException)
            {
                UpdateStatus("Analysis canceled");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Analysis failed: {ex.Message}", isError: true);
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
                    _analyzeButton.Text = "Cancel";
                }
                else
                {
                    _analyzeButton.Text = "Analyze";
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
