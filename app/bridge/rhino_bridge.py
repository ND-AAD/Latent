"""
Rhino Bridge - Handles communication with Rhino/Grasshopper
CRITICAL: Maintains exact SubD representation - NO mesh conversion
"""

import json
import requests
import rhino3dm
import base64
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import hashlib


@dataclass
class SubDGeometry:
    """
    Container for EXACT SubD geometry from Rhino
    Maintains lossless representation through rhino3dm
    """
    subd_data: str  # Base64 encoded 3dm binary data
    vertex_count: int
    face_count: int
    edge_count: int
    mesh_data: Optional[Dict] = None  # Temporary mesh for display (manual push mode)

    _subd_object: Optional[rhino3dm.SubD] = None

    def get_subd(self) -> Optional[rhino3dm.SubD]:
        """Get the actual rhino3dm SubD object"""
        if self._subd_object is None and self.subd_data:
            try:
                # Decode from base64
                binary_data = base64.b64decode(self.subd_data)
                # Create File3dm and read from bytes
                model = rhino3dm.File3dm.FromByteArray(binary_data)
                if model and model.Objects.Count > 0:
                    # Extract the first SubD geometry
                    geom = model.Objects[0].Geometry
                    if hasattr(geom, 'IsSubD') or type(geom).__name__ == 'SubD':
                        self._subd_object = geom
                    else:
                        print(f"Warning: Geometry is {type(geom).__name__}, not SubD")
            except Exception as e:
                print(f"Error decoding SubD: {e}")
        return self._subd_object

    def get_hash(self) -> str:
        """
        Get hash of geometry for change detection
        MUST match server calculation exactly: vertex_count_face_count_edge_count
        """
        data_str = f"{self.vertex_count}_{self.face_count}_{self.edge_count}"
        return hashlib.md5(data_str.encode()).hexdigest()


class RhinoBridge(QObject):
    """Bridge for communicating with Rhino via HTTP"""
    
    # Signals
    geometry_received = pyqtSignal(object)  # SubDGeometry
    connection_status_changed = pyqtSignal(bool)
    update_detected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        super().__init__()
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.connected = False
        self.current_geometry = None

        # NO POLLING - manual push workflow only

    def connect(self) -> bool:
        """Establish connection with Rhino HTTP server (status check only)"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'connected':
                    self.connected = True
                    self.connection_status_changed.emit(True)
                    print("✅ Connected to Grasshopper (manual push mode)")
                    return True
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Connection failed: {str(e)}")

        self.connected = False
        self.connection_status_changed.emit(False)
        return False

    def disconnect(self):
        """Disconnect from Rhino"""
        self.connected = False
        self.connection_status_changed.emit(False)

    def is_connected(self) -> bool:
        """Check if connected to Rhino"""
        return self.connected

    def receive_geometry(self, geometry_data: Dict) -> Optional[SubDGeometry]:
        """
        Receive geometry pushed from Grasshopper
        This is called by the HTTP server when Grasshopper pushes geometry
        """
        try:
            # Create SubDGeometry from received data
            geometry = SubDGeometry(
                subd_data='',  # No 3dm data in manual push mode
                vertex_count=geometry_data.get('vertex_count', 0),
                face_count=geometry_data.get('face_count', 0),
                edge_count=0  # Not needed in manual mode
            )

            # Add mesh data
            if 'vertices' in geometry_data and 'faces' in geometry_data:
                geometry.mesh_data = {
                    'vertices': geometry_data['vertices'],
                    'faces': geometry_data['faces'],
                    'normals': geometry_data.get('normals', [])
                }
                print(f"📥 Received geometry: {len(geometry_data['vertices'])} vertices, {len(geometry_data['faces'])} faces")

            self.current_geometry = geometry
            self.geometry_received.emit(geometry)

            return geometry

        except Exception as e:
            print(f"Error receiving geometry: {e}")
            return None

    def send_molds(self, mold_pieces: List[Dict]) -> bool:
        """
        Send generated mold pieces back to Rhino

        Args:
            mold_pieces: List of mold geometry dictionaries

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            data = {'mold_pieces': mold_pieces}
            response = requests.post(
                f"{self.base_url}/molds",
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                return True

        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Failed to send molds: {str(e)}")

        return False
