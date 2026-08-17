"""REST API Router for Specialized Business Engines (3-Way Match, Norma 43, Payroll Splitter)."""

from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import AuthContext, require_editor_or_api_key, resolve_auth
from app.domain.business_models import (
    Norma43ParseResult,
    PayrollSplitResult,
    ThreeWayMatchRequest,
    ThreeWayMatchResult,
)
from app.services.business.norma43_parser import Norma43Parser
from app.services.business.payroll_splitter import PayrollSplitter
from app.services.business.three_way_matching import ThreeWayMatchingEngine

router = APIRouter(prefix="/api/v1/business", tags=["Business Engines & Reconciliation"])

match_engine = ThreeWayMatchingEngine()
norma43_parser = Norma43Parser()
payroll_splitter = PayrollSplitter()


@router.post(
    "/three-way-match",
    response_model=ThreeWayMatchResult,
    status_code=status.HTTP_200_OK,
)
async def perform_three_way_match(
    request: ThreeWayMatchRequest,
    auth: AuthContext = Depends(resolve_auth),
):
    """Reconciles line items across Purchase Order, Goods Receipt, and Invoice."""
    return match_engine.reconcile(
        po_number=request.po_number,
        invoice_number=request.invoice_number,
        lines=request.lines,
        qty_tolerance_pct=request.qty_tolerance_pct,
        price_tolerance_pct=request.price_tolerance_pct,
    )


@router.post(
    "/norma43/parse",
    response_model=Norma43ParseResult,
    status_code=status.HTTP_200_OK,
)
async def parse_norma43_file(
    file: UploadFile = File(..., description="Spanish Norma 43 / CSB 43 bank statement file"),
    auth: AuthContext = Depends(require_editor_or_api_key),
):
    """Parses a Spanish standard Norma 43 bank statement into structured movement records."""
    content = await file.read()
    try:
        return norma43_parser.parse(content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Norma 43 parsing failed: {str(e)}")


@router.post(
    "/payroll/split",
    response_model=PayrollSplitResult,
    status_code=status.HTTP_200_OK,
)
async def split_payroll_document(
    file: UploadFile = File(..., description="Multi-page payroll PDF"),
    auth: AuthContext = Depends(require_editor_or_api_key),
):
    """Splits a mass payroll PDF into individual employee PDFs."""
    content = await file.read()
    try:
        return payroll_splitter.split_payroll_pdf(content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Payroll splitting failed: {str(e)}")
