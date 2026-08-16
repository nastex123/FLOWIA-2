"""Deterministic business rule engine for evaluating extracted data against automation rules."""

from typing import Any, Dict, List, Optional, Tuple

from app.domain.automation_models import RuleOperatorEnum


def _coerce_number(value: Any) -> Optional[float]:
    """Tries to coerce a value into a float for numeric comparisons."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            cleaned = value.strip().replace("€", "").replace("$", "").replace(" ", "").replace("\xa0", "")
            # Handle European decimal format: "1.250,50" -> 1250.50
            if "," in cleaned and "." in cleaned:
                if cleaned.rfind(",") > cleaned.rfind("."):
                    cleaned = cleaned.replace(".", "").replace(",", ".")
                else:
                    cleaned = cleaned.replace(",", "")
            elif "," in cleaned:
                cleaned = cleaned.replace(",", ".")
            return float(cleaned)
        except ValueError:
            return None
    return None


def evaluate_rule_value(operator: str, expected: Any, actual: Any) -> bool:
    """Evaluates a single condition value against the operator and expected value."""
    op = RuleOperatorEnum(operator)

    if op == RuleOperatorEnum.IS_EMPTY:
        return actual is None or actual == "" or actual == [] or actual == {}
    if op == RuleOperatorEnum.NOT_EMPTY:
        return not (actual is None or actual == "" or actual == [] or actual == {})

    if actual is None:
        return False

    if op in (RuleOperatorEnum.GT, RuleOperatorEnum.LT, RuleOperatorEnum.GTE, RuleOperatorEnum.LTE):
        left = _coerce_number(actual)
        right = _coerce_number(expected)
        if left is None or right is None:
            return False
        return {
            RuleOperatorEnum.GT: lambda: left > right,
            RuleOperatorEnum.LT: lambda: left < right,
            RuleOperatorEnum.GTE: lambda: left >= right,
            RuleOperatorEnum.LTE: lambda: left <= right,
        }[op]()

    if op == RuleOperatorEnum.EQ:
        return str(actual).lower() == str(expected).lower()

    if op == RuleOperatorEnum.NEQ:
        return str(actual).lower() != str(expected).lower()

    if op == RuleOperatorEnum.CONTAINS:
        return str(expected).lower() in str(actual).lower()

    return False


def evaluate_field_rule(rule: Dict[str, Any], field_value: Any) -> bool:
    """Evaluates a rule against a single field value (extraction event context)."""
    return evaluate_rule_value(
        operator=rule["operator"],
        expected=rule.get("value"),
        actual=field_value,
    )


def evaluate_records_rule(
    rule: Dict[str, Any],
    records: List[Dict[str, Any]],
) -> Tuple[bool, Optional[Any], int]:
    """Evaluates a rule across normalized records.

    Returns (matched, first_matched_value, matched_rows_count).
    """
    field = rule.get("field", "")
    matched_rows = 0
    first_matched_value: Optional[Any] = None

    for row in records:
        actual = row.get(field)
        if evaluate_rule_value(rule["operator"], rule.get("value"), actual):
            matched_rows += 1
            if first_matched_value is None:
                first_matched_value = actual

    return matched_rows > 0, first_matched_value, matched_rows


def extract_field_value(fields: Dict[str, Any], field_name: str) -> Any:
    """Extracts the scalar value of a canonical field from an extraction fields map.

    Fields are stored as ``{key: {"value": ..., "confidence": ..., ...}}``.
    """
    entry = fields.get(field_name)
    if isinstance(entry, dict):
        return entry.get("value")
    return entry