"""
JSON-RPC 2.0 HTTP server for the analysis service.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Dict, Any

from .protocol import JsonRpcRequest, JsonRpcResponse, ErrorCode
from .handlers import AnalysisHandler
from .exceptions import AnalysisError

logger = logging.getLogger(__name__)


class AnalysisService:
    """Main analysis service."""

    def __init__(self):
        self.handler = AnalysisHandler()
        self._methods: Dict[str, Callable] = {
            "initialize": self._handle_initialize,
            "analyze": self._handle_analyze,
            "get_boundaries": self._handle_get_boundaries,
            "ping": self._handle_ping,
        }

    def handle_request(self, request_data: dict) -> dict:
        """Handle a JSON-RPC request."""
        try:
            request = JsonRpcRequest.from_dict(request_data)

            # Validate request
            error = request.validate()
            if error:
                return JsonRpcResponse.make_error(
                    ErrorCode.INVALID_REQUEST, error, request.id
                ).to_dict()

            # Find method handler
            method_handler = self._methods.get(request.method)
            if not method_handler:
                return JsonRpcResponse.make_error(
                    ErrorCode.METHOD_NOT_FOUND,
                    f"Method not found: {request.method}",
                    request.id
                ).to_dict()

            # Execute method
            result = method_handler(request.params)
            return JsonRpcResponse.make_success(result, request.id).to_dict()

        except AnalysisError as e:
            logger.error(f"Analysis error: {e}")
            return JsonRpcResponse.make_error(
                ErrorCode.INTERNAL_ERROR, str(e), request_data.get("id", "")
            ).to_dict()

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JsonRpcResponse.make_error(
                ErrorCode.INTERNAL_ERROR,
                f"Internal error: {e}",
                request_data.get("id", "")
            ).to_dict()

    def _handle_initialize(self, params: dict) -> dict:
        return self.handler.initialize(params.get("cage", {}))

    def _handle_analyze(self, params: dict) -> dict:
        return self.handler.analyze(
            lens=params.get("lens", "differential"),
            params=params.get("params", {}),
            pinned_regions=params.get("pinned_regions", [])
        )

    def _handle_get_boundaries(self, params: dict) -> dict:
        return self.handler.get_boundaries(params.get("region_ids", []))

    def _handle_ping(self, params: dict) -> dict:
        return {"status": "ok", "version": "0.1.0"}


class JsonRpcHandler(BaseHTTPRequestHandler):
    """HTTP handler for JSON-RPC requests."""

    service: AnalysisService = None  # Set by server

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode("utf-8"))

            response_data = self.service.handle_request(request_data)
            response_body = json.dumps(response_data).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(response_body))
            self.end_headers()
            self.wfile.write(response_body)

        except json.JSONDecodeError as e:
            self._send_error(ErrorCode.PARSE_ERROR, f"Parse error: {e}")

        except Exception as e:
            logger.exception(f"HTTP error: {e}")
            self._send_error(ErrorCode.INTERNAL_ERROR, str(e))

    def _send_error(self, code: int, message: str):
        response = JsonRpcResponse.make_error(code, message).to_dict()
        response_body = json.dumps(response).encode("utf-8")

        self.send_response(200)  # JSON-RPC errors use 200 status
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        logger.debug(f"{self.client_address[0]} - {format % args}")


def run_server(host: str = "localhost", port: int = 5555):
    """Start the analysis service HTTP server."""
    service = AnalysisService()
    JsonRpcHandler.service = service

    server = HTTPServer((host, port), JsonRpcHandler)
    logger.info(f"Analysis service listening on http://{host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()
