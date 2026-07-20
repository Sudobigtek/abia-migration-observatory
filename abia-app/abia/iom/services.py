import requests
from django.conf import settings
from .models import IOMDataExchange, IOMConfiguration

class IOMService:
    @staticmethod
    def get_config():
        config = IOMConfiguration.objects.filter(is_active=True).first()
        if not config:
            return None
        return config

    @staticmethod
    def _headers(config):
        return {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "X-Source-System": "abia-migration-observatory",
            "X-Partner-Code": "ABIA-NCFRMI-001",
        }

    @staticmethod
    def send_migrant_to_iom(migrant, config=None):
        if not config:
            config = IOMService.get_config()
        if not config:
            return None
        payload = {
            "full_name": migrant.full_name,
            "date_of_birth": str(getattr(migrant, "date_of_birth", None)) if getattr(migrant, "date_of_birth", None) else None,
            "gender": getattr(migrant, "gender", None),
            "nationality": getattr(migrant, "nationality", "Nigeria"),
            "phone": migrant.phone,
            "email": getattr(migrant, "email", None),
            "current_location": {
                "lga": str(migrant.current_lga) if getattr(migrant, "current_lga", None) else None,
                "state": "Abia",
                "country": "Nigeria"
            },
            "status": migrant.status,
            "vulnerabilities": getattr(migrant, "vulnerabilities", []),
            "data_source": "abia_observatory",
            "external_id": str(migrant.id)
        }
        exchange = IOMDataExchange.objects.create(
            direction="outbound",
            entity_type="migrant",
            entity_id=str(migrant.id),
            payload=payload
        )
        try:
            response = requests.post(
                f"{config.api_base_url}/migrants/",
                json=payload,
                headers=IOMService._headers(config),
                timeout=60
            )
            exchange.response_data = {"status_code": response.status_code, "body": response.text[:500]}
            if response.status_code in [200, 201]:
                data = response.json()
                exchange.iom_reference = data.get("id", "")
                exchange.status = "completed"
            else:
                exchange.status = "failed"
                exchange.error_message = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            exchange.status = "failed"
            exchange.error_message = str(e)[:500]
        exchange.save()
        return exchange

    @staticmethod
    def send_case_to_iom(case, config=None):
        if not config:
            config = IOMService.get_config()
        if not config:
            return None
        payload = {
            "case_type": case.case_type,
            "description": case.description,
            "status": case.status,
            "priority": getattr(case, "priority", "medium"),
            "location": {
                "lga": str(case.current_lga) if getattr(case, "current_lga", None) else None,
                "state": "Abia"
            },
            "data_source": "abia_observatory",
            "external_id": str(case.id)
        }
        exchange = IOMDataExchange.objects.create(
            direction="outbound",
            entity_type="case",
            entity_id=str(case.id),
            payload=payload
        )
        try:
            response = requests.post(
                f"{config.api_base_url}/cases/",
                json=payload,
                headers=IOMService._headers(config),
                timeout=60
            )
            exchange.response_data = {"status_code": response.status_code, "body": response.text[:500]}
            if response.status_code in [200, 201]:
                exchange.status = "completed"
            else:
                exchange.status = "failed"
                exchange.error_message = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            exchange.status = "failed"
            exchange.error_message = str(e)[:500]
        exchange.save()
        return exchange

    @staticmethod
    def sync_all_to_iom(entity_type="migrant"):
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        config = IOMService.get_config()
        if not config:
            return {"error": "IOM not configured"}
        results = {"sent": 0, "failed": 0}
        if entity_type == "migrant":
            for m in Migrant.objects.all():
                ex = IOMService.send_migrant_to_iom(m, config)
                if ex.status == "completed":
                    results["sent"] += 1
                else:
                    results["failed"] += 1
        elif entity_type == "case":
            for c in Case.objects.all():
                ex = IOMService.send_case_to_iom(c, config)
                if ex.status == "completed":
                    results["sent"] += 1
                else:
                    results["failed"] += 1
        config.last_sync_at = __import__("django.utils.timezone").now()
        config.save()
        return results