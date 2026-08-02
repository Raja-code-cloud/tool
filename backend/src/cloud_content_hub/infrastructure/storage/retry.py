"""Storage-layer retry placeholder and circuit-breaker hook type."""

from collections.abc import Awaitable, Callable

CircuitBreakerHook = Callable[[str, bool], Awaitable[None]]
