"""initial_schema

Revision ID: bd3726e86063
Revises:
Create Date: 2026-08-02 14:48:19.870
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "bd3726e86063"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.create_table('users',
    sa.Column('email', postgresql.CITEXT(), nullable=True),
    sa.Column('display_name', sa.Text(), nullable=False),
    sa.Column('avatar_object_key', sa.Text(), nullable=True),
    sa.Column('locale', sa.Text(), server_default=sa.text("'en'"), nullable=False),
    sa.Column('time_zone', sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'active'"), nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('active', 'disabled', 'anonymized')", name=op.f('ck_users__ck_users__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_users__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_users__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    comment='Global internal user principal; external subjects live elsewhere.'
    )
    op.create_index('uq_users__email_where_active', 'users', ['email'], unique=True, postgresql_where=sa.text('deleted_at IS NULL AND email IS NOT NULL'))
    op.create_table('ai_providers',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'enabled'"), nullable=False),
    sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('secret_config_ref', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('enabled', 'disabled', 'degraded')", name=op.f('ck_ai_providers__status_values')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_providers__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_providers__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_providers')),
    comment='Extensible global AI provider catalog.'
    )
    op.create_index('uq_ai_providers__code', 'ai_providers', ['code'], unique=True)
    op.create_table('external_identities',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('issuer', sa.Text(), nullable=False),
    sa.Column('subject', sa.Text(), nullable=False),
    sa.Column('provider_code', sa.Text(), nullable=False),
    sa.Column('email_at_link', postgresql.CITEXT(), nullable=True),
    sa.Column('claims_fingerprint', sa.LargeBinary(), nullable=True),
    sa.Column('linked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_external_identities__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_external_identities__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_external_identities__user_id__users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_external_identities')),
    comment='OIDC subject mapping only; no bearer tokens or raw claims.'
    )
    op.create_index('uq_external_identities__issuer_subject', 'external_identities', ['issuer', 'subject'], unique=True)
    op.create_index('uq_external_identities__user_issuer_where_active', 'external_identities', ['user_id', 'issuer'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('notification_types',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('category', sa.Text(), nullable=False),
    sa.Column('default_channels', postgresql.ARRAY(sa.Text()), server_default=sa.text("'{}'::text[]"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("category IN ('transactional','product','security')", name=op.f('ck_notification_types__ck_notification_types__category')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_notification_types__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_notification_types__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notification_types')),
    sa.UniqueConstraint('code', name='uq_notification_types__code'),
    comment='Extensible catalog of notification event kinds and default channels.'
    )
    op.create_table('organizations',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('slug', postgresql.CITEXT(), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'active'"), nullable=False),
    sa.Column('billing_email', postgresql.CITEXT(), nullable=True),
    sa.Column('default_time_zone', sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
    sa.Column('data_region', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('trial', 'active', 'suspended', 'closed')", name=op.f('ck_organizations__ck_organizations__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_organizations__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_organizations__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_organizations')),
    comment='Commercial customer boundary; legal and billing hold aware.'
    )
    op.create_index('uq_organizations__slug_where_active', 'organizations', ['slug'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('permissions',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('module', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('risk_level', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("risk_level IN ('normal', 'sensitive', 'destructive')", name=op.f('ck_permissions__ck_permissions__risk_level')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_permissions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_permissions__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_permissions')),
    sa.UniqueConstraint('code', name='uq_permissions__code'),
    comment='Global stable permission codes; retired only when unreferenced.'
    )
    op.create_table('setting_definitions',
    sa.Column('key', postgresql.CITEXT(), nullable=False),
    sa.Column('value_type', sa.Text(), nullable=False),
    sa.Column('allowed_scopes', postgresql.ARRAY(sa.Text()), nullable=False),
    sa.Column('default_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('validation_schema', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('is_secret', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("value_type IN ('boolean','integer','decimal','string','string_list','object')", name=op.f('ck_setting_definitions__ck_setting_definitions__value_type')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_setting_definitions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_setting_definitions__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_setting_definitions')),
    sa.UniqueConstraint('key', name='uq_setting_definitions__key'),
    comment='Typed setting registry with defaults and validation metadata.'
    )
    op.create_table('social_platforms',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('api_version', sa.Text(), nullable=True),
    sa.Column('capability_metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('enabled','disabled','coming_soon')", name=op.f('ck_social_platforms__ck_social_platforms__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_platforms__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_platforms__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_platforms')),
    comment='Extensible global social publishing platform catalog.'
    )
    op.create_index('uq_social_platforms__code', 'social_platforms', ['code'], unique=True)
    op.create_table('usage_dimensions',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('unit', sa.Text(), nullable=False),
    sa.Column('aggregation', sa.Text(), nullable=False),
    sa.Column('billable', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("aggregation IN ('sum','max','last')", name=op.f('ck_usage_dimensions__ck_usage_dimensions__aggregation')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_usage_dimensions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_usage_dimensions__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usage_dimensions')),
    sa.UniqueConstraint('code', name='uq_usage_dimensions__code'),
    comment='Extensible catalog of metered resources and aggregation semantics.'
    )
    op.create_table('user_sessions',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('session_hash', sa.LargeBinary(), nullable=False),
    sa.Column('provider_session_id_hash', sa.LargeBinary(), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revocation_reason', sa.Text(), nullable=True),
    sa.Column('ip_hash', sa.LargeBinary(), nullable=True),
    sa.Column('user_agent_hash', sa.LargeBinary(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('expires_at > issued_at', name=op.f('ck_user_sessions__ck_user_sessions__expires_after_issued')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_user_sessions__ck_user_sessions__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_user_sessions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_user_sessions__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_sessions__user_id__users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_sessions')),
    comment='Revocable session metadata with hashed identifiers only.'
    )
    op.create_index('ix_user_sessions__user_expires', 'user_sessions', ['user_id', sa.literal_column('expires_at DESC')], unique=False)
    op.create_index('uq_user_sessions__session_hash', 'user_sessions', ['session_hash'], unique=True)
    op.create_table('ai_models',
    sa.Column('provider_id', sa.UUID(), nullable=False),
    sa.Column('model_code', sa.Text(), nullable=False),
    sa.Column('display_name', sa.Text(), nullable=False),
    sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('context_window', sa.Integer(), nullable=True),
    sa.Column('input_cost_per_million', sa.Numeric(precision=20, scale=8), nullable=True),
    sa.Column('output_cost_per_million', sa.Numeric(precision=20, scale=8), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('enabled', 'disabled', 'deprecated')", name=op.f('ck_ai_models__status_values')),
    sa.CheckConstraint('context_window IS NULL OR context_window > 0', name=op.f('ck_ai_models__context_window')),
    sa.CheckConstraint('input_cost_per_million IS NULL OR input_cost_per_million >= 0', name=op.f('ck_ai_models__input_cost_nonnegative')),
    sa.CheckConstraint('output_cost_per_million IS NULL OR output_cost_per_million >= 0', name=op.f('ck_ai_models__output_cost_nonnegative')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_models__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], name=op.f('fk_ai_models__provider_id__ai_providers'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_models__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_models')),
    comment='Provider-specific global AI model catalog.'
    )
    op.create_index('ix_ai_models__provider_status', 'ai_models', ['provider_id', 'status'], unique=False)
    op.create_index('uq_ai_models__provider_model_code', 'ai_models', ['provider_id', 'model_code'], unique=True)
    op.create_table('billing_customers',
    sa.Column('provider_code', sa.Text(), nullable=False),
    sa.Column('external_customer_id', sa.Text(), nullable=False),
    sa.Column('billing_email', postgresql.CITEXT(), nullable=True),
    sa.Column('tax_region', sa.Text(), nullable=True),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('active','delinquent','closed')", name=op.f('ck_billing_customers__ck_billing_customers__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_billing_customers__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_billing_customers__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_billing_customers__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_billing_customers')),
    sa.UniqueConstraint('organization_id', 'id', name='uq_billing_customers__organization_id_id'),
    comment='External billing customer reference without payment instruments.'
    )
    op.create_index(op.f('ix_billing_customers__organization_id'), 'billing_customers', ['organization_id'], unique=False)
    op.create_index('uq_billing_customers__organization_provider_where_active', 'billing_customers', ['organization_id', 'provider_code'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_billing_customers__provider_external', 'billing_customers', ['provider_code', 'external_customer_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('billing_events',
    sa.Column('provider_code', sa.Text(), nullable=False),
    sa.Column('external_event_id', sa.Text(), nullable=False),
    sa.Column('event_type', sa.Text(), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('amount', sa.Numeric(precision=20, scale=8), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('payload_fragment', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('payload_hash', sa.LargeBinary(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('amount IS NULL OR amount >= 0', name=op.f('ck_billing_events__ck_billing_events__amount')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_billing_events__ck_billing_events__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_billing_events__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_billing_events__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_billing_events__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_billing_events')),
    sa.UniqueConstraint('organization_id', 'id', name='uq_billing_events__organization_id_id'),
    comment='Immutable redacted billing webhook and accounting evidence.'
    )
    op.create_index(op.f('ix_billing_events__organization_id'), 'billing_events', ['organization_id'], unique=False)
    op.create_index('ix_billing_events__organization_time', 'billing_events', ['organization_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('uq_billing_events__provider_event', 'billing_events', ['provider_code', 'external_event_id'], unique=True)
    op.create_table('metric_definitions',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('unit', sa.Text(), nullable=False),
    sa.Column('aggregation', sa.Text(), nullable=False),
    sa.Column('value_kind', sa.Text(), nullable=False),
    sa.Column('methodology_version', sa.Integer(), server_default='1', nullable=False),
    sa.Column('platform_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("aggregation IN ('sum','last','max','min','average','ratio')", name=op.f('ck_metric_definitions__ck_metric_definitions__aggregation')),
    sa.CheckConstraint("value_kind IN ('integer','decimal','percentage','currency')", name=op.f('ck_metric_definitions__ck_metric_definitions__value_kind')),
    sa.CheckConstraint('methodology_version > 0', name=op.f('ck_metric_definitions__ck_metric_definitions__methodology_version_positive')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_metric_definitions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['platform_id'], ['social_platforms.id'], name=op.f('fk_metric_definitions__platform_id__social_platforms'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_metric_definitions__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_metric_definitions')),
    sa.UniqueConstraint('code', 'methodology_version', 'platform_id', name='uq_metric_definitions__code_version_platform', postgresql_nulls_not_distinct=True),
    comment='Versioned, extensible semantics for normalized analytics metrics.'
    )
    op.create_table('organization_memberships',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.Text(), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'active'"), nullable=False),
    sa.Column('invited_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("role IN ('owner', 'billing_admin', 'admin', 'member')", name=op.f('ck_organization_memberships__ck_organization_memberships__role')),
    sa.CheckConstraint("status IN ('invited', 'active', 'suspended')", name=op.f('ck_organization_memberships__ck_organization_memberships__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_organization_memberships__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_organization_memberships__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_organization_memberships__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_organization_memberships__user_id__users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_organization_memberships')),
    comment='Organization-level commercial and admin access separate from workspace access.'
    )
    op.create_index(op.f('ix_organization_memberships__organization_id'), 'organization_memberships', ['organization_id'], unique=False)
    op.create_index('ix_organization_memberships__organization_user', 'organization_memberships', ['organization_id', 'user_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_organization_memberships__organization_user_where_active', 'organization_memberships', ['organization_id', 'user_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('social_platform_capabilities',
    sa.Column('platform_id', sa.UUID(), nullable=False),
    sa.Column('capability_code', postgresql.CITEXT(), nullable=False),
    sa.Column('supported', sa.Boolean(), nullable=False),
    sa.Column('limit_value', sa.Numeric(precision=20, scale=6), nullable=True),
    sa.Column('unit', sa.Text(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('effective_from', sa.DateTime(timezone=True), nullable=False),
    sa.Column('effective_to', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('effective_to IS NULL OR effective_to > effective_from', name=op.f('ck_social_platform_capabilities__ck_social_platform_capabilities__effective_interval')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_social_platform_capabilities__ck_social_platform_capabilities__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_platform_capabilities__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['platform_id'], ['social_platforms.id'], name=op.f('fk_social_platform_capabilities__platform_id__social_platforms'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_platform_capabilities__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_platform_capabilities')),
    sa.UniqueConstraint('platform_id', 'capability_code', 'effective_from', name='uq_social_platform_capabilities__platform_code_effective'),
    comment='Immutable versioned social platform capability records.'
    )
    op.create_index('ix_social_platform_capabilities__created_at', 'social_platform_capabilities', ['created_at', 'id'], unique=False)
    op.create_table('subscriptions',
    sa.Column('provider_code', sa.Text(), nullable=False),
    sa.Column('external_subscription_id', sa.Text(), nullable=False),
    sa.Column('plan_code', sa.Text(), nullable=False),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
    sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancel_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('trialing','active','past_due','paused','cancelled','ended')", name=op.f('ck_subscriptions__ck_subscriptions__status')),
    sa.CheckConstraint('current_period_end IS NULL OR current_period_start IS NULL OR current_period_end > current_period_start', name=op.f('ck_subscriptions__ck_subscriptions__current_period')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_subscriptions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_subscriptions__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_subscriptions__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_subscriptions')),
    sa.UniqueConstraint('organization_id', 'id', name='uq_subscriptions__organization_id_id'),
    comment='External subscription mirror; the provider remains billing authority.'
    )
    op.create_index(op.f('ix_subscriptions__organization_id'), 'subscriptions', ['organization_id'], unique=False)
    op.create_index('uq_subscriptions__one_current_org', 'subscriptions', ['organization_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND status IN ('trialing','active','past_due','paused')"))
    op.create_index('uq_subscriptions__provider_external', 'subscriptions', ['provider_code', 'external_subscription_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('workspaces',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('slug', postgresql.CITEXT(), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'active'"), nullable=False),
    sa.Column('time_zone', sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
    sa.Column('retention_policy_days', sa.Integer(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('provisioning', 'active', 'suspended', 'closing', 'closed')", name=op.f('ck_workspaces__ck_workspaces__status')),
    sa.CheckConstraint('retention_policy_days IS NULL OR retention_policy_days > 0', name=op.f('ck_workspaces__ck_workspaces__retention_policy_days')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_workspaces__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_workspaces__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_workspaces__updated_by__users'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_workspaces')),
    sa.UniqueConstraint('id', 'organization_id', name='uq_workspaces__id_organization_id'),
    comment='Operational tenant; application commands must scope here explicitly.'
    )
    op.create_index(op.f('ix_workspaces__organization_id'), 'workspaces', ['organization_id'], unique=False)
    op.create_index('uq_workspaces__organization_slug_where_active', 'workspaces', ['organization_id', 'slug'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('activity_logs',
    sa.Column('actor_id', sa.UUID(), nullable=True),
    sa.Column('activity_type', sa.Text(), nullable=False),
    sa.Column('resource_type', sa.Text(), nullable=True),
    sa.Column('resource_id', sa.UUID(), nullable=True),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('hidden_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], name=op.f('fk_activity_logs__actor_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_activity_logs__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_activity_logs__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_activity_logs__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_activity_logs')),
    comment='User-facing recent activity; not compliance evidence.'
    )
    op.create_index('ix_activity_logs__workspace_cursor', 'activity_logs', ['workspace_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL AND hidden_at IS NULL'))
    op.create_index(op.f('ix_activity_logs__workspace_id'), 'activity_logs', ['workspace_id'], unique=False)
    op.create_table('ai_prompt_templates',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('purpose', sa.Text(), nullable=False),
    sa.Column('template_text', sa.Text(), nullable=False),
    sa.Column('template_version', sa.Integer(), nullable=False),
    sa.Column('input_schema', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('template_version > 0', name=op.f('ck_ai_prompt_templates__ck_ai_prompt_templates__template_version')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_prompt_templates__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_prompt_templates__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_ai_prompt_templates__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_prompt_templates')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_ai_prompt_templates__workspace_id_id'),
    comment='Versioned workspace prompt policy templates.'
    )
    op.create_index(op.f('ix_ai_prompt_templates__workspace_id'), 'ai_prompt_templates', ['workspace_id'], unique=False)
    op.create_index('ix_ai_prompt_templates__workspace_name_version_desc', 'ai_prompt_templates', ['workspace_id', 'name', sa.literal_column('template_version DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('analytics_snapshots',
    sa.Column('snapshot_type', sa.Text(), nullable=False),
    sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('time_zone', sa.Text(), nullable=False),
    sa.Column('dimensions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('fresh_through', sa.DateTime(timezone=True), nullable=False),
    sa.Column('methodology_version', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("snapshot_type IN ('workspace_kpi','platform_comparison','growth_trend','publishing_frequency')", name=op.f('ck_analytics_snapshots__ck_analytics_snapshots__snapshot_type')),
    sa.CheckConstraint('methodology_version > 0', name=op.f('ck_analytics_snapshots__ck_analytics_snapshots__methodology')),
    sa.CheckConstraint('period_end > period_start', name=op.f('ck_analytics_snapshots__ck_analytics_snapshots__period')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_analytics_snapshots__ck_analytics_snapshots__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_analytics_snapshots__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_analytics_snapshots__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_analytics_snapshots__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_analytics_snapshots')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_analytics_snapshots__workspace_id_id'),
    comment='Immutable dashboard aggregate cache with explicit methodology.'
    )
    op.create_index(op.f('ix_analytics_snapshots__workspace_id'), 'analytics_snapshots', ['workspace_id'], unique=False)
    op.create_index('ix_analytics_snapshots__workspace_type_period_end', 'analytics_snapshots', ['workspace_id', 'snapshot_type', sa.literal_column('period_end DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('uq_analytics_snapshots__identity', 'analytics_snapshots', ['workspace_id', 'snapshot_type', 'period_start', 'period_end', 'methodology_version', sa.literal_column('md5(dimensions::text)')], unique=True)
    op.create_table('audit_logs',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('actor_user_id', sa.UUID(), nullable=True),
    sa.Column('actor_type', sa.Text(), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('target_type', sa.Text(), nullable=False),
    sa.Column('target_id', sa.UUID(), nullable=True),
    sa.Column('outcome', sa.Text(), nullable=False),
    sa.Column('source', sa.Text(), nullable=False),
    sa.Column('correlation_id', sa.UUID(), nullable=True),
    sa.Column('request_id', sa.Text(), nullable=True),
    sa.Column('safe_diff', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ip_hash', sa.LargeBinary(), nullable=True),
    sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("actor_type IN ('user','service','system','provider')", name=op.f('ck_audit_logs__audit_logs_actor_type')),
    sa.CheckConstraint("outcome IN ('success','failure','denied')", name=op.f('ck_audit_logs__audit_logs_outcome')),
    sa.CheckConstraint("workspace_id IS NOT NULL OR organization_id IS NOT NULL OR source = 'global'", name=op.f('ck_audit_logs__audit_logs_scope')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_audit_logs__audit_logs_immutable_shape')),
    sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], name=op.f('fk_audit_logs__actor_user_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_audit_logs__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_audit_logs__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_audit_logs__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_audit_logs__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs')),
    comment='Append-only redacted security and compliance evidence.'
    )
    op.create_index('brin_audit_logs__occurred_at', 'audit_logs', ['occurred_at'], unique=False, postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.create_index('ix_audit_logs__organization_time', 'audit_logs', ['organization_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('ix_audit_logs__workspace_time', 'audit_logs', ['workspace_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_table('background_jobs',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('job_type', sa.Text(), nullable=False),
    sa.Column('queue_name', sa.Text(), nullable=False),
    sa.Column('state', sa.Text(), nullable=False),
    sa.Column('resource_type', sa.Text(), nullable=True),
    sa.Column('resource_id', sa.UUID(), nullable=True),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('priority', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('available_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('attempt_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('max_attempts', sa.Integer(), server_default=sa.text('5'), nullable=False),
    sa.Column('lease_owner', sa.Text(), nullable=True),
    sa.Column('leased_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_code', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("queue_name IN ('ai','media','notification','maintenance')", name=op.f('ck_background_jobs__background_jobs_queue_name')),
    sa.CheckConstraint("state IN ('queued','leased','running','retry_wait','succeeded','failed','dead_lettered','cancelled')", name=op.f('ck_background_jobs__background_jobs_state')),
    sa.CheckConstraint('attempt_count <= max_attempts', name=op.f('ck_background_jobs__background_jobs_attempts_within_max')),
    sa.CheckConstraint('attempt_count >= 0', name=op.f('ck_background_jobs__background_jobs_attempt_count_nonnegative')),
    sa.CheckConstraint('max_attempts > 0', name=op.f('ck_background_jobs__background_jobs_max_attempts_positive')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_background_jobs__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_background_jobs__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_background_jobs__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_background_jobs')),
    comment='Durable non-publishing work with bounded retries and leases.'
    )
    op.create_index('ix_background_jobs__claim', 'background_jobs', ['available_at', sa.literal_column('priority DESC'), 'id'], unique=False, postgresql_include=['workspace_id', 'queue_name'], postgresql_where=sa.text("deleted_at IS NULL AND state IN ('queued','retry_wait')"))
    op.create_index('ix_background_jobs__expired_lease', 'background_jobs', ['leased_until', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND state IN ('leased','running')"))
    op.create_index('uq_background_jobs__scope_type_key_where_active', 'background_jobs', ['workspace_id', 'job_type', 'idempotency_key'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('brand_profiles',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('voice_guidelines', sa.Text(), nullable=True),
    sa.Column('audience', sa.Text(), nullable=True),
    sa.Column('default_language', sa.Text(), server_default=sa.text("'en'"), nullable=False),
    sa.Column('style_settings', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('is_default', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_brand_profiles__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_brand_profiles__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_brand_profiles__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_brand_profiles')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_brand_profiles__workspace_id_id'),
    comment='Brand voice guidelines and workspace default settings.'
    )
    op.create_index(op.f('ix_brand_profiles__workspace_id'), 'brand_profiles', ['workspace_id'], unique=False)
    op.create_index('uq_brand_profiles__one_default', 'brand_profiles', ['workspace_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL AND is_default'))
    op.create_index('uq_brand_profiles__workspace_name_where_active', 'brand_profiles', ['workspace_id', 'name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('categories',
    sa.Column('parent_category_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('slug', postgresql.CITEXT(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('parent_category_id IS NULL OR parent_category_id <> id', name=op.f('ck_categories__ck_categories__parent_not_self')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_categories__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_categories__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'parent_category_id'], ['categories.workspace_id', 'categories.id'], name='fk_categories__parent', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_categories__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_categories__workspace_id_id'),
    comment='Controlled hierarchical taxonomy within a workspace.'
    )
    op.create_index(op.f('ix_categories__workspace_id'), 'categories', ['workspace_id'], unique=False)
    op.create_index('ix_categories__workspace_parent', 'categories', ['workspace_id', 'parent_category_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_categories__workspace_slug_where_active', 'categories', ['workspace_id', 'slug'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('collections',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('visibility', sa.Text(), server_default=sa.text("'workspace'"), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("visibility IN ('private', 'workspace')", name=op.f('ck_collections__ck_collections__visibility')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_collections__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_collections__owner_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_collections__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_collections__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_collections')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_collections__workspace_id_id'),
    comment='Curated ordered content sets within a workspace.'
    )
    op.create_index(op.f('ix_collections__workspace_id'), 'collections', ['workspace_id'], unique=False)
    op.create_index('ix_collections__workspace_updated_cursor', 'collections', ['workspace_id', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_collections__workspace_name_where_active', 'collections', ['workspace_id', 'name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('dead_letters',
    sa.Column('source_type', sa.Text(), nullable=False),
    sa.Column('source_id', sa.UUID(), nullable=False),
    sa.Column('reason_code', sa.Text(), nullable=False),
    sa.Column('reason_message', sa.Text(), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('failed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('replay_state', sa.Text(), server_default=sa.text("'pending'"), nullable=False),
    sa.Column('replayed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("replay_state IN ('pending','replayed','discarded')", name=op.f('ck_dead_letters__ck_dead_letters__replay_state')),
    sa.CheckConstraint("source_type IN ('publishing_job','notification','outbox','webhook','background_job')", name=op.f('ck_dead_letters__ck_dead_letters__source_type')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_dead_letters__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_dead_letters__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_dead_letters__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_dead_letters')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_dead_letters__workspace_id_id'),
    comment='Terminal failed work with redacted payload and replay control.'
    )
    op.create_index(op.f('ix_dead_letters__workspace_id'), 'dead_letters', ['workspace_id'], unique=False)
    op.create_index('ix_dead_letters__workspace_pending', 'dead_letters', ['workspace_id', 'failed_at', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND replay_state = 'pending'"))
    op.create_index('uq_dead_letters__workspace_source_where_active', 'dead_letters', ['workspace_id', 'source_type', 'source_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('folders',
    sa.Column('parent_folder_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('path_cache', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('parent_folder_id IS NULL OR parent_folder_id <> id', name=op.f('ck_folders__ck_folders__parent_not_self')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_folders__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_folders__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'parent_folder_id'], ['folders.workspace_id', 'folders.id'], name='fk_folders__parent', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_folders__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_folders')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_folders__workspace_id_id'),
    comment='Hierarchical content folder tree within a workspace.'
    )
    op.create_index(op.f('ix_folders__workspace_id'), 'folders', ['workspace_id'], unique=False)
    op.create_index('ix_folders__workspace_parent_name', 'folders', ['workspace_id', 'parent_folder_id', 'name'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('idempotency_keys',
    sa.Column('principal_id', sa.UUID(), nullable=True),
    sa.Column('key', sa.Text(), nullable=False),
    sa.Column('operation', sa.Text(), nullable=False),
    sa.Column('request_hash', sa.LargeBinary(), nullable=False),
    sa.Column('state', sa.Text(), nullable=False),
    sa.Column('response_status', sa.Integer(), nullable=True),
    sa.Column('response_headers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('response_body_ref', sa.Text(), nullable=True),
    sa.Column('locked_until', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("state IN ('processing','completed','failed')", name=op.f('ck_idempotency_keys__idempotency_keys_state')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_idempotency_keys__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_idempotency_keys__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_idempotency_keys__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_idempotency_keys')),
    comment='Short-lived request deduplication and response replay state.'
    )
    op.create_index('ix_idempotency_keys__expiry', 'idempotency_keys', ['expires_at', 'id'], unique=False)
    op.create_index(op.f('ix_idempotency_keys__workspace_id'), 'idempotency_keys', ['workspace_id'], unique=False)
    op.create_index('uq_idempotency_keys__scope_principal_operation_key_where_active', 'idempotency_keys', ['workspace_id', 'principal_id', 'operation', 'key'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('inbox_messages',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('consumer_name', sa.Text(), nullable=False),
    sa.Column('message_id', sa.UUID(), nullable=False),
    sa.Column('event_type', sa.Text(), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('outcome', sa.Text(), nullable=True),
    sa.Column('payload_hash', sa.LargeBinary(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("outcome IS NULL OR outcome IN ('processed','ignored','failed')", name=op.f('ck_inbox_messages__inbox_messages_outcome')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_inbox_messages__inbox_messages_immutable_shape')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_inbox_messages__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_inbox_messages__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_inbox_messages__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_inbox_messages')),
    comment='Immutable at-least-once consumer deduplication evidence.'
    )
    op.create_index('ix_inbox_messages__retention', 'inbox_messages', ['processed_at', 'id'], unique=False, postgresql_where=sa.text('processed_at IS NOT NULL'))
    op.create_index('uq_inbox_messages__consumer_message', 'inbox_messages', ['consumer_name', 'message_id'], unique=True)
    op.create_table('notification_preferences',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('notification_type_id', sa.UUID(), nullable=False),
    sa.Column('channel', sa.Text(), nullable=False),
    sa.Column('enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('quiet_hours_start', sa.Time(), nullable=True),
    sa.Column('quiet_hours_end', sa.Time(), nullable=True),
    sa.Column('time_zone', sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("channel IN ('in_app','email','webhook')", name=op.f('ck_notification_preferences__ck_notification_preferences__channel')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_notification_preferences__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['notification_type_id'], ['notification_types.id'], name=op.f('fk_notification_preferences__notification_type_id__notification_types'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_notification_preferences__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notification_preferences__user_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_notification_preferences__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notification_preferences')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_notification_preferences__workspace_id_id'),
    comment='Recipient channel preferences scoped to workspace and notification type.'
    )
    op.create_index(op.f('ix_notification_preferences__workspace_id'), 'notification_preferences', ['workspace_id'], unique=False)
    op.create_index('uq_notification_preferences__workspace_user_type_channel_where_active', 'notification_preferences', ['workspace_id', 'user_id', 'notification_type_id', 'channel'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('notification_templates',
    sa.Column('notification_type_id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('channel', sa.Text(), nullable=False),
    sa.Column('locale', sa.Text(), server_default=sa.text("'en'"), nullable=False),
    sa.Column('template_version', sa.Integer(), nullable=False),
    sa.Column('subject_template', sa.Text(), nullable=True),
    sa.Column('body_template', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("channel IN ('in_app','email','webhook')", name=op.f('ck_notification_templates__ck_notification_templates__channel')),
    sa.CheckConstraint('template_version > 0', name=op.f('ck_notification_templates__ck_notification_templates__template_version')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_notification_templates__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['notification_type_id'], ['notification_types.id'], name=op.f('fk_notification_templates__notification_type_id__notification_types'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_notification_templates__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_notification_templates__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notification_templates')),
    comment='Global or workspace-scoped localized notification rendering templates.'
    )
    op.create_index('ix_notification_templates__active_lookup', 'notification_templates', ['notification_type_id', 'channel', 'locale', 'is_active'], unique=False, postgresql_where=sa.text('deleted_at IS NULL AND is_active'))
    op.create_index('uq_notification_templates__global_type_channel_locale_version', 'notification_templates', ['notification_type_id', 'channel', 'locale', 'template_version'], unique=True, postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NULL'))
    op.create_index('uq_notification_templates__workspace_type_channel_locale_version', 'notification_templates', ['workspace_id', 'notification_type_id', 'channel', 'locale', 'template_version'], unique=True, postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NOT NULL'))
    op.create_table('notifications',
    sa.Column('notification_type_id', sa.UUID(), nullable=False),
    sa.Column('recipient_user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('severity', sa.Text(), nullable=False),
    sa.Column('resource_type', sa.Text(), nullable=True),
    sa.Column('resource_id', sa.UUID(), nullable=True),
    sa.Column('dedupe_key', sa.Text(), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("severity IN ('info','success','warning','error')", name=op.f('ck_notifications__ck_notifications__severity')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_notifications__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['notification_type_id'], ['notification_types.id'], name=op.f('fk_notifications__notification_type_id__notification_types'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['recipient_user_id'], ['users.id'], name=op.f('fk_notifications__recipient_user_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_notifications__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_notifications__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_notifications__workspace_id_id'),
    comment='User-visible notification instances with deduplicated inbox semantics.'
    )
    op.create_index(op.f('ix_notifications__workspace_id'), 'notifications', ['workspace_id'], unique=False)
    op.create_index('ix_notifications__workspace_recipient_cursor', 'notifications', ['workspace_id', 'recipient_user_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('ix_notifications__workspace_recipient_unread', 'notifications', ['workspace_id', 'recipient_user_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL AND read_at IS NULL'))
    op.create_index('uq_notifications__workspace_recipient_dedupe_where_active', 'notifications', ['workspace_id', 'recipient_user_id', 'dedupe_key'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('outbox_events',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('aggregate_type', sa.Text(), nullable=False),
    sa.Column('aggregate_id', sa.UUID(), nullable=False),
    sa.Column('event_type', sa.Text(), nullable=False),
    sa.Column('event_version', sa.Integer(), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('headers', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('available_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('attempt_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('last_error', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("workspace_id IS NOT NULL OR organization_id IS NOT NULL OR aggregate_type = 'global'", name=op.f('ck_outbox_events__outbox_events_scope')),
    sa.CheckConstraint('attempt_count >= 0', name=op.f('ck_outbox_events__outbox_events_attempt_count_nonnegative')),
    sa.CheckConstraint('event_version > 0', name=op.f('ck_outbox_events__outbox_events_event_version_positive')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_outbox_events__outbox_events_immutable_shape')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_outbox_events__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_outbox_events__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_outbox_events__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_outbox_events__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_outbox_events')),
    comment='Redacted, versioned transactional integration events.'
    )
    op.create_index('brin_outbox_events__occurred_at', 'outbox_events', ['occurred_at'], unique=False, postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.create_index('ix_outbox_events__aggregate', 'outbox_events', ['aggregate_type', 'aggregate_id', 'occurred_at', 'id'], unique=False)
    op.create_index('ix_outbox_events__publish_due', 'outbox_events', ['available_at', 'id'], unique=False, postgresql_where=sa.text('published_at IS NULL'))
    op.create_table('projects',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('slug', postgresql.CITEXT(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Text(), server_default=sa.text("'active'"), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('starts_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('active', 'archived')", name=op.f('ck_projects__ck_projects__status')),
    sa.CheckConstraint('ends_at IS NULL OR starts_at IS NULL OR ends_at > starts_at', name=op.f('ck_projects__ck_projects__dates')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_projects__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_projects__owner_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_projects__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_projects__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_projects')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_projects__workspace_id_id'),
    comment='Campaign/project grouping within a workspace.'
    )
    op.create_index(op.f('ix_projects__workspace_id'), 'projects', ['workspace_id'], unique=False)
    op.create_index('ix_projects__workspace_updated_cursor', 'projects', ['workspace_id', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_projects__workspace_slug_where_active', 'projects', ['workspace_id', 'slug'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('quota_periods',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('usage_dimension_id', sa.UUID(), nullable=False),
    sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('consumed_quantity', sa.Numeric(precision=30, scale=10), server_default=sa.text('0'), nullable=False),
    sa.Column('reserved_quantity', sa.Numeric(precision=30, scale=10), server_default=sa.text('0'), nullable=False),
    sa.Column('last_reconciled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('consumed_quantity >= 0', name=op.f('ck_quota_periods__ck_quota_periods__consumed')),
    sa.CheckConstraint('period_end > period_start', name=op.f('ck_quota_periods__ck_quota_periods__period')),
    sa.CheckConstraint('reserved_quantity >= 0', name=op.f('ck_quota_periods__ck_quota_periods__reserved')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_quota_periods__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_quota_periods__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_quota_periods__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usage_dimension_id'], ['usage_dimensions.id'], name=op.f('fk_quota_periods__usage_dimension_id__usage_dimensions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_quota_periods__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_quota_periods')),
    comment='Concurrency-safe quota counters and reservations.'
    )
    op.create_index('ix_quota_periods__organization_dimension_period', 'quota_periods', ['organization_id', 'usage_dimension_id', 'period_start', 'period_end'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_quota_periods__organization_id'), 'quota_periods', ['organization_id'], unique=False)
    op.create_index('ix_quota_periods__workspace_dimension_period', 'quota_periods', ['workspace_id', 'usage_dimension_id', 'period_start', 'period_end'], unique=False, postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NOT NULL'))
    op.create_index('uq_quota_periods__scope_dimension_period', 'quota_periods', ['organization_id', 'workspace_id', 'usage_dimension_id', 'period_start', 'period_end'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('quota_policies',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('usage_dimension_id', sa.UUID(), nullable=False),
    sa.Column('period_kind', sa.Text(), nullable=False),
    sa.Column('hard_limit', sa.Numeric(precision=30, scale=10), nullable=False),
    sa.Column('soft_limit', sa.Numeric(precision=30, scale=10), nullable=True),
    sa.Column('effective_from', sa.DateTime(timezone=True), nullable=False),
    sa.Column('effective_to', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("period_kind IN ('day','month','billing_cycle','lifetime')", name=op.f('ck_quota_policies__ck_quota_policies__period_kind')),
    sa.CheckConstraint('effective_to IS NULL OR effective_to > effective_from', name=op.f('ck_quota_policies__ck_quota_policies__effective_range')),
    sa.CheckConstraint('hard_limit >= 0', name=op.f('ck_quota_policies__ck_quota_policies__hard_limit')),
    sa.CheckConstraint('soft_limit IS NULL OR (soft_limit >= 0 AND soft_limit <= hard_limit)', name=op.f('ck_quota_policies__ck_quota_policies__soft_limit')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_quota_policies__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_quota_policies__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_quota_policies__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usage_dimension_id'], ['usage_dimensions.id'], name=op.f('fk_quota_policies__usage_dimension_id__usage_dimensions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_quota_policies__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_quota_policies')),
    comment='Effective-dated organization or workspace quota limits.'
    )
    op.create_index('ix_quota_policies__organization_dimension_effective', 'quota_policies', ['organization_id', 'usage_dimension_id', sa.literal_column('effective_from DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_quota_policies__organization_id'), 'quota_policies', ['organization_id'], unique=False)
    op.create_index('ix_quota_policies__workspace_dimension_effective', 'quota_policies', ['workspace_id', 'usage_dimension_id', sa.literal_column('effective_from DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NOT NULL'))
    op.create_index('uq_quota_policies__scope_dimension_effective', 'quota_policies', ['organization_id', 'workspace_id', 'usage_dimension_id', 'effective_from'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('roles',
    sa.Column('code', postgresql.CITEXT(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_system', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('(is_system AND workspace_id IS NULL) OR (NOT is_system AND workspace_id IS NOT NULL)', name=op.f('ck_roles__ck_roles__system_workspace_scope')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_roles__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_roles__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_roles__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_roles')),
    comment='System role templates and workspace custom roles.'
    )
    op.create_index(op.f('ix_roles__workspace_id'), 'roles', ['workspace_id'], unique=False)
    op.create_index('uq_roles__code_where_global_active', 'roles', ['code'], unique=True, postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NULL'))
    op.create_index('uq_roles__workspace_code_where_active', 'roles', ['workspace_id', 'code'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('saved_views',
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('view_type', sa.Text(), nullable=False),
    sa.Column('filter_spec', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('sort_spec', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('is_shared', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("view_type IN ('content', 'calendar', 'analytics', 'activity')", name=op.f('ck_saved_views__ck_saved_views__view_type')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_saved_views__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_saved_views__owner_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_saved_views__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_saved_views__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_saved_views')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_saved_views__workspace_id_id'),
    comment='Persisted library, calendar, analytics, and activity filters.'
    )
    op.create_index(op.f('ix_saved_views__workspace_id'), 'saved_views', ['workspace_id'], unique=False)
    op.create_index('ix_saved_views__workspace_owner_type', 'saved_views', ['workspace_id', 'owner_id', 'view_type', 'name'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_saved_views__workspace_owner_type_name_where_active', 'saved_views', ['workspace_id', 'owner_id', 'view_type', 'name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('social_accounts',
    sa.Column('platform_id', sa.UUID(), nullable=False),
    sa.Column('external_account_id', sa.Text(), nullable=False),
    sa.Column('account_name', sa.Text(), nullable=False),
    sa.Column('display_name', sa.Text(), nullable=False),
    sa.Column('username', sa.Text(), nullable=True),
    sa.Column('account_type', sa.Text(), nullable=True),
    sa.Column('connection_status', sa.Text(), nullable=False),
    sa.Column('health_status', sa.Text(), nullable=False),
    sa.Column('publishing_enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('default_audience', sa.Text(), nullable=True),
    sa.Column('time_zone', sa.Text(), server_default=sa.text("'UTC'"), nullable=False),
    sa.Column('followers_count', sa.BigInteger(), nullable=True),
    sa.Column('connected_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("connection_status IN ('connected','disconnected')", name=op.f('ck_social_accounts__ck_social_accounts__connection_status')),
    sa.CheckConstraint("health_status IN ('healthy','warning','error','needs_reauth')", name=op.f('ck_social_accounts__ck_social_accounts__health_status')),
    sa.CheckConstraint('followers_count IS NULL OR followers_count >= 0', name=op.f('ck_social_accounts__ck_social_accounts__followers_count')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_accounts__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['platform_id'], ['social_platforms.id'], name=op.f('fk_social_accounts__platform_id__social_platforms'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_accounts__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_social_accounts__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_accounts')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_social_accounts__workspace_id_id'),
    comment='Connected external social account identity and health.'
    )
    op.create_index('ix_social_accounts__workspace_health', 'social_accounts', ['workspace_id', 'connection_status', 'health_status', sa.literal_column('updated_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_social_accounts__workspace_id'), 'social_accounts', ['workspace_id'], unique=False)
    op.create_index('ix_social_accounts__workspace_sync_due', 'social_accounts', ['workspace_id', 'last_sync_at', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND connection_status = 'connected'"))
    op.create_index('uq_social_accounts__workspace_platform_external_where_active', 'social_accounts', ['workspace_id', 'platform_id', 'external_account_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('social_content_templates',
    sa.Column('platform_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('template_version', sa.Integer(), nullable=False),
    sa.Column('body_template', sa.Text(), nullable=False),
    sa.Column('constraints', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('template_version > 0', name=op.f('ck_social_content_templates__ck_social_content_templates__template_version')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_content_templates__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['platform_id'], ['social_platforms.id'], name=op.f('fk_social_content_templates__platform_id__social_platforms'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_content_templates__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_social_content_templates__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_content_templates')),
    comment='Platform content rendering templates with global or workspace scope.'
    )
    op.create_index(op.f('ix_social_content_templates__workspace_id'), 'social_content_templates', ['workspace_id'], unique=False)
    op.create_index('uq_social_content_templates__scope_platform_name_version', 'social_content_templates', ['workspace_id', 'platform_id', 'name', 'template_version'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('storage_objects',
    sa.Column('object_key', sa.Text(), nullable=False),
    sa.Column('storage_provider', sa.Text(), server_default=sa.text("'azure_blob'"), nullable=False),
    sa.Column('container_name', sa.Text(), nullable=False),
    sa.Column('mime_type', sa.Text(), nullable=False),
    sa.Column('byte_size', sa.BigInteger(), nullable=False),
    sa.Column('checksum_sha256', sa.LargeBinary(), nullable=False),
    sa.Column('scan_status', sa.Text(), server_default=sa.text("'pending'"), nullable=False),
    sa.Column('scan_completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('encryption_key_ref', sa.Text(), nullable=True),
    sa.Column('retention_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("scan_status IN ('pending', 'clean', 'infected', 'failed')", name=op.f('ck_storage_objects__ck_storage_objects__scan_status')),
    sa.CheckConstraint('byte_size >= 0', name=op.f('ck_storage_objects__ck_storage_objects__byte_size')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_storage_objects__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_storage_objects__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_storage_objects__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_storage_objects')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_storage_objects__workspace_id_id'),
    comment='Private blob metadata; URLs are never stored directly.'
    )
    op.create_index('ix_storage_objects__workspace_checksum', 'storage_objects', ['workspace_id', 'checksum_sha256', 'byte_size'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_storage_objects__workspace_id'), 'storage_objects', ['workspace_id'], unique=False)
    op.create_index('ix_storage_objects__workspace_scan_due', 'storage_objects', ['workspace_id', 'created_at', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND scan_status IN ('pending','failed')"))
    op.create_index('uq_storage_objects__workspace_object_key_where_active', 'storage_objects', ['workspace_id', 'object_key'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('subscription_items',
    sa.Column('subscription_id', sa.UUID(), nullable=False),
    sa.Column('usage_dimension_id', sa.UUID(), nullable=True),
    sa.Column('external_item_id', sa.Text(), nullable=True),
    sa.Column('price_code', sa.Text(), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=20, scale=6), nullable=False),
    sa.Column('unit_amount', sa.Numeric(precision=20, scale=8), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('quantity >= 0', name=op.f('ck_subscription_items__ck_subscription_items__quantity')),
    sa.CheckConstraint('unit_amount IS NULL OR unit_amount >= 0', name=op.f('ck_subscription_items__ck_subscription_items__unit_amount')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_subscription_items__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_subscription_items__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], name=op.f('fk_subscription_items__subscription_id__subscriptions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_subscription_items__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usage_dimension_id'], ['usage_dimensions.id'], name=op.f('fk_subscription_items__usage_dimension_id__usage_dimensions'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_subscription_items')),
    sa.UniqueConstraint('organization_id', 'id', name='uq_subscription_items__organization_id_id'),
    comment='External subscription line items mirrored for metering and entitlements.'
    )
    op.create_index(op.f('ix_subscription_items__organization_id'), 'subscription_items', ['organization_id'], unique=False)
    op.create_index('ix_subscription_items__organization_subscription', 'subscription_items', ['organization_id', 'subscription_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_subscription_items__subscription_price_dimension_where_active', 'subscription_items', ['subscription_id', 'price_code', 'usage_dimension_id'], unique=True, postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('tags',
    sa.Column('name', postgresql.CITEXT(), nullable=False),
    sa.Column('color', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_tags__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_tags__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_tags__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_tags__workspace_id_id'),
    comment='Workspace folksonomy tags for content assets.'
    )
    op.create_index(op.f('ix_tags__workspace_id'), 'tags', ['workspace_id'], unique=False)
    op.create_index('uq_tags__workspace_name_where_active', 'tags', ['workspace_id', 'name'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('usage_events',
    sa.Column('organization_id', sa.UUID(), nullable=False),
    sa.Column('usage_dimension_id', sa.UUID(), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=30, scale=10), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('source_type', sa.Text(), nullable=False),
    sa.Column('source_id', sa.UUID(), nullable=False),
    sa.Column('dedupe_key', sa.Text(), nullable=False),
    sa.Column('cost_amount', sa.Numeric(precision=20, scale=8), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('cost_amount IS NULL OR cost_amount >= 0', name=op.f('ck_usage_events__ck_usage_events__cost')),
    sa.CheckConstraint('quantity >= 0', name=op.f('ck_usage_events__ck_usage_events__quantity')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_usage_events__ck_usage_events__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_usage_events__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_usage_events__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_usage_events__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['usage_dimension_id'], ['usage_dimensions.id'], name=op.f('fk_usage_events__usage_dimension_id__usage_dimensions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_usage_events__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_usage_events')),
    sa.UniqueConstraint('workspace_id', 'dedupe_key', name='uq_usage_events__workspace_dedupe'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_usage_events__workspace_id_id'),
    comment='Immutable metering facts retained under usage and billing policy.'
    )
    op.create_index('brin_usage_events__occurred_at', 'usage_events', ['occurred_at'], unique=False, postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.create_index('ix_usage_events__organization_dimension_time', 'usage_events', ['organization_id', 'usage_dimension_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('ix_usage_events__workspace_dimension_time', 'usage_events', ['workspace_id', 'usage_dimension_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index(op.f('ix_usage_events__workspace_id'), 'usage_events', ['workspace_id'], unique=False)
    op.create_table('webhook_receipts',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('provider_code', sa.Text(), nullable=False),
    sa.Column('external_event_id', sa.Text(), nullable=False),
    sa.Column('event_type', sa.Text(), nullable=False),
    sa.Column('signature_valid', sa.Boolean(), nullable=False),
    sa.Column('payload_hash', sa.LargeBinary(), nullable=False),
    sa.Column('payload_fragment', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('processing_status', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("processing_status IN ('received','processed','ignored','failed')", name=op.f('ck_webhook_receipts__webhook_receipts_processing_status')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_webhook_receipts__webhook_receipts_immutable_shape')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_webhook_receipts__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_webhook_receipts__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_webhook_receipts__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_webhook_receipts')),
    comment='Immutable redacted inbound callback deduplication evidence.'
    )
    op.create_index('ix_webhook_receipts__unprocessed', 'webhook_receipts', ['received_at', 'id'], unique=False, postgresql_where=sa.text("processed_at IS NULL AND processing_status IN ('received','failed')"))
    op.create_index('uq_webhook_receipts__provider_external', 'webhook_receipts', ['provider_code', 'external_event_id'], unique=True)
    op.create_index('uq_webhook_receipts__provider_payload_hash', 'webhook_receipts', ['provider_code', 'payload_hash'], unique=True, postgresql_where=sa.text("external_event_id = ''"))
    op.create_table('workspace_memberships',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'active'"), nullable=False),
    sa.Column('invited_by', sa.UUID(), nullable=True),
    sa.Column('invited_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('invited', 'active', 'suspended')", name=op.f('ck_workspace_memberships__ck_workspace_memberships__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_workspace_memberships__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['invited_by'], ['users.id'], name=op.f('fk_workspace_memberships__invited_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_workspace_memberships__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_workspace_memberships__user_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_workspace_memberships__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_workspace_memberships')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_workspace_memberships__workspace_id_id'),
    comment='Workspace user access; commercial org membership does not imply access.'
    )
    op.create_index(op.f('ix_workspace_memberships__workspace_id'), 'workspace_memberships', ['workspace_id'], unique=False)
    op.create_index('ix_workspace_memberships__workspace_status_user', 'workspace_memberships', ['workspace_id', 'status', 'user_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_workspace_memberships__workspace_user_where_active', 'workspace_memberships', ['workspace_id', 'user_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('content_assets',
    sa.Column('project_id', sa.UUID(), nullable=True),
    sa.Column('folder_id', sa.UUID(), nullable=True),
    sa.Column('asset_type', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('lifecycle_status', sa.Text(), server_default=sa.text("'draft'"), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.Column('is_favorite', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('search_document', postgresql.TSVECTOR(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("asset_type IN ('article', 'video', 'poster', 'thumbnail')", name=op.f('ck_content_assets__ck_content_assets__asset_type')),
    sa.CheckConstraint("lifecycle_status IN ('draft', 'active', 'archived')", name=op.f('ck_content_assets__ck_content_assets__lifecycle_status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_content_assets__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_content_assets__owner_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_content_assets__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'folder_id'], ['folders.workspace_id', 'folders.id'], name='fk_content_assets__folder', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'project_id'], ['projects.workspace_id', 'projects.id'], name='fk_content_assets__project', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_content_assets__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_content_assets')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_content_assets__workspace_id_id'),
    comment='Master content aggregate and library record.'
    )
    op.create_index('ix_content_assets__search_gin', 'content_assets', ['search_document'], unique=False, postgresql_using='gin')
    op.create_index('ix_content_assets__workspace_folder_updated', 'content_assets', ['workspace_id', 'folder_id', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_content_assets__workspace_id'), 'content_assets', ['workspace_id'], unique=False)
    op.create_index('ix_content_assets__workspace_owner_updated', 'content_assets', ['workspace_id', 'owner_id', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('ix_content_assets__workspace_project_updated', 'content_assets', ['workspace_id', 'project_id', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('ix_content_assets__workspace_type_status_updated', 'content_assets', ['workspace_id', 'asset_type', 'lifecycle_status', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('ix_content_assets__workspace_updated_cursor', 'content_assets', ['workspace_id', sa.literal_column('updated_at DESC'), 'id'], unique=False, postgresql_include=['title', 'asset_type', 'lifecycle_status', 'owner_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('data_exports',
    sa.Column('requested_by', sa.UUID(), nullable=True),
    sa.Column('export_type', sa.Text(), nullable=False),
    sa.Column('state', sa.Text(), nullable=False),
    sa.Column('storage_object_id', sa.UUID(), nullable=True),
    sa.Column('requested_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('purged_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('checksum_sha256', sa.LargeBinary(), nullable=True),
    sa.Column('failure_code', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("export_type IN ('workspace_export','user_export','erasure_evidence')", name=op.f('ck_data_exports__ck_data_exports__export_type')),
    sa.CheckConstraint("state IN ('queued','running','ready','failed','expired','purged')", name=op.f('ck_data_exports__ck_data_exports__state')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_data_exports__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['requested_by'], ['users.id'], name=op.f('fk_data_exports__requested_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['storage_object_id'], ['storage_objects.id'], name=op.f('fk_data_exports__storage_object_id__storage_objects'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_data_exports__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_data_exports__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_data_exports')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_data_exports__workspace_id_id'),
    comment='Tenant export and erasure package tracking with expiry.'
    )
    op.create_index('ix_data_exports__expiry', 'data_exports', ['expires_at', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND state IN ('ready','expired')"))
    op.create_index('ix_data_exports__workspace_cursor', 'data_exports', ['workspace_id', sa.literal_column('updated_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_data_exports__workspace_id'), 'data_exports', ['workspace_id'], unique=False)
    op.create_table('membership_roles',
    sa.Column('membership_id', sa.UUID(), nullable=False),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_membership_roles__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_membership_roles__role_id__roles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_membership_roles__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'membership_id'], ['workspace_memberships.workspace_id', 'workspace_memberships.id'], name='fk_membership_roles__workspace_id_membership_id__workspace_memberships', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_membership_roles__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('workspace_id', 'membership_id', 'role_id', name='pk_membership_roles'),
    comment='Workspace-local role assignments for workspace memberships.'
    )
    op.create_index(op.f('ix_membership_roles__workspace_id'), 'membership_roles', ['workspace_id'], unique=False)
    op.create_index('ix_membership_roles__workspace_membership', 'membership_roles', ['workspace_id', 'membership_id'], unique=False)
    op.create_index('ix_membership_roles__workspace_role', 'membership_roles', ['workspace_id', 'role_id'], unique=False)
    op.create_table('notification_deliveries',
    sa.Column('notification_id', sa.UUID(), nullable=False),
    sa.Column('recipient_user_id', sa.UUID(), nullable=False),
    sa.Column('channel', sa.Text(), nullable=False),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('attempt_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('provider_reference', sa.Text(), nullable=True),
    sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_code', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("channel IN ('in_app','email','webhook')", name=op.f('ck_notification_deliveries__ck_notification_deliveries__channel')),
    sa.CheckConstraint("status IN ('pending','sent','delivered','failed','suppressed')", name=op.f('ck_notification_deliveries__ck_notification_deliveries__status')),
    sa.CheckConstraint('attempt_count >= 0', name=op.f('ck_notification_deliveries__ck_notification_deliveries__attempt_count')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_notification_deliveries__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], name=op.f('fk_notification_deliveries__notification_id__notifications'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['recipient_user_id'], ['users.id'], name=op.f('fk_notification_deliveries__recipient_user_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_notification_deliveries__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_notification_deliveries__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notification_deliveries')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_notification_deliveries__workspace_id_id'),
    comment='Per-channel delivery attempts and terminal status for notifications.'
    )
    op.create_index('ix_notification_deliveries__due', 'notification_deliveries', ['created_at', 'id'], unique=False, postgresql_include=['workspace_id', 'channel'], postgresql_where=sa.text("deleted_at IS NULL AND status IN ('pending','failed')"))
    op.create_index(op.f('ix_notification_deliveries__workspace_id'), 'notification_deliveries', ['workspace_id'], unique=False)
    op.create_index('uq_notification_deliveries__notification_recipient_channel_where_active', 'notification_deliveries', ['workspace_id', 'notification_id', 'recipient_user_id', 'channel'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('oauth_token_vaults',
    sa.Column('social_account_id', sa.UUID(), nullable=False),
    sa.Column('ciphertext', sa.LargeBinary(), nullable=True),
    sa.Column('managed_secret_ref', sa.Text(), nullable=True),
    sa.Column('key_id', sa.Text(), nullable=False),
    sa.Column('key_version', sa.Text(), nullable=False),
    sa.Column('token_fingerprint', sa.LargeBinary(), nullable=False),
    sa.Column('scopes_hash', sa.LargeBinary(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rotated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('active','expiring_soon','expired','renew_required','revoked')", name=op.f('ck_oauth_token_vaults__ck_oauth_token_vaults__status')),
    sa.CheckConstraint('(ciphertext IS NOT NULL AND managed_secret_ref IS NULL) OR (ciphertext IS NULL AND managed_secret_ref IS NOT NULL)', name=op.f('ck_oauth_token_vaults__ck_oauth_token_vaults__secret_source')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_oauth_token_vaults__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_oauth_token_vaults__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'social_account_id'], ['social_accounts.workspace_id', 'social_accounts.id'], name='fk_oauth_token_vaults__social_account', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_oauth_token_vaults__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_oauth_token_vaults')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_oauth_token_vaults__workspace_id_id'),
    comment='Encrypted OAuth token metadata; no plaintext secrets stored.'
    )
    op.create_index('ix_oauth_token_vaults__expiry_due', 'oauth_token_vaults', ['expires_at', 'social_account_id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND status IN ('active','expiring_soon')"))
    op.create_index('ix_oauth_token_vaults__workspace_account', 'oauth_token_vaults', ['workspace_id', 'social_account_id'], unique=False)
    op.create_index(op.f('ix_oauth_token_vaults__workspace_id'), 'oauth_token_vaults', ['workspace_id'], unique=False)
    op.create_index('uq_oauth_token_vaults__workspace_account_where_active', 'oauth_token_vaults', ['workspace_id', 'social_account_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('project_members',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('project_role', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("project_role IN ('owner', 'editor', 'reviewer', 'viewer')", name=op.f('ck_project_members__ck_project_members__project_role')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_project_members__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_project_members__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_project_members__user_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'project_id'], ['projects.workspace_id', 'projects.id'], name='fk_project_members__project', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_project_members__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_project_members')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_project_members__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'project_id', 'user_id', name='uq_project_members__project_user'),
    comment='Project-level user responsibility assignments.'
    )
    op.create_index(op.f('ix_project_members__workspace_id'), 'project_members', ['workspace_id'], unique=False)
    op.create_index('ix_project_members__workspace_project', 'project_members', ['workspace_id', 'project_id'], unique=False)
    op.create_index('ix_project_members__workspace_user', 'project_members', ['workspace_id', 'user_id'], unique=False)
    op.create_table('role_permissions',
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('permission_id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_role_permissions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], name=op.f('fk_role_permissions__permission_id__permissions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name=op.f('fk_role_permissions__role_id__roles'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_role_permissions__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_role_permissions__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('role_id', 'permission_id', name='pk_role_permissions'),
    comment='Permission grants copied with custom roles for workspace RLS.'
    )
    op.create_index('ix_role_permissions__permission_id', 'role_permissions', ['permission_id'], unique=False)
    op.create_index('ix_role_permissions__role_id', 'role_permissions', ['role_id'], unique=False)
    op.create_index(op.f('ix_role_permissions__workspace_id'), 'role_permissions', ['workspace_id'], unique=False)
    op.create_table('settings',
    sa.Column('workspace_id', sa.UUID(), nullable=True),
    sa.Column('organization_id', sa.UUID(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('project_id', sa.UUID(), nullable=True),
    sa.Column('social_account_id', sa.UUID(), nullable=True),
    sa.Column('definition_id', sa.UUID(), nullable=False),
    sa.Column('scope_type', sa.Text(), nullable=False),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("((scope_type = 'organization' AND organization_id IS NOT NULL AND workspace_id IS NULL AND user_id IS NULL AND project_id IS NULL AND social_account_id IS NULL) OR (scope_type = 'workspace' AND workspace_id IS NOT NULL AND organization_id IS NULL AND user_id IS NULL AND project_id IS NULL AND social_account_id IS NULL) OR (scope_type = 'user' AND workspace_id IS NOT NULL AND user_id IS NOT NULL AND organization_id IS NULL AND project_id IS NULL AND social_account_id IS NULL) OR (scope_type = 'project' AND workspace_id IS NOT NULL AND project_id IS NOT NULL AND organization_id IS NULL AND user_id IS NULL AND social_account_id IS NULL) OR (scope_type = 'social_account' AND workspace_id IS NOT NULL AND social_account_id IS NOT NULL AND organization_id IS NULL AND user_id IS NULL AND project_id IS NULL))", name=op.f('ck_settings__ck_settings__scope_target')),
    sa.CheckConstraint("scope_type IN ('organization','workspace','user','project','social_account')", name=op.f('ck_settings__ck_settings__scope_type')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_settings__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['definition_id'], ['setting_definitions.id'], name=op.f('fk_settings__definition_id__setting_definitions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('fk_settings__organization_id__organizations'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=op.f('fk_settings__project_id__projects'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], name=op.f('fk_settings__social_account_id__social_accounts'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_settings__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_settings__user_id__users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_settings__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_settings')),
    comment='Scoped setting overrides resolved from specific to general.'
    )
    op.create_index('ix_settings__organization_definition', 'settings', ['organization_id', 'definition_id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'organization'"))
    op.create_index('ix_settings__project_definition', 'settings', ['workspace_id', 'project_id', 'definition_id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'project'"))
    op.create_index('ix_settings__social_account_definition', 'settings', ['workspace_id', 'social_account_id', 'definition_id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'social_account'"))
    op.create_index('ix_settings__user_definition', 'settings', ['workspace_id', 'user_id', 'definition_id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'user'"))
    op.create_index('ix_settings__workspace_definition', 'settings', ['workspace_id', 'definition_id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'workspace'"))
    op.create_index('uq_settings__organization_definition', 'settings', ['organization_id', 'definition_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'organization'"))
    op.create_index('uq_settings__project_definition', 'settings', ['workspace_id', 'project_id', 'definition_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'project'"))
    op.create_index('uq_settings__social_account_definition', 'settings', ['workspace_id', 'social_account_id', 'definition_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'social_account'"))
    op.create_index('uq_settings__user_definition', 'settings', ['workspace_id', 'user_id', 'definition_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'user'"))
    op.create_index('uq_settings__workspace_definition', 'settings', ['workspace_id', 'definition_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'workspace'"))
    op.create_table('social_account_permissions',
    sa.Column('social_account_id', sa.UUID(), nullable=False),
    sa.Column('permission_code', postgresql.CITEXT(), nullable=False),
    sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_account_permissions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_account_permissions__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'social_account_id'], ['social_accounts.workspace_id', 'social_accounts.id'], name='fk_social_account_permissions__social_account', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_social_account_permissions__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_account_permissions')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_social_account_permissions__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'social_account_id', 'permission_code', name='uq_social_account_permissions__account_code'),
    comment='Granted platform scope permissions for connected social accounts.'
    )
    op.create_index('ix_social_account_permissions__workspace_account', 'social_account_permissions', ['workspace_id', 'social_account_id'], unique=False)
    op.create_index(op.f('ix_social_account_permissions__workspace_id'), 'social_account_permissions', ['workspace_id'], unique=False)
    op.create_table('social_account_settings',
    sa.Column('social_account_id', sa.UUID(), nullable=False),
    sa.Column('visibility', sa.Text(), nullable=True),
    sa.Column('hashtag_strategy', sa.Text(), nullable=True),
    sa.Column('auto_publish', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('ai_optimization', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('auto_schedule', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('url_tracking', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('provider_defaults', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_account_settings__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_account_settings__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'social_account_id'], ['social_accounts.workspace_id', 'social_accounts.id'], name='fk_social_account_settings__social_account', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_social_account_settings__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_account_settings')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_social_account_settings__workspace_id_id'),
    comment='Publishing defaults and feature toggles for social accounts.'
    )
    op.create_index('ix_social_account_settings__workspace_account', 'social_account_settings', ['workspace_id', 'social_account_id'], unique=False)
    op.create_index(op.f('ix_social_account_settings__workspace_id'), 'social_account_settings', ['workspace_id'], unique=False)
    op.create_index('uq_social_account_settings__workspace_account_where_active', 'social_account_settings', ['workspace_id', 'social_account_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('social_account_snapshots',
    sa.Column('social_account_id', sa.UUID(), nullable=False),
    sa.Column('snapshot_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('followers_count', sa.BigInteger(), nullable=True),
    sa.Column('connection_status', sa.Text(), nullable=False),
    sa.Column('health_status', sa.Text(), nullable=False),
    sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("connection_status IN ('connected','disconnected')", name=op.f('ck_social_account_snapshots__ck_social_account_snapshots__connection_status')),
    sa.CheckConstraint("health_status IN ('healthy','warning','error','needs_reauth')", name=op.f('ck_social_account_snapshots__ck_social_account_snapshots__health_status')),
    sa.CheckConstraint('followers_count IS NULL OR followers_count >= 0', name=op.f('ck_social_account_snapshots__ck_social_account_snapshots__followers')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_social_account_snapshots__ck_social_account_snapshots__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_social_account_snapshots__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_social_account_snapshots__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'social_account_id'], ['social_accounts.workspace_id', 'social_accounts.id'], name='fk_social_account_snapshots__account', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_social_account_snapshots__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_social_account_snapshots')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_social_account_snapshots__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'social_account_id', 'snapshot_at', name='uq_social_account_snapshots__account_time'),
    comment='Immutable social-account health and follower history.'
    )
    op.create_index('ix_social_account_snapshots__workspace_account_time', 'social_account_snapshots', ['workspace_id', 'social_account_id', sa.literal_column('snapshot_at DESC')], unique=False)
    op.create_index(op.f('ix_social_account_snapshots__workspace_id'), 'social_account_snapshots', ['workspace_id'], unique=False)
    op.create_table('articles',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('source_kind', sa.Text(), nullable=False),
    sa.Column('canonical_url', sa.Text(), nullable=True),
    sa.Column('language_code', sa.Text(), server_default=sa.text("'en'"), nullable=False),
    sa.Column('word_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('reading_minutes', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("source_kind IN ('compose', 'paste', 'import', 'upload')", name=op.f('ck_articles__ck_articles__source_kind')),
    sa.CheckConstraint('reading_minutes >= 0', name=op.f('ck_articles__ck_articles__reading_minutes')),
    sa.CheckConstraint('word_count >= 0', name=op.f('ck_articles__ck_articles__word_count')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_articles__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_articles__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_articles__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_articles__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('asset_id', name=op.f('pk_articles')),
    sa.UniqueConstraint('workspace_id', 'asset_id', name='uq_articles__workspace_asset'),
    comment='Article-specific metadata for content assets of type article.'
    )
    op.create_index(op.f('ix_articles__workspace_id'), 'articles', ['workspace_id'], unique=False)
    op.create_table('asset_categories',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.UUID(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_asset_categories__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_asset_categories__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_asset_categories__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'category_id'], ['categories.workspace_id', 'categories.id'], name='fk_asset_categories__category', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_asset_categories__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_asset_categories')),
    sa.UniqueConstraint('workspace_id', 'asset_id', 'category_id', name='uq_asset_categories__asset_category'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_asset_categories__workspace_id_id'),
    comment='Many-to-many bridge between content assets and categories.'
    )
    op.create_index('ix_asset_categories__workspace_asset_category', 'asset_categories', ['workspace_id', 'asset_id', 'category_id'], unique=False)
    op.create_index('ix_asset_categories__workspace_category_asset', 'asset_categories', ['workspace_id', 'category_id', 'asset_id'], unique=False)
    op.create_index(op.f('ix_asset_categories__workspace_id'), 'asset_categories', ['workspace_id'], unique=False)
    op.create_index('uq_asset_categories__one_primary', 'asset_categories', ['workspace_id', 'asset_id'], unique=True, postgresql_where=sa.text('is_primary'))
    op.create_table('asset_storage_objects',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('storage_object_id', sa.UUID(), nullable=False),
    sa.Column('purpose', sa.Text(), nullable=False),
    sa.Column('variant_key', sa.Text(), server_default=sa.text("'original'"), nullable=False),
    sa.Column('position', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("purpose IN ('source', 'rendition', 'poster', 'thumbnail', 'transcript', 'caption', 'attachment')", name=op.f('ck_asset_storage_objects__ck_asset_storage_objects__purpose')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_asset_storage_objects__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_asset_storage_objects__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_asset_storage_objects__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'storage_object_id'], ['storage_objects.workspace_id', 'storage_objects.id'], name='fk_asset_storage_objects__storage_object', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_asset_storage_objects__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_asset_storage_objects')),
    sa.UniqueConstraint('workspace_id', 'asset_id', 'purpose', 'variant_key', 'position', name='uq_asset_storage_objects__asset_purpose_variant_position'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_asset_storage_objects__workspace_id_id'),
    comment='Named blob attachments and renditions for content assets.'
    )
    op.create_index('ix_asset_storage_objects__workspace_asset_purpose', 'asset_storage_objects', ['workspace_id', 'asset_id', 'purpose', 'variant_key', 'position'], unique=False)
    op.create_index(op.f('ix_asset_storage_objects__workspace_id'), 'asset_storage_objects', ['workspace_id'], unique=False)
    op.create_index('ix_asset_storage_objects__workspace_object', 'asset_storage_objects', ['workspace_id', 'storage_object_id'], unique=False)
    op.create_table('asset_tags',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('tag_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_asset_tags__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_asset_tags__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_asset_tags__asset', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['workspace_id', 'tag_id'], ['tags.workspace_id', 'tags.id'], name='fk_asset_tags__tag', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_asset_tags__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_asset_tags')),
    sa.UniqueConstraint('workspace_id', 'asset_id', 'tag_id', name='uq_asset_tags__asset_tag'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_asset_tags__workspace_id_id'),
    comment='Many-to-many bridge between content assets and tags.'
    )
    op.create_index('ix_asset_tags__workspace_asset_tag', 'asset_tags', ['workspace_id', 'asset_id', 'tag_id'], unique=False)
    op.create_index(op.f('ix_asset_tags__workspace_id'), 'asset_tags', ['workspace_id'], unique=False)
    op.create_index('ix_asset_tags__workspace_tag_asset', 'asset_tags', ['workspace_id', 'tag_id', 'asset_id'], unique=False)
    op.create_table('collection_items',
    sa.Column('collection_id', sa.UUID(), nullable=False),
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('position', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('position >= 0', name=op.f('ck_collection_items__ck_collection_items__position')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_collection_items__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_collection_items__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_collection_items__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'collection_id'], ['collections.workspace_id', 'collections.id'], name='fk_collection_items__collection', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_collection_items__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_collection_items')),
    sa.UniqueConstraint('workspace_id', 'collection_id', 'asset_id', name='uq_collection_items__collection_asset'),
    sa.UniqueConstraint('workspace_id', 'collection_id', 'position', name='uq_collection_items__collection_position'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_collection_items__workspace_id_id'),
    comment='Ordered membership of content assets in collections.'
    )
    op.create_index('ix_collection_items__workspace_asset', 'collection_items', ['workspace_id', 'asset_id'], unique=False)
    op.create_index('ix_collection_items__workspace_collection_position', 'collection_items', ['workspace_id', 'collection_id', 'position', 'id'], unique=False)
    op.create_index(op.f('ix_collection_items__workspace_id'), 'collection_items', ['workspace_id'], unique=False)
    op.create_table('content_relations',
    sa.Column('source_asset_id', sa.UUID(), nullable=False),
    sa.Column('target_asset_id', sa.UUID(), nullable=False),
    sa.Column('relation_type', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("relation_type IN ('thumbnail_for', 'poster_for', 'derived_from', 'translation_of', 'related_to')", name=op.f('ck_content_relations__ck_content_relations__relation_type')),
    sa.CheckConstraint('source_asset_id <> target_asset_id', name=op.f('ck_content_relations__ck_content_relations__distinct_assets')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_content_relations__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_content_relations__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'source_asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_content_relations__source_asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'target_asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_content_relations__target_asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_content_relations__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_content_relations')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_content_relations__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'source_asset_id', 'target_asset_id', 'relation_type', name='uq_content_relations__source_target_type'),
    comment='Typed directed links among content assets.'
    )
    op.create_index(op.f('ix_content_relations__workspace_id'), 'content_relations', ['workspace_id'], unique=False)
    op.create_index('ix_content_relations__workspace_source', 'content_relations', ['workspace_id', 'source_asset_id'], unique=False)
    op.create_index('ix_content_relations__workspace_target', 'content_relations', ['workspace_id', 'target_asset_id'], unique=False)
    op.create_table('content_versions',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('body_text', sa.Text(), nullable=True),
    sa.Column('body_rich', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('origin', sa.Text(), nullable=False),
    sa.Column('source_version_id', sa.UUID(), nullable=True),
    sa.Column('content_hash', sa.LargeBinary(), nullable=False),
    sa.Column('change_summary', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("origin IN ('user', 'ai', 'import', 'regeneration')", name=op.f('ck_content_versions__ck_content_versions__origin')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_content_versions__ck_content_versions__immutable_uac')),
    sa.CheckConstraint('version_number > 0', name=op.f('ck_content_versions__ck_content_versions__version_number')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_content_versions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_content_versions__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_content_versions__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'source_version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_content_versions__source_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_content_versions__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_content_versions')),
    sa.UniqueConstraint('workspace_id', 'asset_id', 'content_hash', name='uq_content_versions__workspace_asset_hash'),
    sa.UniqueConstraint('workspace_id', 'asset_id', 'version_number', name='uq_content_versions__workspace_asset_number'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_content_versions__workspace_id_id'),
    comment='Immutable content snapshots retained for publishing and audit.'
    )
    op.create_index('ix_content_versions__workspace_asset_version_desc', 'content_versions', ['workspace_id', 'asset_id', sa.literal_column('version_number DESC')], unique=False, postgresql_include=['created_at', 'origin', 'content_hash'])
    op.create_index(op.f('ix_content_versions__workspace_id'), 'content_versions', ['workspace_id'], unique=False)
    op.create_table('posters',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('aspect_ratio', sa.Numeric(precision=12, scale=6), nullable=True),
    sa.Column('alt_text', sa.Text(), nullable=True),
    sa.Column('crop_metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('aspect_ratio IS NULL OR aspect_ratio > 0', name=op.f('ck_posters__ck_posters__aspect_ratio')),
    sa.CheckConstraint('height IS NULL OR height > 0', name=op.f('ck_posters__ck_posters__height')),
    sa.CheckConstraint('width IS NULL OR width > 0', name=op.f('ck_posters__ck_posters__width')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_posters__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_posters__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_posters__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_posters__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('asset_id', name=op.f('pk_posters')),
    sa.UniqueConstraint('workspace_id', 'asset_id', name='uq_posters__workspace_asset'),
    comment='Poster-specific metadata for content assets of type poster.'
    )
    op.create_index(op.f('ix_posters__workspace_id'), 'posters', ['workspace_id'], unique=False)
    op.create_table('thumbnails',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('aspect_ratio', sa.Numeric(precision=12, scale=6), nullable=True),
    sa.Column('alt_text', sa.Text(), nullable=True),
    sa.Column('source_time_ms', sa.BigInteger(), nullable=True),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('aspect_ratio IS NULL OR aspect_ratio > 0', name=op.f('ck_thumbnails__ck_thumbnails__aspect_ratio')),
    sa.CheckConstraint('height IS NULL OR height > 0', name=op.f('ck_thumbnails__ck_thumbnails__height')),
    sa.CheckConstraint('source_time_ms IS NULL OR source_time_ms >= 0', name=op.f('ck_thumbnails__ck_thumbnails__source_time')),
    sa.CheckConstraint('width IS NULL OR width > 0', name=op.f('ck_thumbnails__ck_thumbnails__width')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_thumbnails__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_thumbnails__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_thumbnails__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_thumbnails__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('asset_id', name=op.f('pk_thumbnails')),
    sa.UniqueConstraint('workspace_id', 'asset_id', name='uq_thumbnails__workspace_asset'),
    comment='Thumbnail-specific metadata for content assets of type thumbnail.'
    )
    op.create_index(op.f('ix_thumbnails__workspace_id'), 'thumbnails', ['workspace_id'], unique=False)
    op.create_table('videos',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('duration_ms', sa.BigInteger(), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('frame_rate', sa.Numeric(precision=8, scale=3), nullable=True),
    sa.Column('transcript_status', sa.Text(), server_default=sa.text("'none'"), nullable=False),
    sa.Column('caption_language', sa.Text(), nullable=True),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("transcript_status IN ('none', 'pending', 'ready', 'failed')", name=op.f('ck_videos__ck_videos__transcript_status')),
    sa.CheckConstraint('duration_ms IS NULL OR duration_ms >= 0', name=op.f('ck_videos__ck_videos__duration')),
    sa.CheckConstraint('frame_rate IS NULL OR frame_rate > 0', name=op.f('ck_videos__ck_videos__frame_rate')),
    sa.CheckConstraint('height IS NULL OR height > 0', name=op.f('ck_videos__ck_videos__height')),
    sa.CheckConstraint('width IS NULL OR width > 0', name=op.f('ck_videos__ck_videos__width')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_videos__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_videos__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_videos__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_videos__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('asset_id', name=op.f('pk_videos')),
    sa.UniqueConstraint('workspace_id', 'asset_id', name='uq_videos__workspace_asset'),
    comment='Video-specific metadata for content assets of type video.'
    )
    op.create_index(op.f('ix_videos__workspace_id'), 'videos', ['workspace_id'], unique=False)
    op.create_index('ix_videos__workspace_transcript_status', 'videos', ['workspace_id', 'transcript_status'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('ai_generation_requests',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('source_version_id', sa.UUID(), nullable=False),
    sa.Column('model_id', sa.UUID(), nullable=False),
    sa.Column('prompt_template_id', sa.UUID(), nullable=True),
    sa.Column('brand_profile_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.Text(), server_default=sa.text("'queued'"), nullable=False),
    sa.Column('scope', sa.Text(), nullable=False),
    sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('provider_request_id', sa.Text(), nullable=True),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('failure_code', sa.Text(), nullable=True),
    sa.Column('failure_message', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("scope IN ('whole','selection','headline','cta','hashtags','tone','platform_variant')", name=op.f('ck_ai_generation_requests__ck_ai_generation_requests__scope')),
    sa.CheckConstraint("status IN ('queued','running','succeeded','failed','cancelled')", name=op.f('ck_ai_generation_requests__ck_ai_generation_requests__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_generation_requests__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], name=op.f('fk_ai_generation_requests__model_id__ai_models'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_generation_requests__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_ai_generation_requests__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'brand_profile_id'], ['brand_profiles.workspace_id', 'brand_profiles.id'], name='fk_ai_generation_requests__brand_profile', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'prompt_template_id'], ['ai_prompt_templates.workspace_id', 'ai_prompt_templates.id'], name='fk_ai_generation_requests__prompt_template', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'source_version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_ai_generation_requests__source_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_ai_generation_requests__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_generation_requests')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_ai_generation_requests__workspace_id_id'),
    comment='AI generation aggregate with idempotent request tracking.'
    )
    op.create_index('ix_ai_generation_requests__provider_request', 'ai_generation_requests', ['model_id', 'provider_request_id'], unique=False, postgresql_where=sa.text('provider_request_id IS NOT NULL'))
    op.create_index('ix_ai_generation_requests__workspace_asset_cursor', 'ai_generation_requests', ['workspace_id', 'asset_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('ix_ai_generation_requests__workspace_due', 'ai_generation_requests', ['workspace_id', 'created_at', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND status = 'queued'"))
    op.create_index(op.f('ix_ai_generation_requests__workspace_id'), 'ai_generation_requests', ['workspace_id'], unique=False)
    op.create_index('uq_ai_generation_requests__workspace_idempotency', 'ai_generation_requests', ['workspace_id', 'idempotency_key'], unique=True)
    op.create_table('approval_requests',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('version_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Text(), server_default=sa.text("'pending'"), nullable=False),
    sa.Column('requested_by', sa.UUID(), nullable=True),
    sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('decision_reason', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'changes_requested', 'cancelled')", name=op.f('ck_approval_requests__ck_approval_requests__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_approval_requests__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['requested_by'], ['users.id'], name=op.f('fk_approval_requests__requested_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_approval_requests__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_approval_requests__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_approval_requests__version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_approval_requests__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_approval_requests')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_approval_requests__workspace_id_id'),
    comment='Approval workflow instance for a specific content version.'
    )
    op.create_index(op.f('ix_approval_requests__workspace_id'), 'approval_requests', ['workspace_id'], unique=False)
    op.create_index('ix_approval_requests__workspace_pending', 'approval_requests', ['workspace_id', sa.literal_column('requested_at'), 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND status = 'pending'"))
    op.create_index('uq_approval_requests__one_pending_per_version', 'approval_requests', ['workspace_id', 'version_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND status = 'pending'"))
    op.create_table('comments',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('version_id', sa.UUID(), nullable=True),
    sa.Column('parent_comment_id', sa.UUID(), nullable=True),
    sa.Column('author_id', sa.UUID(), nullable=True),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('anchor', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolved_by', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('length(trim(body)) > 0', name=op.f('ck_comments__ck_comments__body_nonblank')),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], name=op.f('fk_comments__author_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_comments__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], name=op.f('fk_comments__resolved_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_comments__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_comments__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'parent_comment_id'], ['comments.workspace_id', 'comments.id'], name='fk_comments__parent', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_comments__version', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_comments__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_comments')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_comments__workspace_id_id'),
    comment='Threaded review comments on content assets and versions.'
    )
    op.create_index('ix_comments__workspace_asset_created_cursor', 'comments', ['workspace_id', 'asset_id', sa.literal_column('created_at DESC'), 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_comments__workspace_id'), 'comments', ['workspace_id'], unique=False)
    op.create_index('ix_comments__workspace_parent', 'comments', ['workspace_id', 'parent_comment_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('content_drafts',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('base_version_id', sa.UUID(), nullable=True),
    sa.Column('body_text', sa.Text(), nullable=True),
    sa.Column('body_rich', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('autosaved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_content_drafts__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_content_drafts__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_content_drafts__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'base_version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_content_drafts__base_version', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_content_drafts__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_content_drafts')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_content_drafts__workspace_id_id'),
    comment='Current mutable autosave/editor state per content asset.'
    )
    op.create_index(op.f('ix_content_drafts__workspace_id'), 'content_drafts', ['workspace_id'], unique=False)
    op.create_index('uq_content_drafts__workspace_asset_where_active', 'content_drafts', ['workspace_id', 'asset_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('ai_generation_outputs',
    sa.Column('generation_request_id', sa.UUID(), nullable=False),
    sa.Column('sequence_no', sa.Integer(), nullable=False),
    sa.Column('platform_id', sa.UUID(), nullable=True),
    sa.Column('output_text', sa.Text(), nullable=False),
    sa.Column('output_metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('safety_status', sa.Text(), nullable=False),
    sa.Column('content_hash', sa.LargeBinary(), nullable=False),
    sa.Column('materialized_version_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("safety_status IN ('unchecked','passed','flagged','blocked')", name=op.f('ck_ai_generation_outputs__ck_ai_generation_outputs__safety_status')),
    sa.CheckConstraint('sequence_no > 0', name=op.f('ck_ai_generation_outputs__ck_ai_generation_outputs__sequence_no')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_ai_generation_outputs__ck_ai_generation_outputs__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_generation_outputs__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['platform_id'], ['social_platforms.id'], name=op.f('fk_ai_generation_outputs__platform_id__social_platforms'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_generation_outputs__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'generation_request_id'], ['ai_generation_requests.workspace_id', 'ai_generation_requests.id'], name='fk_ai_generation_outputs__generation_request', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'materialized_version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_ai_generation_outputs__materialized_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_ai_generation_outputs__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_generation_outputs')),
    sa.UniqueConstraint('workspace_id', 'generation_request_id', 'sequence_no', name='uq_ai_generation_outputs__request_sequence'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_ai_generation_outputs__workspace_id_id'),
    comment='Immutable generated AI output candidates.'
    )
    op.create_index('ix_ai_generation_outputs__created_at', 'ai_generation_outputs', ['created_at', 'id'], unique=False)
    op.create_index('ix_ai_generation_outputs__materialized_version', 'ai_generation_outputs', ['workspace_id', 'materialized_version_id'], unique=False, postgresql_where=sa.text('materialized_version_id IS NOT NULL'))
    op.create_index(op.f('ix_ai_generation_outputs__workspace_id'), 'ai_generation_outputs', ['workspace_id'], unique=False)
    op.create_index('ix_ai_generation_outputs__workspace_request_sequence', 'ai_generation_outputs', ['workspace_id', 'generation_request_id', 'sequence_no'], unique=False)
    op.create_table('ai_suggestions',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('version_id', sa.UUID(), nullable=False),
    sa.Column('generation_request_id', sa.UUID(), nullable=True),
    sa.Column('category', sa.Text(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('proposed_change', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.Text(), server_default=sa.text("'open'"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("category IN ('grammar','seo','engagement','readability','timing','warning')", name=op.f('ck_ai_suggestions__ck_ai_suggestions__category')),
    sa.CheckConstraint("status IN ('open','accepted','dismissed','expired')", name=op.f('ck_ai_suggestions__ck_ai_suggestions__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_suggestions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_suggestions__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_ai_suggestions__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'generation_request_id'], ['ai_generation_requests.workspace_id', 'ai_generation_requests.id'], name='fk_ai_suggestions__generation_request', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_ai_suggestions__version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_ai_suggestions__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_suggestions')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_ai_suggestions__workspace_id_id'),
    comment='Explainable AI and editor recommendations for content assets.'
    )
    op.create_index('ix_ai_suggestions__workspace_asset_open', 'ai_suggestions', ['workspace_id', 'asset_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND status = 'open'"))
    op.create_index(op.f('ix_ai_suggestions__workspace_id'), 'ai_suggestions', ['workspace_id'], unique=False)
    op.create_table('ai_usage_records',
    sa.Column('generation_request_id', sa.UUID(), nullable=False),
    sa.Column('provider_id', sa.UUID(), nullable=False),
    sa.Column('model_id', sa.UUID(), nullable=False),
    sa.Column('input_tokens', sa.BigInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('output_tokens', sa.BigInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('total_tokens', sa.BigInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('provider_units', sa.Numeric(precision=20, scale=6), nullable=True),
    sa.Column('cost_amount', sa.Numeric(precision=20, scale=8), server_default=sa.text('0'), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('provider_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('cost_amount >= 0', name=op.f('ck_ai_usage_records__ck_ai_usage_records__cost_amount')),
    sa.CheckConstraint('input_tokens >= 0', name=op.f('ck_ai_usage_records__ck_ai_usage_records__input_tokens')),
    sa.CheckConstraint('output_tokens >= 0', name=op.f('ck_ai_usage_records__ck_ai_usage_records__output_tokens')),
    sa.CheckConstraint('provider_units IS NULL OR provider_units >= 0', name=op.f('ck_ai_usage_records__ck_ai_usage_records__provider_units')),
    sa.CheckConstraint('total_tokens >= 0', name=op.f('ck_ai_usage_records__ck_ai_usage_records__total_tokens')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_ai_usage_records__ck_ai_usage_records__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_usage_records__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['model_id'], ['ai_models.id'], name=op.f('fk_ai_usage_records__model_id__ai_models'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['provider_id'], ['ai_providers.id'], name=op.f('fk_ai_usage_records__provider_id__ai_providers'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_usage_records__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'generation_request_id'], ['ai_generation_requests.workspace_id', 'ai_generation_requests.id'], name='fk_ai_usage_records__generation_request', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_ai_usage_records__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_usage_records')),
    sa.UniqueConstraint('workspace_id', 'generation_request_id', 'provider_id', 'model_id', name='uq_ai_usage_records__request_provider_model'),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_ai_usage_records__workspace_id_id'),
    comment='Immutable normalized AI provider usage and cost evidence.'
    )
    op.create_index('ix_ai_usage_records__created_at', 'ai_usage_records', ['created_at', 'id'], unique=False)
    op.create_index('ix_ai_usage_records__model_created', 'ai_usage_records', ['model_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('ix_ai_usage_records__provider_created', 'ai_usage_records', ['provider_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('ix_ai_usage_records__workspace_created', 'ai_usage_records', ['workspace_id', sa.literal_column('created_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index(op.f('ix_ai_usage_records__workspace_id'), 'ai_usage_records', ['workspace_id'], unique=False)
    op.create_table('approval_steps',
    sa.Column('approval_request_id', sa.UUID(), nullable=False),
    sa.Column('step_order', sa.Integer(), nullable=False),
    sa.Column('reviewer_user_id', sa.UUID(), nullable=True),
    sa.Column('reviewer_role_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.Text(), server_default=sa.text("'pending'"), nullable=False),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'changes_requested', 'skipped')", name=op.f('ck_approval_steps__ck_approval_steps__status')),
    sa.CheckConstraint('(reviewer_user_id IS NOT NULL AND reviewer_role_id IS NULL) OR (reviewer_user_id IS NULL AND reviewer_role_id IS NOT NULL)', name=op.f('ck_approval_steps__ck_approval_steps__reviewer_selector')),
    sa.CheckConstraint('step_order > 0', name=op.f('ck_approval_steps__ck_approval_steps__step_order')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_approval_steps__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reviewer_role_id'], ['roles.id'], name=op.f('fk_approval_steps__reviewer_role_id__roles'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['reviewer_user_id'], ['users.id'], name=op.f('fk_approval_steps__reviewer_user_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_approval_steps__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'approval_request_id'], ['approval_requests.workspace_id', 'approval_requests.id'], name='fk_approval_steps__approval_request', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_approval_steps__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_approval_steps')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_approval_steps__workspace_id_id'),
    comment='Ordered reviewer decisions within an approval request.'
    )
    op.create_index(op.f('ix_approval_steps__workspace_id'), 'approval_steps', ['workspace_id'], unique=False)
    op.create_index('ix_approval_steps__workspace_reviewer_pending', 'approval_steps', ['workspace_id', 'reviewer_user_id', 'created_at', 'id'], unique=False, postgresql_where=sa.text("deleted_at IS NULL AND status = 'pending'"))
    op.create_index('uq_approval_steps__request_step_where_active', 'approval_steps', ['workspace_id', 'approval_request_id', 'step_order'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('publications',
    sa.Column('asset_id', sa.UUID(), nullable=False),
    sa.Column('version_id', sa.UUID(), nullable=False),
    sa.Column('approval_request_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.Text(), server_default=sa.text("'draft'"), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("status IN ('draft','ready','in_progress','completed','partially_failed','cancelled')", name=op.f('ck_publications__ck_publications__status')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_publications__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_publications__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'approval_request_id'], ['approval_requests.workspace_id', 'approval_requests.id'], name='fk_publications__approval_request', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_publications__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_publications__version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_publications__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publications')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_publications__workspace_id_id'),
    comment='Publish aggregate for approved content versions.'
    )
    op.create_index('ix_publications__workspace_asset_cursor', 'publications', ['workspace_id', 'asset_id', sa.literal_column('updated_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_publications__workspace_id'), 'publications', ['workspace_id'], unique=False)
    op.create_index('uq_publications__workspace_version_where_active', 'publications', ['workspace_id', 'version_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND status <> 'cancelled'"))
    op.create_table('ai_suggestion_actions',
    sa.Column('suggestion_id', sa.UUID(), nullable=False),
    sa.Column('action', sa.Text(), nullable=False),
    sa.Column('actor_id', sa.UUID(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("action IN ('accepted','dismissed','reopened','applied')", name=op.f('ck_ai_suggestion_actions__ck_ai_suggestion_actions__action')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_ai_suggestion_actions__ck_ai_suggestion_actions__immutable_uac')),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], name=op.f('fk_ai_suggestion_actions__actor_id__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_ai_suggestion_actions__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_ai_suggestion_actions__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'suggestion_id'], ['ai_suggestions.workspace_id', 'ai_suggestions.id'], name='fk_ai_suggestion_actions__suggestion', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_ai_suggestion_actions__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_suggestion_actions')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_ai_suggestion_actions__workspace_id_id'),
    comment='Immutable AI suggestion decision audit trail.'
    )
    op.create_index('ix_ai_suggestion_actions__created_at', 'ai_suggestion_actions', ['created_at', 'id'], unique=False)
    op.create_index(op.f('ix_ai_suggestion_actions__workspace_id'), 'ai_suggestion_actions', ['workspace_id'], unique=False)
    op.create_index('ix_ai_suggestion_actions__workspace_suggestion_created', 'ai_suggestion_actions', ['workspace_id', 'suggestion_id', 'created_at', 'id'], unique=False)
    op.create_table('publication_targets',
    sa.Column('publication_id', sa.UUID(), nullable=False),
    sa.Column('social_account_id', sa.UUID(), nullable=False),
    sa.Column('platform_id', sa.UUID(), nullable=False),
    sa.Column('content_version_id', sa.UUID(), nullable=False),
    sa.Column('generation_output_id', sa.UUID(), nullable=True),
    sa.Column('approval_state', sa.Text(), nullable=False),
    sa.Column('external_post_id', sa.Text(), nullable=True),
    sa.Column('external_post_url', sa.Text(), nullable=True),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("approval_state IN ('pending','approved','rejected','changes_requested','cancelled')", name=op.f('ck_publication_targets__ck_publication_targets__approval_state')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_publication_targets__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['platform_id'], ['social_platforms.id'], name=op.f('fk_publication_targets__platform_id__social_platforms'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_publication_targets__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'content_version_id'], ['content_versions.workspace_id', 'content_versions.id'], name='fk_publication_targets__content_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'generation_output_id'], ['ai_generation_outputs.workspace_id', 'ai_generation_outputs.id'], name='fk_publication_targets__generation_output', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'publication_id'], ['publications.workspace_id', 'publications.id'], name='fk_publication_targets__publication', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'social_account_id'], ['social_accounts.workspace_id', 'social_accounts.id'], name='fk_publication_targets__social_account', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_publication_targets__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publication_targets')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_publication_targets__workspace_id_id'),
    comment='Per-account platform rendition within a publication.'
    )
    op.create_index('ix_publication_targets__external_post', 'publication_targets', ['platform_id', 'external_post_id'], unique=False, postgresql_where=sa.text('external_post_id IS NOT NULL'))
    op.create_index('ix_publication_targets__workspace_account_published', 'publication_targets', ['workspace_id', 'social_account_id', sa.literal_column('published_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index(op.f('ix_publication_targets__workspace_id'), 'publication_targets', ['workspace_id'], unique=False)
    op.create_index('ix_publication_targets__workspace_publication', 'publication_targets', ['workspace_id', 'publication_id', 'id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('uq_publication_targets__workspace_publication_account_where_active', 'publication_targets', ['workspace_id', 'publication_id', 'social_account_id'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_table('content_performance_snapshots',
    sa.Column('content_asset_id', sa.UUID(), nullable=False),
    sa.Column('publication_target_id', sa.UUID(), nullable=False),
    sa.Column('snapshot_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('reach', sa.BigInteger(), nullable=True),
    sa.Column('engagements', sa.BigInteger(), nullable=True),
    sa.Column('clicks', sa.BigInteger(), nullable=True),
    sa.Column('conversions', sa.BigInteger(), nullable=True),
    sa.Column('engagement_rate', sa.Numeric(precision=12, scale=8), nullable=True),
    sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('clicks IS NULL OR clicks >= 0', name=op.f('ck_content_performance_snapshots__ck_content_performance_snapshots__clicks')),
    sa.CheckConstraint('conversions IS NULL OR conversions >= 0', name=op.f('ck_content_performance_snapshots__ck_content_performance_snapshots__conversions')),
    sa.CheckConstraint('engagement_rate IS NULL OR engagement_rate >= 0', name=op.f('ck_content_performance_snapshots__ck_content_performance_snapshots__engagement_rate')),
    sa.CheckConstraint('engagements IS NULL OR engagements >= 0', name=op.f('ck_content_performance_snapshots__ck_content_performance_snapshots__engagements')),
    sa.CheckConstraint('reach IS NULL OR reach >= 0', name=op.f('ck_content_performance_snapshots__ck_content_performance_snapshots__reach')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_content_performance_snapshots__ck_content_performance_snapshots__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_content_performance_snapshots__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_content_performance_snapshots__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'content_asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_content_performance_snapshots__asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'publication_target_id'], ['publication_targets.workspace_id', 'publication_targets.id'], name='fk_content_performance_snapshots__target', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_content_performance_snapshots__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_content_performance_snapshots')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_content_performance_snapshots__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'publication_target_id', 'snapshot_at', name='uq_content_performance_snapshots__target_time'),
    comment='Immutable ranked content-performance projection.'
    )
    op.create_index('ix_content_performance_snapshots__workspace_asset_time', 'content_performance_snapshots', ['workspace_id', 'content_asset_id', sa.literal_column('snapshot_at DESC')], unique=False)
    op.create_index(op.f('ix_content_performance_snapshots__workspace_id'), 'content_performance_snapshots', ['workspace_id'], unique=False)
    op.create_index('ix_content_performance_snapshots__workspace_target', 'content_performance_snapshots', ['workspace_id', 'publication_target_id'], unique=False)
    op.create_table('metric_observations',
    sa.Column('metric_definition_id', sa.UUID(), nullable=False),
    sa.Column('social_account_id', sa.UUID(), nullable=True),
    sa.Column('publication_target_id', sa.UUID(), nullable=True),
    sa.Column('content_asset_id', sa.UUID(), nullable=True),
    sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('bucket_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('bucket_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('value', sa.Numeric(precision=30, scale=10), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=True),
    sa.Column('is_estimated', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('source_fingerprint', sa.LargeBinary(), nullable=False),
    sa.Column('provider_fragment', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('bucket_end > bucket_start', name=op.f('ck_metric_observations__ck_metric_observations__bucket')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_metric_observations__ck_metric_observations__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_metric_observations__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['metric_definition_id'], ['metric_definitions.id'], name=op.f('fk_metric_observations__metric_definition_id__metric_definitions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_metric_observations__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'content_asset_id'], ['content_assets.workspace_id', 'content_assets.id'], name='fk_metric_observations__content_asset', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'publication_target_id'], ['publication_targets.workspace_id', 'publication_targets.id'], name='fk_metric_observations__publication_target', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'social_account_id'], ['social_accounts.workspace_id', 'social_accounts.id'], name='fk_metric_observations__social_account', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_metric_observations__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_metric_observations')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_metric_observations__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'metric_definition_id', 'source_fingerprint', name='uq_metric_observations__workspace_metric_fingerprint'),
    comment='Immutable raw normalized time-series analytics facts.'
    )
    op.create_index('brin_metric_observations__observed_at', 'metric_observations', ['observed_at'], unique=False, postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.create_index(op.f('ix_metric_observations__workspace_id'), 'metric_observations', ['workspace_id'], unique=False)
    op.create_index('ix_metric_observations__workspace_metric_time', 'metric_observations', ['workspace_id', 'metric_definition_id', sa.literal_column('observed_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_index('ix_metric_observations__workspace_publication_target_metric_time', 'metric_observations', ['workspace_id', 'publication_target_id', 'metric_definition_id', sa.literal_column('observed_at DESC')], unique=False)
    op.create_index('ix_metric_observations__workspace_social_account_metric_time', 'metric_observations', ['workspace_id', 'social_account_id', 'metric_definition_id', sa.literal_column('observed_at DESC')], unique=False)
    op.create_table('publication_schedules',
    sa.Column('publication_target_id', sa.UUID(), nullable=False),
    sa.Column('requested_local_at', sa.DateTime(), nullable=False),
    sa.Column('time_zone', sa.Text(), nullable=False),
    sa.Column('fold', sa.SmallInteger(), nullable=True),
    sa.Column('ambiguity_policy', sa.Text(), server_default=sa.text("'reject'"), nullable=False),
    sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False),
    sa.Column('state', sa.Text(), server_default=sa.text("'draft'"), nullable=False),
    sa.Column('priority', sa.Text(), server_default=sa.text("'normal'"), nullable=False),
    sa.Column('queue_order', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('dispatched_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("ambiguity_policy IN ('reject','earlier','later')", name=op.f('ck_publication_schedules__ck_publication_schedules__ambiguity_policy')),
    sa.CheckConstraint("priority IN ('low','normal','high')", name=op.f('ck_publication_schedules__ck_publication_schedules__priority')),
    sa.CheckConstraint("state IN ('draft','scheduled','paused','dispatched','completed','cancelled','failed')", name=op.f('ck_publication_schedules__ck_publication_schedules__state')),
    sa.CheckConstraint('fold IS NULL OR fold IN (0, 1)', name=op.f('ck_publication_schedules__ck_publication_schedules__fold')),
    sa.CheckConstraint('queue_order >= 0', name=op.f('ck_publication_schedules__ck_publication_schedules__queue_order')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_publication_schedules__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_publication_schedules__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'publication_target_id'], ['publication_targets.workspace_id', 'publication_targets.id'], name='fk_publication_schedules__publication_target', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_publication_schedules__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publication_schedules')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_publication_schedules__workspace_id_id'),
    comment='Authoritative requested and resolved publication schedule.'
    )
    op.create_index('ix_publication_schedules__due', 'publication_schedules', ['scheduled_for', sa.literal_column('priority DESC'), 'id'], unique=False, postgresql_include=['workspace_id', 'publication_target_id'], postgresql_where=sa.text("deleted_at IS NULL AND state = 'scheduled'"))
    op.create_index('ix_publication_schedules__workspace_calendar', 'publication_schedules', ['workspace_id', 'scheduled_for', 'id'], unique=False, postgresql_include=['state', 'publication_target_id'], postgresql_where=sa.text("deleted_at IS NULL AND state IN ('scheduled','paused','dispatched','completed','failed')"))
    op.create_index(op.f('ix_publication_schedules__workspace_id'), 'publication_schedules', ['workspace_id'], unique=False)
    op.create_index('ix_publication_schedules__workspace_target', 'publication_schedules', ['workspace_id', 'publication_target_id'], unique=False)
    op.create_index('uq_publication_schedules__active_target', 'publication_schedules', ['workspace_id', 'publication_target_id'], unique=True, postgresql_where=sa.text("deleted_at IS NULL AND state IN ('scheduled','paused','dispatched')"))
    op.create_table('publishing_jobs',
    sa.Column('schedule_id', sa.UUID(), nullable=False),
    sa.Column('target_id', sa.UUID(), nullable=False),
    sa.Column('state', sa.Text(), server_default=sa.text("'queued'"), nullable=False),
    sa.Column('idempotency_key', sa.Text(), nullable=False),
    sa.Column('priority', sa.SmallInteger(), server_default=sa.text('0'), nullable=False),
    sa.Column('available_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('attempt_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('max_attempts', sa.Integer(), server_default=sa.text('5'), nullable=False),
    sa.Column('last_error_code', sa.Text(), nullable=True),
    sa.Column('last_error_message', sa.Text(), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("state IN ('queued','leased','running','retry_wait','succeeded','failed','dead_lettered','cancelled')", name=op.f('ck_publishing_jobs__ck_publishing_jobs__state')),
    sa.CheckConstraint('attempt_count <= max_attempts', name=op.f('ck_publishing_jobs__ck_publishing_jobs__attempts_within_max')),
    sa.CheckConstraint('attempt_count >= 0', name=op.f('ck_publishing_jobs__ck_publishing_jobs__attempt_count')),
    sa.CheckConstraint('max_attempts > 0', name=op.f('ck_publishing_jobs__ck_publishing_jobs__max_attempts')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_publishing_jobs__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_publishing_jobs__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'schedule_id'], ['publication_schedules.workspace_id', 'publication_schedules.id'], name='fk_publishing_jobs__schedule', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'target_id'], ['publication_targets.workspace_id', 'publication_targets.id'], name='fk_publishing_jobs__target', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_publishing_jobs__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publishing_jobs')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_publishing_jobs__workspace_id_id'),
    comment='Durable publish execution with bounded retries.'
    )
    op.create_index('ix_publishing_jobs__claim', 'publishing_jobs', ['available_at', sa.literal_column('priority DESC'), 'id'], unique=False, postgresql_include=['workspace_id'], postgresql_where=sa.text("deleted_at IS NULL AND state IN ('queued','retry_wait')"))
    op.create_index(op.f('ix_publishing_jobs__workspace_id'), 'publishing_jobs', ['workspace_id'], unique=False)
    op.create_index('ix_publishing_jobs__workspace_schedule', 'publishing_jobs', ['workspace_id', 'schedule_id'], unique=False)
    op.create_index('ix_publishing_jobs__workspace_status_cursor', 'publishing_jobs', ['workspace_id', 'state', sa.literal_column('updated_at DESC'), sa.literal_column('id DESC')], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('ix_publishing_jobs__workspace_target', 'publishing_jobs', ['workspace_id', 'target_id'], unique=False)
    op.create_index('uq_publishing_jobs__workspace_idempotency', 'publishing_jobs', ['workspace_id', 'idempotency_key'], unique=True)
    op.create_table('job_leases',
    sa.Column('publishing_job_id', sa.UUID(), nullable=False),
    sa.Column('lease_owner', sa.Text(), nullable=False),
    sa.Column('lease_token', sa.UUID(), nullable=False),
    sa.Column('leased_until', sa.DateTime(timezone=True), nullable=False),
    sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('acquired_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_job_leases__ck_job_leases__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_job_leases__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_job_leases__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'publishing_job_id'], ['publishing_jobs.workspace_id', 'publishing_jobs.id'], name='fk_job_leases__publishing_job', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_job_leases__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_job_leases')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_job_leases__workspace_id_id'),
    comment='Short-lived publishing job worker leases and heartbeats.'
    )
    op.create_index('ix_job_leases__created_at', 'job_leases', ['created_at', 'id'], unique=False)
    op.create_index('ix_job_leases__expired', 'job_leases', ['leased_until', 'id'], unique=False)
    op.create_index(op.f('ix_job_leases__workspace_id'), 'job_leases', ['workspace_id'], unique=False)
    op.create_index('ix_job_leases__workspace_job', 'job_leases', ['workspace_id', 'publishing_job_id'], unique=False)
    op.create_index('uq_job_leases__lease_token', 'job_leases', ['lease_token'], unique=True)
    op.create_table('publication_status_history',
    sa.Column('publication_target_id', sa.UUID(), nullable=False),
    sa.Column('schedule_id', sa.UUID(), nullable=True),
    sa.Column('job_id', sa.UUID(), nullable=True),
    sa.Column('state_type', sa.Text(), nullable=False),
    sa.Column('from_state', sa.Text(), nullable=True),
    sa.Column('to_state', sa.Text(), nullable=False),
    sa.Column('reason_code', sa.Text(), nullable=True),
    sa.Column('reason_text', sa.Text(), nullable=True),
    sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("state_type IN ('approval','schedule','job','provider')", name=op.f('ck_publication_status_history__ck_publication_status_history__state_type')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_publication_status_history__ck_publication_status_history__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_publication_status_history__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_publication_status_history__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'job_id'], ['publishing_jobs.workspace_id', 'publishing_jobs.id'], name='fk_publication_status_history__job', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'publication_target_id'], ['publication_targets.workspace_id', 'publication_targets.id'], name='fk_publication_status_history__publication_target', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id', 'schedule_id'], ['publication_schedules.workspace_id', 'publication_schedules.id'], name='fk_publication_status_history__schedule', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_publication_status_history__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publication_status_history')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_publication_status_history__workspace_id_id'),
    comment='Append-only publication target status timeline.'
    )
    op.create_index('ix_publication_status_history__occurred_at', 'publication_status_history', ['occurred_at', 'id'], unique=False)
    op.create_index(op.f('ix_publication_status_history__workspace_id'), 'publication_status_history', ['workspace_id'], unique=False)
    op.create_index('ix_publication_status_history__workspace_target_time', 'publication_status_history', ['workspace_id', 'publication_target_id', sa.literal_column('occurred_at DESC'), sa.literal_column('id DESC')], unique=False)
    op.create_table('publishing_attempts',
    sa.Column('publishing_job_id', sa.UUID(), nullable=False),
    sa.Column('attempt_no', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('outcome', sa.Text(), nullable=False),
    sa.Column('provider_request_id', sa.Text(), nullable=True),
    sa.Column('http_status', sa.Integer(), nullable=True),
    sa.Column('error_code', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('response_fragment', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False),
    sa.CheckConstraint("outcome IN ('succeeded','transient_failure','permanent_failure','timeout','cancelled')", name=op.f('ck_publishing_attempts__ck_publishing_attempts__outcome')),
    sa.CheckConstraint('attempt_no > 0', name=op.f('ck_publishing_attempts__ck_publishing_attempts__attempt_no')),
    sa.CheckConstraint('http_status IS NULL OR (http_status >= 100 AND http_status <= 599)', name=op.f('ck_publishing_attempts__ck_publishing_attempts__http_status')),
    sa.CheckConstraint('updated_at = created_at AND updated_by IS NOT DISTINCT FROM created_by AND deleted_at IS NULL AND version = 1', name=op.f('ck_publishing_attempts__ck_publishing_attempts__immutable_uac')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_publishing_attempts__created_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name=op.f('fk_publishing_attempts__updated_by__users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id', 'publishing_job_id'], ['publishing_jobs.workspace_id', 'publishing_jobs.id'], name='fk_publishing_attempts__publishing_job', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_publishing_attempts__workspace_id__workspaces'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_publishing_attempts')),
    sa.UniqueConstraint('workspace_id', 'id', name='uq_publishing_attempts__workspace_id_id'),
    sa.UniqueConstraint('workspace_id', 'publishing_job_id', 'attempt_no', name='uq_publishing_attempts__job_attempt'),
    comment='Immutable provider publishing attempt history.'
    )
    op.create_index('ix_publishing_attempts__created_at', 'publishing_attempts', ['created_at', 'id'], unique=False)
    op.create_index(op.f('ix_publishing_attempts__workspace_id'), 'publishing_attempts', ['workspace_id'], unique=False)
    op.create_index('ix_publishing_attempts__workspace_job_attempt', 'publishing_attempts', ['workspace_id', 'publishing_job_id', sa.literal_column('attempt_no DESC')], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index('ix_publishing_attempts__workspace_job_attempt', table_name='publishing_attempts')
    op.drop_index(op.f('ix_publishing_attempts__workspace_id'), table_name='publishing_attempts')
    op.drop_index('ix_publishing_attempts__created_at', table_name='publishing_attempts')
    op.drop_table('publishing_attempts')
    op.drop_index('ix_publication_status_history__workspace_target_time', table_name='publication_status_history')
    op.drop_index(op.f('ix_publication_status_history__workspace_id'), table_name='publication_status_history')
    op.drop_index('ix_publication_status_history__occurred_at', table_name='publication_status_history')
    op.drop_table('publication_status_history')
    op.drop_index('uq_job_leases__lease_token', table_name='job_leases')
    op.drop_index('ix_job_leases__workspace_job', table_name='job_leases')
    op.drop_index(op.f('ix_job_leases__workspace_id'), table_name='job_leases')
    op.drop_index('ix_job_leases__expired', table_name='job_leases')
    op.drop_index('ix_job_leases__created_at', table_name='job_leases')
    op.drop_table('job_leases')
    op.drop_index('uq_publishing_jobs__workspace_idempotency', table_name='publishing_jobs')
    op.drop_index('ix_publishing_jobs__workspace_target', table_name='publishing_jobs')
    op.drop_index('ix_publishing_jobs__workspace_status_cursor', table_name='publishing_jobs', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_publishing_jobs__workspace_schedule', table_name='publishing_jobs')
    op.drop_index(op.f('ix_publishing_jobs__workspace_id'), table_name='publishing_jobs')
    op.drop_index('ix_publishing_jobs__claim', table_name='publishing_jobs', postgresql_include=['workspace_id'], postgresql_where=sa.text("deleted_at IS NULL AND state IN ('queued','retry_wait')"))
    op.drop_table('publishing_jobs')
    op.drop_index('uq_publication_schedules__active_target', table_name='publication_schedules', postgresql_where=sa.text("deleted_at IS NULL AND state IN ('scheduled','paused','dispatched')"))
    op.drop_index('ix_publication_schedules__workspace_target', table_name='publication_schedules')
    op.drop_index(op.f('ix_publication_schedules__workspace_id'), table_name='publication_schedules')
    op.drop_index('ix_publication_schedules__workspace_calendar', table_name='publication_schedules', postgresql_include=['state', 'publication_target_id'], postgresql_where=sa.text("deleted_at IS NULL AND state IN ('scheduled','paused','dispatched','completed','failed')"))
    op.drop_index('ix_publication_schedules__due', table_name='publication_schedules', postgresql_include=['workspace_id', 'publication_target_id'], postgresql_where=sa.text("deleted_at IS NULL AND state = 'scheduled'"))
    op.drop_table('publication_schedules')
    op.drop_index('ix_metric_observations__workspace_social_account_metric_time', table_name='metric_observations')
    op.drop_index('ix_metric_observations__workspace_publication_target_metric_time', table_name='metric_observations')
    op.drop_index('ix_metric_observations__workspace_metric_time', table_name='metric_observations')
    op.drop_index(op.f('ix_metric_observations__workspace_id'), table_name='metric_observations')
    op.drop_index('brin_metric_observations__observed_at', table_name='metric_observations', postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.drop_table('metric_observations')
    op.drop_index('ix_content_performance_snapshots__workspace_target', table_name='content_performance_snapshots')
    op.drop_index(op.f('ix_content_performance_snapshots__workspace_id'), table_name='content_performance_snapshots')
    op.drop_index('ix_content_performance_snapshots__workspace_asset_time', table_name='content_performance_snapshots')
    op.drop_table('content_performance_snapshots')
    op.drop_index('uq_publication_targets__workspace_publication_account_where_active', table_name='publication_targets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_publication_targets__workspace_publication', table_name='publication_targets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_publication_targets__workspace_id'), table_name='publication_targets')
    op.drop_index('ix_publication_targets__workspace_account_published', table_name='publication_targets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_publication_targets__external_post', table_name='publication_targets', postgresql_where=sa.text('external_post_id IS NOT NULL'))
    op.drop_table('publication_targets')
    op.drop_index('ix_ai_suggestion_actions__workspace_suggestion_created', table_name='ai_suggestion_actions')
    op.drop_index(op.f('ix_ai_suggestion_actions__workspace_id'), table_name='ai_suggestion_actions')
    op.drop_index('ix_ai_suggestion_actions__created_at', table_name='ai_suggestion_actions')
    op.drop_table('ai_suggestion_actions')
    op.drop_index('uq_publications__workspace_version_where_active', table_name='publications', postgresql_where=sa.text("deleted_at IS NULL AND status <> 'cancelled'"))
    op.drop_index(op.f('ix_publications__workspace_id'), table_name='publications')
    op.drop_index('ix_publications__workspace_asset_cursor', table_name='publications', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('publications')
    op.drop_index('uq_approval_steps__request_step_where_active', table_name='approval_steps', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_approval_steps__workspace_reviewer_pending', table_name='approval_steps', postgresql_where=sa.text("deleted_at IS NULL AND status = 'pending'"))
    op.drop_index(op.f('ix_approval_steps__workspace_id'), table_name='approval_steps')
    op.drop_table('approval_steps')
    op.drop_index(op.f('ix_ai_usage_records__workspace_id'), table_name='ai_usage_records')
    op.drop_index('ix_ai_usage_records__workspace_created', table_name='ai_usage_records')
    op.drop_index('ix_ai_usage_records__provider_created', table_name='ai_usage_records')
    op.drop_index('ix_ai_usage_records__model_created', table_name='ai_usage_records')
    op.drop_index('ix_ai_usage_records__created_at', table_name='ai_usage_records')
    op.drop_table('ai_usage_records')
    op.drop_index(op.f('ix_ai_suggestions__workspace_id'), table_name='ai_suggestions')
    op.drop_index('ix_ai_suggestions__workspace_asset_open', table_name='ai_suggestions', postgresql_where=sa.text("deleted_at IS NULL AND status = 'open'"))
    op.drop_table('ai_suggestions')
    op.drop_index('ix_ai_generation_outputs__workspace_request_sequence', table_name='ai_generation_outputs')
    op.drop_index(op.f('ix_ai_generation_outputs__workspace_id'), table_name='ai_generation_outputs')
    op.drop_index('ix_ai_generation_outputs__materialized_version', table_name='ai_generation_outputs', postgresql_where=sa.text('materialized_version_id IS NOT NULL'))
    op.drop_index('ix_ai_generation_outputs__created_at', table_name='ai_generation_outputs')
    op.drop_table('ai_generation_outputs')
    op.drop_index('uq_content_drafts__workspace_asset_where_active', table_name='content_drafts', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_content_drafts__workspace_id'), table_name='content_drafts')
    op.drop_table('content_drafts')
    op.drop_index('ix_comments__workspace_parent', table_name='comments', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_comments__workspace_id'), table_name='comments')
    op.drop_index('ix_comments__workspace_asset_created_cursor', table_name='comments', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('comments')
    op.drop_index('uq_approval_requests__one_pending_per_version', table_name='approval_requests', postgresql_where=sa.text("deleted_at IS NULL AND status = 'pending'"))
    op.drop_index('ix_approval_requests__workspace_pending', table_name='approval_requests', postgresql_where=sa.text("deleted_at IS NULL AND status = 'pending'"))
    op.drop_index(op.f('ix_approval_requests__workspace_id'), table_name='approval_requests')
    op.drop_table('approval_requests')
    op.drop_index('uq_ai_generation_requests__workspace_idempotency', table_name='ai_generation_requests')
    op.drop_index(op.f('ix_ai_generation_requests__workspace_id'), table_name='ai_generation_requests')
    op.drop_index('ix_ai_generation_requests__workspace_due', table_name='ai_generation_requests', postgresql_where=sa.text("deleted_at IS NULL AND status = 'queued'"))
    op.drop_index('ix_ai_generation_requests__workspace_asset_cursor', table_name='ai_generation_requests', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_ai_generation_requests__provider_request', table_name='ai_generation_requests', postgresql_where=sa.text('provider_request_id IS NOT NULL'))
    op.drop_table('ai_generation_requests')
    op.drop_index('ix_videos__workspace_transcript_status', table_name='videos', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_videos__workspace_id'), table_name='videos')
    op.drop_table('videos')
    op.drop_index(op.f('ix_thumbnails__workspace_id'), table_name='thumbnails')
    op.drop_table('thumbnails')
    op.drop_index(op.f('ix_posters__workspace_id'), table_name='posters')
    op.drop_table('posters')
    op.drop_index(op.f('ix_content_versions__workspace_id'), table_name='content_versions')
    op.drop_index('ix_content_versions__workspace_asset_version_desc', table_name='content_versions', postgresql_include=['created_at', 'origin', 'content_hash'])
    op.drop_table('content_versions')
    op.drop_index('ix_content_relations__workspace_target', table_name='content_relations')
    op.drop_index('ix_content_relations__workspace_source', table_name='content_relations')
    op.drop_index(op.f('ix_content_relations__workspace_id'), table_name='content_relations')
    op.drop_table('content_relations')
    op.drop_index(op.f('ix_collection_items__workspace_id'), table_name='collection_items')
    op.drop_index('ix_collection_items__workspace_collection_position', table_name='collection_items')
    op.drop_index('ix_collection_items__workspace_asset', table_name='collection_items')
    op.drop_table('collection_items')
    op.drop_index('ix_asset_tags__workspace_tag_asset', table_name='asset_tags')
    op.drop_index(op.f('ix_asset_tags__workspace_id'), table_name='asset_tags')
    op.drop_index('ix_asset_tags__workspace_asset_tag', table_name='asset_tags')
    op.drop_table('asset_tags')
    op.drop_index('ix_asset_storage_objects__workspace_object', table_name='asset_storage_objects')
    op.drop_index(op.f('ix_asset_storage_objects__workspace_id'), table_name='asset_storage_objects')
    op.drop_index('ix_asset_storage_objects__workspace_asset_purpose', table_name='asset_storage_objects')
    op.drop_table('asset_storage_objects')
    op.drop_index('uq_asset_categories__one_primary', table_name='asset_categories', postgresql_where=sa.text('is_primary'))
    op.drop_index(op.f('ix_asset_categories__workspace_id'), table_name='asset_categories')
    op.drop_index('ix_asset_categories__workspace_category_asset', table_name='asset_categories')
    op.drop_index('ix_asset_categories__workspace_asset_category', table_name='asset_categories')
    op.drop_table('asset_categories')
    op.drop_index(op.f('ix_articles__workspace_id'), table_name='articles')
    op.drop_table('articles')
    op.drop_index(op.f('ix_social_account_snapshots__workspace_id'), table_name='social_account_snapshots')
    op.drop_index('ix_social_account_snapshots__workspace_account_time', table_name='social_account_snapshots')
    op.drop_table('social_account_snapshots')
    op.drop_index('uq_social_account_settings__workspace_account_where_active', table_name='social_account_settings', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_social_account_settings__workspace_id'), table_name='social_account_settings')
    op.drop_index('ix_social_account_settings__workspace_account', table_name='social_account_settings')
    op.drop_table('social_account_settings')
    op.drop_index(op.f('ix_social_account_permissions__workspace_id'), table_name='social_account_permissions')
    op.drop_index('ix_social_account_permissions__workspace_account', table_name='social_account_permissions')
    op.drop_table('social_account_permissions')
    op.drop_index('uq_settings__workspace_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'workspace'"))
    op.drop_index('uq_settings__user_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'user'"))
    op.drop_index('uq_settings__social_account_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'social_account'"))
    op.drop_index('uq_settings__project_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'project'"))
    op.drop_index('uq_settings__organization_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'organization'"))
    op.drop_index('ix_settings__workspace_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'workspace'"))
    op.drop_index('ix_settings__user_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'user'"))
    op.drop_index('ix_settings__social_account_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'social_account'"))
    op.drop_index('ix_settings__project_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'project'"))
    op.drop_index('ix_settings__organization_definition', table_name='settings', postgresql_where=sa.text("deleted_at IS NULL AND scope_type = 'organization'"))
    op.drop_table('settings')
    op.drop_index(op.f('ix_role_permissions__workspace_id'), table_name='role_permissions')
    op.drop_index('ix_role_permissions__role_id', table_name='role_permissions')
    op.drop_index('ix_role_permissions__permission_id', table_name='role_permissions')
    op.drop_table('role_permissions')
    op.drop_index('ix_project_members__workspace_user', table_name='project_members')
    op.drop_index('ix_project_members__workspace_project', table_name='project_members')
    op.drop_index(op.f('ix_project_members__workspace_id'), table_name='project_members')
    op.drop_table('project_members')
    op.drop_index('uq_oauth_token_vaults__workspace_account_where_active', table_name='oauth_token_vaults', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_oauth_token_vaults__workspace_id'), table_name='oauth_token_vaults')
    op.drop_index('ix_oauth_token_vaults__workspace_account', table_name='oauth_token_vaults')
    op.drop_index('ix_oauth_token_vaults__expiry_due', table_name='oauth_token_vaults', postgresql_where=sa.text("deleted_at IS NULL AND status IN ('active','expiring_soon')"))
    op.drop_table('oauth_token_vaults')
    op.drop_index('uq_notification_deliveries__notification_recipient_channel_where_active', table_name='notification_deliveries', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_notification_deliveries__workspace_id'), table_name='notification_deliveries')
    op.drop_index('ix_notification_deliveries__due', table_name='notification_deliveries', postgresql_include=['workspace_id', 'channel'], postgresql_where=sa.text("deleted_at IS NULL AND status IN ('pending','failed')"))
    op.drop_table('notification_deliveries')
    op.drop_index('ix_membership_roles__workspace_role', table_name='membership_roles')
    op.drop_index('ix_membership_roles__workspace_membership', table_name='membership_roles')
    op.drop_index(op.f('ix_membership_roles__workspace_id'), table_name='membership_roles')
    op.drop_table('membership_roles')
    op.drop_index(op.f('ix_data_exports__workspace_id'), table_name='data_exports')
    op.drop_index('ix_data_exports__workspace_cursor', table_name='data_exports', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_data_exports__expiry', table_name='data_exports', postgresql_where=sa.text("deleted_at IS NULL AND state IN ('ready','expired')"))
    op.drop_table('data_exports')
    op.drop_index('ix_content_assets__workspace_updated_cursor', table_name='content_assets', postgresql_include=['title', 'asset_type', 'lifecycle_status', 'owner_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_content_assets__workspace_type_status_updated', table_name='content_assets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_content_assets__workspace_project_updated', table_name='content_assets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_content_assets__workspace_owner_updated', table_name='content_assets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_content_assets__workspace_id'), table_name='content_assets')
    op.drop_index('ix_content_assets__workspace_folder_updated', table_name='content_assets', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_content_assets__search_gin', table_name='content_assets', postgresql_using='gin')
    op.drop_table('content_assets')
    op.drop_index('uq_workspace_memberships__workspace_user_where_active', table_name='workspace_memberships', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_workspace_memberships__workspace_status_user', table_name='workspace_memberships', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_workspace_memberships__workspace_id'), table_name='workspace_memberships')
    op.drop_table('workspace_memberships')
    op.drop_index('uq_webhook_receipts__provider_payload_hash', table_name='webhook_receipts', postgresql_where=sa.text("external_event_id = ''"))
    op.drop_index('uq_webhook_receipts__provider_external', table_name='webhook_receipts')
    op.drop_index('ix_webhook_receipts__unprocessed', table_name='webhook_receipts', postgresql_where=sa.text("processed_at IS NULL AND processing_status IN ('received','failed')"))
    op.drop_table('webhook_receipts')
    op.drop_index(op.f('ix_usage_events__workspace_id'), table_name='usage_events')
    op.drop_index('ix_usage_events__workspace_dimension_time', table_name='usage_events')
    op.drop_index('ix_usage_events__organization_dimension_time', table_name='usage_events')
    op.drop_index('brin_usage_events__occurred_at', table_name='usage_events', postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.drop_table('usage_events')
    op.drop_index('uq_tags__workspace_name_where_active', table_name='tags', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_tags__workspace_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index('uq_subscription_items__subscription_price_dimension_where_active', table_name='subscription_items', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_subscription_items__organization_subscription', table_name='subscription_items', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_subscription_items__organization_id'), table_name='subscription_items')
    op.drop_table('subscription_items')
    op.drop_index('uq_storage_objects__workspace_object_key_where_active', table_name='storage_objects', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_storage_objects__workspace_scan_due', table_name='storage_objects', postgresql_where=sa.text("deleted_at IS NULL AND scan_status IN ('pending','failed')"))
    op.drop_index(op.f('ix_storage_objects__workspace_id'), table_name='storage_objects')
    op.drop_index('ix_storage_objects__workspace_checksum', table_name='storage_objects', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('storage_objects')
    op.drop_index('uq_social_content_templates__scope_platform_name_version', table_name='social_content_templates', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_social_content_templates__workspace_id'), table_name='social_content_templates')
    op.drop_table('social_content_templates')
    op.drop_index('uq_social_accounts__workspace_platform_external_where_active', table_name='social_accounts', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_social_accounts__workspace_sync_due', table_name='social_accounts', postgresql_where=sa.text("deleted_at IS NULL AND connection_status = 'connected'"))
    op.drop_index(op.f('ix_social_accounts__workspace_id'), table_name='social_accounts')
    op.drop_index('ix_social_accounts__workspace_health', table_name='social_accounts', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('social_accounts')
    op.drop_index('uq_saved_views__workspace_owner_type_name_where_active', table_name='saved_views', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_saved_views__workspace_owner_type', table_name='saved_views', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_saved_views__workspace_id'), table_name='saved_views')
    op.drop_table('saved_views')
    op.drop_index('uq_roles__workspace_code_where_active', table_name='roles', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('uq_roles__code_where_global_active', table_name='roles', postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NULL'))
    op.drop_index(op.f('ix_roles__workspace_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index('uq_quota_policies__scope_dimension_effective', table_name='quota_policies', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_quota_policies__workspace_dimension_effective', table_name='quota_policies', postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NOT NULL'))
    op.drop_index(op.f('ix_quota_policies__organization_id'), table_name='quota_policies')
    op.drop_index('ix_quota_policies__organization_dimension_effective', table_name='quota_policies', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('quota_policies')
    op.drop_index('uq_quota_periods__scope_dimension_period', table_name='quota_periods', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_quota_periods__workspace_dimension_period', table_name='quota_periods', postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NOT NULL'))
    op.drop_index(op.f('ix_quota_periods__organization_id'), table_name='quota_periods')
    op.drop_index('ix_quota_periods__organization_dimension_period', table_name='quota_periods', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('quota_periods')
    op.drop_index('uq_projects__workspace_slug_where_active', table_name='projects', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_projects__workspace_updated_cursor', table_name='projects', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_projects__workspace_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index('ix_outbox_events__publish_due', table_name='outbox_events', postgresql_where=sa.text('published_at IS NULL'))
    op.drop_index('ix_outbox_events__aggregate', table_name='outbox_events')
    op.drop_index('brin_outbox_events__occurred_at', table_name='outbox_events', postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.drop_table('outbox_events')
    op.drop_index('uq_notifications__workspace_recipient_dedupe_where_active', table_name='notifications', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_notifications__workspace_recipient_unread', table_name='notifications', postgresql_where=sa.text('deleted_at IS NULL AND read_at IS NULL'))
    op.drop_index('ix_notifications__workspace_recipient_cursor', table_name='notifications', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_notifications__workspace_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index('uq_notification_templates__workspace_type_channel_locale_version', table_name='notification_templates', postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NOT NULL'))
    op.drop_index('uq_notification_templates__global_type_channel_locale_version', table_name='notification_templates', postgresql_where=sa.text('deleted_at IS NULL AND workspace_id IS NULL'))
    op.drop_index('ix_notification_templates__active_lookup', table_name='notification_templates', postgresql_where=sa.text('deleted_at IS NULL AND is_active'))
    op.drop_table('notification_templates')
    op.drop_index('uq_notification_preferences__workspace_user_type_channel_where_active', table_name='notification_preferences', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_notification_preferences__workspace_id'), table_name='notification_preferences')
    op.drop_table('notification_preferences')
    op.drop_index('uq_inbox_messages__consumer_message', table_name='inbox_messages')
    op.drop_index('ix_inbox_messages__retention', table_name='inbox_messages', postgresql_where=sa.text('processed_at IS NOT NULL'))
    op.drop_table('inbox_messages')
    op.drop_index('uq_idempotency_keys__scope_principal_operation_key_where_active', table_name='idempotency_keys', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_idempotency_keys__workspace_id'), table_name='idempotency_keys')
    op.drop_index('ix_idempotency_keys__expiry', table_name='idempotency_keys')
    op.drop_table('idempotency_keys')
    op.drop_index('ix_folders__workspace_parent_name', table_name='folders', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_folders__workspace_id'), table_name='folders')
    op.drop_table('folders')
    op.drop_index('uq_dead_letters__workspace_source_where_active', table_name='dead_letters', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_dead_letters__workspace_pending', table_name='dead_letters', postgresql_where=sa.text("deleted_at IS NULL AND replay_state = 'pending'"))
    op.drop_index(op.f('ix_dead_letters__workspace_id'), table_name='dead_letters')
    op.drop_table('dead_letters')
    op.drop_index('uq_collections__workspace_name_where_active', table_name='collections', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_collections__workspace_updated_cursor', table_name='collections', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_collections__workspace_id'), table_name='collections')
    op.drop_table('collections')
    op.drop_index('uq_categories__workspace_slug_where_active', table_name='categories', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_categories__workspace_parent', table_name='categories', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_categories__workspace_id'), table_name='categories')
    op.drop_table('categories')
    op.drop_index('uq_brand_profiles__workspace_name_where_active', table_name='brand_profiles', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('uq_brand_profiles__one_default', table_name='brand_profiles', postgresql_where=sa.text('deleted_at IS NULL AND is_default'))
    op.drop_index(op.f('ix_brand_profiles__workspace_id'), table_name='brand_profiles')
    op.drop_table('brand_profiles')
    op.drop_index('uq_background_jobs__scope_type_key_where_active', table_name='background_jobs', postgresql_nulls_not_distinct=True, postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_background_jobs__expired_lease', table_name='background_jobs', postgresql_where=sa.text("deleted_at IS NULL AND state IN ('leased','running')"))
    op.drop_index('ix_background_jobs__claim', table_name='background_jobs', postgresql_include=['workspace_id', 'queue_name'], postgresql_where=sa.text("deleted_at IS NULL AND state IN ('queued','retry_wait')"))
    op.drop_table('background_jobs')
    op.drop_index('ix_audit_logs__workspace_time', table_name='audit_logs')
    op.drop_index('ix_audit_logs__organization_time', table_name='audit_logs')
    op.drop_index('brin_audit_logs__occurred_at', table_name='audit_logs', postgresql_using='brin', postgresql_with={'pages_per_range': 64})
    op.drop_table('audit_logs')
    op.drop_index('uq_analytics_snapshots__identity', table_name='analytics_snapshots')
    op.drop_index('ix_analytics_snapshots__workspace_type_period_end', table_name='analytics_snapshots')
    op.drop_index(op.f('ix_analytics_snapshots__workspace_id'), table_name='analytics_snapshots')
    op.drop_table('analytics_snapshots')
    op.drop_index('ix_ai_prompt_templates__workspace_name_version_desc', table_name='ai_prompt_templates', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_ai_prompt_templates__workspace_id'), table_name='ai_prompt_templates')
    op.drop_table('ai_prompt_templates')
    op.drop_index(op.f('ix_activity_logs__workspace_id'), table_name='activity_logs')
    op.drop_index('ix_activity_logs__workspace_cursor', table_name='activity_logs', postgresql_where=sa.text('deleted_at IS NULL AND hidden_at IS NULL'))
    op.drop_table('activity_logs')
    op.drop_index('uq_workspaces__organization_slug_where_active', table_name='workspaces', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_workspaces__organization_id'), table_name='workspaces')
    op.drop_table('workspaces')
    op.drop_index('uq_subscriptions__provider_external', table_name='subscriptions', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('uq_subscriptions__one_current_org', table_name='subscriptions', postgresql_where=sa.text("deleted_at IS NULL AND status IN ('trialing','active','past_due','paused')"))
    op.drop_index(op.f('ix_subscriptions__organization_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index('ix_social_platform_capabilities__created_at', table_name='social_platform_capabilities')
    op.drop_table('social_platform_capabilities')
    op.drop_index('uq_organization_memberships__organization_user_where_active', table_name='organization_memberships', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('ix_organization_memberships__organization_user', table_name='organization_memberships', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_organization_memberships__organization_id'), table_name='organization_memberships')
    op.drop_table('organization_memberships')
    op.drop_table('metric_definitions')
    op.drop_index('uq_billing_events__provider_event', table_name='billing_events')
    op.drop_index('ix_billing_events__organization_time', table_name='billing_events')
    op.drop_index(op.f('ix_billing_events__organization_id'), table_name='billing_events')
    op.drop_table('billing_events')
    op.drop_index('uq_billing_customers__provider_external', table_name='billing_customers', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('uq_billing_customers__organization_provider_where_active', table_name='billing_customers', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index(op.f('ix_billing_customers__organization_id'), table_name='billing_customers')
    op.drop_table('billing_customers')
    op.drop_index('uq_ai_models__provider_model_code', table_name='ai_models')
    op.drop_index('ix_ai_models__provider_status', table_name='ai_models')
    op.drop_table('ai_models')
    op.drop_index('uq_user_sessions__session_hash', table_name='user_sessions')
    op.drop_index('ix_user_sessions__user_expires', table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_table('usage_dimensions')
    op.drop_index('uq_social_platforms__code', table_name='social_platforms')
    op.drop_table('social_platforms')
    op.drop_table('setting_definitions')
    op.drop_table('permissions')
    op.drop_index('uq_organizations__slug_where_active', table_name='organizations', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_table('organizations')
    op.drop_table('notification_types')
    op.drop_index('uq_external_identities__user_issuer_where_active', table_name='external_identities', postgresql_where=sa.text('deleted_at IS NULL'))
    op.drop_index('uq_external_identities__issuer_subject', table_name='external_identities')
    op.drop_table('external_identities')
    op.drop_index('uq_ai_providers__code', table_name='ai_providers')
    op.drop_table('ai_providers')
    op.drop_index('uq_users__email_where_active', table_name='users', postgresql_where=sa.text('deleted_at IS NULL AND email IS NOT NULL'))
    op.drop_table('users')
    # ### end Alembic commands ###
    op.execute("DROP EXTENSION IF EXISTS citext")
