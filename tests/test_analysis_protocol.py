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
        response = JsonRpcResponse.make_success({"status": "ok"}, "123")
        data = response.to_dict()

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "123"
        assert data["result"]["status"] == "ok"
        assert "error" not in data

    def test_error_response(self):
        response = JsonRpcResponse.make_error(ErrorCode.METHOD_NOT_FOUND, "Not found", "123")
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
