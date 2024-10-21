import sys


def main() -> int:
    print("Starting up!")
    while True:
        # Prompt for input
        sys.stdout.write(">>> ")
        sys.stdout.flush()

        # Wait for input from the user
        line = sys.stdin.readline()
        if line:
            # Echo back
            sys.stdout.write(line.strip() + "\r\n")
            sys.stdout.flush()
    return 0
