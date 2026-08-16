"""Outgoing webhook delivery with optional HMAC signing and audit-friendly results."""

import asyncio
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings


@dataclass
class WebhookDeliveryResult:
    status: str  # "success" | "failed" | "error"
    http_status: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    duration_ms: float


def _sign_payload(secret: str, payload: bytes) -> str:
    """Computes an HMAC-SHA256 signature over the serialized payload."""
    signature = hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


async def _send_request(
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
    timeout: float,
) -> httpx.Response:
    """Performs the actual HTTP POST. Isolated for testability (monkeypatch target)."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.post(url, json=payload, headers=headers)


async def dispatch_webhook(
    url: str,
    payload: Dict[str, Any],
    *,
    secret: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    retries: Optional[int] = None,
) -> WebhookDeliveryResult:
    """Delivers a webhook payload with retries, returning structured audit information."""
    timeout = timeout or settings.WEBHOOK_TIMEOUT_SECONDS
    retries = retries if retries is not None else settings.WEBHOOK_MAX_RETRIES

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update({k: str(v) for k, v in extra_headers.items()})

    body = json.dumps(payload, ensure_ascii=False, default=str)
    if secret:
        headers["X-Webhook-Signature"] = _sign_payload(secret, body.encode("utf-8"))

    start = time.perf_counter()
    last_error: Optional[str] = None
    last_response: Optional[httpx.Response] = None

    for attempt in range(max(1, retries + 1)):
        try:
            last_response = await _send_request(url, payload, headers, timeout)
            if 200 <= last_response.status_code < 300:
                duration_ms = (time.perf_counter() - start) * 1000
                text = last_response.text[:500]
                return WebhookDeliveryResult(
                    status="success",
                    http_status=last_response.status_code,
                    response_body=text,
                    error_message=None,
                    duration_ms=round(duration_ms, 2),
                )
            last_error = (
                f"HTTP {last_response.status_code} no exitoso: {last_response.text[:200]}"
            )
        except httpx.TimeoutException:
            last_error = "Timeout al contactar el endpoint del webhook."
        except httpx.HTTPError as exc:
            last_error = f"Error HTTP: {str(exc)[:200]}"
        except Exception as exc:
            last_error = f"Error inesperado: {str(exc)[:200]}"

        if attempt < retries:
            await asyncio.sleep(settings.WEBHOOK_RETRY_DELAY_SECONDS)

    duration_ms = (time.perf_counter() - start) * 1000
    return WebhookDeliveryResult(
        status="error" if last_response is None else "failed",
        http_status=last_response.status_code if last_response is not None else None,
        response_body=last_response.text[:500] if last_response is not None else None,
        error_message=last_error,
        duration_ms=round(duration_ms, 2),
    )