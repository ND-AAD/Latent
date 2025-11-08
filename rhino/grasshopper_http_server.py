"""
Grasshopper HTTP Server for EXACT SubD Transfer
Maintains lossless representation - NO mesh conversion

CRITICAL: This preserves the exact SubD mathematical representation
for the "Lossless Until Fabrication" principle

To use in Grasshopper:
1. Create a GhPython component
2. Add input parameter 'subd' (type: SubD, Item Access)
3. Add output parameter 'status' (type: Text)
4. Paste this entire code into the component
5. Connect your SubD geometry to the input
6. The server will start automatically on port 8080
"""

import System
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import json
import threading
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import hashlib
import io

# Server configuration
HOST = 'localhost'
PORT = 8800  # Changed from 8080 to avoid conflicts

# Global storage
current_subd = None
current_hash = None
server_thread = None
httpd = None


class RhinoHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for exact SubD bridge"""

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
                'server': 'Grasshopper SubD Bridge v2.0'
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/subd':
            if current_subd:
                # Serialize exact SubD
                geometry_data = serialize_exact_subd(current_subd)

                if geometry_data:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(geometry_data).encode())
                else:
                    # Serialization failed
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

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/molds':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode())
                mold_pieces = data.get('mold_pieces', [])

                # Process received molds
                for piece in mold_pieces:
                    add_mold_to_rhino(piece)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                response = {
                    'status': 'success',
                    'pieces_received': len(mold_pieces)
                }
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                self.send_error(400, str(e))
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


def serialize_exact_subd(subd):
    """
    Serialize SubD maintaining EXACT representation
    This is the critical function for lossless transfer
    """
    global current_hash

    print(f"serialize_exact_subd called with subd: {subd}")

    if not subd:
        print("SubD is None!")
        return None

    try:
        # Get SubD statistics first to verify it's valid
        vertex_count = subd.Vertices.Count
        face_count = subd.Faces.Count
        edge_count = subd.Edges.Count
        print(f"SubD stats: V={vertex_count}, F={face_count}, E={edge_count}")

        # Create a temporary File3dm to hold the SubD
        file3dm = Rhino.FileIO.File3dm()

        # Add the SubD to the file
        attrs = Rhino.DocObjects.ObjectAttributes()
        file3dm.Objects.AddSubD(subd, attrs)

        # Serialize to memory stream
        ms = System.IO.MemoryStream()
        write_options = Rhino.FileIO.File3dmWriteOptions()
        write_options.Version = 7  # Use Rhino 7 format for compatibility

        success = file3dm.Write(ms, write_options)

        if not success:
            print("Failed to serialize SubD to 3dm")
            return None

        # Convert to base64 for JSON transport
        byte_array = ms.ToArray()
        base64_data = System.Convert.ToBase64String(byte_array)
        print(f"Serialized to base64, length: {len(str(base64_data))}")

        # Calculate hash for change detection
        hash_str = f"{vertex_count}_{face_count}_{edge_count}"
        current_hash = hashlib.md5(hash_str.encode()).hexdigest()

        result = {
            'subd_data': str(base64_data),  # Exact SubD as base64
            'vertex_count': vertex_count,
            'face_count': face_count,
            'edge_count': edge_count,
            'hash': current_hash,
            'is_exact': True,  # Flag indicating this is exact, not mesh
            'format': '3dm'
        }

        print(f"Returning serialized data with {len(result['subd_data'])} chars of base64 data")
        return result

    except Exception as e:
        print(f"Error in serialize_exact_subd: {e}")
        import traceback
        print(traceback.format_exc())
        return None


def add_mold_to_rhino(mold_data):
    """Add received mold geometry back to Rhino"""
    try:
        mold_id = mold_data.get('id', 'unknown')
        print(f"Received mold piece: {mold_id}")

        # If mold data contains 3dm format
        if mold_data.get('format') == '3dm' and 'geometry_data' in mold_data:
            base64_data = mold_data['geometry_data']
            byte_array = System.Convert.FromBase64String(base64_data)

            ms = System.IO.MemoryStream(byte_array)
            file3dm = Rhino.FileIO.File3dm.Read(ms)

            if file3dm:
                # Add objects from file to document
                for obj in file3dm.Objects:
                    sc.doc.Objects.Add(obj.Geometry, obj.Attributes)

                sc.doc.Views.Redraw()
                print(f"Added mold {mold_id} to document")

    except Exception as e:
        print(f"Error adding mold: {e}")


def start_server():
    """Start the HTTP server in a background thread"""
    global httpd, server_thread

    try:
        httpd = HTTPServer((HOST, PORT), RhinoHTTPHandler)
        print(f"SubD Bridge Server started on http://{HOST}:{PORT}")
        print("EXACT SubD transfer enabled - NO mesh conversion")

        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

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
            status += f"\n🔄 Exact transfer mode (lossless)"
    else:
        status = "❌ Failed to start server"
else:
    status = "✅ Server already running"
    if current_subd:
        status += f"\n📦 SubD updated: {current_subd.Vertices.Count} vertices"

# Output status
print(status)