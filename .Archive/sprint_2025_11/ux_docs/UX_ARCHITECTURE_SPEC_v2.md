# Latent UX Architecture Specification v2.0

**Living Document - Last Updated: November 2025**

## Executive Summary

This document defines the comprehensive UX architecture for Latent, a desktop application for discovering mathematical decompositions of SubD surfaces to create slip-casting ceramic molds. The interface follows a **four-sided, tab-based architecture** inspired by professional CAD applications like Rhino, but refined for clarity and workflow efficiency.

## Core Design Principles

### 1. Four-Sided Cognitive Geography
- **TOP**: Primary actions for active workflow (changes with tab)
- **LEFT**: Secondary/advanced actions for active workflow (changes with tab)
- **RIGHT**: Display properties and data (persistent, context-aware)
- **BOTTOM**: System communication and history (persistent)

### 2. Hierarchical Tool Organization
- **TOP = "I want to do X"** (primary actions everyone needs)
- **LEFT = "I want to do X in a special way"** (advanced/specialized actions)
- **RIGHT = "How do I see/configure it?"** (display and parameters)
- **BOTTOM = "What's happening?"** (system state and feedback)

### 3. Modal vs Persistent
- **Modal Elements** (TOP/LEFT): Change based on active tab
- **Persistent Elements** (RIGHT/BOTTOM): Always available, context-aware

### 4. Growth Pattern
- TOP remains stable as features are added (primary interface consistency)
- LEFT expands over time with advanced features
- New functionality goes LEFT, not TOP (unless it's primary to workflow)

---

## Tab Architecture

### TAB 1: FILE
**Purpose**: Standard file operations and session management

**TOP (Primary File Operations)**
- New Session
- Open Session
- Save Session
- Save As
- Import from Rhino
- Export to Rhino

**LEFT (Advanced File Operations)**
- Save Template
- Load Template
- Recent Files (with thumbnails)
- Export Analysis Report
- Export Validation Report
- Batch Export
- Auto-save Settings (future)
- Version History (future)
- Cloud Sync (future)

---

### TAB 2: ANALYZE
**Purpose**: Mathematical analysis and region discovery

**TOP (Primary Analysis Actions)**
- Run Curvature Analysis (button with icon)
- Run Spectral Analysis (button with icon)
- Run Flow Analysis (button with icon)
- Run Topological Analysis (button with icon)
- Analyze Button (large, primary action)
- Stop Analysis (appears during analysis)

**LEFT (Secondary Analysis Actions)**
- Compare Analyses (overlay multiple results)
- Differential Analysis (between two states)
- Batch Analysis (multiple lenses at once)
- Analysis History Timeline
- Save Analysis Preset
- Load Analysis Preset
- Custom Analysis Scripts (future)
- ML-Based Region Suggestion (future)

---

### TAB 3: EDIT
**Purpose**: Region manipulation and selection operations

**TOP (Primary Editing)**
- Mode Selector (Solid/Panel/Edge/Vertex) - toggle group
- Select All (Ctrl+A)
- Clear Selection (Esc)
- Invert Selection (Ctrl+I)
- Pin/Unpin Region (toggle button)
- Delete Region

**LEFT (Secondary Editing)**
- Grow Selection (Ctrl+>)
- Shrink Selection (Ctrl+<)
- Edit Boundary (manual adjustment)
- Export Selection to Region
- Merge Regions
- Split Regions
- Pin All Regions
- Unpin All Regions
- Batch Region Operations
- Selection Filters (future)

---

### TAB 4: VALIDATE
**Purpose**: Constraint checking and manufacturing validation

**TOP (Primary Validation)**
- Run Constraint Check
- Show All Errors (filter toggle)
- Show All Warnings (filter toggle)
- Show Features (filter toggle)
- Clear Validation
- Re-validate All

**LEFT (Secondary Validation - Fixes)**
- Fix Undercuts (interactive)
- Adjust Pull Direction
- Auto-Fix Draft Angles
- Adjust Wall Thickness
- Repair Seam Gaps
- Custom Constraint Editor
- Tolerance Overrides
- Exemption Manager
- Validation Profiles (future)

---

### TAB 5: FABRICATE
**Purpose**: Mold generation and casting preparation

**TOP (Primary Fabrication)**
- Generate Mold Shells
- Add Registration Keys
- Add Band Grooves
- Add Pour Spouts
- Calculate Slip Volume
- Export for 3D Printing

**LEFT (Advanced Fabrication)**
- Custom Key Profiles
- Optimize Seam Placement
- Add Part Numbers/Labels
- Generate Assembly Diagram
- Multi-pour Strategy
- Drying Time Calculator
- Add Witness Marks
- Mold Weight Calculator
- Generate Casting Instructions
- QC Checklist Generator (future)
- Kiln Schedule Generator (future)

---

### TAB 6: VIEW
**Purpose**: Viewport and display control

**TOP (Primary View Controls)**
- Reset All Views (home icon)
- Reset Current View
- Frame All Geometry
- Frame Selected
- Show/Hide Axes (toggle)
- Show/Hide Grid (toggle)

**LEFT (Advanced View Controls)**
- Save Named View
- Restore Named View (dropdown)
- Lock Camera (toggle)
- Camera Properties Dialog
- Reset Panel Layout
- Toggle Full Screen (F11)
- Section Planes (future)
- Display Modes (future)
- Turntable Animation (future)

---

## Right Panel Architecture

### Persistent Vertical Tabs

#### VIEWPORT Tab
**Purpose**: Interface and display properties

**Contents**:
- Layout Selector
  - Single Viewport
  - Two Horizontal
  - Two Vertical
  - Four Grid
- Shading Mode
  - Wireframe
  - Shaded
  - Rendered
  - X-Ray (future)
- Edge Display (on/off)
- Background Color (color picker)
- Grid Settings
  - Show Grid (checkbox)
  - Grid Spacing (numeric)
  - Grid Snap (checkbox)
- Camera Sync Options
  - Sync All Cameras
  - Independent Cameras
- Material Preview (on/off)
- Lighting Settings (future)

#### REGIONS Tab
**Purpose**: Region management and properties

**Contents**:
- Header: "Regions: N (M pinned)"
- Search/Filter Bar
- Sort Dropdown (Name/Unity/Pinned First)
- Region List (scrollable)
  - Color-coded items (green/yellow/orange/red)
  - Pin icon for pinned items
  - Unity principle text
  - Strength badge
- Selected Region Properties (expandable)
  - Name (editable)
  - Unity Principle
  - Unity Strength (progress bar)
  - Face Count
  - Modified Status
  - Constraints Status
- Action Buttons
  - Properties Dialog
  - Export to JSON

#### CONSTRAINTS Tab
**Purpose**: Validation results and issues

**Contents**:
- Summary Header
  - "N Errors, M Warnings"
  - Overall Status Icon
- Error Section (red, expandable)
  - Undercut violations
  - Trapped volumes
  - Inaccessible surfaces
- Warning Section (yellow, expandable)
  - Insufficient draft
  - Wall thickness issues
  - Seam gaps
- Feature Section (blue, expandable)
  - Manual edits
  - User overrides
- Each item shows:
  - Description
  - Severity (0.0-1.0)
  - Affected faces
  - Quick Fix button (when available)

#### SELECTION Tab
**Purpose**: Current selection information

**Contents**:
- Current Mode Display
  - Mode icon and name
  - Selection count
- Selected Items
  - Faces: N
  - Edges: N
  - Vertices: N
- Selected Indices (scrollable monospace list)
- Statistics
  - Total Area (mm²)
  - Total Length (mm)
  - Bounding Box
- Actions
  - Copy Indices
  - Export Selection

#### PARAMETERS Tab (Context-Sensitive)
**Purpose**: Active tool parameters

**When in ANALYZE**:
- Resolution (Low/Medium/High/Ultra)
- Min Region Size (Tiny/Small/Medium/Large)
- Colormap (dropdown)
- Auto-range (checkbox)
- Min/Max Values (numeric)
- Histogram Display

**When in VALIDATE**:
- Draft Angle Threshold
- Min Wall Thickness
- Max Wall Thickness
- Seam Gap Tolerance
- Custom Rules

**When in FABRICATE**:
- Mold Wall Thickness
- Key Type and Size
- Band Groove Dimensions
- Pour Spout Diameter
- Surface Finish

---

## Bottom Panel Architecture

### Persistent System Area

**Layout (left to right)**:

1. **Command Input** (30% width)
   - Command palette with autocomplete
   - History navigation with up/down arrows
   - ">" prompt indicator

2. **Command History** (40% width)
   - Scrollable history of executed commands
   - Success/error indicators
   - Timestamp for each command
   - Clear history button

3. **Connection Status** (15% width)
   - Rhino connection indicator (●)
   - "Connected" / "Disconnected" text
   - Live sync status
   - Reconnect button

4. **System Status** (15% width)
   - Progress bar (when active)
   - Current operation text
   - Cancel button (when applicable)
   - Memory usage indicator

5. **Debug Console** (collapsible drawer)
   - Toggle button to show/hide
   - Dark theme (VS Code style)
   - Monospace font
   - Error/Warning/Info filtering
   - Clear console button
   - Export log button

---

## Screen Space Allocation

### Dynamic Window Sizing
- **Window size**: 90vw × 90vh (90% of viewport)
- **Minimum window**: 1280px × 720px
- **Maximum width**: 2400px
- **Aspect ratio**: Flexible, adapts to screen

### Responsive Breakpoints

**Compact Mode (<1400px width)**:
- Left toolbar: 160px (icons + condensed text)
- Right panel: 240px
- Bottom panel: 100px
- Hides section headers in left bar when <1280px
- Tool buttons show icons only when <1280px

**Standard Mode (1400-1600px width)**:
- Left toolbar: 180px
- Right panel: 250px
- Bottom panel: 110px
- Full text labels visible

**Medium Mode (1600-2000px width)**:
- Left toolbar: 220px
- Right panel: 320px
- Bottom panel: 130px
- More comfortable spacing

**Large Mode (2000-2560px width)**:
- Left toolbar: 250px
- Right panel: 400px
- Bottom panel: 140px
- Expanded content areas

**4K Mode (>2560px width)**:
- Left toolbar: 280px
- Right panel: 450px
- Bottom panel: 160px
- Maximum comfort and readability

### Component Constraints

**Left Bar**:
- Minimum: 160px
- Maximum: 280px
- Collapsed: 60px

**Right Panel**:
- Minimum: 240px
- Maximum: 450px

**Bottom Panel**:
- Minimum: 100px
- Maximum: 160px

### Responsive Typography

Font sizes scale with viewport using CSS clamp():
- **Base font**: 10-12px
- **Small font**: 9-11px
- **Large font**: 12-14px
- **XLarge font**: 14-18px
- **Huge numbers**: 24-32px

---

## Keyboard Shortcuts

### Global Shortcuts
- **Ctrl+Z/Ctrl+Shift+Z**: Undo/Redo
- **F1-F6**: Switch tabs (File/Analyze/Edit/Validate/Fabricate/View)
- **F7**: Toggle focus mode (hide all panels)
- **F11**: Full screen
- **Esc**: Clear selection / Cancel operation

### Tab-Specific Shortcuts
- **Tab 1-6**: Quick switch between tabs
- **Ctrl+1-5**: Expand specific right panel section
- **Ctrl+0**: Collapse all right panels
- **Space**: Reset camera (in viewport)

### Mode Shortcuts (Edit Tab)
- **S**: Solid mode
- **P**: Panel mode
- **E**: Edge mode
- **V**: Vertex mode

---

## Visual Design Guidelines

### Color Palette
**Primary Actions**: #007AFF (iOS blue)
**Success**: #34C759 (green)
**Warning**: #FF9500 (orange)
**Error**: #FF3B30 (red)
**Background**: #FFFFFF (white)
**Panel Background**: #F5F5F5 (light gray)
**Borders**: #D1D1D6 (gray)
**Text**: #000000 (primary), #8E8E93 (secondary)

### Typography
**Headers**: System font, 12px, bold
**Body**: System font, 11px, regular
**Monospace**: SF Mono / Consolas, 10px
**Small text**: System font, 10px

### Spacing
- Panel padding: 8px
- Section spacing: 16px
- Button spacing: 8px
- List item height: 28px

### Icons
- Size: 16×16px (standard), 24×24px (primary actions)
- Style: Outlined for inactive, filled for active
- Color: Inherit from text color, primary color when active

---

## Implementation Priority

### Phase 1: Core Architecture (Week 1)
1. Implement tab system
2. Create four-sided layout
3. Basic tool placement
4. Collapsible right panels

### Phase 2: Functionality (Week 2)
1. Connect all existing tools
2. Command palette
3. Keyboard shortcuts
4. Responsive breakpoints

### Phase 3: Polish (Week 3)
1. Visual refinement
2. Animation and transitions
3. Preference persistence
4. Help system

---

## Future Considerations

### Planned Enhancements
- Customizable toolbar layouts
- Workspace presets
- Plugin architecture for custom tools
- Multi-language support
- Collaborative features
- Cloud integration

### Accessibility
- High contrast mode
- Keyboard-only navigation
- Screen reader support
- Adjustable UI scaling

---

## Version History

- **v2.1** (Nov 2024): Added responsive design with 5 breakpoints and dynamic sizing
- **v2.0** (Nov 2024): Complete redesign with four-sided, tab-based architecture
- **v1.0** (Oct 2024): Initial single-panel design

---

## Notes

This is a living document that will evolve as Latent develops. The architecture is designed to accommodate growth while maintaining consistency and usability. The primary interface (TOP tools) should remain stable across versions, with new features added to the LEFT secondary area.