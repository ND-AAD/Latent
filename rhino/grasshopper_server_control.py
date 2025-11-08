"""
Grasshopper HTTP Server with Clean Stop/Start Control
For Rhino 8 with Python 3 support
This version allows stopping and restarting without killing Rhino

Copy this entire code into a GhPython component in Grasshopper
Connect your SubD to the 'subd' input
Add a Boolean Toggle to 'run_server' input to control server state
""" 

import json
import threading
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

# Import Rhino libraries (available in Rhino 8 Python 3)
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc

# Server configuration
PORT = 8800

# Global storage - PERSISTENT across script runs
if 'persistent_server' not in sc.sticky:
    sc.sticky['persistent_server'] = None
if 'persistent_thread' not in sc.sticky:
    sc.sticky['persistent_thread'] = None
if 'current_subd' not in sc.sticky:
    sc.sticky['current_subd'] = None
if 'current_hash' not in sc.sticky:
    sc.sticky['current_hash'] = None


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
                'has_geometry': sc.sticky.get('current_subd') is not None,
                'server': 'Grasshopper SubD Bridge v4.0 (Controlled)'
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/subd':
            current_subd = sc.sticky.get('current_subd')
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

            response = {'geometry_hash': sc.sticky.get('current_hash', '')}
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
    if not subd:
        return None

    try:
        # Convert SubD to display mesh
        mesh = rg.Mesh.CreateFromSubD(subd, 1)

        if not mesh:
            return None

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

        # Extract normals
        mesh.Normals.ComputeNormals()
        normals = []
        for i in range(mesh.Normals.Count):
            n = mesh.Normals[i]
            normals.append([float(n.X), float(n.Y), float(n.Z)])

        # Calculate hash for change detection
        # MUST match client calculation exactly: vertex_count_face_count_edge_count
        vertex_count = len(vertices)
        face_count = len(faces)
        edge_count = subd.Edges.Count
        hash_str = f"{vertex_count}_{face_count}_{edge_count}"
        sc.sticky['current_hash'] = hashlib.md5(hash_str.encode()).hexdigest()

        result = {
            'vertices': vertices,
            'faces': faces,
            'normals': normals,
            'vertex_count': vertex_count,
            'face_count': face_count,
            'subd_vertex_count': subd.Vertices.Count,
            'subd_face_count': subd.Faces.Count,
            'subd_edge_count': subd.Edges.Count,
            'hash': sc.sticky['current_hash'],
            'format': 'mesh',
            'is_display_mesh': True
        }

        return result

    except Exception as e:
        print(f"Error in serialize_subd_as_mesh: {e}")
        return None


def stop_server():
    """Stop the HTTP server cleanly"""
    httpd = sc.sticky.get('persistent_server')
    server_thread = sc.sticky.get('persistent_thread')

    if httpd:
        try:
            httpd.shutdown()
            httpd.server_close()
            sc.sticky['persistent_server'] = None
        except:
            pass

    if server_thread:
        try:
            server_thread.join(timeout=1)
            sc.sticky['persistent_thread'] = None
        except:
            pass

    print("🛑 Server stopped cleanly")
    return True


def start_server():
    """Start the HTTP server in a background thread"""
    # First, ensure any existing server is stopped
    stop_server()

    try:
        # Check if port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', PORT))
        sock.close()

        if result == 0:
            print(f"⚠️ Port {PORT} is already in use by another process")
            print("Try: 1) Disable other GhPython components")
            print("     2) Or use kill_port.py carefully")
            return False

        # Create new server
        httpd = HTTPServer(('localhost', PORT), RhinoHTTPHandler)
        httpd.timeout = 0.5  # Short timeout for clean shutdown

        # Start server thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Store in sticky
        sc.sticky['persistent_server'] = httpd
        sc.sticky['persistent_thread'] = server_thread

        print(f"✅ Server started on http://localhost:{PORT}")
        return True

    except Exception as e:
        print(f"Failed to start server: {e}")
        return False


# ============ MAIN GRASSHOPPER EXECUTION ============

# Get inputs
if 'subd' in locals() and subd is not None:
    sc.sticky['current_subd'] = subd
    subd_info = f"SubD: {subd.Vertices.Count}V, {subd.Faces.Count}F"
else:
    subd_info = "No SubD connected"

# Check for run_server input (Boolean Toggle)
if 'run_server' not in locals():
    run_server = True  # Default to running

# Control server based on input
if run_server:
    # Check if server is already running
    if sc.sticky.get('persistent_server') and sc.sticky.get('persistent_thread'):
        if sc.sticky['persistent_thread'].is_alive():
            status = f"✅ Server running on port {PORT}\n{subd_info}"
        else:
            # Thread died, restart
            if start_server():
                status = f"✅ Server restarted on port {PORT}\n{subd_info}"
            else:
                status = f"❌ Failed to restart server\n{subd_info}"
    else:
        # Start new server
        if start_server():
            status = f"✅ Server started on port {PORT}\n{subd_info}"
        else:
            status = f"❌ Failed to start server\n{subd_info}"
else:
    # Stop server
    stop_server()
    status = f"🛑 Server stopped\n{subd_info}"

# Output status
print(status)