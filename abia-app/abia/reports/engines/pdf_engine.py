"""PDF report engine using WeasyPrint / ReportLab."""
from typing import Dict, Any
from django.template.loader import render_to_string


class PDFEngine:
    """Generate PDF reports from templates and context data."""

    @staticmethod
    def generate(template_name: str, context: Dict[str, Any]) -> bytes:
        """Render HTML template and convert to PDF bytes."""
        html_string = render_to_string(template_name, context)
        # TODO: Integrate WeasyPrint or ReportLab
        return html_string.encode("utf-8")
