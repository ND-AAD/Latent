# Agent 25: Region Visualization & Coloring

**Day**: 3 | **Duration**: 3-4h | **Cost**: $4-6

## Mission
Implement per-region coloring in viewport with color assignment, boundary rendering, and region highlighting.

## Deliverables
- `app/geometry/region_renderer.py` - Region visualization
- `app/ui/region_color_manager.py` - Color assignment
- `tests/test_region_viz.py` - Visualization tests

## Requirements
**Region Coloring**:
- Assign distinct colors to regions (HSV color wheel)
- Apply per-face colors to tessellation
- VTK scalar coloring on mesh
- Boundary curves rendered as tubes

**Color Manager**:
- Generate N visually distinct colors
- Respect pinned region colors
- User color override support
- Export color scheme to JSON

**Region Highlighting**:
- Hover highlights region (lighter shade)
- Selected region outlined (thick boundary)
- Pinned regions marked (pin icon overlay)

## Success Criteria
- [ ] Per-region coloring working
- [ ] Colors visually distinct
- [ ] Boundary rendering visible
- [ ] Highlighting functional
- [ ] Color persistence (pinned)
- [ ] Tests pass

**Ready!**
