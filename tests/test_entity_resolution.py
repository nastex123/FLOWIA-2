"""Tests for the Entity Resolution Engine."""

import pytest
from app.domain.decision_models import EntityResolutionAction
from app.services.decision.entity_resolution import EntityResolutionEngine


@pytest.fixture
def sample_known_entities():
    return [
        {
            "id": "ent-100",
            "name": "Iberdrola Clientes S.A.U.",
            "tax_id": "ESA95748375",
            "ibans": ["ES9121000418450200051332"],
            "email_domain": "iberdrola.es",
            "phone": "+34900225235",
        },
        {
            "id": "ent-200",
            "name": "Amazon Web Services EMEA SARL",
            "tax_id": "ESN0012345J",
            "ibans": ["LU123456789012345678"],
            "email_domain": "amazon.com",
            "phone": "+352123456",
        },
    ]


def test_entity_resolution_exact_tax_id_and_fuzzy_name(sample_known_entities):
    resolver = EntityResolutionEngine()
    query = {
        "name": "Iberdrola Clientes",
        "tax_id": "ESA-95748375",  # with hyphen
        "email_domain": "iberdrola.es",
    }

    res = resolver.resolve(query, sample_known_entities)
    assert res.action == EntityResolutionAction.AUTO_MERGE
    assert res.entity_id == "ent-100"
    assert res.canonical_name == "Iberdrola Clientes S.A.U."
    assert res.confidence_score >= 0.90


def test_entity_resolution_name_only_flag_for_review(sample_known_entities):
    resolver = EntityResolutionEngine(review_threshold=0.20)
    query = {
        "name": "Iberdrola Clientes",  # name matches without tax_id
        "email_domain": "iberdrola.es",
    }

    res = resolver.resolve(query, sample_known_entities)
    assert res.entity_id == "ent-100"
    assert res.canonical_name == "Iberdrola Clientes S.A.U."
    assert res.action in (EntityResolutionAction.FLAG_FOR_REVIEW, EntityResolutionAction.AUTO_MERGE)


def test_entity_resolution_unknown_entity_creates_new(sample_known_entities):
    resolver = EntityResolutionEngine()
    query = {
        "name": "Comercializadora Totalmente Desconocida S.L.",
        "tax_id": "ESB99999999",
        "email_domain": "desconocida.com",
    }

    res = resolver.resolve(query, sample_known_entities)
    assert res.action == EntityResolutionAction.CREATE_NEW
    assert res.entity_id is None
    assert res.confidence_score < 0.60
