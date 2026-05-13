import runpy
import sys
from pathlib import Path

server_main = r"D:\Program Files\MWORKS\Sysplorer 2026a\Tools\sysplorer_mcp\sysplorer-mcp-server\main.py"
sys.path.insert(0, str(Path(server_main).parent))
sys.argv = [
    server_main,
    "--mworks-install-dir",
    r"D:\Program Files\MWORKS\Sysplorer 2026a",
    "--sysplorer-platform-label",
    "Sysplorer 2026a",
]
runpy.run_path(server_main, run_name="__main__")
