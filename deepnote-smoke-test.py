from pathlib import Path
import socket
import subprocess

def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()

for name, cmd in {
    'python': ('python','--version'), 'java': ('java','-version'), 'node': ('node','--version'),
    'npm': ('npm','--version'), 'git': ('git','--version'), 'gcc': ('gcc','--version'),
    'clang': ('clang','--version'), 'cmake': ('cmake','--version'), 'maven': ('mvn','--version'),
    'gradle': ('gradle','--version'), 'go': ('go','version'), 'rustc': ('rustc','--version'),
    'cargo': ('cargo','--version'), 'R': ('R','--version'), 'php': ('php','--version'),
    'ruby': ('ruby','--version'), 'code-server': ('code-server','--version'),
}.items():
    print(name + ':', run(*cmd).splitlines()[0])

assert Path('/work/projects').exists()
assert Path('/etc/deepnote/config.toml').exists()
with socket.socket() as s:
    s.settimeout(0.5)
    assert s.connect_ex(('127.0.0.1',8080)) == 0
print('8080: listening')
