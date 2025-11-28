# LATENT APPLICATION - SCREEN SIZE & DISPLAY REQUIREMENTS ANALYSIS
## Comprehensive Technical Specification
**Date**: November 15, 2025  
**Project**: Ceramic Mold Analyzer (Latent)  
**Framework**: PyQt6 6.9.1 + VTK 9.3.0

---

## EXECUTIVE SUMMARY

The Latent application has **dynamic scaling** with **minimum requirements of 1280x720** and **optimal operation at 1920x1080 or larger**. The application does **NOT use fixed pixel dimensions** but instead uses **percentage-based layouts and maximum/minimum constraints** for responsive design.

**Key Finding**: No explicit high-DPI awareness code detected. The application relies on PyQt6's native DPI handling through QScreen methods.

---

## 1. WINDOW SIZING SPECIFICATIONS

### 1.1 Primary Window Initialization

**File**: `main.py` (lines 137-143)

```python
# Dynamic sizing based on available screen
screen = QApplication.primaryScreen().availableGeometry()
width = int(screen.width() * 0.8)      # 80% of screen width
height = int(screen.height() * 0.8)    # 80% of screen height
x = (screen.width() - width) // 2      # Center horizontally
y = (screen.height() - height) // 2    # Center vertically
self.setGeometry(x, y, width, height)
```

**Behavior**:
- Window scales to **80% of available screen dimensions**
- Automatically centered on primary screen
- No fixed minimum enforced in code (relies on Qt default minimum)
- Respects system taskbars/menu bars via `availableGeometry()`

### 1.2 Minimum Window Size Requirement

**Source**: `docs/reference/UX_UI_DESIGN_SPECIFICATION.md` (line 230)

```
Minimum window size: 1280x720
Optimal size: 1920x1080 or larger
```

**Implications**:
- On 1280x720 screen → window occupies entire available area
- On 1920x1080 screen → window is 1536x864 (80%)
- On 2560x1440 screen → window is 2048x1152 (80%)
- On 1920x1200 (16:10) → window is 1536x960 (80%)

**Note**: The 1280x720 minimum is a specification requirement, NOT enforced in code. The application should set this via `setMinimumSize()` but currently doesn't.

---

## 2. PANEL LAYOUT & SIZING

### 2.1 Dock Widget Architecture

The application uses **5 dockable panels** arranged around a central viewport:

**File**: `main.py` (lines 448-521)

```
┌─────────────────────────────────────────────┐
│ Menu Bar                                    │
├─────────────────────────────────────────────┤
│ Edit Mode Toolbar  │  Analysis Toolbar      │
├─────────────────────────────────────────────┤
│                  │                           │
│    VIEWPORT      │   Right Dock Stack       │
│    (Primary)     │   ├─ Analysis            │
│    ~65-70%       │   ├─ Regions             │
│                  │   ├─ Constraints         │
│                  │   └─ Selection Info      │
│                  │   (~300px nominal)       │
│                  │                           │
├─────────────────────────────────────────────┤
│ Debug Console (Bottom Dock) ~150px height   │
└─────────────────────────────────────────────┘
```

### 2.2 Right Panel Stack Configuration

**Panel Stack Components**:
1. **Analysis Panel** (AnalysisPanel)
2. **Region List Panel** (RegionListWidget)
3. **Constraint Panel** (ConstraintPanel)
4. **Selection Info Panel** (SelectionInfoPanel)

**Stacking Method**: `tabifyDockWidget()`
- Panels occupy same horizontal space
- Tabbed interface for switching between panels
- All panels visible as tabs, one content area visible

**Width Constraints**:

| Panel | Max Width | Min Width | Notes |
|-------|-----------|-----------|-------|
| Constraint Panel | None specified | None specified | Column widths: 300px + 80px |
| Region List | None specified | None specified | Sort combo: 100px max |
| Analysis Panel | None specified | None specified | Histogram canvas: 4"×2" @100dpi |
| Selection Info | None specified | None specified | Indices list: 150px max height |

**Key Constraint Panel Specification** (lines 55-57):
```python
self.tree.setColumnWidth(0, 300)  # Description column
self.tree.setColumnWidth(1, 80)   # Severity column
# Total: 380px minimum width
```

### 2.3 Toolbar Sizing

**Edit Mode Toolbar** (`app/ui/edit_mode_toolbar.py`):
- Mode buttons: ~60px min-width each (× 4 buttons = 240px)
- Spacing and labels add ~100px
- Total estimated: 340-400px

**Analysis Toolbar** (`main.py`, lines 396-446):
- Labels and separators: ~50px
- 4 lens buttons: ~80px each = 320px
- Separator: ~10px
- "Generate Molds" button: ~120px
- "Send to Rhino" button: ~120px
- Total estimated: 620-700px

**Combined Toolbar Height**:
- Each toolbar: ~32px (with padding)
- Two toolbars: ~64px total
- Status bar: ~22px

---

## 3. DETAIL COMPONENT SIZING

### 3.1 Debug Console

**File**: `main.py` (lines 488-514)

```python
self.debug_console.setMaximumHeight(150)  # Line 495
```

**Dock Configuration**:
- Bottom position (`Qt.DockWidgetArea.BottomDockWidgetArea`)
- Fixed maximum height: **150px**
- Width: Full application width
- Contains: Read-only monospace text + test button
- Font: Monospace, 10px
- Background: Dark (#1E1E1E), light text (#D4D4D4)

### 3.2 Region List Widget

**File**: `app/ui/region_list_widget.py` (lines 24-102)

```python
self.pin_btn.setMaximumWidth(40)       # Line 75
self.sort_combo.setMaximumWidth(100)   # Line 58
```

**Component Widths**:
| Component | Width |
|-----------|-------|
| Pin button (📌) | 40px |
| Edit button (✏️) | 40px |
| Delete button (🗑️) | 40px |
| Sort dropdown | 100px |
| Filter input | Remaining (flexible) |

**Overall Region List Panel Width**: 
- Typical dock width: 250-350px
- Or expandable to fill if floating

### 3.3 Selection Info Panel

**File**: `app/ui/selection_info_panel.py` (line 58)

```python
self.indices_list.setMaximumHeight(150)  # Line 58
```

**Constraints**:
- List widget max height: 150px
- Width: Parent panel width (flexible)

### 3.4 Analysis Panel Histogram

**File**: `app/ui/analysis_panel.py` (lines 30-65)

```python
self.figure = Figure(figsize=(4, 2), dpi=100)  # Line 52
self.canvas.setMinimumHeight(150)              # Line 54
```

**Matplotlib Canvas Specifications**:
| Property | Value | Notes |
|----------|-------|-------|
| Figure Size (inches) | 4" × 2" | At 100 DPI |
| Canvas Minimum Height | 150px | ~1.5 inches |
| DPI | 100 | Fixed, not system DPI-aware |
| Canvas Size Policy | Expanding | Fills available space |

**Pixel Calculation at 100 DPI**:
- 4 inches × 100 DPI = 400px width
- 2 inches × 100 DPI = 200px height
- Rendered in 150px minimum container

### 3.5 Button and Control Sizing

**Styles** (`app/ui/styles.py`):

```python
# Padding: 8px vertical, 16px horizontal
padding: 8px 16px;

# Minimum width
min-width: 80px;

# Edit Mode Toolbar Buttons
min-width: 60px;
padding: 5px 10px;

# Tool buttons
padding: 4px;
border-radius: 3px;
```

---

## 4. VIEWPORT LAYOUT SPECIFICATIONS

### 4.1 Viewport Configuration Layouts

**File**: `app/ui/viewport_layout.py`

#### Single Viewport Layout
- Viewport size: 100% of central area
- Margin: 0px (full bleed)
- Spacing: 0px

#### Two Horizontal Layout
- Splitter orientation: Vertical (top/bottom split)
- Initial sizes: `[400, 400]` pixels
- Adjustable via splitter drag

#### Two Vertical Layout
- Splitter orientation: Horizontal (left/right split)
- Initial sizes: `[400, 400]` pixels
- Adjustable via splitter drag

#### Four Grid Layout (Default)
- Nested splitters: Vertical > Horizontal (2 levels)
- Initial sizes: `[400, 400]` per split
- Default viewport arrangement:
  ```
  ┌─────────────┬──────────────┐
  │  Top View   │ Perspective  │ (Top Split)
  ├─────────────┼──────────────┤
  │ Front View  │  Right View  │ (Bottom Split)
  └─────────────┴──────────────┘
  ```

**Minimum Viewport Size**:
- No explicit minimum set in code
- Four-grid layout with 400px splits = 800×800 minimum
- 1280×720 minimum window allows ~800×550 of usable viewport space

### 4.2 Viewport Content Area Calculation

For a **1280×720 window** with four-grid layout:

```
Window: 1280 × 720
├─ Menu bar: 22px
├─ Toolbars (2×): 64px  
├─ Viewport area: 720 - 22 - 64 - 22(status bar) ≈ 612px height
├─ Left panel (right dock): ~300px width
└─ Right area (viewport): 1280 - 22(margin) - 300 ≈ 958px width

Actual viewport space: ~958px × 612px = 585,696 px²
Per viewport (4-grid): ~239px × 306px = 73,134 px² each
```

For a **1920×1080 window** (optimal):

```
Window: 1920 × 1080
├─ Menu bar: 22px
├─ Toolbars (2×): 64px
├─ Viewport area: 1080 - 22 - 64 - 22 ≈ 972px height
├─ Left panel (right dock): ~300px width  
└─ Right area (viewport): 1920 - 22 - 300 ≈ 1598px width

Actual viewport space: ~1598px × 972px = 1,551,456 px²
Per viewport (4-grid): ~799px × 486px = 388,314 px² each
```

---

## 5. RESPONSIVE DESIGN PATTERNS

### 5.1 Dynamic Panel Sizing

**Characteristics**:
- ✅ Right panel stack is **dockable** - can float or resize
- ✅ Splitters are **draggable** - user can adjust viewport/panel ratio
- ✅ Panels use **flexible layouts** - no fixed widths (except constraints like 300px)
- ✅ Viewport fills **remaining space** - grows/shrinks with window

**NOT Responsive**:
- ❌ No breakpoints for window size changes
- ❌ No automatic panel hiding at small sizes
- ❌ No layout switching (e.g., stacking panels vertically on narrow windows)
- ❌ No mobile/tablet optimizations

### 5.2 Window Resizing Behavior

**How layout responds to window resize**:

| Action | Behavior |
|--------|----------|
| Resize window larger | Viewport expands, panels maintain ~300px width |
| Resize window smaller | Viewport shrinks, panels remain at dock width |
| Below 1280px width | Horizontal scroll or panel overlap likely |
| Below 720px height | Vertical scroll or clipping occurs |

### 5.3 Panel Management Features

**Collapsible Panels**:
- View → toggle visibility of each dock via menu
- Dock tabs can be reorganized by dragging
- Panels can be floated (undocked) as separate windows

**Layout Persistence**:
- Uses QSettings to save/restore layout
- File: Platform-specific settings storage
- Method: `save_layout()` / `restore_layout()` (lines 577-594)

**Reset Option**:
- Menu: View → Reset Panel Layout
- Restores default configuration

---

## 6. HIGH-DPI AND SCALING ANALYSIS

### 6.1 DPI Awareness Status

**Finding**: **NO explicit high-DPI support code detected**

Search for DPI-related code:
- ✅ Found: `matplotlib` Figure uses fixed `dpi=100`
- ✅ Found: VTK text scaling disabled (`SetTextScaleModeToNone()`)
- ❌ Not found: `devicePixelRatio()` calls
- ❌ Not found: `windowHandle().logicalDotsPerInch()`
- ❌ Not found: Scaling factor adjustments
- ❌ Not found: High-DPI pixmap loading

### 6.2 PyQt6 Native DPI Handling

PyQt6 **automatically handles DPI** through:

1. **QScreen Methods** (used in main.py):
   ```python
   screen = QApplication.primaryScreen().availableGeometry()
   # Returns geometry in logical pixels, not physical pixels
   # Qt automatically scales based on system DPI
   ```

2. **Automatic Scaling**:
   - macOS: Uses point-based coordinates (automatic)
   - Windows: Qt scales based on display DPI setting
   - Font sizes use logical pixels (auto-scaled)

3. **Potential Issues**:
   - Matplotlib figure at fixed 100 DPI may appear small on high-DPI displays
   - VTK rendering quality depends on native resolution (usually OK)
   - Text rendering uses system fonts (generally fine)

### 6.3 High-DPI Display Implications

**On Retina/High-DPI Displays** (e.g., MacBook Pro 13" 2560×1600):

| Property | Behavior |
|----------|----------|
| Physical pixels | Double or more than logical pixels |
| Window sizes | Specified in logical pixels (correct) |
| Font rendering | Automatic scaling (correct) |
| Icons/buttons | May appear slightly small |
| Matplotlib chart | ~100 DPI output (may look fuzzy) |
| VTK viewport | Full native resolution (correct) |

**Recommendation**: Add explicit high-DPI awareness for matplotlib:
```python
dpi = self.logicalDpiX()  # Get system DPI
self.figure = Figure(figsize=(4, 2), dpi=dpi)
```

---

## 7. MONITOR RESOLUTION COMPATIBILITY MATRIX

### 7.1 Common Resolutions and Behavior

| Resolution | 80% Window | Usable Viewport | Notes |
|------------|-----------|-----------------|-------|
| **1280×720** (HD) | 1024×576 | ~700×550 | Minimum spec - tight fit |
| **1366×768** (HD+) | 1092×614 | ~780×580 | Common laptop - adequate |
| **1440×900** (WXGA+) | 1152×720 | ~850×650 | Small laptop - good |
| **1600×900** (16:9) | 1280×720 | ~980×650 | Desktop - good |
| **1920×1080** (FHD) | 1536×864 | ~1200×800 | Optimal spec - good |
| **2560×1440** (QHD) | 2048×1152 | ~1740×1050 | Large monitor - excellent |
| **3440×1440** (Ultrawide) | 2752×1152 | ~2450×1050 | Ultrawide - excellent |

### 7.2 Problematic Resolutions

| Resolution | Issue | Impact |
|------------|-------|--------|
| **1024×768** (XGA) | 819×614 window < 1280 min | Horizontal scrolling needed |
| **1024×600** (WSVGA) | 819×480 window < 1280 min | Severe overflow |
| **640×480** (VGA) | 512×384 window | Unusable |

---

## 8. DISPLAY DEVICE COMPATIBILITY

### 8.1 Supported Configurations

**Explicitly Mentioned**:
- Single monitor setup (most common) ✅
- Dual monitor (viewport on one, controls on other) ✅ (via floating panels)
- High DPI/Retina displays ✅ (partial - automatic scaling, no explicit awareness)
- Different aspect ratios ✅ (responsive splitters)

**Source**: `docs/reference/UX_UI_DESIGN_SPECIFICATION.md` (lines 241-245)

### 8.2 Multi-Monitor Strategy

**Current Implementation**:
- Right panel can be **floated** as separate window
- Place on secondary monitor manually
- Each panel is independent (can float or dock)
- Viewport remains on primary monitor

**Not Implemented**:
- Automatic multi-monitor detection
- Preset layout for dual monitors
- Synchronized cameras across monitors

---

## 9. ELEMENT-BY-ELEMENT DIMENSION SUMMARY

### 9.1 Fixed Pixel Dimensions (EXACT)

| Element | Size | Location | Purpose |
|---------|------|----------|---------|
| Debug console max height | 150px | Bottom dock | Display logs |
| Constraint column widths | 300px + 80px | Right dock | Tree layout |
| Region sort combo width | 100px (max) | Region list | ComboBox |
| Region button widths | 40px (max) each | Region list | Pin/edit/delete |
| Selection indices max height | 150px | Right dock | List height |
| Matplotlib canvas height | 150px (min) | Analysis panel | Chart display |
| Edit mode button width | 60px (min) | Toolbar | Mode selector |
| Button padding | 8px (v), 16px (h) | UI buttons | Spacing |
| Toolbar button padding | 5px (v), 10px (h) | Toolbar | Spacing |
| Toolbar icon padding | 4px | Tool buttons | Spacing |

### 9.2 Percentage/Relative Dimensions

| Element | Percentage | Reference | Notes |
|---------|-----------|-----------|-------|
| Window width | 80% | Screen width | Initial size |
| Window height | 80% | Screen height | Initial size |
| Viewport space | 65-70% | Total width | Nominal ratio |
| Right panel | 30-35% | Total width | Nominal ratio |
| Splitter initial | 400px | N/A | Adjustable, not fixed |

### 9.3 Dynamic/Calculated Dimensions

| Element | Calculation | Notes |
|---------|-----------|-------|
| Window position | `(width-w)//2, (height-h)//2` | Centered on screen |
| Available height | Screen height - taskbar | Uses `availableGeometry()` |
| Viewport height | Total height - toolbars - status | Dynamic |
| Panel width in grid | ~window width × 0.30 | Adjustable via splitter |

---

## 10. PLATFORM-SPECIFIC CONSIDERATIONS

### 10.1 macOS (Primary Platform)

**Specifications**:
- PyQt6 with native macOS integration ✅
- Uses Cocoa widgets automatically
- Respects macOS menu bar (22px typically)
- High-DPI support via point-based coordinates ✅
- Retina display handling: Automatic scaling

**Tested Resolutions**:
- MacBook Air 13" (1440×900) ✅
- MacBook Pro 14" (3072×1920) - likely ✅
- iMac 24" (4480×2520) - untested

### 10.2 Windows (Future Support)

**Considerations**:
- Different taskbar behavior (bottom by default)
- DPI scaling settings may affect layout
- Window decoration size varies

### 10.3 Linux (Not Supported)

---

## 11. RECOMMENDATIONS FOR OPTIMIZATION

### 11.1 Minimum Size Enforcement

**Current Issue**: No `setMinimumSize()` call

**Recommendation**:
```python
# In MainWindow.__init__() or init_ui()
self.setMinimumSize(1280, 720)
```

### 11.2 High-DPI Awareness

**Current Issue**: Matplotlib uses fixed 100 DPI

**Recommendation**:
```python
# In CurvatureHistogramWidget.init_ui()
dpi = self.logicalDpiX()  # Get system DPI
self.figure = Figure(figsize=(4, 2), dpi=dpi)
```

### 11.3 Responsive Layout Breakpoints

**Recommendation** (for future enhancement):
```python
# Add responsive behavior for narrow windows
if self.width() < 1400:
    # Stack panels vertically instead of horizontally
    # Hide non-essential info
    # Adjust viewport layout to single view
```

### 11.4 Panel Width Configuration

**Current**: Dock panel widths are dynamic

**Consider**: Setting preferred width:
```python
self.analysis_dock.setPreferredWidth(300)
self.region_dock.setPreferredWidth(300)
```

---

## 12. SUMMARY TABLE: SCREEN REQUIREMENTS

### Absolute Minimums

| Requirement | Specification | Status |
|-------------|---------------|--------|
| Minimum window width | 1280px | Code: Not enforced |
| Minimum window height | 720px | Code: Not enforced |
| Initial window size | 80% × 80% of screen | Code: Enforced ✅ |

### Recommended

| Requirement | Specification | Target Use Case |
|-------------|---------------|-----------------|
| Optimal window | 1920×1080 | Full HD desktop |
| Large display | 2560×1440+ | QHD monitor |
| Dual monitor | 3840×1080+ | Split across monitors |

### Component Maximums

| Component | Max Size | Min Size |
|-----------|----------|----------|
| Debug console | 150px H | (no min) |
| Right panel | (no max) | (no min) |
| Viewport splitter | (no max) | 400px nominal |
| Matplotlib chart | (no max) | 150px H |

---

## 13. TESTING CHECKLIST

- [ ] Test on 1280×720 minimum resolution
- [ ] Test on 1920×1080 recommended resolution  
- [ ] Test on 2560×1440 high resolution
- [ ] Test Retina display (high DPI)
- [ ] Test dual monitor setup
- [ ] Test window resize operations
- [ ] Test panel floating/docking
- [ ] Test splitter drag operations
- [ ] Verify matplotlib chart rendering quality
- [ ] Verify UI text legibility at all sizes
- [ ] Test taskbar/menu bar interaction (macOS/Windows)

---

## CONCLUSION

The Latent application uses a **flexible, percentage-based layout** with **specific maximum constraints** for key UI elements. While the application successfully scales across different monitor sizes, it lacks explicit **minimum size enforcement** and **high-DPI awareness for non-VTK components**.

The specification requires **1280×720 minimum**, and the application should enforce this to prevent layout degradation on smaller screens. For optimal experience, **1920×1080 or larger** displays are recommended, particularly for 4-viewport grid layout.

