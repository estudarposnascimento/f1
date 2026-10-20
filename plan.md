# Plano de Implementação do Projeto F1 (OpenF1 Python SDK)

> **Documento:** `plan.md`  
> **Status:** Aprovado para Execução  
> **Fontes de Referência:** [`doc.api.md`](file:///c:/workspace/projeto_python/projeto_aula/f1/doc.api.md) e [`SKILL.md`](file:///c:/workspace/projeto_python/projeto_aula/f1/SKILL.md)  
> **Diretrizes Arquiteturais:** Python 3.12+, Poetry, `src/` layout, Pydantic v2, Ruff, Pytest (cobertura >= 50%), MkDocs Material.

---

## 1. Visão Geral e Objetivos do Projeto

O objetivo deste projeto é construir um SDK / biblioteca Python moderna, tipada e resiliente chamada **`f1`**, dedicada ao consumo, modelagem e análise dos dados da API pública [OpenF1](https://openf1.org/docs/#api-endpoints).

### Metas Principais:
1. **Cliente HTTP Padronizado e Tipado:** Consumir os 18 endpoints da OpenF1 com suporte nativo a filtros flexíveis (`=`, `<`, `<=`, `>`, `>=`), valores múltiplos e o identificador especial `latest`.
2. **Modelos de Domínio com Pydantic v2:** Validação estrita, tipagem completa e serialização de dados (telemetria, tempos de volta, posições, rádio, meteorologia, etc.).
3. **Integração com Análise de Dados:** Suporte transparente para conversão em `pandas.DataFrame` e exportação nativa em CSV (`csv=true`).
4. **Excelência de Engenharia:** Aderência integral às diretrizes da `SKILL.md` (Poetry isolado, `src/` layout, Ruff linter/formatter, suíte de testes com cobertura >= 50% e documentação MkDocs Material com compilação estrita).

---

## 2. Estrutura Canônica do Repositório (`src/` layout)

Conforme prescrito na seção 3 da [`SKILL.md`](file:///c:/workspace/projeto_python/projeto_aula/f1/SKILL.md), o projeto adotará a seguinte árvore de diretórios:

```text
f1/
├── .gitignore                     # Bloqueio de venvs, caches, .env, artefatos de build
├── .python-version                # Fixação do interpretador Python (3.12.x)
├── pyproject.toml                 # Configuração centralizada (Poetry, Ruff, Pytest, Coverage)
├── poetry.lock                    # Árvore determinística de dependências
├── README.md                      # Apresentação do projeto, instalação e quickstart
├── SKILL.md                       # Padrões operacionais de engenharia
├── doc.api.md                     # Especificação técnica dos endpoints da OpenF1
├── plan.md                        # Este plano de execução
├── mkdocs.yml                     # Configuração do site MkDocs Material
├── src/
│   └── f1/                        # Pacote raiz da biblioteca
│       ├── __init__.py            # Exposição da versão e interfaces públicas principais
│       ├── exceptions.py          # Hierarquia de exceções de domínio
│       ├── core/                  # Modelos Pydantic, enums e constantes
│       │   ├── __init__.py
│       │   ├── constants.py       # Enums: DRSStatus, TyreCompound, FlagType, SessionType
│       │   ├── models.py          # Modelos de dados para os 18 endpoints
│       │   └── filters.py         # Construtor e validador de query parameters e operadores
│       ├── clients/               # Camada de comunicação de rede
│       │   ├── __init__.py
│       │   ├── base.py            # Cliente HTTP base (sessão, retries, headers, timeouts)
│       │   └── openf1.py          # OpenF1Client com métodos específicos para cada endpoint
│       └── utils/                 # Formatadores, conversores e rotinas auxiliares puras
│           ├── __init__.py
│           ├── datetime.py        # Normalização e parsing de timestamps ISO 8601 / UTC
│           └── dataframe.py       # Conversores para Pandas DataFrame
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures de mocks HTTP, payloads de exemplo da OpenF1
│   ├── unit/                      # Testes unitários puros (sem I/O ou chamadas de rede reais)
│   │   ├── __init__.py
│   │   ├── test_models.py         # Validação dos modelos Pydantic
│   │   ├── test_filters.py        # Validação da montagem de filtros e operadores
│   │   ├── test_client.py         # Teste dos métodos do OpenF1Client com mocks
│   │   └── test_utils.py          # Teste de conversores datetime e dataframe
│   └── integration/               # Testes de integração de fluxo de componentes
│       ├── __init__.py
│       └── test_workflow.py       # Fluxo integrado (consulta -> validação de modelo -> dataframe)
└── docs/
    ├── index.md                   # Home da documentação
    ├── setup.md                   # Instalação, requisitos e configuração de ambiente
    ├── architecture.md            # Arquitetura em camadas e decisões de design
    ├── api_reference.md           # Referência completa do OpenF1Client e endpoints
    └── testing.md                 # Guia de testes, execução e métricas de cobertura
```

---

## 3. Mapeamento de Endpoints da OpenF1 (`doc.api.md`)

O cliente `OpenF1Client` fornecerá métodos específicos e tipados para todos os recursos documentados em [`doc.api.md`](file:///c:/workspace/projeto_python/projeto_aula/f1/doc.api.md):

| # | Endpoint | Método do Cliente | Modelo Pydantic Principal | Descrição Resumida |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `/v1/car_data` | `get_car_data(...)` | `CarData` | Telemetria a ~3.7 Hz (velocidade, rpm, marcha, acelerador, freio, DRS). |
| 2 | `/v1/championship_drivers` | `get_championship_drivers(...)` | `ChampionshipDriver` | Classificação do mundial de pilotos. |
| 3 | `/v1/championship_teams` | `get_championship_teams(...)` | `ChampionshipTeam` | Classificação do mundial de construtores/equipes. |
| 4 | `/v1/drivers` | `get_drivers(...)` | `Driver` | Detalhes cadastrais dos pilotos na sessão. |
| 5 | `/v1/intervals` | `get_intervals(...)` | `Interval` | Intervalos e gap para o líder atualizados a cada ~4s. |
| 6 | `/v1/laps` | `get_laps(...)` | `Lap` | Tempos de volta, setores 1/2/3, mini-setores e speed traps. |
| 7 | `/v1/location` | `get_location(...)` | `CarLocation` | Coordenadas espaciais tridimensionais (X, Y, Z). |
| 8 | `/v1/meetings` | `get_meetings(...)` | `Meeting` | Grandes Prêmios, circuitos e calendários de fim de semana. |
| 9 | `/v1/overtakes` | `get_overtakes(...)` | `Overtake` | Registros de ultrapassagens e trocas de posição em pista. |
| 10 | `/v1/pit` | `get_pit(...)` | `PitStop` | Tempos no pit lane e paradas para troca de pneus. |
| 11 | `/v1/position` | `get_position(...)` | `Position` | Posições cronológicas dos pilotos ao longo da prova. |
| 12 | `/v1/race_control` | `get_race_control(...)` | `RaceControlMessage` | Mensagens da FIA (bandeiras, safety car, investigações). |
| 13 | `/v1/sessions` | `get_sessions(...)` | `Session` | Sessões de treinos livres, sprint e corridas. |
| 14 | `/v1/session_result` | `get_session_results(...)` | `SessionResult` | Resultado e classificação oficial homologada. |
| 15 | `/v1/starting_grid` | `get_starting_grid(...)` | `StartingGrid` | Grid oficial de largada para sprint e corrida. |
| 16 | `/v1/stints` | `get_stints(...)` | `Stint` | Trechos com mesmo jogo de pneus e idade do composto. |
| 17 | `/v1/team_radio` | `get_team_radio(...)` | `TeamRadio` | URLs para arquivos de áudio dos rádios de comunicação. |
| 18 | `/v1/weather` | `get_weather(...)` | `Weather` | Condições climáticas da pista minuto a minuto. |

---

## 4. Fases de Execução do Projeto

O desenvolvimento seguirá o ciclo estrito em 12 etapas estabelecido na seção 8 da [`SKILL.md`](file:///c:/workspace/projeto_python/projeto_aula/f1/SKILL.md):

### Fase 1: Configuração do Ambiente e Ferramentas
- [ ] Criar `.python-version` fixando Python 3.12.
- [ ] Atualizar `pyproject.toml` integrando:
  - Dependências de produção: `pydantic>=2.7.0`, `requests>=2.31.0`, `pandas>=2.2.0`.
  - Dependências de dev: `pytest>=8.2.0`, `pytest-cov>=5.0.0`, `pytest-mock>=3.14.0`, `ruff>=0.4.0`, `mkdocs>=1.6.0`, `mkdocs-material>=9.5.0`.
  - Configuração do Ruff (`line-length = 88`, `quote-style = "double"`, regras `E`, `W`, `F`, `I`, `B`, `C4`, `UP`, `ARG`, `SIM`, `PTH`).
  - Configuração do Pytest (`testpaths = ["tests"]`, `pythonpath = ["src"]`).
  - Configuração do Coverage com barreira inegociável `fail_under = 50`.
- [ ] Configurar `.gitignore` completo impedindo versionamento de `.venv`, `__pycache__`, `.coverage`, `site/` e `.env`.

### Fase 2: Camada de Domínio e Modelos (`src/f1/core`)
- [ ] Implementar hierarquia de exceções semânticas em `src/f1/exceptions.py` (`OpenF1Exception`, `OpenF1APIError`, `OpenF1ConnectionError`, `OpenF1ValidationError`).
- [ ] Implementar `src/f1/core/constants.py` com Enums fortemente tipados (`DRSStatus`, `TyreCompound`, `FlagType`, `SessionType`, `CircuitType`).
- [ ] Implementar `src/f1/core/filters.py` com mecanismo de parsing para filtros e operadores de comparação (`=, <, <=, >, >=`), validação de datas e valores múltiplos.
- [ ] Implementar `src/f1/core/models.py` contendo os schemas Pydantic v2 para todos os 18 endpoints da OpenF1, com validações de tipos opcionais, timestamps e arrays.

### Fase 3: Cliente HTTP da OpenF1 (`src/f1/clients`)
- [ ] Implementar `src/f1/clients/base.py`:
  - Sessão HTTP com retry exponencial em erros transitórios (status 429, 500, 502, 503, 504).
  - Timeouts defensivos.
  - Tratamento e tradução de códigos de erro HTTP para exceções de domínio.
- [ ] Implementar `src/f1/clients/openf1.py` (`OpenF1Client`):
  - Construtor aceitando `base_url`, `timeout` e `session`.
  - Métodos dedicados para cada um dos 18 endpoints com type annotations estritas.
  - Suporte a retorno tipado (instâncias Pydantic), dicionários brutos e formato CSV nativo via `csv=True`.

### Fase 4: Utilitários e Integração com Pandas (`src/f1/utils`)
- [ ] Implementar `src/f1/utils/datetime.py` para formatação compatível de datas aceitas pela API.
- [ ] Implementar `src/f1/utils/dataframe.py` para conversão simplificada de listas de modelos em `pandas.DataFrame`.
- [ ] Expor interfaces principais em `src/f1/__init__.py` (`OpenF1Client`, exceções e versão `__version__ = "0.1.0"`).

### Fase 5: Implementação dos Testes Automatizados (`tests/`)
- [ ] Configurar `tests/conftest.py` com fixtures de payloads JSON reais simulando respostas da API.
- [ ] Implementar `tests/unit/test_models.py` validando integridade e serialização dos modelos Pydantic.
- [ ] Implementar `tests/unit/test_filters.py` validando montagem de queries complexas e operadores.
- [ ] Implementar `tests/unit/test_client.py` mockando respostas HTTP e testando cenários de sucesso, respostas vazias e tratamento de falhas (4xx/5xx).
- [ ] Implementar `tests/unit/test_utils.py` testando conversão de datas e transformação em DataFrame.
- [ ] Implementar `tests/integration/test_workflow.py` validando o ciclo completo mockado (requisição -> validação -> manipulação).
- [ ] Validar cobertura com comando obrigatório:  
  `poetry run pytest --cov=f1 --cov-report=term-missing --cov-fail-under=50`.

### Fase 6: Validação de Qualidade e Formatação com Ruff
- [ ] Executar `poetry run ruff check . --fix` garantindo zero violações.
- [ ] Executar `poetry run ruff format .` padronizando todo o código-fonte.
- [ ] Validar conformidade estrita com `poetry run ruff format --check .`.

### Fase 7: Documentação Técnica MkDocs Material (`docs/` & `mkdocs.yml`)
- [ ] Configurar `mkdocs.yml` com tema Material, esquema claro/escuro e navegação estruturada.
- [ ] Criar `docs/index.md` (visão geral, instalação rápida e primeiro exemplo).
- [ ] Criar `docs/setup.md` (guia passo a passo de ambiente virtual, Poetry e dependências).
- [ ] Criar `docs/architecture.md` (diagrama arquitetural, fluxo de dados e design decisions).
- [ ] Criar `docs/api_reference.md` (tabela de endpoints, assinaturas de métodos e exemplos de código).
- [ ] Criar `docs/testing.md` (procedimentos de execução de testes e relatório de cobertura).
- [ ] Validar build estrito com `poetry run mkdocs build --strict` (sem links quebrados nem advertências).

### Fase 8: Auditoria Final e Emissão do Relatório
- [ ] Executar o checklist operacional de 11 itens da [`SKILL.md`](file:///c:/workspace/projeto_python/projeto_aula/f1/SKILL.md).
- [ ] Emitir relatório com as evidências reais de execução dos comandos de terminal.

---

## 5. Matriz de Qualidade e Critérios de Aceite

| Requisito | Meta Estrita | Ferramenta / Validação |
| :--- | :--- | :--- |
| **Cobertura de Testes** | >= 50% das linhas de `src/f1` | `pytest-cov` com flag `--cov-fail-under=50` |
| **Isolamento de Testes** | 100% livre de I/O e chamadas externas | Fixtures e mocks com `unittest.mock` / `pytest-mock` |
| **Lint e Formatação** | Zero erros e zero avisos pendentes | `ruff check .` e `ruff format --check .` |
| **Tipagem Estrita** | 100% das assinaturas públicas tipadas | Type hints em funções, métodos e modelos Pydantic |
| **Compilação de Docs** | Zero warnings ou links quebrados | `mkdocs build --strict` |
| **Segurança e Segredos** | Zero credenciais no Git | `.gitignore` configurado e auditado |

