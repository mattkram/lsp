import io
import os
import sys


class Stream:
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.buffer = io.StringIO()

    def _reset_buffer(self):
        self.buffer = io.StringIO()

    def _append_to_buffer(self, contents: str):
        old_pos = self.buffer.tell()
        self.buffer.seek(0, os.SEEK_END)
        self.buffer.write(contents)
        self.buffer.seek(old_pos)

    def _buffered(self):
        old_pos = self.buffer.tell()
        data = self.buffer.read()
        self.buffer.seek(old_pos)
        return data

    def peek(self, size: int):
        buf = self._buffered()[:size]
        if len(buf) < size:
            contents = self.fileobj.read(size - len(buf))
            self._append_to_buffer(contents)
            return self._buffered()
        return buf

    def read(self, size=None):
        if size is None:
            contents = self.buffer.read() + self.fileobj.read()
            self._reset_buffer()
            return contents

        contents = self.buffer.read(size)
        if len(contents) < size:
            contents += self.fileobj.read(size - len(contents))
            self._reset_buffer()
        return contents

    def readline(self):
        line = self.buffer.readline()
        if not line.endswith("\n"):
            line += self.fileobj.readline()
            self._reset_buffer()
        return line

    def close(self):
        self.buffer = None
        self.fileobj = None


def main() -> int:
    print("Starting up!")
    stream = Stream(sys.stdin)
    while True:
        # Read a single character
        sys.stdout.write(f"Peeked:  {stream.peek(1)}\n")
        sys.stdout.write(f"Peeked:  {stream.peek(1)}\n")
        char = stream.read(1)

        # Echo back (looks like typing)
        sys.stdout.write(f"LSP got: {char}\n")
        sys.stdout.flush()
    return 0
