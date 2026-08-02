"""Load test collection hooks."""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.load, pytest.mark.performance]
