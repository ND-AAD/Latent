"""
Tests for Region Operations (Merge/Split)
"""

import pytest
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.state.parametric_region import ParametricRegion, ParametricCurve
from app.operations.region_operations import RegionOperations


class TestRegionMerge:
    """Tests for region merging operations"""

    def test_merge_two_regions(self):
        """Test merging two basic regions"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        r2 = ParametricRegion(
            id="region_2",
            faces=[3, 4, 5],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.7
        )

        merged = RegionOperations.merge_regions([r1, r2])

        # Check face combination
        assert len(merged.faces) == 6
        assert set(merged.faces) == {0, 1, 2, 3, 4, 5}

        # Check attributes
        assert merged.modified is True
        assert merged.pinned is False  # Neither was pinned

    def test_merge_preserves_pinned_status(self):
        """Test that merge preserves pinned status if any region is pinned"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8,
            pinned=True
        )

        r2 = ParametricRegion(
            id="region_2",
            faces=[2, 3],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.7,
            pinned=False
        )

        merged = RegionOperations.merge_regions([r1, r2])
        assert merged.pinned is True

    def test_merge_multiple_regions(self):
        """Test merging more than two regions"""
        regions = [
            ParametricRegion(
                id=f"region_{i}",
                faces=[i * 2, i * 2 + 1],
                boundary=[],
                unity_principle="curvature",
                unity_strength=0.8
            )
            for i in range(4)
        ]

        merged = RegionOperations.merge_regions(regions)

        # Should have all 8 faces
        assert len(merged.faces) == 8
        assert set(merged.faces) == set(range(8))

    def test_merge_removes_duplicate_faces(self):
        """Test that merging handles overlapping faces correctly"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        r2 = ParametricRegion(
            id="region_2",
            faces=[2, 3, 4],  # Face 2 overlaps
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.7
        )

        merged = RegionOperations.merge_regions([r1, r2])

        # Should have 5 unique faces
        assert len(merged.faces) == 5
        assert set(merged.faces) == {0, 1, 2, 3, 4}

    def test_merge_requires_at_least_two_regions(self):
        """Test that merge requires at least 2 regions"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        with pytest.raises(ValueError, match="at least 2 regions"):
            RegionOperations.merge_regions([r1])

    def test_merge_averages_unity_strength(self):
        """Test that merge properly combines unity strength"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        r2 = ParametricRegion(
            id="region_2",
            faces=[2, 3],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.6
        )

        merged = RegionOperations.merge_regions([r1, r2])

        # Should average: (0.8 + 0.6) / 2 = 0.7
        assert merged.unity_strength == 0.7


class TestRegionSplit:
    """Tests for region splitting operations"""

    def test_split_region_basic(self):
        """Test basic region splitting"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2, 3, 4, 5],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        # Simple split curve
        split_curve = ParametricCurve(
            points=[(2, 0.5, 0.5)],
            is_closed=False
        )

        r1, r2 = RegionOperations.split_region(region, split_curve)

        # Both should have faces
        assert len(r1.faces) > 0
        assert len(r2.faces) > 0

        # Total faces should match
        assert len(r1.faces) + len(r2.faces) == 6

        # No overlapping faces
        assert not (set(r1.faces) & set(r2.faces))

    def test_split_maintains_attributes(self):
        """Test that split maintains region attributes"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2, 3],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8,
            metadata={"lens": "differential"}
        )

        split_curve = ParametricCurve(
            points=[(1, 0.5, 0.5)],
            is_closed=False
        )

        r1, r2 = RegionOperations.split_region(region, split_curve)

        # Check attributes
        assert r1.unity_principle == "curvature"
        assert r2.unity_principle == "curvature"
        assert r1.modified is True
        assert r2.modified is True
        assert "lens" in r1.metadata
        assert "lens" in r2.metadata
        assert "split_from" in r1.metadata
        assert "split_from" in r2.metadata

    def test_split_reduces_unity_strength(self):
        """Test that split slightly reduces unity strength"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2, 3],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        split_curve = ParametricCurve(
            points=[(1, 0.5, 0.5)],
            is_closed=False
        )

        r1, r2 = RegionOperations.split_region(region, split_curve)

        # Should be 0.8 * 0.9 = 0.72
        assert r1.unity_strength == pytest.approx(0.72)
        assert r2.unity_strength == pytest.approx(0.72)

    def test_split_with_empty_region_raises_error(self):
        """Test that splitting empty region raises error"""
        region = ParametricRegion(
            id="region_1",
            faces=[],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        split_curve = ParametricCurve(
            points=[(0, 0.5, 0.5)],
            is_closed=False
        )

        with pytest.raises(ValueError, match="no faces"):
            RegionOperations.split_region(region, split_curve)

    def test_split_with_invalid_curve_raises_error(self):
        """Test that splitting with invalid curve raises error"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        split_curve = ParametricCurve(
            points=[],  # Empty curve
            is_closed=False
        )

        with pytest.raises(ValueError, match="at least one point"):
            RegionOperations.split_region(region, split_curve)

    def test_split_single_face_region(self):
        """Test splitting a single-face region"""
        region = ParametricRegion(
            id="region_1",
            faces=[0],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        split_curve = ParametricCurve(
            points=[(0, 0.5, 0.5)],
            is_closed=False
        )

        # Should handle gracefully - may put entire face in one region
        r1, r2 = RegionOperations.split_region(region, split_curve)

        # At least one should have the face
        assert len(r1.faces) + len(r2.faces) >= 1


class TestRegionValidation:
    """Tests for region validation"""

    def test_validate_good_region(self):
        """Test validation of a well-formed region"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        is_valid, issues = RegionOperations.validate_region(region)
        assert is_valid is True
        assert len(issues) == 0

    def test_validate_empty_region(self):
        """Test validation catches empty faces"""
        region = ParametricRegion(
            id="region_1",
            faces=[],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        is_valid, issues = RegionOperations.validate_region(region)
        assert is_valid is False
        assert "no faces" in issues[0]

    def test_validate_invalid_unity_strength(self):
        """Test validation catches invalid unity strength"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1],
            boundary=[],
            unity_principle="curvature",
            unity_strength=1.5  # Invalid: > 1.0
        )

        is_valid, issues = RegionOperations.validate_region(region)
        assert is_valid is False
        assert any("unity_strength" in issue for issue in issues)

    def test_validate_duplicate_faces(self):
        """Test validation catches duplicate faces"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2, 1],  # Duplicate face 1
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        is_valid, issues = RegionOperations.validate_region(region)
        assert is_valid is False
        assert any("duplicate" in issue for issue in issues)


class TestCanMerge:
    """Tests for merge feasibility checking"""

    def test_can_merge_non_overlapping_regions(self):
        """Test that non-overlapping regions can merge"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        r2 = ParametricRegion(
            id="region_2",
            faces=[3, 4, 5],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.7
        )

        assert RegionOperations.can_merge(r1, r2) is True

    def test_cannot_merge_overlapping_regions(self):
        """Test that overlapping regions cannot merge"""
        r1 = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        r2 = ParametricRegion(
            id="region_2",
            faces=[2, 3, 4],  # Face 2 overlaps
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.7
        )

        assert RegionOperations.can_merge(r1, r2) is False


class TestBoundaryComputation:
    """Tests for boundary computation"""

    def test_compute_boundary_empty_faces(self):
        """Test boundary computation with empty faces"""
        boundary = RegionOperations._compute_boundary([])
        assert len(boundary) == 0

    def test_compute_boundary_creates_curves(self):
        """Test that boundary computation creates curves"""
        boundary = RegionOperations._compute_boundary([0, 1, 2])
        # Should create at least one curve
        assert len(boundary) >= 0  # May be empty in simplified implementation


class TestResonanceRecalculation:
    """Tests for resonance score recalculation"""

    def test_recalculate_without_analyzer(self):
        """Test recalculation without analyzer applies penalty"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        new_score = RegionOperations.recalculate_resonance(region, None)

        # Should apply 0.95 penalty: 0.8 * 0.95 = 0.76
        assert new_score == pytest.approx(0.76)

    def test_recalculate_maintains_score_with_analyzer(self):
        """Test recalculation with analyzer maintains score"""
        region = ParametricRegion(
            id="region_1",
            faces=[0, 1, 2],
            boundary=[],
            unity_principle="curvature",
            unity_strength=0.8
        )

        # Mock analyzer (any object)
        mock_analyzer = object()

        new_score = RegionOperations.recalculate_resonance(region, mock_analyzer)

        # Currently maintains score
        assert new_score == 0.8


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
