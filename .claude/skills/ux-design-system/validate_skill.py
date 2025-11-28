#!/usr/bin/env python3
"""
UX Design System Skill Validator
Ensures all skill components are present and properly structured
"""

import os
import json
import yaml
from pathlib import Path

def validate_skill_structure():
    """Validate the skill follows proper structure"""

    print("UX Design System Skill Validator")
    print("=" * 40)

    errors = []
    warnings = []

    # Check SKILL.md exists
    if not os.path.exists("SKILL.md"):
        errors.append("❌ SKILL.md file not found")
    else:
        print("✅ SKILL.md found")

        # Validate frontmatter
        with open("SKILL.md", "r") as f:
            content = f.read()
            if not content.startswith("---"):
                errors.append("❌ SKILL.md missing YAML frontmatter")
            else:
                # Extract frontmatter
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    try:
                        metadata = yaml.safe_load(parts[1])
                        if "name" not in metadata:
                            errors.append("❌ Missing 'name' in frontmatter")
                        if "description" not in metadata:
                            errors.append("❌ Missing 'description' in frontmatter")
                        else:
                            print(f"✅ Skill name: {metadata.get('name')}")
                            print(f"✅ Description present ({len(metadata['description'])} chars)")
                    except yaml.YAMLError as e:
                        errors.append(f"❌ Invalid YAML frontmatter: {e}")

        # Check file size
        file_size = len(content.split('\n'))
        if file_size > 500:
            warnings.append(f"⚠️  SKILL.md has {file_size} lines (recommended < 500)")
        else:
            print(f"✅ SKILL.md size: {file_size} lines")

    # Check references directory
    if os.path.exists("references"):
        ref_files = list(Path("references").glob("*.md"))
        print(f"✅ References directory found with {len(ref_files)} files")
        for ref_file in ref_files:
            print(f"   - {ref_file.name}")
    else:
        warnings.append("⚠️  No references directory found")

    # Check scripts directory
    if os.path.exists("scripts"):
        script_files = list(Path("scripts").glob("*.py"))
        print(f"✅ Scripts directory found with {len(script_files)} files")
        for script_file in script_files:
            print(f"   - {script_file.name}")
            # Check if script is executable
            if not os.access(script_file, os.X_OK):
                warnings.append(f"⚠️  {script_file.name} is not executable")
    else:
        warnings.append("⚠️  No scripts directory found")

    # Check assets directory
    if os.path.exists("assets"):
        asset_files = list(Path("assets").iterdir())
        print(f"✅ Assets directory found with {len(asset_files)} files")
        for asset_file in asset_files:
            print(f"   - {asset_file.name}")
    else:
        warnings.append("⚠️  No assets directory found")

    # Summary
    print("\n" + "=" * 40)
    print("Validation Summary")
    print("=" * 40)

    if errors:
        print(f"\n❌ {len(errors)} Error(s) Found:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ No errors found!")

    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for warning in warnings:
            print(f"  {warning}")

    if not errors:
        print("\n🎉 Skill is valid and ready to use!")
        return True
    else:
        print("\n❌ Please fix errors before using the skill")
        return False

def check_skill_content():
    """Check skill content quality"""

    print("\n" + "=" * 40)
    print("Content Quality Check")
    print("=" * 40)

    checks = {
        "Core UX principles": False,
        "Design process workflow": False,
        "Evaluation methods": False,
        "Accessibility guidelines": False,
        "Component patterns": False,
        "Scripts referenced": False,
        "Progressive disclosure": False
    }

    with open("SKILL.md", "r") as f:
        content = f.read().lower()

        # Check for key concepts
        if "visual hierarchy" in content and "cognitive load" in content:
            checks["Core UX principles"] = True

        if "discovery" in content and "design" in content and "evaluate" in content:
            checks["Design process workflow"] = True

        if "heuristic" in content or "nielsen" in content:
            checks["Evaluation methods"] = True

        if "wcag" in content or "accessibility" in content:
            checks["Accessibility guidelines"] = True

        if "component" in content and "atomic" in content:
            checks["Component patterns"] = True

        if "scripts/" in content:
            checks["Scripts referenced"] = True

        if "references/" in content:
            checks["Progressive disclosure"] = True

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    passed_checks = sum(checks.values())
    total_checks = len(checks)

    print(f"\nQuality Score: {passed_checks}/{total_checks}")

    if passed_checks == total_checks:
        print("🌟 Excellent! All quality checks passed!")
    elif passed_checks >= total_checks * 0.7:
        print("👍 Good! Most quality checks passed.")
    else:
        print("⚠️  Consider adding more UX content to the skill.")

if __name__ == "__main__":
    # Change to skill directory
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(skill_dir)

    # Run validation
    if validate_skill_structure():
        check_skill_content()

    print("\n" + "=" * 40)
    print("Validation Complete")
    print("=" * 40)