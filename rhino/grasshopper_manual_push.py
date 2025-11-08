"""
Simplified Grasshopper HTTP Server - MANUAL PUSH ONLY
For Rhino 8 with Python 3 support

NO automatic polling. Each button click sends geometry once.
NO external dependencies (no requests library needed)

INSTRUCTIONS:
1. Copy this code into a GhPython component
2. Connect your SubD to 'subd' input
3. Add a Button to 'push_button' input (NOT a toggle!)
4. Click button to send geometry to desktop app

INPUTS:
- subd: SubD geometry to send
- push_button: Button component (click to send)
"""

import json
import threading
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

# Import Rhino libraries
import Rhino.Geometry as rg
import scriptcontext as sc

# Server configuration
PORT = 8888

# Global storage
if 'http_server' not in sc.sticky:
    sc.sticky['http_server'] = None
if 'server_thread' not in sc.sticky:
    sc.sticky['server_thread'] = None


class SimplifiedHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler - only status endpoint"""

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'status': 'connected',
                'server': 'Grasshopper Manual Push v1.1 (No deps)'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """Suppress console spam"""
        pass


def serialize_subd_as_mesh(subd):
    """Convert SubD to mesh for display"""
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

        return {
            'vertices': vertices,
            'faces': faces,
            'normals': normals,
            'vertex_count': len(vertices),
            'face_count': len(faces),
            'format': 'mesh'
        }

    except Exception as e:
        print(f"Error serializing SubD: {e}")
        return None


def push_geometry_to_app(geometry_data):
    """Push geometry to desktop app via HTTP POST using http.client (no requests needed)"""
    try:
        # Convert data to JSON and encode
        json_data = json.dumps(geometry_data)
        json_bytes = json_data.encode('utf-8')

        # Create HTTP connection
        # Use port 8800 to avoid conflict with macOS ControlCenter (AirPlay on 5000)
        conn = http.client.HTTPConnection('localhost', 8800, timeout=5)

        # Set headers
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(json_bytes)),
            'Accept': 'application/json'
        }

        # Send POST request with body as bytes
        conn.request('POST', '/receive_geometry', body=json_bytes, headers=headers)

        # Get response
        response = conn.getresponse()
        status_code = response.status
        response_body = response.read().decode('utf-8')

        conn.close()

        if status_code == 200:
            print("✅ Geometry sent to desktop app successfully")
            print(f"   Server response: {response_body}")
            return True
        else:
            print(f"⚠️ Desktop app returned status {status_code}")
            print(f"   Response: {response_body}")
            return False

    except ConnectionRefusedError:
        print("❌ Desktop app not running or not listening on port 8800")
        return False
    except Exception as e:
        print(f"❌ Failed to send geometry: {e}")
        import traceback
        traceback.print_exc()
        return False


def ensure_server_running():
    """Make sure HTTP server is running for status checks"""
    if sc.sticky.get('http_server') and sc.sticky.get('server_thread'):
        if sc.sticky['server_thread'].is_alive():
            return True  # Already running

    # Start server
    try:
        # Check port availability
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', PORT))
        sock.close()

        if result == 0:
            print(f"⚠️ Port {PORT} already in use")
            return False

        # Create server
        httpd = HTTPServer(('localhost', PORT), SimplifiedHandler)
        httpd.timeout = 0.5

        # Start thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        sc.sticky['http_server'] = httpd
        sc.sticky['server_thread'] = server_thread

        print(f"✅ Status server running on port {PORT}")
        return True

    except Exception as e:
        print(f"Failed to start server: {e}")
        return False


# ============ MAIN GRASSHOPPER EXECUTION ============

# Ensure server is running
server_running = ensure_server_running()

# Get inputs
has_subd = 'subd' in locals() and subd is not None
button_clicked = 'push_button' in locals() and push_button

# Status message
if not server_running:
    status = "❌ Server failed to start"
elif not has_subd:
    status = "⚠️ No SubD connected\nServer ready on port 8888"
elif button_clicked:
    # Button was clicked - send geometry!
    print("📤 Sending geometry to desktop app...")
    geometry_data = serialize_subd_as_mesh(subd)

    if geometry_data:
        success = push_geometry_to_app(geometry_data)
        if success:
            status = f"✅ Sent: {geometry_data['vertex_count']}V, {geometry_data['face_count']}F"
        else:
            status = "❌ Failed to send geometry\nIs desktop app running?"
    else:
        status = "❌ Failed to serialize SubD"
else:
    status = f"⏸️ Ready to send\nSubD: {subd.Vertices.Count}V, {subd.Faces.Count}F\nClick button to push"

print(status)
