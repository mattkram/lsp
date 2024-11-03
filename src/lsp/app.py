import sys
from typing import Callable, Iterator

from lsp import rpc, schema
from lsp.logger import log
from lsp.types import HandlerFunc, MethodName
from lsp.stream import Stream, InputStreamClosed


class HandlerRegistry:
    _handlers: dict[MethodName, HandlerFunc]

    def __init__(self) -> None:
        self._handlers = {}

    def register(self, name: MethodName) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a handler function for a given method."""

        def decorator(f: HandlerFunc) -> HandlerFunc:
            self._handlers[name] = f
            return f

        return decorator

    def get(self, name: MethodName) -> HandlerFunc:
        """Get a handler by name.

        If no handler is found, a dummy handler is returned which returns None and does
        not send any message back to the client.
        """
        return self._handlers.get(name, lambda _: None)


class LspApp:
    def __init__(self) -> None:
        self._registry = HandlerRegistry()
        self._input_stream = Stream(sys.stdin)

    def register(self, name: MethodName) -> Callable[[HandlerFunc], HandlerFunc]:
        return self._registry.register(name)

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
        response = handler(content)
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
