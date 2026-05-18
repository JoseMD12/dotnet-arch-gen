# dotnet-arch-gen

![CI](https://github.com/JoseMD12/dotnet-arch-gen/actions/workflows/ci.yml/badge.svg)
![Security Audit](https://github.com/JoseMD12/dotnet-arch-gen/actions/workflows/security.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Gerador de arquitetura para soluções .NET via linha de comando, configurado por arquivo JSON.

Cria automaticamente a estrutura de projetos seguindo **Clean Architecture** e **DDD** — com referências entre camadas já configuradas — pronto para `dotnet build`.

---

## Requisitos

- Python 3.10+
- [.NET SDK](https://dotnet.microsoft.com/download) instalado e disponível no `PATH`

---

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/JoseMD12/dotnet-arch-gen.git
cd dotnet-arch-gen
pip install -e .
```

Para instalar também as ferramentas de desenvolvimento (testes, linting, auditoria):

```bash
pip install -e ".[dev]"
```

---

## Uso

Após a instalação, você pode usar o comando diretamente ou via script Python:

```bash
# Comando direto (recomendado após instalação)
dotnet-arch-gen --config meu-projeto.json

# Ou via script
python dotnet_arch_gen.py --config meu-projeto.json
```

Outros exemplos:

```bash
# Define o diretório de saída (sobrescreve output_path do JSON)
dotnet-arch-gen --output C:/Projects/MinhaApp

# Visualiza os comandos sem criar nada
dotnet-arch-gen --dry-run

# Exibe a saída completa dos comandos dotnet
dotnet-arch-gen --verbose

# Exibe a versão
dotnet-arch-gen --version
```

---

## Arquivo de configuração

```json
{
  "solution": "AuthSecurity",
  "namespace": "MyCompany",
  "framework": "net10.0",
  "output_path": "C:/MyProjects/AuthSecurity",
  "docker": true,
  "gitignore": true,
  "shared": {
    "layers": ["domain", "infrastructure"]
  },
  "modules": [
    {
      "name": "JWT",
      "layers": ["domain", "application", "infrastructure", "api", "tests"]
    },
    {
      "name": "TokenCleanup",
      "layers": ["domain", "application", "infrastructure", "worker"]
    },
    {
      "name": "Reports",
      "layers": ["domain", "application", "infrastructure", "console"]
    }
  ]
}
```

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `solution` | string | ✅ | Nome da solução `.sln` |
| `namespace` | string | ✅ | Namespace raiz — ex: `MyCompany` gera `MyCompany.JWT.Domain` |
| `framework` | string | | Target framework. Suporta: `net8.0`, `net9.0`, `net10.0`. Padrão: `net10.0` |
| `output_path` | string | | Caminho de saída. **Nota:** Não permite `..` por segurança. Padrão: pasta com o nome da solução |
| `docker` | bool | | Gera `docker-compose.yml`. Padrão: `false` |
| `gitignore` | bool | | Gera `.gitignore` para .NET. Padrão: `true` |
| `shared.layers` | array | | Camadas compartilhadas entre todos os módulos |
| `modules` | array | ✅ | Lista de módulos com suas camadas |

---

## Camadas disponíveis

| Camada | Template .NET | Subpastas criadas |
|---|---|---|
| `domain` | classlib | Entities, ValueObjects, Exceptions, Repositories |
| `application` | classlib | UseCases, DTOs, Interfaces, Mappings |
| `infrastructure` | classlib | Data, Repositories, Security |
| `api` | webapi (Minimal API) | Controllers, Endpoints, Middlewares |
| `worker` | worker service | Jobs, Handlers, Consumers |
| `console` | console app | Commands, Handlers |
| `tests` | xunit | Unit, Integration, Fixtures |

Cada módulo usa apenas as camadas que fazem sentido para ele — um worker de limpeza não precisa de `api`, um gerador de relatórios não precisa de `api` nem de `worker`.

---

## Dependency Rule

As referências entre projetos são configuradas automaticamente respeitando a regra de dependência do Clean Architecture:

```text
domain          ←  nenhuma dependência
application     →  domain
infrastructure  →  domain
api             →  application, infrastructure
worker          →  application, infrastructure
console         →  application
tests           →  application, infrastructure
```

O `domain` nunca conhece nenhuma outra camada.

---

## Estrutura gerada

Para o exemplo acima:

```text
AuthSecurity/
├── AuthSecurity.sln
├── .gitignore
├── docker-compose.yml
│
├── Shared/
│   ├── MyCompany.Shared.Domain/
│   │   ├── Entities/
│   │   ├── ValueObjects/
│   │   ├── Exceptions/
│   │   └── Repositories/
│   └── MyCompany.Shared.Infrastructure/
│       ├── Data/
│       ├── Repositories/
│       └── Security/
│
├── JWT/
│   ├── MyCompany.JWT.Domain/
│   ├── MyCompany.JWT.Application/
│   ├── MyCompany.JWT.Infrastructure/
│   ├── MyCompany.JWT.API/
│   └── MyCompany.JWT.Tests/
│
├── TokenCleanup/
│   ├── MyCompany.TokenCleanup.Domain/
│   ├── MyCompany.TokenCleanup.Application/
│   ├── MyCompany.TokenCleanup.Infrastructure/
│   └── MyCompany.TokenCleanup.Worker/
│
└── Reports/
    ├── MyCompany.Reports.Domain/
    ├── MyCompany.Reports.Application/
    ├── MyCompany.Reports.Infrastructure/
    └── MyCompany.Reports.Console/
```

---

## Estrutura do projeto

```text
dotnet-arch-gen/
├── dotnet_arch_gen.py        # Ponto de entrada — CLI e argumentos
├── example-config.json       # Configuração de exemplo
├── pyproject.toml            # Dependências e configuração do projeto
└── arch_gen/
    ├── __init__.py           # Versão do pacote
    ├── core.py               # Orquestração principal
    ├── config.py             # Leitura e validação do JSON com Pydantic
    ├── generators.py         # Criação de projetos, pastas e arquivos de suporte
    ├── shell.py              # Execução segura de comandos dotnet
    ├── ui.py                 # Output colorido no terminal
    └── templates/
        ├── docker-compose.yml
        └── gitignore.txt
```

---

## Testes

Rode a suíte de testes com relatório de cobertura:

```bash
pytest -v
```

O relatório de cobertura é exibido no terminal automaticamente. Para gerar também em HTML:

```bash
pytest --cov=arch_gen --cov-report=html
```

O resultado fica em `htmlcov/index.html`, com cobertura linha a linha de cada arquivo.

---

## Segurança

O projeto usa duas ferramentas complementares para análise de segurança:

**Bandit** — analisa o código Python em busca de padrões inseguros:

```bash
bandit -r arch_gen/ -c pyproject.toml
```

**pip-audit** — audita as dependências externas contra o banco de CVEs do PyPI:

```bash
pip-audit
```

Ambas rodam automaticamente via GitHub Actions a cada push.

---

## CI/CD

O repositório possui dois workflows automatizados:

**CI** — roda em todo push e pull request, em Python 3.10, 3.11, 3.12 e 3.13 em paralelo:

- Testes com cobertura
- Análise estática com Bandit

**Security Audit** — roda a cada push na `main` ou `dev` e toda segunda-feira às 06h UTC:

- Auditoria de dependências com pip-audit

---

## Idempotência

O script é seguro para rodar múltiplas vezes. Projetos e arquivos que já existem são pulados com aviso, sem sobrescrever nada. Isso permite adicionar novos módulos a uma solução existente sem recriar o que já está lá.

---

## Licença

MIT
