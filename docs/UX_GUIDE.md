# UX Implementation Guide

## Source of Truth

The React prototype in `docs/reference/UX/` is the **definitive UX reference**.

**To view the prototype:**
```bash
cd docs/reference/UX
npm install
npm run dev
```

---

## Architecture Summary

### Four-Sided Layout

| Position | Purpose | Behavior |
|----------|---------|----------|
| **TOP** | Primary actions | Changes with active tab |
| **LEFT** | Secondary/advanced actions | Changes with active tab |
| **RIGHT** | Properties and data | Persistent, 5 vertical tabs |
| **BOTTOM** | System console and history | Persistent |

### 6 Workflow Tabs

1. **FILE** - Session and project management
2. **ANALYZE** - Mathematical analysis and region discovery
3. **EDIT** - Region manipulation and selection
4. **VALIDATE** - Constraint checking and fixes
5. **FABRICATE** - Mold generation and export
6. **VIEW** - Viewport and display control

### Right Panel Tabs (Persistent)

1. VIEWPORT - Display settings
2. REGIONS - Region list and properties
3. CONSTRAINTS - Validation results
4. SELECTION - Current selection info
5. PARAMETERS - Analysis parameters

---

## Viewport Controls (Rhino-Compatible)

**DO NOT DEVIATE from these controls:**

| Action | Mouse/Key |
|--------|-----------|
| Select | LEFT click/drag |
| Rotate/orbit | RIGHT drag |
| Pan | Shift + RIGHT drag |
| Zoom | Mouse wheel or Ctrl + RIGHT drag |
| Add to selection | Shift + LEFT click |
| Remove from selection | Ctrl + LEFT click |
| Deselect all | Esc |

---

## Responsive Breakpoints

| Breakpoint | Width | Left Panel | Right Panel | Bottom |
|------------|-------|------------|-------------|--------|
| Compact | <1400px | 160px | 240px | 100px |
| Standard | 1400-1600px | 180px | 250px | 110px |
| Medium | 1600-2000px | 220px | 320px | 130px |
| Large | 2000-2560px | 250px | 400px | 140px |
| 4K | >2560px | 280px | 450px | 160px |

---

## Implementation Status

| Aspect | Status |
|--------|--------|
| React prototype | Complete |
| PyQt6 desktop | Phase 0 (pre-v2.0) |
| Migration | Pending |

---

## Key Prototype Files

| File | Purpose |
|------|---------|
| [App.tsx](reference/UX/src/App.tsx) | Main layout |
| [TopBar.tsx](reference/UX/src/components/TopBar.tsx) | Tab navigation + primary actions |
| [LeftSidebar.tsx](reference/UX/src/components/LeftSidebar.tsx) | Secondary tools |
| [RightPanel.tsx](reference/UX/src/components/RightPanel.tsx) | Properties (5 tabs) |
| [BottomPanel.tsx](reference/UX/src/components/BottomPanel.tsx) | Console |
| [Viewport.tsx](reference/UX/src/components/Viewport.tsx) | 3D view layouts |
