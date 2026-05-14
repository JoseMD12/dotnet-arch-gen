import os
from .ui import step, info, warn, err, print_banner, ok, skip, Colors
from .config import load_config
from .shell import run_command
from .generators import create_project, add_to_sln, add_reference, make_dirs, create_support_files

def generate(config_path: str, dry_run: bool, output_path_override: str = None, verbose: bool = False):
    config = load_config(config_path)
    layer_config = config["_layer_config"]

    solution = config.get("solution")
    namespace = config.get("namespace")
    framework = config.get("framework", "net10.0")
    
    output_path = output_path_override or config.get("output_path") or solution

    if not solution or not namespace:
        err("Campos 'solution' e 'namespace' são obrigatórios no JSON.")

    print_banner()
    info(f"Solução    : {Colors.BOLD}{solution}{Colors.RESET}")
    info(f"Namespace  : {Colors.BOLD}{namespace}{Colors.RESET}")
    info(f"Framework  : {Colors.BOLD}{framework}{Colors.RESET}")
    info(f"Destino    : {Colors.BOLD}{output_path}{Colors.RESET}")
    
    if dry_run:
        warn("Modo dry-run ativo — nenhum arquivo será criado.")

    root_dir = output_path
    sln_file = f"{solution}.sln"
    sln_path = os.path.join(root_dir, sln_file)

    # -- Solução --
    step("Criando solução")
    if os.path.exists(sln_path):
        skip(sln_file)
    else:
        if not dry_run:
            os.makedirs(root_dir, exist_ok=True)
        if run_command(["dotnet", "new", "sln", "--name", solution, "--output", root_dir], dry_run, verbose=verbose):
            ok(sln_file)

    # Dicionário para rastrear todos os CSPROJs criados
    csproj_map = {}

    # -- Módulos --
    modules = config.get("modules", [])
    if not modules:
        err("Nenhum módulo definido em 'modules' no JSON.")

    for module_cfg in modules:
        module_name = module_cfg.get("name")
        module_layers = module_cfg.get("layers", [])
        
        step(f"Módulo: {module_name}")
        
        for layer in module_layers:
            layer = layer.lower()
            if layer not in layer_config:
                warn(f"Camada desconhecida no módulo '{module_name}': '{layer}'")
                continue
            
            l_info = layer_config[layer]
            layer_display = l_info.get("name") or layer.capitalize()
            proj_name = f"{namespace}.{module_name}.{layer_display}"
            output_dir = os.path.join(root_dir, module_name, proj_name)
            csproj_path = os.path.join(output_dir, f"{proj_name}.csproj")
            
            if create_project(proj_name, l_info["template"], framework, output_dir, dry_run, verbose=verbose):
                make_dirs(output_dir, l_info["subdirs"], dry_run)
                add_to_sln(sln_path, csproj_path, dry_run, verbose=verbose)
            
            csproj_map[(module_name, layer)] = csproj_path

        # Configurar referências (Dependency Rule)
        info("Configurando referências...")
        for layer in module_layers:
            layer = layer.lower()
            if layer not in layer_config: continue
            
            l_info = layer_config[layer]
            from_csproj = csproj_map.get((module_name, layer))
            if not from_csproj: continue
            
            # Dependências internas do módulo
            for dep in l_info["deps"]:
                to_csproj = csproj_map.get((module_name, dep))
                if to_csproj:
                    if add_reference(from_csproj, to_csproj, dry_run, verbose=verbose):
                        ok(f"{layer} → {dep}")

    # -- Arquivos de Suporte --
    step("Arquivos de suporte")
    create_support_files(root_dir, config, dry_run)

    # -- Resumo Final --
    _print_summary(root_dir)

def _print_summary(root_dir):
    print("")
    print(f"{Colors.GREEN}{Colors.BOLD}  ══════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  ✔  Solução gerada com sucesso!{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  ══════════════════════════════════════════{Colors.RESET}")
    print("")
    info(f"Diretório        : {Colors.BOLD}{root_dir}/{Colors.RESET}")
    print("")
    print(f"  {Colors.YELLOW}Próximos passos:{Colors.RESET}")
    print(f"    cd {root_dir}")
    print(f"    dotnet restore")
    print(f"    dotnet build")
    print("")
