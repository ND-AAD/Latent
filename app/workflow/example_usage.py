"""
Example: Mold Generation Workflow Usage

Demonstrates complete workflow integration from UI to Rhino export.
"""

# NOTE: This is a reference example - requires cpp_core and full application context


def example_mold_generation_from_ui():
    """
    Example: User clicks 'Generate Molds' button in UI.

    Flow:
    1. User analyzes SubD and gets regions
    2. User clicks 'Generate Molds'
    3. Parameter dialog opens
    4. Workflow executes
    5. Results sent to Rhino
    """
    # Imports (would be at top of actual file)
    from app.workflow.mold_generator import MoldWorkflow
    from app.ui.mold_params_dialog import MoldParametersDialog
    import cpp_core

    # Assume we have:
    # - evaluator: cpp_core.SubDEvaluator (from current SubD)
    # - regions: List[ParametricRegion] (from analysis)
    # - bridge: RhinoBridge (for communication)

    # Show parameter dialog
    dialog = MoldParametersDialog()
    if dialog.exec():  # User clicked "Generate Molds"
        params = dialog.get_parameters()

        # Create workflow
        workflow = MoldWorkflow(evaluator)

        # Execute (with progress feedback)
        print("Starting mold generation...")
        result = workflow.generate_molds(regions, params)

        if result.success:
            print(f"✓ Successfully generated {len(result.nurbs_surfaces)} molds")

            # Show quality metrics
            for i, surface in enumerate(result.nurbs_surfaces):
                print(f"  Mold {i}: Quality check passed")

            # Send to Rhino
            bridge.post_molds(result.export_data)
            print("✓ Molds sent to Rhino")

            # Show success message to user
            # QMessageBox.information(parent, "Success", "Molds generated and sent to Rhino!")

        else:
            print(f"✗ Mold generation failed: {result.error_message}")

            # Show constraint violations if present
            if result.constraint_reports:
                print("\nConstraint validation details:")
                for i, report in enumerate(result.constraint_reports):
                    if report.has_errors():
                        print(f"  Region {i}: FAILED")
                        # Show specific errors
                    else:
                        print(f"  Region {i}: passed")

            # Show error to user
            # QMessageBox.warning(parent, "Error", result.error_message)


def example_batch_processing():
    """
    Example: Process multiple decompositions in batch.

    Useful for exploring different analytical lenses.
    """
    from app.workflow.mold_generator import MoldWorkflow
    from app.ui.mold_params_dialog import MoldParameters

    # Assume we have multiple region sets from different lenses
    region_sets = {
        'curvature': curvature_regions,
        'spectral': spectral_regions,
        'flow': flow_regions
    }

    params = MoldParameters(
        draft_angle=2.0,
        wall_thickness=40.0,
        demolding_direction=(0, 0, 1)
    )

    workflow = MoldWorkflow(evaluator)
    results = {}

    for lens_name, regions in region_sets.items():
        print(f"\nProcessing {lens_name} decomposition...")
        result = workflow.generate_molds(regions, params)

        if result.success:
            results[lens_name] = result
            print(f"  ✓ {len(result.nurbs_surfaces)} molds generated")

            # Calculate quality score
            avg_quality = sum(
                r.get_quality_score() for r in result.constraint_reports
            ) / len(result.constraint_reports)
            print(f"  Quality: {avg_quality:.2f}")
        else:
            print(f"  ✗ Failed: {result.error_message}")

    # Compare results and select best
    if results:
        best_lens = max(results.items(), key=lambda x: calculate_score(x[1]))
        print(f"\nBest decomposition: {best_lens[0]}")


def example_quality_inspection():
    """
    Example: Inspect NURBS fitting quality before export.

    Allows user to review quality metrics and adjust parameters.
    """
    from app.workflow.mold_generator import MoldWorkflow
    from app.ui.mold_params_dialog import MoldParameters

    params = MoldParameters(draft_angle=2.0, wall_thickness=40.0)
    workflow = MoldWorkflow(evaluator)

    # First pass: Check quality
    result = workflow.generate_molds(regions, params)

    if result.success:
        # Inspect each mold
        quality_issues = []

        for i, (surface, region_id) in enumerate(zip(result.nurbs_surfaces, regions)):
            quality = workflow.nurbs_gen.check_fitting_quality(surface, regions[i].faces)

            print(f"Mold {i} (Region {region_id}):")
            print(f"  Max deviation: {quality.max_deviation:.3f}mm")
            print(f"  RMS error: {quality.rms_error:.3f}mm")
            print(f"  Mean deviation: {quality.mean_deviation:.3f}mm")

            if quality.max_deviation > 0.1:
                quality_issues.append(i)
                print(f"  ⚠ Quality below threshold!")

        if quality_issues:
            print(f"\n{len(quality_issues)} molds have quality issues")
            # Option to re-generate with higher sample density
            # Option to manually inspect in 3D view
        else:
            print("\n✓ All molds meet quality standards")
            # Proceed to export


def example_constraint_validation_details():
    """
    Example: Detailed constraint violation reporting.

    Shows how to extract and display specific constraint failures.
    """
    from app.workflow.mold_generator import MoldWorkflow
    from app.ui.mold_params_dialog import MoldParameters

    params = MoldParameters(
        draft_angle=2.0,
        wall_thickness=40.0,
        demolding_direction=(0, 0, 1)
    )

    workflow = MoldWorkflow(evaluator)
    result = workflow.generate_molds(regions, params)

    if not result.success and "constraint violations" in result.error_message:
        print("Constraint Validation Failures:\n")

        for i, (region, report) in enumerate(zip(regions, result.constraint_reports)):
            print(f"Region {i} ({region.id}):")
            print(f"  Unity: {region.unity_principle} ({region.unity_strength:.2f})")

            if report.has_errors():
                print("  Status: FAILED ✗")

                # Undercut violations
                if report.has_undercuts:
                    print(f"  - Undercuts detected: {len(report.undercut_faces)} faces")
                    print(f"    Worst angle: {report.worst_undercut_angle:.1f}°")

                # Draft angle violations
                if report.has_insufficient_draft:
                    print(f"  - Insufficient draft: {len(report.low_draft_faces)} faces")
                    print(f"    Minimum found: {report.min_draft_angle:.1f}°")

                # Wall thickness violations
                if report.has_thin_walls:
                    print(f"  - Thin walls: {len(report.thin_faces)} faces")
                    print(f"    Minimum thickness: {report.min_thickness:.1f}mm")
            else:
                print("  Status: PASSED ✓")

            print()


def example_export_and_roundtrip():
    """
    Example: Export to Rhino and verify round-trip.

    Demonstrates data integrity validation.
    """
    from app.workflow.mold_generator import MoldWorkflow
    from app.ui.mold_params_dialog import MoldParameters
    import json

    params = MoldParameters(draft_angle=2.0, wall_thickness=40.0)
    workflow = MoldWorkflow(evaluator)

    # Generate molds
    result = workflow.generate_molds(regions, params)

    if result.success:
        # Validate export data structure
        export_data = result.export_data

        assert export_data['type'] == 'ceramic_mold_set'
        assert export_data['version'] == '1.0'
        assert len(export_data['molds']) == len(regions)
        assert 'timestamp' in export_data

        # Verify each mold has required NURBS data
        for mold_data in export_data['molds']:
            assert 'degree_u' in mold_data
            assert 'degree_v' in mold_data
            assert 'control_points' in mold_data
            assert 'weights' in mold_data
            assert 'knots_u' in mold_data
            assert 'knots_v' in mold_data

            # Verify data consistency
            num_points = len(mold_data['control_points'])
            assert num_points == len(mold_data['weights'])
            assert num_points == mold_data['count_u'] * mold_data['count_v']

        # Serialize to JSON (for network transfer)
        json_str = json.dumps(export_data, indent=2)
        print(f"Export package size: {len(json_str)} bytes")

        # Verify JSON is valid (round-trip)
        recovered = json.loads(json_str)
        assert recovered == export_data

        print("✓ Export data validated")

        # Send to Rhino
        bridge.post_molds(export_data)


def calculate_score(result):
    """Helper: Calculate overall quality score for a result."""
    if not result.success:
        return 0.0

    # Combine constraint validation scores
    constraint_score = sum(
        1.0 if not r.has_errors() else 0.0
        for r in result.constraint_reports
    ) / len(result.constraint_reports)

    # Could add NURBS quality metrics, etc.
    return constraint_score


if __name__ == '__main__':
    print("Mold Workflow Usage Examples")
    print("=" * 50)
    print("\nThese examples demonstrate workflow integration.")
    print("Run within full application context with cpp_core.")
    print("\nSee app/workflow/README.md for full documentation.")
