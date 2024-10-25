import io
import os
import sys
from typing import Iterator, TextIO

from lsp import rpc, schema
from lsp.logger import log


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

    def _buffered(self) -> bytes:
        old_pos = self.buffer.tell()
        data = self.buffer.read()
        self.buffer.seek(old_pos)
        return data

    def peek(self, size: int) -> bytes:
        buf = self._buffered()[:size]
        if len(buf) < size:
            contents = self.fileobj.buffer.read(size - len(buf))
            self._append_to_buffer(contents)
            return self._buffered()
        return buf

    def read(self, size: int | None = None) -> bytes:
        if size is None:
            contents = self.buffer.read() + self.fileobj.buffer.read()
            self._reset_buffer()
            return contents

        contents = self.buffer.read(size)
        if len(contents) < size:
            contents += self.fileobj.buffer.read(size - len(contents))
            self._reset_buffer()
        return contents

    def readline(self) -> bytes:
        line = self.buffer.readline()
        if not line.endswith(b"\n"):
            line += self.fileobj.buffer.readline()
            self._reset_buffer()
        return line

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
        msg = rpc.encode_message(response)
        log.debug("msg=%s", msg)
        sys.stdout.buffer.write(msg)
        sys.stdout.flush()


def main() -> int:
    log.info("Starting up!")
    stream = Stream(sys.stdin)
    for msg in stream.messages():
        handle_message(msg)
    return 0
