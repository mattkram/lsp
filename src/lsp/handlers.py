import sys
from typing import Callable

from lsp import rpc, schema
from lsp.logger import log

__all__ = ["handle_message"]

MethodName = str
HandlerFunc = Callable[[bytes], schema.Response | None]

_handlers: dict[MethodName, HandlerFunc] = {}


def register(name: MethodName) -> Callable[[HandlerFunc], HandlerFunc]:
    def decorator(f: HandlerFunc) -> HandlerFunc:
        _handlers[name] = f
        return f

    return decorator


@register("initialize")
def _handle_initialize(content: bytes) -> schema.InitializeResponse:
    request = schema.InitializeRequest.model_validate_json(content)
    if client_info := request.params.client_info:
        log.info(
            "Connected to: %s %s",
            client_info.name,
            client_info.version,
        )
    return schema.InitializeResponse(
        id=request.id,
        result=schema.InitializeResult(
            capabilities=schema.ServerCapabilities(),
            server_info=schema.ServerInfo(
                name="kramer-lsp",
                version="0.0.0.0.0.alpha1",
            ),
        ),
    )


@register("shutdown")
def _handle_shutdown(content: bytes) -> None:
    log.info("Shutting down")
    raise SystemExit()


def _send_response(response: schema.Response) -> None:
    """Send an encoded response back to the editor."""
    msg = rpc.encode_message(response)
    log.debug("msg=%s", msg)
    sys.stdout.buffer.write(msg)
    sys.stdout.flush()


def handle_message(msg: bytes) -> None:
    method, content = rpc.decode_message(msg)
    log.info("Received message with method: %s", method)
    log.debug("msg=%s", msg)
    handler = _handlers.get(method, lambda _: None)
    response = handler(content)
    if response is not None:
        _send_response(response)
