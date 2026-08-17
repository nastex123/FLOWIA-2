"""Unit and integration tests for the VisionExtractor, QR/Barcode Decoder, and OMR Checkbox Detector."""

import io
import numpy as np
import pytest
from PIL import Image, ImageDraw

from app.domain.vision_models import BarcodeFormat
from app.services.extractors.vision_extractor import VisionExtractor


@pytest.fixture
def vision_extractor():
    return VisionExtractor()


def test_parse_ticketbai_verifactu_payload(vision_extractor):
    url = "https://sede.agenciatributaria.gob.es/verifactu?nif=B12345678&num=FAC-2024-99&imp=1250.50&crc=ABCD1234"
    ptype, meta = vision_extractor._parse_barcode_payload(url)

    assert ptype == "ticketbai_verifactu"
    assert meta["nif"] == "B12345678"
    assert meta["invoice_number"] == "FAC-2024-99"
    assert meta["total_amount"] == 1250.50
    assert meta["fiscal_hash"] == "ABCD1234"


def test_parse_sepa_epc_payload(vision_extractor):
    payload = "BCD\n002\n1\nSCT\n\nProveedor S.L.\nES9121000418450200051332\nEUR850.00\n\nREF-9988\nFactura Junio"
    ptype, meta = vision_extractor._parse_barcode_payload(payload)

    assert ptype == "sepa_epc"
    assert meta["iban"] == "ES9121000418450200051332"
    assert meta["total_amount"] == 850.00


def test_parse_key_value_payload(vision_extractor):
    payload = "vendor=Acme Corp;inv_no=INV-001;total=450.00"
    ptype, meta = vision_extractor._parse_barcode_payload(payload)

    assert ptype == "key_value"
    assert meta["vendor"] == "Acme Corp"
    assert meta["inv_no"] == "INV-001"
    assert meta["total"] == "450.00"


def test_detect_omr_checkboxes(vision_extractor):
    # Create synthetic image with 2 checkboxes: one checked (filled), one unchecked (empty)
    img = Image.new("RGB", (300, 150), color="white")
    draw = ImageDraw.Draw(img)

    # Box 1: Empty (Unchecked) at (30, 30) size 30x30
    draw.rectangle([30, 30, 60, 60], outline="black", width=2)

    # Box 2: Checked (Filled inside) at (120, 30) size 30x30
    draw.rectangle([120, 30, 150, 60], outline="black", width=2)
    draw.rectangle([126, 36, 144, 54], fill="black")

    img_np = np.array(img)
    checkboxes = vision_extractor.detect_checkboxes(img_np)

    assert len(checkboxes) >= 2
    # Find checked and unchecked
    checked_boxes = [c for c in checkboxes if c.is_checked]
    unchecked_boxes = [c for c in checkboxes if not c.is_checked]

    assert len(checked_boxes) >= 1
    assert len(unchecked_boxes) >= 1


def test_dewarp_document_perspective(vision_extractor):
    # Create a synthetic white document sheet on dark background
    canvas = np.zeros((400, 400, 3), dtype=np.uint8)
    # Draw a tilted/perspective quadrilateral document in the center
    # Top-left=(50, 80), Top-right=(320, 50), Bottom-right=(350, 320), Bottom-left=(70, 340)
    pts = np.array([[50, 80], [320, 50], [350, 320], [70, 340]], dtype=np.int32)
    import cv2
    cv2.fillPoly(canvas, [pts], (255, 255, 255))

    warped, info = vision_extractor.dewarp_document(canvas)
    assert info.applied is True
    assert len(info.warped_dimensions) == 2
    assert info.warped_dimensions[0] > 100
    assert info.warped_dimensions[1] > 100


def test_extract_from_image_bytes(vision_extractor):
    # Create a synthetic image with invoice text drawn
    img = Image.new("RGB", (600, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((30, 30), "FACTURA F-2024-8888", fill="black")
    draw.text((30, 70), "CIF: B12345678", fill="black")
    draw.text((30, 110), "TOTAL: 1500,00 EUR", fill="black")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    result = vision_extractor.extract(
        file_input=img_bytes,
        filename="scanned_invoice.png",
        document_id="doc-vision-001",
    )

    assert result.document_id == "doc-vision-001"
    assert result.filename == "scanned_invoice.png"
    assert result.classification is not None
