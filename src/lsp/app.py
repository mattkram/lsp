import io
import os
import sys


class Stream:
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.buffer = io.StringIO()

    def _append_to_buffer(self, contents: str):
        old_pos = self.buffer.tell()
        self.buffer.seek(0, os.SEEK_END)
        self.buffer.write(contents)
        self.buffer.seek(old_pos)

    def peek(self, size: int):
        contents = self.fileobj.read(size)
        self._append_to_buffer(contents)
        return contents

    def read(self, size=None):
        if size is None:
            return self.buffer.read() + self.fileobj.read()
        contents = self.buffer.read(size)
        if len(contents) < size:
            contents += self.fileobj.read(size - len(contents))
        return contents

    def readline(self):
        line = self.buffer.readline()
        if not line.endswith("\n"):
            line += self.fileobj.readline()
        return line


def main() -> int:
    print("Starting up!")
    stream = Stream(sys.stdin)
    while True:
        # Read a single character
        sys.stdout.write(f"Peeked:  {stream.peek(1)}\n")
        char = stream.read(1)

        # Echo back (looks like typing)
        sys.stdout.write(f"LSP got: {char}\n")
        sys.stdout.flush()
    return 0
