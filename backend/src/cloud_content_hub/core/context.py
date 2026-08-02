from contextvars import ContextVar, Token

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def bind_request_context(
    request_id: str, correlation_id: str
) -> tuple[Token[str | None], Token[str | None]]:
    return request_id_var.set(request_id), correlation_id_var.set(correlation_id)


def clear_request_context(tokens: tuple[Token[str | None], Token[str | None]]) -> None:
    request_id_var.reset(tokens[0])
    correlation_id_var.reset(tokens[1])
