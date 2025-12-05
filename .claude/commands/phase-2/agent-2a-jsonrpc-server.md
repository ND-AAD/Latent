# Agent 2A: JSON-RPC Protocol & Server

## Objective

Create a JSON-RPC 2.0 server infrastructure for the Python analysis service.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `docs/plans/2025-12-04-rhino-plugin-implementation-plan.md` - protocol schema (lines 194-242)
- `analysis_service/__init__.py` - existing package structure

## Files to Create

1. `analysis_service/protocol.py` - request/response schemas
2. `analysis_service/server.py` - HTTP JSON-RPC server
3. `analysis_service/exceptions.py` - custom exceptions
4. `analysis_service/handlers.py` - method handlers (stubs)
5. `tests/test_analysis_protocol.py` - protocol tests

## Files to Modify

1. `analysis_service/__main__.py` - launch server
2. `analysis_service/requirements.txt` - add dependencies

## Tasks

### 1. Create protocol.py

```python
# analysis_service/protocol.py
"""
JSON-RPC 2.0 protocol definitions for the analysis service.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional, List, Dict
from enum import Enum
import json


class LensType(str, Enum):
    DIFFERENTIAL = "differential"
    SPECTRAL = "spectral"
    CAGE_ALIGNED = "cage_aligned"


@dataclass
class ControlCage:
    """SubD control cage representation."""
    vertices: List[List[float]]  # [[x, y, z], ...]
    faces: List[List[int]]       # [[v0, v1, v2, ...], ...]
    creases: List[List[float]] = field(default_factory=list)  # [[v0, v1, sharpness], ...]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ControlCage":
        return cls(
            vertices=data["vertices"],
            faces=data["faces"],
            creases=data.get("creases", [])
        )


@dataclass
class ParametricPoint:
    """A point in SubD parametric space."""
    face_id: int
    u: float
    v: float

    def to_list(self) -> List:
        return [self.face_id, self.u, self.v]

    @classmethod
    def from_list(cls, data: List) -> "ParametricPoint":
        return cls(face_id=data[0], u=data[1], v=data[2])


@dataclass
class BoundaryCurve:
    """A curve defined by control points in parametric space."""
    control_points: List[ParametricPoint]
    curve_type: str = "bezier"
    degree: int = 3

    def to_dict(self) -> dict:
        return {
            "control_points": [p.to_list() for p in self.control_points],
            "type": self.curve_type,
            "degree": self.degree
        }


@dataclass
class Vertex:
    """A vertex in the region graph."""
    id: str
    position: ParametricPoint
    implicit_position: Optional[ParametricPoint] = None
    created_by: str = "lens"
    is_pinned: bool = False

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "position": self.position.to_list(),
            "created_by": self.created_by,
            "is_pinned": self.is_pinned
        }
        if self.implicit_position:
            result["implicit_position"] = self.implicit_position.to_list()
        return result


@dataclass
class Edge:
    """An edge (boundary curve) in the region graph."""
    id: str
    vertex_ids: List[str]
    curve_type: str = "bezier"
    degree: int = 3
    is_pinned: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "vertex_ids": self.vertex_ids,
            "curve_type": self.curve_type,
            "degree": self.degree,
            "is_pinned": self.is_pinned
        }


@dataclass
class Region:
    """A region bounded by edges."""
    id: str
    boundary_edge_ids: List[str]
    boundary_curves: List[BoundaryCurve]
    unity_principle: str
    resonance_score: float
    is_pinned: bool = False
    is_implicit: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "boundary_edge_ids": self.boundary_edge_ids,
            "boundary_curves": [c.to_dict() for c in self.boundary_curves],
            "unity_principle": self.unity_principle,
            "resonance_score": self.resonance_score,
            "is_pinned": self.is_pinned,
            "is_implicit": self.is_implicit
        }


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    regions: List[Region]
    vertices: List[Vertex]
    edges: List[Edge]

    def to_dict(self) -> dict:
        return {
            "regions": [r.to_dict() for r in self.regions],
            "vertices": [v.to_dict() for v in self.vertices],
            "edges": [e.to_dict() for e in self.edges]
        }


@dataclass
class JsonRpcRequest:
    """JSON-RPC 2.0 request."""
    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: str

    @classmethod
    def from_dict(cls, data: dict) -> "JsonRpcRequest":
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            method=data["method"],
            params=data.get("params", {}),
            id=data.get("id", "")
        )

    def validate(self) -> Optional[str]:
        """Validate request format. Returns error message or None."""
        if self.jsonrpc != "2.0":
            return "Invalid JSON-RPC version"
        if not self.method:
            return "Missing method"
        return None


@dataclass
class JsonRpcResponse:
    """JSON-RPC 2.0 response."""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: str = ""

    def to_dict(self) -> dict:
        response = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response

    @classmethod
    def success(cls, result: dict, request_id: str) -> "JsonRpcResponse":
        return cls(result=result, id=request_id)

    @classmethod
    def error(cls, code: int, message: str, request_id: str = "") -> "JsonRpcResponse":
        return cls(error={"code": code, "message": message}, id=request_id)


# Standard JSON-RPC error codes
class ErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
```

### 2. Create exceptions.py

```python
# analysis_service/exceptions.py
"""Custom exceptions for the analysis service."""


class AnalysisError(Exception):
    """Base exception for analysis errors."""
    pass


class InvalidCageError(AnalysisError):
    """Raised when control cage data is invalid."""
    pass


class LensError(AnalysisError):
    """Raised when lens analysis fails."""
    pass


class BoundaryExtractionError(AnalysisError):
    """Raised when boundary curve extraction fails."""
    pass


class ServiceNotInitializedError(AnalysisError):
    """Raised when service is used before initialization."""
    pass
```

### 3. Create handlers.py

```python
# analysis_service/handlers.py
"""
Request handlers for the analysis service.

Actual lens implementation will be added in Agents 2B and 2C.
"""

from typing import Dict, Any
import logging

from .protocol import (
    ControlCage, AnalysisResult, Region, Vertex, Edge,
    BoundaryCurve, ParametricPoint, LensType
)
from .exceptions import InvalidCageError, LensError

logger = logging.getLogger(__name__)


class AnalysisHandler:
    """Handles analysis requests."""

    def __init__(self):
        self._cage: ControlCage | None = None
        self._initialized = False

    def initialize(self, cage_data: dict) -> dict:
        """Initialize with control cage data."""
        try:
            self._cage = ControlCage.from_dict(cage_data)
            self._initialized = True
            logger.info(f"Initialized with {len(self._cage.vertices)} vertices, "
                       f"{len(self._cage.faces)} faces")
            return {"status": "initialized"}
        except (KeyError, TypeError) as e:
            raise InvalidCageError(f"Invalid cage data: {e}")

    def analyze(self, lens: str, params: dict, pinned_regions: list = None) -> dict:
        """Run lens analysis."""
        if not self._initialized:
            raise LensError("Service not initialized")

        lens_type = LensType(lens)
        logger.info(f"Running {lens_type.value} analysis with params: {params}")

        # Dispatch to lens-specific handler
        if lens_type == LensType.DIFFERENTIAL:
            result = self._analyze_differential(params)
        elif lens_type == LensType.SPECTRAL:
            result = self._analyze_spectral(params)
        else:
            result = self._analyze_cage_aligned(params)

        return result.to_dict()

    def _analyze_differential(self, params: dict) -> AnalysisResult:
        """Differential (curvature) lens analysis."""
        # TODO: Agent 2B will implement this
        # For now, return empty result
        logger.warning("Differential lens not yet implemented")
        return AnalysisResult(regions=[], vertices=[], edges=[])

    def _analyze_spectral(self, params: dict) -> AnalysisResult:
        """Spectral (eigenfunction) lens analysis."""
        # TODO: Agent 2C will implement this
        logger.warning("Spectral lens not yet implemented")
        return AnalysisResult(regions=[], vertices=[], edges=[])

    def _analyze_cage_aligned(self, params: dict) -> AnalysisResult:
        """Cage-aligned lens analysis (degenerate case)."""
        # Uses control cage edges directly
        logger.warning("Cage-aligned lens not yet implemented")
        return AnalysisResult(regions=[], vertices=[], edges=[])

    def get_boundaries(self, region_ids: list) -> dict:
        """Get boundary curves for specific regions."""
        # TODO: Implement after analysis is working
        return {"boundaries": []}
```

### 4. Create server.py

```python
# analysis_service/server.py
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
                return JsonRpcResponse.error(
                    ErrorCode.INVALID_REQUEST, error, request.id
                ).to_dict()

            # Find method handler
            method_handler = self._methods.get(request.method)
            if not method_handler:
                return JsonRpcResponse.error(
                    ErrorCode.METHOD_NOT_FOUND,
                    f"Method not found: {request.method}",
                    request.id
                ).to_dict()

            # Execute method
            result = method_handler(request.params)
            return JsonRpcResponse.success(result, request.id).to_dict()

        except AnalysisError as e:
            logger.error(f"Analysis error: {e}")
            return JsonRpcResponse.error(
                ErrorCode.INTERNAL_ERROR, str(e), request_data.get("id", "")
            ).to_dict()

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JsonRpcResponse.error(
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
        response = JsonRpcResponse.error(code, message).to_dict()
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
```

### 5. Update __main__.py

```python
# analysis_service/__main__.py
"""
Entry point for running the analysis service.

Usage: python -m analysis_service [--port PORT] [--host HOST]
"""

import argparse
import logging
import sys

from .server import run_server


def main():
    parser = argparse.ArgumentParser(description="Latent Analysis Service")
    parser.add_argument("--port", type=int, default=5555, help="Port to listen on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting analysis service on {args.host}:{args.port}")

    try:
        run_server(host=args.host, port=args.port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 6. Create Protocol Tests

```python
# tests/test_analysis_protocol.py
"""Tests for the analysis service protocol."""

import pytest
import json
import threading
import time
import urllib.request
from http.server import HTTPServer

from analysis_service.protocol import (
    JsonRpcRequest, JsonRpcResponse, ControlCage,
    ParametricPoint, BoundaryCurve, Region, Vertex, Edge, ErrorCode
)
from analysis_service.server import AnalysisService, JsonRpcHandler


class TestProtocolDataClasses:
    """Test protocol data structures."""

    def test_parametric_point_roundtrip(self):
        point = ParametricPoint(face_id=0, u=0.5, v=0.75)
        data = point.to_list()
        restored = ParametricPoint.from_list(data)

        assert restored.face_id == 0
        assert restored.u == 0.5
        assert restored.v == 0.75

    def test_control_cage_from_dict(self):
        data = {
            "vertices": [[0, 0, 0], [1, 0, 0], [1, 1, 0]],
            "faces": [[0, 1, 2]],
            "creases": []
        }
        cage = ControlCage.from_dict(data)

        assert len(cage.vertices) == 3
        assert len(cage.faces) == 1
        assert cage.vertices[1] == [1, 0, 0]

    def test_region_to_dict(self):
        region = Region(
            id="r1",
            boundary_edge_ids=["e1", "e2"],
            boundary_curves=[],
            unity_principle="Test",
            resonance_score=0.85
        )
        data = region.to_dict()

        assert data["id"] == "r1"
        assert data["resonance_score"] == 0.85
        assert data["is_implicit"] is True


class TestJsonRpcRequest:
    """Test JSON-RPC request handling."""

    def test_valid_request(self):
        data = {
            "jsonrpc": "2.0",
            "method": "analyze",
            "params": {"lens": "differential"},
            "id": "1"
        }
        request = JsonRpcRequest.from_dict(data)

        assert request.validate() is None
        assert request.method == "analyze"

    def test_invalid_version(self):
        data = {
            "jsonrpc": "1.0",
            "method": "test",
            "id": "1"
        }
        request = JsonRpcRequest.from_dict(data)
        assert request.validate() is not None

    def test_missing_method(self):
        data = {"jsonrpc": "2.0", "id": "1"}
        request = JsonRpcRequest.from_dict(data)
        assert "method" in str(request.validate()).lower()


class TestJsonRpcResponse:
    """Test JSON-RPC response formatting."""

    def test_success_response(self):
        response = JsonRpcResponse.success({"status": "ok"}, "123")
        data = response.to_dict()

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "123"
        assert data["result"]["status"] == "ok"
        assert "error" not in data

    def test_error_response(self):
        response = JsonRpcResponse.error(ErrorCode.METHOD_NOT_FOUND, "Not found", "123")
        data = response.to_dict()

        assert data["error"]["code"] == ErrorCode.METHOD_NOT_FOUND
        assert "Not found" in data["error"]["message"]


class TestAnalysisService:
    """Test the analysis service."""

    def test_ping(self):
        service = AnalysisService()
        response = service.handle_request({
            "jsonrpc": "2.0",
            "method": "ping",
            "params": {},
            "id": "1"
        })

        assert "result" in response
        assert response["result"]["status"] == "ok"

    def test_initialize(self):
        service = AnalysisService()
        response = service.handle_request({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "cage": {
                    "vertices": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
                    "faces": [[0, 1, 2, 3]],
                    "creases": []
                }
            },
            "id": "1"
        })

        assert "result" in response
        assert response["result"]["status"] == "initialized"

    def test_method_not_found(self):
        service = AnalysisService()
        response = service.handle_request({
            "jsonrpc": "2.0",
            "method": "nonexistent",
            "params": {},
            "id": "1"
        })

        assert "error" in response
        assert response["error"]["code"] == ErrorCode.METHOD_NOT_FOUND


class TestHttpServer:
    """Test the HTTP server (integration test)."""

    @pytest.fixture
    def server(self):
        """Start a test server."""
        service = AnalysisService()
        JsonRpcHandler.service = service

        server = HTTPServer(("localhost", 0), JsonRpcHandler)
        port = server.server_address[1]

        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        yield f"http://localhost:{port}"

        server.shutdown()

    def test_ping_via_http(self, server):
        request_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "ping",
            "params": {},
            "id": "1"
        }).encode("utf-8")

        req = urllib.request.Request(
            server,
            data=request_data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())

        assert data["result"]["status"] == "ok"
```

### 7. Update requirements.txt

```text
# analysis_service/requirements.txt
numpy>=1.21.0
scipy>=1.7.0
pytest>=7.0.0
```

## Success Criteria

- [ ] Server starts without errors
- [ ] `ping` method returns `{"status": "ok"}`
- [ ] `initialize` accepts control cage data
- [ ] `analyze` dispatches to lens handlers (returns empty result for now)
- [ ] Invalid requests return proper JSON-RPC errors
- [ ] All protocol tests pass
- [ ] HTTP integration test passes

## Verification Commands

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent

# Run protocol tests
python -m pytest tests/test_analysis_protocol.py -v

# Start server manually (in background)
python -m analysis_service --debug &
SERVER_PID=$!
sleep 2

# Test ping
curl -X POST http://localhost:5555 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","params":{},"id":"1"}'

# Test initialize
curl -X POST http://localhost:5555 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"initialize",
    "params":{"cage":{"vertices":[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],"faces":[[0,1,2,3]],"creases":[]}},
    "id":"2"
  }'

# Kill server
kill $SERVER_PID
```

## Do Not Modify

- Existing files in `app/analysis/` (Agents 2B/2C will modify those)
- Files in `cpp_core/`

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run all tests

## Report

When complete, provide:
1. Test output showing all tests pass
2. Sample curl output for ping and initialize
3. Any issues encountered
