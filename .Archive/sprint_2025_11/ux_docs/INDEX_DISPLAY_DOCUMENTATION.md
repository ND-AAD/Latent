# Display & Screen Size Documentation Index

## Quick Navigation

**Need a quick answer?** Jump to:
- Minimum/Optimal sizes? → [DISPLAY_QUICK_REFERENCE.md](DISPLAY_QUICK_REFERENCE.md#minimum-vs-optimal-display-requirements)
- Visual layout? → [DISPLAY_DIAGRAMS.txt](DISPLAY_DIAGRAMS.txt)
- Specific component size? → [SCREEN_SIZE_DISPLAY_ANALYSIS.md](SCREEN_SIZE_DISPLAY_ANALYSIS.md#9-element-by-element-dimension-summary)
- Testing checklist? → [DISPLAY_QUICK_REFERENCE.md](DISPLAY_QUICK_REFERENCE.md#calibration-checklist)

---

## Document Overview

### 1. README_DISPLAY_ANALYSIS.md
**Start here for navigation and overview**

- Index of all documents
- Key findings summary  
- How to use this documentation
- Critical specifications checklist
- Recommended improvements
- File locations in codebase

**Best for**: Orientation, quick reference

---

### 2. SCREEN_SIZE_DISPLAY_ANALYSIS.md
**Complete technical specification**

**13 Sections covering:**

1. Window Sizing Specifications
   - Primary window initialization logic
   - Minimum window size requirements
   - Dynamic 80% screen scaling formula

2. Panel Layout & Sizing
   - Dock widget architecture diagram
   - Right panel stack configuration
   - Toolbar sizing specifications

3. Detail Component Sizing
   - Debug console (150px max)
   - Region list widgets (40px buttons)
   - Selection info panel
   - Matplotlib canvas specifications
   - Button and control sizing

4. Viewport Layout Specifications
   - Single, 2H, 2V, 4-grid modes
   - Viewport content area calculations
   - Minimum viewport sizes

5. Responsive Design Patterns
   - What is and isn't responsive
   - Window resizing behavior
   - Panel management features

6. High-DPI and Scaling Analysis
   - DPI awareness status
   - PyQt6 native DPI handling
   - High-DPI display implications

7. Monitor Resolution Compatibility Matrix
   - Common resolutions and behavior
   - Problematic resolutions

8. Display Device Compatibility
   - Single monitor setup
   - Dual monitor setup
   - High DPI/Retina displays

9. Element-by-Element Dimension Summary
   - Fixed pixel dimensions (exact)
   - Percentage/relative dimensions
   - Dynamic/calculated dimensions

10. Platform-Specific Considerations
    - macOS specifications
    - Windows future support
    - Linux not supported

11. Recommendations for Optimization
    - Minimum size enforcement
    - High-DPI awareness
    - Responsive layout breakpoints
    - Panel width configuration

12. Summary Table: Screen Requirements
    - Absolute minimums
    - Recommended specifications
    - Component maximums

13. Testing Checklist
    - Resolution testing checklist
    - Display testing requirements

**Best for**: Developers, technical reference, detailed specifications

---

### 3. DISPLAY_QUICK_REFERENCE.md
**Quick lookup guide**

**Sections:**

1. Minimum vs Optimal Requirements
   - 1280×720 minimum
   - 1920×1080 optimal
   - Aspect ratio specifications

2. Automatic Window Sizing
   - 80% of screen formula
   - Examples for common resolutions

3. Interface Layout Breakdown
   - ASCII diagram of full interface
   - Menu bar, toolbars, viewport, panels
   - All dimensions labeled

4. Fixed Component Dimensions
   - Console & list widget sizes
   - Panel column widths
   - Button sizes
   - Spacing & padding table

5. Viewport Layout Modes
   - Single view
   - Two horizontal
   - Two vertical
   - Four grid (default)

6. Responsive Behavior
   - What is responsive
   - What is not responsive
   - How to adapt for small screens

7. Monitor Compatibility Chart
   - Resolution vs window size vs status
   - Common resolutions listed

8. High-DPI / Retina Displays
   - Current behavior
   - Supported densities
   - macOS Retina support

9. Keyboard Shortcuts
   - Viewport navigation controls

10. Total Screen Footprint
    - At 1280×720 minimum
    - At 1920×1080 optimal

11. Panel Floating Strategy
    - Multi-monitor setup instructions
    - Panels that can float

12. Calibration Checklist
    - Pre-production verification steps

13. Troubleshooting
    - Common issues and solutions

14. Specifications Reference
    - Framework and platform info

**Best for**: Quick lookup, designers, testers

---

### 4. DISPLAY_DIAGRAMS.txt
**Visual ASCII diagrams**

**10 Diagrams:**

1. Full application window structure
   - All UI elements with dimensions
   - At 1920×1080 optimal resolution
   - Exact pixel measurements labeled

2. Viewport layout modes
   - Single, 2H, 2V, 4-grid visuals
   - Percentage allocation shown

3. Right panel dock stack
   - Tabbed interface diagram
   - Shows all 4 panels
   - Tab switching example

4. Component sizing reference
   - Button and control sizes table
   - Padding and spacing table
   - Fixed heights reference

5. Screen real estate allocation
   - At 1920×1080 optimal
   - Pixel count breakdown
   - Percentage allocation

6. Minimum configuration (1280×720)
   - Layout at minimum spec
   - Warnings about tight fit

7. DPI scaling (Retina example)
   - MacBook Pro 14" example
   - Physical vs logical pixels
   - Scaling factor explanation

8. Panel docking relationships
   - Default single-monitor setup
   - Dual-monitor setup
   - Floating panels shown

9. Responsive behavior tree
   - Decision tree for resizing
   - What happens when width/height changes
   - Minimum spec violations noted

10. Resolution compatibility matrix
    - Width vs height compatibility
    - Status indicators (✗, ○, ●, ✓, ★)
    - All common resolutions

**Best for**: Visual learners, presentations, documentation

---

## By Role

### For Developers
1. Read: README_DISPLAY_ANALYSIS.md (overview)
2. Study: SCREEN_SIZE_DISPLAY_ANALYSIS.md sections 1-3, 9
3. Reference: DISPLAY_DIAGRAMS.txt diagram 1, 4
4. Implement: Recommendations in section 11
5. Test: Follow checklist in section 13

### For Designers
1. Start: DISPLAY_QUICK_REFERENCE.md
2. Visualize: DISPLAY_DIAGRAMS.txt all diagrams
3. Study: SCREEN_SIZE_DISPLAY_ANALYSIS.md sections 5-6
4. Test at: 1280×720 and 1920×1080 resolutions
5. Verify: DISPLAY_QUICK_REFERENCE.md "Calibration Checklist"

### For QA/Testers
1. Reference: DISPLAY_QUICK_REFERENCE.md
2. Use: "Monitor Compatibility Chart"
3. Follow: "Calibration Checklist"
4. Test: All resolutions in compatibility matrix
5. Troubleshoot: Using "Troubleshooting" section

### For Technical Writers
1. Reference: SCREEN_SIZE_DISPLAY_ANALYSIS.md (complete)
2. Visuals: DISPLAY_DIAGRAMS.txt (include in docs)
3. Summary: README_DISPLAY_ANALYSIS.md (quick facts)
4. Specs: DISPLAY_QUICK_REFERENCE.md (user-facing)

### For Project Managers
1. Overview: README_DISPLAY_ANALYSIS.md
2. Requirements: DISPLAY_QUICK_REFERENCE.md "Minimum vs Optimal"
3. Issues: README_DISPLAY_ANALYSIS.md "Critical Issues"
4. Roadmap: SCREEN_SIZE_DISPLAY_ANALYSIS.md section 11

---

## Key Numbers at a Glance

| Specification | Value |
|---|---|
| **Minimum Window** | 1280×720 px |
| **Optimal Window** | 1920×1080 px |
| **Automatic Sizing** | 80% of screen |
| **Menu Bar** | 22px |
| **Toolbars** | 32px each (2) |
| **Status Bar** | 22px |
| **Debug Console Max** | 150px |
| **Right Panel** | ~300px (adjustable) |
| **Constraint Columns** | 300px + 80px |
| **Button Padding** | 8px V, 16px H |
| **Viewport at 1920×1080** | 1200×754 px |

---

## Critical Issues Found

| Issue | Severity | Status |
|---|---|---|
| No `setMinimumSize()` enforcement | High | Not implemented |
| Matplotlib fixed 100 DPI on Retina | Medium | Needs DPI-aware code |
| No responsive breakpoints | Low | Future enhancement |

---

## File Locations in Codebase

- `main.py` (137-143): Window sizing logic
- `main.py` (448-521): Dock widget creation
- `main.py` (495): Debug console max height
- `app/ui/styles.py`: All UI component styles
- `app/ui/viewport_layout.py`: Viewport modes & splitters
- `app/ui/constraint_panel.py` (55-57): Column widths
- `app/ui/region_list_widget.py`: Button constraints
- `app/ui/analysis_panel.py` (52-54): Matplotlib sizing
- `app/ui/selection_info_panel.py` (58): List max height

---

## Cross-References

Related Project Documentation:
- [UX/UI Design Specification](reference/UX_UI_DESIGN_SPECIFICATION.md)
- [CLAUDE.md](../CLAUDE.md) - Project architecture
- [README.md](../README.md) - Project overview

---

## Document Maintenance

- **Last Updated**: November 15, 2025
- **Accuracy Status**: Verified against source code ✓
- **Framework**: PyQt6 6.9.1, VTK 9.3.0
- **Files Reviewed**: 25+ UI components, main.py, styles.py
- **Next Review**: After significant UI changes

---

## Start Reading

**New to this project?**
→ Read README_DISPLAY_ANALYSIS.md first

**Need specific information?**
→ Use the navigation links above

**Need a visual?**
→ See DISPLAY_DIAGRAMS.txt

**Need code locations?**
→ Check SCREEN_SIZE_DISPLAY_ANALYSIS.md section 2 or README section "File Locations in Codebase"

---

**All files are in the same directory as this index.**
