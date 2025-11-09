# Agent 20: Edge Picker (Edge Mode)

**Day**: 3 | **Duration**: 3-4h | **Cost**: $4-6

## Mission
Implement edge selection with visual highlighting using tubular edge rendering for visibility.

## Deliverables
- `app/ui/pickers/edge_picker.py` - SubDEdgePicker class
- Edge extraction and visualization
- `tests/test_edge_picker.py` - Edge picking tests

## Requirements
**Edge Picking**:
- Extract edges from tessellation (shared triangle edges)
- Render edges as tubes (vtkTubeFilter) for visibility
- Cyan wireframe guide (0.0, 1.0, 1.0) for all edges
- Yellow highlighting (1.0, 1.0, 0.0) for selected edges
- Tolerance-based picking (ray-to-edge distance <0.1 units)

**Edge Extraction**:
- Build edge→triangle adjacency map
- Identify boundary vs. internal edges
- Store edge as (vertex_i, vertex_j) pairs

## Success Criteria
- [ ] Edge extraction working
- [ ] Tubular rendering visible
- [ ] Picking accurate within tolerance
- [ ] Yellow highlighting only selected edges (not all)
- [ ] Multi-select functional
- [ ] Tests pass

**Ready!**
