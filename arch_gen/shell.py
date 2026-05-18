import subprocess
import sys
from typing import List, Optional
from .ui import Colors, warn, err

ALLOWED_FLAGS = {
    "--version",
    "--output",
    "--verbose",
    "--dry-run",
    "--config",
    "--name",
    "--framework",
    "--no-restore",
    "--use-minimal-apis",
}

def check_dotnet_sdk() -> str:
    """Verifica se o dotnet SDK está instalado."""
    try:
        result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        err("dotnet SDK não encontrado. Certifique-se de que o .NET está instalado e no PATH.")
        sys.exit(1)

def _validate_args(cmd: List[str]):
    """
    Previne Flag Injection validando os argumentos do comando.
    """
    for arg in cmd[1:]:
        if arg.startswith("-") and arg not in ALLOWED_FLAGS:
            err(f"Argumento de CLI potencialmente perigoso detectado: {arg}")
            sys.exit(1)

def run_command(cmd: List[str], dry_run: bool = False, cwd: Optional[str] = None, verbose: bool = False):
    _validate_args(cmd)
    
    if dry_run:
        print(f"  {Colors.GRAY}[dry-run]{Colors.RESET} {' '.join(cmd)}")
        return
    
    try:
        subprocess.run(
            cmd, 
            capture_output=not verbose, 
            text=True, 
            check=True,
            cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        if not verbose:
            warn(f"Erro ao executar comando: {' '.join(cmd)}")
            if e.stderr:
                print(f"  {Colors.RED}Saída de erro:{Colors.RESET} {e.stderr.strip()}")
        raise
