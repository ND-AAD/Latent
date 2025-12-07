"""
Analysis Engine HTTP Server

Exposes the C++ SubDEvaluator and Python analysis lenses via HTTP.
The Rhino plugin communicates with this server.

Usage:
    python server.py [--port 5000]
"""

import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional
import traceback

# Import our analysis engine
try:
    import cpp_core
    HAS_CPP = True
except ImportError:
    HAS_CPP = False
    print("Warning: cpp_core not available, using mock responses")

from app.analysis.differential_lens import DifferentialLens
from app.state.parametric_region import ParametricRegion, ParametricCurve


class AnalysisRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for analysis engine"""

    # Shared state
    evaluator: Optional['cpp_core.SubDEvaluator'] = None
    current_regions: List[ParametricRegion] = []

    def _send_json(self, data: Dict[str, Any], status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, message: str, status: int = 400):
        """Send error response"""
        self._send_json({'error': message}, status)

    def _read_json(self) -> Optional[Dict[str, Any]]:
        """Read JSON from request body"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            return json.loads(body)
        except Exception as e:
            return None

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self._send_json({'status': 'ok', 'cpp_available': HAS_CPP})
        else:
            self._send_error('Not found', 404)

    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/analyze':
                self._handle_analyze()
            elif self.path == '/evaluate':
                self._handle_evaluate()
            elif self.path == '/project':
                self._handle_project()
            elif self.path == '/validate_boundary':
                self._handle_validate_boundary()
            else:
                self._send_error('Not found', 404)
        except Exception as e:
            traceback.print_exc()
            self._send_error(str(e), 500)

    def _handle_analyze(self):
        """Run analysis on control cage"""
        data = self._read_json()
        if not data:
            self._send_error('Invalid JSON')
            return

        control_cage = data.get('control_cage', {})
        lens_name = data.get('lens', 'differential')

        # Initialize evaluator from control cage
        if HAS_CPP:
            vertices = control_cage.get('vertices', [])
            faces = control_cage.get('faces', [])
            creases = control_cage.get('creases', [])

            # Create evaluator
            AnalysisRequestHandler.evaluator = cpp_core.SubDEvaluator()

            # Convert to flat arrays for C++
            verts_flat = [coord for v in vertices for coord in v]
            faces_flat = []
            face_sizes = []
            for face in faces:
                face_sizes.append(len(face))
                faces_flat.extend(face)

            # Initialize
            success = AnalysisRequestHandler.evaluator.initialize(
                verts_flat, faces_flat, face_sizes
            )

            if not success:
                self._send_error('Failed to initialize evaluator')
                return

            # Run analysis
            if lens_name == 'differential':
                lens = DifferentialLens()
                regions = lens.analyze(AnalysisRequestHandler.evaluator)
                AnalysisRequestHandler.current_regions = regions
            else:
                # Other lenses not yet implemented
                regions = []

            # Convert regions to response format
            boundaries = []
            region_data = []

            for region in regions:
                # Convert boundary curves
                for curve in region.boundary:
                    boundaries.append({
                        'id': f"{region.id}_boundary",
                        'points': [
                            {'face_id': p[0], 'u': p[1], 'v': p[2]}
                            for p in curve.points
                        ],
                        'is_closed': curve.is_closed,
                        'is_pinned': region.pinned
                    })

                region_data.append({
                    'id': region.id,
                    'face_ids': region.faces,
                    'is_pinned': region.pinned,
                    'unity_principle': region.unity_principle,
                    'unity_strength': region.unity_strength
                })

            # Calculate overall resonance
            if regions:
                overall_resonance = sum(r.unity_strength for r in regions) / len(regions)
            else:
                overall_resonance = 0.0

            self._send_json({
                'boundaries': boundaries,
                'regions': region_data,
                'lens': lens_name,
                'overall_resonance': overall_resonance
            })

        else:
            # Mock response for testing without C++
            self._send_json({
                'boundaries': [
                    {
                        'id': 'mock_boundary_1',
                        'points': [
                            {'face_id': 0, 'u': 0.5, 'v': 0.0},
                            {'face_id': 0, 'u': 0.5, 'v': 1.0}
                        ],
                        'is_closed': False,
                        'is_pinned': False
                    }
                ],
                'regions': [
                    {
                        'id': 'mock_region_1',
                        'face_ids': [0, 1, 2, 3],
                        'is_pinned': False,
                        'unity_principle': 'mock',
                        'unity_strength': 0.8
                    }
                ],
                'lens': lens_name,
                'overall_resonance': 0.8
            })

    def _handle_evaluate(self):
        """Evaluate limit surface at parametric point"""
        data = self._read_json()
        if not data:
            self._send_error('Invalid JSON')
            return

        if not HAS_CPP or AnalysisRequestHandler.evaluator is None:
            self._send_error('Evaluator not initialized')
            return

        face_id = data.get('face_id', 0)
        u = data.get('u', 0.5)
        v = data.get('v', 0.5)

        point, normal = AnalysisRequestHandler.evaluator.evaluate_limit(face_id, u, v)

        self._send_json({
            'point': [point.x, point.y, point.z],
            'normal': [normal.x, normal.y, normal.z]
        })

    def _handle_project(self):
        """Project 3D point onto surface, return parametric coords"""
        data = self._read_json()
        if not data:
            self._send_error('Invalid JSON')
            return

        # This would need a spatial query structure
        # For now, return error
        self._send_error('Project not yet implemented', 501)

    def _handle_validate_boundary(self):
        """Validate a modified boundary"""
        data = self._read_json()
        if not data:
            self._send_error('Invalid JSON')
            return

        # Basic validation - check if points are within valid parameter range
        points = data.get('points', [])
        valid = True
        message = "OK"

        for p in points:
            u = p.get('u', 0)
            v = p.get('v', 0)
            if u < 0 or u > 1 or v < 0 or v > 1:
                valid = False
                message = f"Parameter out of range: ({u}, {v})"
                break

        self._send_json({
            'valid': valid,
            'message': message,
            'affected_regions': []
        })


def run_server(port: int = 5000):
    """Start the HTTP server"""
    server = HTTPServer(('localhost', port), AnalysisRequestHandler)
    print(f"Analysis engine running on http://localhost:{port}")
    print("Endpoints:")
    print("  GET  /health           - Check server status")
    print("  POST /analyze          - Run analysis on control cage")
    print("  POST /evaluate         - Evaluate limit surface point")
    print("  POST /validate_boundary - Validate boundary modification")
    print()
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analysis Engine HTTP Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    args = parser.parse_args()

    run_server(args.port)
