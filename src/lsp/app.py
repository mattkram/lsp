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
        self.buffer = io.BytesIO()

    def _reset_buffer(self) -> None:
        self.buffer = io.BytesIO()

    def _append_to_buffer(self, contents: bytes) -> None:
        old_pos = self.buffer.tell()
        self.buffer.seek(0, os.SEEK_END)
        self.buffer.write(contents)
        self.buffer.seek(old_pos)

    def read(self, size: int | None = None) -> bytes:
        contents = self.fileobj.buffer.read(size)
        if not contents:
            log.debug("Found no bytes in stdin, which means the buffer is closed")
            raise InputStreamClosed()
        return contents

    def messages(self) -> Iterator[bytes]:
        msg = b""
        while True:
            # Read a single character into the buffer
            msg += self.read(1)

            header, sep, _ = msg.partition(b"\r\n\r\n")

            if not sep:
                continue  # not a message

            _, content_length_str = header.split()
            content_length = int(content_length_str)
            msg += self.read(content_length)
            yield msg
            msg = b""


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
