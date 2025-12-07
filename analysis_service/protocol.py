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
            method=data.get("method", ""),
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

    @staticmethod
    def make_success(result: dict, request_id: str) -> "JsonRpcResponse":
        return JsonRpcResponse(result=result, id=request_id)

    @staticmethod
    def make_error(code: int, message: str, request_id: str = "") -> "JsonRpcResponse":
        return JsonRpcResponse(error={"code": code, "message": message}, id=request_id)


# Standard JSON-RPC error codes
class ErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
