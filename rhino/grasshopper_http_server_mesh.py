"""
Grasshopper HTTP Server for SubD Bridge - Mesh Transfer Version
For Rhino 8 with Python 3 support
Copy this entire code into a GhPython component in Grasshopper
Connect your SubD to the 'subd' input
"""

import json
import threading
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer

# Import Rhino libraries (available in Rhino 8 Python 3)
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc

# Server configuration
PORT = 8800

# Global storage
current_subd = None
current_hash = None
server_thread = None
httpd = None


class RhinoHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for SubD bridge"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'connected',
                'has_geometry': current_subd is not None,
                'server': 'Grasshopper SubD Bridge v3.0 (Mesh Transfer)'
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/subd':
            if current_subd:
                # Serialize as mesh for display
                geometry_data = serialize_subd_as_mesh(current_subd)

                if geometry_data:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(geometry_data).encode())
                else:
                    self.send_error(500, "Failed to serialize SubD")
            else:
                self.send_error(404, "No SubD geometry available")

        elif self.path == '/check_update':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {'geometry_hash': current_hash or ''}
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_error(404)

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress console output"""
        pass


def serialize_subd_as_mesh(subd):
    """
    Convert SubD to mesh representation for display
    This is a display approximation - the exact SubD is preserved separately
    """
    global current_hash

    print(f"serialize_subd_as_mesh called")

    if not subd:
        print("SubD is None!")
        return None

    try:
        # Convert SubD to display mesh
        # Use density=1 for reasonable quality without being too heavy
        mesh = rg.Mesh.CreateFromSubD(subd, 1)

        if not mesh:
            print("Failed to create mesh from SubD")
            return None

        print(f"Created mesh: V={mesh.Vertices.Count}, F={mesh.Faces.Count}")

        # Extract vertices
        vertices = []
        for i in range(mesh.Vertices.Count):
            v = mesh.Vertices[i]
            vertices.append([float(v.X), float(v.Y), float(v.Z)])

        # Extract faces
        faces = []
        for i in range(mesh.Faces.Count):
            f = mesh.Faces[i]
            if f.IsQuad:
                faces.append([f.A, f.B, f.C, f.D])
            else:
                faces.append([f.A, f.B, f.C])

        # Extract normals if available
        mesh.Normals.ComputeNormals()
        normals = []
        for i in range(mesh.Normals.Count):
            n = mesh.Normals[i]
            normals.append([float(n.X), float(n.Y), float(n.Z)])

        # Calculate hash for change detection
        vertex_count = len(vertices)
        face_count = len(faces)
        hash_str = f"{vertex_count}_{face_count}_{subd.Vertices.Count}_{subd.Faces.Count}"
        current_hash = hashlib.md5(hash_str.encode()).hexdigest()

        result = {
            'vertices': vertices,
            'faces': faces,
            'normals': normals,
            'vertex_count': vertex_count,
            'face_count': face_count,
            'subd_vertex_count': subd.Vertices.Count,  # Original SubD counts
            'subd_face_count': subd.Faces.Count,
            'subd_edge_count': subd.Edges.Count,
            'hash': current_hash,
            'format': 'mesh',
            'is_display_mesh': True  # Indicates this is for display only
        }

        print(f"Returning mesh data: {vertex_count} vertices, {face_count} faces")
        return result

    except Exception as e:
        print(f"Error in serialize_subd_as_mesh: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def start_server():
    """Start the HTTP server in a background thread"""
    global server_thread, httpd

    try:
        httpd = HTTPServer(('localhost', PORT), RhinoHTTPHandler)
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        print(f"SubD Bridge Server started on http://localhost:{PORT}")
        print("Mesh transfer mode (display approximation)")
        return True

    except Exception as e:
        print(f"Failed to start server: {e}")
        return False


def stop_server():
    """Stop the HTTP server"""
    global httpd, server_thread

    if httpd:
        httpd.shutdown()
        httpd = None

    if server_thread:
        server_thread.join(timeout=1)
        server_thread = None

    print("Server stopped")


# ============ MAIN GRASSHOPPER EXECUTION ============

# Input SubD from Grasshopper parameter
if 'subd' in locals() and subd is not None:
    current_subd = subd
    print(f"SubD loaded: Vertices={subd.Vertices.Count}, Faces={subd.Faces.Count}")
else:
    print("No SubD input connected")
    current_subd = None

# Start server if not running
if not server_thread or not server_thread.is_alive():
    if start_server():
        status = f"✅ Server running on http://localhost:{PORT}"
        if current_subd:
            status += f"\n📦 SubD ready: {current_subd.Vertices.Count} vertices"
            status += f"\n🔄 Mesh transfer mode (visual approximation)"
    else:
        status = "❌ Failed to start server"
else:
    status = "✅ Server already running"
    if current_subd:
        status += f"\n📦 SubD updated: {current_subd.Vertices.Count} vertices"

# Output status
print(status)