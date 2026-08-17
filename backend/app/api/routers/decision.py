"""REST API endpoints for the Enterprise Decision Engine, Mathematical Validator, and Sentinel."""

from fastapi import APIRouter, Depends, HTTPException, status
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
    """Resolves a supplier/client name, tax ID, and IBAN against known entities using multi-signal scoring."""
    # Mock seed entities for testing / demo
    known_entities = [
        {
            "id": "ent-001",
            "name": "Suministros Industriales Iberica S.L.",
            "tax_id": "ESB12345678",
            "ibans": ["ES9121000418450200051332"],
            "email_domain": "suministros.es",
            "phone": "+34912345678",
        },
        {
            "id": "ent-002",
            "name": "Tech Logistics & Distribution S.A.",
            "tax_id": "ESA87654321",
            "ibans": ["ES6000491500051234567892"],
            "email_domain": "techlogistics.com",
            "phone": "+34934567890",
        },
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
    """Runs continuous anti-fraud audit checks: IBAN changes, multidimensional duplicates, and anomaly detection."""
    # Historical mock data for vendor IBANs and prior invoices
    known_ibans = ["ES9121000418450200051332"] if request.vendor_tax_id == "ESB12345678" else []
    historical_records = [
        {
            "document_id": "doc-hist-001",
            "vendor_tax_id": "ESB12345678",
            "invoice_number": "F-2024-001",
            "invoice_date": "2024-05-10",
            "total_amount": 1500.00,
        }
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
