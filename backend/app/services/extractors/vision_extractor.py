"""Local Computer Vision, Barcode/QR Decoder, OMR Checkbox Detector and OCR Extractor."""

import io
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import zxingcpp
except ImportError:
    zxingcpp = None

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

from app.core.exceptions import ExtractionError
from app.domain.schemas import (
    ClassificationResult,
    DocumentType,
    ExtractedField,
    ExtractionResult,
)
from app.domain.vision_models import (
    BarcodeFormat,
    BarcodeItem,
    CheckboxItem,
    DewarpInfo,
    VisionExtractionResult,
)
from app.services.extractors.base import BaseExtractor
from app.services.extractors.rule_extractor import RuleExtractor


class VisionExtractor(BaseExtractor):
    """Offline computer vision engine for QR/Barcode reading, OMR checkbox detection and local OCR."""

    def __init__(self, rule_extractor: Optional[RuleExtractor] = None):
        self.rule_extractor = rule_extractor or RuleExtractor()

    def extract(
        self,
        file_input: Union[str, Path, bytes, BinaryIO, np.ndarray, Image.Image],
        filename: str = "document_image.png",
        document_id: Optional[str] = None,
        **kwargs,
    ) -> ExtractionResult:
        start_time = time.perf_counter()
        img_np = self._to_numpy_image(file_input)

        if img_np is None:
            raise ExtractionError(f"Could not decode image from '{filename}'")

        # 1. Barcode and QR Code Extraction
        barcodes = self.decode_barcodes(img_np)

        # 2. OMR Checkbox Detection
        checkboxes = self.detect_checkboxes(img_np)

        # 3. Local OCR Text Extraction
        ocr_text = self.extract_ocr_text(img_np)

        # 4. Extract atomic fields using RuleExtractor + QR metadata
        fields: Dict[str, ExtractedField] = {}
        if ocr_text:
            fields.update(self.rule_extractor.extract_from_text(ocr_text))

        # Inject barcode/QR parsed metadata into fields
        for b in barcodes:
            if b.metadata:
                if "nif" in b.metadata and "vendor_tax_id" not in fields:
                    fields["vendor_tax_id"] = ExtractedField(
                        key="vendor_tax_id",
                        value=b.metadata["nif"],
                        raw_value=str(b.metadata["nif"]),
                        confidence=1.0,
                        extractor_type="qr_barcode",
                        source_location=f"Barcode: {b.format.value}",
                    )
                if "invoice_number" in b.metadata and "invoice_number" not in fields:
                    fields["invoice_number"] = ExtractedField(
                        key="invoice_number",
                        value=b.metadata["invoice_number"],
                        raw_value=str(b.metadata["invoice_number"]),
                        confidence=1.0,
                        extractor_type="qr_barcode",
                        source_location=f"Barcode: {b.format.value}",
                    )
                if "total_amount" in b.metadata and "total_amount" not in fields:
                    fields["total_amount"] = ExtractedField(
                        key="total_amount",
                        value=b.metadata["total_amount"],
                        raw_value=str(b.metadata["total_amount"]),
                        confidence=1.0,
                        extractor_type="qr_barcode",
                        source_location=f"Barcode: {b.format.value}",
                    )
                if "iban" in b.metadata and "iban" not in fields:
                    fields["iban"] = ExtractedField(
                        key="iban",
                        value=b.metadata["iban"],
                        raw_value=str(b.metadata["iban"]),
                        confidence=1.0,
                        extractor_type="qr_barcode",
                        source_location=f"Barcode: {b.format.value}",
                    )

        # Add checkboxes as structured fields if any detected
        for cb in checkboxes:
            fields[f"checkbox_{cb.checkbox_id}"] = ExtractedField(
                key=f"checkbox_{cb.checkbox_id}",
                value=cb.is_checked,
                raw_value="checked" if cb.is_checked else "unchecked",
                confidence=round(cb.confidence, 2),
                extractor_type="omr_vision",
                source_location=f"Box {cb.position_box}",
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        doc_type = DocumentType.INVOICE if ("invoice_number" in fields or "total_amount" in fields) else DocumentType.UNKNOWN
        if checkboxes and not fields.get("invoice_number"):
            doc_type = DocumentType.CONTRACT

        summary_text = (ocr_text or "")[:500]
        if barcodes:
            summary_text += f"\n[Decoded {len(barcodes)} Barcodes/QRs: {', '.join(b.format.value for b in barcodes)}]"

        return ExtractionResult(
            document_id=document_id,
            filename=filename,
            classification=ClassificationResult(
                document_type=doc_type,
                confidence=0.90 if barcodes or fields else 0.5,
                classifier_type="vision_ocr",
                matched_features=[b.format.value for b in barcodes],
            ),
            fields=fields,
            tables=[],
            raw_text_summary=summary_text if summary_text else None,
            processing_time_ms=round(elapsed_ms, 2),
        )

    def decode_barcodes(self, image_np: np.ndarray) -> List[BarcodeItem]:
        """Decodes 1D and 2D barcodes (QR, DataMatrix, Code 128, EAN) using zxingcpp and pyzbar."""
        results: List[BarcodeItem] = []
        seen_payloads = set()

        # 1. Try zxingcpp first (fast and robust C++ implementation)
        if zxingcpp is not None:
            try:
                # Ensure 2D grayscale or RGB
                if len(image_np.shape) == 3 and image_np.shape[2] == 4:
                    conv_img = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR) if cv2 else image_np[:, :, :3]
                else:
                    conv_img = image_np

                zxing_barcodes = zxingcpp.read_barcodes(conv_img)
                for b in zxing_barcodes:
                    raw_text = b.text.strip() if b.text else ""
                    if not raw_text or raw_text in seen_payloads:
                        continue
                    seen_payloads.add(raw_text)

                    fmt_str = str(b.format).split(".")[-1].upper()
                    barcode_fmt = self._map_barcode_format(fmt_str)
                    parsed_type, metadata = self._parse_barcode_payload(raw_text)

                    results.append(
                        BarcodeItem(
                            format=barcode_fmt,
                            raw_payload=raw_text,
                            parsed_type=parsed_type,
                            metadata=metadata,
                        )
                    )
            except Exception:
                pass

        # 2. Fallback or augment with pyzbar
        if pyzbar is not None and not results:
            try:
                pyz_barcodes = pyzbar.decode(image_np)
                for b in pyz_barcodes:
                    raw_text = b.data.decode("utf-8", errors="ignore").strip()
                    if not raw_text or raw_text in seen_payloads:
                        continue
                    seen_payloads.add(raw_text)

                    barcode_fmt = self._map_barcode_format(b.type.upper())
                    parsed_type, metadata = self._parse_barcode_payload(raw_text)
                    rect = [b.rect.left, b.rect.top, b.rect.width, b.rect.height]

                    results.append(
                        BarcodeItem(
                            format=barcode_fmt,
                            raw_payload=raw_text,
                            position_box=rect,
                            parsed_type=parsed_type,
                            metadata=metadata,
                        )
                    )
            except Exception:
                pass

        return results

    def detect_checkboxes(
        self,
        image_np: np.ndarray,
        min_size: int = 14,
        max_size: int = 70,
        fill_threshold: float = 0.28,
    ) -> List[CheckboxItem]:
        """Detects square checkboxes and determines if they are checked using OMR pixel density analysis."""
        if cv2 is None:
            return []

        checkboxes: List[CheckboxItem] = []
        try:
            if len(image_np.shape) == 3:
                gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_np

            # Binarize image
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            box_count = 0

            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / float(h)

                # Check if contour resembles a square checkbox box
                if min_size <= w <= max_size and min_size <= h <= max_size and 0.80 <= aspect_ratio <= 1.25:
                    box_count += 1
                    # Examine inner 60% of the box to avoid contour border pixels
                    pad_x = int(w * 0.20)
                    pad_y = int(h * 0.20)
                    roi = binary[y + pad_y : y + h - pad_y, x + pad_x : x + w - pad_x]

                    if roi.size == 0:
                        continue

                    dark_pixels = cv2.countNonZero(roi)
                    total_pixels = roi.size
                    fill_ratio = round(float(dark_pixels) / float(total_pixels), 2)

                    is_checked = fill_ratio >= fill_threshold
                    confidence = 0.95 if abs(fill_ratio - fill_threshold) > 0.10 else 0.75

                    checkboxes.append(
                        CheckboxItem(
                            checkbox_id=f"cb_{box_count}_{x}_{y}",
                            position_box=[int(x), int(y), int(w), int(h)],
                            is_checked=is_checked,
                            confidence=confidence,
                            fill_ratio=fill_ratio,
                        )
                    )
        except Exception:
            pass

        return checkboxes

    def dewarp_document(self, image_np: np.ndarray) -> Tuple[np.ndarray, DewarpInfo]:
        """Corrects skewed perspective from mobile document photos using 4-point contour transform."""
        if cv2 is None:
            return image_np, DewarpInfo(applied=False)

        h, w = image_np.shape[:2]
        orig_dims = [int(w), int(h)]

        try:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY) if len(image_np.shape) == 3 else image_np
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 200)

            contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

            doc_contour = None
            for c in contours:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4 and cv2.contourArea(c) > (w * h * 0.20):
                    doc_contour = approx.reshape(4, 2)
                    break

            if doc_contour is None:
                return image_np, DewarpInfo(applied=False, original_dimensions=orig_dims)

            # Order points: TL, TR, BR, BL
            rect = self._order_points(doc_contour)
            (tl, tr, br, bl) = rect

            width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            max_w = max(int(width_a), int(width_b))

            height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            max_h = max(int(height_a), int(height_b))

            dst = np.array(
                [[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]],
                dtype="float32",
            )

            m = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image_np, m, (max_w, max_h))

            info = DewarpInfo(
                applied=True,
                original_dimensions=orig_dims,
                warped_dimensions=[int(max_w), int(max_h)],
                corners=rect.astype(int).tolist(),
            )
            return warped, info

        except Exception:
            return image_np, DewarpInfo(applied=False, original_dimensions=orig_dims)

    def extract_ocr_text(self, image_np: np.ndarray, lang: str = "spa+eng") -> Optional[str]:
        """Extracts text via pytesseract with graceful fallback if tesseract binary is not installed."""
        if pytesseract is None:
            return None

        try:
            pil_img = Image.fromarray(image_np)
            text = pytesseract.image_to_string(pil_img, lang=lang)
            clean_text = text.strip()
            return clean_text if clean_text else None
        except Exception:
            # Pytesseract may fail if tesseract-ocr executable is not in PATH
            return None

    def _to_numpy_image(self, file_input: Union[str, Path, bytes, BinaryIO, np.ndarray, Image.Image]) -> Optional[np.ndarray]:
        """Converts diverse image input formats into a standardized OpenCV BGR numpy array."""
        if isinstance(file_input, np.ndarray):
            return file_input

        if isinstance(file_input, Image.Image):
            return np.array(file_input)

        raw_bytes = None
        if isinstance(file_input, bytes):
            raw_bytes = file_input
        elif isinstance(file_input, (str, Path)):
            with open(file_input, "rb") as f:
                raw_bytes = f.read()
        elif hasattr(file_input, "read"):
            raw_bytes = file_input.read()

        if raw_bytes and cv2 is not None:
            nparr = np.frombuffer(raw_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img

        if raw_bytes:
            pil_img = Image.open(io.BytesIO(raw_bytes))
            return np.array(pil_img)

        return None

    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Orders 4 coordinates: [top-left, top-right, bottom-right, bottom-left]."""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def _map_barcode_format(self, fmt: str) -> BarcodeFormat:
        f_up = fmt.upper().replace("-", "_")
        for member in BarcodeFormat:
            if member.value in f_up or f_up in member.value:
                return member
        return BarcodeFormat.UNKNOWN

    def _parse_barcode_payload(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extracts structured fiscal and financial metadata from QR/barcode payload strings."""
        meta: Dict[str, Any] = {}

        # 1. TicketBAI / Veri*factu QR (URL format)
        if "tbai" in text.lower() or "verifactu" in text.lower() or "sede.agenciatributaria.gob.es" in text.lower():
            parsed_url = urllib.parse.urlparse(text)
            params = urllib.parse.parse_qs(parsed_url.query)
            for k, v in params.items():
                k_low = k.lower()
                val = v[0] if v else ""
                if k_low in ("nif", "emisor", "cif"):
                    meta["nif"] = val
                elif k_low in ("num", "numero", "factura", "series"):
                    meta["invoice_number"] = val
                elif k_low in ("imp", "importe", "total"):
                    try:
                        meta["total_amount"] = float(val.replace(",", "."))
                    except ValueError:
                        meta["total_amount"] = val
                elif k_low in ("crc", "signature", "hash"):
                    meta["fiscal_hash"] = val
            return "ticketbai_verifactu", meta

        # 2. SEPA EPC QR format (BCD\n002\n...)
        if text.startswith("BCD\n") or text.startswith("BCD\r\n") or "SCT\n" in text:
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            for line in lines:
                if line.startswith("ES") and len(line) >= 20:
                    meta["iban"] = line
                elif re.match(r"^EUR\d+", line):
                    try:
                        meta["total_amount"] = float(line.replace("EUR", "").replace(",", "."))
                    except ValueError:
                        pass
            return "sepa_epc", meta

        # 3. Key-Value pair format: key=val;key2=val2
        if "=" in text and (";" in text or "&" in text):
            delimiter = ";" if ";" in text else "&"
            pairs = text.split(delimiter)
            for pair in pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    meta[k.strip().lower()] = v.strip()
            return "key_value", meta

        return "plain_text", meta
