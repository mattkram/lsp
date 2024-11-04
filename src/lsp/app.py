import sys
from typing import Callable, Iterator

from lsp import rpc, schema
from lsp.logger import log
from lsp.types import HandlerFunc, MethodName
from lsp.stream import Stream, InputStreamClosed

DocumentPath = str
DocumentContents = str


class HandlerRegistry:
    _handlers: dict[MethodName, HandlerFunc]

    def __init__(self) -> None:
        self._handlers = {}

    def register(self, name: MethodName) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler function for a given method."""

        def decorator(f: HandlerFunc) -> HandlerFunc:
            self.add(name, f)
            return f

        return decorator

    def handlers(self) -> Iterator[tuple[MethodName, HandlerFunc]]:
        yield from self._handlers.items()

    def add(self, name: MethodName, func: HandlerFunc) -> None:
        self._handlers[name] = func

    def get(self, name: MethodName) -> HandlerFunc:
        """Get a handler by name.

        If no handler is found, a dummy handler is returned which returns None and does
        not send any message back to the client.
        """
        return self._handlers.get(name, lambda *_: None)


class DocumentState:
    def __init__(self):
        self._state: dict[DocumentPath, DocumentContents] = {}

    def open_document(self, uri: DocumentPath, text: DocumentContents) -> None:
        self._state[uri] = text


class LspApp:
    def __init__(self) -> None:
        self._registry = HandlerRegistry()
        self._input_stream = Stream(sys.stdin)
        self.state = DocumentState()

    def register(self, name: MethodName) -> Callable[[HandlerFunc], HandlerFunc]:
        return self._registry.register(name)

    def add_registry(self, registry: HandlerRegistry) -> None:
        for name, handler_func in registry.handlers():
            self._registry.add(name, handler_func)

    def _receive_messages(self) -> Iterator[bytes]:
        yield from self._input_stream.messages()

    @staticmethod
    def _send_response(response: schema.Response) -> None:
        """Send an encoded response back to the editor."""
        msg = rpc.encode_message(response)
        log.debug("msg=%s", msg)
        sys.stdout.buffer.write(msg)
        sys.stdout.flush()

    def _handle_message(self, msg: bytes) -> None:
        """Dispatch message to registered handler based on method and send response."""
        method, content = rpc.decode_message(msg)
        log.info("Received message with method: %s", method)
        log.debug("msg=%s", msg)
        handler = self._registry.get(method)
        response = handler(self, content)
        if response is not None:
            self._send_response(response)

    def run(self) -> int:
        log.info("Starting up!")
        try:
            for msg in self._receive_messages():
                self._handle_message(msg)
        except (SystemExit, InputStreamClosed):
            pass
        return 0
