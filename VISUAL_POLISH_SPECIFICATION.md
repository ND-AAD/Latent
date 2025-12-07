# Visual Polish Specification

**Agent 1 - UX Sprint Day 5**

This document specifies exact visual values extracted from the React prototype in `docs/reference/UX/` to ensure pixel-perfect consistency with the PyQt implementation.

---

## 1. SPACING SYSTEM

### React Prototype (Tailwind)
- **Base unit**: `0.25rem` (4px)
- **Multipliers**:
  - `p-1` = 4px (0.25rem × 1)
  - `p-2` = 8px (0.25rem × 2) ✓ **STANDARD PADDING**
  - `p-3` = 12px (0.25rem × 3)
  - `p-4` = 16px (0.25rem × 4) ✓ **SECTION SPACING**
  - `gap-1` = 4px ✓ **BUTTON MARGIN**
  - `gap-2` = 8px

### Current PyQt Implementation
```python
PADDING_SMALL = 4   # Matches p-1 ✓
PADDING_MEDIUM = 8  # Matches p-2 ✓
PADDING_LARGE = 12  # Matches p-3 ✓
```

### Required Changes
- Add `PADDING_XLARGE = 16  # Matches p-4 for section spacing`
- Verify all components use consistent padding multipliers

---

## 2. FONT SIZES

### React Prototype (index.css)
```css
--text-xs: .75rem;      /* 12px - labels, hints */
--text-base: 1rem;      /* 16px - but base font size is 16px */
--text-lg: 1.125rem;    /* 18px - large text */
--text-xl: 1.25rem;     /* 20px - headings */
--text-2xl: 1.5rem;     /* 24px - large headings */
```

**IMPORTANT**: The React prototype uses `--font-size: 16px` as the root, but actual component text appears at:
- `text-xs` (.75rem) = **12px** for labels, hints, secondary text
- Implied **13px** for standard body text (not explicitly defined, but used in components)

### Component Usage in React
- **TopBar tabs**: `text-xs` (12px)
- **Buttons**: `text-xs` (12px) for action buttons
- **Panel labels**: `text-xs` (12px)
- **Panel values**: Appears to be 13px (default)

### Current PyQt Implementation
```python
font-size: 13px;  # Global default in styles.py ✓
font-size: 12px;  # For tooltips, tabs ✓
```

### Required Changes
- Verify all component font sizes match:
  - **xs**: 11px (for extra small labels)
  - **sm**: 12px (for labels, hints, secondary text)
  - **base**: 13px (for standard text) ✓
  - **lg**: 14px (for headings)
- Update tab font sizes to 12px to match React prototype

---

## 3. BORDER COLORS & RADIUS

### React Prototype (globals.css)

#### Light Theme
```css
--border: rgba(0, 0, 0, 0.1);  /* #0000001a - semi-transparent */
--color-gray-200: oklch(.928 .006 264.531);  /* Lighter borders */
--color-gray-300: oklch(.872 .01 258.338);   /* Standard borders */
```

#### Dark Theme
```css
--border: oklch(.269 0 0);  /* Solid dark gray */
--color-gray-700: oklch(.373 .034 259.733);  /* Panel borders */
```

### Converted to Hex (approximate)
- Light border: `#D1D1D6` (current) → Should be `#E6E6E6` (rgba(0,0,0,0.1) overlay)
- Dark border: `#444444` ✓ Matches

### Border Radius
```css
--radius: 0.625rem;  /* 10px */
--radius-sm: calc(var(--radius) - 4px);  /* 6px */
--radius-md: calc(var(--radius) - 2px);  /* 8px */
--radius-lg: var(--radius);  /* 10px */
```

### Current PyQt Implementation
```python
BORDER_RADIUS = 4  # ❌ Should be 6px for buttons, 10px for panels
```

### Required Changes
```python
BORDER_RADIUS_SMALL = 4   # For input fields
BORDER_RADIUS = 6         # For buttons (matches --radius-sm)
BORDER_RADIUS_LARGE = 10  # For panels (matches --radius-lg)
```

---

## 4. HOVER STATE TIMINGS

### React Prototype (index.css)
```css
--default-transition-duration: .15s;  /* 150ms */
--default-transition-timing-function: cubic-bezier(.4, 0, .2, 1);  /* ease */
```

### Component Usage
```tsx
className="transition-colors"  // Applies 150ms ease transition
```

### Current PyQt Implementation
No explicit transition timing defined in QSS (Qt handles this natively with shorter durations).

### Required Changes
While Qt doesn't support CSS-style transitions, we can:
- Ensure hover states are immediate (no delay)
- Use subtle color changes that feel smooth
- Consider adding hover animations for critical buttons

---

## 5. FOCUS INDICATORS

### React Prototype (globals.css)
```css
--ring: oklch(.708 0 0);  /* Blue-gray focus ring */
outline-color: color-mix(in oklab, var(--ring) 50%, transparent);  /* 50% opacity */
```

### Component Examples
All interactive elements have automatic outline on focus.

### Current PyQt Implementation
```python
# In get_input_style():
QLineEdit:focus {
    border-color: {colors['accent']};  # Blue border
}
```

### Required Changes
- Add consistent focus states across all interactive elements
- Use 2px outline offset for better visibility
- Ensure keyboard navigation shows visible focus ring

---

## 6. ICON CONSISTENCY

### React Prototype
Uses [Lucide React](https://lucide.dev/) icons with:
- **Inline icons**: 16px (`size={16}`)
- **Button icons**: 18px (`size={18}`)
- **Tab icons**: 16px
- Consistent stroke width across all icons

### Current PyQt Implementation
Uses Unicode symbols and custom icons inconsistently.

### Required Changes
- Standardize icon sizes:
  - Inline: 16px
  - Buttons: 18px
  - Large actions: 20px
- Ensure all icons align vertically with text baseline
- Use consistent icon family (Unicode or custom SVG set)

---

## 7. COLOR CONSISTENCY

### React Light Theme Colors
```css
Primary Background: #FFFFFF
Secondary Background: oklch(.985 0 0) ≈ #FAFAFA
Tertiary Background: oklch(.97 0 0) ≈ #F5F5F5

Text Primary: oklch(.145 0 0) ≈ #252525
Text Secondary: #717182
Text Muted: oklch(.708 0 0) ≈ #999999

Border: rgba(0,0,0,0.1) ≈ #E6E6E6
Border Light: oklch(.922 0 0) ≈ #EBEBEB

Accent: #3B82F6 (blue-500)
Accent Hover: #2563EB (blue-600)
```

### React Dark Theme Colors
```css
Primary Background: oklch(.145 0 0) ≈ #252525
Secondary Background: oklch(.205 0 0) ≈ #343434
Tertiary Background: oklch(.269 0 0) ≈ #444444

Text Primary: oklch(.985 0 0) ≈ #FAFAFA
Text Secondary: oklch(.708 0 0) ≈ #B4B4B4
Text Muted: #717182

Border: oklch(.269 0 0) ≈ #444444
```

### Current PyQt Implementation
```python
LIGHT_THEME = {
    'bg_primary': '#FFFFFF',      # ✓
    'bg_secondary': '#FAFAFA',    # ✓
    'bg_tertiary': '#F5F5F5',     # ✓
    'border': '#D1D1D6',          # ❌ Should be #E6E6E6
    'text_primary': '#1A1A1A',    # ❌ Should be #252525
}

DARK_THEME = {
    'bg_primary': '#1A1A1A',      # ❌ Should be #252525
    'bg_secondary': '#252525',    # ❌ Should be #343434
    'bg_tertiary': '#2D2D2D',     # ❌ Should be #444444
    'border': '#444444',          # ✓
}
```

### Required Changes
Update theme colors to match React prototype exactly.

---

## 8. BUTTON SPECIFICATIONS

### React Primary Button
```tsx
className="px-4 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors text-xs"
```
- Padding: 16px horizontal, 6px vertical
- Background: #3B82F6 → #2563EB on hover
- Border radius: 4px (rounded)
- Font size: 12px (text-xs)
- Transition: 150ms ease

### React Secondary Button (Light)
```tsx
className="px-3 py-1.5 rounded bg-white text-gray-700 hover:bg-gray-100 border border-gray-300 text-xs"
```
- Padding: 12px horizontal, 6px vertical
- Background: #FFFFFF → #F5F5F5 on hover
- Border: 1px solid #D1D5DB
- Border radius: 4px
- Font size: 12px

### React Toggle Button
```tsx
className="px-3 py-1 rounded text-gray-700 hover:bg-white hover:text-gray-900 text-xs"
```
- Padding: 12px horizontal, 4px vertical
- Background: transparent → white on hover
- Font size: 12px

### Current PyQt Implementation
```python
# Primary button
padding: 8px 12px;  # ❌ Should be 6px 16px
border-radius: 4px;  # ✓
font-size: 13px;    # ❌ Should be 12px
```

### Required Changes
- Update button padding to match React exactly
- Reduce font size to 12px for buttons
- Adjust border radius to 4px for buttons, 6px for panels

---

## 9. PANEL SPECIFICATIONS

### TopBar
```tsx
className="flex flex-col border-b bg-white border-gray-300"
```
- Height: Auto (tabs ~36px + actions ~48px)
- Border bottom: 1px solid #D1D5DB
- Tab padding: 16px horizontal, 8px vertical
- Tab border-bottom when active: 2px solid #3B82F6

### LeftSidebar
```tsx
className="w-[220px] border-r bg-gray-50 border-gray-300"
style={{ minWidth: '160px', maxWidth: '280px' }}
```
- Width: 220px (default)
- Min width: 160px
- Max width: 280px
- Background: #FAFAFA
- Border right: 1px solid #D1D5DB
- Section header padding: 16px horizontal, 8px vertical
- Button padding: 12px horizontal, 6px vertical

### RightPanel
```tsx
className="w-[320px] flex border-l bg-gray-50 border-gray-300"
style={{ minWidth: '240px', maxWidth: '450px' }}
```
- Width: 320px (default)
- Min width: 240px
- Max width: 450px
- Tab bar width: 48px
- Icon size: 18px

### BottomPanel
```tsx
className="flex items-stretch h-10"
style={{ minHeight: '100px', maxHeight: '160px' }}
```
- Min height: 100px (when collapsed)
- Max height: 160px (debug console expanded: 40px header + 120px content)

### Current PyQt Implementation
```python
SIDEBAR_WIDTH_DEFAULT = 220     # ✓
RIGHT_PANEL_WIDTH_DEFAULT = 320 # ✓
BOTTOM_PANEL_HEIGHT_MIN = 100   # ✓
TAB_HEIGHT = 36                 # ✓
ICON_TAB_WIDTH = 48             # ✓
```

All panel dimensions match! ✓

---

## 10. SUMMARY OF REQUIRED CHANGES

### Critical (Must Fix)
1. **Font sizes**: Ensure all text uses 12px for labels/buttons, 13px for body
2. **Border radius**: Update to 6px for buttons (currently 4px)
3. **Button padding**: Adjust to match React (6px vertical, 12-16px horizontal)
4. **Theme colors**: Update dark theme backgrounds to match React values

### Important (Should Fix)
5. **Section spacing**: Add 16px spacing constant (PADDING_XLARGE)
6. **Focus indicators**: Add consistent 2px blue outline on focus
7. **Icon sizes**: Standardize to 16px inline, 18px buttons
8. **Hover transitions**: Ensure smooth 150ms color transitions

### Nice to Have (Polish)
9. **Border colors**: Fine-tune light theme border to #E6E6E6
10. **Typography**: Add subtle font weight variations (400 normal, 500 medium)

---

## 11. VERIFICATION CHECKLIST

After implementing changes:

- [ ] Take screenshot of TopBar with tabs → Compare with React prototype
- [ ] Take screenshot of LeftSidebar with buttons → Compare spacing
- [ ] Take screenshot of RightPanel tabs → Compare icon alignment
- [ ] Take screenshot of BottomPanel → Compare heights
- [ ] Verify button hover states feel smooth
- [ ] Verify focus indicators are visible on all interactive elements
- [ ] Verify dark mode matches React prototype colors
- [ ] Test with keyboard navigation to ensure focus is visible

---

## 12. FILES TO MODIFY

1. **app/ui/styles.py**
   - Update LIGHT_THEME and DARK_THEME colors
   - Add BORDER_RADIUS_SMALL, BORDER_RADIUS_LARGE
   - Update button padding in get_button_style()
   - Update font sizes

2. **app/ui/top_bar.py**
   - Verify tab spacing and padding
   - Verify button padding

3. **app/ui/left_panels.py**
   - Verify button padding
   - Verify section spacing

4. **app/ui/right_panel.py**
   - Verify icon sizes
   - Verify tab button sizes

5. **app/ui/bottom_panel.py**
   - Verify heights
   - Verify input padding

6. **app/ui/collapsible_section.py**
   - Verify header padding
   - Verify section spacing
