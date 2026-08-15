"""Integration tests validating extraction on all generated sample documents."""

from pathlib import Path
import pytest
from app.domain.schemas import DocumentType
from app.services.extractors.pdf_extractor import PDFExtractor
from app.services.extractors.tabular_extractor import TabularExtractor
from app.services.classifiers.ml_classifier import MLClassifier
from app.services.classifiers.rule_classifier import RuleClassifier


SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def test_sample_invoice_xlsx():
    file_path = SAMPLES_DIR / "factura_suministros_2024.xlsx"
    extractor = TabularExtractor()
    result = extractor.extract(file_input=file_path, filename=file_path.name)

    assert result.classification.document_type == DocumentType.INVOICE
    assert len(result.tables) >= 1
    assert result.tables[0].rows_count >= 5
    assert "tax_id" in result.fields or "invoice_number" in result.fields


def test_sample_inventory_csv():
    file_path = SAMPLES_DIR / "inventario_almacen_central.csv"
    extractor = TabularExtractor()
    result = extractor.extract(file_input=file_path, filename=file_path.name)

    assert result.classification.document_type == DocumentType.INVENTORY
    assert len(result.tables) == 1
    assert result.tables[0].rows_count == 8
    assert "SKU" in result.tables[0].headers


def test_sample_purchase_order_csv():
    file_path = SAMPLES_DIR / "orden_compra_material_po_4091.csv"
    extractor = TabularExtractor()
    result = extractor.extract(file_input=file_path, filename=file_path.name)

    assert result.classification.document_type == DocumentType.PURCHASE_ORDER
    assert len(result.tables) == 1
    assert result.tables[0].rows_count == 4


def test_sample_payroll_xlsx():
    file_path = SAMPLES_DIR / "nomina_empleado_junio_2024.xlsx"
    extractor = TabularExtractor()
    result = extractor.extract(file_input=file_path, filename=file_path.name)

    assert result.classification.document_type == DocumentType.PAYROLL
    assert len(result.tables) >= 1


def test_sample_invoice_pdf():
    file_path = SAMPLES_DIR / "factura_consultoria_cloud.pdf"
    extractor = PDFExtractor()
    result = extractor.extract(file_input=file_path, filename=file_path.name)

    assert result.classification.document_type == DocumentType.INVOICE
    assert "invoice_number" in result.fields
    assert "tax_id" in result.fields
    assert "email" in result.fields
    assert "total_amount" in result.fields


def test_sample_contract_pdf():
    file_path = SAMPLES_DIR / "contrato_prestacion_servicios.pdf"
    extractor = PDFExtractor()
    result = extractor.extract(file_input=file_path, filename=file_path.name)

    assert result.classification.document_type == DocumentType.CONTRACT
    assert "tax_id" in result.fields
