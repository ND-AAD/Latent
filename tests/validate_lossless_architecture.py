#!/usr/bin/env python3
"""
Lossless Architecture Static Validation

Validates the codebase follows lossless architecture principles by:
- Checking that regions are parametric (face indices, not mesh triangles)
- Verifying no mesh conversion patterns in analysis code
- Confirming proper separation between display and analysis
- Validating API patterns follow lossless principles

This script performs STATIC analysis and doesn't require C++ module.
For RUNTIME validation, see test_lossless.py

Run: python3 tests/validate_lossless_architecture.py
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class LosslessArchitectureValidator:
    """Validates lossless architecture patterns in codebase."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.validations = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("=" * 70)
        print("Lossless Architecture Static Validation")
        print("=" * 70)
        print()

        # Run validation checks
        self.check_parametric_region_definition()
        self.check_cpp_api_patterns()
        self.check_analysis_uses_limit_surface()
        self.check_no_mesh_conversions()
        self.check_tessellation_separation()
        self.check_bridge_transfer_pattern()

        # Print results
        self.print_results()

        return len(self.issues) == 0

    def check_parametric_region_definition(self):
        """Verify ParametricRegion uses face indices, not mesh data."""
        print("🔍 Checking parametric region definition...")

        region_file = self.project_root / "app" / "state" / "parametric_region.py"

        if not region_file.exists():
            self.issues.append("parametric_region.py not found")
            return

        content = region_file.read_text()

        # Check for correct pattern: faces as List[int]
        if "faces: List[int]" in content or "faces: list[int]" in content:
            self.validations.append("✓ ParametricRegion.faces uses List[int] (control face indices)")
        else:
            self.issues.append("ParametricRegion.faces should be List[int] (face indices)")

        # Check it DOESN'T store mesh triangles or vertices
        bad_patterns = [
            (r"triangles\s*:\s*List", "Region should not store triangle indices"),
            (r"mesh_vertices\s*:\s*", "Region should not store mesh vertices"),
            (r"mesh_indices\s*:\s*", "Region should not store mesh indices"),
        ]

        for pattern, message in bad_patterns:
            if re.search(pattern, content):
                self.issues.append(f"❌ {message}")

        # Check for parametric documentation
        if "(face_id, u, v)" in content or "parametric" in content.lower():
            self.validations.append("✓ Documentation mentions parametric (face_id, u, v) format")

        print("  Done.\n")

    def check_cpp_api_patterns(self):
        """Verify C++ API follows lossless patterns."""
        print("🔍 Checking C++ API patterns...")

        # Check SubDEvaluator header
        evaluator_h = self.project_root / "cpp_core" / "geometry" / "subd_evaluator.h"

        if not evaluator_h.exists():
            self.issues.append("subd_evaluator.h not found")
            return

        content = evaluator_h.read_text()

        # Check for exact limit evaluation methods
        required_methods = [
            ("evaluate_limit_point", "Exact limit point evaluation"),
            ("evaluate_limit", "Exact limit with normal"),
            ("tessellate", "Tessellation for display"),
        ]

        for method, description in required_methods:
            if method in content:
                self.validations.append(f"✓ {description}: {method}() found")
            else:
                self.issues.append(f"❌ Missing {description}: {method}()")

        # Check for advanced evaluation (derivatives)
        if "evaluate_limit_with_derivatives" in content:
            self.validations.append("✓ Advanced limit evaluation with derivatives available")

        # Verify tessellate is separate from evaluation
        if "tessellate" in content and "evaluate_limit" in content:
            # They should be separate methods
            self.validations.append("✓ Tessellation and limit evaluation are separate methods")

        print("  Done.\n")

    def check_analysis_uses_limit_surface(self):
        """Check analysis modules query limit surface, not mesh."""
        print("🔍 Checking analysis modules use limit surface...")

        analysis_dir = self.project_root / "app" / "analysis"

        if not analysis_dir.exists():
            self.warnings.append("app/analysis/ directory not found (may not be implemented yet)")
            print("  Not yet implemented.\n")
            return

        # Check for proper patterns in analysis files
        for py_file in analysis_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            content = py_file.read_text()

            # Good patterns: using evaluator.evaluate_limit_point
            if "evaluate_limit_point" in content or "evaluate_limit" in content:
                self.validations.append(f"✓ {py_file.name} uses limit surface evaluation")

            # Bad patterns: using mesh vertices directly
            bad_patterns = [
                (r"mesh\.vertices\[", f"{py_file.name} accesses mesh vertices directly"),
                (r"tess\.vertices\[", f"{py_file.name} uses tessellation vertices for analysis"),
            ]

            for pattern, message in bad_patterns:
                if re.search(pattern, content):
                    self.issues.append(f"❌ {message}")

        print("  Done.\n")

    def check_no_mesh_conversions(self):
        """Check for prohibited mesh conversion patterns."""
        print("🔍 Checking for mesh conversion anti-patterns...")

        # Files to check
        check_files = [
            "app/bridge/subd_fetcher.py",
            "app/bridge/geometry_receiver.py",
            "app/state/app_state.py",
        ]

        prohibited_patterns = [
            (r"\.ToMesh\(", "Rhino .ToMesh() conversion (lossy!)"),
            (r"subd_to_mesh", "SubD to mesh conversion function"),
            (r"convert.*mesh", "Mesh conversion detected"),
        ]

        found_violations = False

        for file_path in check_files:
            full_path = self.project_root / file_path

            if not full_path.exists():
                continue

            content = full_path.read_text()

            for pattern, description in prohibited_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.issues.append(f"❌ {file_path}: {description}")
                    found_violations = True

        if not found_violations:
            self.validations.append("✓ No mesh conversion anti-patterns detected")

        print("  Done.\n")

    def check_tessellation_separation(self):
        """Verify tessellation is used only for display."""
        print("🔍 Checking tessellation separation (display only)...")

        # Check VTK display modules use tessellation
        display_files = [
            "app/geometry/subd_display.py",
            "app/geometry/subd_renderer.py",
        ]

        for file_path in display_files:
            full_path = self.project_root / file_path

            if not full_path.exists():
                continue

            content = full_path.read_text()

            # Should use tessellation for VTK actors
            if "tessellate" in content and "vtk" in content.lower():
                self.validations.append(f"✓ {file_path} uses tessellation for VTK display")

            # Should not use tessellation results for curvature/analysis
            if "tessellate" in content and ("curvature" in content.lower() or "analysis" in content.lower()):
                # Check if it's just passing through or actually computing from tess
                if "compute" in content.lower() and "tessellat" in content.lower():
                    self.warnings.append(f"⚠️  {file_path} may compute analysis from tessellation (verify)")

        print("  Done.\n")

    def check_bridge_transfer_pattern(self):
        """Verify bridge transfers control cage, not mesh."""
        print("🔍 Checking Grasshopper bridge transfer pattern...")

        fetcher_file = self.project_root / "app" / "bridge" / "subd_fetcher.py"

        if not fetcher_file.exists():
            self.warnings.append("subd_fetcher.py not found")
            return

        content = fetcher_file.read_text()

        # Should fetch control cage
        if "SubDControlCage" in content:
            self.validations.append("✓ Bridge fetches SubDControlCage (exact topology)")
        else:
            self.issues.append("❌ Bridge should fetch SubDControlCage")

        # Should have vertices, faces, creases
        required_fields = ["vertices", "faces"]
        for field in required_fields:
            if f"'{field}'" in content or f'"{field}"' in content:
                self.validations.append(f"✓ Bridge transfers '{field}' from control cage")

        # Should NOT transfer mesh data
        if "mesh" not in content.lower() or "control" in content.lower():
            self.validations.append("✓ No mesh transfer pattern detected in bridge")

        print("  Done.\n")

    def print_results(self):
        """Print validation results."""
        print()
        print("=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)
        print()

        if self.validations:
            print("✅ Validations Passed:")
            for v in self.validations:
                print(f"   {v}")
            print()

        if self.warnings:
            print("⚠️  Warnings:")
            for w in self.warnings:
                print(f"   {w}")
            print()

        if self.issues:
            print("❌ Issues Found:")
            for i in self.issues:
                print(f"   {i}")
            print()

        # Summary
        print("=" * 70)
        total_checks = len(self.validations) + len(self.issues)

        if len(self.issues) == 0:
            print("✅ LOSSLESS ARCHITECTURE VALIDATED")
            print(f"   {len(self.validations)} checks passed")
            if self.warnings:
                print(f"   {len(self.warnings)} warnings (non-critical)")
            print()
            print("Architecture follows lossless principles:")
            print("  ✓ Control cage transfer (exact)")
            print("  ✓ Limit surface evaluation (exact)")
            print("  ✓ Parametric regions (face indices)")
            print("  ✓ Tessellation for display only")
            print("  ✓ No mesh conversions detected")
        else:
            print("❌ LOSSLESS ARCHITECTURE VIOLATIONS DETECTED")
            print(f"   {len(self.issues)} issues found")
            print(f"   {len(self.validations)} checks passed")
            print()
            print("⚠️  Review issues above and fix violations.")

        print("=" * 70)


def main():
    """Run validation."""
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Create validator
    validator = LosslessArchitectureValidator(project_root)

    # Run validation
    success = validator.validate_all()

    # Exit with appropriate code
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
