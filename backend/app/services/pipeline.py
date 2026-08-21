"""End-to-end document processing pipeline with database persistence and invoice audit."""

import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import select

from app.core.logging import logger
from app.domain.decision_models import LineItemInput
from app.domain.schemas import DocumentType
from app.infrastructure.database import async_session_factory
from app.infrastructure.models import (
    Document,
    DocumentCheck,
    DocumentStatus,
    EntityRecord,
    ExtractionRecord,
    InvoiceFingerprint,
)
from app.services.automation.runner import run_automation_rules
from app.services.classifiers.ml_classifier import MLClassifier
from app.services.classifiers.rule_classifier import RuleClassifier
from app.services.decision.entity_resolution import EntityResolutionEngine
from app.services.decision.mathematical_validator import MathematicalDocumentValidator
from app.services.decision.sentinel import FlowMindSentinel
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.extractors.vision_extractor import VisionExtractor
from app.services.invoice.structurizer import InvoiceStructurizer


def _get_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def process_document_pipeline(
    document_id: str,
    organization_id: str,
    file_path: Path,
    filename: str,
) -> None:
    """Executes extraction, ML classification, invoice validation, and persists structured results asynchronously."""
    start_time = time.perf_counter()
    logger.info(f"Pipeline started for document '{filename}' (ID: {document_id})")

    tabular_extractor = TabularExtractor()
    pdf_extractor = PDFExtractor()
    vision_extractor = VisionExtractor()
    rule_classifier = RuleClassifier()
    ml_classifier = MLClassifier(auto_train=True)
    invoice_structurizer = InvoiceStructurizer()
    math_validator = MathematicalDocumentValidator()
    sentinel = FlowMindSentinel()
    entity_resolver = EntityResolutionEngine()

    ext = Path(filename).suffix.lower().lstrip(".")

    async with async_session_factory() as session:
        # Mark as processing
        stmt = select(Document).where(
            Document.id == document_id, Document.organization_id == organization_id
        )
        result = await session.execute(stmt)
        doc = result.scalar_one_or_none()
        if not doc:
            logger.error(f"Document {document_id} not found for tenant {organization_id}")
            return

        doc.status = DocumentStatus.PROCESSING
        await session.commit()

        try:
            # 1. Extract structured data
            if ext in ("xlsx", "xls", "csv"):
                extraction_result = tabular_extractor.extract(
                    file_input=file_path,
                    filename=filename,
                    document_id=document_id,
                )
            elif ext == "pdf":
                extraction_result = pdf_extractor.extract(
                    file_input=file_path,
                    filename=filename,
                    document_id=document_id,
                )
            elif ext in ("png", "jpg", "jpeg", "tiff", "bmp", "webp"):
                extraction_result = vision_extractor.extract(
                    file_input=file_path,
                    filename=filename,
                    document_id=document_id,
                )
            else:
                raise ValueError(f"Unsupported format: {ext}")

            # 2. Refine classification with hybrid (Rules + ML)
            text_summary = extraction_result.raw_text_summary or ""
            classification = rule_classifier.classify(text_summary)
            if classification.document_type == DocumentType.UNKNOWN:
                classification = ml_classifier.classify(text_summary)

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # 3. Extract and serialize raw fields/tables
            fields_data = {
                k: v.model_dump() for k, v in extraction_result.fields.items()
            }
            tables_data = [
                t.model_dump() for t in extraction_result.tables
            ]

            structured_invoice_data: Optional[Dict[str, Any]] = None
            generated_checks: List[DocumentCheck] = []

            # 4. If document is an invoice, execute specialized validation & audit pipeline
            if classification.document_type == DocumentType.INVOICE or classification.document_type.value == "invoice":
                # A. Structurize invoice
                structured_inv = invoice_structurizer.structurize(
                    extraction_result=extraction_result,
                    document_id=document_id,
                )
                structured_invoice_data = structured_inv.model_dump(mode="json")

                # B. Mathematical validation
                line_inputs = [
                    LineItemInput(
                        description=item.description,
                        quantity=item.quantity or 1.0,
                        unit_price=item.unit_price or 0.0,
                        discount_pct=item.discount_pct or 0.0,
                        tax_rate_pct=item.tax_rate_pct or 21.0,
                        line_total=item.line_total,
                    )
                    for item in structured_inv.items
                ]

                math_res = math_validator.validate_invoice(
                    lines=line_inputs,
                    document_subtotal=structured_inv.subtotal,
                    document_tax=structured_inv.tax_total,
                    document_total=structured_inv.total_amount,
                    withholding_pct=0.0,
                    shipping_cost=structured_inv.shipping_amount or 0.0,
                )

                if math_res.findings:
                    for finding in math_res.findings:
                        generated_checks.append(
                            DocumentCheck(
                                organization_id=organization_id,
                                document_id=document_id,
                                check_type="math_discrepancy",
                                severity=finding.severity.value,
                                status="open",
                                title=finding.description,
                                detail_json={
                                    "deviation": finding.deviation,
                                    "expected_value": finding.expected_value,
                                    "actual_value": finding.actual_value,
                                    "category": finding.category,
                                },
                            )
                        )
                else:
                    generated_checks.append(
                        DocumentCheck(
                            organization_id=organization_id,
                            document_id=document_id,
                            check_type="math_discrepancy",
                            severity="ok",
                            status="open",
                            title="Recálculo matemático de totales e impuestos correcto",
                            detail_json={"deviation": math_res.deviation},
                        )
                    )

                # C. Sentinel Duplicate & Bank Account change checks
                # Fingerprint check
                fingerprint_hash = sentinel.generate_fingerprint(
                    vendor_tax_id=structured_inv.vendor_tax_id,
                    invoice_number=structured_inv.invoice_number,
                    invoice_date=str(structured_inv.issue_date or ""),
                    total_amount=structured_inv.total_amount,
                )

                # Query existing fingerprint for tenant
                fp_stmt = select(InvoiceFingerprint).where(
                    InvoiceFingerprint.organization_id == organization_id,
                    InvoiceFingerprint.fingerprint == fingerprint_hash,
                    InvoiceFingerprint.document_id != document_id,
                )
                existing_fp = (await session.execute(fp_stmt)).scalar_one_or_none()

                if existing_fp:
                    generated_checks.append(
                        DocumentCheck(
                            organization_id=organization_id,
                            document_id=document_id,
                            check_type="duplicate_invoice",
                            severity="critical",
                            status="open",
                            title=f"Factura duplicada detectada: coincide con documento {existing_fp.document_id[:8]}...",
                            detail_json={
                                "duplicate_document_id": existing_fp.document_id,
                                "fingerprint": fingerprint_hash,
                                "invoice_number": structured_inv.invoice_number,
                                "vendor_tax_id": structured_inv.vendor_tax_id,
                            },
                        )
                    )
                else:
                    # Persist new fingerprint
                    inv_fp = InvoiceFingerprint(
                        organization_id=organization_id,
                        document_id=document_id,
                        fingerprint=fingerprint_hash,
                        vendor_tax_id=structured_inv.vendor_tax_id,
                        invoice_number=structured_inv.invoice_number,
                        invoice_date=datetime.combine(structured_inv.issue_date, datetime.min.time()) if structured_inv.issue_date else None,
                        total_amount=structured_inv.total_amount,
                    )
                    session.add(inv_fp)

                # Detect IBAN from text or fields
                iban_candidate = None
                if "iban" in fields_data:
                    iban_candidate = str(fields_data["iban"].get("value", ""))
                else:
                    iban_match = re.search(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b", text_summary)
                    if iban_match:
                        iban_candidate = iban_match.group(0)

                # D. Entity Resolution & Bank Account verification
                if structured_inv.vendor_name or structured_inv.vendor_tax_id:
                    # Query existing entities for tenant
                    ent_stmt = select(EntityRecord).where(
                        EntityRecord.organization_id == organization_id
                    )
                    existing_entities = (await session.execute(ent_stmt)).scalars().all()
                    candidates = [
                        {
                            "entity_id": ent.entity_id,
                            "name": ent.name,
                            "tax_id": ent.tax_id,
                            "ibans": ent.ibans_json or [],
                        }
                        for ent in existing_entities
                    ]

                    query_entity = {
                        "name": structured_inv.vendor_name,
                        "tax_id": structured_inv.vendor_tax_id,
                        "iban": iban_candidate,
                    }

                    match_res = entity_resolver.resolve(query_entity, candidates)

                    if match_res.entity_id:
                        matched_ent = next((e for e in existing_entities if e.entity_id == match_res.entity_id), None)
                        if matched_ent and iban_candidate:
                            # Verify if IBAN changed
                            bank_alert = sentinel.check_bank_account_change(
                                vendor_tax_id=structured_inv.vendor_tax_id or matched_ent.name,
                                current_iban=iban_candidate,
                                known_vendor_ibans=matched_ent.ibans_json or [],
                            )
                            if bank_alert:
                                generated_checks.append(
                                    DocumentCheck(
                                        organization_id=organization_id,
                                        document_id=document_id,
                                        check_type="bank_account_change",
                                        severity="critical",
                                        status="open",
                                        title=bank_alert.title,
                                        detail_json=bank_alert.evidence,
                                    )
                                )
                            else:
                                clean_ib = sentinel.clean_iban(iban_candidate)
                                if clean_ib and clean_ib not in (matched_ent.ibans_json or []):
                                    matched_ent.ibans_json = list(matched_ent.ibans_json or []) + [clean_ib]
                                    matched_ent.updated_at = _get_utc_now()
                    else:
                        # Create new entity record
                        new_entity_id = f"ENT-{abs(hash(structured_inv.vendor_tax_id or structured_inv.vendor_name or document_id)) % 1000000:06d}"
                        clean_ib_list = [sentinel.clean_iban(iban_candidate)] if iban_candidate else []
                        new_ent = EntityRecord(
                            organization_id=organization_id,
                            entity_id=new_entity_id,
                            name=structured_inv.vendor_name or "Proveedor Desconocido",
                            tax_id=structured_inv.vendor_tax_id,
                            ibans_json=clean_ib_list,
                        )
                        session.add(new_ent)

                    generated_checks.append(
                        DocumentCheck(
                            organization_id=organization_id,
                            document_id=document_id,
                            check_type="entity_resolution",
                            severity="info",
                            status="open",
                            title=f"Resolución de entidad: {match_res.canonical_name or structured_inv.vendor_name or 'Nuevo proveedor'}",
                            detail_json={
                                "action": match_res.action.value,
                                "entity_id": match_res.entity_id or "new_entity",
                                "confidence_score": match_res.confidence_score,
                                "reasons": match_res.reasons,
                            },
                        )
                    )

            # 5. Persist extraction record
            record = ExtractionRecord(
                document_id=document_id,
                organization_id=organization_id,
                document_type=classification.document_type.value,
                confidence=classification.confidence,
                fields_json=fields_data,
                tables_json=tables_data,
                structured_json=structured_invoice_data,
                raw_summary=text_summary[:1000],
                processing_time_ms=round(elapsed_ms, 2),
            )
            session.add(record)

            # Add all generated checks
            for chk in generated_checks:
                session.add(chk)

            doc.status = DocumentStatus.COMPLETED
            doc.review_status = "unreviewed"
            doc.error_message = None
            await session.commit()
            logger.info(
                f"Pipeline successfully completed for document {document_id} "
                f"({len(generated_checks)} checks generated) in {elapsed_ms:.2f}ms"
            )

            # 6. Fire business automation rules
            try:
                await run_automation_rules(
                    session,
                    event="extraction_completed",
                    document_id=document_id,
                    organization_id=organization_id,
                    filename=filename,
                    document_type=classification.document_type.value,
                    fields=fields_data,
                )
            except Exception:
                logger.exception(
                    f"Automation rules dispatch failed for document {document_id}"
                )

        except Exception as e:
            logger.exception(f"Pipeline error processing document {document_id}")
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
            await session.commit()
