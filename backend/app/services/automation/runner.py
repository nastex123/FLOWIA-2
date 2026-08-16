"""Automation orchestration: loads rules, evaluates them and dispatches webhook deliveries."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.infrastructure.database import async_session_factory
from app.infrastructure.models import (
    AutomationRule,
    WebhookConfig,
    WebhookDelivery,
    get_utc_now,
)
from app.services.rules.rule_engine import evaluate_field_rule, evaluate_records_rule
from app.services.webhooks.dispatcher import dispatch_webhook


def _rule_as_dict(rule: AutomationRule) -> Dict[str, Any]:
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "document_type": rule.document_type,
        "event": rule.event,
        "field": rule.field,
        "operator": rule.operator,
        "value": rule.value_json,
        "webhook_ids": rule.webhook_ids_json or [],
        "enabled": rule.enabled,
    }


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def load_active_rules(
    session: AsyncSession,
    *,
    organization_id: str,
    event: str,
    document_type: str,
) -> List[AutomationRule]:
    """Loads enabled rules for a tenant matching the event and document type."""
    stmt = select(AutomationRule).where(
        AutomationRule.organization_id == organization_id,
        AutomationRule.enabled.is_(True),
        AutomationRule.event == event,
    )
    result = await session.execute(stmt)
    rules = result.scalars().all()
    return [
        r for r in rules
        if not r.document_type or r.document_type == document_type
    ]


async def load_webhook_targets(
    session: AsyncSession,
    organization_id: str,
    webhook_ids: List[str],
) -> List[WebhookConfig]:
    """Resolves the webhook configs a rule should deliver to."""
    stmt = select(WebhookConfig).where(
        WebhookConfig.organization_id == organization_id,
        WebhookConfig.active.is_(True),
    )
    result = await session.execute(stmt)
    all_webhooks = result.scalars().all()

    if not webhook_ids:
        return list(all_webhooks)

    by_id = {w.id: w for w in all_webhooks}
    return [by_id[w_id] for w_id in webhook_ids if w_id in by_id]


async def _evaluate_rule(
    rule: AutomationRule,
    extraction_fields: Optional[Dict[str, Any]],
    normalized_records: Optional[List[Dict[str, Any]]],
) -> Tuple[bool, Optional[Any], int]:
    """Evaluates a rule against extraction fields and/or normalized records."""
    if normalized_records is not None:
        return evaluate_records_rule(_rule_as_dict(rule), normalized_records)

    from app.services.rules.rule_engine import extract_field_value

    field_value = extract_field_value(extraction_fields or {}, rule.field)
    matched = evaluate_field_rule(_rule_as_dict(rule), field_value)
    return matched, field_value, 1 if matched else 0


def build_payload(
    *,
    event: str,
    organization_id: str,
    document_id: str,
    filename: str,
    document_type: str,
    rule: Dict[str, Any],
    matched_value: Optional[Any],
    matched_rows: int,
    fields: Optional[Dict[str, Any]] = None,
    normalized_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Builds a structured webhook payload with rule context and extracted data."""
    flattened_fields: Dict[str, Any] = {}
    if fields:
        for key, entry in fields.items():
            if isinstance(entry, dict):
                flattened_fields[key] = entry.get("value")
            else:
                flattened_fields[key] = entry

    return {
        "event": event,
        "timestamp": _iso_now(),
        "organization_id": organization_id,
        "document": {
            "id": document_id,
            "filename": filename,
            "document_type": document_type,
        },
        "rule": {
            "id": rule["id"],
            "name": rule["name"],
            "field": rule["field"],
            "operator": rule["operator"],
            "value": rule.get("value"),
        },
        "matched_value": matched_value,
        "matched_rows": matched_rows,
        "fields": flattened_fields,
        "normalized": normalized_context,
    }


async def run_automation_rules(
    session: AsyncSession,
    *,
    event: str,
    document_id: str,
    organization_id: str,
    filename: str,
    document_type: str,
    fields: Optional[Dict[str, Any]] = None,
    normalized_context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Evaluates all matching rules and dispatches webhooks, persisting delivery audit rows."""
    rules = await load_active_rules(
        session,
        organization_id=organization_id,
        event=event,
        document_type=document_type,
    )
    if not rules:
        return []

    normalized_records = None
    if normalized_context:
        normalized_records = normalized_context.get("records")

    triggered: List[Dict[str, Any]] = []

    for rule in rules:
        matched, matched_value, matched_rows = await _evaluate_rule(
            rule,
            extraction_fields=fields if normalized_records is None else None,
            normalized_records=normalized_records,
        )
        if not matched:
            continue

        webhooks = await load_webhook_targets(
            session, organization_id, rule.webhook_ids_json or []
        )
        if not webhooks:
            continue

        payload = build_payload(
            event=event,
            organization_id=organization_id,
            document_id=document_id,
            filename=filename,
            document_type=document_type,
            rule=_rule_as_dict(rule),
            matched_value=matched_value,
            matched_rows=matched_rows,
            fields=fields,
            normalized_context=normalized_context,
        )

        for webhook in webhooks:
            result = await dispatch_webhook(
                webhook.url,
                payload,
                secret=webhook.secret,
                extra_headers=webhook.headers_json,
            )
            delivery = WebhookDelivery(
                organization_id=organization_id,
                webhook_id=webhook.id,
                rule_id=rule.id,
                document_id=document_id,
                event=event,
                url=webhook.url,
                status=result.status,
                http_status=result.http_status,
                response_body=result.response_body,
                error_message=result.error_message,
                duration_ms=result.duration_ms,
            )
            session.add(delivery)

            triggered.append(
                {
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "webhook_id": webhook.id,
                    "webhook_name": webhook.name,
                    "status": result.status,
                }
            )

        logger.info(
            "Rule '%s' triggered %d webhook(s) for document %s",
            rule.name,
            len(webhooks),
            document_id,
        )

    await session.commit()
    return triggered


async def run_automation_for_document(
    *,
    event: str,
    document_id: str,
    organization_id: str,
    filename: str,
    document_type: str,
    fields: Optional[Dict[str, Any]] = None,
    normalized_context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Convenience wrapper opening its own session (used from background tasks)."""
    async with async_session_factory() as session:
        try:
            return await run_automation_rules(
                session,
                event=event,
                document_id=document_id,
                organization_id=organization_id,
                filename=filename,
                document_type=document_type,
                fields=fields,
                normalized_context=normalized_context,
            )
        except Exception:
            logger.exception(
                "Automation pipeline failed for document %s (event=%s)",
                document_id,
                event,
            )
            await session.rollback()
            return []


async def evaluate_single_rule(
    session: AsyncSession,
    rule: AutomationRule,
    *,
    document_id: str,
    document_type: str,
    fields: Optional[Dict[str, Any]] = None,
    normalized_records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Evaluates a single rule against provided data (used by the manual evaluation endpoint)."""
    matched, matched_value, matched_rows = await _evaluate_rule(
        rule,
        extraction_fields=fields if normalized_records is None else None,
        normalized_records=normalized_records,
    )
    return {
        "rule_id": rule.id,
        "rule_name": rule.name,
        "matched": matched,
        "matched_value": matched_value,
        "matched_rows": matched_rows,
    }


async def dispatch_test_webhook(webhook: WebhookConfig) -> Dict[str, Any]:
    """Sends a lightweight test ping to a webhook endpoint."""
    test_payload = {
        "event": "webhook.test",
        "timestamp": _iso_now(),
        "organization_id": webhook.organization_id,
        "message": f"Test ping desde FlowMind AI para '{webhook.name}'",
    }
    result = await dispatch_webhook(
        webhook.url,
        test_payload,
        secret=webhook.secret,
        extra_headers=webhook.headers_json,
    )
    return {
        "webhook_id": webhook.id,
        "webhook_name": webhook.name,
        "status": result.status,
        "http_status": result.http_status,
        "error_message": result.error_message,
        "duration_ms": result.duration_ms,
    }