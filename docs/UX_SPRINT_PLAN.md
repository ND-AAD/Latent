# UX Migration Sprint Plan

**Goal**: Align PyQt6 desktop application with React prototype in `docs/reference/UX/`
**Duration**: 5 Days
**Structure**: Parallel agent workstreams with daily consolidation

---

## Sprint Overview

### Parallel Workstreams (5 Tracks)

| Track | Focus Area | Files | Dependencies |
|-------|-----------|-------|--------------|
| **A** | Top Bar + Primary Actions | `app/ui/top_bar.py` (new), `main.py` | None |
| **B** | Right Panel Redesign | `app/ui/right_panel.py` (new) | None |
| **C** | Viewport Enhancements | `app/ui/viewport_layout.py`, `app/ui/viewport_3d.py` | None |
| **D** | Bottom Panel Restructure | `app/ui/bottom_panel.py` (new) | None |
| **E** | Left Panel + Styling | `app/ui/left_panels.py` (new), `app/ui/styles.py` | Track A (Day 2+) |

### Daily Cadence

| Time | Activity |
|------|----------|
| Morning | Parallel development (Agents 1-5) |
| Midday | Quick sync check (no merge) |
| Afternoon | Continue development |
| End of Day | Consolidation Agent merges + tests |

---

## Day 1: Foundation Components

### Morning Session (Parallel)

**Agent 1 - Track A: TopBar Component**
```
Create: app/ui/top_bar.py

Classes:
- TopBar(QWidget): Main top bar container
- PrimaryActionsBar(QWidget): Tab-specific action buttons
- SettingsDropdown(QWidget): Settings gear menu

Must implement:
- 6 tab-specific action configurations (FILE, ANALYZE, EDIT, VALIDATE, FABRICATE, VIEW)
- ActionButton and ToggleButton helper classes
- Settings dropdown with: Theme toggle, Units selectors, Tolerance selector

Reference: docs/reference/UX/src/components/TopBar.tsx
```

**Agent 2 - Track B: RightPanel Foundation**
```
Create: app/ui/right_panel.py

Classes:
- RightPanel(QWidget): Main container with vertical icon tabs
- VerticalIconTabBar(QWidget): Left-edge icon tab strip
- TabButton(QPushButton): Icon button with active state

Must implement:
- 5 icon tabs: Viewport, Regions, Constraints, Selection, Parameters
- Active tab indicator (left blue border)
- Tab switching mechanism

Reference: docs/reference/UX/src/components/RightPanel.tsx (lines 1-97)
```

**Agent 3 - Track C: Viewport Splitters**
```
Modify: app/ui/viewport_layout.py

Must implement:
- Change default from SINGLE to FOUR_GRID
- Add draggable splitter handles with hover highlight (blue)
- Track splitter positions as percentages
- Center intersection handle for 4-grid simultaneous adjustment

Reference: docs/reference/UX/src/components/Viewport.tsx (lines 147-282)
```

**Agent 4 - Track D: BottomPanel Component**
```
Create: app/ui/bottom_panel.py

Classes:
- BottomPanel(QWidget): Main container
- ConnectionStatus(QWidget): Rhino connection indicator
- CommandInput(QWidget): Command line with ">" prefix
- SystemStatus(QWidget): Activity + memory display
- DebugConsole(QWidget): Collapsible console

Must implement:
- Collapsible debug console with toggle button
- Proper layout: Connection(140px) | Command(flex) | Status(128px) | Toggle(48px)

Reference: docs/reference/UX/src/components/BottomPanel.tsx
```

**Agent 5 - Track E: Style System**
```
Create: app/ui/styles.py (expand existing)

Must define:
- Color palette constants (LIGHT_THEME, DARK_THEME)
- Button styles: primary_button(), secondary_button(), toggle_button(), sidebar_button()
- Panel styles: panel_style(), section_header_style()
- Common dimensions: SIDEBAR_WIDTH, RIGHT_PANEL_WIDTH, BOTTOM_PANEL_HEIGHT

Apply to: Global QApplication stylesheet
```

### End of Day 1: Consolidation

**Consolidation Agent**
```
1. Pull all Track A-E changes
2. Verify no file conflicts
3. Run: python3 launch.py (smoke test - should launch without crash)
4. Create integration branch checkpoint
5. Document any interface mismatches
```

**Checkpoint Criteria:**
- [ ] Application launches without error
- [ ] TopBar component imports successfully
- [ ] RightPanel component imports successfully
- [ ] BottomPanel component imports successfully
- [ ] Viewport shows 4-grid by default

---

## Day 2: Integration + Panel Content

### Morning Session (Parallel)

**Agent 1 - Track A: MainWindow Integration**
```
Modify: main.py

Must implement:
- Replace create_tab_widget() to use new TopBar
- Wire TopBar tab changes to content switching
- Wire TopBar actions to existing methods
- Remove primary actions from left panels (they move to TopBar)

Integration points:
- TopBar.tab_changed -> MainWindow.on_tab_changed
- TopBar.action_triggered -> MainWindow.{method}
```

**Agent 2 - Track B: RightPanel Content - Viewport & Regions**
```
Modify: app/ui/right_panel.py

Add panel content:
- ViewportPanel: Layout dropdown, Shading mode, Display options checkboxes, Camera sync, Background color
- RegionsPanel: Search input, Sort dropdown, Region list with items, Selected region properties

Must implement:
- PanelSection helper class with collapsible support
- PropertyRow helper for key-value display
- RegionItem with color indicator, name, unity type, action icons

Reference: docs/reference/UX/src/components/RightPanel.tsx (lines 99-230)
```

**Agent 3 - Track C: Viewport Double-Click + Labels**
```
Modify: app/ui/viewport_layout.py, app/ui/viewport_3d.py

Must implement:
- Double-click on viewport to maximize (single view)
- Double-click again to restore (4-grid)
- Track maximized state
- View labels: Grey background badge in top-left corner
- Axis indicator: X(red), Y(green), Z(blue) in bottom-left

Reference: docs/reference/UX/src/components/Viewport.tsx (lines 284-339)
```

**Agent 4 - Track D: BottomPanel Integration**
```
Modify: main.py

Must implement:
- Replace create_bottom_panel() to use new BottomPanel
- Wire debug console to existing log_debug() method
- Connect connection status to LiveBridge
- Connect command input to execute_command()

Move from main.py to BottomPanel:
- debug_console
- command_input
- status_widget
```

**Agent 5 - Track E: Left Panel Cleanup**
```
Create: app/ui/left_panels.py

Must implement:
- LeftSidebar(QWidget): Container that shows tab-specific content
- FileTools, AnalyzeTools, EditTools, ValidateTools, FabricateTools, ViewTools classes
- SidebarButton: Full-width, left-aligned, proper hover states
- Expandable sections (Export Settings, Camera Properties)
- "ADVANCED TOOLS" header with icon

Remove from existing left panels: Primary actions (now in TopBar)

Reference: docs/reference/UX/src/components/LeftSidebar.tsx
```

### End of Day 2: Consolidation + Testing

**Consolidation Agent**
```
1. Merge all Track changes
2. Run comprehensive tests:
   - python3 launch.py
   - Click through all 6 tabs
   - Verify TopBar actions appear correctly per tab
   - Verify RightPanel switches tabs
   - Verify Viewport is 4-grid with labels
   - Test double-click maximize
   - Test debug console collapse/expand
3. Fix any integration issues
4. Update PROJECT_STATUS.md
```

**Checkpoint Criteria:**
- [ ] All 6 tabs show correct TopBar actions
- [ ] RightPanel shows 5 icon tabs
- [ ] Viewport shows 4-grid with view labels
- [ ] Double-click maximize works
- [ ] Debug console collapses/expands
- [ ] Left panels show only advanced tools

---

## Day 3: Complete Panel Content + Polish

### Morning Session (Parallel)

**Agent 1 - Track B: RightPanel Content - Constraints & Selection**
```
Modify: app/ui/right_panel.py

Add panel content:
- ConstraintsPanel: Overall status card, Errors section (collapsible), Warnings section, Features section
- ConstraintItem: Title, description, severity indicator, Quick Fix button
- SelectionPanel: Current mode badge, Selection count, Statistics, Selected indices (copyable)

Reference: docs/reference/UX/src/components/RightPanel.tsx (lines 232-363)
```

**Agent 2 - Track B: RightPanel Content - Parameters**
```
Modify: app/ui/right_panel.py

Add panel content:
- ParametersPanel: Resolution dropdown, Min region size, Colormap selector
- Auto-range checkbox
- Value range min/max inputs
- Histogram placeholder

Reference: docs/reference/UX/src/components/RightPanel.tsx (lines 365-443)
```

**Agent 3 - Track C: Viewport Grid Overlay + Styling**
```
Modify: app/ui/viewport_3d.py

Must implement:
- Grid overlay (subtle lines, adjustable spacing)
- Proper background color (dark: #1a1a1a, light: #f5f5f5)
- Border styling for viewport panels
- Active viewport highlight

Reference: docs/reference/UX/src/components/Viewport.tsx (lines 284-339)
```

**Agent 4 - Track A: Settings Dropdown**
```
Modify: app/ui/top_bar.py

Must implement complete SettingsDropdown:
- View Mode: Light/Dark toggle buttons
- Length Units: Dropdown (mm, cm, m, fractional, decimal-in, decimal-ft)
- Mass Units: Dropdown (mg, g, kg, oz, lb)
- Volume Units: Dropdown (ml, L, m³, fl oz, cup, gal, ft³)
- Tolerance: Dropdown (0.1, 0.01, 0.001, 0.0001, 0.00001)
- Close button

Wire to ApplicationState for persistence.
```

**Agent 5 - Track E: Theme Implementation**
```
Modify: app/ui/styles.py, main.py

Must implement:
- Dark theme color palette
- Theme switching function
- Apply theme to all components
- Persist theme preference in QSettings

Test: Toggle between light/dark in Settings dropdown
```

### End of Day 3: Consolidation + Full Testing

**Consolidation Agent**
```
1. Merge all changes
2. Full application test:
   - Launch application
   - Navigate all tabs, verify actions
   - Test all RightPanel tabs and content
   - Test viewport interactions (splitters, maximize, labels)
   - Test Settings dropdown (theme, units)
   - Test debug console
3. Visual comparison with React prototype screenshots
4. Document remaining gaps
```

**Checkpoint Criteria:**
- [ ] All RightPanel content matches prototype
- [ ] Settings dropdown fully functional
- [ ] Theme switching works
- [ ] Viewport styling matches prototype
- [ ] No visual regressions

---

## Day 4: Wire Functionality + Edge Cases

### Morning Session (Parallel)

**Agent 1 - Wire TopBar Actions**
```
Modify: main.py, app/ui/top_bar.py

Wire all TopBar actions to functionality:
- FILE: New/Open/Save session, Import/Export Rhino
- ANALYZE: Lens buttons -> run_analysis()
- EDIT: Mode toggles -> edit_mode_manager, Selection operations
- VALIDATE: Constraint check -> constraint validation
- FABRICATE: Generate molds, Export
- VIEW: Reset cameras, Frame geometry, Show/hide toggles
```

**Agent 2 - Wire RightPanel Data**
```
Modify: main.py, app/ui/right_panel.py

Wire RightPanel to live data:
- ViewportPanel: Layout change -> viewport_layout.set_layout()
- RegionsPanel: Display from state.regions, handle selection/pin
- ConstraintsPanel: Display from constraint_panel.constraints
- SelectionPanel: Display from edit_mode_manager selection
- ParametersPanel: Wire to analysis settings
```

**Agent 3 - Viewport Edge Cases**
```
Modify: app/ui/viewport_layout.py

Handle edge cases:
- Splitter minimum sizes (10% per pane)
- Maximize/restore preserves splitter positions
- Geometry display updates in all viewports
- Camera reset per view type
- Handle window resize gracefully
```

**Agent 4 - BottomPanel Edge Cases**
```
Modify: app/ui/bottom_panel.py

Handle edge cases:
- Command history (up/down arrows)
- Auto-scroll console
- Memory usage periodic update
- Connection reconnect handling
- Console size limits (max lines)
```

**Agent 5 - Left Panel Edge Cases**
```
Modify: app/ui/left_panels.py

Handle edge cases:
- Disabled button styling
- Expandable section state persistence
- Scroll for long tool lists
- Tool availability based on state (e.g., no geometry loaded)
```

### End of Day 4: Integration Testing

**Consolidation Agent**
```
1. Merge all changes
2. Integration tests:
   - Load geometry from Rhino (if available)
   - Run analysis, verify regions appear in RightPanel
   - Select regions, verify SelectionPanel updates
   - Run validation, verify ConstraintsPanel updates
   - Test all TopBar actions trigger correct behavior
3. Edge case testing:
   - Resize window to minimum
   - Rapidly switch tabs
   - Double-click maximize while geometry loaded
4. Performance check (no lag)
```

**Checkpoint Criteria:**
- [ ] All actions trigger correct functionality
- [ ] RightPanel displays live data
- [ ] No crashes on edge cases
- [ ] Responsive performance

---

## Day 5: Polish + Documentation

### Morning Session (Parallel)

**Agent 1 - Visual Polish Pass**
```
Review and fix:
- Spacing consistency (8px standard)
- Font sizes match prototype (xs=11px, sm=12px)
- Border colors and radiuses
- Hover state timings
- Focus indicators
```

**Agent 2 - Accessibility + Keyboard**
```
Implement:
- Tab order through all controls
- Keyboard shortcuts display in tooltips
- F1-F6 for tab switching (verify)
- Escape to clear selection
- Enter in command input
```

**Agent 3 - Error Handling**
```
Add:
- Graceful degradation if no geometry
- Clear error messages in console
- Disabled states for unavailable actions
- Loading states for long operations
```

**Agent 4 - Documentation Update**
```
Update:
- docs/PROJECT_STATUS.md - UX section
- docs/UX_GUIDE.md - Implementation notes
- CLAUDE.md - Any new conventions
```

**Agent 5 - Final Testing**
```
Create: tests/test_ui_integration.py

Test scenarios:
- Application launch
- Tab navigation
- Viewport layout switching
- Settings persistence
- Theme switching
- Geometry display (mock data)
```

### End of Day 5: Final Consolidation

**Consolidation Agent**
```
1. Final merge
2. Complete test suite run
3. Visual comparison checklist (screenshot comparison)
4. Update PROJECT_STATUS.md with completion status
5. Create PR summary
```

**Final Acceptance Criteria:**
- [ ] Visual match with React prototype (90%+)
- [ ] All interactions functional
- [ ] No console errors
- [ ] Tests pass
- [ ] Documentation updated

---

## File Ownership Matrix

Prevents merge conflicts by assigning exclusive ownership:

| File | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 |
|------|-------|-------|-------|-------|-------|
| `app/ui/top_bar.py` | Agent 1 | Agent 1 | Agent 4 | Agent 1 | Agent 1 |
| `app/ui/right_panel.py` | Agent 2 | Agent 2 | Agent 1,2 | Agent 2 | Agent 2 |
| `app/ui/viewport_layout.py` | Agent 3 | Agent 3 | - | Agent 3 | - |
| `app/ui/viewport_3d.py` | - | Agent 3 | Agent 3 | - | - |
| `app/ui/bottom_panel.py` | Agent 4 | Agent 4 | - | Agent 4 | - |
| `app/ui/left_panels.py` | - | Agent 5 | - | Agent 5 | - |
| `app/ui/styles.py` | Agent 5 | - | Agent 5 | - | Agent 1 |
| `main.py` | - | Agent 1,4 | - | Agent 1,2 | - |

---

## Slash Commands for Sprint

Create these in `.claude/commands/`:

### `/launch-ux-day1-morning`
Launch Agents 1-5 for Day 1 morning session

### `/consolidate-ux-day1`
Run Day 1 consolidation checks

### `/launch-ux-day2-morning`
Launch Agents 1-5 for Day 2 morning session

(Continue pattern for Days 2-5)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Merge conflicts | File ownership matrix, daily consolidation |
| Integration breaks | Checkpoint criteria, smoke tests |
| Visual mismatches | Screenshot comparison at each checkpoint |
| Performance regression | Performance check at Day 4 |
| Missing functionality | Wire functionality explicitly on Day 4 |

---

## Success Metrics

1. **Visual Fidelity**: Side-by-side comparison with React prototype scores 90%+
2. **Functionality**: All existing features still work
3. **Performance**: No noticeable lag in UI interactions
4. **Code Quality**: No new linting errors, consistent style
5. **Test Coverage**: UI integration tests pass

---

## Post-Sprint

After UX sprint completion:
1. Update `docs/PROJECT_STATUS.md` to reflect completed UX migration
2. Archive this sprint plan to `.Archive/`
3. Begin Backend Testing Sprint (separate plan)
