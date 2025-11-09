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
import logging
from requests.exceptions import RequestException, Timeout, ConnectionError

from app.utils.error_handling import get_logger, graceful_degradation

logger = get_logger(__name__)


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
                        logger.warning(f"Geometry is {type(geom).__name__}, not SubD")
                else:
                    logger.error("No geometry found in 3dm data")
            except base64.binascii.Error as e:
                logger.error(f"Base64 decode error: {e}")
            except Exception as e:
                logger.error(f"Error decoding SubD: {e}", exc_info=True)
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
            logger.info(f"Attempting to connect to {self.base_url}")
            response = requests.get(f"{self.base_url}/status", timeout=2)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'connected':
                    self.connected = True
                    self.connection_status_changed.emit(True)
                    logger.info("Successfully connected to Grasshopper (manual push mode)")
                    return True
                else:
                    logger.warning(f"Server responded but status is: {data.get('status')}")
            else:
                logger.error(f"Server returned status code {response.status_code}")
                self.error_occurred.emit(f"Server error: HTTP {response.status_code}")

        except Timeout:
            error_msg = "Connection timeout - server not responding"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        except ConnectionError:
            error_msg = "Cannot connect - ensure Grasshopper HTTP server is running"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
        except RequestException as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during connection: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

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
            # Validate required fields
            if not geometry_data:
                logger.error("Empty geometry data received")
                self.error_occurred.emit("Empty geometry data")
                return None

            if 'vertices' not in geometry_data or 'faces' not in geometry_data:
                logger.error("Missing required geometry fields (vertices/faces)")
                self.error_occurred.emit("Invalid geometry data format")
                return None

            vertices = geometry_data['vertices']
            faces = geometry_data['faces']

            # Validate data integrity
            if not vertices or not faces:
                logger.error("Empty vertices or faces array")
                self.error_occurred.emit("Geometry has no vertices or faces")
                return None

            # Create SubDGeometry from received data
            geometry = SubDGeometry(
                subd_data='',  # No 3dm data in manual push mode
                vertex_count=geometry_data.get('vertex_count', len(vertices)),
                face_count=geometry_data.get('face_count', len(faces)),
                edge_count=0  # Not needed in manual mode
            )

            # Add mesh data
            geometry.mesh_data = {
                'vertices': vertices,
                'faces': faces,
                'normals': geometry_data.get('normals', [])
            }

            logger.info(f"Received geometry: {len(vertices)} vertices, {len(faces)} faces")

            self.current_geometry = geometry
            self.geometry_received.emit(geometry)

            return geometry

        except KeyError as e:
            error_msg = f"Missing required field: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return None
        except Exception as e:
            error_msg = f"Error receiving geometry: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
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
            logger.warning("Cannot send molds - not connected to server")
            self.error_occurred.emit("Not connected to Rhino")
            return False

        if not mold_pieces:
            logger.warning("No mold pieces to send")
            return False

        try:
            logger.info(f"Sending {len(mold_pieces)} mold pieces to Rhino")
            data = {'mold_pieces': mold_pieces}
            response = requests.post(
                f"{self.base_url}/molds",
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Molds sent successfully")
                return True
            else:
                error_msg = f"Server returned status code {response.status_code}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return False

        except Timeout:
            error_msg = "Timeout sending molds to Rhino"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
        except ConnectionError:
            error_msg = "Connection lost while sending molds"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
        except RequestException as e:
            error_msg = f"Failed to send molds: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error sending molds: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            return False
