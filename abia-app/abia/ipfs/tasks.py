from celery import shared_task
from .models import IPFSDocument, PinQueue


@shared_task(bind=True, max_retries=5)
def pin_document_to_ipfs(self, document_id):
    """Async IPFS pinning task."""
    try:
        doc = IPFSDocument.objects.get(id=document_id)
        queue = PinQueue.objects.get(document=doc)
        
        queue.status = 'processing'
        queue.attempts += 1
        queue.save()
        
        # Simulate IPFS upload delay
        import time
        time.sleep(2)
        
        # Placeholder CID generation
        doc.cid = f"QmAsync{doc.id.hex[:20]}"
        doc.ipfs_gateway_url = f"https://ipfs.io/ipfs/{doc.cid}"
        doc.pin_status = 'pinned'
        doc.save()
        
        queue.status = 'completed'
        import django.utils.timezone
        queue.completed_at = django.utils.timezone.now()
        queue.save()
        
        return {'document_id': str(document_id), 'cid': doc.cid, 'status': 'pinned'}
    except Exception as exc:
        queue = PinQueue.objects.filter(document_id=document_id).first()
        if queue:
            queue.status = 'failed'
            queue.last_error = str(exc)
            queue.save()
        raise self.retry(exc=exc, countdown=300)


@shared_task
def process_pin_queue():
    """Process all queued documents."""
    queued = PinQueue.objects.filter(status='queued')
    count = 0
    for queue in queued:
        pin_document_to_ipfs.delay(str(queue.document.id))
        count += 1
    return f"Queued {count} documents for pinning"


@shared_task
def cleanup_removed_documents():
    """Remove documents marked as removed from local storage."""
    removed = IPFSDocument.objects.filter(pin_status='removed').exclude(local_file='')
    count = 0
    for doc in removed:
        if doc.local_file:
            doc.local_file.delete(save=False)
            count += 1
    return f"Cleaned up {count} removed documents"
