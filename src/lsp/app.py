import io
import logging
import os
import sys
from pathlib import Path
from typing import Iterator

FORMAT = "[%(asctime)s,%(msecs)d] %(name)s [%(levelname)s] %(message)s"
LOG_FILENAME = Path("log.txt")
LOG_LEVEL = logging.DEBUG

logging.basicConfig(
    filename=LOG_FILENAME,
    filemode="w",
    format=FORMAT,
    datefmt="%H:%M:%S",
    level=LOG_LEVEL,
)
log = logging.getLogger("lsp")


class Stream:
    def __init__(self, fileobj):
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

    def close(self) -> None:
        self.buffer = None
        self.fileobj = None

    def messages(self) -> Iterator[str]:
        buf = b""
        while True:
            # Read a single character into the buffer
            buf += self.read(1)

            header, sep, msg = buf.partition(b"\r\n\r\n")

            if not sep:
                continue  # not a message

            _, content_length = header.split()
            content_length = int(content_length)
            msg = self.read(content_length)
            yield msg
            buf = b""


def handle_message(msg: bytes) -> None:
    log.info("msg=%s", msg)


def main() -> int:
    log.info("Starting up!")
    stream = Stream(sys.stdin)
    for msg in stream.messages():
        handle_message(msg)
    return 0
