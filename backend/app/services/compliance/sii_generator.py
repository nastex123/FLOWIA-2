"""Spanish Tax Agency (AEAT) Suministro Inmediato de Información (SII) XML Generator."""

import xml.etree.ElementTree as ET
from app.domain.compliance_models import (
    SIIRegistrationRequest,
    SIIRegistrationResult,
)


class SIIGenerator:
    """Generates official SII XML messages for issued and received invoices."""

    SII_NS = "https://www.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroInformacion.xsd"
    LR_NS = "https://www.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroLR.xsd"

    def generate_sii_xml(self, request: SIIRegistrationRequest) -> SIIRegistrationResult:
        root_tag = "siiLR:SuministroLRFacturasEmitidas" if request.is_issued else "siiLR:SuministroLRFacturasRecibidas"
        
        root = ET.Element(
            root_tag,
            {
                "xmlns:sii": self.SII_NS,
                "xmlns:siiLR": self.LR_NS,
            },
        )

        # 1. Cabecera
        cabecera = ET.SubElement(root, "sii:Cabecera")
        ET.SubElement(cabecera, "sii:TipoComunicacion").text = "A0"  # A0 = Alta

        titular = ET.SubElement(cabecera, "sii:Titular")
        ET.SubElement(titular, "sii:NombreRazon").text = request.emitter_name if request.is_issued else request.counterparty_name
        ET.SubElement(titular, "sii:NIF").text = request.emitter_nif if request.is_issued else request.counterparty_nif

        # 2. RegistroLRFacturas
        registro_tag = "siiLR:RegistroLRFacturasEmitidas" if request.is_issued else "siiLR:RegistroLRFacturasRecibidas"
        registro = ET.SubElement(root, registro_tag)

        periodo_impositivo = ET.SubElement(registro, "sii:PeriodoImpositivo")
        ET.SubElement(periodo_impositivo, "sii:Ejercicio").text = str(request.fiscal_year)
        ET.SubElement(periodo_impositivo, "sii:Periodo").text = request.period

        # 3. IDFactura
        id_factura_tag = "siiLR:IDFactura"
        id_factura = ET.SubElement(registro, id_factura_tag)
        emisor_factura = ET.SubElement(id_factura, "sii:IDEmisorFactura")
        ET.SubElement(emisor_factura, "sii:NIF").text = request.emitter_nif
        ET.SubElement(id_factura, "sii:NumSerieFacturaEmisor").text = request.invoice_number
        ET.SubElement(id_factura, "sii:FechaExpedicionFacturaEmisor").text = request.invoice_date

        # 4. FacturaExpedida / FacturaRecibida
        factura_tag = "siiLR:FacturaExpedida" if request.is_issued else "siiLR:FacturaRecibida"
        factura = ET.SubElement(registro, factura_tag)
        ET.SubElement(factura, "sii:TipoFactura").text = "F1"
        ET.SubElement(factura, "sii:ClaveRegimenEspecialOTrascendencia").text = "01"
        ET.SubElement(factura, "sii:ImporteTotal").text = f"{request.total_amount:.2f}"
        ET.SubElement(factura, "sii:DescripcionOperacion").text = "Prestacion de servicios / Entrega de bienes"

        # Counterparty
        contraparte = ET.SubElement(factura, "sii:Contraparte")
        ET.SubElement(contraparte, "sii:NombreRazon").text = request.counterparty_name if request.is_issued else request.emitter_name
        ET.SubElement(contraparte, "sii:NIF").text = request.counterparty_nif if request.is_issued else request.emitter_nif

        # Tax breakdown (DesgloseIVA)
        tipo_desglose = ET.SubElement(factura, "sii:TipoDesglose")
        desglose_factura = ET.SubElement(tipo_desglose, "sii:DesgloseFactura")
        sujeta = ET.SubElement(desglose_factura, "sii:Sujeta")
        no_exenta = ET.SubElement(sujeta, "sii:NoExenta")
        ET.SubElement(no_exenta, "sii:TipoNoExenta").text = "S1"
        desglose_iva = ET.SubElement(no_exenta, "sii:DesgloseIVA")

        for tb in request.tax_breakdown:
            detalle_iva = ET.SubElement(desglose_iva, "sii:DetalleIVA")
            ET.SubElement(detalle_iva, "sii:TipoImpositivo").text = f"{tb.tax_rate_pct:.2f}"
            ET.SubElement(detalle_iva, "sii:BaseImponible").text = f"{tb.taxable_base:.2f}"
            ET.SubElement(detalle_iva, "sii:CuotaRepercutida").text = f"{tb.tax_quota:.2f}"

        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

        return SIIRegistrationResult(
            is_valid=True,
            message_type=root_tag,
            xml_content=xml_str,
            fields_count=len(request.tax_breakdown) + 6,
        )
