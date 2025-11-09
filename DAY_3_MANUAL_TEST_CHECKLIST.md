# Day 3 Manual Testing Checklist

**Date**: November 9, 2025
**Automated Tests**: ✅ PASSED
**Manual Tests**: ⏳ PENDING

---

## Pre-Flight Check ✅

- [x] All dependencies installed
- [x] All modules import successfully
- [x] Data structures work correctly
- [x] C++ module loads

---

## Manual UI Tests

### Test 1: Application Launch
```bash
cd "/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent"
python3 main.py
```

**Expected**:
- [x] Application window opens
- [x] VTK viewport visible
- [x] Edit mode toolbar visible with S/P/E/V buttons
- [x] No errors in console

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 2: Edit Mode Switching

**Actions**:
1. Click **S** button (Solid mode)
2. Click **P** button (Panel mode)
3. Click **E** button (Edge mode)
4. Click **V** button (Vertex mode)

**Expected**:
- [x] Each button highlights in blue when selected
- [x] Only one button highlighted at a time
- [x] Selection info label updates with mode name
- [x] Toolbar feels responsive

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 3: Face Selection (Panel Mode)

**Setup**:
1. Switch to Panel mode (P button)
2. Load a SubD from Rhino (or use test geometry)

**Actions**:
1. Left-click on a face in the viewport
2. Shift+Click on another face
3. Click the "Clear" button

**Expected**:
- [x] Clicked face highlights in yellow
- [x] Shift+Click adds face to selection (multiple yellow faces)
- [x] Clear button removes all highlighting
- [x] Selection info shows "X faces selected"

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 4: Edge Selection (Edge Mode)

**Setup**:
1. Switch to Edge mode (E button)
2. Ensure SubD is loaded

**Actions**:
1. Click on an edge
2. Shift+Click on another edge
3. Observe edge visualization

**Expected**:
- [ ] Cyan guide edges visible on the mesh
- [ ] Clicked edge highlights with yellow tube
- [ ] Shift+Click adds to selection
- [ ] Multiple edges can be selected simultaneously
- [ ] Edge thickness visually distinct from faces

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 5: Vertex Selection (Vertex Mode)

**Setup**:
1. Switch to Vertex mode (V button)
2. Ensure SubD control cage visible

**Actions**:
1. Click on a control cage vertex
2. Shift+Click on another vertex
3. Try selecting multiple vertices

**Expected**:
- [ ] Control cage vertices visible as small spheres
- [ ] Clicked vertex highlights with yellow sphere
- [ ] Shift+Click adds vertices to selection
- [ ] Clear works to deselect all

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 6: Region Visualization

**Setup**:
1. Create or load regions (if region creation UI exists)
2. If not available yet, skip this test

**Actions**:
1. View regions in viewport
2. Observe color coding
3. Check visual quality

**Expected**:
- [ ] Each region has a distinct color
- [ ] Colors are visually distinguishable
- [ ] No Z-fighting or visual artifacts
- [ ] Smooth rendering

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail / ⏭️ Skip (not implemented)

**Notes**:


---

### Test 7: Region Properties Dialog

**Setup**:
1. Ensure region list widget is visible
2. Regions must be loaded or created

**Actions**:
1. Double-click a region in the region list
2. Verify all fields in the dialog
3. Edit the region name
4. Click "Apply"
5. Try "Export to JSON"

**Expected**:
- [ ] Dialog opens on double-click
- [ ] All fields populate correctly:
  - [ ] Region ID (read-only)
  - [ ] Region name (editable)
  - [ ] Face count
  - [ ] Pinned checkbox
  - [ ] Unity principle text
  - [ ] Unity strength progress bar (color-coded)
- [ ] Apply button saves changes
- [ ] Export button creates JSON file
- [ ] Dialog closes properly

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail / ⏭️ Skip (no regions yet)

**Notes**:


---

### Test 8: Selection Info Panel

**Actions**:
1. Select various elements (faces, edges, vertices)
2. Observe the selection info panel

**Expected**:
- [ ] Panel updates in real-time
- [ ] Shows count of selected items
- [ ] Format: "X faces selected" / "X edges selected" / "X vertices selected"
- [ ] Shows "No selection" when nothing selected

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 9: Selection Operations

**Actions**:
1. Select some faces/edges/vertices
2. Click "Select All" button
3. Click "Invert Selection" button
4. Click "Clear" button

**Expected**:
- [ ] Select All selects all elements in current mode
- [ ] Invert flips the selection
- [ ] Clear removes all selections
- [ ] Operations feel responsive

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

### Test 10: Multi-Selection (Shift+Click)

**Actions**:
1. In Panel mode, click face A
2. Shift+Click face B
3. Shift+Click face A again

**Expected**:
- [ ] Face A highlights
- [ ] Face B adds to selection (both highlighted)
- [ ] Clicking A again removes it from selection
- [ ] Toggle behavior works correctly

**Status**: ⬜ Not tested / ✅ Pass / ❌ Fail

**Notes**:


---

## Summary

### Automated Tests
- ✅ All dependencies present
- ✅ All modules import
- ✅ Data structures functional
- ✅ JSON serialization works

### Manual Tests Results

| Test | Status | Notes |
|------|--------|-------|
| 1. Application Launch | ⬜ | |
| 2. Edit Mode Switching | ⬜ | |
| 3. Face Selection | ⬜ | |
| 4. Edge Selection | ⬜ | |
| 5. Vertex Selection | ⬜ | |
| 6. Region Visualization | ⬜ | |
| 7. Region Properties | ⬜ | |
| 8. Selection Info | ⬜ | |
| 9. Selection Operations | ⬜ | |
| 10. Multi-Selection | ⬜ | |

**Total Tests**: ___ / 10 passed

---

## Issues Found

List any issues discovered during testing:

1.

2.

3.


---

## Decision

After completing manual tests:

- [ ] ✅ **All tests pass** → Proceed to Day 4
- [ ] ⚠️ **Minor issues found** → Document and proceed (can fix later)
- [ ] ❌ **Critical issues found** → Debug before Day 4

---

## Sign-Off

**Tester**: Nick
**Date**: ___________
**Status**: ⬜ APPROVED / ⬜ ISSUES FOUND / ⬜ BLOCKED

**Ready for Day 4**: ⬜ YES / ⬜ NO

---

*Complete this checklist and report back to proceed with Day 4 launch.*
