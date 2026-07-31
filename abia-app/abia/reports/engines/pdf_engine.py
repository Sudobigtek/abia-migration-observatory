import logging
from typing import Dict, Any
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)


class PDFEngine:
    """Generate PDF reports from Django templates using WeasyPrint."""

    @staticmethod
    def generate(template_name: str, context: Dict[str, Any]) -> bytes:
        """Render HTML template and convert to PDF bytes."""
        html_string = render_to_string(template_name, context)
        pdf_bytes = HTML(string=html_string).write_pdf()
        return pdf_bytes
