import sys

class Colors:
    GREEN = '\033[0;32m'
    CYAN = '\033[0;36m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    GRAY = '\033[0;90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def ok(msg: str): print(f"  {Colors.GREEN}✔{Colors.RESET}  {msg}")
def skip(msg: str): print(f"  {Colors.GRAY}–{Colors.RESET}  {msg} {Colors.GRAY}(já existe, pulando){Colors.RESET}")
def step(msg: str): print(f"\n{Colors.BOLD}{Colors.YELLOW}▶  {msg}{Colors.RESET}")
def info(msg: str): print(f"  {Colors.CYAN}i{Colors.RESET}  {msg}")
def warn(msg: str): print(f"  {Colors.YELLOW}!{Colors.RESET}  {msg}")
def err(msg: str):
    print(f"\n  {Colors.RED}✖  Erro: {msg}{Colors.RESET}\n", file=sys.stderr)
    sys.exit(1)

def print_banner():
    print(f"\n{Colors.CYAN}{Colors.BOLD}")
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║       .NET Architecture Generator (Python)  ║")
    print("  ╚══════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
