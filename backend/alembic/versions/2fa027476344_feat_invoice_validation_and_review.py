"""feat: invoice validation and review

Revision ID: 2fa027476344
Revises: 3bfc3f0c7da4
Create Date: 2026-08-20 07:48:36.692114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fa027476344'
down_revision: Union[str, Sequence[str], None] = '3bfc3f0c7da4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'entity_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('ibans_json', sa.JSON(), nullable=False),
        sa.Column('email_domain', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_entity_records_entity_id'), 'entity_records', ['entity_id'], unique=False)
    op.create_index(op.f('ix_entity_records_organization_id'), 'entity_records', ['organization_id'], unique=False)
    op.create_index(op.f('ix_entity_records_tax_id'), 'entity_records', ['tax_id'], unique=False)

    op.create_table(
        'document_checks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('check_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('detail_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_checks_created_at'), 'document_checks', ['created_at'], unique=False)
    op.create_index(op.f('ix_document_checks_document_id'), 'document_checks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_checks_organization_id'), 'document_checks', ['organization_id'], unique=False)
    op.create_index(op.f('ix_document_checks_severity'), 'document_checks', ['severity'], unique=False)
    op.create_index(op.f('ix_document_checks_status'), 'document_checks', ['status'], unique=False)

    op.create_table(
        'invoice_fingerprints',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('fingerprint', sa.String(length=64), nullable=False),
        sa.Column('vendor_tax_id', sa.String(length=50), nullable=True),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('invoice_date', sa.DateTime(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'fingerprint', name='uq_org_invoice_fingerprint')
    )
    op.create_index(op.f('ix_invoice_fingerprints_created_at'), 'invoice_fingerprints', ['created_at'], unique=False)
    op.create_index(op.f('ix_invoice_fingerprints_document_id'), 'invoice_fingerprints', ['document_id'], unique=False)
    op.create_index(op.f('ix_invoice_fingerprints_fingerprint'), 'invoice_fingerprints', ['fingerprint'], unique=False)
    op.create_index(op.f('ix_invoice_fingerprints_organization_id'), 'invoice_fingerprints', ['organization_id'], unique=False)

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('review_status', sa.String(length=20), server_default='unreviewed', nullable=False))
        batch_op.add_column(sa.Column('reviewed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('reviewed_by', sa.String(length=36), nullable=True))
        batch_op.create_index('ix_documents_review_status', ['review_status'], unique=False)
        batch_op.create_foreign_key('fk_documents_reviewed_by_users', 'users', ['reviewed_by'], ['id'])

    with op.batch_alter_table('extraction_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('structured_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('extraction_records', schema=None) as batch_op:
        batch_op.drop_column('structured_json')

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint('fk_documents_reviewed_by_users', type_='foreignkey')
        batch_op.drop_index('ix_documents_review_status')
        batch_op.drop_column('reviewed_by')
        batch_op.drop_column('reviewed_at')
        batch_op.drop_column('review_status')

    op.drop_index(op.f('ix_invoice_fingerprints_organization_id'), table_name='invoice_fingerprints')
    op.drop_index(op.f('ix_invoice_fingerprints_fingerprint'), table_name='invoice_fingerprints')
    op.drop_index(op.f('ix_invoice_fingerprints_document_id'), table_name='invoice_fingerprints')
    op.drop_index(op.f('ix_invoice_fingerprints_created_at'), table_name='invoice_fingerprints')
    op.drop_table('invoice_fingerprints')

    op.drop_index(op.f('ix_document_checks_status'), table_name='document_checks')
    op.drop_index(op.f('ix_document_checks_severity'), table_name='document_checks')
    op.drop_index(op.f('ix_document_checks_organization_id'), table_name='document_checks')
    op.drop_index(op.f('ix_document_checks_document_id'), table_name='document_checks')
    op.drop_index(op.f('ix_document_checks_created_at'), table_name='document_checks')
    op.drop_table('document_checks')

    op.drop_index(op.f('ix_entity_records_tax_id'), table_name='entity_records')
    op.drop_index(op.f('ix_entity_records_organization_id'), table_name='entity_records')
    op.drop_index(op.f('ix_entity_records_entity_id'), table_name='entity_records')
    op.drop_table('entity_records')
