"""Pytest configuration and shared fixtures for FlowMind AI."""

import sys
from pathlib import Path
import pytest

# Ensure backend root is on Python path
BACKEND_DIR = Path(__file__).parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import asyncio
from app.infrastructure.database import Base, engine


@pytest.fixture(autouse=True)
def clean_db():
    """Ensures each test starts with a clean isolated database state."""
    async def _reset():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_reset())
    yield


@pytest.fixture
def sample_csv_invoice():
    """Generates a sample CSV invoice with European delimiter and formatted amounts."""
    return (
        "Factura_No;Fecha_Emision;Cliente;CIF_NIF;Base_Imponible;Total_Factura\n"
        "INV-2024-9988;2024-05-15;Acme Corp SL;B87654321;1000,00;1210,00\n"
        "INV-2024-9989;2024-05-16;Beta Retail SA;A12345678;2500,50;3025,60\n"
    ).encode("utf-8")


@pytest.fixture
def sample_csv_with_formula_injection():
    """CSV containing potential formula injection payloads."""
    return (
        "Item,Price,FormulaPayload\n"
        "Server,1200,=cmd|' /C calc'!A0\n"
        "License,300,+cmd|' /C calc'!A0\n"
        "Support,150,@SUM(1+1)\n"
    ).encode("utf-8")


@pytest.fixture
def sample_invoice_text():
    """Sample raw invoice text snippet for NLP and regex extraction."""
    return """
    EMPRESA SUMINISTROS INDUSTRIALES S.L.
    CIF: B87654321
    Email de contacto: facturacion@suministros.com
    
    FACTURA: F-2024-0899
    Fecha: 2024-06-20
    
    Cliente: Construcciones del Norte S.A.
    NIF: A11223344
    
    Concepto                       Cantidad   Precio Unitario   Total
    Material de construcción       10         100.00 €          1000.00 €
    
    Base imponible: 1.000,00 €
    IVA (21%): 210,00 €
    IMPORTE TOTAL: 1.210,00 €
    
    Forma de pago: Transferencia al IBAN ES7621000418401234567891
    """
