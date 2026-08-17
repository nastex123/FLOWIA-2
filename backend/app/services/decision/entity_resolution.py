"""Entity Resolution Engine for fuzzy matching, canonical deduplication and vendor entity linking."""

import re
from typing import Any, Dict, List, Optional, Tuple
from rapidfuzz import fuzz

from app.domain.decision_models import (
    EntityMatchResult,
    EntityResolutionAction,
)


class EntityResolutionEngine:
    """Unifies supplier and client variants into canonical business entities."""

    LEGAL_SUFFIXES = [
        r"\bs\.l\.u\.\b",
        r"\bs\.a\.u\.\b",
        r"\bs\.l\.\b",
        r"\bs\.a\.\b",
        r"\bs\.r\.l\.\b",
        r"\bcorp\b",
        r"\bcorporation\b",
        r"\binc\b",
        r"\bincorporated\b",
        r"\bllc\b",
        r"\bgmbh\b",
        r"\bsociedad limitada\b",
        r"\bsociedad anonima\b",
    ]

    def __init__(
        self,
        auto_merge_threshold: float = 0.85,
        review_threshold: float = 0.60,
    ):
        self.auto_merge_threshold = auto_merge_threshold
        self.review_threshold = review_threshold

    def clean_tax_id(self, tax_id: Optional[str]) -> str:
        if not tax_id:
            return ""
        return re.sub(r"[\s\-\.]", "", tax_id).upper().strip()

    def clean_name(self, name: Optional[str]) -> str:
        if not name:
            return ""
        s = name.lower().strip()
        for suffix in self.LEGAL_SUFFIXES:
            s = re.sub(suffix, "", s, flags=re.IGNORECASE)
        s = re.sub(r"[^\w\s]", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    def clean_iban(self, iban: Optional[str]) -> str:
        if not iban:
            return ""
        return re.sub(r"[\s\-\.]", "", iban).upper().strip()

    def calculate_match_score(
        self,
        query: Dict[str, Any],
        candidate: Dict[str, Any],
    ) -> Tuple[float, Dict[str, float], List[str]]:
        """Calculates a weighted confidence score between a query record and a candidate entity."""
        score = 0.0
        features: Dict[str, float] = {}
        reasons: List[str] = []

        q_tax = self.clean_tax_id(query.get("tax_id"))
        c_tax = self.clean_tax_id(candidate.get("tax_id"))
        if q_tax and c_tax:
            if q_tax == c_tax:
                score += 0.45
                features["tax_id"] = 1.0
                reasons.append(f"Coincidencia exacta de NIF/CIF ({q_tax})")
            else:
                features["tax_id"] = 0.0

        q_name = self.clean_name(query.get("name"))
        c_name = self.clean_name(candidate.get("name"))
        if q_name and c_name:
            if q_name == c_name:
                name_sim = 1.0
            else:
                name_sim = fuzz.token_sort_ratio(q_name, c_name) / 100.0
            features["name"] = round(name_sim, 2)
            score += round(0.25 * name_sim, 2)
            if name_sim >= 0.80:
                reasons.append(f"Similitud de razón social ({int(name_sim * 100)}%)")

        q_iban = self.clean_iban(query.get("iban"))
        c_ibans = [self.clean_iban(ib) for ib in candidate.get("ibans", []) if ib]
        if q_iban and c_ibans:
            if q_iban in c_ibans:
                score += 0.15
                features["iban"] = 1.0
                reasons.append("IBAN coincide con histórico de cuentas")
            else:
                features["iban"] = 0.0

        q_domain = (query.get("email_domain") or "").lower().strip()
        c_domain = (candidate.get("email_domain") or "").lower().strip()
        if q_domain and c_domain:
            if q_domain == c_domain and q_domain not in ("gmail.com", "outlook.com", "hotmail.com", "yahoo.com"):
                score += 0.10
                features["domain"] = 1.0
                reasons.append(f"Dominio corporativo común (@{q_domain})")
            else:
                features["domain"] = 0.0

        q_phone = re.sub(r"\D", "", query.get("phone") or "")
        c_phone = re.sub(r"\D", "", candidate.get("phone") or "")
        if q_phone and c_phone and len(q_phone) >= 7 and len(c_phone) >= 7:
            if q_phone == c_phone or q_phone.endswith(c_phone) or c_phone.endswith(q_phone):
                score += 0.05
                features["phone"] = 1.0
                reasons.append("Teléfono de contacto coincide")
            else:
                features["phone"] = 0.0

        # Normalization bonus if tax_id matched exactly and name was high
        if features.get("tax_id") == 1.0 and features.get("name", 0.0) >= 0.70:
            score = max(score, 0.95)

        score = min(1.0, round(score, 2))
        return score, features, reasons

    def resolve(
        self,
        query: Dict[str, Any],
        known_entities: List[Dict[str, Any]],
    ) -> EntityMatchResult:
        """Finds the best matching canonical entity for a query record."""
        if not known_entities:
            return EntityMatchResult(
                action=EntityResolutionAction.CREATE_NEW,
                confidence_score=0.0,
                reasons=["No hay entidades históricas registradas"],
            )

        best_score = 0.0
        best_candidate: Optional[Dict[str, Any]] = None
        best_features: Dict[str, float] = {}
        best_reasons: List[str] = []

        for candidate in known_entities:
            score, feats, reasons = self.calculate_match_score(query, candidate)
            if score > best_score:
                best_score = score
                best_candidate = candidate
                best_features = feats
                best_reasons = reasons

        if not best_candidate or best_score < self.review_threshold:
            return EntityMatchResult(
                action=EntityResolutionAction.CREATE_NEW,
                confidence_score=best_score,
                matched_features=best_features,
                reasons=best_reasons or ["Sin coincidencias significativas con entidades conocidas"],
            )

        if best_score >= self.auto_merge_threshold:
            action = EntityResolutionAction.AUTO_MERGE
        else:
            action = EntityResolutionAction.FLAG_FOR_REVIEW

        return EntityMatchResult(
            entity_id=best_candidate.get("id"),
            canonical_name=best_candidate.get("name"),
            confidence_score=best_score,
            action=action,
            matched_features=best_features,
            reasons=best_reasons,
        )
