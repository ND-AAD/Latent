"""
Grasshopper HTTP Server - Control Cage Transfer & Mold Import
=============================================================

Serves SubD control cage data via HTTP and receives NURBS molds from desktop app.

CRITICAL: This replaces grasshopper_server_control.py which used mesh transfer.
This version uses control cage transfer (lossless, exact topology).

Grasshopper Component:
  Inputs:
    - SubD: SubD geometry to serve
    - Run: Boolean to start/stop server
  Outputs:
    - Status: Server status message
    - URL: Server URL

Endpoints:
  GET  /geometry - Serve SubD control cage as JSON
  GET  /status   - Server status check
  POST /molds    - Import NURBS molds back to Rhino

Usage:
  1. Create or reference SubD in Grasshopper
  2. Connect to SubD input
  3. Set Run = True
  4. Server starts on http://localhost:8888
  5. Desktop app fetches geometry via GET /geometry
  6. Desktop app sends molds back via POST /molds
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
    """Handle HTTP requests for SubD geometry and mold import."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/geometry':
            self.serve_geometry()
        elif self.path == '/status':
            self.serve_status()
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        """Handle POST requests for mold import."""
        if self.path == '/molds':
            self._handle_mold_import()
        else:
            self.send_error(404, f"POST endpoint not found: {self.path}")

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

    def _handle_mold_import(self):
        """
        Import NURBS molds sent from desktop app.

        Expected JSON:
        {
            "type": "ceramic_mold_set",
            "molds": [
                {
                    "name": "mold_1",
                    "degree_u": 3,
                    "degree_v": 3,
                    "control_points": [[x,y,z], ...],
                    "weights": [w, ...],
                    "count_u": n,
                    "count_v": m,
                    "knots_u": [u0, u1, ...],
                    "knots_v": [v0, v1, ...]
                },
                ...
            ]
        }
        """
        # Read POST body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))

            # Validate
            if data.get('type') != 'ceramic_mold_set':
                self.send_error(400, "Invalid data type")
                return

            # Import each mold
            imported_ids = []
            for mold_data in data['molds']:
                guid = self._import_nurbs_surface(mold_data)
                if guid:
                    imported_ids.append(str(guid))

            # Response
            response = {
                "status": "success",
                "imported_count": len(imported_ids),
                "guids": imported_ids
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

            print(f"✅ Imported {len(imported_ids)} molds to Rhino")

        except Exception as e:
            print(f"❌ Import failed: {str(e)}")
            self.send_error(500, f"Import failed: {str(e)}")

    def _import_nurbs_surface(self, mold_data):
        """
        Create Rhino NurbsSurface from serialized data.

        Args:
            mold_data: Dict with NURBS surface data

        Returns:
            GUID of created surface, or None on failure
        """
        try:
            # Import rhinoscriptsyntax for object manipulation
            import rhinoscriptsyntax as rs

            # Extract data
            degree_u = mold_data['degree_u']
            degree_v = mold_data['degree_v']
            count_u = mold_data['count_u']
            count_v = mold_data['count_v']

            # Create NurbsSurface
            surface = rg.NurbsSurface.Create(
                dimension=3,
                isRational=True,
                orderU=degree_u + 1,  # Rhino uses order = degree + 1
                orderV=degree_v + 1,
                controlPointCountU=count_u,
                controlPointCountV=count_v
            )

            # Set control points and weights
            points = mold_data['control_points']
            weights = mold_data['weights']

            idx = 0
            for i in range(count_u):
                for j in range(count_v):
                    x, y, z = points[idx]
                    w = weights[idx]
                    surface.Points.SetPoint(i, j, x, y, z, w)
                    idx += 1

            # Set knot vectors
            for i, knot in enumerate(mold_data['knots_u']):
                surface.KnotsU[i] = knot
            for i, knot in enumerate(mold_data['knots_v']):
                surface.KnotsV[i] = knot

            # Add to Rhino document
            guid = rs.AddSurface(surface)

            # Set name
            if 'name' in mold_data:
                rs.ObjectName(guid, mold_data['name'])

            return guid

        except Exception as e:
            print(f"❌ Failed to import surface: {e}")
            return None

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
