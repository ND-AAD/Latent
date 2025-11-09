"""
UI Components for Ceramic Mold Analyzer

This module contains all UI widgets and panels for the desktop application.
"""

from app.ui.analysis_panel import AnalysisPanel, CurvatureHistogramWidget
from app.ui.iteration_timeline import IterationTimeline, IterationListItem

__all__ = [
    'AnalysisPanel',
    'CurvatureHistogramWidget',
    'IterationTimeline',
    'IterationListItem',
]
