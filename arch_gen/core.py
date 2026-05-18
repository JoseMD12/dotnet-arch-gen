import os
from .ui import step, info, warn, err, print_banner, ok, skip, Colors
from .config import load_config, ProjectConfig, LayerInfo, ValidLayer
from .shell import run_command
from .generators import create_project, add_to_sln, add_reference, make_dirs, create_support_files

def _find_solution_path(root_dir: str, solution_name: str):
    for ext in [".sln", ".slnx"]:
        path = os.path.join(root_dir, f"{solution_name}{ext}")
        if os.path.exists(path):
            return path, f"{solution_name}{ext}"
    return None, None

def generate(config_path: str, dry_run: bool, output_path_override: str = None, verbose: bool = False):
    config: ProjectConfig = load_config(config_path)
    layer_config = config.layer_definitions

    solution = config.solution
    namespace = config.namespace
    framework = config.framework
    
    output_path = output_path_override or config.output_path or solution
    output_path = os.path.abspath(output_path)

    print_banner()
    info(f"Solução    : {Colors.BOLD}{solution}{Colors.RESET}")
    info(f"Namespace  : {Colors.BOLD}{namespace}{Colors.RESET}")
    info(f"Framework  : {Colors.BOLD}{framework}{Colors.RESET}")
    info(f"Destino    : {Colors.BOLD}{output_path}{Colors.RESET}")
    
    if dry_run:
        warn("Modo dry-run ativo — nenhum arquivo será criado.")

    root_dir = output_path
    
    # Busca por solução existente
    sln_path, sln_file = _find_solution_path(root_dir, solution)

    # -- Solução --
    step("Criando solução")
    if sln_path:
        skip(sln_file)
    else:
        if not dry_run:
            os.makedirs(root_dir, exist_ok=True)
        
        run_command(["dotnet", "new", "sln", "--name", solution, "--output", root_dir], dry_run, verbose=verbose)
        # Após criar, verifica qual extensão o .NET SDK usou de fato
        sln_path, sln_file = _find_solution_path(root_dir, solution)
        
        if dry_run and not sln_path:
            sln_path = os.path.join(root_dir, f"{solution}.sln")

        ok(sln_file or f"{solution}.sln")

    # Dicionário para rastrear todos os .csproj criados
    csproj_map = {}

    # -- Shared --
    if config.shared.layers:
        _process_module("Shared", config.shared.layers, namespace, framework, root_dir, layer_config, sln_path, dry_run, verbose, csproj_map)

    # -- Módulos --
    for module_cfg in config.modules:
        _process_module(module_cfg.name, module_cfg.layers, namespace, framework, root_dir, layer_config, sln_path, dry_run, verbose, csproj_map)

    # -- Arquivos de Suporte --
    step("Arquivos de suporte")
    create_support_files(root_dir, config.model_dump(), dry_run)

    # -- Resumo Final --
    _print_summary(root_dir)

def _process_module(module_name: str, layers: list[ValidLayer], namespace: str, framework: str, root_dir: str, layer_config: dict[ValidLayer, LayerInfo], sln_path: str | None, dry_run: bool, verbose: bool, csproj_map: dict):
    step(f"Módulo: {module_name}")
    
    try:
        for layer in layers:
            if layer not in layer_config:
                warn(f"Camada desconhecida no módulo '{module_name}': '{layer}'")
                continue
            
            l_info = layer_config[layer]
            layer_display = l_info.name or layer.capitalize()
            proj_name = f"{namespace}.{module_name}.{layer_display}"
            output_dir = os.path.join(root_dir, module_name, proj_name)
            csproj_path = os.path.join(output_dir, f"{proj_name}.csproj")
            
            if create_project(proj_name, l_info.template, framework, output_dir, dry_run, verbose=verbose):
                make_dirs(output_dir, l_info.subdirs, dry_run)
                add_to_sln(sln_path, csproj_path, dry_run, verbose=verbose)
            
            csproj_map[(module_name, layer)] = csproj_path

        # Configurar referências
        info("Configurando referências...")
        for layer in layers:
            if layer not in layer_config: continue
            
            l_info = layer_config[layer]
            from_csproj = csproj_map.get((module_name, layer))
            if not from_csproj: continue
            
            # Dependências internas do módulo
            for dep in l_info.deps:
                to_csproj = csproj_map.get((module_name, dep))
                if to_csproj:
                    add_reference(from_csproj, to_csproj, dry_run, verbose=verbose)

            # Dependências para o Shared
            if module_name != "Shared":
                shared_csproj = csproj_map.get(("Shared", layer))
                if shared_csproj:
                    add_reference(from_csproj, shared_csproj, dry_run, verbose=verbose)
    except Exception as e:
        err(f"Falha ao processar módulo '{module_name}': {e}. Interrompendo este módulo.")

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
