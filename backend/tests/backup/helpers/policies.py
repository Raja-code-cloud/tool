"""Backup policy constants and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DeploymentEnvironment(StrEnum):
    DEV = "dev"
    QA = "qa"
    PROD = "prod"
    DR = "dr"


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    """Documented backup retention targets per environment."""

    postgresql_pitr_days: int
    blob_soft_delete_days: int
    log_retention_days: int


RETENTION_POLICIES: dict[DeploymentEnvironment, RetentionPolicy] = {
    DeploymentEnvironment.DEV: RetentionPolicy(
        postgresql_pitr_days=7,
        blob_soft_delete_days=7,
        log_retention_days=30,
    ),
    DeploymentEnvironment.QA: RetentionPolicy(
        postgresql_pitr_days=14,
        blob_soft_delete_days=14,
        log_retention_days=30,
    ),
    DeploymentEnvironment.PROD: RetentionPolicy(
        postgresql_pitr_days=35,
        blob_soft_delete_days=30,
        log_retention_days=90,
    ),
    DeploymentEnvironment.DR: RetentionPolicy(
        postgresql_pitr_days=35,
        blob_soft_delete_days=30,
        log_retention_days=90,
    ),
}

BACKUP_COMPONENTS: frozenset[str] = frozenset(
    {
        "PostgreSQL",
        "Blob storage",
        "Redis",
        "Key Vault",
        "Container images",
    }
)

KEY_VAULT_SECRETS: tuple[str, ...] = (
    "CCH-DATABASE-URL",
    "CCH-MIGRATION-DATABASE-URL",
    "CCH-REDIS-URL",
)

BLOB_CONTAINERS: tuple[str, ...] = (
    "posters",
    "articles",
    "videos",
    "thumbnails",
    "generated-content",
    "temp",
    "exports",
    "logs",
)
