import subprocess
from typing import List, Optional
from .ui import Colors, warn, err

def check_dotnet_sdk():
    """Verifica se o dotnet SDK está instalado."""
    try:
        result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        err("dotnet SDK não encontrado. Certifique-se de que o .NET está instalado e no PATH.")

def run_command(cmd: List[str], dry_run: bool = False, cwd: Optional[str] = None, verbose: bool = False):
    if dry_run:
        print(f"  {Colors.GRAY}[dry-run]{Colors.RESET} {' '.join(cmd)}")
        return True
    
    subprocess.run(
        cmd, 
        capture_output=not verbose, 
        text=True, 
        check=True,
        cwd=cwd
    )
