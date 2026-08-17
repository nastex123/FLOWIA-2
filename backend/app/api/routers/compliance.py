"""REST API Router for Fiscal Compliance (AEAT SII, Verifactu) and PII Redactor."""

from fastapi import APIRouter, Depends, status

from app.api.deps import AuthContext, require_editor_or_api_key, resolve_auth
from app.domain.compliance_models import (
    PIIRedactionRequest,
    PIIRedactionResult,
    SIIRegistrationRequest,
    SIIRegistrationResult,
    VerifactuChainingRequest,
    VerifactuChainingResult,
)
from app.services.compliance.pii_redactor import PIIRedactor
from app.services.compliance.sii_generator import SIIGenerator
from app.services.compliance.verifactu_engine import VerifactuEngine

router = APIRouter(prefix="/api/v1/compliance", tags=["Fiscal Compliance & PII"])

sii_gen = SIIGenerator()
verifactu_engine = VerifactuEngine()
pii_redactor = PIIRedactor()


@router.post(
    "/sii/generate-xml",
    response_model=SIIRegistrationResult,
    status_code=status.HTTP_200_OK,
)
async def generate_sii_xml_endpoint(
    request: SIIRegistrationRequest,
    auth: AuthContext = Depends(require_editor_or_api_key),
):
    """Generates official AEAT Suministro Inmediato de Información (SII) XML payload."""
    return sii_gen.generate_sii_xml(request)


@router.post(
    "/verifactu/chain-hash",
    response_model=VerifactuChainingResult,
    status_code=status.HTTP_200_OK,
)
async def chain_verifactu_hash_endpoint(
    request: VerifactuChainingRequest,
    auth: AuthContext = Depends(require_editor_or_api_key),
):
    """Computes verifiable SHA-256 chained hash and QR payload for Veri*factu / TicketBAI compliance."""
    return verifactu_engine.compute_chained_hash(request)


@router.post(
    "/pii/redact",
    response_model=PIIRedactionResult,
    status_code=status.HTTP_200_OK,
)
async def redact_pii_endpoint(
    request: PIIRedactionRequest,
    auth: AuthContext = Depends(resolve_auth),
):
    """Anonymizes sensitive PII entities (NIF, IBAN, emails, phones) from text."""
    return pii_redactor.redact(request)
