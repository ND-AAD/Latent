"""
Simple HTTP server to receive geometry from Grasshopper
Runs on port 5000 in the desktop app
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from PyQt6.QtCore import QObject, pyqtSignal


class GeometryReceiverHandler(BaseHTTPRequestHandler):
    """HTTP handler for receiving geometry from Grasshopper"""

    # Class variable to store reference to the receiver
    receiver = None

    def do_POST(self):
        """Handle POST requests with geometry data"""
        print(f"📨 POST request received: {self.path}")
        print(f"   Headers: {dict(self.headers)}")

        if self.path == '/receive_geometry':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                print(f"   Content-Length: {content_length}")

                post_data = self.rfile.read(content_length)
                geometry_data = json.loads(post_data.decode('utf-8'))

                print(f"   ✅ Parsed geometry: {geometry_data.get('vertex_count')}V, {geometry_data.get('face_count')}F")

                # Send to receiver
                if self.receiver:
                    self.receiver.handle_geometry(geometry_data)
                else:
                    print("   ⚠️ No receiver set!")

                # Send success response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                response = {'status': 'received'}
                self.wfile.write(json.dumps(response).encode())
                print("   📤 Sent 200 OK response")

            except Exception as e:
                print(f"   ❌ Error receiving geometry: {e}")
                import traceback
                traceback.print_exc()
                self.send_error(500, str(e))
        else:
            print(f"   ❌ Unknown path: {self.path}")
            self.send_error(404)

    def do_OPTIONS(self):
        """Handle OPTIONS for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Log HTTP requests for debugging"""
        print(f"🔍 HTTP: {format % args}")


class GeometryReceiver(QObject):
    """Receives geometry from Grasshopper via HTTP"""

    geometry_received = pyqtSignal(dict)

    def __init__(self, port=5000):
        super().__init__()
        self.port = port
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the HTTP server"""
        try:
            self.server = HTTPServer(('localhost', self.port), GeometryReceiverHandler)
            GeometryReceiverHandler.receiver = self  # Set class reference

            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"✅ Geometry receiver listening on port {self.port}")
            return True

        except Exception as e:
            print(f"Failed to start geometry receiver: {e}")
            return False

    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            print("🛑 Geometry receiver stopped")

    def handle_geometry(self, geometry_data):
        """Handle received geometry data"""
        # Emit signal on Qt thread
        self.geometry_received.emit(geometry_data)
