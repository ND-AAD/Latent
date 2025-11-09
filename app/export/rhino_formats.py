"""
Rhino Format Utilities

Validation and export utilities for Rhino-compatible NURBS data.
"""

import json
from typing import Dict, Any


def validate_nurbs_data(data: Dict) -> bool:
    """
    Validate NURBS data before export.

    Checks:
    - Required fields present
    - Array dimensions consistent
    - Knot vector validity
    """
    required = ['degree_u', 'degree_v', 'control_points', 'weights',
                'count_u', 'count_v', 'knots_u', 'knots_v']

    for field in required:
        if field not in data:
            return False

    # Check dimensions
    num_points = len(data['control_points'])
    expected = data['count_u'] * data['count_v']
    if num_points != expected:
        return False

    if len(data['weights']) != num_points:
        return False

    # Check knot vector lengths
    # For degree p, with n control points:
    # knot vector has n + p + 1 entries
    expected_u_knots = data['count_u'] + data['degree_u'] + 1
    expected_v_knots = data['count_v'] + data['degree_v'] + 1

    if len(data['knots_u']) != expected_u_knots:
        return False
    if len(data['knots_v']) != expected_v_knots:
        return False

    return True


def write_json_export(data: Dict, filepath: str, pretty: bool = True):
    """Write NURBS data to JSON file."""
    with open(filepath, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)
