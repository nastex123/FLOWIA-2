"""REST API endpoints for the Enterprise Decision Engine, Mathematical Validator, and Sentinel with database persistence."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthContext, resolve_auth
from app.domain.decision_models import (
    DecisionScoreResult,
    EntityMatchResult,
    EntityResolveRequest,
    MathValidationRequest,
    MathematicalValidationResult,
    SentinelAuditRequest,
    SentinelAuditResult,
)
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    Document,
    DocumentCheck,
    EntityRecord,
    InvoiceFingerprint,
)
from app.services.decision.entity_resolution import EntityResolutionEngine
from app.services.decision.mathematical_validator import MathematicalDocumentValidator
from app.services.decision.sentinel import FlowMindSentinel

router = APIRouter(prefix="/api/v1/decision", tags=["Enterprise Decision Engine & Sentinel"])

math_validator = MathematicalDocumentValidator()
entity_resolver = EntityResolutionEngine()
sentinel = FlowMindSentinel()


@router.post(
    "/validate-math",
    response_model=MathematicalValidationResult,
    status_code=status.HTTP_200_OK,
)
async def validate_document_math(
    request: MathValidationRequest,
    auth: AuthContext = Depends(resolve_auth),
):
    """Deterministically recalculates line item totals, tax groups, withholdings and checks against document totals."""
    return math_validator.validate_invoice(
        lines=request.lines,
        document_subtotal=request.document_subtotal,
        document_tax=request.document_tax,
        document_total=request.document_total,
        withholding_pct=request.withholding_pct,
        shipping_cost=request.shipping_cost,
    )


@router.post(
    "/entities/resolve",
    response_model=EntityMatchResult,
    status_code=status.HTTP_200_OK,
)
async def resolve_entity(
    request: EntityResolveRequest,
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Resolves a supplier/client name, tax ID, and IBAN against tenant entity records using multi-signal scoring."""
    stmt = select(EntityRecord).where(
        EntityRecord.organization_id == auth.org_id
    )
    entities = (await db.execute(stmt)).scalars().all()

    known_entities = [
        {
            "id": ent.entity_id,
            "name": ent.name,
            "tax_id": ent.tax_id,
            "ibans": ent.ibans_json or [],
            "email_domain": ent.email_domain,
            "phone": ent.phone,
        }
        for ent in entities
    ]

    return entity_resolver.resolve(
        query={
            "name": request.name,
            "tax_id": request.tax_id,
            "iban": request.iban,
            "email_domain": request.email_domain,
            "phone": request.phone,
        },
        known_entities=known_entities,
    )


@router.post(
    "/sentinel-audit",
    response_model=SentinelAuditResult,
    status_code=status.HTTP_200_OK,
)
async def audit_invoice_with_sentinel(
    request: SentinelAuditRequest,
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Runs continuous anti-fraud audit checks: IBAN changes, multidimensional duplicates, and anomaly detection against tenant history."""
    # 1. Fetch vendor's known IBANs from database
    known_ibans: List[str] = []
    if request.vendor_tax_id:
        ent_stmt = select(EntityRecord).where(
            EntityRecord.organization_id == auth.org_id,
            EntityRecord.tax_id == request.vendor_tax_id,
        )
        ent = (await db.execute(ent_stmt)).scalar_one_or_none()
        if ent and ent.ibans_json:
            known_ibans = list(ent.ibans_json)

    # 2. Fetch historical invoice records from database
    fp_stmt = select(InvoiceFingerprint).where(
        InvoiceFingerprint.organization_id == auth.org_id
    )
    fps = (await db.execute(fp_stmt)).scalars().all()

    historical_records = [
        {
            "document_id": fp.document_id,
            "vendor_tax_id": fp.vendor_tax_id,
            "invoice_number": fp.invoice_number,
            "invoice_date": fp.invoice_date.strftime("%Y-%m-%d") if fp.invoice_date else "",
            "total_amount": fp.total_amount,
        }
        for fp in fps
    ]

    return sentinel.audit_document(
        document_id=request.document_id,
        vendor_tax_id=request.vendor_tax_id,
        invoice_number=request.invoice_number,
        invoice_date=request.invoice_date,
        total_amount=request.total_amount,
        iban=request.iban,
        known_vendor_ibans=known_ibans,
        historical_records=historical_records,
    )


@router.get(
    "/checks",
    status_code=status.HTTP_200_OK,
)
async def list_decision_checks(
    document_id: Optional[str] = Query(None, description="Filter checks for a specific document"),
    severity: Optional[str] = Query(None, description="Filter by severity: ok, warning, critical, info"),
    status: Optional[str] = Query(None, description="Filter by status: open, acknowledged"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Lists audit and validation checks for the organization with pagination and filters."""
    base_query = (
        select(DocumentCheck, Document.filename)
        .join(Document, Document.id == DocumentCheck.document_id)
        .where(DocumentCheck.organization_id == auth.org_id)
    )
    count_query = (
        select(func.count(DocumentCheck.id))
        .where(DocumentCheck.organization_id == auth.org_id)
    )

    if document_id:
        base_query = base_query.where(DocumentCheck.document_id == document_id)
        count_query = count_query.where(DocumentCheck.document_id == document_id)

    if severity:
        base_query = base_query.where(DocumentCheck.severity == severity.lower())
        count_query = count_query.where(DocumentCheck.severity == severity.lower())

    if status:
        base_query = base_query.where(DocumentCheck.status == status.lower())
        count_query = count_query.where(DocumentCheck.status == status.lower())

    # Total count
    total_count = (await db.execute(count_query)).scalar() or 0

    # Paginated results
    query = (
        base_query
        .order_by(DocumentCheck.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = (await db.execute(query)).all()

    items = [
        {
            "id": chk.id,
            "document_id": chk.document_id,
            "filename": filename,
            "check_type": chk.check_type,
            "severity": chk.severity,
            "status": chk.status,
            "title": chk.title,
            "detail_json": chk.detail_json,
            "created_at": chk.created_at.isoformat(),
        }
        for chk, filename in rows
    ]

    return {
        "items": items,
        "total": total_count,
        "limit": limit,
        "offset": offset,
    }
