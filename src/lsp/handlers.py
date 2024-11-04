from lsp import schema
from lsp.app import HandlerRegistry
from lsp.logger import log


registry = HandlerRegistry()


@registry.register("initialize")
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


@registry.register("shutdown")
def _handle_shutdown(content: bytes) -> None:
    log.info("Shutting down")
    raise SystemExit()
