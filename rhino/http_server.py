"""
HTTP Server for Rhino/Grasshopper
Provides live bridge to Ceramic Mold Analyzer desktop application

This component should be placed in a Grasshopper definition with:
- Input: SubD surface from Rhino
- Output: Status messages and received mold geometry

To use:
1. Copy this code into a GhPython component
2. Connect your SubD surface to the input
3. The server will start automatically
4. Connect from the desktop app
"""

import json
import threading
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import Rhino.Geometry as rg
import scriptcontext as sc
import rhinoscriptsyntax as rs

# Server configuration
HOST = 'localhost'
PORT = 8080

# Global storage for geometry
current_subd = None
current_hash = None
received_molds = []


class RhinoHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Rhino bridge"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/status':
            # Status check endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'connected',
                'has_geometry': current_subd is not None
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/subd':
            # Send SubD geometry
            if current_subd:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                # Convert SubD to JSON
                geometry_data = serialize_subd(current_subd)
                self.wfile.write(json.dumps(geometry_data).encode())
            else:
                self.send_response(404)
                self.end_headers()
                
        elif self.path == '/check_update':
            # Quick update check
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'geometry_hash': current_hash
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/molds':
            # Receive mold geometry
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                mold_pieces = data.get('mold_pieces', [])
                
                # Store received molds
                global received_molds
                received_molds = mold_pieces
                
                # Add to Rhino document
                for piece in mold_pieces:
                    add_mold_to_rhino(piece)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {'status': 'success', 'pieces_received': len(mold_pieces)}
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress console output"""
        pass


def serialize_subd(subd):
    """Convert SubD to JSON-serializable format"""
    # Convert to Brep for easier processing
    brep = subd.ToBrep()
    mesh = rg.Mesh.CreateFromBrep(brep)[0]
    
    # Extract vertices
    vertices = []
    for i in range(mesh.Vertices.Count):
        v = mesh.Vertices[i]
        vertices.append([v.X, v.Y, v.Z])
    
    # Extract faces
    faces = []
    for i in range(mesh.Faces.Count):
        f = mesh.Faces[i]
        if f.IsQuad:
            faces.append([f.A, f.B, f.C, f.D])
        else:
            faces.append([f.A, f.B, f.C])
    
    # Calculate hash
    global current_hash
    hash_str = f"{len(vertices)}_{len(faces)}"
    current_hash = hashlib.md5(hash_str.encode()).hexdigest()
    
    return {
        'vertices': vertices,
        'faces': faces,
        'hash': current_hash
    }


def add_mold_to_rhino(mold_data):
    """Add received mold geometry to Rhino"""
    try:
        # This would deserialize and add the mold
        # For now, just print status
        print(f"Received mold piece: {mold_data.get('id', 'unknown')}")
    except Exception as e:
        print(f"Error adding mold: {e}")


# Server thread
server_thread = None
httpd = None


def start_server():
    """Start the HTTP server in a background thread"""
    global httpd, server_thread
    
    try:
        httpd = HTTPServer((HOST, PORT), RhinoHTTPHandler)
        print(f"HTTP Server started on {HOST}:{PORT}")
        
        # Run server in thread
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
    
    print("HTTP Server stopped")


# MAIN EXECUTION IN GRASSHOPPER
if __name__ == "__main__":
    # Input from Grasshopper
    if 'subd_surface' in locals():
        current_subd = subd_surface
        print(f"SubD loaded: {current_subd}")
    
    # Start server if not running
    if not server_thread or not server_thread.is_alive():
        if start_server():
            status = "Server running on http://localhost:8080"
        else:
            status = "Failed to start server"
    else:
        status = "Server already running"
    
    # Output status
    print(status)
    
    # Output received molds if any
    if received_molds:
        print(f"Received {len(received_molds)} mold pieces from desktop app")
