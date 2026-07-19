from celery import shared_task
import requests
import hmac
import hashlib
import json
from .models import WebhookEndpoint, WebhookDelivery

@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id):
    try:
        delivery = WebhookDelivery.objects.select_related('endpoint').get(id=delivery_id)
        endpoint = delivery.endpoint
        
        if not endpoint.is_active:
            delivery.status = 'failed'
            delivery.error_message = 'Endpoint deactivated'
            delivery.save()
            return {'status': 'failed', 'reason': 'inactive'}

        payload = json.dumps(delivery.payload, separators=(',', ':'))
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Event': delivery.event_type,
            'X-Webhook-ID': str(delivery.id),
        }
        
        if endpoint.secret:
            signature = hmac.new(
                endpoint.secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = f'sha256={signature}'

        delivery.attempts += 1
        delivery.save()

        response = requests.post(
            endpoint.url,
            data=payload,
            headers=headers,
            timeout=30
        )
        
        delivery.response_status = response.status_code
        delivery.response_body = response.text[:1000]
        
        if response.status_code in [200, 201, 202, 204]:
            delivery.status = 'success'
            delivery.delivered_at = __import__('django.utils.timezone').utils.timezone.now()
        else:
            delivery.status = 'failed'
            delivery.error_message = f'HTTP {response.status_code}'
            raise self.retry(countdown=60 * (2 ** self.request.retries))
            
        delivery.save()
        return {'status': delivery.status, 'response_status': response.status_code}
        
    except requests.exceptions.RequestException as exc:
        delivery.status = 'retrying' if self.request.retries < 3 else 'failed'
        delivery.error_message = str(exc)[:500]
        delivery.save()
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
    except Exception as exc:
        delivery.status = 'failed'
        delivery.error_message = str(exc)[:500]
        delivery.save()
        return {'status': 'failed', 'error': str(exc)}

@shared_task
def trigger_webhook_event(event_type, payload):
    """Trigger webhooks for a specific event type."""
    endpoints = WebhookEndpoint.objects.filter(is_active=True, events__contains=event_type)
    for endpoint in endpoints:
        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            event_type=event_type,
            payload=payload
        )
        deliver_webhook.delay(str(delivery.id))
