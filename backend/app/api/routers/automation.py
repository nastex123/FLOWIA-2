"""Business automation rules and outgoing webhooks management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import AuthContext, require_roles
from app.domain.automation_models import (
    AutomationRuleCreate,
    AutomationRuleResponse,
    AutomationRuleUpdate,
    RuleEvaluationRequest,
    RuleEvaluationResponse,
    WebhookConfigCreate,
    WebhookConfigResponse,
    WebhookConfigUpdate,
    WebhookDeliveryResponse,
    WebhookTestResponse,
)
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    AutomationRule,
    Document,
    UserRole,
    WebhookConfig,
    WebhookDelivery,
)
from app.services.automation.runner import (
    dispatch_test_webhook,
    evaluate_single_rule,
)

router = APIRouter(prefix="/api/v1", tags=["Automation & Webhooks"])


def _rule_to_response(r: AutomationRule) -> AutomationRuleResponse:
    return AutomationRuleResponse(
        id=r.id,
        organization_id=r.organization_id,
        name=r.name,
        description=r.description,
        document_type=r.document_type,
        event=r.event,
        field=r.field,
        operator=r.operator,
        value=r.value_json,
        webhook_ids=r.webhook_ids_json or [],
        enabled=r.enabled,
        created_at=r.created_at.isoformat(),
        updated_at=r.updated_at.isoformat(),
    )


def _webhook_to_response(w: WebhookConfig) -> WebhookConfigResponse:
    return WebhookConfigResponse(
        id=w.id,
        organization_id=w.organization_id,
        name=w.name,
        url=w.url,
        has_secret=bool(w.secret),
        headers=w.headers_json or {},
        active=w.active,
        created_at=w.created_at.isoformat(),
        updated_at=w.updated_at.isoformat(),
    )


def _delivery_to_response(d: WebhookDelivery) -> WebhookDeliveryResponse:
    return WebhookDeliveryResponse(
        id=d.id,
        organization_id=d.organization_id,
        webhook_id=d.webhook_id,
        rule_id=d.rule_id,
        document_id=d.document_id,
        event=d.event,
        url=d.url,
        status=d.status,
        http_status=d.http_status,
        error_message=d.error_message,
        duration_ms=d.duration_ms,
        created_at=d.created_at.isoformat(),
    )


# ==========================================
# Automation Rules
# ==========================================


@router.get(
    "/rules",
    response_model=List[AutomationRuleResponse],
)
async def list_rules(
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
):
    """Lists all automation rules for the organization."""
    result = await db.execute(
        select(AutomationRule)
        .where(AutomationRule.organization_id == auth.org_id)
        .order_by(AutomationRule.created_at.asc())
    )
    rules = result.scalars().all()
    return [_rule_to_response(r) for r in rules]


@router.post(
    "/rules",
    response_model=AutomationRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rule(
    payload: AutomationRuleCreate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Creates a business automation rule (Admin only)."""
    import uuid

    rule = AutomationRule(
        id=str(uuid.uuid4()),
        organization_id=auth.org_id,
        name=payload.name,
        description=payload.description,
        document_type=payload.document_type,
        event=payload.event.value,
        field=payload.field,
        operator=payload.operator.value,
        value_json=payload.value,
        webhook_ids_json=payload.webhook_ids,
        enabled=payload.enabled,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return _rule_to_response(rule)


@router.get(
    "/rules/{rule_id}",
    response_model=AutomationRuleResponse,
)
async def get_rule(
    rule_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a single automation rule."""
    rule = await _load_rule(db, rule_id, auth.org_id)
    return _rule_to_response(rule)


@router.put(
    "/rules/{rule_id}",
    response_model=AutomationRuleResponse,
)
async def update_rule(
    rule_id: str,
    payload: AutomationRuleUpdate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Updates an automation rule (Admin only)."""
    rule = await _load_rule(db, rule_id, auth.org_id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if key == "event" and value is not None:
            setattr(rule, key, value.value)
        elif key == "operator" and value is not None:
            setattr(rule, key, value.value)
        elif key == "webhook_ids" and value is not None:
            rule.webhook_ids_json = value
        elif key == "value":
            rule.value_json = value
        else:
            setattr(rule, key, value)
    await db.commit()
    await db.refresh(rule)
    return _rule_to_response(rule)


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_rule(
    rule_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Deletes an automation rule (Admin only)."""
    rule = await _load_rule(db, rule_id, auth.org_id)
    await db.delete(rule)
    await db.commit()
    return {"status": "deleted", "rule_id": rule_id}


@router.post(
    "/rules/{rule_id}/evaluate",
    response_model=RuleEvaluationResponse,
)
async def evaluate_rule_against_document(
    rule_id: str,
    payload: RuleEvaluationRequest,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Manually evaluates a rule against an extracted document (dry-run, no webhooks fired)."""
    rule = await _load_rule(db, rule_id, auth.org_id)

    stmt = (
        select(Document)
        .options(selectinload(Document.extraction_record))
        .where(
            Document.id == payload.document_id,
            Document.organization_id == auth.org_id,
        )
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc or not doc.extraction_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document or extraction record not found.",
        )

    if rule.event != "extraction_completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La evaluación manual solo soporta reglas de evento 'extraction_completed'.",
        )

    evaluation = await evaluate_single_rule(
        db,
        rule,
        document_id=doc.id,
        document_type=doc.extraction_record.document_type,
        fields=doc.extraction_record.fields_json,
    )
    return RuleEvaluationResponse(**evaluation)


# ==========================================
# Webhook Configurations
# ==========================================


@router.get(
    "/webhooks",
    response_model=List[WebhookConfigResponse],
)
async def list_webhooks(
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
):
    """Lists webhook configurations for the organization."""
    result = await db.execute(
        select(WebhookConfig)
        .where(WebhookConfig.organization_id == auth.org_id)
        .order_by(WebhookConfig.created_at.asc())
    )
    webhooks = result.scalars().all()
    return [_webhook_to_response(w) for w in webhooks]


@router.post(
    "/webhooks",
    response_model=WebhookConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_webhook(
    payload: WebhookConfigCreate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Registers an outgoing webhook endpoint (Admin only)."""
    import uuid

    webhook = WebhookConfig(
        id=str(uuid.uuid4()),
        organization_id=auth.org_id,
        name=payload.name,
        url=str(payload.url),
        secret=payload.secret,
        headers_json=payload.headers,
        active=payload.active,
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return _webhook_to_response(webhook)


@router.get(
    "/webhooks/{webhook_id}",
    response_model=WebhookConfigResponse,
)
async def get_webhook(
    webhook_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a single webhook configuration."""
    webhook = await _load_webhook(db, webhook_id, auth.org_id)
    return _webhook_to_response(webhook)


@router.put(
    "/webhooks/{webhook_id}",
    response_model=WebhookConfigResponse,
)
async def update_webhook(
    webhook_id: str,
    payload: WebhookConfigUpdate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Updates a webhook configuration (Admin only)."""
    webhook = await _load_webhook(db, webhook_id, auth.org_id)
    updates = payload.model_dump(exclude_unset=True)
    if updates.get("url") is not None:
        updates["url"] = str(updates["url"])
    for key, value in updates.items():
        if key == "headers" and value is not None:
            webhook.headers_json = value
        else:
            setattr(webhook, key, value)
    await db.commit()
    await db.refresh(webhook)
    return _webhook_to_response(webhook)


@router.delete(
    "/webhooks/{webhook_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_webhook(
    webhook_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a webhook configuration (Admin only)."""
    webhook = await _load_webhook(db, webhook_id, auth.org_id)
    await db.delete(webhook)
    await db.commit()
    return {"status": "deleted", "webhook_id": webhook_id}


@router.post(
    "/webhooks/{webhook_id}/test",
    response_model=WebhookTestResponse,
)
async def test_webhook(
    webhook_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Sends a lightweight test ping to the webhook endpoint (Admin only)."""
    webhook = await _load_webhook(db, webhook_id, auth.org_id)
    result = WebhookTestResponse(**await dispatch_test_webhook(webhook))

    # Persist the test ping in the audit trail for full traceability
    delivery = WebhookDelivery(
        organization_id=auth.org_id,
        webhook_id=webhook.id,
        document_id=None,
        event="webhook.test",
        url=webhook.url,
        status=result.status,
        http_status=result.http_status,
        response_body=None,
        error_message=result.error_message,
        duration_ms=result.duration_ms,
    )
    db.add(delivery)
    await db.commit()
    return result


@router.get(
    "/webhooks/deliveries",
    response_model=List[WebhookDeliveryResponse],
)
async def list_webhook_deliveries(
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=500),
):
    """Lists the audit trail of webhook deliveries for the organization."""
    result = await db.execute(
        select(WebhookDelivery)
        .where(WebhookDelivery.organization_id == auth.org_id)
        .order_by(WebhookDelivery.created_at.desc())
        .limit(limit)
    )
    deliveries = result.scalars().all()
    return [_delivery_to_response(d) for d in deliveries]


@router.get(
    "/webhooks/{webhook_id}/deliveries",
    response_model=List[WebhookDeliveryResponse],
)
async def list_webhook_deliveries_for_webhook(
    webhook_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER)),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=500),
):
    """Lists the audit trail for a specific webhook configuration."""
    webhook = await _load_webhook(db, webhook_id, auth.org_id)
    result = await db.execute(
        select(WebhookDelivery)
        .where(
            WebhookDelivery.organization_id == auth.org_id,
            WebhookDelivery.webhook_id == webhook.id,
        )
        .order_by(WebhookDelivery.created_at.desc())
        .limit(limit)
    )
    deliveries = result.scalars().all()
    return [_delivery_to_response(d) for d in deliveries]


async def _load_rule(
    db: AsyncSession, rule_id: str, organization_id: str
) -> AutomationRule:
    result = await db.execute(
        select(AutomationRule).where(
            AutomationRule.id == rule_id,
            AutomationRule.organization_id == organization_id,
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regla '{rule_id}' no encontrada.",
        )
    return rule


async def _load_webhook(
    db: AsyncSession, webhook_id: str, organization_id: str
) -> WebhookConfig:
    result = await db.execute(
        select(WebhookConfig).where(
            WebhookConfig.id == webhook_id,
            WebhookConfig.organization_id == organization_id,
        )
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook '{webhook_id}' no encontrado.",
        )
    return webhook