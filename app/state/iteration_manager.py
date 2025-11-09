"""
Iteration Management System
Manages design snapshots for non-destructive exploration of different decompositions
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import uuid
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from app.state.parametric_region import ParametricRegion


@dataclass
class DesignIteration:
    """
    A snapshot of a design iteration.

    Stores complete state for non-destructive design exploration:
    - Regions discovered by mathematical lenses
    - Control cage data (for lossless representation)
    - Thumbnail for visual identification
    - Lens parameters and settings
    """
    id: str
    name: str
    timestamp: datetime
    regions: List[ParametricRegion] = field(default_factory=list)
    control_cage_data: Optional[Dict[str, Any]] = None  # Vertices, faces, creases
    thumbnail: Optional[bytes] = None  # PNG/JPG thumbnail (256x256)
    lens_used: Optional[str] = None  # Which mathematical lens generated this
    parameters: Dict[str, Any] = field(default_factory=dict)  # Lens-specific parameters
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional data

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize iteration to JSON-compatible dictionary

        Returns:
            Dictionary representation for JSON export
        """
        return {
            'id': self.id,
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'regions': [region.to_json() for region in self.regions],
            'control_cage_data': self.control_cage_data,
            'thumbnail_size': len(self.thumbnail) if self.thumbnail else 0,
            # Note: thumbnail stored separately as binary file to keep JSON readable
            'lens_used': self.lens_used,
            'parameters': self.parameters,
            'metadata': self.metadata,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any], thumbnail: Optional[bytes] = None) -> 'DesignIteration':
        """
        Deserialize iteration from JSON-compatible dictionary

        Args:
            data: Dictionary containing iteration data
            thumbnail: Optional thumbnail bytes (loaded separately)

        Returns:
            DesignIteration instance
        """
        # Parse timestamp
        timestamp_str = data.get('timestamp')
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()

        # Restore regions
        regions = [
            ParametricRegion.from_json(region_data)
            for region_data in data.get('regions', [])
        ]

        return cls(
            id=data['id'],
            name=data['name'],
            timestamp=timestamp,
            regions=regions,
            control_cage_data=data.get('control_cage_data'),
            thumbnail=thumbnail,
            lens_used=data.get('lens_used'),
            parameters=data.get('parameters', {}),
            metadata=data.get('metadata', {}),
        )

    def get_summary(self) -> str:
        """Get human-readable summary of this iteration"""
        lens = self.lens_used or "Unknown"
        count = len(self.regions)
        time = self.timestamp.strftime("%Y-%m-%d %H:%M")
        return f"{self.name} - {count} regions ({lens}) - {time}"


class IterationManager(QObject):
    """
    Manages collection of design iterations.

    Provides non-destructive design exploration by maintaining snapshots
    of different decomposition attempts. Users can:
    - Create new iterations from current state
    - Duplicate existing iterations
    - Switch between iterations
    - Delete unwanted iterations
    - Save/load entire iteration history
    """

    # Signals
    iterations_changed = pyqtSignal()  # Iteration list changed
    current_iteration_changed = pyqtSignal(str)  # Current iteration ID changed

    def __init__(self, work_directory: Optional[Path] = None):
        """
        Initialize iteration manager

        Args:
            work_directory: Directory for storing iteration data (optional)
        """
        super().__init__()

        self.iterations: List[DesignIteration] = []
        self.current_iteration_id: Optional[str] = None
        self.work_directory = work_directory or Path.home() / ".ceramic_mold_analyzer" / "iterations"

        # Ensure work directory exists
        self.work_directory.mkdir(parents=True, exist_ok=True)

    def create_iteration(
        self,
        name: str,
        regions: List[ParametricRegion],
        control_cage_data: Optional[Dict[str, Any]] = None,
        thumbnail: Optional[bytes] = None,
        lens_used: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> DesignIteration:
        """
        Create a new iteration from current state

        Args:
            name: Human-readable name for this iteration
            regions: List of parametric regions
            control_cage_data: Optional control cage data
            thumbnail: Optional thumbnail image (PNG/JPG bytes)
            lens_used: Name of mathematical lens used
            parameters: Lens-specific parameters

        Returns:
            Created DesignIteration
        """
        iteration = DesignIteration(
            id=f"iter_{uuid.uuid4().hex[:8]}",
            name=name,
            timestamp=datetime.now(),
            regions=regions,
            control_cage_data=control_cage_data,
            thumbnail=thumbnail,
            lens_used=lens_used,
            parameters=parameters or {},
        )

        self.iterations.append(iteration)
        self.current_iteration_id = iteration.id

        self.iterations_changed.emit()
        self.current_iteration_changed.emit(iteration.id)

        return iteration

    def duplicate_iteration(self, iteration_id: str, new_name: Optional[str] = None) -> Optional[DesignIteration]:
        """
        Duplicate an existing iteration

        Args:
            iteration_id: ID of iteration to duplicate
            new_name: Optional new name (defaults to "Copy of {original}")

        Returns:
            New DesignIteration or None if not found
        """
        source = self.get_iteration(iteration_id)
        if not source:
            return None

        # Create deep copy with new ID
        name = new_name or f"Copy of {source.name}"

        # Deep copy regions
        regions = [
            ParametricRegion(
                id=f"region_{uuid.uuid4().hex[:8]}",
                faces=region.faces.copy(),
                boundary=[curve for curve in region.boundary],
                unity_principle=region.unity_principle,
                unity_strength=region.unity_strength,
                pinned=region.pinned,
                metadata=region.metadata.copy(),
                modified=region.modified,
                constraints_passed=region.constraints_passed,
            )
            for region in source.regions
        ]

        return self.create_iteration(
            name=name,
            regions=regions,
            control_cage_data=source.control_cage_data.copy() if source.control_cage_data else None,
            thumbnail=source.thumbnail,
            lens_used=source.lens_used,
            parameters=source.parameters.copy(),
        )

    def delete_iteration(self, iteration_id: str) -> bool:
        """
        Delete an iteration

        Args:
            iteration_id: ID of iteration to delete

        Returns:
            True if deleted, False if not found
        """
        iteration = self.get_iteration(iteration_id)
        if not iteration:
            return False

        self.iterations.remove(iteration)

        # Update current if we deleted it
        if self.current_iteration_id == iteration_id:
            if self.iterations:
                self.current_iteration_id = self.iterations[-1].id
                self.current_iteration_changed.emit(self.current_iteration_id)
            else:
                self.current_iteration_id = None
                self.current_iteration_changed.emit("")

        self.iterations_changed.emit()

        return True

    def get_iteration(self, iteration_id: str) -> Optional[DesignIteration]:
        """
        Get iteration by ID

        Args:
            iteration_id: Iteration ID

        Returns:
            DesignIteration or None if not found
        """
        for iteration in self.iterations:
            if iteration.id == iteration_id:
                return iteration
        return None

    def get_current_iteration(self) -> Optional[DesignIteration]:
        """
        Get currently active iteration

        Returns:
            Current DesignIteration or None
        """
        if self.current_iteration_id:
            return self.get_iteration(self.current_iteration_id)
        return None

    def set_current_iteration(self, iteration_id: str) -> bool:
        """
        Switch to a different iteration

        Args:
            iteration_id: ID of iteration to switch to

        Returns:
            True if switched, False if not found
        """
        iteration = self.get_iteration(iteration_id)
        if not iteration:
            return False

        self.current_iteration_id = iteration_id
        self.current_iteration_changed.emit(iteration_id)

        return True

    def get_all_iterations(self) -> List[DesignIteration]:
        """
        Get all iterations sorted by timestamp (newest first)

        Returns:
            List of all DesignIterations
        """
        return sorted(self.iterations, key=lambda x: x.timestamp, reverse=True)

    def save_to_file(self, filepath: Path) -> bool:
        """
        Save all iterations to file

        Args:
            filepath: Path to save file

        Returns:
            True if successful
        """
        try:
            # Create directory structure
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Save JSON data
            data = {
                'version': '1.0',
                'current_iteration_id': self.current_iteration_id,
                'iterations': [iteration.to_json() for iteration in self.iterations],
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            # Save thumbnails separately
            for iteration in self.iterations:
                if iteration.thumbnail:
                    thumb_path = filepath.parent / f"{iteration.id}_thumb.png"
                    with open(thumb_path, 'wb') as f:
                        f.write(iteration.thumbnail)

            return True

        except Exception as e:
            print(f"Error saving iterations: {e}")
            return False

    def load_from_file(self, filepath: Path) -> bool:
        """
        Load iterations from file

        Args:
            filepath: Path to load file

        Returns:
            True if successful
        """
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                return False

            # Load JSON data
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Restore iterations
            self.iterations = []
            for iteration_data in data.get('iterations', []):
                # Load thumbnail if it exists
                thumb_path = filepath.parent / f"{iteration_data['id']}_thumb.png"
                thumbnail = None
                if thumb_path.exists():
                    with open(thumb_path, 'rb') as f:
                        thumbnail = f.read()

                iteration = DesignIteration.from_json(iteration_data, thumbnail)
                self.iterations.append(iteration)

            # Restore current iteration
            self.current_iteration_id = data.get('current_iteration_id')

            self.iterations_changed.emit()
            if self.current_iteration_id:
                self.current_iteration_changed.emit(self.current_iteration_id)

            return True

        except Exception as e:
            print(f"Error loading iterations: {e}")
            return False

    def clear(self):
        """Clear all iterations"""
        self.iterations = []
        self.current_iteration_id = None
        self.iterations_changed.emit()
        self.current_iteration_changed.emit("")

    def get_iteration_count(self) -> int:
        """Get total number of iterations"""
        return len(self.iterations)
