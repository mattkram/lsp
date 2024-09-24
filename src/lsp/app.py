import sys


def main() -> int:
    print("Starting up!")
    while True:
        line = sys.stdin.readline()
        if line:
            print(line.strip())
    return 0
