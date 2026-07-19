import os
import requests
from django.conf import settings
from .models import NCFRMISyncLog

class NCFRMIService:
    BASE_URL = getattr(settings, "NCFRMI_API_URL", "https://api.ncfrmi.gov.ng/v1")
    API_KEY = getattr(settings, "NCFRMI_API_KEY", "")

    @classmethod
    def _headers(cls):
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json",
            "X-Source-System": "abia-migration-observatory"
        }

    @classmethod
    def sync_migrant(cls, migrant, user=None):
        payload = {
            "full_name": migrant.full_name,
            "phone": migrant.phone,
            "email": getattr(migrant, "email", None),
            "date_of_birth": str(migrant.date_of_birth) if getattr(migrant, "date_of_birth", None) else None,
            "gender": getattr(migrant, "gender", None),
            "lga_of_origin": str(migrant.lga_of_origin) if getattr(migrant, "lga_of_origin", None) else None,
            "current_lga": str(migrant.current_lga) if getattr(migrant, "current_lga", None) else None,
            "status": migrant.status,
            "data_source": "abia_observatory",
            "external_id": str(migrant.id)
        }
        log = NCFRMISyncLog.objects.create(
            migrant=migrant,
            sync_payload=payload,
            synced_by=user
        )
        try:
            response = requests.post(
                f"{cls.BASE_URL}/migrants/",
                json=payload,
                headers=cls._headers(),
                timeout=30
            )
            log.response_data = {"status_code": response.status_code, "body": response.text[:1000]}
            if response.status_code in [200, 201]:
                data = response.json()
                log.ncfrmi_record_id = data.get("id", "")
                log.status = "synced"
            else:
                log.status = "failed"
                log.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
        except requests.RequestException as e:
            log.status = "failed"
            log.error_message = str(e)[:500]
        log.save()
        return log

    @classmethod
    def bulk_sync(cls, migrants, user=None):
        results = {"synced": 0, "failed": 0, "logs": []}
        for migrant in migrants:
            log = cls.sync_migrant(migrant, user)
            if log.status == "synced":
                results["synced"] += 1
            else:
                results["failed"] += 1
            results["logs"].append(str(log.id))
        return results