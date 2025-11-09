# -*- coding: utf-8 -*-
"""Live geometry synchronization between Rhino and desktop app."""

import hashlib
import json
from typing import Optional, Callable
from PyQt6.QtCore import QTimer
import sys
from pathlib import Path

# Add cpp_core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'cpp_core' / 'build'))

try:
    import cpp_core
except ImportError:
    print("Warning: cpp_core module not available. Build C++ module first.")
    cpp_core = None

from .subd_fetcher import SubDFetcher


class LiveBridge:
    """Manage live connection to Grasshopper server."""

    def __init__(self,
                 fetcher: SubDFetcher,
                 on_geometry_changed: Callable,
                 poll_interval_ms: int = 2000):
        """Initialize live bridge.

        Args:
            fetcher: SubDFetcher instance
            on_geometry_changed: Callback when geometry changes
            poll_interval_ms: Polling interval in milliseconds
        """
        self.fetcher = fetcher
        self.on_geometry_changed = on_geometry_changed
        self.poll_interval_ms = poll_interval_ms

        self.timer = QTimer()
        self.timer.timeout.connect(self._check_for_updates)

        self.is_connected = False
        self.current_hash = None
        self.last_cage = None

    def start(self):
        """Start live sync."""
        if not self.fetcher.is_server_available():
            print("[ERROR] Cannot start live sync: Server not available")
            return False

        self.is_connected = True
        self.timer.start(self.poll_interval_ms)
        print(f"[OK] Live sync started (polling every {self.poll_interval_ms}ms)")

        # Immediate first fetch
        self._check_for_updates()
        return True

    def stop(self):
        """Stop live sync."""
        self.timer.stop()
        self.is_connected = False
        print("[STOP] Live sync stopped")

    def is_active(self) -> bool:
        """Check if live sync is active."""
        return self.timer.isActive()

    def force_update(self):
        """Force geometry refresh regardless of hash."""
        self.current_hash = None
        self._check_for_updates()

    def _check_for_updates(self):
        """Check if geometry has changed and update if needed."""
        # Check server is still available
        if not self.fetcher.is_server_available():
            if self.is_connected:
                print("[WARN] Server connection lost")
                self.is_connected = False
            return

        if not self.is_connected:
            print("[OK] Server connection restored")
            self.is_connected = True

        # Fetch full geometry to compute hash
        cage = self.fetcher.fetch_control_cage()
        if cage is None:
            return

        # Compute hash from control cage
        new_hash = self._compute_cage_hash(cage)

        # Check if changed
        if new_hash != self.current_hash:
            print(f"[UPDATE] Geometry changed (hash: {new_hash[:8]}...)")
            self.current_hash = new_hash
            self.last_cage = cage

            # Notify callback
            self.on_geometry_changed(cage)
        # else: No change, no update

    def _compute_cage_hash(self, cage) -> str:
        """Compute hash of control cage for change detection.

        Args:
            cage: SubD control cage

        Returns:
            SHA256 hash string
        """
        if cpp_core is None:
            # Fallback if cpp_core not available
            return "no_cpp_core"

        # Create deterministic representation
        data = {
            'vertices': [
                [v.x, v.y, v.z] for v in cage.vertices
            ],
            'faces': cage.faces,
            'vertex_count': cage.vertex_count(),
            'face_count': cage.face_count()
        }

        # Serialize to JSON (sorted keys for determinism)
        json_str = json.dumps(data, sort_keys=True)

        # Compute SHA256 hash
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get_connection_status(self) -> dict:
        """Get current connection status.

        Returns:
            dict with 'connected', 'active', 'hash' keys
        """
        return {
            'connected': self.is_connected,
            'active': self.is_active(),
            'hash': self.current_hash[:8] if self.current_hash else None,
            'has_geometry': self.last_cage is not None
        }
