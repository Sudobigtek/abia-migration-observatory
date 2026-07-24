"""Custom domain exceptions for public dashboard."""
class PublicDashboardError(Exception):
    """Base exception for public dashboard domain."""
    pass
class FeedbackSubmissionError(PublicDashboardError):
    """Raised when feedback submission fails."""
    pass
class MapDataError(PublicDashboardError):
    """Raised when map data cannot be retrieved."""
    pass
