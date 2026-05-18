import os
import argparse
import sys
from arch_gen.core import generate
from arch_gen.shell import check_dotnet_sdk
from arch_gen import __version__

def main():
    parser = argparse.ArgumentParser(
        description=f".NET Architecture Generator v{__version__} - Cria uma estrutura Clean Architecture para .NET.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--config", 
        help="Caminho para o arquivo JSON de configuração. (Padrão: config.json)"
    )

    parser.add_argument(
        "--output", 
        help="Caminho total onde o projeto será criado. (Sobrescreve o 'output_path' do JSON)"
    )

    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Exibe os comandos que seriam executados sem criar nenhum arquivo ou diretório."
    )

    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Exibe a saída detalhada dos comandos dotnet."
    )

    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )

    parser.epilog = """
Exemplos:
  python3 dotnet-arch-gen.py                           (Usa config.json por padrão)
  python3 dotnet-arch-gen.py --config custom.json
  python3 dotnet-arch-gen.py --output /home/user/projects/MyNewProject
  python3 dotnet-arch-gen.py --dry-run
  python3 dotnet-arch-gen.py --verbose
"""

    args = parser.parse_args()

    # Verifica ambiente
    check_dotnet_sdk()

    # Lógica para encontrar o arquivo de configuração
    config_path = args.config
    if not config_path:
        if os.path.exists("config.json"):
            config_path = "config.json"
        else:
            print("\nErro: Nenhum arquivo de configuração informado (--config) e 'config.json' não encontrado.")
            print("Use --help para ver as instruções.\n")
            sys.exit(1)

    try:
        generate(
            config_path=config_path, 
            dry_run=args.dry_run, 
            output_path_override=args.output,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\n\nAbortado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        # Em modo verbose, mostra o traceback completo
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

