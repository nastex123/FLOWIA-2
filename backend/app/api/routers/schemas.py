"""Schema definitions CRUD endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthContext, require_roles, resolve_auth
from app.domain.schema_models import SchemaCreate, SchemaResponse, SchemaUpdate
from app.infrastructure.database import get_db
from app.infrastructure.models import SchemaDefinition, UserRole

router = APIRouter(prefix="/api/v1/schemas", tags=["Schemas"])


def _to_response(s: SchemaDefinition) -> SchemaResponse:
    return SchemaResponse(
        id=s.id,
        organization_id=s.organization_id,
        name=s.name,
        description=s.description,
        document_type=s.document_type,
        fields=s.fields_config_json,
        created_at=s.created_at.isoformat(),
        updated_at=s.updated_at.isoformat(),
    )


@router.get(
    "",
    response_model=List[SchemaResponse],
)
async def list_schemas(
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Lists all active schema definitions for the organization (including standard presets)."""
    stmt = (
        select(SchemaDefinition)
        .where(
            (SchemaDefinition.organization_id == auth.org_id)
            | (SchemaDefinition.organization_id == "default-org")
        )
        .order_by(SchemaDefinition.created_at.asc())
    )
    result = await db.execute(stmt)
    schemas = result.scalars().all()
    return [_to_response(s) for s in schemas]


@router.post(
    "",
    response_model=SchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schema(
    schema_in: SchemaCreate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new canonical data schema for an organization."""
    import uuid

    fields_data = [f.model_dump() for f in schema_in.fields]
    schema_id = str(uuid.uuid4())

    new_schema = SchemaDefinition(
        id=schema_id,
        organization_id=auth.org_id,
        name=schema_in.name,
        description=schema_in.description,
        document_type=schema_in.document_type,
        fields_config_json=fields_data,
    )
    db.add(new_schema)
    await db.commit()
    await db.refresh(new_schema)
    return _to_response(new_schema)


@router.get(
    "/{schema_id}",
    response_model=SchemaResponse,
)
async def get_schema_detail(
    schema_id: str,
    auth: AuthContext = Depends(resolve_auth),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a specific schema definition."""
    stmt = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        (SchemaDefinition.organization_id == auth.org_id)
        | (SchemaDefinition.organization_id == "default-org"),
    )
    result = await db.execute(stmt)
    schema_def = result.scalar_one_or_none()

    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{schema_id}' not found.",
        )
    return _to_response(schema_def)


@router.put(
    "/{schema_id}",
    response_model=SchemaResponse,
)
async def update_schema(
    schema_id: str,
    schema_in: SchemaUpdate,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Updates a custom schema definition."""
    stmt = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        SchemaDefinition.organization_id == auth.org_id,
    )
    result = await db.execute(stmt)
    schema_def = result.scalar_one_or_none()
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{schema_id}' not found.",
        )

    updates = schema_in.model_dump(exclude_unset=True)
    if "fields" in updates and updates["fields"] is not None:
        schema_def.fields_config_json = [f.model_dump() for f in updates.pop("fields")]
    for key, value in updates.items():
        setattr(schema_def, key, value)
    await db.commit()
    await db.refresh(schema_def)
    return _to_response(schema_def)


@router.delete(
    "/{schema_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_schema(
    schema_id: str,
    auth: AuthContext = Depends(require_roles(UserRole.ADMIN, UserRole.MEMBER)),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a custom schema definition."""
    stmt = select(SchemaDefinition).where(
        SchemaDefinition.id == schema_id,
        SchemaDefinition.organization_id == auth.org_id,
    )
    result = await db.execute(stmt)
    schema_def = result.scalar_one_or_none()

    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{schema_id}' not found or cannot be deleted.",
        )

    await db.delete(schema_def)
    await db.commit()
    return {"status": "deleted", "schema_id": schema_id}