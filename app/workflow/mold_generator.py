"""
Mold Generation Workflow Orchestration

Complete end-to-end workflow: Region analysis → Constraint validation → NURBS generation → Export to Rhino.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass

import cpp_core
from app.state.parametric_region import ParametricRegion
from app.export.nurbs_serializer import NURBSSerializer
from app.ui.mold_params_dialog import MoldParameters


@dataclass
class MoldGenerationResult:
    """Complete mold generation result."""
    success: bool
    nurbs_surfaces: List  # OpenCASCADE surfaces
    constraint_reports: List  # Validation results
    export_data: Dict  # Serialized for Rhino
    error_message: str = ""


class MoldWorkflow:
    """
    Orchestrate end-to-end mold generation workflow.

    Steps:
    1. Validate regions (constraints)
    2. Generate NURBS from exact limit surface
    3. Apply draft transformation
    4. Create solid mold cavities
    5. Serialize for Rhino export
    """

    def __init__(self, evaluator: cpp_core.SubDEvaluator):
        self.evaluator = evaluator
        self.nurbs_gen = cpp_core.NURBSMoldGenerator(evaluator)
        self.constraint_val = cpp_core.ConstraintValidator(evaluator)
        self.serializer = NURBSSerializer()

    def generate_molds(self,
                      regions: List[ParametricRegion],
                      params: MoldParameters) -> MoldGenerationResult:
        """
        Generate complete mold set from regions.

        Args:
            regions: List of ParametricRegion objects
            params: Mold generation parameters

        Returns:
            MoldGenerationResult with NURBS surfaces and export data
        """
        try:
            # Step 1: Validate all regions
            print("Validating constraints...")
            reports = []
            for region in regions:
                report = self.constraint_val.validate_region(
                    region.faces,
                    cpp_core.Vector3(*params.demolding_direction),
                    params.wall_thickness
                )
                reports.append(report)

                # Check for errors
                if report.has_errors():
                    return MoldGenerationResult(
                        success=False,
                        nurbs_surfaces=[],
                        constraint_reports=reports,
                        export_data={},
                        error_message=f"Region {region.id} has constraint violations"
                    )

            print(f"All {len(regions)} regions validated ✓")

            # Step 2: Generate NURBS surfaces
            print("Generating NURBS surfaces from exact limit...")
            nurbs_surfaces = []

            for i, region in enumerate(regions):
                surface = self.nurbs_gen.fit_nurbs_surface(
                    region.faces,
                    sample_density=50
                )

                # Check fitting quality
                quality = self.nurbs_gen.check_fitting_quality(
                    surface, region.faces
                )

                if quality.max_deviation > 0.1:  # mm
                    print(f"Warning: Region {i} deviation {quality.max_deviation:.3f}mm")

                nurbs_surfaces.append((surface, region.id))

            print(f"Generated {len(nurbs_surfaces)} NURBS surfaces ✓")

            # Step 3: Apply draft angles
            print(f"Applying {params.draft_angle}° draft...")
            drafted_surfaces = []

            for surface, region_id in nurbs_surfaces:
                drafted = self.nurbs_gen.apply_draft_angle(
                    surface,
                    cpp_core.Vector3(*params.demolding_direction),
                    params.draft_angle,
                    []  # TODO: Extract parting line
                )
                drafted_surfaces.append((drafted, region_id))

            print("Draft applied ✓")

            # Step 4: Serialize for export
            print("Serializing for Rhino export...")
            export_data = self.serializer.serialize_mold_set(
                drafted_surfaces,
                metadata={
                    'draft_angle': params.draft_angle,
                    'wall_thickness': params.wall_thickness,
                    'demolding_direction': params.demolding_direction
                }
            )

            print("Export data ready ✓")

            return MoldGenerationResult(
                success=True,
                nurbs_surfaces=[s for s, _ in drafted_surfaces],
                constraint_reports=reports,
                export_data=export_data,
                error_message=""
            )

        except Exception as e:
            return MoldGenerationResult(
                success=False,
                nurbs_surfaces=[],
                constraint_reports=[],
                export_data={},
                error_message=str(e)
            )
