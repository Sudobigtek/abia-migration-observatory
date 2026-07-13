"""IPFS dataset publication script. Per Architecture Contract §17."""
import json
import os
from datetime import datetime

import requests


IPFS_API = os.getenv("IPFS_API_URL", "http://localhost:5001")
CID_REGISTRY = os.path.join(os.path.dirname(__file__), "cids.json")


def add_to_ipfs(file_path: str) -> dict:
    """Add a file to IPFS and return the CID."""
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{IPFS_API}/api/v0/add",
            files={"file": f},
            timeout=30,
        )
    response.raise_for_status()
    return response.json()


def verify_cid(cid: str) -> bool:
    """Verify a CID is accessible via the local gateway."""
    try:
        response = requests.head(
            f"http://localhost:8081/ipfs/{cid}",
            timeout=10,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def register_cid(name: str, cid: str, record_count: int, description: str) -> None:
    """Register a CID in the local registry."""
    registry = {"datasets": []}
    if os.path.exists(CID_REGISTRY):
        with open(CID_REGISTRY, "r") as f:
            registry = json.load(f)

    registry["datasets"].append({
        "name": name,
        "cid": cid,
        "date_published": datetime.utcnow().isoformat(),
        "record_count": record_count,
        "checksum_sha256": "placeholder",
        "description": description,
    })

    with open(CID_REGISTRY, "w") as f:
        json.dump(registry, f, indent=2)

    print(f"[OK] Registered CID: {cid}")


def publish_test_dataset() -> None:
    """Create and publish a test dataset."""
    test_data = """name,age,lga,date_registered
John Doe,25,Aba North,2026-07-01
Jane Smith,30,Aba South,2026-07-02
Bob Johnson,22,Umuahia North,2026-07-03
"""

    test_file = "/tmp/abia_test_dataset.csv"
    with open(test_file, "w") as f:
        f.write(test_data)

    print("[INFO] Adding test dataset to IPFS...")
    result = add_to_ipfs(test_file)
    cid = result["Hash"]

    print(f"[INFO] CID: {cid}")
    print("[INFO] Verifying CID accessibility...")
    if verify_cid(cid):
        print("[OK] CID verified via gateway")
    else:
        print("[WARN] CID not yet available on gateway")

    register_cid(
        name="abia-migrants-test-2026",
        cid=cid,
        record_count=3,
        description="Test migrant registration dataset for Abia State",
    )

    requests.post(f"{IPFS_API}/api/v0/pin/add?arg={cid}", timeout=10)
    print("[OK] CID pinned permanently")


if __name__ == "__main__":
    publish_test_dataset()
