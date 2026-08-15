"""Schema normalization and fuzzy column mapping engine using rapidfuzz."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from rapidfuzz import fuzz


class SchemaNormalizer:
    """Engine to auto-match columns and transform unstructured tabular records into canonical schemas."""

    def auto_suggest_mappings(
        self,
        source_columns: List[str],
        schema_fields: List[Dict[str, Any]],
        threshold: float = 0.45,
    ) -> List[Dict[str, Any]]:
        """Calculates optimal fuzzy matching suggestions between source columns and schema fields."""
        # 1. Compute similarity score for every (field, column) pair
        pair_scores: List[Tuple[float, str, str]] = []

        for field in schema_fields:
            target_name = field.get("name", "")
            target_label = field.get("label", target_name)
            aliases = field.get("aliases", [])
            candidates = [target_name, target_label] + aliases

            for col in source_columns:
                col_clean = col.lower().strip()
                col_normalized = re.sub(r"[_\-\.\(\)\[\]]", " ", col_clean).strip()

                best_col_score = 0.0

                for cand in candidates:
                    cand_clean = cand.lower().strip()
                    cand_normalized = re.sub(r"[_\-\.\(\)\[\]]", " ", cand_clean).strip()

                    # Exact match
                    if col_clean == cand_clean or col_normalized == cand_normalized:
                        best_col_score = max(best_col_score, 1.0)
                        break

                    # Token sort ratio
                    sort_ratio = fuzz.token_sort_ratio(col_normalized, cand_normalized) / 100.0
                    best_col_score = max(best_col_score, sort_ratio)

                    # Substring overlap
                    if cand_clean in col_clean or col_clean in cand_clean:
                        overlap = max(len(cand_clean), len(col_clean))
                        overlap_ratio = min(len(cand_clean), len(col_clean)) / overlap if overlap > 0 else 0
                        best_col_score = max(best_col_score, overlap_ratio * 0.85)

                if best_col_score >= threshold:
                    pair_scores.append((best_col_score, target_name, col))

        # 2. Sort pairs by score descending
        pair_scores.sort(key=lambda x: x[0], reverse=True)

        assigned_fields: Dict[str, Tuple[str, float]] = {}
        assigned_cols = set()

        for score, f_name, col in pair_scores:
            if f_name not in assigned_fields and col not in assigned_cols:
                assigned_fields[f_name] = (col, round(score, 2))
                assigned_cols.add(col)

        # 3. Construct suggestions in original schema order
        suggestions: List[Dict[str, Any]] = []
        for field in schema_fields:
            target_name = field.get("name", "")
            target_label = field.get("label", target_name)
            data_type = field.get("data_type", "string")
            required = field.get("required", False)

            if target_name in assigned_fields:
                col, score = assigned_fields[target_name]
                suggestions.append({
                    "target_field": target_name,
                    "target_label": target_label,
                    "data_type": data_type,
                    "required": required,
                    "suggested_source_column": col,
                    "confidence": score,
                })
            else:
                suggestions.append({
                    "target_field": target_name,
                    "target_label": target_label,
                    "data_type": data_type,
                    "required": required,
                    "suggested_source_column": None,
                    "confidence": 0.0,
                })

        return suggestions

    def normalize_value(self, raw_val: Any, data_type: str) -> Tuple[Any, Optional[str]]:
        """Converts raw cell value into target data type, returning (normalized_value, error_message)."""
        if raw_val is None or raw_val == "":
            return None, None

        if data_type == "number":
            if isinstance(raw_val, (int, float)):
                return raw_val, None
            s = str(raw_val).strip()
            # Remove currency symbols, spaces, and thousand separators
            s = re.sub(r"[$€£¥USD\s]", "", s, flags=re.IGNORECASE)
            # Handle European decimal: 1.250,50 -> 1250.50
            if "," in s and "." in s:
                if s.find(".") < s.find(","):
                    s = s.replace(".", "").replace(",", ".")
                else:
                    s = s.replace(",", "")
            elif "," in s:
                s = s.replace(",", ".")

            try:
                if "." in s:
                    return float(s), None
                return int(s), None
            except ValueError:
                return raw_val, f"No se pudo convertir '{raw_val}' a número."

        elif data_type == "date":
            if isinstance(raw_val, datetime):
                return raw_val.strftime("%Y-%m-%d"), None
            s = str(raw_val).strip()
            # Common date formats: DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD
            date_patterns = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%Y/%m/%d",
                "%d.%m.%Y",
                "%Y%m%d",
            ]
            for fmt in date_patterns:
                try:
                    dt = datetime.strptime(s, fmt)
                    return dt.strftime("%Y-%m-%d"), None
                except ValueError:
                    continue
            return raw_val, f"Formato de fecha no reconocido para '{raw_val}'."

        elif data_type == "boolean":
            if isinstance(raw_val, bool):
                return raw_val, None
            s = str(raw_val).strip().lower()
            if s in ("true", "1", "si", "sí", "yes", "verdadero", "ok"):
                return True, None
            if s in ("false", "0", "no", "falso"):
                return False, None
            return raw_val, f"No se pudo convertir '{raw_val}' a booleano."

        # Default string type
        val_str = str(raw_val).strip()
        # Prevent formula injection
        if val_str.startswith(("=", "+", "-", "@")):
            val_str = f"'{val_str}"
        return val_str, None

    def normalize_records(
        self,
        source_records: List[Dict[str, Any]],
        column_mapping: Dict[str, str],
        schema_fields: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Maps and converts records according to column_mapping and schema definition."""
        normalized_records: List[Dict[str, Any]] = []
        validation_errors: List[Dict[str, Any]] = []

        fields_by_name = {f["name"]: f for f in schema_fields}

        for row_idx, raw_row in enumerate(source_records, 1):
            normalized_row: Dict[str, Any] = {}

            for target_field, source_col in column_mapping.items():
                if not source_col or target_field not in fields_by_name:
                    continue

                field_def = fields_by_name[target_field]
                raw_value = raw_row.get(source_col)

                norm_val, err = self.normalize_value(
                    raw_value, field_def.get("data_type", "string")
                )
                normalized_row[target_field] = norm_val

                if err:
                    validation_errors.append({
                        "row": row_idx,
                        "field": target_field,
                        "raw_value": raw_value,
                        "error": err,
                    })

            # Check required fields
            for field in schema_fields:
                f_name = field.get("name")
                if field.get("required") and (
                    f_name not in normalized_row
                    or normalized_row[f_name] is None
                    or normalized_row[f_name] == ""
                ):
                    validation_errors.append({
                        "row": row_idx,
                        "field": f_name,
                        "error": f"El campo obligatorio '{field.get('label', f_name)}' está vacío.",
                    })

            normalized_records.append(normalized_row)

        return normalized_records, validation_errors
