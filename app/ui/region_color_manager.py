"""
Region Color Manager - Assign and manage colors for regions.

Provides:
- Generation of N visually distinct colors using HSV color wheel
- Color persistence for pinned regions
- User color override support
- Color scheme export/import
"""

import json
import colorsys
from typing import List, Dict, Tuple, Optional
from app.state.parametric_region import ParametricRegion


class RegionColorManager:
    """
    Manages color assignment for regions.

    Features:
    - Generates visually distinct colors using HSV color wheel
    - Respects user overrides and pinned region colors
    - Persists color schemes to JSON
    - Provides color cycling for large region counts
    """

    def __init__(self):
        """Initialize the color manager."""
        # Maps region ID -> RGB color tuple (0-1 range)
        self.region_colors: Dict[str, Tuple[float, float, float]] = {}

        # User overrides - takes precedence over auto-generated colors
        self.user_overrides: Dict[str, Tuple[float, float, float]] = {}

        # Color generation parameters
        self.saturation = 0.75  # 75% saturation for vivid colors
        self.value = 0.85       # 85% value for bright but not harsh colors

        # Default color for unassigned regions
        self.default_color = (0.7, 0.7, 0.8)  # Light blue-gray

    def assign_colors(self, regions: List[ParametricRegion], preserve_existing: bool = True):
        """
        Assign colors to a list of regions.

        Generates visually distinct colors using HSV color wheel.
        Preserves existing colors for pinned regions by default.

        Args:
            regions: List of ParametricRegion to assign colors to
            preserve_existing: If True, keep colors for existing regions
        """
        if not regions:
            return

        # Separate regions into categories
        existing_colored = []
        needs_color = []

        for region in regions:
            if preserve_existing and region.id in self.region_colors:
                existing_colored.append(region)
            else:
                needs_color.append(region)

        # Generate new colors for regions that need them
        if needs_color:
            new_colors = self._generate_distinct_colors(len(needs_color))

            for region, color in zip(needs_color, new_colors):
                self.region_colors[region.id] = color

    def _generate_distinct_colors(self, count: int) -> List[Tuple[float, float, float]]:
        """
        Generate N visually distinct colors using HSV color wheel.

        Uses golden ratio for optimal hue distribution to maximize
        perceptual distinctiveness.

        Args:
            count: Number of colors to generate

        Returns:
            List of RGB tuples (0-1 range)
        """
        if count == 0:
            return []

        colors = []
        golden_ratio = 0.618033988749895  # Golden ratio conjugate

        # Start at a random-ish hue to avoid always starting with red
        hue = 0.3  # Start in green-cyan region

        for i in range(count):
            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(hue, self.saturation, self.value)
            colors.append(rgb)

            # Increment hue using golden ratio for maximum spacing
            hue = (hue + golden_ratio) % 1.0

        return colors

    def get_color(self, region_id: str) -> Tuple[float, float, float]:
        """
        Get the color for a region.

        Checks user overrides first, then assigned colors, then default.

        Args:
            region_id: ID of the region

        Returns:
            RGB color tuple (0-1 range)
        """
        # User override takes precedence
        if region_id in self.user_overrides:
            return self.user_overrides[region_id]

        # Then check assigned colors
        if region_id in self.region_colors:
            return self.region_colors[region_id]

        # Fall back to default
        return self.default_color

    def set_color(self, region_id: str, color: Tuple[float, float, float]):
        """
        Set a specific color for a region (user override).

        Args:
            region_id: ID of the region
            color: RGB color tuple (0-1 range)
        """
        self.user_overrides[region_id] = color

    def clear_override(self, region_id: str):
        """
        Clear user override for a region.

        Args:
            region_id: ID of the region
        """
        if region_id in self.user_overrides:
            del self.user_overrides[region_id]

    def get_highlight_color(self, region_id: str, factor: float = 1.3) -> Tuple[float, float, float]:
        """
        Get a lighter shade of region color for highlighting.

        Used for hover effects and selection highlighting.

        Args:
            region_id: ID of the region
            factor: Lightening factor (>1.0 for lighter, <1.0 for darker)

        Returns:
            RGB color tuple (0-1 range)
        """
        base_color = self.get_color(region_id)

        # Convert to HSV for easier manipulation
        h, s, v = colorsys.rgb_to_hsv(*base_color)

        # Increase value (brightness) and decrease saturation for lighter shade
        v = min(1.0, v * factor)
        s = max(0.0, s * 0.7)  # Reduce saturation for pastel effect

        # Convert back to RGB
        return colorsys.hsv_to_rgb(h, s, v)

    def get_boundary_color(self, region_id: str, darken: float = 0.7) -> Tuple[float, float, float]:
        """
        Get a darker shade of region color for boundary rendering.

        Args:
            region_id: ID of the region
            darken: Darkening factor (0-1, lower is darker)

        Returns:
            RGB color tuple (0-1 range)
        """
        base_color = self.get_color(region_id)

        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(*base_color)

        # Darken the value
        v = v * darken
        s = min(1.0, s * 1.2)  # Increase saturation slightly

        # Convert back to RGB
        return colorsys.hsv_to_rgb(h, s, v)

    def remove_region(self, region_id: str):
        """
        Remove color assignment for a region.

        Args:
            region_id: ID of the region to remove
        """
        if region_id in self.region_colors:
            del self.region_colors[region_id]

        if region_id in self.user_overrides:
            del self.user_overrides[region_id]

    def clear_all(self):
        """Clear all color assignments and overrides."""
        self.region_colors.clear()
        self.user_overrides.clear()

    def to_dict(self) -> Dict:
        """
        Export color scheme to dictionary for JSON serialization.

        Returns:
            Dictionary with color mappings
        """
        return {
            'region_colors': {
                region_id: list(color)
                for region_id, color in self.region_colors.items()
            },
            'user_overrides': {
                region_id: list(color)
                for region_id, color in self.user_overrides.items()
            },
            'saturation': self.saturation,
            'value': self.value,
            'default_color': list(self.default_color)
        }

    def from_dict(self, data: Dict):
        """
        Load color scheme from dictionary.

        Args:
            data: Dictionary with color mappings
        """
        # Load region colors
        self.region_colors = {
            region_id: tuple(color)
            for region_id, color in data.get('region_colors', {}).items()
        }

        # Load user overrides
        self.user_overrides = {
            region_id: tuple(color)
            for region_id, color in data.get('user_overrides', {}).items()
        }

        # Load parameters
        self.saturation = data.get('saturation', 0.75)
        self.value = data.get('value', 0.85)
        self.default_color = tuple(data.get('default_color', [0.7, 0.7, 0.8]))

    def save_to_json(self, filepath: str):
        """
        Save color scheme to JSON file.

        Args:
            filepath: Path to save JSON file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_json(self, filepath: str):
        """
        Load color scheme from JSON file.

        Args:
            filepath: Path to JSON file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.from_dict(data)

    def get_all_colors(self) -> Dict[str, Tuple[float, float, float]]:
        """
        Get all region colors including overrides.

        Returns:
            Dictionary mapping region IDs to RGB colors
        """
        # Merge auto-assigned and user override colors
        all_colors = dict(self.region_colors)
        all_colors.update(self.user_overrides)
        return all_colors
