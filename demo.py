import subprocess
import sys
import tty

# Make the terminal send stdin after each character
tty.setcbreak(sys.stdin.fileno())

# Run the LSP in a subprocess
process = subprocess.Popen(
    ["lsp"],
    stdin=subprocess.PIPE,
)

process.stdin.write(b'Content-Length 17\r\n\r\n{"hello":"world"}')
process.stdin.flush()
process.stdin.write(b'Content-Length 16\r\n\r\n{"hello":"matt"}')
process.stdin.flush()

# # Here, we read each character the user types and send it to the
# # LSP subprocess
# while True:
#     # Wait for input from the user
#     char = sys.stdin.buffer.read(1)
#
#     # Write the user input to the subprocess
#     process.stdin.write(char)
#     process.stdin.flush()

process.wait()
