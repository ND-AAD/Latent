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
    /// Sort criteria for the geometry list.
    /// </summary>
    public enum GeometrySortBy
    {
        Id,
        State,
        Score
    }

    /// <summary>
    /// Panel that displays geometry elements (vertices, edges, regions) with
    /// state indicators, pin/unpin, and revert controls.
    /// </summary>
    [System.Runtime.InteropServices.Guid("A1B2C3D4-E5F6-7890-ABCD-EF1234567890")]
    public class GeometryListPanel : Panel, IPanel
    {
        private readonly DropDown _modeSelector;
        private readonly TextBox _filterTextBox;
        private readonly DropDown _sortSelector;
        private readonly GridView _gridView;
        private readonly Button _pinButton;
        private readonly Button _revertButton;
        private readonly Button _pinSelectedButton;
        private readonly Label _statusLabel;

        private RegionManager? _regionManager;
        private GeometryListMode _currentMode = GeometryListMode.Regions;
        private GeometrySortBy _sortBy = GeometrySortBy.Id;
        private bool _sortAscending = true;
        private string _filterText = "";
        private List<GeometryListItem> _allItems = new();
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

            // Filter text box
            _filterTextBox = new TextBox
            {
                PlaceholderText = "Filter by ID...",
                Width = 120
            };
            _filterTextBox.TextChanged += OnFilterChanged;

            // Sort selector
            _sortSelector = new DropDown();
            _sortSelector.Items.Add("ID ↑");
            _sortSelector.Items.Add("ID ↓");
            _sortSelector.Items.Add("State ↑");
            _sortSelector.Items.Add("State ↓");
            _sortSelector.Items.Add("Score ↑");
            _sortSelector.Items.Add("Score ↓");
            _sortSelector.SelectedIndex = 0;
            _sortSelector.SelectedIndexChanged += OnSortChanged;

            // Grid view with multi-selection enabled
            _gridView = new GridView
            {
                AllowMultipleSelection = true,
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

            // Batch operation button for multi-selection
            _pinSelectedButton = new Button { Text = "📌 Pin Selected", Enabled = false };
            _pinSelectedButton.Click += OnPinSelectedClicked;

            // Status label
            _statusLabel = new Label
            {
                Text = "Select geometry to see options",
                TextColor = Colors.Gray
            };

            // Top toolbar layout
            var toolbarLayout = new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items =
                {
                    _modeSelector,
                    _filterTextBox,
                    _sortSelector
                }
            };

            // Button layout
            var buttonLayout = new StackLayout
            {
                Orientation = Orientation.Horizontal,
                Spacing = 5,
                Items = { _pinButton, _revertButton, _pinSelectedButton }
            };

            Content = new StackLayout
            {
                Padding = new Padding(5),
                Spacing = 5,
                Items =
                {
                    toolbarLayout,
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

        private void OnFilterChanged(object? sender, EventArgs e)
        {
            _filterText = _filterTextBox.Text ?? "";
            ApplyFilterAndSort();
        }

        private void OnSortChanged(object? sender, EventArgs e)
        {
            // Parse sort selector: 0=ID↑, 1=ID↓, 2=State↑, 3=State↓, 4=Score↑, 5=Score↓
            var index = _sortSelector.SelectedIndex;
            _sortBy = (index / 2) switch
            {
                0 => GeometrySortBy.Id,
                1 => GeometrySortBy.State,
                2 => GeometrySortBy.Score,
                _ => GeometrySortBy.Id
            };
            _sortAscending = (index % 2) == 0;
            ApplyFilterAndSort();
        }

        private void OnPinSelectedClicked(object? sender, EventArgs e)
        {
            if (_regionManager == null) return;

            var selectedItems = _gridView.SelectedItems.Cast<GeometryListItem>().ToList();
            if (selectedItems.Count == 0) return;

            // Determine if we should pin or unpin based on majority state
            int pinnedCount = selectedItems.Count(i => i.IsPinned);
            bool shouldPin = pinnedCount < selectedItems.Count / 2.0;

            foreach (var item in selectedItems)
            {
                _regionManager.SetPinned(item.Id, shouldPin);
            }

            _pinSelectedButton.Text = shouldPin ? "📍 Unpin Selected" : "📌 Pin Selected";
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
                    case Latent.Geometry.Region:
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

                case Latent.Geometry.Region region:
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
                var dialog = new CurveModificationVertexDialog(vertex.Id, vertex.ParentEdgeId);
                if (dialog.ShowModal(this) && dialog.RevertParentEdge && vertex.ParentEdgeId != null)
                {
                    // Revert the parent edge's curve type
                    _regionManager.RevertEdgeCurveType(vertex.ParentEdgeId);
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
                _allItems = new List<GeometryListItem>();
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

            _allItems = elements.Select(e => new GeometryListItem(e)).ToList();
            ApplyFilterAndSort();
        }

        private void ApplyFilterAndSort()
        {
            // Apply filter
            IEnumerable<GeometryListItem> filtered = _allItems;
            if (!string.IsNullOrWhiteSpace(_filterText))
            {
                var lowerFilter = _filterText.ToLowerInvariant();
                filtered = filtered.Where(i =>
                    i.Id.ToLowerInvariant().Contains(lowerFilter) ||
                    i.State.ToLowerInvariant().Contains(lowerFilter) ||
                    i.Details.ToLowerInvariant().Contains(lowerFilter)
                );
            }

            // Apply sort
            filtered = _sortBy switch
            {
                GeometrySortBy.Id => _sortAscending
                    ? filtered.OrderBy(i => i.Id)
                    : filtered.OrderByDescending(i => i.Id),
                GeometrySortBy.State => _sortAscending
                    ? filtered.OrderBy(i => i.State)
                    : filtered.OrderByDescending(i => i.State),
                GeometrySortBy.Score => _sortAscending
                    ? filtered.OrderBy(i => GetSortScore(i))
                    : filtered.OrderByDescending(i => GetSortScore(i)),
                _ => filtered.OrderBy(i => i.Id)
            };

            _items = filtered.ToList();
            _gridView.DataStore = _items;

            UpdateStatusLabel(null);
        }

        private double GetSortScore(GeometryListItem item)
        {
            // Extract numeric score from details for sorting
            if (item.Element is Latent.Geometry.Region r)
                return r.ResonanceScore;
            if (item.Element is Edge e)
                return e.Degree;
            return 0;
        }

        private void UpdateButtonStates(GeometryListItem? item)
        {
            // Update single-item buttons
            if (item == null)
            {
                _pinButton.Enabled = false;
                _revertButton.Enabled = false;
            }
            else
            {
                _pinButton.Enabled = true;
                _pinButton.Text = item.IsPinned ? "📍 Unpin" : "📌 Pin";
                _revertButton.Enabled = item.CanRevert && !item.IsPinned;
            }

            // Update multi-selection button
            var selectedCount = _gridView.SelectedItems.Count();
            _pinSelectedButton.Enabled = selectedCount > 1;
            if (selectedCount > 1)
            {
                var selectedItems = _gridView.SelectedItems.Cast<GeometryListItem>().ToList();
                int pinnedCount = selectedItems.Count(i => i.IsPinned);
                _pinSelectedButton.Text = pinnedCount > selectedCount / 2
                    ? $"📍 Unpin {selectedCount}"
                    : $"📌 Pin {selectedCount}";
            }
            else
            {
                _pinSelectedButton.Text = "📌 Pin Selected";
            }
        }

        private void UpdateStatusLabel(GeometryListItem? item)
        {
            if (item == null)
            {
                int totalCount = _allItems.Count;
                int filteredCount = _items.Count;
                int pinned = _items.Count(i => i.IsPinned);

                if (filteredCount < totalCount)
                {
                    _statusLabel.Text = $"{filteredCount}/{totalCount} {_currentMode} ({pinned} pinned)";
                }
                else
                {
                    _statusLabel.Text = $"{filteredCount} {_currentMode} ({pinned} pinned)";
                }
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
                _gridView.SelectRow(_items.IndexOf(newItem));
            }
        }

        #endregion
    }
}
