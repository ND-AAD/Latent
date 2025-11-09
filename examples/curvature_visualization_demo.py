#!/usr/bin/env python3
"""
Curvature Visualization Demo

Demonstrates the false-color curvature visualization system on various
test surfaces with known curvature properties.

Author: Ceramic Mold Analyzer - Agent 29
Date: November 2025
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import vtk
import numpy as np
from app.geometry.curvature_renderer import (
    CurvatureRenderer,
    CurvatureType,
    ColorMapType,
    create_test_curvature_visualization
)


def demo_sphere_gaussian():
    """Demo: Gaussian curvature on a sphere (all positive)."""
    print("\n=== Demo 1: Gaussian Curvature on Sphere ===")

    # Create sphere
    radius = 5.0
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(radius)
    sphere_source.SetThetaResolution(50)
    sphere_source.SetPhiResolution(50)
    sphere_source.Update()
    polydata = sphere_source.GetOutput()

    # Compute Gaussian curvature
    renderer = CurvatureRenderer()
    gaussian_values = renderer.compute_curvature_from_mesh(
        polydata,
        CurvatureType.GAUSSIAN
    )

    # Print statistics
    stats = renderer.get_curvature_statistics(gaussian_values)
    expected_k = 1.0 / (radius ** 2)
    print(f"Expected Gaussian curvature: K = 1/r² = {expected_k:.4f}")
    print(f"Computed statistics:")
    print(f"  Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
    print(f"  Mean: {stats['mean']:.4f} ± {stats['std']:.4f}")
    print(f"  Median: {stats['median']:.4f}")
    print(f"  Error: {abs(stats['mean'] - expected_k) / expected_k * 100:.1f}%")

    # Create visualization
    actor = renderer.create_curvature_actor(
        polydata,
        gaussian_values,
        curvature_type=CurvatureType.GAUSSIAN,
        color_map=ColorMapType.DIVERGING_BWR,
        auto_range=True,
        show_edges=False
    )

    scalar_bar = renderer.create_scalar_bar(num_labels=5)

    # Setup rendering
    vtk_renderer = vtk.vtkRenderer()
    vtk_renderer.SetBackground(0.1, 0.1, 0.15)
    vtk_renderer.AddActor(actor)
    vtk_renderer.AddActor2D(scalar_bar)

    # Create window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(vtk_renderer)
    render_window.SetSize(800, 600)
    render_window.SetWindowName("Gaussian Curvature - Sphere")

    # Create interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Set camera
    vtk_renderer.ResetCamera()
    camera = vtk_renderer.GetActiveCamera()
    camera.Elevation(20)
    camera.Azimuth(30)

    # Show
    print("Opening visualization window... (close to continue)")
    render_window.Render()
    interactor.Start()


def demo_torus_comparison():
    """Demo: Compare Gaussian vs. Mean curvature on torus."""
    print("\n=== Demo 2: Gaussian vs. Mean Curvature on Torus ===")

    # Create torus
    torus_source = vtk.vtkParametricTorus()
    torus_source.SetRingRadius(5.0)
    torus_source.SetCrossSectionRadius(2.0)

    param_source = vtk.vtkParametricFunctionSource()
    param_source.SetParametricFunction(torus_source)
    param_source.SetUResolution(50)
    param_source.SetVResolution(50)
    param_source.Update()
    polydata = param_source.GetOutput()

    # Compute both curvatures
    renderer = CurvatureRenderer()

    gaussian_values = renderer.compute_curvature_from_mesh(
        polydata,
        CurvatureType.GAUSSIAN
    )

    mean_values = renderer.compute_curvature_from_mesh(
        polydata,
        CurvatureType.MEAN
    )

    # Print statistics
    g_stats = renderer.get_curvature_statistics(gaussian_values)
    m_stats = renderer.get_curvature_statistics(mean_values)

    print("Gaussian curvature statistics:")
    print(f"  Range: [{g_stats['min']:.4f}, {g_stats['max']:.4f}]")
    print(f"  Mean: {g_stats['mean']:.4f}")
    print(f"  Note: Torus has both positive (outer) and negative (inner) K")

    print("\nMean curvature statistics:")
    print(f"  Range: [{m_stats['min']:.4f}, {m_stats['max']:.4f}]")
    print(f"  Mean: {m_stats['mean']:.4f}")

    # Create side-by-side visualization
    # Left: Gaussian curvature
    g_actor = renderer.create_curvature_actor(
        polydata,
        gaussian_values,
        curvature_type=CurvatureType.GAUSSIAN,
        color_map=ColorMapType.DIVERGING_BWR,
        auto_range=True
    )

    g_renderer = vtk.vtkRenderer()
    g_renderer.SetBackground(0.1, 0.1, 0.15)
    g_renderer.AddActor(g_actor)
    g_renderer.SetViewport(0.0, 0.0, 0.5, 1.0)  # Left half

    g_scalar_bar = renderer.create_scalar_bar(num_labels=5)
    g_renderer.AddActor2D(g_scalar_bar)

    # Right: Mean curvature
    renderer2 = CurvatureRenderer()
    m_actor = renderer2.create_curvature_actor(
        polydata,
        mean_values,
        curvature_type=CurvatureType.MEAN,
        color_map=ColorMapType.COOL_WARM,
        auto_range=True
    )

    m_renderer = vtk.vtkRenderer()
    m_renderer.SetBackground(0.1, 0.1, 0.15)
    m_renderer.AddActor(m_actor)
    m_renderer.SetViewport(0.5, 0.0, 1.0, 1.0)  # Right half

    m_scalar_bar = renderer2.create_scalar_bar(num_labels=5)
    m_renderer.AddActor2D(m_scalar_bar)

    # Create window with both renderers
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(g_renderer)
    render_window.AddRenderer(m_renderer)
    render_window.SetSize(1600, 600)
    render_window.SetWindowName("Torus: Gaussian (left) vs. Mean (right) Curvature")

    # Create interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Set cameras (sync viewpoints)
    g_renderer.ResetCamera()
    camera = g_renderer.GetActiveCamera()
    camera.Elevation(20)
    camera.Azimuth(30)

    m_renderer.SetActiveCamera(camera)  # Share camera

    # Show
    print("Opening comparison window... (close to continue)")
    render_window.Render()
    interactor.Start()


def demo_color_maps():
    """Demo: Compare different color maps on same surface."""
    print("\n=== Demo 3: Color Map Comparison ===")

    # Create test surface (saddle)
    saddle_source = vtk.vtkParametricRandomHills()
    saddle_source.SetNumberOfHills(5)

    param_source = vtk.vtkParametricFunctionSource()
    param_source.SetParametricFunction(saddle_source)
    param_source.SetUResolution(40)
    param_source.SetVResolution(40)
    param_source.Update()
    polydata = param_source.GetOutput()

    # Compute curvature
    renderer = CurvatureRenderer()
    gaussian_values = renderer.compute_curvature_from_mesh(
        polydata,
        CurvatureType.GAUSSIAN
    )

    stats = renderer.get_curvature_statistics(gaussian_values)
    print(f"Surface curvature range: [{stats['min']:.4f}, {stats['max']:.4f}]")

    # Create visualization with different color maps
    color_maps = [
        ColorMapType.DIVERGING_BWR,
        ColorMapType.COOL_WARM,
        ColorMapType.RAINBOW,
        ColorMapType.VIRIDIS
    ]

    # Create 2x2 grid layout
    renderers = []
    for i, color_map in enumerate(color_maps):
        r = CurvatureRenderer()
        actor = r.create_curvature_actor(
            polydata,
            gaussian_values,
            curvature_type=CurvatureType.GAUSSIAN,
            color_map=color_map,
            auto_range=True,
            show_edges=False
        )

        vtk_renderer = vtk.vtkRenderer()
        vtk_renderer.SetBackground(0.1, 0.1, 0.15)
        vtk_renderer.AddActor(actor)

        # Set viewport (2x2 grid)
        x = (i % 2) * 0.5
        y = (i // 2) * 0.5
        vtk_renderer.SetViewport(x, y, x + 0.5, y + 0.5)

        # Add label
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(color_map.value)
        text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        text_actor.GetTextProperty().SetFontSize(18)
        text_actor.GetTextProperty().BoldOn()
        text_actor.SetPosition(10, 10)
        vtk_renderer.AddActor2D(text_actor)

        renderers.append(vtk_renderer)

    # Create window
    render_window = vtk.vtkRenderWindow()
    for r in renderers:
        render_window.AddRenderer(r)
    render_window.SetSize(1200, 1200)
    render_window.SetWindowName("Color Map Comparison")

    # Create interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Set cameras (sync all)
    renderers[0].ResetCamera()
    camera = renderers[0].GetActiveCamera()
    camera.Elevation(30)
    camera.Azimuth(45)

    for r in renderers[1:]:
        r.SetActiveCamera(camera)

    # Show
    print("Opening color map comparison... (close to continue)")
    render_window.Render()
    interactor.Start()


def demo_quick_test():
    """Quick test using convenience function."""
    print("\n=== Quick Test: One-Liner Visualization ===")

    actor, scalar_bar = create_test_curvature_visualization(
        curvature_type=CurvatureType.MEAN,
        color_map=ColorMapType.VIRIDIS
    )

    # Setup rendering
    vtk_renderer = vtk.vtkRenderer()
    vtk_renderer.SetBackground(0.1, 0.1, 0.15)
    vtk_renderer.AddActor(actor)
    vtk_renderer.AddActor2D(scalar_bar)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(vtk_renderer)
    render_window.SetSize(800, 600)
    render_window.SetWindowName("Quick Test - Mean Curvature Sphere")

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    vtk_renderer.ResetCamera()

    print("Opening quick test window...")
    render_window.Render()
    interactor.Start()


def main():
    """Run all demos."""
    print("=" * 60)
    print("Curvature Visualization Demo")
    print("Agent 29 - Day 4 Morning")
    print("=" * 60)

    demos = [
        ("Gaussian curvature on sphere", demo_sphere_gaussian),
        ("Gaussian vs. Mean curvature comparison", demo_torus_comparison),
        ("Color map comparison", demo_color_maps),
        ("Quick test", demo_quick_test),
    ]

    while True:
        print("\nAvailable demos:")
        for i, (name, _) in enumerate(demos):
            print(f"  {i+1}. {name}")
        print(f"  0. Exit")

        choice = input("\nSelect demo (0-4): ").strip()

        if choice == "0":
            print("Exiting demo.")
            break
        elif choice in ["1", "2", "3", "4"]:
            idx = int(choice) - 1
            try:
                demos[idx][1]()
            except Exception as e:
                print(f"Error running demo: {e}")
        else:
            print("Invalid choice. Please enter 0-4.")


if __name__ == "__main__":
    main()
