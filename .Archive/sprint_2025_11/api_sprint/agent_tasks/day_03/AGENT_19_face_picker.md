# Agent 19: Face Picker (Panel Mode)

**Day**: 3 | **Duration**: 3-4h | **Cost**: $4-6

## Mission
Implement VTK-based face picking for Panel edit mode with visual highlighting and multi-select support.

## Deliverables
- `app/ui/pickers/face_picker.py` - SubDFacePicker class
- Integration with EditModeManager
- `tests/test_face_picker.py` - Picking tests

## Requirements
**Face Picking**:
- VTK cell picker for triangle selection
- Map triangle → parent SubD face (using face_parents from TessellationResult)
- Highlight selected faces (yellow, 1.0, 1.0, 0.0)
- Multi-select with Shift+Click (add/remove from selection)
- Selection toggle (Shift+Click on selected face deselects it)

**Integration**:
- Only active in PANEL mode
- LEFT click triggers pick
- Updates EditModeManager.selected_faces
- Emits selection_changed signal

## Success Criteria
- [ ] Face picking accurate
- [ ] Triangle→face mapping working
- [ ] Yellow highlighting applied
- [ ] Multi-select functional
- [ ] Selection toggle working
- [ ] Tests pass

**Ready!**
