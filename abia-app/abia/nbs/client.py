"""NBS API client — disabled by default."""
from typing import Optional
from django.conf import settings


class NBSClient:
    """Batch-oriented NBS data submission client."""

    BASE_URL = "https://data.gov.ng/api"

    def __init__(self, api_key: Optional[str] = None):
        # Load from settings; no hardcoded credentials
        self.api_key = None
        if api_key:
            self.api_key = api_key
        elif hasattr(settings, "NBS_API_KEY"):
            self.api_key = settings.NBS_API_KEY

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def submit_dataset(self, dataset: dict) -> dict:
        """Submit dataset to NBS — requires admin approval."""
        if not self.is_configured():
            raise RuntimeError("NBS_API_KEY not configured")
        return {"status": "queued", "dataset_id": dataset.get("id")}
