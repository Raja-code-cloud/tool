"""Unit tests for worker retry policy."""

from __future__ import annotations

import pytest

from cloud_content_hub.core.errors import ResourceNotFoundError, ValidationError
from cloud_content_hub.workers.config import WorkerRetryConfig
from cloud_content_hub.workers.exceptions import (
    PermanentWorkerError,
    PoisonMessageError,
    TransientWorkerError,
)
from cloud_content_hub.workers.retry import WorkerRetryPolicy, is_transient_error


@pytest.fixture
def policy() -> WorkerRetryPolicy:
    return WorkerRetryPolicy(
        WorkerRetryConfig(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=30.0,
            backoff_multiplier=2.0,
            poison_message_threshold=2,
        )
    )


def test_is_transient_error_classifies_dependency_failures() -> None:
    assert is_transient_error(TransientWorkerError()) is True
    assert is_transient_error(ValidationError()) is False
    assert is_transient_error(PermanentWorkerError()) is False
    assert is_transient_error(RuntimeError("unexpected")) is False


def test_retry_policy_retries_transient_failure(policy: WorkerRetryPolicy) -> None:
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="timeout"),
    )

    assert decision.retry is True
    assert decision.reason_code == "transient_failure"
    assert decision.backoff_seconds == 1.0


def test_retry_policy_detects_poison_message(policy: WorkerRetryPolicy) -> None:
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=1,
        last_error="same failure",
        error=TransientWorkerError(detail="same failure"),
    )

    assert decision.retry is False
    assert decision.reason_code == "poison_message"


def test_retry_policy_exhausts_retries(policy: WorkerRetryPolicy) -> None:
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=3,
        last_error=None,
        error=TransientWorkerError(detail="still failing"),
    )

    assert decision.retry is False
    assert decision.reason_code == "retry_exhausted"


def test_retry_policy_rejects_permanent_failures(policy: WorkerRetryPolicy) -> None:
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=0,
        last_error=None,
        error=ResourceNotFoundError(),
    )

    assert decision.retry is False
    assert decision.reason_code == "permanent_failure"


def test_retry_policy_rejects_poison_message_error(policy: WorkerRetryPolicy) -> None:
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=0,
        last_error=None,
        error=PoisonMessageError(),
    )

    assert decision.retry is False
    assert decision.reason_code == "poison_message"
