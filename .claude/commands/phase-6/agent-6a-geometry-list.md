# Agent 6A: Geometry List Panel

## Objective

Implement an Eto.Forms panel that displays vertices, edges, and regions with state indicators, pin/unpin controls, and revert functionality.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `rhino_plugin/Geometry/IGeometryElement.cs` - common interface (Id, IsPinned, IsImplicit, CanRevert)
- `rhino_plugin/Geometry/Vertex.cs` - vertex with CreatedBy, CanRevert logic
- `rhino_plugin/Geometry/Edge.cs` - edge with CurveType, RevertCurveType()
- `rhino_plugin/Geometry/RegionManager.cs` - state management with Changed event
- `app/ui/region_list_widget.py` - Python reference implementation to port

## Files to Create

1. `rhino_plugin/UI/GeometryListItem.cs` - list item adapter
2. `rhino_plugin/UI/EdgeRevertDialog.cs` - edge revert options dialog
3. `rhino_plugin/UI/GeometryListPanel.cs` - main panel
4. `rhino_plugin/Tests/GeometryListPanelTests.cs` - unit tests

## Files to Modify

1. `rhino_plugin/LatentPlugin.cs` - register panel

## Tasks

### 1. Create GeometryListItem.cs

```csharp
// rhino_plugin/UI/GeometryListItem.cs
using System;
using Latent.Geometry;

namespace Latent.UI
{
    /// <summary>
    /// Display mode for the geometry list.
    /// </summary>
    public enum GeometryListMode
    {
        Regions,
        Edges,
        Vertices
    }

    /// <summary>
    /// Adapter for displaying geometry elements in a grid view.
    /// Wraps IGeometryElement with display-friendly properties.
    /// </summary>
    public class GeometryListItem
    {
        private readonly IGeometryElement _element;

        public GeometryListItem(IGeometryElement element)
        {
            _element = element ?? throw new ArgumentNullException(nameof(element));
        }

        /// <summary>
        /// The underlying geometry element.
        /// </summary>
        public IGeometryElement Element => _element;

        /// <summary>
        /// Element ID for display.
        /// </summary>
        public string Id => _element.Id;

        /// <summary>
        /// Whether the element is pinned.
        /// </summary>
        public bool IsPinned
        {
            get => _element.IsPinned;
            set => _element.IsPinned = value;
        }

        /// <summary>
        /// State string for display: "implicit", "explicit", or "pinned".
        /// </summary>
        public string State
        {
            get
            {
                if (IsPinned) return "📌 pinned";
                if (_element.IsImplicit) return "implicit";
                return "explicit";
            }
        }

        /// <summary>
        /// Whether revert is available.
        /// </summary>
        public bool CanRevert => _element.CanRevert;

        /// <summary>
        /// Additional info based on element type.
        /// </summary>
        public string Details
        {
            get
            {
                return _element switch
                {
                    Vertex v => $"Origin: {v.CreatedBy}",
                    Edge e => $"{e.CurveType} °{e.Degree}",
                    Region r => $"Score: {r.ResonanceScore:F2}",
                    _ => ""
                };
            }
        }

        /// <summary>
        /// Tooltip with full element information.
        /// </summary>
        public string Tooltip
        {
            get
            {
                return _element switch
                {
                    Vertex v => $"Vertex {v.Id}\nOrigin: {v.CreatedBy}\nImplicit: {v.IsImplicit}\nPinned: {v.IsPinned}",
                    Edge e => $"Edge {e.Id}\nType: {e.CurveType} degree {e.Degree}\nVertices: {e.VertexIds.Count}\nPinned: {e.IsPinned}",
                    Region r => $"Region {r.Id}\nPrinciple: {r.UnityPrinciple}\nResonance: {r.ResonanceScore:F3}\nEdges: {r.BoundaryEdgeIds.Count}",
                    _ => ""
                };
            }
        }

        /// <summary>
        /// Get the element type name.
        /// </summary>
        public string TypeName
        {
            get
            {
                return _element switch
                {
                    Vertex => "Vertex",
                    Edge => "Edge",
                    Region => "Region",
                    _ => "Unknown"
                };
            }
        }

        /// <summary>
        /// For vertices created by curve modification, get the parent edge ID.
        /// </summary>
        public string? ParentEdgeId
        {
            get
            {
                if (_element is Vertex v && v.CreatedBy == VertexOrigin.CurveModification)
                {
                    // TODO: Track parent edge relationship
                    return null;
                }
                return null;
            }
        }
    }
}
```

### 2. Create EdgeRevertDialog.cs

```csharp
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
```

### 3. Create GeometryListPanel.cs

```csharp
// rhino_plugin/UI/GeometryListPanel.cs
using System;
using System.Collections.Generic;
using System.Linq;
using Eto.Forms;
using Eto.Drawing;
using Rhino;
using Rhino.UI;
using Latent.Geometry;

namespace Latent.UI
{
    /// <summary>
    /// Panel that displays geometry elements (vertices, edges, regions) with
    /// state indicators, pin/unpin, and revert controls.
    /// </summary>
    [System.Runtime.InteropServices.Guid("A1B2C3D4-E5F6-7890-ABCD-EF1234567890")]
    public class GeometryListPanel : Panel, IPanel
    {
        private readonly DropDown _modeSelector;
        private readonly GridView _gridView;
        private readonly Button _pinButton;
        private readonly Button _revertButton;
        private readonly Label _statusLabel;

        private RegionManager? _regionManager;
        private GeometryListMode _currentMode = GeometryListMode.Regions;
        private List<GeometryListItem> _items = new();

        public static Guid PanelId => typeof(GeometryListPanel).GUID;

        public GeometryListPanel()
        {
            // Mode selector
            _modeSelector = new DropDown();
            _modeSelector.Items.Add("Regions");
            _modeSelector.Items.Add("Edges");
            _modeSelector.Items.Add("Vertices");
            _modeSelector.SelectedIndex = 0;
            _modeSelector.SelectedIndexChanged += OnModeChanged;

            // Grid view
            _gridView = new GridView
            {
                AllowMultipleSelection = false,
                ShowHeader = true
            };

            _gridView.Columns.Add(new GridColumn
            {
                HeaderText = "ID",
                DataCell = new TextBoxCell { Binding = Binding.Property<GeometryListItem, string>(i => i.Id) },
                Width = 80
            });

            _gridView.Columns.Add(new GridColumn
            {
                HeaderText = "State",
                DataCell = new TextBoxCell { Binding = Binding.Property<GeometryListItem, string>(i => i.State) },
                Width = 80
            });

            _gridView.Columns.Add(new GridColumn
            {
                HeaderText = "Details",
                DataCell = new TextBoxCell { Binding = Binding.Property<GeometryListItem, string>(i => i.Details) },
                Width = 100
            });

            _gridView.SelectionChanged += OnSelectionChanged;
            _gridView.CellDoubleClick += OnCellDoubleClick;

            // Action buttons
            _pinButton = new Button { Text = "📌 Pin", Enabled = false };
            _pinButton.Click += OnPinClicked;

            _revertButton = new Button { Text = "↩ Revert", Enabled = false };
            _revertButton.Click += OnRevertClicked;

            // Status label
            _statusLabel = new Label
            {
                Text = "Select geometry to see options",
                TextColor = Colors.Gray
            };

            // Layout
            var buttonLayout = new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items = { _pinButton, _revertButton }
            };

            Content = new StackLayout
            {
                Padding = new Padding(5),
                Spacing = 5,
                Items =
                {
                    _modeSelector,
                    new StackLayoutItem(_gridView, true),
                    buttonLayout,
                    _statusLabel
                }
            };

            // Subscribe to RegionManager when available
            SubscribeToRegionManager();
        }

        #region IPanel Implementation

        public void PanelShown(uint documentSerialNumber, ShowPanelReason reason)
        {
            SubscribeToRegionManager();
            RefreshList();
        }

        public void PanelHidden(uint documentSerialNumber, ShowPanelReason reason)
        {
            // Optionally unsubscribe to reduce overhead
        }

        public void PanelClosing(uint documentSerialNumber, bool onCloseDocument)
        {
            UnsubscribeFromRegionManager();
        }

        #endregion

        #region RegionManager Integration

        private void SubscribeToRegionManager()
        {
            UnsubscribeFromRegionManager();

            _regionManager = LatentPlugin.Instance?.RegionManager;
            if (_regionManager != null)
            {
                _regionManager.Changed += OnRegionManagerChanged;
            }
        }

        private void UnsubscribeFromRegionManager()
        {
            if (_regionManager != null)
            {
                _regionManager.Changed -= OnRegionManagerChanged;
                _regionManager = null;
            }
        }

        private void OnRegionManagerChanged(object? sender, EventArgs e)
        {
            // Marshal to UI thread
            Application.Instance.Invoke(RefreshList);
        }

        #endregion

        #region Event Handlers

        private void OnModeChanged(object? sender, EventArgs e)
        {
            _currentMode = _modeSelector.SelectedIndex switch
            {
                0 => GeometryListMode.Regions,
                1 => GeometryListMode.Edges,
                2 => GeometryListMode.Vertices,
                _ => GeometryListMode.Regions
            };
            RefreshList();
        }

        private void OnSelectionChanged(object? sender, EventArgs e)
        {
            var selectedItem = _gridView.SelectedItem as GeometryListItem;
            UpdateButtonStates(selectedItem);
            UpdateStatusLabel(selectedItem);

            // Sync selection to RegionManager
            if (selectedItem != null && _regionManager != null)
            {
                switch (selectedItem.Element)
                {
                    case Vertex:
                        _regionManager.SelectVertex(selectedItem.Id);
                        break;
                    case Edge:
                        _regionManager.SelectEdge(selectedItem.Id);
                        break;
                    case Region:
                        _regionManager.SelectRegion(selectedItem.Id);
                        break;
                }

                // Redraw viewports
                RhinoDoc.ActiveDoc?.Views.Redraw();
            }
        }

        private void OnCellDoubleClick(object? sender, GridCellMouseEventArgs e)
        {
            // Double-click to toggle pin state
            var item = e.Item as GeometryListItem;
            if (item != null)
            {
                TogglePin(item);
            }
        }

        private void OnPinClicked(object? sender, EventArgs e)
        {
            var selectedItem = _gridView.SelectedItem as GeometryListItem;
            if (selectedItem != null)
            {
                TogglePin(selectedItem);
            }
        }

        private void OnRevertClicked(object? sender, EventArgs e)
        {
            var selectedItem = _gridView.SelectedItem as GeometryListItem;
            if (selectedItem == null || _regionManager == null)
                return;

            // Check preconditions
            if (selectedItem.IsPinned)
            {
                MessageBox.Show(
                    "Unpin the element before reverting.",
                    "Cannot Revert",
                    MessageBoxButtons.OK,
                    MessageBoxType.Information
                );
                return;
            }

            // Handle based on element type
            switch (selectedItem.Element)
            {
                case Vertex v:
                    HandleVertexRevert(v);
                    break;

                case Edge edge:
                    HandleEdgeRevert(edge);
                    break;

                case Region region:
                    _regionManager.Revert(region.Id);
                    break;
            }

            RefreshList();
        }

        #endregion

        #region Revert Handlers

        private void HandleVertexRevert(Vertex vertex)
        {
            if (_regionManager == null) return;

            // Check if vertex was created by curve modification
            if (vertex.CreatedBy == VertexOrigin.CurveModification)
            {
                var dialog = new CurveModificationVertexDialog(vertex.Id, null);
                if (dialog.ShowModal(this) && dialog.RevertParentEdge)
                {
                    // TODO: Find and revert parent edge
                    RhinoApp.WriteLine("Parent edge revert not yet implemented");
                }
                return;
            }

            // Normal vertex revert
            if (vertex.CanRevert)
            {
                _regionManager.Revert(vertex.Id);
            }
        }

        private void HandleEdgeRevert(Edge edge)
        {
            if (_regionManager == null) return;

            var dialog = new EdgeRevertDialog();
            if (dialog.ShowModal(this))
            {
                if (dialog.RevertCurveTypeOnly)
                {
                    _regionManager.RevertEdgeCurveType(edge.Id);
                }
                else
                {
                    _regionManager.RevertEdgeFully(edge.Id);
                }
            }
        }

        #endregion

        #region UI Updates

        private void RefreshList()
        {
            if (_regionManager == null)
            {
                _items = new List<GeometryListItem>();
                _gridView.DataStore = _items;
                return;
            }

            IEnumerable<IGeometryElement> elements = _currentMode switch
            {
                GeometryListMode.Regions => _regionManager.Regions.Cast<IGeometryElement>(),
                GeometryListMode.Edges => _regionManager.Edges.Cast<IGeometryElement>(),
                GeometryListMode.Vertices => _regionManager.Vertices.Cast<IGeometryElement>(),
                _ => Enumerable.Empty<IGeometryElement>()
            };

            _items = elements.Select(e => new GeometryListItem(e)).ToList();
            _gridView.DataStore = _items;

            UpdateStatusLabel(null);
        }

        private void UpdateButtonStates(GeometryListItem? item)
        {
            if (item == null)
            {
                _pinButton.Enabled = false;
                _revertButton.Enabled = false;
                return;
            }

            _pinButton.Enabled = true;
            _pinButton.Text = item.IsPinned ? "📍 Unpin" : "📌 Pin";

            _revertButton.Enabled = item.CanRevert && !item.IsPinned;
        }

        private void UpdateStatusLabel(GeometryListItem? item)
        {
            if (item == null)
            {
                int count = _items.Count;
                int pinned = _items.Count(i => i.IsPinned);
                _statusLabel.Text = $"{count} {_currentMode} ({pinned} pinned)";
            }
            else
            {
                _statusLabel.Text = item.Tooltip.Replace("\n", " | ");
            }
        }

        private void TogglePin(GeometryListItem item)
        {
            if (_regionManager == null) return;

            _regionManager.SetPinned(item.Id, !item.IsPinned);
            RefreshList();

            // Re-select the item
            var newItem = _items.FirstOrDefault(i => i.Id == item.Id);
            if (newItem != null)
            {
                _gridView.SelectedItem = newItem;
            }
        }

        #endregion
    }
}
```

### 4. Create Unit Tests

```csharp
// rhino_plugin/Tests/GeometryListPanelTests.cs
using System.Collections.Generic;
using NUnit.Framework;
using Latent.Geometry;
using Latent.UI;
using Latent.Interop;

namespace Latent.Tests
{
    [TestFixture]
    public class GeometryListItemTests
    {
        [Test]
        public void State_WhenImplicit_ReturnsImplicit()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.State, Is.EqualTo("implicit"));
        }

        [Test]
        public void State_WhenExplicit_ReturnsExplicit()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var movedPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", movedPos, originalPos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.State, Is.EqualTo("explicit"));
        }

        [Test]
        public void State_WhenPinned_ReturnsPinned()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos);
            vertex.IsPinned = true;

            var item = new GeometryListItem(vertex);

            Assert.That(item.State, Contains.Substring("pinned"));
        }

        [Test]
        public void CanRevert_WhenPinned_ReturnsFalse()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var movedPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", movedPos, originalPos);
            vertex.IsPinned = true;

            var item = new GeometryListItem(vertex);

            Assert.That(item.CanRevert, Is.False);
        }

        [Test]
        public void CanRevert_WhenExplicitAndNotPinned_ReturnsTrue()
        {
            var originalPos = new ParametricPoint(0, 0.5, 0.5);
            var movedPos = new ParametricPoint(0, 0.6, 0.5);
            var vertex = new Vertex("v1", movedPos, originalPos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.CanRevert, Is.True);
        }

        [Test]
        public void Details_ForVertex_ShowsOrigin()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos, pos, VertexOrigin.Lens);

            var item = new GeometryListItem(vertex);

            Assert.That(item.Details, Contains.Substring("Lens"));
        }

        [Test]
        public void Details_ForEdge_ShowsCurveType()
        {
            var edge = new Edge("e1", new List<string> { "v1", "v2" },
                CurveType.Bezier, 3);

            var item = new GeometryListItem(edge);

            Assert.That(item.Details, Contains.Substring("Bezier"));
            Assert.That(item.Details, Contains.Substring("3"));
        }

        [Test]
        public void Details_ForRegion_ShowsResonanceScore()
        {
            var region = new Region("r1", new List<string> { "e1" },
                "High curvature", 0.85);

            var item = new GeometryListItem(region);

            Assert.That(item.Details, Contains.Substring("0.85"));
        }

        [Test]
        public void TypeName_ReturnsCorrectType()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("v1", pos);
            var edge = new Edge("e1", new List<string>());
            var region = new Region("r1", new List<string>(), "test", 0.5);

            Assert.That(new GeometryListItem(vertex).TypeName, Is.EqualTo("Vertex"));
            Assert.That(new GeometryListItem(edge).TypeName, Is.EqualTo("Edge"));
            Assert.That(new GeometryListItem(region).TypeName, Is.EqualTo("Region"));
        }

        [Test]
        public void Id_MatchesElementId()
        {
            var pos = new ParametricPoint(0, 0.5, 0.5);
            var vertex = new Vertex("test-vertex-123", pos);

            var item = new GeometryListItem(vertex);

            Assert.That(item.Id, Is.EqualTo("test-vertex-123"));
        }
    }

    [TestFixture]
    public class GeometryListModeTests
    {
        [Test]
        public void Mode_HasExpectedValues()
        {
            Assert.That(GeometryListMode.Regions, Is.EqualTo((GeometryListMode)0));
            Assert.That(GeometryListMode.Edges, Is.EqualTo((GeometryListMode)1));
            Assert.That(GeometryListMode.Vertices, Is.EqualTo((GeometryListMode)2));
        }
    }
}
```

### 5. Update LatentPlugin.cs for Panel Registration

Add this to the `OnLoad` method in `LatentPlugin.cs`:

```csharp
// Add to rhino_plugin/LatentPlugin.cs in OnLoad method, after other initialization

// Register UI panels
Rhino.UI.Panels.RegisterPanel(
    this,
    typeof(UI.GeometryListPanel),
    "Latent Geometry",
    System.Drawing.SystemIcons.Application.ToBitmap()
);
```

## Success Criteria

- [ ] `GeometryListItem` correctly wraps all element types
- [ ] Panel shows correct items for each mode (Region/Edge/Vertex)
- [ ] State column shows "implicit", "explicit", or "📌 pinned"
- [ ] Pin button toggles pin state
- [ ] Revert button is disabled when pinned
- [ ] Revert button shows EdgeRevertDialog for edges
- [ ] Revert button shows CurveModificationVertexDialog for curve-modified vertices
- [ ] Selection syncs to RegionManager
- [ ] Panel updates when RegionManager.Changed fires
- [ ] All unit tests pass

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run tests
dotnet test --filter "FullyQualifiedName~GeometryListItem|FullyQualifiedName~GeometryListMode"

# Verify files exist
ls UI/GeometryListPanel.cs
ls UI/GeometryListItem.cs
ls UI/EdgeRevertDialog.cs
```

## Do Not Modify

- Files in `Geometry/` (Phase 3 domain)
- Files in `Display/` (Phase 4 domain)
- Files in `Interaction/` (Phase 5 domain)
- `UI/LensPanel.cs` (Agent 6B's domain)
- `UI/VisualizationPanel.cs` (Agent 6C's domain)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests before reporting

## Notes

- Use `Application.Instance.Invoke()` to marshal UI updates from background threads
- `IPanel` interface is required for Rhino panel lifecycle
- Panel GUID must be unique and consistent
- Python `region_list_widget.py` provides reference for filter/sort features (optional enhancement)

## Report

When complete, provide:
1. Build output showing no errors
2. Test output showing all tests pass
3. Screenshot description of panel layout
4. Any edge cases discovered
