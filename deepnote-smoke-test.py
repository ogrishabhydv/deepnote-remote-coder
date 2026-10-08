from pathlib import Path
import socket
import subprocess

print("Python:", subprocess.check_output(["python", "--version"], text=True).strip())
print("Java:", subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True).splitlines()[0])
print("Node:", subprocess.check_output(["node", "--version"], text=True).strip())
print("npm:", subprocess.check_output(["npm", "--version"], text=True).strip())
print("code-server:", subprocess.check_output(["code-server", "--version"], text=True).strip())
print("/work exists:", Path("/work").exists())
print("/work/projects exists:", Path("/work/projects").exists())

with socket.socket() as s:
    s.settimeout(0.5)
    result = s.connect_ex(("127.0.0.1", 8080))
print("8080 listening:", result == 0)
