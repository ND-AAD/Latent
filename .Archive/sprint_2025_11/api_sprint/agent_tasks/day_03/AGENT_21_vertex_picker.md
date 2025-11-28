# Agent 21: Vertex Picker (Vertex Mode)

**Day**: 3 | **Duration**: 3-4h | **Cost**: $3-5

## Mission
Implement vertex selection with sphere visualization and proximity-based picking.

## Deliverables
- `app/ui/pickers/vertex_picker.py` - SubDVertexPicker class
- Vertex sphere rendering
- `tests/test_vertex_picker.py` - Vertex picking tests

## Requirements
**Vertex Picking**:
- Render vertices as spheres (vtkSphereSource)
- Default gray spheres for all vertices
- Yellow spheres (1.0, 1.0, 0.0) for selected
- Proximity-based picking (closest vertex within tolerance)
- Sphere radius adaptive to model size

**Picking Strategy**:
- 3D ray from click position
- Find closest vertex to ray within threshold
- Multi-select with Shift+Click

## Success Criteria
- [ ] Vertex spheres rendered
- [ ] Proximity picking accurate
- [ ] Yellow highlighting working
- [ ] Multi-select functional
- [ ] Adaptive sphere sizing
- [ ] Tests pass

**Ready!**
