from lsp import schema
from lsp.app import HandlerRegistry, LspApp
from lsp.logger import log


registry = HandlerRegistry()


@registry.register("initialize")
def _handle_initialize(app: LspApp, content: bytes) -> schema.InitializeResponse:
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
            capabilities=schema.ServerCapabilities(
                text_document_sync=schema.TextDocumentSyncKind.FULL,
                hover_provider=True,
            ),
            server_info=schema.ServerInfo(
                name="kramer-lsp",
                version="0.0.0.0.0.alpha1",
            ),
        ),
    )


@registry.register("textDocument/didOpen")
def _handle_text_document_did_open(app: LspApp, content: bytes) -> None:
    request = schema.DidOpenTextDocumentNotification.model_validate_json(content)
    app.state.open_document(
        request.params.text_document.uri, request.params.text_document.text
    )
    log.info("Opened: %s", request.params.text_document.uri)
    log.info("Received text: %s", request.params.text_document.text)


@registry.register("textDocument/didChange")
def _handle_text_document_did_change(app: LspApp, content: bytes) -> None:
    request = schema.DidChangeTextDocument.model_validate_json(content)
    log.info(
        "Changed: %s, version %s",
        request.params.text_document.uri,
        request.params.text_document.version,
    )

    for change in request.params.content_changes:
        app.state.update_document(request.params.text_document.uri, change.text)


@registry.register("textDocument/hover")
def _handle_hover(app: LspApp, content: bytes) -> schema.InitializeResponse:
    request = schema.HoverRequest.model_validate_json(content)
    return schema.HoverResponse(
        id=request.id,
        result=schema.HoverResult(
            contents="Hey dude!",
        ),
    )


@registry.register("shutdown")
def _handle_shutdown(app: LspApp, content: bytes) -> None:
    log.info("Shutting down")
    raise SystemExit()
