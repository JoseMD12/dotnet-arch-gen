# Roadmap e Visão Estratégica - dotnet-arch-gen

Este documento consolida as sugestões de melhorias técnicas e a análise de posicionamento de mercado para o futuro da ferramenta.

---

## 🚀 Próximos Passos (Melhorias Sugeridas)

### 1. Boilerplate de Código (Scaffolding)

* **O que é:** Gerar classes base e configurações mínimas para que o projeto saia "compilando e rodando".
* **Impacto:** Reduz o tempo de setup inicial de 15 minutos para zero.
* **Ação:** Gerar um `Program.cs` básico na camada de API que já registre as injeções de dependência das outras camadas.

### 2. Customização de Templates

* **O que é:** Permitir que o usuário forneça seus próprios arquivos de template (ex: via Jinja2).
* **Impacto:** Atende empresas que possuem padrões internos específicos de NuGets e arquitetura.
* **Ação:** Criar uma pasta de templates externos que sobrepõe os templates padrão da aplicação.

### 3. Solution Folders (Agrupamento Virtual)

* **O que é:** Organizar os projetos em pastas virtuais dentro do Visual Studio/`.sln`.
* **Impacto:** Melhora drasticamente a organização visual em soluções com muitos módulos.
* **Ação:** Adicionar suporte no JSON para definir o agrupamento de cada módulo.

### 4. Instalação Automática de NuGets

* **O que é:** Permitir a definição de pacotes externos no JSON.
* **Impacto:** Automatiza a instalação de frameworks como EF Core, MediatR ou Automapper.
* **Ação:** Adicionar um campo `packages` no JSON para cada camada.

### 5. Modo CLI Wizard (`init`)

* **O que é:** Um modo interativo para criar o arquivo `config.json`.
* **Impacto:** Facilita a entrada de novos usuários que ainda não conhecem o esquema do JSON.
* **Ação:** Implementar o comando `dotnet-arch-gen init`.

---

## 📈 Visão de Futuro

### Propósito da Ferramenta

O **dotnet-arch-gen** foi criado para simplificar o setup inicial de projetos .NET, focando na **estrutura arquitetural** de forma leve e agnóstica. O uso de uma configuração declarativa (JSON) permite:

1. **Padronização:** Facilita a manutenção de uma estrutura consistente de camadas em múltiplos projetos ou microserviços.
2. **Reprodutibilidade:** A arquitetura do projeto pode ser versionada e compartilhada facilmente.

### Objetivos de Evolução

* **Foco na Produtividade:** O objetivo principal a curto prazo é permitir que o código gerado seja imediatamente funcional (compilável e executável).
* **Flexibilidade:** Melhorar a integração com o ecossistema .NET, mantendo a ferramenta leve e livre de dependências pesadas no ambiente do desenvolvedor.
* **Comunidade:** Aprimorar a documentação e fornecer exemplos práticos de arquiteturas geradas pela ferramenta.

---

*Documento em constante evolução.*
