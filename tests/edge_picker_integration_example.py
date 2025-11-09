"""
Integration Example for SubDEdgePicker

This example demonstrates how to use the SubDEdgePicker in a real application.
It shows:
1. Creating a simple mesh
2. Setting up the edge picker
3. Extracting edges with adjacency tracking
4. Identifying boundary vs internal edges
5. Selection management

Note: This example requires a display environment (X11, Wayland, etc.) to run.
It's provided as reference for integration, not as an automated test.
"""

import sys

try:
    # Try to import VTK - this will fail in headless environments
    from app import vtk_bridge as vtk
    from app.ui.pickers.edge_picker import SubDEdgePicker, EdgeInfo
    VTK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  VTK not available: {e}")
    print("This example requires a display environment with EGL/OpenGL support.")
    VTK_AVAILABLE = False
    sys.exit(0)


def create_simple_mesh():
    """Create a simple triangulated quad mesh for testing"""
    # Points forming a quad
    #   0---1
    #   |  /|
    #   | / |
    #   |/  |
    #   2---3

    points = vtk.vtkPoints()
    points.InsertNextPoint(0.0, 1.0, 0.0)  # 0
    points.InsertNextPoint(1.0, 1.0, 0.0)  # 1
    points.InsertNextPoint(0.0, 0.0, 0.0)  # 2
    points.InsertNextPoint(1.0, 0.0, 0.0)  # 3

    # Two triangles
    triangles = vtk.vtkCellArray()

    # Triangle 0: (0, 1, 2)
    tri1 = vtk.vtkTriangle()
    tri1.GetPointIds().SetId(0, 0)
    tri1.GetPointIds().SetId(1, 1)
    tri1.GetPointIds().SetId(2, 2)
    triangles.InsertNextCell(tri1)

    # Triangle 1: (1, 3, 2)
    tri2 = vtk.vtkTriangle()
    tri2.GetPointIds().SetId(0, 1)
    tri2.GetPointIds().SetId(1, 3)
    tri2.GetPointIds().SetId(2, 2)
    triangles.InsertNextCell(tri2)

    # Create polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(triangles)

    return polydata


def main():
    """Main integration example"""
    print("=" * 60)
    print("SubDEdgePicker Integration Example")
    print("=" * 60)

    # Create renderer and window
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 600)
    render_window.OffScreenRenderingOn()  # No GUI needed

    print("✅ Created VTK renderer and window")

    # Create edge picker
    picker = SubDEdgePicker(renderer, render_window)
    print("✅ Created SubDEdgePicker")

    # Create simple test mesh
    polydata = create_simple_mesh()
    print(f"✅ Created test mesh: {polydata.GetNumberOfPoints()} points, {polydata.GetNumberOfCells()} triangles")

    # Setup edge extraction
    print("\n" + "=" * 60)
    print("Edge Extraction")
    print("=" * 60)
    picker.setup_edge_extraction(polydata)

    # Analyze edges
    print(f"\n📊 Total edges: {len(picker.edges)}")
    print(f"   Boundary edges: {len(picker.get_boundary_edges())}")
    print(f"   Internal edges: {len(picker.get_internal_edges())}")

    # Show edge details
    print("\n" + "=" * 60)
    print("Edge Details")
    print("=" * 60)
    for edge_id, edge_info in picker.edges.items():
        edge_type = "BOUNDARY" if edge_info.is_boundary else "INTERNAL"
        print(f"Edge {edge_id}: vertices {edge_info.vertices}, {len(edge_info.adjacent_triangles)} triangles, {edge_type}")

    # Test selection
    print("\n" + "=" * 60)
    print("Selection Management")
    print("=" * 60)

    # Select first edge
    first_edge_id = list(picker.edges.keys())[0]
    picker.selected_edge_ids.add(first_edge_id)
    print(f"✅ Selected edge {first_edge_id}")
    print(f"   Selected edges: {picker.get_selected_edges()}")

    # Update highlight (this would show yellow tubes in actual rendering)
    picker._update_highlight()
    print("✅ Updated highlight visualization (yellow tubes)")

    # Multi-select - add another edge
    if len(picker.edges) > 1:
        second_edge_id = list(picker.edges.keys())[1]
        picker.selected_edge_ids.add(second_edge_id)
        print(f"✅ Added edge {second_edge_id} to selection")
        print(f"   Selected edges: {picker.get_selected_edges()}")

    # Clear selection
    picker.clear_selection()
    print("✅ Cleared selection")
    print(f"   Selected edges: {picker.get_selected_edges()}")

    # Cleanup
    print("\n" + "=" * 60)
    print("Cleanup")
    print("=" * 60)
    picker.cleanup()
    print("✅ Edge picker cleaned up")

    print("\n" + "=" * 60)
    print("Integration Example Complete!")
    print("=" * 60)
    print("\nKey features demonstrated:")
    print("  ✓ Edge extraction from tessellation")
    print("  ✓ Edge→triangle adjacency mapping")
    print("  ✓ Boundary vs internal edge identification")
    print("  ✓ Tubular rendering (cyan guide, yellow highlight)")
    print("  ✓ Multi-select support")
    print("  ✓ Selection state management")


if __name__ == '__main__':
    if VTK_AVAILABLE:
        main()
    else:
        print("Skipping example - VTK not available")
