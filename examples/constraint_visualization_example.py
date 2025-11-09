"""
Example: Constraint Visualization with ConstraintRenderer

This example demonstrates how to use the ConstraintRenderer to visualize
manufacturing constraints including undercuts, draft angles, and demolding
direction in a VTK viewport.

Usage:
    python examples/constraint_visualization_example.py
"""

import vtk
import numpy as np
from app.geometry.constraint_renderer import ConstraintRenderer


def main():
    """
    Demonstrate constraint visualization on a simple test geometry.
    """
    # Create a VTK renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.15)  # Dark blue background

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 600)
    render_window.SetWindowName("Constraint Visualization Example")

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Create a test mesh (cylinder to simulate a mold surface)
    print("Creating test geometry...")
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetHeight(4.0)
    cylinder.SetRadius(1.5)
    cylinder.SetResolution(32)
    cylinder.Update()

    test_mesh = cylinder.GetOutput()
    num_cells = test_mesh.GetNumberOfCells()

    print(f"Mesh has {num_cells} faces")

    # Create the constraint renderer
    constraint_renderer = ConstraintRenderer(renderer)

    # 1. Simulate undercut detection
    # Bottom 15% of faces have undercuts (can't be demolded)
    undercut_faces = list(range(int(num_cells * 0.85), num_cells))
    print(f"\nSimulating {len(undercut_faces)} undercut faces...")
    constraint_renderer.show_undercuts(undercut_faces, test_mesh)

    # 2. Simulate draft angle calculation
    # Create gradient: top faces have good draft, bottom faces have poor draft
    draft_map = {}
    for i in range(num_cells):
        # Height-based draft gradient (0.2° at bottom to 3.5° at top)
        draft_angle = 0.2 + (i / num_cells) * 3.3
        draft_map[i] = draft_angle

    print("Simulating draft angle analysis...")
    constraint_renderer.show_draft_angles(draft_map, test_mesh)

    # Get and print draft statistics
    stats = constraint_renderer.get_draft_statistics(draft_map)
    print(f"\nDraft Angle Statistics:")
    print(f"  Range: {stats['min']:.2f}° to {stats['max']:.2f}°")
    print(f"  Mean: {stats['mean']:.2f}° ± {stats['std']:.2f}°")
    print(f"  Median: {stats['median']:.2f}°")
    print(f"\nDraft Quality Distribution:")
    print(f"  Insufficient (<0.5°): {stats['count_insufficient']} faces")
    print(f"  Marginal (0.5-2.0°): {stats['count_marginal']} faces")
    print(f"  Good (>2.0°): {stats['count_good']} faces")

    # 3. Show demolding direction
    # For a cylinder, the demolding direction is along the axis (+Y in VTK cylinder)
    demolding_direction = (0.0, 1.0, 0.0)  # Upward along Y-axis
    print(f"\nDemolding direction: {demolding_direction}")
    constraint_renderer.show_demolding_direction(
        direction=demolding_direction,
        scale=3.0  # Make arrow clearly visible
    )

    # Add a base mesh for reference (wireframe)
    base_mapper = vtk.vtkPolyDataMapper()
    base_mapper.SetInputData(test_mesh)

    base_actor = vtk.vtkActor()
    base_actor.SetMapper(base_mapper)
    base_actor.GetProperty().SetRepresentationToWireframe()
    base_actor.GetProperty().SetColor(0.3, 0.3, 0.3)
    base_actor.GetProperty().SetLineWidth(0.5)
    base_actor.GetProperty().SetOpacity(0.3)

    renderer.AddActor(base_actor)

    # Add text annotation
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(
        "Constraint Visualization\n"
        "Red faces: Undercuts (Tier 1)\n"
        "Color gradient: Draft angles (Tier 2)\n"
        "  Red: <0.5° | Yellow: 0.5-2.0° | Green: >2.0°\n"
        "Blue arrow: Demolding direction"
    )
    text_actor.GetTextProperty().SetFontSize(14)
    text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text_actor.SetPosition(10, 500)
    renderer.AddActor2D(text_actor)

    # Reset camera to show entire scene
    renderer.ResetCamera()

    # Set up interactive controls
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    # Start rendering
    print("\nStarting interactive visualization...")
    print("Controls:")
    print("  - Left click + drag: Rotate view")
    print("  - Mouse wheel: Zoom")
    print("  - Right click + drag: Pan")
    print("  - 'q' or close window: Exit")

    render_window.Render()
    interactor.Start()

    # Cleanup
    constraint_renderer.clear_all()
    print("\nVisualization closed.")


if __name__ == "__main__":
    main()
