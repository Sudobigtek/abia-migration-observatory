"""Tests for IPFS publication layer."""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from abia.common.ipfs_client import IPFSClient
from abia.ipfs.publish import DatasetPublisher


class TestIPFSClient:
    """Test IPFS Kubo client."""

    @patch("abia.common.ipfs_client.IPFSClient._request")
    def test_add_file_returns_cid(self, mock_request):
        """Given file bytes, return CID."""
        mock_request.return_value = {"Hash": "QmTest123", "Size": "1024"}

        cid = IPFSClient.add_file(b"test data", "test.txt")

        assert cid == "QmTest123"

    @patch("abia.common.ipfs_client.IPFSClient._request")
    def test_add_json_returns_cid(self, mock_request):
        """Given dict, serialize and return CID."""
        mock_request.return_value = {"Hash": "QmJson456"}

        cid = IPFSClient.add_json({"key": "value"})

        assert cid == "QmJson456"

    @patch("abia.common.ipfs_client.IPFSClient._request")
    def test_pin_cid_success(self, mock_request):
        """Given CID, pin and return True."""
        mock_request.return_value = {"Pins": ["QmTest123"]}

        result = IPFSClient.pin_cid("QmTest123")

        assert result is True

    @patch("abia.common.ipfs_client.IPFSClient._request")
    def test_list_pins(self, mock_request):
        """Given pins, return CID list."""
        mock_request.return_value = {"Keys": {"QmA": {}, "QmB": {}}}

        pins = IPFSClient.list_pins()

        assert "QmA" in pins
        assert "QmB" in pins


class TestDatasetPublisher:
    """Test dataset publication workflow."""

    @patch("abia.ipfs.publish.IPFSClient.add_json")
    @patch("abia.ipfs.publish.IPFSClient.pin_cid")
    def test_publish_dataset(self, mock_pin, mock_add):
        """Given dataset, publish and register CID."""
        mock_add.return_value = "QmDataset789"

        data = {
            "schema_version": "1.0",
            "record_count": 150,
            "records": [{"id": "1", "name": "Test"}],
        }

        record = DatasetPublisher.publish_dataset("test-dataset", data)

        assert record["cid"] == "QmDataset789"
        assert record["record_count"] == 150
        assert record["checksum_sha256"] is not None

    def test_compute_sha256(self):
        """Given bytes, compute correct SHA-256."""
        data = b"hello world"
        checksum = DatasetPublisher.compute_sha256(data)
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        assert checksum == expected

    @patch("abia.ipfs.publish.IPFSClient.get_cid_content")
    def test_verify_dataset_success(self, mock_get):
        """Given matching checksum, return True."""
        data = b"test content"
        checksum = DatasetPublisher.compute_sha256(data)
        mock_get.return_value = data

        result = DatasetPublisher.verify_dataset("QmX", checksum)

        assert result is True

    @patch("abia.ipfs.publish.IPFSClient.get_cid_content")
    def test_verify_dataset_failure(self, mock_get):
        """Given mismatched checksum, return False."""
        mock_get.return_value = b"wrong content"

        result = DatasetPublisher.verify_dataset("QmX", "bad_checksum")

        assert result is False
