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
from app.utils.error_handling import get_logger, graceful_degradation

logger = get_logger(__name__)


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
            logger.error("Cannot start live sync: Server not available")
            return False

        self.is_connected = True
        self.timer.start(self.poll_interval_ms)
        logger.info(f"Live sync started (polling every {self.poll_interval_ms}ms)")

        # Immediate first fetch
        try:
            self._check_for_updates()
        except Exception as e:
            logger.error(f"Error during initial update check: {e}", exc_info=True)

        return True

    def stop(self):
        """Stop live sync."""
        self.timer.stop()
        self.is_connected = False
        logger.info("Live sync stopped")

    def is_active(self) -> bool:
        """Check if live sync is active."""
        return self.timer.isActive()

    def force_update(self):
        """Force geometry refresh regardless of hash."""
        self.current_hash = None
        self._check_for_updates()

    def _check_for_updates(self):
        """Check if geometry has changed and update if needed."""
        try:
            # Check server is still available
            if not self.fetcher.is_server_available():
                if self.is_connected:
                    logger.warning("Server connection lost")
                    self.is_connected = False
                return

            if not self.is_connected:
                logger.info("Server connection restored")
                self.is_connected = True

            # Fetch full geometry to compute hash
            cage = self.fetcher.fetch_control_cage()
            if cage is None:
                logger.debug("No control cage received from server")
                return

            # Compute hash from control cage
            try:
                new_hash = self._compute_cage_hash(cage)
            except Exception as e:
                logger.error(f"Error computing cage hash: {e}", exc_info=True)
                return

            # Check if changed
            if new_hash != self.current_hash:
                logger.info(f"Geometry changed (hash: {new_hash[:8]}...)")
                self.current_hash = new_hash
                self.last_cage = cage

                # Notify callback
                try:
                    self.on_geometry_changed(cage)
                except Exception as e:
                    logger.error(f"Error in geometry change callback: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error checking for updates: {e}", exc_info=True)

    def _compute_cage_hash(self, cage) -> str:
        """Compute hash of control cage for change detection.

        Args:
            cage: SubD control cage

        Returns:
            SHA256 hash string
        """
        if cpp_core is None:
            # Fallback if cpp_core not available
            logger.warning("cpp_core not available for hash computation")
            return "no_cpp_core"

        try:
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

        except AttributeError as e:
            logger.error(f"Invalid cage object structure: {e}")
            raise
        except Exception as e:
            logger.error(f"Error computing hash: {e}", exc_info=True)
            raise

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
