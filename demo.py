import subprocess
import sys

p = subprocess.Popen(
    ["lsp"], 
    stdin=subprocess.PIPE, 
    text=True,
)

while True:
    # Wait for input from the user
    line = sys.stdin.readline()

    # Write the user input to the subprocess
    p.stdin.write(line)
    p.stdin.flush()

p.wakt()
