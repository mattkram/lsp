import io
import os
import sys
from typing import Iterator, TextIO

from lsp import rpc, schema
from lsp.logger import log


class InputStreamClosed(Exception):
    pass


class Stream:
    def __init__(self, fileobj: TextIO):
        self.fileobj = fileobj
        self._buffer = io.BytesIO()

    @property
    def buffer_contents(self) -> bytes:
        """The contents of the buffer as bytes."""
        old_pos = self._buffer.tell()
        data = self._buffer.read()
        self._buffer.seek(old_pos)
        return data

    def _reset_buffer(self) -> None:
        self._buffer = io.BytesIO()

    def _append_to_buffer(self, contents: bytes) -> None:
        old_pos = self._buffer.tell()
        self._buffer.seek(0, os.SEEK_END)
        self._buffer.write(contents)
        self._buffer.seek(old_pos)

    def _read_into_buffer(self, size: int | None = None) -> None:
        contents = self.fileobj.buffer.read(size)
        if not contents:
            log.debug("Found no bytes in stdin, which means the buffer is closed")
            raise InputStreamClosed()
        self._append_to_buffer(contents)

    def messages(self) -> Iterator[bytes]:
        while True:
            # Read a single character into the buffer
            self._read_into_buffer(1)

            header, sep, _ = self.buffer_contents.partition(b"\r\n\r\n")

            if not sep:
                continue  # not a message

            _, content_length_str = header.split()
            content_length = int(content_length_str)
            self._read_into_buffer(content_length)
            yield self.buffer_contents
            self._reset_buffer()


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


def main() -> int:
    log.info("Starting up!")
    stream = Stream(sys.stdin)
    try:
        for msg in stream.messages():
            handle_message(msg)
    except (SystemExit, InputStreamClosed):
        pass
    return 0
