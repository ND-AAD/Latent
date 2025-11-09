"""
Rhino Format Utilities

Validation and export utilities for Rhino-compatible NURBS data.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from app.utils.error_handling import get_logger, handle_exceptions

logger = get_logger(__name__)


def validate_nurbs_data(data: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate NURBS data before export.

    Checks:
    - Required fields present
    - Array dimensions consistent
    - Knot vector validity

    Args:
        data: NURBS data dictionary

    Returns:
        (is_valid, error_message) tuple
    """
    if not data:
        return False, "NURBS data is empty"

    required = ['degree_u', 'degree_v', 'control_points', 'weights',
                'count_u', 'count_v', 'knots_u', 'knots_v']

    for field in required:
        if field not in data:
            return False, f"Missing required field: {field}"

    try:
        # Validate types
        if not isinstance(data['degree_u'], int) or not isinstance(data['degree_v'], int):
            return False, "Degrees must be integers"

        if data['degree_u'] < 1 or data['degree_v'] < 1:
            return False, f"Invalid degrees: u={data['degree_u']}, v={data['degree_v']}"

        if not isinstance(data['count_u'], int) or not isinstance(data['count_v'], int):
            return False, "Counts must be integers"

        if data['count_u'] < 2 or data['count_v'] < 2:
            return False, f"Invalid counts: u={data['count_u']}, v={data['count_v']}"

        # Check dimensions
        num_points = len(data['control_points'])
        expected = data['count_u'] * data['count_v']

        if num_points != expected:
            return False, (
                f"Control point count mismatch: got {num_points}, "
                f"expected {expected} ({data['count_u']} × {data['count_v']})"
            )

        if len(data['weights']) != num_points:
            return False, (
                f"Weight count mismatch: got {len(data['weights'])}, "
                f"expected {num_points}"
            )

        # Check knot vector lengths
        # For degree p, with n control points:
        # knot vector has n + p + 1 entries
        expected_u_knots = data['count_u'] + data['degree_u'] + 1
        expected_v_knots = data['count_v'] + data['degree_v'] + 1

        if len(data['knots_u']) != expected_u_knots:
            return False, (
                f"U knot vector length mismatch: got {len(data['knots_u'])}, "
                f"expected {expected_u_knots}"
            )

        if len(data['knots_v']) != expected_v_knots:
            return False, (
                f"V knot vector length mismatch: got {len(data['knots_v'])}, "
                f"expected {expected_v_knots}"
            )

        # Validate knot vectors are non-decreasing
        if not all(data['knots_u'][i] <= data['knots_u'][i+1]
                   for i in range(len(data['knots_u'])-1)):
            return False, "U knot vector is not non-decreasing"

        if not all(data['knots_v'][i] <= data['knots_v'][i+1]
                   for i in range(len(data['knots_v'])-1)):
            return False, "V knot vector is not non-decreasing"

    except (KeyError, TypeError, IndexError) as e:
        return False, f"Data validation error: {e}"

    return True, None


def write_json_export(data: Dict, filepath: str, pretty: bool = True) -> tuple[bool, Optional[str]]:
    """
    Write NURBS data to JSON file.

    Args:
        data: NURBS data dictionary
        filepath: Output file path
        pretty: Whether to use pretty formatting

    Returns:
        (success, error_message) tuple
    """
    if not data:
        logger.error("Cannot write empty data")
        return False, "No data to write"

    if not filepath:
        logger.error("No filepath provided")
        return False, "No filepath provided"

    try:
        # Ensure parent directory exists
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Check write permissions
        if path.exists() and not os.access(filepath, os.W_OK):
            error_msg = f"No write permission for file: {filepath}"
            logger.error(error_msg)
            return False, error_msg

        # Write file
        logger.info(f"Writing JSON to {filepath}")
        with open(filepath, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)

        logger.info(f"Successfully wrote {filepath}")
        return True, None

    except PermissionError as e:
        error_msg = f"Permission denied writing to {filepath}: {e}"
        logger.error(error_msg)
        return False, error_msg
    except OSError as e:
        error_msg = f"OS error writing to {filepath}: {e}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    except TypeError as e:
        error_msg = f"Data serialization error: {e}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error writing to {filepath}: {e}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg


def read_json_import(filepath: str) -> tuple[Optional[Dict], Optional[str]]:
    """
    Read NURBS data from JSON file.

    Args:
        filepath: Input file path

    Returns:
        (data_dict, error_message) tuple
    """
    if not filepath:
        return None, "No filepath provided"

    path = Path(filepath)

    # Check file exists
    if not path.exists():
        error_msg = f"File not found: {filepath}"
        logger.error(error_msg)
        return None, error_msg

    # Check read permissions
    if not os.access(filepath, os.R_OK):
        error_msg = f"No read permission for file: {filepath}"
        logger.error(error_msg)
        return None, error_msg

    try:
        logger.info(f"Reading JSON from {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)

        logger.info(f"Successfully read {filepath}")
        return data, None

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {filepath}: {e}"
        logger.error(error_msg)
        return None, error_msg
    except PermissionError as e:
        error_msg = f"Permission denied reading {filepath}: {e}"
        logger.error(error_msg)
        return None, error_msg
    except OSError as e:
        error_msg = f"OS error reading {filepath}: {e}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error reading {filepath}: {e}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg
