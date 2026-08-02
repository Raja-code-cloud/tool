"""Shared test fixtures for integration and end-to-end workflows."""

from tests.fixtures.app import (
    bound_principal,
    build_principal,
    create_api_test_app,
    workspace_headers,
)
from tests.fixtures.auth import admin_actor, all_permissions, issue_access_token, workflow_actor
from tests.fixtures.constants import (
    DEFAULT_USER_ID,
    DEFAULT_WORKSPACE_ID,
    PLATFORM_CODES,
    SAMPLE_PNG_BYTES,
    SAMPLE_TEXT_BYTES,
    SAMPLE_WEBP_BYTES,
    USER_ID,
    WORKSPACE_ID,
)
from tests.fixtures.factories import FIXED_NOW
from tests.fixtures.handlers import build_mock_handlers
from tests.fixtures.outbox import drain_outbox, query_outbox_events
from tests.fixtures.problem import assert_problem_response, assert_success_envelope
from tests.fixtures.seed import E2ESeedBundle, seed_e2e_environment

__all__ = [
    "DEFAULT_USER_ID",
    "DEFAULT_WORKSPACE_ID",
    "E2ESeedBundle",
    "FIXED_NOW",
    "PLATFORM_CODES",
    "SAMPLE_PNG_BYTES",
    "SAMPLE_TEXT_BYTES",
    "SAMPLE_WEBP_BYTES",
    "USER_ID",
    "WORKSPACE_ID",
    "admin_actor",
    "all_permissions",
    "assert_problem_response",
    "assert_success_envelope",
    "bound_principal",
    "build_mock_handlers",
    "build_principal",
    "create_api_test_app",
    "drain_outbox",
    "issue_access_token",
    "query_outbox_events",
    "seed_e2e_environment",
    "workflow_actor",
    "workspace_headers",
]
