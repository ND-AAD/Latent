// rhino_plugin/UI/EdgeRevertDialog.cs
using Eto.Forms;
using Eto.Drawing;

namespace Latent.UI
{
    /// <summary>
    /// Dialog for choosing edge revert options.
    /// </summary>
    public class EdgeRevertDialog : Dialog<bool>
    {
        private readonly RadioButton _curveTypeOnlyRadio;
        private readonly RadioButton _fullyRevertRadio;

        /// <summary>
        /// If true, only revert curve type. If false, revert curve type AND vertex positions.
        /// </summary>
        public bool RevertCurveTypeOnly { get; private set; } = true;

        public EdgeRevertDialog()
        {
            Title = "Revert Edge";
            MinimumSize = new Size(300, 150);
            Padding = new Padding(10);

            // Radio buttons
            _curveTypeOnlyRadio = new RadioButton
            {
                Text = "Revert curve type only",
                Checked = true
            };

            _fullyRevertRadio = new RadioButton(_curveTypeOnlyRadio)
            {
                Text = "Revert curve type AND vertex positions"
            };

            // Description
            var description = new Label
            {
                Text = "Choose how to revert this edge:",
                TextColor = Colors.Gray
            };

            // Buttons
            var okButton = new Button { Text = "Revert" };
            okButton.Click += (s, e) =>
            {
                RevertCurveTypeOnly = _curveTypeOnlyRadio.Checked;
                Result = true;
                Close();
            };

            var cancelButton = new Button { Text = "Cancel" };
            cancelButton.Click += (s, e) =>
            {
                Result = false;
                Close();
            };

            DefaultButton = okButton;
            AbortButton = cancelButton;

            Content = new StackLayout
            {
                Spacing = 10,
                Items =
                {
                    description,
                    _curveTypeOnlyRadio,
                    _fullyRevertRadio,
                    new StackLayoutItem(null, true), // Spacer
                    new StackLayout
                    {
                        Orientation = Orientation.Horizontal,
                        Spacing = 5,
                        Items = { null, cancelButton, okButton }
                    }
                }
            };
        }
    }

    /// <summary>
    /// Dialog shown when trying to revert a vertex created by curve modification.
    /// </summary>
    public class CurveModificationVertexDialog : Dialog<bool>
    {
        /// <summary>
        /// If true, user wants to revert the parent edge's curve type.
        /// </summary>
        public bool RevertParentEdge { get; private set; }

        public CurveModificationVertexDialog(string vertexId, string? parentEdgeId)
        {
            Title = "Cannot Revert Vertex";
            MinimumSize = new Size(350, 150);
            Padding = new Padding(10);

            var message = new Label
            {
                Text = $"Vertex {vertexId} was added when the curve type was changed.\n\n" +
                       "To remove this vertex, revert the edge's curve type first.",
                Wrap = WrapMode.Word
            };

            var revertEdgeButton = new Button
            {
                Text = parentEdgeId != null ? $"Revert Edge {parentEdgeId}" : "Revert Parent Edge"
            };
            revertEdgeButton.Click += (s, e) =>
            {
                RevertParentEdge = true;
                Result = true;
                Close();
            };
            revertEdgeButton.Enabled = parentEdgeId != null;

            var cancelButton = new Button { Text = "OK" };
            cancelButton.Click += (s, e) =>
            {
                RevertParentEdge = false;
                Result = false;
                Close();
            };

            DefaultButton = cancelButton;

            Content = new StackLayout
            {
                Spacing = 10,
                Items =
                {
                    message,
                    new StackLayoutItem(null, true),
                    new StackLayout
                    {
                        Orientation = Orientation.Horizontal,
                        Spacing = 5,
                        Items = { null, revertEdgeButton, cancelButton }
                    }
                }
            };
        }
    }
}
