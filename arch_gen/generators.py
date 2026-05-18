import os
from typing import List
from .ui import ok, skip, Colors, warn
from .shell import run_command
from .config import ProjectConfig

def get_template(name: str) -> str:
    """Lê um arquivo de template do diretório de templates."""
    base_path = os.path.dirname(__file__)
    template_path = os.path.join(base_path, "templates", name)
    
    if not os.path.exists(template_path):
        warn(f"Template não encontrado: {name}")
        return ""
        
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def create_project(proj_name: str, template: str, framework: str, output_dir: str, dry_run: bool, verbose: bool = False) -> bool:
    if os.path.exists(output_dir):
        skip(proj_name)
        return False

    cmd = ["dotnet", "new", template, "--name", proj_name, "--framework", framework, "--output", output_dir, "--no-restore"]
    
    # Minimal API flag for webapi
    if template == "webapi":
        cmd.append("--use-minimal-apis")

    run_command(cmd, dry_run, verbose=verbose)
    
    # Se chegou aqui, run_command não lançou exceção (sucesso)
    ok(f"{Colors.BOLD}{proj_name}{Colors.RESET}  {Colors.GRAY}({template}){Colors.RESET}")
    return True

def add_to_sln(sln_path: str, csproj_path: str, dry_run: bool, verbose: bool = False) -> None:
    if sln_path is None: return
    run_command(["dotnet", "sln", sln_path, "add", csproj_path], dry_run, verbose=verbose)
    
    # Se chegou aqui, sucesso
    proj_name = os.path.basename(csproj_path)
    ok(f"{proj_name} adicionado à solução")

def add_reference(from_csproj: str, to_csproj: str, dry_run: bool, verbose: bool = False) -> None:
    run_command(["dotnet", "add", from_csproj, "reference", to_csproj], dry_run, verbose=verbose)
    
    from_name = os.path.basename(from_csproj).replace(".csproj", "")
    to_name = os.path.basename(to_csproj).replace(".csproj", "")
    ok(f"{from_name} {Colors.GRAY}→{Colors.RESET} {to_name}")

def make_dirs(base_path: str, subdirs: List[str], dry_run: bool) -> None:
    for d in subdirs:
        path = os.path.join(base_path, d)
        if dry_run:
            print(f"  {Colors.GRAY}[dry-run]{Colors.RESET} mkdir -p {path}")
        else:
            os.makedirs(path, exist_ok=True)

def create_support_files(root_dir: str, config: ProjectConfig, dry_run: bool) -> None:
    if config.gitignore:
        gitignore_path = os.path.join(root_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            skip(".gitignore")
        else:
            content = get_template("gitignore.txt")
            if dry_run:
                print(f"  {Colors.GRAY}[dry-run]{Colors.RESET} create .gitignore")
            else:
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(content)
                ok(".gitignore")

    if config.docker:
        docker_path = os.path.join(root_dir, "docker-compose.yml")
        if os.path.exists(docker_path):
            skip("docker-compose.yml")
        else:
            content = get_template("docker-compose.yml")
            if dry_run:
                print(f"  {Colors.GRAY}[dry-run]{Colors.RESET} create docker-compose.yml")
            else:
                with open(docker_path, "w", encoding="utf-8") as f:
                    f.write(content)
                ok("docker-compose.yml")
