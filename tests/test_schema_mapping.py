"""Tests for Schema Definition, Fuzzy Column Auto-Mapping, and Normalization."""

import pytest
from app.services.mapping.schema_normalizer import SchemaNormalizer
from app.infrastructure.presets import DEFAULT_SCHEMA_PRESETS


@pytest.fixture
def normalizer():
    return SchemaNormalizer()


def test_auto_suggest_mappings(normalizer):
    inventory_preset = next(p for p in DEFAULT_SCHEMA_PRESETS if p["id"] == "preset-inventory-std")
    fields = inventory_preset["fields_config_json"]

    source_cols = [
        "Cod_Articulo",
        "Descripcion_Producto",
        "Familia_Art",
        "Stock_Disponible",
        "Precio_Coste (€)",
        "Pasillo_Rack",
    ]

    suggestions = normalizer.auto_suggest_mappings(
        source_columns=source_cols,
        schema_fields=fields,
    )

    mapping_dict = {s["target_field"]: s["suggested_source_column"] for s in suggestions}

    assert mapping_dict["sku"] == "Cod_Articulo"
    assert mapping_dict["product_name"] == "Descripcion_Producto"
    assert mapping_dict["category"] == "Familia_Art"
    assert mapping_dict["stock_units"] == "Stock_Disponible"
    assert mapping_dict["unit_cost"] == "Precio_Coste (€)"
    assert mapping_dict["location"] == "Pasillo_Rack"


def test_normalize_values_currency_and_numbers(normalizer):
    val, err = normalizer.normalize_value(" 1.450,75 € ", "number")
    assert err is None
    assert val == 1450.75

    val2, err2 = normalizer.normalize_value("$99.90", "number")
    assert err2 is None
    assert val2 == 99.90


def test_normalize_values_dates(normalizer):
    val, err = normalizer.normalize_value("18/06/2024", "date")
    assert err is None
    assert val == "2024-06-18"

    val2, err2 = normalizer.normalize_value("2024-12-31", "date")
    assert err2 is None
    assert val2 == "2024-12-31"


def test_normalize_records_with_validation_errors(normalizer):
    schema_fields = [
        {"name": "sku", "label": "SKU", "data_type": "string", "required": True},
        {"name": "price", "label": "Precio", "data_type": "number", "required": True},
    ]

    raw_data = [
        {"Cod": "SKU-1", "Importe": "25.50 €"},
        {"Cod": None, "Importe": "10.00 €"},  # Missing required SKU
    ]

    col_map = {"sku": "Cod", "price": "Importe"}

    norm_rows, errors = normalizer.normalize_records(raw_data, col_map, schema_fields)

    assert len(norm_rows) == 2
    assert norm_rows[0]["sku"] == "SKU-1"
    assert norm_rows[0]["price"] == 25.50
    assert len(errors) >= 1
    assert errors[0]["field"] == "sku"


@pytest.mark.asyncio
async def test_schemas_api_endpoints(auth_client):
    # 1. List pre-seeded schemas
    res = await auth_client.get("/api/v1/schemas")
    assert res.status_code == 200
    schemas = res.json()
    assert len(schemas) >= 4

    # 2. Create custom schema
    payload = {
        "name": "Custom ERP Catalog",
        "description": "Test schema for catalog items",
        "document_type": "inventory",
        "fields": [
            {
                "name": "item_code",
                "label": "Código Artículo",
                "data_type": "string",
                "required": True,
                "aliases": ["cod", "referencia"],
            },
            {
                "name": "pvp",
                "label": "PVP Recomendado (€)",
                "data_type": "number",
                "required": False,
                "aliases": ["precio", "pvp"],
            },
        ],
    }
    res_create = await auth_client.post("/api/v1/schemas", json=payload)
    assert res_create.status_code == 201
    created = res_create.json()
    schema_id = created["id"]
    assert created["name"] == "Custom ERP Catalog"

    # 3. Get schema detail
    res_get = await auth_client.get(f"/api/v1/schemas/{schema_id}")
    assert res_get.status_code == 200
    assert len(res_get.json()["fields"]) == 2

    # 4. Delete custom schema
    res_del = await auth_client.delete(f"/api/v1/schemas/{schema_id}")
    assert res_del.status_code == 200
