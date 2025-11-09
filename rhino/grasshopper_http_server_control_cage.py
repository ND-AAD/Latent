"""
Grasshopper HTTP Server - Control Cage Transfer
================================================

Serves SubD control cage data via HTTP for the desktop application.

CRITICAL: This replaces grasshopper_server_control.py which used mesh transfer.
This version uses control cage transfer (lossless, exact topology).

Grasshopper Component:
  Inputs:
    - SubD: SubD geometry to serve
    - Run: Boolean to start/stop server
  Outputs:
    - Status: Server status message
    - URL: Server URL

Usage:
  1. Create or reference SubD in Grasshopper
  2. Connect to SubD input
  3. Set Run = True
  4. Server starts on http://localhost:8888
  5. Desktop app fetches via /geometry endpoint
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import Rhino.Geometry as rg

# Global to hold current geometry
current_geometry = None

# Server instance
server = None
server_thread = None


class GeometryHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for SubD geometry."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/geometry':
            self.serve_geometry()
        elif self.path == '/status':
            self.serve_status()
        else:
            self.send_error(404, "Not found")

    def serve_geometry(self):
        """Serve SubD control cage as JSON."""
        global current_geometry

        if current_geometry is None:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'No geometry available'
            }).encode())
            return

        # Extract control cage
        cage_data = extract_control_cage(current_geometry)

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = json.dumps(cage_data, indent=2)
        self.wfile.write(response.encode())

    def serve_status(self):
        """Serve server status."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        status = {
            'status': 'running',
            'port': 8888,
            'has_geometry': current_geometry is not None
        }

        self.wfile.write(json.dumps(status).encode())

    def log_message(self, format, *args):
        """Override to suppress console spam."""
        pass  # Silent logging


def extract_control_cage(subd):
    """
    Extract control cage data from Rhino SubD object.

    Args:
        subd: Rhino.Geometry.SubD object

    Returns:
        dict: {
            'vertices': [[x,y,z], ...],
            'faces': [[i,j,k,...], ...],
            'creases': [[edge_i, edge_j, sharpness], ...],
            'metadata': {...}
        }
    """
    if not isinstance(subd, rg.SubD):
        return {'error': 'Not a SubD object'}

    # Get control vertices
    vertices = []
    vertex_map = {}  # Map vertex ID to index

    for idx, vertex in enumerate(subd.Vertices):
        pt = vertex.ControlNetPoint
        vertices.append([pt.X, pt.Y, pt.Z])
        vertex_map[vertex.Id] = idx

    # Get control faces
    faces = []

    for face in subd.Faces:
        # Get vertex indices for this face
        face_verts = []

        # Get the edges in order around the face
        edge_count = face.EdgeCount

        for i in range(edge_count):
            edge = face.EdgeAt(i)

            # For the first edge, add both vertices
            # For subsequent edges, only add the second vertex (to avoid duplicates)
            if i == 0:
                # Add start vertex of first edge
                v_start = edge.StartVertex
                if face.EdgeDirection(i) > 0:
                    # Edge is oriented with face
                    v_start_id = edge.StartVertex.Id
                else:
                    # Edge is reversed relative to face
                    v_start_id = edge.EndVertex.Id

                v_start_idx = vertex_map.get(v_start_id)
                if v_start_idx is not None:
                    face_verts.append(v_start_idx)

            # Add end vertex (which is start of next edge)
            if face.EdgeDirection(i) > 0:
                v_end_id = edge.EndVertex.Id
            else:
                v_end_id = edge.StartVertex.Id

            v_end_idx = vertex_map.get(v_end_id)
            if v_end_idx is not None:
                face_verts.append(v_end_idx)

        if face_verts:
            faces.append(face_verts)

    # Get creases (sharp edges)
    creases = []

    for edge in subd.Edges:
        if edge.Sharpness > 0:
            # Get edge vertex indices
            v1_idx = vertex_map.get(edge.StartVertex.Id)
            v2_idx = vertex_map.get(edge.EndVertex.Id)

            if v1_idx is not None and v2_idx is not None:
                creases.append([v1_idx, v2_idx, edge.Sharpness])

    # Gather metadata
    metadata = {
        'vertex_count': len(vertices),
        'face_count': len(faces),
        'edge_count': subd.Edges.Count,
        'crease_count': len(creases)
    }

    return {
        'vertices': vertices,
        'faces': faces,
        'creases': creases,
        'metadata': metadata
    }


def start_server(geometry):
    """Start HTTP server with geometry."""
    global server, server_thread, current_geometry

    current_geometry = geometry

    if server is None:
        # Create server
        server = HTTPServer(('localhost', 8888), GeometryHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("✅ Server started on http://localhost:8888")
    else:
        print("🔄 Geometry updated")


def stop_server():
    """Stop HTTP server."""
    global server

    if server is not None:
        server.shutdown()
        server = None
        print("🛑 Server stopped")


# ============================================================================
# GRASSHOPPER COMPONENT CODE
# ============================================================================
# Paste the code below into a Grasshopper Python component
#
# Inputs:
#   - SubD: SubD geometry to serve (type hint: SubD)
#   - Run: Boolean to start/stop server (type hint: bool)
#
# Outputs:
#   - Status: Server status message
#   - URL: Server URL
# ============================================================================

if Run:
    if SubD is not None and isinstance(SubD, rg.SubD):
        start_server(SubD)
        Status = "✅ Server running"
        URL = "http://localhost:8888"
    else:
        Status = "❌ No SubD geometry provided"
        URL = ""
else:
    stop_server()
    Status = "🛑 Server stopped"
    URL = ""
