import sys


def main() -> int:
    print("Starting up!")
    while True:
        # Read a single character
        char = sys.stdin.read(1)

        # Echo back (looks like typing)
        sys.stdout.write(f"LSP got: {char}\n")
        sys.stdout.flush()
    return 0
