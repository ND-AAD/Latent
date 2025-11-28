# Agent 8: Desktop Bridge & Auto-Update

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 3-4 hours
**Estimated Cost**: $3-5 (40K tokens, Sonnet)

---

## Mission

Implement automatic geometry synchronization between Grasshopper and desktop application with change detection and live updates.

---

## Context

You are creating the "live link" between Rhino/Grasshopper and the desktop app. This bridge:
- Polls Grasshopper server for geometry updates
- Detects when SubD has changed (hash-based)
- Auto-refreshes viewport when changes detected
- Provides manual refresh capability
- Shows connection status in UI

**Critical**: Must avoid unnecessary re-tessellation (expensive). Only update when geometry actually changes.

**Dependencies**:
- Agent 6's Grasshopper server
- Agent 7's SubDFetcher and display utilities
- Existing PyQt6 UI infrastructure

---

## Deliverables

**Files to Create/Update**:
1. `app/bridge/live_bridge.py` - Auto-update manager
2. Update `main.py` - Add connection status indicator
3. `tests/test_live_bridge.py` - Test auto-update

---

## Requirements

### 1. Live Bridge Manager

**File**: `app/bridge/live_bridge.py`

```python
"""Live geometry synchronization between Rhino and desktop app."""

import hashlib
import json
from typing import Optional, Callable
from PyQt6.QtCore import QTimer
import cpp_core
from .subd_fetcher import SubDFetcher

class LiveBridge:
    """Manage live connection to Grasshopper server."""

    def __init__(self,
                 fetcher: SubDFetcher,
                 on_geometry_changed: Callable[[cpp_core.SubDControlCage], None],
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
            print("❌ Cannot start live sync: Server not available")
            return False

        self.is_connected = True
        self.timer.start(self.poll_interval_ms)
        print(f"✅ Live sync started (polling every {self.poll_interval_ms}ms)")

        # Immediate first fetch
        self._check_for_updates()
        return True

    def stop(self):
        """Stop live sync."""
        self.timer.stop()
        self.is_connected = False
        print("🛑 Live sync stopped")

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
                print("⚠️  Server connection lost")
                self.is_connected = False
            return

        if not self.is_connected:
            print("✅ Server connection restored")
            self.is_connected = True

        # Get metadata first (lightweight check)
        metadata = self.fetcher.get_metadata()
        if metadata is None:
            return

        # Compute hash from metadata
        # (vertex count, face count, and first/last vertex positions)
        # This is cheaper than downloading full geometry
        hash_data = {
            'vertex_count': metadata.get('vertex_count', 0),
            'face_count': metadata.get('face_count', 0)
        }

        # Actually, we need full geometry to compute proper hash
        # But we can optimize by fetching once and caching
        cage = self.fetcher.fetch_control_cage()
        if cage is None:
            return

        # Compute hash from control cage
        new_hash = self._compute_cage_hash(cage)

        # Check if changed
        if new_hash != self.current_hash:
            print(f"🔄 Geometry changed (hash: {new_hash[:8]}...)")
            self.current_hash = new_hash
            self.last_cage = cage

            # Notify callback
            self.on_geometry_changed(cage)
        # else: No change, no update

    def _compute_cage_hash(self, cage: cpp_core.SubDControlCage) -> str:
        """Compute hash of control cage for change detection.

        Args:
            cage: SubD control cage

        Returns:
            SHA256 hash string
        """
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
```

### 2. Connection Status Widget

Add to `main.py`:

```python
from PyQt6.QtWidgets import QLabel, QHBoxLayout
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QPalette

class ConnectionStatusWidget(QWidget):
    """Show connection status to Grasshopper server."""

    def __init__(self, live_bridge):
        super().__init__()
        self.live_bridge = live_bridge

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        # Status indicator (colored dot)
        self.status_label = QLabel("●")
        self.status_label.setStyleSheet("font-size: 16px;")

        # Status text
        self.text_label = QLabel("Disconnected")

        layout.addWidget(self.status_label)
        layout.addWidget(self.text_label)
        layout.addStretch()

        self.setLayout(layout)

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)  # Update UI every 500ms

    def update_status(self):
        """Update status display."""
        status = self.live_bridge.get_connection_status()

        if status['connected'] and status['active']:
            self.status_label.setStyleSheet("color: green; font-size: 16px;")
            self.text_label.setText("Live sync active")
        elif status['connected']:
            self.status_label.setStyleSheet("color: orange; font-size: 16px;")
            self.text_label.setText("Connected (manual)")
        else:
            self.status_label.setStyleSheet("color: red; font-size: 16px;")
            self.text_label.setText("Disconnected")
```

### 3. Integration with Main Window

Update `MainWindow.__init__()`:

```python
def __init__(self):
    # ... existing code ...

    # Create live bridge
    self.live_bridge = LiveBridge(
        fetcher=self.subd_fetcher,
        on_geometry_changed=self.on_geometry_updated
    )

    # Add status widget to status bar
    self.status_widget = ConnectionStatusWidget(self.live_bridge)
    self.statusBar().addPermanentWidget(self.status_widget)

    # ... rest of initialization ...
```

Add menu items:

```python
def create_menu_bar(self):
    # ... existing menu code ...

    # File menu additions
    file_menu = menubar.addMenu('&File')

    # Load from Rhino (manual)
    load_rhino = QAction('Load from &Rhino', self)
    load_rhino.setShortcut('Ctrl+R')
    load_rhino.triggered.connect(self.load_from_rhino)
    file_menu.addAction(load_rhino)

    # Start live sync
    start_sync = QAction('Start &Live Sync', self)
    start_sync.setShortcut('Ctrl+L')
    start_sync.triggered.connect(self.start_live_sync)
    file_menu.addAction(start_sync)

    # Stop live sync
    stop_sync = QAction('Stop Live Sync', self)
    stop_sync.triggered.connect(self.stop_live_sync)
    file_menu.addAction(stop_sync)

    file_menu.addSeparator()

    # Force refresh
    refresh = QAction('&Refresh', self)
    refresh.setShortcut('F5')
    refresh.triggered.connect(self.force_refresh)
    file_menu.addAction(refresh)

    # ... rest of menu ...
```

Add handlers:

```python
def start_live_sync(self):
    """Start live synchronization with Grasshopper."""
    if self.live_bridge.start():
        print("✅ Live sync enabled")
    else:
        print("❌ Failed to start live sync")

def stop_live_sync(self):
    """Stop live synchronization."""
    self.live_bridge.stop()

def force_refresh(self):
    """Force geometry refresh."""
    print("🔄 Forcing refresh...")
    self.live_bridge.force_update()

def on_geometry_updated(self, cage: cpp_core.SubDControlCage):
    """Called when geometry changes in Grasshopper.

    Args:
        cage: Updated SubD control cage
    """
    print(f"📥 Received updated geometry: "
          f"{cage.vertex_count()} vertices, {cage.face_count()} faces")

    self.current_cage = cage

    # Re-initialize evaluator
    self.subd_evaluator.initialize(cage)

    # Re-tessellate
    result = self.subd_evaluator.tessellate(subdivision_level=3)

    # Update display
    self.display_tessellation(result, cage)

    print("✅ Display updated")
```

---

## Testing

### Test 1: Manual Load and Update

**Procedure**:
1. Start Grasshopper server with SubD sphere
2. Launch desktop app
3. File → Load from Rhino (Ctrl+R)
4. Verify sphere displays
5. In Grasshopper: Modify SubD (e.g., scale it)
6. File → Refresh (F5)
7. Verify updated geometry displays

**Expected**:
- Initial load shows sphere
- After modification and refresh, scaled sphere appears
- Console shows "🔄 Forcing refresh..."
- Console shows "📥 Received updated geometry..."

### Test 2: Live Sync

**Procedure**:
1. Start Grasshopper server
2. Launch desktop app
3. File → Start Live Sync (Ctrl+L)
4. Status bar shows "● Live sync active" (green dot)
5. In Grasshopper: Modify SubD
6. Desktop automatically updates within 2 seconds

**Expected**:
- Status changes to green when sync starts
- Console shows "🔄 Geometry changed (hash: ...)
- Viewport auto-updates when geometry changes
- No update when geometry unchanged (efficiency)

### Test 3: Change Detection

**Test File**: `tests/test_live_bridge.py`

```python
#!/usr/bin/env python3
"""Test live bridge change detection."""

import sys
sys.path.insert(0, 'cpp_core/build')

import cpp_core
from app.bridge.live_bridge import LiveBridge
from app.bridge.subd_fetcher import SubDFetcher

def test_hash_computation():
    """Test cage hash computation."""
    print("Testing hash computation...")

    # Create identical cages
    cage1 = cpp_core.SubDControlCage()
    cage1.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage1.faces = [[0, 1, 2, 3]]

    cage2 = cpp_core.SubDControlCage()
    cage2.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage2.faces = [[0, 1, 2, 3]]

    # Create bridge (dummy callback)
    bridge = LiveBridge(
        fetcher=None,
        on_geometry_changed=lambda c: None
    )

    # Compute hashes
    hash1 = bridge._compute_cage_hash(cage1)
    hash2 = bridge._compute_cage_hash(cage2)

    print(f"  Hash 1: {hash1[:16]}...")
    print(f"  Hash 2: {hash2[:16]}...")

    assert hash1 == hash2, "Identical cages should have same hash"
    print("  ✅ Identical cages have same hash")

    # Modify cage2
    cage2.vertices[0].x = 0.1

    hash3 = bridge._compute_cage_hash(cage2)
    print(f"  Hash 3: {hash3[:16]}... (after modification)")

    assert hash1 != hash3, "Different cages should have different hash"
    print("  ✅ Different cages have different hash")

def test_connection_status():
    """Test connection status reporting."""
    print("\nTesting connection status...")

    fetcher = SubDFetcher()

    change_count = [0]  # Mutable for closure

    def on_change(cage):
        change_count[0] += 1
        print(f"  Change detected: {cage.vertex_count()} vertices")

    bridge = LiveBridge(fetcher, on_change, poll_interval_ms=1000)

    # Check initial status
    status = bridge.get_connection_status()
    assert not status['connected']
    assert not status['active']
    print("  ✅ Initial status correct (disconnected)")

    # Try to start (may fail if server not running)
    if fetcher.is_server_available():
        bridge.start()
        status = bridge.get_connection_status()
        assert status['connected']
        assert status['active']
        print("  ✅ Active status correct (connected)")

        bridge.stop()
        status = bridge.get_connection_status()
        assert not status['active']
        print("  ✅ Stopped status correct")
    else:
        print("  ⚠️  Server not available, skipping active tests")

def main():
    print("=" * 60)
    print("Testing Live Bridge")
    print("=" * 60)
    print()

    try:
        test_hash_computation()
        test_connection_status()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

**Run**:
```bash
python3 tests/test_live_bridge.py
```

---

## Success Criteria

- [ ] LiveBridge class implemented
- [ ] Hash-based change detection working
- [ ] Auto-update triggers only when geometry changes
- [ ] Manual refresh works (F5)
- [ ] Live sync can be started and stopped
- [ ] Connection status widget shows correct state
- [ ] Status indicator color changes correctly (red/green/orange)
- [ ] No unnecessary re-tessellation (verified in logs)
- [ ] All tests pass
- [ ] Performance: <5ms overhead per poll when unchanged

---

## Performance Notes

**Optimization Strategy**:
- Poll interval: 2000ms (balance between responsiveness and overhead)
- Hash computation: ~1ms for typical cage
- Unchanged geometry: No tessellation (just hash check)
- Changed geometry: Full update triggered

**Expected Behavior**:
- 99% of polls: No change → 1ms overhead
- 1% of polls: Change detected → Full update (50-100ms)
- Total overhead: ~0.5% CPU when idle

---

## Integration Notes

**Connects**:
- Agent 6 (Grasshopper server) → LiveBridge → MainWindow
- LiveBridge monitors for changes → Calls on_geometry_updated
- MainWindow updates viewport when notified

**File Structure**:
```
app/
└── bridge/
    ├── subd_fetcher.py          (Agent 7)
    └── live_bridge.py           (You create) ← HERE
main.py                          (You update) ← HERE
tests/test_live_bridge.py        (You create) ← HERE
```

---

## Common Issues and Solutions

**Issue**: "Geometry updates too frequently"
- **Fix**: Increase poll interval (e.g., 3000ms)
- **Fix**: Check hash is computed correctly (deterministic)

**Issue**: "No updates detected when geometry changes"
- **Fix**: Verify hash changes when cage modified
- **Fix**: Check on_geometry_changed callback is connected

**Issue**: "Status widget not updating"
- **Fix**: Ensure update_timer is running
- **Fix**: Check get_connection_status() returns correct values

**Issue**: "Memory leak over time"
- **Fix**: Ensure QTimer.stop() is called when bridge stopped
- **Fix**: Don't store unnecessary tessellation results

---

## Output Format

Provide:
1. Complete `live_bridge.py` implementation
2. Updated `main.py` with connection status widget
3. Complete `test_live_bridge.py` test suite
4. Test output showing hash detection working
5. Description of live sync behavior
6. Performance observations
7. Integration notes

---

**Ready to begin!**
