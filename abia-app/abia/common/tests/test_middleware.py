import json
import pytest
from unittest.mock import MagicMock
from django.http import JsonResponse
from abia.common.response_envelope import EnvelopedResponseMiddleware


class TestEnvelopedResponseMiddleware:
    def test_envelopes_json_response(self):
        mw = EnvelopedResponseMiddleware(lambda req: JsonResponse({"foo": "bar"}))
        request = MagicMock()
        request.path = "/api/v1/migrants/"
        response = mw(request)
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert data["data"] == {"foo": "bar"}
        assert "meta" in data

    def test_skips_non_json(self):
        mw = EnvelopedResponseMiddleware(lambda req: MagicMock(
            status_code=200,
            content=b"plain text",
            __getitem__=lambda s, k: "text/plain",
        ))
        request = MagicMock()
        request.path = "/api/v1/migrants/"
        response = mw(request)
        assert response.content == b"plain text"

    def test_skips_schema_docs(self):
        mw = EnvelopedResponseMiddleware(lambda req: JsonResponse({"schema": "yes"}))
        request = MagicMock()
        request.path = "/api/schema/"
        response = mw(request)
        data = json.loads(response.content)
        assert "status" not in data
        assert data == {"schema": "yes"}

    def test_skips_error_responses(self):
        mw = EnvelopedResponseMiddleware(lambda req: JsonResponse({"error": "bad"}, status=400))
        request = MagicMock()
        request.path = "/api/v1/migrants/"
        response = mw(request)
        data = json.loads(response.content)
        assert "status" not in data
        assert data == {"error": "bad"}
