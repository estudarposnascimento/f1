# Instalação e Configuração de Ambiente

Este guia detalha o fluxo de configuração do ambiente de desenvolvimento em conformidade estrita com os padrões estabelecidos no projeto.

---

## Pré-requisitos

O projeto requer:

1. **Python 3.12+** gerenciado preferencialmente via **pyenv**.
2. **Poetry** (versão 2.0 ou superior) para gestão de dependências e ambientes virtuais.
3. **Git** para controle de versão.

---

## Passo a Passo de Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/f1.git
cd f1
```

### 2. Configurar a Versão do Python com pyenv

O repositório possui o arquivo `.python-version` fixando o interpretador. Para instalar e ativar localmente:

```bash
# Instalar Python 3.12 caso ainda não esteja instalado
pyenv install 3.12.10

# Vincular localmente ao diretório do projeto
pyenv local 3.12.10
```

### 3. Inicializar o Ambiente Virtual com Poetry

```bash
# Apontar o Poetry para o binário do pyenv
poetry env use $(pyenv which python)

# Instalar todas as dependências de produção e desenvolvimento
poetry install
```

### 4. Validar o Ambiente

Inspecione as informações do ambiente virtual criado:

```bash
poetry env info
```

---

## Árvore de Dependências

O arquivo `pyproject.toml` isola as dependências em dois grupos:

- **Produção (`project.dependencies`):**
    - `pydantic>=2.7.0`: Validação e esquemas de dados.
    - `requests>=2.31.0`: Comunicação HTTP resiliente.
    - `pandas>=2.2.0`: Análise e manipulação tabular.
- **Desenvolvimento (`tool.poetry.group.dev.dependencies`):**
    - `pytest>=8.2.0`: Framework de testes unitários.
    - `pytest-cov>=5.0.0`: Relatórios de cobertura de código.
    - `pytest-mock>=3.14.0`: Mocks e fixtures avançadas.
    - `ruff>=0.4.0`: Linter e formatador estático unificado.
    - `mkdocs>=1.6.0` e `mkdocs-material>=9.5.0`: Site estático de documentação técnica.
