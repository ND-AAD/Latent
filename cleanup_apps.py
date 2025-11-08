#!/usr/bin/env python3
"""
Cleanup only Python apps, NOT Rhino/Grasshopper
Use this to stop twitching without crashing Rhino
"""

import os
import subprocess
import sys
import time

def kill_python_apps_only():
    """Kill ALL Python desktop app instances aggressively"""
    print("=" * 60)
    print("AGGRESSIVE CLEANUP - Kill ALL Python App Instances")
    print("(This will NOT affect Rhino/Grasshopper)")
    print("=" * 60)

    print("\n🔍 Finding and killing ALL Python app instances...")

    # More aggressive patterns to catch everything
    patterns = [
        "python3.*launch\\.py",
        "python3.*main\\.py",
        "python3.*test_rhino",
        "Python.*launch\\.py",  # Sometimes shows as Python
        "python.*launch\\.py"   # Sometimes lowercase
    ]

    total_killed = 0

    # First, use pkill to kill all matching processes
    for pattern in patterns:
        subprocess.run(f'pkill -9 -f "{pattern}"', shell=True, stderr=subprocess.DEVNULL)

    # Then use killall as backup
    subprocess.run("killall -9 python3 2>/dev/null", shell=True)
    subprocess.run("killall -9 Python 2>/dev/null", shell=True)

    # Wait a moment for processes to die
    time.sleep(1)

    # Now verify what we killed
    for pattern in patterns:
        try:
            # Check if any processes were killed
            result = subprocess.run(
                f'pgrep -f "{pattern}"',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                print(f"\n⚠️ Still found {len(pids)} stubborn instance(s) of: {pattern}")

                # Force kill them again
                for pid in pids:
                    if pid:
                        print(f"   FORCE killing PID {pid}")
                        subprocess.run(f"kill -9 {pid}", shell=True)
                        subprocess.run(f"kill -KILL {pid}", shell=True)
                        total_killed += 1
            else:
                print(f"✓ Killed all: {pattern}")

        except Exception as e:
            pass

    # Final aggressive cleanup
    print("\n🔨 Final cleanup pass...")
    subprocess.run("pkill -9 -f 'ceramic_mold_analyzer.*python'", shell=True, stderr=subprocess.DEVNULL)

    # Wait for everything to die
    time.sleep(1)

    # Count how many are still running (should be 0)
    check = subprocess.run(
        "ps aux | grep -E 'python3.*(launch|main)' | grep -v grep | wc -l",
        shell=True,
        capture_output=True,
        text=True
    )

    remaining = int(check.stdout.strip())

    if remaining == 0:
        print("\n✅ SUCCESS! All Python app instances killed!")
        print("   The twitching should stop now!")
    else:
        print(f"\n⚠️ WARNING: {remaining} instance(s) may still be running")
        print("   Try running this script again with sudo:")
        print("   sudo python3 cleanup_apps.py")

    # Do NOT touch port 8888 - let Rhino keep running
    print("\n📝 Note: Rhino server on port 8888 is unchanged")
    print("   (To restart server, use Boolean Toggle in Grasshopper)")

    return total_killed

def verify_rhino_still_running():
    """Check if Rhino is still running (good!)"""
    print("\n🔍 Verifying Rhino status...")

    # Check if Rhino process exists
    result = subprocess.run(
        'pgrep -i "rhino"',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print("✅ Rhino is still running (good!)")

        # Check if port 8888 is still open
        port_check = subprocess.run(
            "lsof -ti:8888",
            shell=True,
            capture_output=True,
            text=True
        )

        if port_check.stdout.strip():
            print("✅ Server on port 8888 is active")
            return True
        else:
            print("⚠️ Server on port 8888 may need restart in Grasshopper")
            return False
    else:
        print("⚠️ Rhino is not running")
        return False

def main():
    """Main cleanup routine"""

    # Kill Python apps only
    killed = kill_python_apps_only()

    # Wait for processes to terminate
    if killed > 0:
        print("\n⏳ Waiting for cleanup...")
        time.sleep(1)

    # Verify Rhino is OK
    rhino_ok = verify_rhino_still_running()

    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)

    if rhino_ok:
        print("\n✅ Safe cleanup successful!")
        print("\nNext steps:")
        print("1. The twitching should have stopped")
        print("2. Run: python3 launch.py (ONE instance only)")
        print("3. In app: File → Connect to Rhino")
        print("\nYour geometry should display smoothly now!")
    else:
        print("\n⚠️ You may need to:")
        print("1. Check Grasshopper server component")
        print("2. Toggle the Boolean input to restart server")

    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())