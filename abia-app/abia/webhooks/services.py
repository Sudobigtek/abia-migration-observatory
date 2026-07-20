import hashlib
import hmac
import json
import requests
from django.conf import settings
from .models import WebhookEndpoint, WebhookDelivery

class WebhookService:
    @staticmethod
    def sign_payload(payload, secret):
        if not secret:
            return None
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

    @staticmethod
    def deliver(webhook, event_type, payload):
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event_type=event_type,
            payload=payload
        )
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event_type,
            "X-Webhook-ID": str(delivery.id),
            **webhook.headers
        }
        signature = WebhookService.sign_payload(payload, webhook.secret)
        if signature:
            headers["X-Webhook-Signature"] = signature
        try:
            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=webhook.timeout_seconds
            )
            delivery.response_status = response.status_code
            delivery.response_body = response.text[:1000]
            delivery.attempt_count += 1
            if response.status_code in [200, 201, 202, 204]:
                delivery.status = "delivered"
                delivery.delivered_at = delivery.created_at
            else:
                delivery.status = "failed"
                delivery.error_message = f"HTTP {response.status_code}"
        except requests.RequestException as e:
            delivery.status = "failed"
            delivery.error_message = str(e)[:500]
            delivery.attempt_count += 1
        delivery.save()
        return delivery

    @staticmethod
    def trigger_event(event_type, payload):
        webhooks = WebhookEndpoint.objects.filter(is_active=True)
        if event_type != "all":
            webhooks = webhooks.filter(event_type__in=[event_type, "all"])
        results = []
        for webhook in webhooks:
            delivery = WebhookService.deliver(webhook, event_type, payload)
            results.append({
                "webhook": webhook.name,
                "status": delivery.status,
                "delivery_id": str(delivery.id)
            })
        return results

    @staticmethod
    def retry_failed(webhook_id=None, max_attempts=3):
        qs = WebhookDelivery.objects.filter(status="failed", attempt_count__lt=max_attempts)
        if webhook_id:
            qs = qs.filter(webhook_id=webhook_id)
        retried = 0
        for delivery in qs:
            WebhookService.deliver(delivery.webhook, delivery.event_type, delivery.payload)
            retried += 1
        return retried