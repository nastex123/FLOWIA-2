"""Unit tests for the Mega-PDF Payroll Splitter."""

import io
import pytest
import fitz
from app.services.business.payroll_splitter import PayrollSplitter


@pytest.fixture
def sample_multipage_payroll_pdf():
    """Generates a synthetic 2-page payroll PDF with 2 distinct employees."""
    doc = fitz.open()

    # Page 1: Employee 1
    page1 = doc.new_page()
    text1 = """
    NÓMINA MENSUAL - MAYO 2024
    Empresa: Construcciones Global S.L.
    Trabajador: GARCÍA PÉREZ, JUAN
    DNI: 12345678Z
    Categoría: Oficial de Primera
    Total Devengos: 2.100,00 €
    LÍQUIDO TOTAL A PERCIBIR: 1.750,00 €
    """
    page1.insert_text((50, 72), text1)

    # Page 2: Employee 2
    page2 = doc.new_page()
    text2 = """
    NÓMINA MENSUAL - MAYO 2024
    Empresa: Construcciones Global S.L.
    Trabajador: LÓPEZ MARTÍNEZ, ELENA
    DNI: 87654321A
    Categoría: Jefa de Obra
    Total Devengos: 3.500,00 €
    LÍQUIDO TOTAL A PERCIBIR: 2.800,00 €
    """
    page2.insert_text((50, 72), text2)

    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def test_payroll_splitter_splits_multipage_pdf(sample_multipage_payroll_pdf, tmp_path):
    splitter = PayrollSplitter()
    out_dir = tmp_path / "splits"

    res = splitter.split_payroll_pdf(
        pdf_input=sample_multipage_payroll_pdf,
        output_directory=out_dir,
    )

    assert res.total_pages == 2
    assert res.employees_detected == 2
    assert len(res.splits) == 2

    # Check first employee split
    emp1 = res.splits[0]
    assert "12345678Z" in emp1.employee_nif or "GARCÍA" in emp1.employee_name
    assert (out_dir / emp1.output_filename).exists()

    # Check second employee split
    emp2 = res.splits[1]
    assert "87654321A" in emp2.employee_nif or "LÓPEZ" in emp2.employee_name
    assert (out_dir / emp2.output_filename).exists()
