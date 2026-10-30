# F1 - OpenF1 Python SDK

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Testing: Pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![Docs: MkDocs Material](https://img.shields.io/badge/docs-mkdocs--material-526CFE.svg)](https://squidfunk.github.io/mkdocs-material/)

SDK Python moderno, fortemente tipado e resiliente para consumo, modelagem e análise de dados da [OpenF1 API](https://openf1.org/).

---

## Recursos Principais

- **Cobertura Completa da OpenF1:** Suporte aos 18 endpoints oficiais (telemetria de alta frequência `car_data`, tempos de volta, posições, rádio, meteorologia, resultados e campeonatos).
- **Tipagem Forte e Validação com Pydantic v2:** Validação em tempo de execução com schemas tipados para cada entidade.
- **Filtros Avançados:** Suporte nativo a operadores de comparação (`=`, `<`, `<=`, `>`, `>=`), valores múltiplos e o identificador `latest`.
- **Análise de Dados com Pandas:** Métodos auxiliares para converter coleções de dados diretamente em `pandas.DataFrame` ou consumir o formato CSV nativo da API.
- **Resiliência HTTP:** Retry com backoff exponencial automático para erros transitórios (429, 500, 502, 503, 504) e timeouts defensivos configuráveis.
- **Padrões de Engenharia Estritos:** 100% aderente ao layout `src/`, formatação e linting via Ruff, cobertura de testes com Pytest >= 50% e documentação técnica em MkDocs Material.

---

## Instalação

O projeto utiliza o **Poetry** para isolamento e gerenciamento de dependências:

```bash
# Clone o repositório
git clone https://github.com/estudarposnascimento/f1.git
cd f1

# Garanta a versão correta do Python (3.12+)
pyenv local 3.12.10

# Instale as dependências
poetry install
```

---

## Guia de Início Rápido

### 1. Consultando Pilotos de uma Sessão

```python
from f1 import OpenF1Client

client = OpenF1Client()

# Buscar pilotos da última sessão
drivers = client.get_drivers(session_key="latest")
for driver in drivers:
    print(f"#{driver.driver_number} - {driver.full_name} ({driver.team_name})")
```

### 2. Telemetria e Análise com Pandas

```python
from f1 import OpenF1Client
from f1.utils import to_dataframe

client = OpenF1Client()

# Consultar telemetria com filtro de velocidade
car_data = client.get_car_data(
    session_key=9159,
    driver_number=55,
    speed__gte=315,
)

# Converter em DataFrame para análise
df = to_dataframe(car_data)
print(df[["date", "speed", "rpm", "throttle", "brake"]].head())
```

### 3. Exportação Direta para CSV

```python
from f1 import OpenF1Client

client = OpenF1Client()
csv_text = client.get_meetings(year=2024, csv=True)
with open("meetings_2024.csv", "w", encoding="utf-8") as f:
    f.write(csv_text)
```

### 4. Dashboard Interativo com Streamlit

```bash
# Iniciar o dashboard analítico
poetry run task dashboard
```

---

## Desenvolvimento e Automação de Tarefas (Taskipy)

O projeto conta com atalhos automatizados configurados via **Taskipy**:

```bash
# Iniciar o dashboard analítico interativo (Streamlit)
poetry run task dashboard

# Executar todos os testes com cobertura mínima de 50%
poetry run task test

# Verificar formatação e análise estática (lint)
poetry run task lint

# Aplicar formatação automática e correções com Ruff
poetry run task format

# Iniciar servidor local da documentação MkDocs
poetry run task docs

# Compilar documentação técnica em modo estrito
poetry run task build-docs
```

Você também pode executar os comandos diretamente:

```bash
# Execução direta do Pytest com relatório de cobertura
poetry run pytest --cov=f1 --cov-report=term-missing --cov-fail-under=50

# Execução direta do Ruff
poetry run ruff check .
poetry run ruff format --check .
```

---

## Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais detalhes.
