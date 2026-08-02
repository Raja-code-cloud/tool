"""Stress test collection hooks."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.stress, pytest.mark.performance]
