# Display & Screen Size Quick Reference
## Ceramic Mold Analyzer (Latent)

---

## MINIMUM vs OPTIMAL DISPLAY REQUIREMENTS

```
┌──────────────────────────────────────────────────────┐
│  MINIMUM (Specified)    │  OPTIMAL (Recommended)     │
├─────────────────────────┼────────────────────────────┤
│  1280 × 720 px          │  1920 × 1080 px            │
│  ~2.1 megapixels        │  ~2.1 megapixels           │
│  16:9 aspect ratio      │  16:9 aspect ratio         │
│  Tight fit              │  Comfortable working space │
└──────────────────────────────────────────────────────┘
```

---

## AUTOMATIC WINDOW SIZING

The application automatically sizes itself on launch:

```python
# Application starts at 80% of available screen
Window Width  = Available Screen Width × 0.80
Window Height = Available Screen Height × 0.80
```

**Examples**:

| Screen Size | Window Size |
|-------------|-------------|
| 1280×720   | 1024×576   |
| 1920×1080  | 1536×864   |
| 2560×1440  | 2048×1152  |
| 3440×1440  | 2752×1152  |

---

## INTERFACE LAYOUT BREAKDOWN

```
┌─────────────────────────────────────────────────────────────┐
│ MENU BAR (22px)                                             │
├─────────────────────────────────────────────────────────────┤
│ TOOLBAR 1: Edit Mode Selector (32px)                        │
├─────────────────────────────────────────────────────────────┤
│ TOOLBAR 2: Analysis Tools (32px)                            │
├─────────────────┬───────────────────────────────────────────┤
│                 │                                           │
│   VIEWPORT      │        RIGHT PANEL DOCK STACK            │
│   (~65-70%      │        ├─ Analysis Panel                  │
│    width)       │        ├─ Region List                     │
│                 │        ├─ Constraint Panel (300+80px min) │
│   4-Grid View   │        └─ Selection Info                  │
│   (default)     │        (~300px width, adjustable)         │
│                 │                                           │
│                 │                                           │
│                 │                                           │
├─────────────────┼───────────────────────────────────────────┤
│ DEBUG CONSOLE (Bottom Dock, 150px max height)               │
├─────────────────────────────────────────────────────────────┤
│ STATUS BAR (22px)                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## FIXED COMPONENT DIMENSIONS

### Console & List Widgets
- **Debug Console**: Maximum 150px height
- **Selection Info List**: Maximum 150px height
- **Matplotlib Chart Canvas**: Minimum 150px height

### Panel Column Widths
- **Constraint Panel, Column 1** (Description): 300px
- **Constraint Panel, Column 2** (Severity): 80px
- **Region Sort ComboBox**: Maximum 100px

### Button Sizes
- **Region List Buttons** (Pin/Edit/Delete): 40px max width each
- **Edit Mode Buttons**: 60px min width each
- **Standard Buttons**: Minimum 80px width

### Spacing & Padding
- **Button Padding**: 8px vertical, 16px horizontal
- **Toolbar Padding**: 5px vertical, 10px horizontal
- **Layout Margins**: 5px (panels), 0px (viewport)

---

## VIEWPORT LAYOUT MODES

The application supports 4 different viewport configurations:

### 1. Single View
```
┌──────────────────┐
│   Perspective    │
│     Viewport     │
│   (Full Size)    │
└──────────────────┘
```

### 2. Two Horizontal
```
┌──────────────────┐
│     Top View     │
├──────────────────┤
│  Bottom Viewport │
└──────────────────┘
```

### 3. Two Vertical
```
┌────────────┬─────────────┐
│   Front    │ Perspective │
│    View    │   View      │
└────────────┴─────────────┘
```

### 4. Four Grid (Default)
```
┌────────────┬──────────────┐
│ Top View   │ Perspective  │
├────────────┼──────────────┤
│ Front View │  Right View  │
└────────────┴──────────────┘
```

**Initial Split Size**: 400px per viewport (adjustable)

---

## RESPONSIVE BEHAVIOR

### What IS Responsive
✅ Viewport expands/shrinks with window  
✅ Panels are dockable and draggable  
✅ Splitters between panels are adjustable  
✅ Panels can be floated as separate windows  
✅ Layout can be saved/restored  

### What IS NOT Responsive
❌ No breakpoints for different window widths  
❌ No automatic layout switching for small screens  
❌ No panel hiding or collapsing at narrow widths  
❌ No mobile/tablet optimizations  

### How to Adapt for Small Screens
- Manually float panels to secondary monitor
- Use single viewport mode
- Resize/close optional panels via View menu
- Adjust splitter positions

---

## MONITOR COMPATIBILITY CHART

| Resolution | Window @ 80% | Viewport Size | Status |
|-----------|------------|--------------|--------|
| 1280×720 | 1024×576 | 700×550 | **Minimum (Tight)** |
| 1366×768 | 1092×614 | 780×580 | Common Laptop |
| 1440×900 | 1152×720 | 850×650 | Laptop |
| 1600×900 | 1280×720 | 980×650 | Desktop |
| 1920×1080 | 1536×864 | 1200×800 | **Optimal** ⭐ |
| 2560×1440 | 2048×1152 | 1740×1050 | High-res |
| 3440×1440 | 2752×1152 | 2450×1050 | Ultrawide |

---

## HIGH-DPI / RETINA DISPLAYS

### Current Behavior
- ✅ PyQt6 automatically scales window sizes
- ✅ Fonts and text scale correctly
- ✅ VTK viewport uses full native resolution
- ⚠️ Matplotlib charts use fixed 100 DPI (may appear fuzzy)

### Supported Display Densities
- Standard: 72-96 DPI (Windows/Linux standard)
- High DPI: 110-150 DPI (some Windows laptops)
- Retina: 200+ DPI (macOS Retina, iPhone-class displays)

### macOS Retina Display Support
- MacBook Air 13": 1440×900 logical, 2880×1800 physical ✅
- MacBook Pro 14": 3072×1920 logical ✅
- iMac 24": Likely supported ✅

---

## KEYBOARD SHORTCUTS (Viewport Navigation)

These match Rhino 8 standard controls:

```
RIGHT-DRAG            → Rotate/Orbit view
Shift + RIGHT-DRAG    → Pan view
Ctrl + RIGHT-DRAG     → Zoom in/out
Mouse Wheel          → Zoom in/out
LEFT-CLICK           → Select object (no camera move)
SPACE                → Reset camera to default
```

---

## TOTAL SCREEN FOOTPRINT AT DIFFERENT RESOLUTIONS

### At 1280×720 (Minimum)
```
┌─ Window: 1024×576
│  ├─ Menu/Toolbars/Status: ~108px vertical
│  ├─ Viewport area: ~467px height
│  ├─ Viewport width: ~700px (left side)
│  ├─ Right panel: ~300px width
│  └─ Each viewport in 4-grid: ~239×306px
│
└─ Result: Tight fit, adequate for basic work
```

### At 1920×1080 (Optimal)
```
┌─ Window: 1536×864
│  ├─ Menu/Toolbars/Status: ~108px vertical
│  ├─ Viewport area: ~755px height
│  ├─ Viewport width: ~1200px (left side)
│  ├─ Right panel: ~300px width
│  └─ Each viewport in 4-grid: ~600×378px
│
└─ Result: Comfortable working space, good proportions
```

---

## PANEL FLOATING STRATEGY (Multi-Monitor)

For dual-monitor setups, you can:

1. **Right-click panel tab** → Select "Float"
2. **Drag tab** to secondary monitor
3. **Resize panel** to desired width
4. **Right-click → Dock** to reattach when done

**Panels that can float**:
- Analysis Panel ✅
- Region List Panel ✅
- Constraint Panel ✅
- Selection Info Panel ✅
- Debug Console ✅

---

## CALIBRATION CHECKLIST

Before production use, verify:

- [ ] Window opens at correct size (80% of screen)
- [ ] Viewport displays without black borders
- [ ] All toolbar buttons visible
- [ ] Right panel tabs are accessible
- [ ] Debug console appears at bottom
- [ ] Text is legible (not too small)
- [ ] Splitters can be dragged
- [ ] Panels can be docked/floated
- [ ] Status bar visible at bottom

---

## TROUBLESHOOTING COMMON ISSUES

### Issue: Interface too small on high-DPI display
**Solution**: Matplotlib charts appear at 100 DPI regardless of system DPI. Use PyQt6's DPI scaling (automatic on macOS).

### Issue: Panels disappear or overlap
**Solution**: Use View menu → Reset Panel Layout to restore default positions

### Issue: Viewport is too small
**Solution**: Drag right panel border to make viewport wider, or float panels to secondary monitor

### Issue: Debug console takes up too much space
**Solution**: Click View → Debug Console to hide it, or drag bottom splitter up

### Issue: Can't see buttons in toolbar
**Solution**: Increase window width or right-click toolbar to customize visibility

---

## SPECIFICATIONS REFERENCE

**Framework**: PyQt6 6.9.1  
**3D Engine**: VTK 9.3.0  
**Charting**: Matplotlib (for histograms)  
**Platform**: macOS 12+ (Windows future support)  

**Design Philosophy**: 
> Flexible, responsive layout that prioritizes the 3D viewport while keeping analysis controls accessible and non-intrusive.

---

**Document Version**: 1.0  
**Last Updated**: November 15, 2025  
**Status**: Current and Accurate ✅
