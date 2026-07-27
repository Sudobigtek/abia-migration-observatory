"""Interactive dashboard export engine using Plotly."""
from typing import Dict, Any
import plotly.graph_objects as go
from plotly.offline import plot


class DashboardEngine:
    """Generate interactive HTML dashboard exports."""

    @staticmethod
    def generate(figures: list, title: str = "Dashboard") -> str:
        """Combine Plotly figures into a single HTML page."""
        html_parts = [f"<h1>{title}</h1>"]
        for fig in figures:
            html_parts.append(plot(fig, output_type="div", include_plotlyjs="cdn"))
        return "\n".join(html_parts)
