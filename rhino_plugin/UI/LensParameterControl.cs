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
