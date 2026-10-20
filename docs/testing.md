# Testes e Garantia de Qualidade

A integridade do código do projeto **`f1`** é garantida por uma suíte de testes com isolamento de rede e validação estrita de cobertura.

---

## Automação de Tarefas com Taskipy

Para agilizar o desenvolvimento, os principais fluxos de qualidade foram encapsulados em tarefas do **Taskipy**:

| Comando | Ação Executada |
| :--- | :--- |
| `poetry run task dashboard` | Inicia o dashboard analítico interativo no navegador via Streamlit. |
| `poetry run task test` | Executa pytest com verificação de cobertura (mínimo de 50%). |
| `poetry run task lint` | Executa `ruff check .` e `ruff format --check .`. |
| `poetry run task format` | Executa `ruff format .` e `ruff check . --fix`. |
| `poetry run task docs` | Inicia o servidor local do MkDocs com live-reload. |
| `poetry run task build-docs` | Compila a documentação técnica em modo estrito (`--strict`). |

---

## Execução dos Testes Automatizados

Para executar os testes com enforcement de cobertura mínima (>= 50%):

```bash
# Via Taskipy
poetry run task test

# Ou diretamente pelo Pytest
poetry run pytest --cov=f1 --cov-report=term-missing --cov-fail-under=50
```

### Detalhes das Suítes:
- **`tests/unit/test_models.py`:** Testa a validação e deserialização dos 18 modelos Pydantic v2 e constantes.
- **`tests/unit/test_filters.py`:** Testa operadores de query, serialização de tipos primitivos e montagem de query strings.
- **`tests/unit/test_client.py`:** Testa os 18 métodos do cliente com mocks HTTP, retries e tratamento de exceções.
- **`tests/unit/test_utils.py`:** Testa normalização de datas ISO 8601 e conversões para pandas DataFrame.
- **`tests/integration/test_workflow.py`:** Valida o pipeline completo de ponta a ponta simulando extração analítica.

---

## Verificação e Formatação de Código com Ruff

O projeto utiliza o **Ruff** para análise estática e padronização visual do código:

```bash
# 1. Análise de linting com autocorreção
poetry run ruff check . --fix

# 2. Formatação de código
poetry run ruff format .

# 3. Verificação de conformidade da formatação (modo estrito)
poetry run ruff format --check .
```

---

## Compilação Estrita da Documentação

Para validar se não há links quebrados nem advertências de compilação:

```bash
poetry run mkdocs build --strict
```

