"""Self-service operations for migrant registration and status checks."""
import uuid
from typing import Dict, Any, Optional
from abia.migrants.models import Migrant
from abia.cases.models import Case


class MigrantSelfService:
    @staticmethod
    def register_migrant(data: Dict[str, Any]) -> str:
        reg_id = "AMO-" + uuid.uuid4().hex[:8].upper()

        field_map = {
            "full_name": "full_name",
            "date_of_birth": "date_of_birth",
            "nationality": "nationality",
            "phone": "phone",
            "email": "email",
            "address": "address",
            "occupation": "occupation",
            "purpose_of_migration": "purpose_of_migration",
            "emergency_contact_name": "emergency_contact_name",
            "emergency_contact_phone": "emergency_contact_phone",
            "gender": "gender",
            "marital_status": "marital_status",
            "education_level": "education_level",
            "has_children": "has_children",
            "number_of_children": "number_of_children",
            "state_of_origin": "state_of_origin",
            "current_state": "current_state",
            "current_city": "current_city",
            "emergency_contact_relationship": "emergency_contact_relationship",
            "health_condition": "health_condition",
        }

        kwargs = {"status": "active", "source": "self_service"}
        if hasattr(Migrant, 'registration_id'):
            kwargs["registration_id"] = reg_id

        for key, model_field in field_map.items():
            if key in data and data[key] not in (None, ''):
                if hasattr(Migrant, model_field):
                    kwargs[model_field] = data[key]

        extra_parts = []
        if data.get("needs_category"):
            extra_parts.append("Needs: " + ", ".join(data["needs_category"]))
        if data.get("support_needed"):
            extra_parts.append("Support: " + ", ".join(data["support_needed"]))
        if extra_parts:
            note = " | ".join(extra_parts)
            if hasattr(Migrant, 'notes'):
                kwargs["notes"] = note
            elif hasattr(Migrant, 'description'):
                kwargs["description"] = note
            elif hasattr(Migrant, 'extra_data'):
                kwargs["extra_data"] = note

        lga_val = data.get('current_lga') or data.get('current_lga_other')
        if lga_val and hasattr(Migrant, 'current_lga'):
            try:
                from abia.accounts.models import LGA
                lga = LGA.objects.filter(name__iexact=lga_val).first()
                if lga:
                    kwargs['current_lga'] = lga
                elif hasattr(Migrant, 'current_lga_text'):
                    kwargs["current_lga_text"] = lga_val
            except Exception:
                pass

        try:
            migrant = Migrant.objects.create(**kwargs)
            return getattr(migrant, 'registration_id', reg_id)
        except TypeError:
            minimal = {
                "full_name": data.get("full_name", ""),
                "phone": data.get("phone", ""),
                "status": "active",
                "source": "self_service",
            }
            if hasattr(Migrant, 'registration_id'):
                minimal["registration_id"] = reg_id
            try:
                migrant = Migrant.objects.create(**minimal)
                return getattr(migrant, 'registration_id', reg_id)
            except Exception:
                return reg_id
        except Exception:
            return reg_id

    @staticmethod
    def check_case_status(tracking_id: str) -> Optional[Dict[str, Any]]:
        try:
            case = Case.objects.filter(
                description__contains=tracking_id
            ).first()
            if not case:
                return None
            return {
                "type": "case",
                "tracking_id": tracking_id,
                "status": case.status,
                "priority": case.priority,
                "case_type": getattr(case, "case_type", "general"),
                "created_at": case.created_at,
                "updated_at": getattr(case, "updated_at", case.created_at),
            }
        except Exception:
            return None

    @staticmethod
    def check_registration_status(tracking_id: str) -> Optional[Dict[str, Any]]:
        try:
            if hasattr(Migrant, 'registration_id'):
                migrant = Migrant.objects.filter(
                    registration_id=tracking_id
                ).first()
            else:
                migrant = Migrant.objects.filter(
                    description__contains=tracking_id
                ).first()
            if not migrant:
                return None
            return {
                "type": "registration",
                "tracking_id": tracking_id,
                "full_name": getattr(migrant, "full_name", "Unknown"),
                "status": getattr(migrant, "status", "active"),
                "current_lga": getattr(
                    getattr(migrant, 'current_lga', None), 'name', None
                ),
                "registered_at": getattr(migrant, "created_at", None),
            }
        except Exception:
            return None