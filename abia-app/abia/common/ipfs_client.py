"""IPFS Kubo HTTP client.

Per Architecture Contract §2.5 and §17:
- File Storage: IPFS (Kubo) 0.29
- Data Integrity: Cryptographic CIDs (SHA-256)

No external dependency — uses urllib (built-in).
Kubo container must be running at IPFS_URL.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

logger = logging.getLogger("abia.ipfs")

IPFS_BASE_URL = "http://ipfs:5001"


class IPFSClient:
    """HTTP client for Kubo RPC API."""

    @staticmethod
    def _request(
        path: str,
        data: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """Make HTTP request to Kubo and parse JSON."""
        url = f"{IPFS_BASE_URL}{path}"
        req = urllib.request.Request(
            url, data=data, headers=headers or {}, method=method
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            logger.error("IPFS HTTP %s: %s", exc.code, exc.read().decode())
            raise
        except urllib.error.URLError as exc:
            logger.error("IPFS unreachable: %s", exc.reason)
            raise

    @staticmethod
    def add_file(content: bytes, filename: str = "") -> str:
        """Add file to IPFS and return CID.

        Args:
            content: File bytes.
            filename: Optional filename hint.

        Returns:
            str: The IPFS CID (Content Identifier).
        """
        boundary = "----IPFSBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename or "data"}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + content + f"\r\n--{boundary}--\r\n".encode()

        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        result = IPFSClient._request("/api/v0/add", data=body, headers=headers)
        cid = result.get("Hash", "")
        logger.info("Added file to IPFS: CID %s", cid)
        return cid

    @staticmethod
    def add_json(data: dict, filename: str = "data.json") -> str:
        """Add JSON object to IPFS and return CID."""
        return IPFSClient.add_file(json.dumps(data, indent=2).encode(), filename)

    @staticmethod
    def pin_cid(cid: str) -> bool:
        """Pin a CID to ensure persistence."""
        try:
            IPFSClient._request(f"/api/v0/pin/add?arg={cid}", method="POST")
            logger.info("Pinned CID %s", cid)
            return True
        except Exception as exc:
            logger.error("Failed to pin CID %s: %s", cid, exc)
            return False

    @staticmethod
    def get_cid_content(cid: str) -> bytes:
        """Retrieve content by CID from local node."""
        try:
            req = urllib.request.Request(
                f"{IPFS_BASE_URL}/api/v0/cat?arg={cid}", method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as exc:
            logger.error("Failed to retrieve CID %s: %s", cid, exc)
            raise

    @staticmethod
    def list_pins() -> List[str]:
        """List all pinned CIDs."""
        try:
            result = IPFSClient._request("/api/v0/pin/ls?type=recursive", method="POST")
            keys = result.get("Keys", {})
            return list(keys.keys())
        except Exception as exc:
            logger.warning("Failed to list pins: %s", exc)
            return []
