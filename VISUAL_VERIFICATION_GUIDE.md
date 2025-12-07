# Visual Verification Guide

**Quick reference for verifying visual polish changes**

## How to Verify Changes

### 1. Launch Both Applications

**React Prototype**:
```bash
cd docs/reference/UX
npm run dev
# Opens in browser at http://localhost:5173
```

**PyQt Desktop App**:
```bash
python3 launch.py
```

---

## Visual Elements to Compare

### Top Bar

**React Prototype Specs**:
- Tab height: ~36px
- Tab padding: 16px horizontal, 8px vertical
- Tab font: 12px, uppercase, letter-spacing: 0.025em
- Active tab: 2px blue bottom border
- Button padding: 6px vertical, 12-16px horizontal
- Button font: 12px

**Visual Check**:
- [ ] Tab labels are uppercase with slight letter spacing
- [ ] Active tab has blue bottom border
- [ ] Button text is 12px (smaller than before)
- [ ] Buttons feel balanced (not too tall or wide)

---

### Left Sidebar

**React Prototype Specs**:
- Width: 220px (default)
- Button padding: 6px vertical, 12px horizontal
- Button font: 12px
- Section header: 12px, gray text

**Visual Check**:
- [ ] Sidebar is 220px wide
- [ ] Button text is 12px
- [ ] Hover states show gray background
- [ ] Section headers are visually distinct but subtle

---

### Right Panel

**React Prototype Specs**:
- Width: 320px (default)
- Tab bar: 48px wide
- Tab icons: 18px
- Panel content padding: 16px

**Visual Check**:
- [ ] Panel is 320px wide
- [ ] Vertical tab bar is ~48px wide
- [ ] Icons are 18px (visually balanced with tab height)
- [ ] Active tab has blue left border

---

### Bottom Panel

**React Prototype Specs**:
- Min height: 100px (collapsed)
- Max height: 160px (debug expanded)
- Input font: 12px
- Status indicators: 8px colored dots

**Visual Check**:
- [ ] Panel height is comfortable (not too tall or short)
- [ ] Command input font is 12px
- [ ] Debug console (if expanded) has clear header

---

### Input Fields

**React Prototype Specs**:
- Border radius: 4px
- Padding: 4px vertical, 8px horizontal
- Font: 12px
- Focus: Blue border + 2px blue outline

**Visual Check**:
- [ ] Input corners are slightly rounded (4px)
- [ ] Text inside inputs is 12px
- [ ] Clicking an input shows blue focus ring
- [ ] Tab navigation shows focus ring on all elements

---

### Buttons

**React Prototype Specs**:
- Primary: Blue background, white text, 6px vertical padding
- Secondary: White background, border, 6px vertical padding
- Toggle: Transparent, 4px vertical padding
- All: 12px font, 4px border radius

**Visual Check**:
- [ ] Primary buttons are blue with white text
- [ ] Secondary buttons have borders
- [ ] Button text is 12px (noticeably smaller)
- [ ] Buttons feel "tighter" than before (less vertical padding)

---

### Theme Colors

**Light Theme Visual Check**:
- [ ] Background is pure white (#FFFFFF)
- [ ] Borders are very light gray (#E6E6E6)
- [ ] Text is dark but not pure black (#252525)
- [ ] Hover states are subtle light gray (#F5F5F5)

**Dark Theme Visual Check**:
- [ ] Background is dark gray (#252525, not pure black)
- [ ] Panel backgrounds are slightly lighter (#343434, #444444)
- [ ] Borders are medium gray (#444444)
- [ ] Text is off-white (#FAFAFA, not pure white)

---

## Font Size Quick Reference

Hold a ruler or use browser dev tools to measure:

| Size | Usage | Appearance |
|------|-------|------------|
| 11px | Tooltips, muted labels | Very small, subtle |
| 12px | Buttons, inputs, tabs, labels | Small, readable |
| 13px | Body text, default labels | Standard, comfortable |
| 14px | Headings | Slightly larger, bold |

**Visual Check**:
- [ ] Tab labels feel small but readable (12px)
- [ ] Button text feels smaller than before (12px)
- [ ] Input text matches button text size (12px)
- [ ] Body text in panels feels comfortable (13px)

---

## Border Radius Quick Reference

Use browser dev tools or inspect closely:

| Radius | Usage | Appearance |
|--------|-------|------------|
| 4px | Inputs, buttons | Subtle rounded corners |
| 6px | Buttons (alternative) | Slightly more rounded |
| 10px | Panels, cards | Noticeably rounded |

**Visual Check**:
- [ ] Input field corners are subtly rounded (4px)
- [ ] Button corners are subtly rounded (4px)
- [ ] Panel corners are noticeably rounded (10px)
- [ ] List/tree widgets have rounded corners (10px)

---

## Spacing Consistency

Use browser grid overlay or measure with ruler:

| Spacing | Usage | Visual Check |
|---------|-------|--------------|
| 4px | Button gaps, small margins | Tight, minimal |
| 8px | Standard padding | Comfortable |
| 12px | Section padding | Spacious |
| 16px | Panel padding | Very spacious |

**Visual Check**:
- [ ] Buttons have small gaps between them (~4px)
- [ ] Panel content has comfortable padding (~8-16px)
- [ ] Sections have clear visual separation (~12-16px)

---

## Common Visual Discrepancies

These differences are acceptable:

1. **Font rendering**: Web fonts may appear slightly different from Qt fonts. Size is correct, rendering varies.

2. **Icon appearance**: React uses Lucide SVG icons, PyQt uses Unicode. Icons may look different but should be same size.

3. **Hover timing**: Web has 150ms transitions, Qt hovers are instant. Both are acceptable.

4. **Border sharpness**: Qt borders may appear sharper or softer depending on DPI. This is expected.

5. **Scrollbar appearance**: Qt scrollbars are native, React scrollbars are styled. Both are acceptable.

---

## Screenshot Comparison

For precise comparison:

1. **Take React prototype screenshot**:
   - Open React prototype in browser
   - Set window to exactly 1920×1080
   - Take screenshot of full window

2. **Take PyQt screenshot**:
   - Open PyQt app
   - Resize to match browser window size
   - Take screenshot of full window

3. **Overlay in image editor**:
   - Load both in Photoshop/GIMP
   - Set PyQt screenshot to 50% opacity
   - Align with React screenshot
   - Major elements should align within 2-3 pixels

---

## Keyboard Navigation Test

1. **Launch PyQt app**
2. **Press Tab repeatedly**
3. **Verify**:
   - [ ] Blue focus ring appears on each interactive element
   - [ ] Focus ring is visible but not intrusive
   - [ ] All buttons, inputs, tabs, and controls receive focus
   - [ ] Focus ring is 2px blue outline

---

## Accessibility Check

1. **Contrast ratios**:
   - [ ] Text on white background has sufficient contrast
   - [ ] Text on dark background has sufficient contrast
   - [ ] Disabled elements are clearly distinguishable

2. **Touch targets**:
   - [ ] Buttons are at least 24px tall (comfortable for clicking)
   - [ ] Interactive elements have clear hover states

---

## Performance Check

Visual polish should NOT impact performance:

- [ ] Application launches in < 2 seconds
- [ ] UI feels responsive (no lag when clicking)
- [ ] Theme switching is instant
- [ ] No visual glitches or artifacts
- [ ] Memory usage is normal (~50-100MB)

---

## Final Verification

Before marking complete:

- [ ] Compared TopBar with React prototype
- [ ] Compared LeftSidebar with React prototype
- [ ] Compared RightPanel with React prototype
- [ ] Compared BottomPanel with React prototype
- [ ] Tested keyboard navigation (Tab key)
- [ ] Verified focus indicators on all elements
- [ ] Toggled light/dark themes
- [ ] Verified button hover states
- [ ] Verified input focus states
- [ ] Checked font sizes throughout
- [ ] Checked spacing consistency
- [ ] Checked border radius consistency
- [ ] Checked color accuracy (light theme)
- [ ] Checked color accuracy (dark theme)

---

## Issues to Report

If you find visual discrepancies:

**Acceptable**:
- Font rendering differences (size is correct, rendering varies)
- Icon appearance (different icon set)
- Hover timing (instant vs 150ms)
- Scrollbar styling (native vs custom)

**Should be fixed**:
- Font sizes don't match (12px/13px/14px)
- Button padding feels wrong (too tall/short)
- Border radius missing or wrong (4px/6px/10px)
- Colors clearly don't match themes
- Focus indicators missing or invisible
- Spacing feels cramped or excessive

---

## Summary

Visual polish is complete when:
- All measurements match React prototype (±2px acceptable)
- Font sizes are consistent (11px/12px/13px/14px)
- Border radius is appropriate (4px inputs, 10px panels)
- Colors match themes exactly
- Focus indicators are visible on all interactive elements
- Keyboard navigation works smoothly
- Overall visual appearance feels polished and professional
