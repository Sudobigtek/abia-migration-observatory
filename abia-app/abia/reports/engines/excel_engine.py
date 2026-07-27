"""Excel report engine using openpyxl."""
from typing import Dict, Any, List
from openpyxl import Workbook
from io import BytesIO


class ExcelEngine:
    """Generate .xlsx reports from tabular data."""

    @staticmethod
    def generate(data: List[Dict[str, Any]], sheet_title: str = "Report") -> bytes:
        """Create Excel workbook from list of dict rows."""
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_title

        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append([row.get(h) for h in headers])

        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
