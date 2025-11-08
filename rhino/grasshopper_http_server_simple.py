"""
Simplified Grasshopper HTTP Server for SubD Bridge
This version uses basic data transfer for reliability while maintaining the lossless principle
Copy this entire code into a GhPython component in Grasshopper
Connect your SubD to the 'subd' input
"""

import json
import threading
import time
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer

# Import Rhino libraries (these are available in GhPython)
import Rhino
import System
import scriptcontext as sc

# Server configuration
PORT = 8888  # Changed from 8080 to avoid conflicts

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
                'server': 'Grasshopper SubD Bridge v2.0 (Simple)'
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/subd':
            if current_subd:
                # Use simplified serialization
                geometry_data = serialize_subd_simple(current_subd)

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


def serialize_subd_simple(subd):
    """
    Simplified SubD serialization that's more reliable
    For now, we'll send basic info and create placeholder data
    The full implementation can be added once the connection is working
    """
    global current_hash

    print(f"serialize_subd_simple called")

    if not subd:
        print("SubD is None!")
        return None

    try:
        # Get SubD statistics
        vertex_count = subd.Vertices.Count
        face_count = subd.Faces.Count
        edge_count = subd.Edges.Count
        print(f"SubD stats: V={vertex_count}, F={face_count}, E={edge_count}")

        # Calculate hash for change detection
        hash_str = f"{vertex_count}_{face_count}_{edge_count}"
        current_hash = hashlib.md5(hash_str.encode()).hexdigest()

        # For now, send a simplified representation
        # The desktop app will show a placeholder while maintaining lossless data storage
        result = {
            'subd_data': 'placeholder_base64_data',  # Placeholder for now
            'vertex_count': vertex_count,
            'face_count': face_count,
            'edge_count': edge_count,
            'hash': current_hash,
            'is_exact': False,  # Mark as simplified for now
            'format': 'simplified'
        }

        print(f"Returning simplified data")
        return result

    except Exception as e:
        print(f"Error in serialize_subd_simple: {e}")
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
        print("SIMPLIFIED transfer mode (for testing)")
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
            status += f"\n⚠️ SIMPLIFIED mode (for testing)"
    else:
        status = "❌ Failed to start server"
else:
    status = "✅ Server already running"
    if current_subd:
        status += f"\n📦 SubD updated: {current_subd.Vertices.Count} vertices"

# Output status
print(status)