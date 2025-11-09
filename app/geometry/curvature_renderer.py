"""
Curvature Renderer - VTK-based false-color visualization of surface curvature.

This module provides color-mapped visualization of curvature analysis results,
converting scalar curvature values (Gaussian, mean, principal) into
false-color surface representations using VTK scalar fields.

Features:
- False-color mapping for Gaussian/mean curvature
- Customizable color maps (rainbow, blue-white-red diverging, viridis, etc.)
- Automatic range detection or manual clamping
- Color scale legend/bar
- Support for both vertex-based and face-based curvature data

Mathematical Background:
- Gaussian curvature K = κ₁ × κ₂ (surface type: elliptic/hyperbolic/parabolic)
- Mean curvature H = (κ₁ + κ₂) / 2 (bending measure)
- Principal curvatures κ₁, κ₂ (min/max normal curvatures)

Color Map Conventions:
- Gaussian curvature: Diverging (blue=negative/saddle, white=zero, red=positive/bowl)
- Mean curvature: Diverging (blue=concave, white=flat, red=convex)
- Principal curvatures: Sequential (blue=low, red=high)

Author: Ceramic Mold Analyzer - Agent 29
Date: November 2025
"""

import vtk
import numpy as np
from typing import Tuple, Optional, Dict, List
from enum import Enum


class CurvatureType(Enum):
    """Types of curvature that can be visualized."""
    GAUSSIAN = "gaussian"           # K = κ₁ × κ₂
    MEAN = "mean"                   # H = (κ₁ + κ₂) / 2
    PRINCIPAL_MIN = "principal_min" # κ₁ (minimum principal)
    PRINCIPAL_MAX = "principal_max" # κ₂ (maximum principal)
    ABSOLUTE_MEAN = "absolute_mean" # |H| (magnitude only)


class ColorMapType(Enum):
    """Color map presets for curvature visualization."""
    DIVERGING_BWR = "blue_white_red"  # Diverging: blue (neg) - white (0) - red (pos)
    DIVERGING_RWB = "red_white_blue"  # Diverging: red (neg) - white (0) - blue (pos)
    RAINBOW = "rainbow"                # Sequential: blue - cyan - green - yellow - red
    VIRIDIS = "viridis"                # Sequential: purple - blue - green - yellow
    COOL_WARM = "cool_warm"            # Diverging: blue - white - red (Paraview style)
    GRAYSCALE = "grayscale"            # Sequential: black - white


class CurvatureRenderer:
    """
    Renders curvature data as false-color mapped VTK surfaces.

    This class takes curvature scalar values and creates VTK actors
    with color-mapped visualization for analysis and presentation.
    """

    def __init__(self):
        """Initialize the curvature renderer."""
        self.current_actor = None
        self.current_polydata = None
        self.scalar_bar = None
        self.color_map_type = ColorMapType.DIVERGING_BWR
        self.curvature_type = CurvatureType.GAUSSIAN

        # Range control
        self.auto_range = True
        self.manual_range = (-1.0, 1.0)  # Used when auto_range is False

    def create_curvature_actor(
        self,
        polydata: vtk.vtkPolyData,
        curvature_values: np.ndarray,
        curvature_type: CurvatureType = CurvatureType.GAUSSIAN,
        color_map: ColorMapType = ColorMapType.DIVERGING_BWR,
        auto_range: bool = True,
        manual_range: Optional[Tuple[float, float]] = None,
        show_edges: bool = True
    ) -> vtk.vtkActor:
        """
        Create a VTK actor with false-color curvature mapping.

        Args:
            polydata: VTK polydata for the surface geometry
            curvature_values: Array of curvature values (per vertex or per face)
            curvature_type: Type of curvature being visualized
            color_map: Color map to use for visualization
            auto_range: If True, use data min/max; if False, use manual_range
            manual_range: (min, max) values for color mapping (used if auto_range=False)
            show_edges: If True, show mesh edges in dark gray

        Returns:
            vtkActor with curvature color mapping applied
        """
        self.curvature_type = curvature_type
        self.color_map_type = color_map
        self.auto_range = auto_range
        if manual_range:
            self.manual_range = manual_range

        # Create a copy of polydata to avoid modifying original
        polydata_copy = vtk.vtkPolyData()
        polydata_copy.DeepCopy(polydata)

        # Add curvature values as scalar field
        self._add_scalar_field(polydata_copy, curvature_values, curvature_type.value)

        # Create lookup table (color map)
        lut = self._create_lookup_table(
            curvature_values,
            color_map,
            auto_range,
            manual_range
        )

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata_copy)
        mapper.SetLookupTable(lut)
        mapper.SetScalarModeToUsePointData()

        # Set scalar range
        if auto_range:
            mapper.SetScalarRange(np.min(curvature_values), np.max(curvature_values))
        else:
            range_min, range_max = manual_range if manual_range else self.manual_range
            mapper.SetScalarRange(range_min, range_max)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Configure appearance
        actor.GetProperty().SetInterpolationToGouraud()  # Smooth shading

        if show_edges:
            actor.GetProperty().EdgeVisibilityOn()
            actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.2)  # Dark gray edges
            actor.GetProperty().SetLineWidth(0.5)
        else:
            actor.GetProperty().EdgeVisibilityOff()

        self.current_actor = actor
        self.current_polydata = polydata_copy

        return actor

    def create_scalar_bar(
        self,
        title: Optional[str] = None,
        num_labels: int = 5,
        width: float = 0.1,
        height: float = 0.6
    ) -> vtk.vtkScalarBarActor:
        """
        Create a color scale legend for the curvature visualization.

        Args:
            title: Title for the scalar bar (auto-generated if None)
            num_labels: Number of value labels to show
            width: Width of bar as fraction of window width (0-1)
            height: Height of bar as fraction of window height (0-1)

        Returns:
            vtkScalarBarActor for adding to renderer
        """
        if not self.current_actor:
            raise ValueError("Must create curvature actor before scalar bar")

        scalar_bar = vtk.vtkScalarBarActor()

        # Get lookup table from current actor's mapper
        mapper = self.current_actor.GetMapper()
        lut = mapper.GetLookupTable()
        scalar_bar.SetLookupTable(lut)

        # Set title
        if title is None:
            title = self._get_default_scalar_bar_title()
        scalar_bar.SetTitle(title)

        # Configure appearance
        scalar_bar.SetNumberOfLabels(num_labels)
        scalar_bar.SetWidth(width)
        scalar_bar.SetHeight(height)
        scalar_bar.SetPosition(1.0 - width - 0.05, 0.5 - height / 2)  # Right side, centered

        # Text properties
        scalar_bar.GetTitleTextProperty().SetColor(1.0, 1.0, 1.0)
        scalar_bar.GetTitleTextProperty().SetFontSize(14)
        scalar_bar.GetTitleTextProperty().BoldOn()

        scalar_bar.GetLabelTextProperty().SetColor(1.0, 1.0, 1.0)
        scalar_bar.GetLabelTextProperty().SetFontSize(12)

        self.scalar_bar = scalar_bar
        return scalar_bar

    def _add_scalar_field(
        self,
        polydata: vtk.vtkPolyData,
        values: np.ndarray,
        field_name: str
    ):
        """
        Add scalar values to polydata as point or cell data.

        Args:
            polydata: VTK polydata to modify
            values: Array of scalar values
            field_name: Name for the scalar field
        """
        num_points = polydata.GetNumberOfPoints()
        num_cells = polydata.GetNumberOfCells()

        # Create VTK array
        scalars = vtk.vtkFloatArray()
        scalars.SetName(field_name)

        # Determine if this is per-vertex or per-face data
        if len(values) == num_points:
            # Per-vertex data (most common)
            for value in values:
                scalars.InsertNextValue(float(value))
            polydata.GetPointData().SetScalars(scalars)

        elif len(values) == num_cells:
            # Per-face data
            for value in values:
                scalars.InsertNextValue(float(value))
            polydata.GetCellData().SetScalars(scalars)

        else:
            raise ValueError(
                f"Curvature values length ({len(values)}) doesn't match "
                f"points ({num_points}) or cells ({num_cells})"
            )

    def _create_lookup_table(
        self,
        values: np.ndarray,
        color_map: ColorMapType,
        auto_range: bool,
        manual_range: Optional[Tuple[float, float]]
    ) -> vtk.vtkLookupTable:
        """
        Create a VTK lookup table for the specified color map.

        Args:
            values: Curvature values (for range computation)
            color_map: Color map type
            auto_range: Use data range if True, manual_range if False
            manual_range: (min, max) for color mapping

        Returns:
            vtkLookupTable configured for the color map
        """
        lut = vtk.vtkLookupTable()

        # Determine range
        if auto_range:
            val_min, val_max = np.min(values), np.max(values)
        else:
            val_min, val_max = manual_range if manual_range else self.manual_range

        lut.SetTableRange(val_min, val_max)
        lut.SetNumberOfTableValues(256)

        # Build color map
        if color_map == ColorMapType.DIVERGING_BWR:
            self._build_diverging_bwr(lut, val_min, val_max)
        elif color_map == ColorMapType.DIVERGING_RWB:
            self._build_diverging_rwb(lut, val_min, val_max)
        elif color_map == ColorMapType.RAINBOW:
            self._build_rainbow(lut)
        elif color_map == ColorMapType.VIRIDIS:
            self._build_viridis(lut)
        elif color_map == ColorMapType.COOL_WARM:
            self._build_cool_warm(lut, val_min, val_max)
        elif color_map == ColorMapType.GRAYSCALE:
            self._build_grayscale(lut)
        else:
            # Default: rainbow
            self._build_rainbow(lut)

        lut.Build()
        return lut

    def _build_diverging_bwr(
        self,
        lut: vtk.vtkLookupTable,
        val_min: float,
        val_max: float
    ):
        """Build blue-white-red diverging color map (centered on zero)."""
        # For diverging maps, we want white at zero
        # Blue for negative, red for positive

        for i in range(256):
            t = i / 255.0  # 0 to 1

            # Map t to value in range
            value = val_min + t * (val_max - val_min)

            # Normalize by max absolute value for symmetric coloring
            max_abs = max(abs(val_min), abs(val_max))
            if max_abs > 0:
                norm_value = value / max_abs  # -1 to 1
            else:
                norm_value = 0

            # Clamp to [-1, 1]
            norm_value = np.clip(norm_value, -1, 1)

            if norm_value < 0:
                # Negative: blue to white
                intensity = 1.0 + norm_value  # 0 to 1
                r = intensity
                g = intensity
                b = 1.0
            else:
                # Positive: white to red
                intensity = 1.0 - norm_value  # 1 to 0
                r = 1.0
                g = intensity
                b = intensity

            lut.SetTableValue(i, r, g, b, 1.0)

    def _build_diverging_rwb(
        self,
        lut: vtk.vtkLookupTable,
        val_min: float,
        val_max: float
    ):
        """Build red-white-blue diverging color map (centered on zero)."""
        for i in range(256):
            t = i / 255.0
            value = val_min + t * (val_max - val_min)

            max_abs = max(abs(val_min), abs(val_max))
            if max_abs > 0:
                norm_value = value / max_abs
            else:
                norm_value = 0

            norm_value = np.clip(norm_value, -1, 1)

            if norm_value < 0:
                # Negative: red to white
                intensity = 1.0 + norm_value
                r = 1.0
                g = intensity
                b = intensity
            else:
                # Positive: white to blue
                intensity = 1.0 - norm_value
                r = intensity
                g = intensity
                b = 1.0

            lut.SetTableValue(i, r, g, b, 1.0)

    def _build_rainbow(self, lut: vtk.vtkLookupTable):
        """Build rainbow color map (blue -> cyan -> green -> yellow -> red)."""
        lut.SetHueRange(0.667, 0.0)  # Blue to red
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)

    def _build_viridis(self, lut: vtk.vtkLookupTable):
        """Build Viridis-like color map (perceptually uniform)."""
        # Approximate viridis with control points
        viridis_colors = [
            (0.267004, 0.004874, 0.329415),  # Dark purple
            (0.282623, 0.140926, 0.457517),  # Purple
            (0.253935, 0.265254, 0.529983),  # Blue
            (0.206756, 0.371758, 0.553117),  # Blue-green
            (0.163625, 0.471133, 0.558148),  # Teal
            (0.127568, 0.566949, 0.550556),  # Green-teal
            (0.134692, 0.658636, 0.517649),  # Green
            (0.266941, 0.748751, 0.440573),  # Yellow-green
            (0.477504, 0.821444, 0.318195),  # Yellow
            (0.741388, 0.873449, 0.149561),  # Light yellow
            (0.993248, 0.906157, 0.143936),  # Yellow
        ]

        for i in range(256):
            t = i / 255.0
            # Interpolate through color stops
            idx = t * (len(viridis_colors) - 1)
            idx_low = int(np.floor(idx))
            idx_high = min(idx_low + 1, len(viridis_colors) - 1)
            frac = idx - idx_low

            c_low = viridis_colors[idx_low]
            c_high = viridis_colors[idx_high]

            r = c_low[0] + frac * (c_high[0] - c_low[0])
            g = c_low[1] + frac * (c_high[1] - c_low[1])
            b = c_low[2] + frac * (c_high[2] - c_low[2])

            lut.SetTableValue(i, r, g, b, 1.0)

    def _build_cool_warm(
        self,
        lut: vtk.vtkLookupTable,
        val_min: float,
        val_max: float
    ):
        """Build cool-warm diverging color map (Paraview style)."""
        # Cool (blue) to neutral to warm (red)
        for i in range(256):
            t = i / 255.0
            value = val_min + t * (val_max - val_min)

            max_abs = max(abs(val_min), abs(val_max))
            if max_abs > 0:
                norm_value = value / max_abs
            else:
                norm_value = 0

            norm_value = np.clip(norm_value, -1, 1)

            # Cool-warm uses a more saturated transition
            if norm_value < 0:
                # Cool (blue)
                intensity = abs(norm_value)
                r = 0.23 + (1.0 - intensity) * 0.53
                g = 0.30 + (1.0 - intensity) * 0.46
                b = 0.75 + (1.0 - intensity) * 0.09
            else:
                # Warm (red)
                intensity = norm_value
                r = 0.76 + intensity * 0.10
                g = 0.76 - intensity * 0.36
                b = 0.84 - intensity * 0.61

            lut.SetTableValue(i, r, g, b, 1.0)

    def _build_grayscale(self, lut: vtk.vtkLookupTable):
        """Build grayscale color map (black to white)."""
        for i in range(256):
            intensity = i / 255.0
            lut.SetTableValue(i, intensity, intensity, intensity, 1.0)

    def _get_default_scalar_bar_title(self) -> str:
        """Generate default title for scalar bar based on curvature type."""
        type_names = {
            CurvatureType.GAUSSIAN: "Gaussian Curvature (K)",
            CurvatureType.MEAN: "Mean Curvature (H)",
            CurvatureType.PRINCIPAL_MIN: "Min Principal Curvature (κ₁)",
            CurvatureType.PRINCIPAL_MAX: "Max Principal Curvature (κ₂)",
            CurvatureType.ABSOLUTE_MEAN: "Absolute Mean Curvature (|H|)",
        }
        return type_names.get(self.curvature_type, "Curvature")

    def compute_curvature_from_mesh(
        self,
        polydata: vtk.vtkPolyData,
        curvature_type: CurvatureType = CurvatureType.GAUSSIAN
    ) -> np.ndarray:
        """
        Compute curvature values from mesh geometry using VTK's built-in estimators.

        This is a convenience method for quick visualization when exact
        SubD curvature analysis is not available.

        Args:
            polydata: VTK polydata with surface geometry
            curvature_type: Type of curvature to compute

        Returns:
            Array of curvature values per vertex
        """
        # Use VTK's curvature filter
        curvature_filter = vtk.vtkCurvatures()
        curvature_filter.SetInputData(polydata)

        if curvature_type == CurvatureType.GAUSSIAN:
            curvature_filter.SetCurvatureTypeToGaussian()
        elif curvature_type == CurvatureType.MEAN:
            curvature_filter.SetCurvatureTypeToMean()
        elif curvature_type == CurvatureType.PRINCIPAL_MIN:
            curvature_filter.SetCurvatureTypeToMinimum()
        elif curvature_type == CurvatureType.PRINCIPAL_MAX:
            curvature_filter.SetCurvatureTypeToMaximum()
        elif curvature_type == CurvatureType.ABSOLUTE_MEAN:
            curvature_filter.SetCurvatureTypeToMean()

        curvature_filter.Update()

        output = curvature_filter.GetOutput()
        scalars = output.GetPointData().GetScalars()

        # Convert to numpy array
        num_points = scalars.GetNumberOfTuples()
        values = np.zeros(num_points, dtype=np.float32)

        for i in range(num_points):
            values[i] = scalars.GetValue(i)

        # For absolute mean curvature, take absolute value
        if curvature_type == CurvatureType.ABSOLUTE_MEAN:
            values = np.abs(values)

        return values

    def update_color_map(self, color_map: ColorMapType):
        """
        Update the color map of the current actor.

        Args:
            color_map: New color map type
        """
        if not self.current_actor or not self.current_polydata:
            raise ValueError("No current actor to update")

        # Get current curvature values
        scalars = self.current_polydata.GetPointData().GetScalars()
        if not scalars:
            scalars = self.current_polydata.GetCellData().GetScalars()

        if not scalars:
            raise ValueError("No scalar data found on polydata")

        num_values = scalars.GetNumberOfTuples()
        values = np.zeros(num_values, dtype=np.float32)
        for i in range(num_values):
            values[i] = scalars.GetValue(i)

        # Create new lookup table
        lut = self._create_lookup_table(
            values,
            color_map,
            self.auto_range,
            self.manual_range if not self.auto_range else None
        )

        # Update mapper
        mapper = self.current_actor.GetMapper()
        mapper.SetLookupTable(lut)

        self.color_map_type = color_map

    def get_curvature_statistics(self, values: np.ndarray) -> Dict[str, float]:
        """
        Compute statistics for curvature values.

        Args:
            values: Array of curvature values

        Returns:
            Dictionary with min, max, mean, std, median, percentiles
        """
        return {
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "median": float(np.median(values)),
            "percentile_5": float(np.percentile(values, 5)),
            "percentile_95": float(np.percentile(values, 95)),
            "count": len(values)
        }


def create_test_curvature_visualization(
    curvature_type: CurvatureType = CurvatureType.GAUSSIAN,
    color_map: ColorMapType = ColorMapType.DIVERGING_BWR
) -> Tuple[vtk.vtkActor, vtk.vtkScalarBarActor]:
    """
    Create a test curvature visualization on a sphere.

    Sphere has known curvatures: K = 1/r², H = 1/r

    Args:
        curvature_type: Type of curvature to visualize
        color_map: Color map to use

    Returns:
        (actor, scalar_bar) tuple for adding to renderer
    """
    # Create test sphere
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(5.0)
    sphere_source.SetThetaResolution(40)
    sphere_source.SetPhiResolution(40)
    sphere_source.Update()

    polydata = sphere_source.GetOutput()

    # Create renderer
    renderer = CurvatureRenderer()

    # Compute curvature
    values = renderer.compute_curvature_from_mesh(polydata, curvature_type)

    # Create actor
    actor = renderer.create_curvature_actor(
        polydata,
        values,
        curvature_type=curvature_type,
        color_map=color_map,
        auto_range=True,
        show_edges=False
    )

    # Create scalar bar
    scalar_bar = renderer.create_scalar_bar()

    return actor, scalar_bar
