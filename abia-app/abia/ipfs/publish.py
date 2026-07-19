"""Dataset publication workflow for IPFS.

Per Architecture Contract §17:
Dataset finalized → Export → Add to IPFS → Receive CID → Register → Publish.
"""

import hashlib
import json
import logging
import os
from datetime import datetime

from abia.common.ipfs_client import IPFSClient

logger = logging.getLogger("abia.ipfs.publish")

CID_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "cids.json")


class DatasetPublisher:
    """Publish quarterly/annual datasets to IPFS."""

    @staticmethod
    def export_migrants_to_json(queryset) -> dict:
        """Serialize migrant queryset to structured dict."""
        records = []
        for m in queryset:
            records.append({
                "id": str(m.id),
                "full_name": m.full_name,
                "gender": m.gender,
                "current_lga": m.current_lga.name if m.current_lga else None,
                "odk_submission_id": m.odk_submission_id,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })
        return {
            "schema_version": "1.0",
            "record_count": len(records),
            "exported_at": datetime.utcnow().isoformat(),
            "records": records,
        }

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        """Compute SHA-256 checksum for integrity verification."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def publish_dataset(name: str, data: dict) -> dict:
        """Publish dataset to IPFS and register CID.

        Args:
            name: Dataset name (e.g., "abia-migrants-q3-2026").
            data: Dataset dict.

        Returns:
            dict: Publication record with CID and checksum.
        """
        json_bytes = json.dumps(data, indent=2).encode()
        checksum = DatasetPublisher.compute_sha256(json_bytes)

        cid = IPFSClient.add_json(data, filename=f"{name}.json")
        IPFSClient.pin_cid(cid)

        record = {
            "name": name,
            "cid": cid,
            "date_published": datetime.utcnow().strftime("%Y-%m-%d"),
            "record_count": data.get("record_count", 0),
            "checksum_sha256": checksum,
            "description": data.get("description", f"Dataset {name}"),
        }

        DatasetPublisher._register_cid(record)
        logger.info("Published dataset %s with CID %s", name, cid)
        return record

    @staticmethod
    def _register_cid(record: dict):
        """Append CID to local registry."""
        registry = {"datasets": []}
        if os.path.exists(CID_REGISTRY_PATH):
            try:
                with open(CID_REGISTRY_PATH, "r") as f:
                    registry = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Corrupted CID registry, starting fresh")

        registry["datasets"].append(record)

        with open(CID_REGISTRY_PATH, "w") as f:
            json.dump(registry, f, indent=2)

    @staticmethod
    def get_registry() -> dict:
        """Load CID registry."""
        if not os.path.exists(CID_REGISTRY_PATH):
            return {"datasets": []}
        with open(CID_REGISTRY_PATH, "r") as f:
            return json.load(f)

    @staticmethod
    def verify_dataset(cid: str, expected_checksum: str) -> bool:
        """Download dataset by CID and verify SHA-256."""
        try:
            content = IPFSClient.get_cid_content(cid)
            actual = hashlib.sha256(content).hexdigest()
            return actual == expected_checksum
        except Exception as exc:
            logger.error("Verification failed for CID %s: %s", cid, exc)
            return False
