"""End-to-end document processing pipeline with database persistence."""

import time
from pathlib import Path
from typing import Optional
from sqlalchemy import select

from app.core.logging import logger
from app.domain.schemas import DocumentType
from app.infrastructure.database import async_session_factory
from app.infrastructure.models import Document, DocumentStatus, ExtractionRecord
from app.services.classifiers.ml_classifier import MLClassifier
from app.services.classifiers.rule_classifier import RuleClassifier
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.extractors.vision_extractor import VisionExtractor
from app.services.automation.runner import run_automation_rules


async def process_document_pipeline(
    document_id: str,
    organization_id: str,
    file_path: Path,
    filename: str,
) -> None:
    """Executes extraction, ML classification, and persists structured results asynchronously."""
    start_time = time.perf_counter()
    logger.info(f"Pipeline started for document '{filename}' (ID: {document_id})")

    tabular_extractor = TabularExtractor()
    pdf_extractor = PDFExtractor()
    vision_extractor = VisionExtractor()
    rule_classifier = RuleClassifier()
    ml_classifier = MLClassifier(auto_train=True)

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

            # 3. Persist extraction record
            fields_data = {
                k: v.model_dump() for k, v in extraction_result.fields.items()
            }
            tables_data = [
                t.model_dump() for t in extraction_result.tables
            ]

            record = ExtractionRecord(
                document_id=document_id,
                organization_id=organization_id,
                document_type=classification.document_type.value,
                confidence=classification.confidence,
                fields_json=fields_data,
                tables_json=tables_data,
                raw_summary=text_summary[:1000],
                processing_time_ms=round(elapsed_ms, 2),
            )
            session.add(record)

            doc.status = DocumentStatus.COMPLETED
            doc.error_message = None
            await session.commit()
            logger.info(f"Pipeline successfully completed for document {document_id} in {elapsed_ms:.2f}ms")

            # Fire business automation rules for the extraction event
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
