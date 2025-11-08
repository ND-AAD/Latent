#!/usr/bin/env python3
"""
Utility to kill processes on port 8888 and clean up Python instances
Run this to get a clean slate before starting servers
"""

import os
import subprocess
import sys
import time

def kill_port(port=8888):
    """Kill any process using the specified port"""
    print(f"🔍 Checking for processes on port {port}...")

    try:
        # Find processes using the port
        result = subprocess.run(
            f"lsof -ti:{port}",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"📍 Found {len(pids)} process(es) on port {port}")

            for pid in pids:
                if pid:
                    print(f"   Killing PID {pid}...")
                    subprocess.run(f"kill -9 {pid}", shell=True)

            print(f"✅ Killed all processes on port {port}")
            return True
        else:
            print(f"✓ Port {port} is already free")
            return False

    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False

def kill_python_apps():
    """Kill any running Python app instances"""
    print("\n🔍 Checking for running Python apps...")

    patterns = [
        "python3.*launch.py",
        "python3.*main.py",
        "python3.*test_rhino"
    ]

    killed_any = False
    for pattern in patterns:
        try:
            result = subprocess.run(
                f'pkill -f "{pattern}"',
                shell=True,
                capture_output=True
            )

            # Check if any processes were killed
            check = subprocess.run(
                f'pgrep -f "{pattern}"',
                shell=True,
                capture_output=True,
                text=True
            )

            if not check.stdout.strip():
                if result.returncode == 0:
                    print(f"   ✓ Killed processes matching: {pattern}")
                    killed_any = True

        except Exception as e:
            pass

    if killed_any:
        print("✅ Cleaned up Python app instances")
    else:
        print("✓ No Python app instances were running")

    return killed_any

def verify_clean():
    """Verify the port is free and no apps running"""
    print("\n🔍 Verifying clean state...")

    # Check port
    result = subprocess.run(
        f"lsof -ti:8888",
        shell=True,
        capture_output=True,
        text=True
    )

    port_free = not result.stdout.strip()

    # Check for Python apps
    patterns = ["launch.py", "main.py"]
    apps_running = False

    for pattern in patterns:
        check = subprocess.run(
            f'pgrep -f "python3.*{pattern}"',
            shell=True,
            capture_output=True,
            text=True
        )
        if check.stdout.strip():
            apps_running = True
            break

    if port_free and not apps_running:
        print("✅ Clean state verified:")
        print("   • Port 8888 is free")
        print("   • No Python apps running")
        return True
    else:
        if not port_free:
            print("⚠️  Port 8888 is still in use")
        if apps_running:
            print("⚠️  Some Python apps are still running")
        return False

def main():
    """Main cleanup routine"""
    print("=" * 60)
    print("PORT AND PROCESS CLEANUP UTILITY")
    print("=" * 60)

    # Kill processes on port 8888
    port_killed = kill_port(8888)

    # Kill Python app instances
    apps_killed = kill_python_apps()

    # Wait a moment for processes to fully terminate
    if port_killed or apps_killed:
        print("\n⏳ Waiting for processes to terminate...")
        time.sleep(2)

    # Verify everything is clean
    clean = verify_clean()

    print("\n" + "=" * 60)

    if clean:
        print("SUCCESS! Ready to start fresh.")
        print("\nNext steps:")
        print("1. In Grasshopper: Run the mesh server script")
        print("2. In Terminal: python3 launch.py")
        print("3. In App: File → Connect to Rhino")
    else:
        print("WARNING: Some processes may still be running.")
        print("Try running this script again or manually check:")
        print("  lsof -i:8888")
        print("  ps aux | grep python")

    print("=" * 60)

    return 0 if clean else 1

if __name__ == "__main__":
    sys.exit(main())