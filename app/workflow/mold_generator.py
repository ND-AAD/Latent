"""
Mold Generation Workflow Orchestration

Complete end-to-end workflow: Region analysis → Constraint validation → NURBS generation → Export to Rhino.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

try:
    import cpp_core
    CPP_CORE_AVAILABLE = True
except ImportError:
    CPP_CORE_AVAILABLE = False
    cpp_core = None

from app.state.parametric_region import ParametricRegion
from app.export.nurbs_serializer import NURBSSerializer
from app.ui.mold_params_dialog import MoldParameters
from app.utils.error_handling import get_logger, handle_exceptions

logger = get_logger(__name__)


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

    def __init__(self, evaluator):
        """
        Initialize mold workflow.

        Args:
            evaluator: SubDEvaluator instance

        Raises:
            RuntimeError: If cpp_core is not available or evaluator not initialized
        """
        if not CPP_CORE_AVAILABLE:
            raise RuntimeError(
                "cpp_core module not available. "
                "Please build the C++ module first:\n"
                "  cd cpp_core && mkdir build && cd build\n"
                "  cmake .. && make"
            )

        if evaluator is None:
            raise ValueError("Evaluator cannot be None")

        if not evaluator.is_initialized():
            raise RuntimeError(
                "Evaluator not initialized. "
                "Call evaluator.initialize(cage) before creating workflow."
            )

        self.evaluator = evaluator

        try:
            self.nurbs_gen = cpp_core.NURBSMoldGenerator(evaluator)
            self.constraint_val = cpp_core.ConstraintValidator(evaluator)
        except Exception as e:
            logger.error(f"Failed to initialize workflow components: {e}", exc_info=True)
            raise RuntimeError(f"Workflow initialization failed: {e}")

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
        # Validate inputs
        if not regions:
            logger.error("Cannot generate molds with no regions")
            return MoldGenerationResult(
                success=False,
                nurbs_surfaces=[],
                constraint_reports=[],
                export_data={},
                error_message="No regions provided for mold generation"
            )

        if params is None:
            logger.error("Mold parameters are None")
            return MoldGenerationResult(
                success=False,
                nurbs_surfaces=[],
                constraint_reports=[],
                export_data={},
                error_message="Invalid mold parameters"
            )

        try:
            # Step 1: Validate all regions
            logger.info(f"Validating {len(regions)} regions...")
            reports = []

            for i, region in enumerate(regions):
                try:
                    if not region.faces:
                        logger.warning(f"Region {region.id} has no faces, skipping")
                        continue

                    report = self.constraint_val.validate_region(
                        region.faces,
                        cpp_core.Vector3(*params.demolding_direction),
                        params.wall_thickness
                    )
                    reports.append(report)

                    # Check for errors
                    if report.has_errors():
                        error_msg = f"Region {region.id} has {report.error_count()} constraint violations"
                        logger.error(error_msg)
                        return MoldGenerationResult(
                            success=False,
                            nurbs_surfaces=[],
                            constraint_reports=reports,
                            export_data={},
                            error_message=error_msg
                        )

                    if report.has_warnings():
                        logger.warning(f"Region {region.id} has {report.warning_count()} warnings")

                except ValueError as e:
                    error_msg = f"Invalid parameters for region {region.id}: {e}"
                    logger.error(error_msg)
                    return MoldGenerationResult(
                        success=False,
                        nurbs_surfaces=[],
                        constraint_reports=reports,
                        export_data={},
                        error_message=error_msg
                    )
                except Exception as e:
                    error_msg = f"Validation failed for region {region.id}: {e}"
                    logger.error(error_msg, exc_info=True)
                    return MoldGenerationResult(
                        success=False,
                        nurbs_surfaces=[],
                        constraint_reports=reports,
                        export_data={},
                        error_message=error_msg
                    )

            logger.info(f"All {len(regions)} regions validated successfully")

            # Step 2: Generate NURBS surfaces
            logger.info("Generating NURBS surfaces from exact limit surface...")
            nurbs_surfaces = []

            for i, region in enumerate(regions):
                try:
                    if not region.faces:
                        continue

                    logger.debug(f"Fitting NURBS for region {region.id} ({len(region.faces)} faces)")

                    surface = self.nurbs_gen.fit_nurbs_surface(
                        region.faces,
                        sample_density=50
                    )

                    # Check fitting quality
                    quality = self.nurbs_gen.check_fitting_quality(
                        surface, region.faces
                    )

                    logger.info(
                        f"Region {region.id} NURBS quality: "
                        f"max={quality.max_deviation:.4f}mm, "
                        f"rms={quality.rms_deviation:.4f}mm"
                    )

                    if quality.max_deviation > 0.1:  # mm
                        error_msg = (
                            f"Region {region.id} NURBS fitting quality poor: "
                            f"max deviation {quality.max_deviation:.3f}mm exceeds 0.1mm tolerance"
                        )
                        logger.error(error_msg)
                        return MoldGenerationResult(
                            success=False,
                            nurbs_surfaces=nurbs_surfaces,
                            constraint_reports=reports,
                            export_data={},
                            error_message=error_msg
                        )

                    nurbs_surfaces.append((surface, region.id))

                except ValueError as e:
                    error_msg = f"Invalid NURBS parameters for region {region.id}: {e}"
                    logger.error(error_msg)
                    return MoldGenerationResult(
                        success=False,
                        nurbs_surfaces=nurbs_surfaces,
                        constraint_reports=reports,
                        export_data={},
                        error_message=error_msg
                    )
                except RuntimeError as e:
                    error_msg = f"NURBS fitting failed for region {region.id}: {e}"
                    logger.error(error_msg, exc_info=True)
                    return MoldGenerationResult(
                        success=False,
                        nurbs_surfaces=nurbs_surfaces,
                        constraint_reports=reports,
                        export_data={},
                        error_message=error_msg
                    )

            logger.info(f"Generated {len(nurbs_surfaces)} NURBS surfaces successfully")

            # Step 3: Apply draft angles
            logger.info(f"Applying {params.draft_angle}° draft angle...")
            drafted_surfaces = []

            for surface, region_id in nurbs_surfaces:
                try:
                    drafted = self.nurbs_gen.apply_draft_angle(
                        surface,
                        cpp_core.Vector3(*params.demolding_direction),
                        params.draft_angle,
                        []  # TODO: Extract parting line
                    )
                    drafted_surfaces.append((drafted, region_id))
                    logger.debug(f"Applied draft to region {region_id}")

                except Exception as e:
                    error_msg = f"Draft transformation failed for region {region_id}: {e}"
                    logger.error(error_msg, exc_info=True)
                    return MoldGenerationResult(
                        success=False,
                        nurbs_surfaces=nurbs_surfaces,
                        constraint_reports=reports,
                        export_data={},
                        error_message=error_msg
                    )

            logger.info("Draft angles applied successfully")

            # Step 4: Serialize for export
            logger.info("Serializing mold data for Rhino export...")
            try:
                export_data = self.serializer.serialize_mold_set(
                    drafted_surfaces,
                    metadata={
                        'draft_angle': params.draft_angle,
                        'wall_thickness': params.wall_thickness,
                        'demolding_direction': params.demolding_direction
                    }
                )
                logger.info("Export data serialized successfully")

            except Exception as e:
                error_msg = f"Serialization failed: {e}"
                logger.error(error_msg, exc_info=True)
                return MoldGenerationResult(
                    success=False,
                    nurbs_surfaces=[s for s, _ in drafted_surfaces],
                    constraint_reports=reports,
                    export_data={},
                    error_message=error_msg
                )

            return MoldGenerationResult(
                success=True,
                nurbs_surfaces=[s for s, _ in drafted_surfaces],
                constraint_reports=reports,
                export_data=export_data,
                error_message=""
            )

        except Exception as e:
            error_msg = f"Unexpected error during mold generation: {e}"
            logger.error(error_msg, exc_info=True)
            return MoldGenerationResult(
                success=False,
                nurbs_surfaces=[],
                constraint_reports=[],
                export_data={},
                error_message=error_msg
            )
