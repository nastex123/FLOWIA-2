"""Tests for RuleClassifier and scikit-learn MLClassifier."""

import pytest
from app.domain.schemas import DocumentType
from app.services.classifiers.ml_classifier import MLClassifier
from app.services.classifiers.rule_classifier import RuleClassifier


def test_rule_classifier():
    classifier = RuleClassifier()

    invoice_text = "Factura de venta CIF B12345678 importe total 500 euros base imponible e IVA"
    res = classifier.classify(invoice_text)
    assert res.document_type == DocumentType.INVOICE
    assert res.confidence > 0.5
    assert "factura" in res.matched_features

    payroll_text = "Nómina de empleados con deducciones de IRPF y líquido a percibir devengos"
    res = classifier.classify(payroll_text)
    assert res.document_type == DocumentType.PAYROLL


def test_ml_classifier():
    classifier = MLClassifier(auto_train=True)
    assert classifier.is_trained

    # Predict an unseen invoice sample
    sample_invoice = "Factura rectificativa nº 500 emitida para abono importe total vencimiento"
    res = classifier.classify(sample_invoice)
    assert res.document_type == DocumentType.INVOICE
    assert res.confidence > 0.0
    assert len(res.matched_features) > 0

    # Predict an unseen payroll sample
    sample_payroll = "Hoja salarial mensual deducción IRPF cotización a la seguridad social"
    res = classifier.classify(sample_payroll)
    assert res.document_type == DocumentType.PAYROLL
