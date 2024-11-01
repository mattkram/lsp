import sys

from lsp import rpc, schema
from lsp.logger import log


def handle_message(msg: bytes) -> None:
    method, content = rpc.decode_message(msg)
    log.info("Received message with method: %s", method)
    log.debug("msg=%s", msg)
    if method == "initialize":
        request = schema.InitializeRequest.model_validate_json(content)
        if client_info := request.params.client_info:
            log.info(
                "Connected to: %s %s",
                client_info.name,
                client_info.version,
            )
        response = schema.InitializeResponse(
            id=request.id,
            result=schema.InitializeResult(
                capabilities=schema.ServerCapabilities(),
                server_info=schema.ServerInfo(
                    name="kramer-lsp",
                    version="0.0.0.0.0.alpha1",
                ),
            ),
        )
        send_response(response)
    elif method == "shutdown":
        log.info("Shutting down")
        raise SystemExit()


def send_response(response: schema.Response) -> None:
    """Send an encoded response back to the editor."""
    msg = rpc.encode_message(response)
    log.debug("msg=%s", msg)
    sys.stdout.buffer.write(msg)
    sys.stdout.flush()
