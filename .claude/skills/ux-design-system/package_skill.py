#!/usr/bin/env python3
"""
Package the UX Design System skill for distribution
Creates a .skill archive that can be easily installed
"""

import os
import zipfile
import json
import yaml
from datetime import datetime
from pathlib import Path

def package_skill():
    """Package the skill into a distributable format"""

    print("UX Design System Skill Packager")
    print("=" * 40)

    skill_name = "ux-design-system"

    # Validate skill structure first
    if not os.path.exists("SKILL.md"):
        print("❌ Error: SKILL.md not found. Run from skill directory.")
        return False

    # Parse metadata
    with open("SKILL.md", "r") as f:
        content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            try:
                metadata = yaml.safe_load(parts[1])
                skill_name = metadata.get("name", skill_name)
                print(f"📦 Packaging skill: {skill_name}")
            except yaml.YAMLError as e:
                print(f"⚠️  Warning: Could not parse metadata: {e}")

    # Create package manifest
    manifest = {
        "name": skill_name,
        "version": "1.0.0",
        "created": datetime.now().isoformat(),
        "structure": {
            "core": ["SKILL.md"],
            "references": [],
            "scripts": [],
            "assets": []
        }
    }

    # Collect all files
    files_to_package = ["SKILL.md", "validate_skill.py"]

    # Add references
    if os.path.exists("references"):
        for ref_file in Path("references").glob("*.md"):
            files_to_package.append(str(ref_file))
            manifest["structure"]["references"].append(ref_file.name)

    # Add scripts
    if os.path.exists("scripts"):
        for script_file in Path("scripts").glob("*.py"):
            files_to_package.append(str(script_file))
            manifest["structure"]["scripts"].append(script_file.name)

    # Add assets
    if os.path.exists("assets"):
        for asset_file in Path("assets").iterdir():
            files_to_package.append(str(asset_file))
            manifest["structure"]["assets"].append(asset_file.name)

    # Add documentation
    if os.path.exists("INSTALL.md"):
        files_to_package.append("INSTALL.md")

    # Create package
    package_name = f"{skill_name}.skill"

    print(f"\n📋 Files to package: {len(files_to_package)}")

    try:
        with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add manifest
            zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

            # Add all files
            for file_path in files_to_package:
                if os.path.exists(file_path):
                    arcname = f"{skill_name}/{file_path}"
                    zipf.write(file_path, arcname)
                    print(f"   ✅ Added: {file_path}")
                else:
                    print(f"   ⚠️  Skipped (not found): {file_path}")

        # Get package size
        package_size = os.path.getsize(package_name)
        size_kb = package_size / 1024

        print(f"\n✅ Package created successfully!")
        print(f"📦 Package: {package_name}")
        print(f"📏 Size: {size_kb:.2f} KB")
        print(f"\n📥 To install:")
        print(f"   1. Copy {package_name} to your project")
        print(f"   2. Extract to .claude/skills/ directory")
        print(f"   3. Or use: unzip {package_name} -d .claude/skills/")

        return True

    except Exception as e:
        print(f"❌ Error creating package: {e}")
        return False

def unpack_skill(package_path, target_dir="."):
    """Unpack a .skill package"""

    print(f"Unpacking {package_path}...")

    try:
        with zipfile.ZipFile(package_path, 'r') as zipf:
            # Check for manifest
            if "manifest.json" in zipf.namelist():
                manifest_data = zipf.read("manifest.json")
                manifest = json.loads(manifest_data)
                print(f"📦 Skill: {manifest['name']}")
                print(f"📅 Created: {manifest['created']}")

            # Extract all files
            zipf.extractall(target_dir)
            print(f"✅ Unpacked to: {target_dir}")

            return True

    except Exception as e:
        print(f"❌ Error unpacking: {e}")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "unpack":
        if len(sys.argv) > 2:
            package_file = sys.argv[2]
            target = sys.argv[3] if len(sys.argv) > 3 else "."
            unpack_skill(package_file, target)
        else:
            print("Usage: python package_skill.py unpack <package.skill> [target_dir]")
    else:
        # Change to skill directory
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(skill_dir)

        # Package the skill
        package_skill()