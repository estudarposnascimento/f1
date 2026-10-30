# Especificação do Pipeline Analítico

!!! warning "Status da implementação"
		Este documento descreve a arquitetura-alvo do pipeline analítico. O repositório
		atualmente contém o SDK cliente OpenF1; a ingestão, o banco DuckDB e as camadas
		`raw`, `metadata`, `refined` e `gold` ainda não estão implementados. A configuração
		vigente do pacote continua definida em `pyproject.toml`.

## Tecnologias-alvo

| Tecnologia | Responsabilidade |
| --- | --- |
| Python 3.13 | Linguagem principal do pipeline. |
| `uv` | Gerenciamento de dependências e ambientes. |
| HTTPX | Comunicação HTTP com a OpenF1 API. |
| pandas | Manipulação tabular e apoio à análise. |
| DuckDB | Armazenamento e consultas analíticas locais. |
| SQL | Transformações e modelagem das camadas analíticas. |
| pytest | Testes automatizados. |
| DuckDB UI | Exploração visual do banco já criado. |
| SHA-256 | Identificação e comparação de conteúdo. |
| Git | Controle de versão do código e da documentação. |

> Antes de tratar essa pilha como ambiente executável, alinhe `pyproject.toml`, o
> lockfile e os guias de instalação com Python 3.13 e `uv`. Hoje o pacote ainda declara
> Python 3.12.10 ou superior, Poetry e `requests`.

## Banco de dados

- **Arquivo:** `formula1.duckdb`, na raiz do projeto.
- **Schemas obrigatórios:** `raw`, `metadata`, `refined` e `gold`.
- A rotina de inicialização da ingestão cria o arquivo e os schemas necessários.
- A DuckDB UI é somente uma interface de exploração; não cria um banco ausente.
- A interface deve informar claramente quando o arquivo ainda não foi gerado pela
	ingestão.

## Catálogo de endpoints

O pipeline deve cobrir os 18 endpoints. Os filtros abaixo são os parâmetros de consulta
mais relevantes para cada recurso, não uma lista de parâmetros obrigatórios. A API
aceita filtros pelos campos escalares disponíveis em cada endpoint; operadores
relacionais e os limites de disponibilidade devem seguir a documentação oficial da
[OpenF1 API](https://openf1.org/docs/).

| Endpoint | Tabela RAW | Parâmetros de consulta usuais |
| --- | --- | --- |
| `meetings` | `grandes_premios` | `year`, `meeting_key`, `circuit_key`, `country_name` |
| `sessions` | `sessoes` | `year`, `meeting_key`, `session_key`, `session_name`, `session_type`, `date_start` |
| `drivers` | `pilotos` | `session_key`, `meeting_key`, `driver_number`, `name_acronym`, `team_name` |
| `car_data` | `telemetria_carros` | `session_key`, `meeting_key`, `driver_number`, `date`, `speed`, `rpm`, `n_gear` |
| `laps` | `voltas` | `session_key`, `meeting_key`, `driver_number`, `lap_number`, `lap_duration` |
| `location` | `localizacao_carros` | `session_key`, `meeting_key`, `driver_number`, `date`, `x`, `y`, `z` |
| `position` | `posicoes` | `session_key`, `meeting_key`, `driver_number`, `date`, `position` |
| `intervals` | `intervalos` | `session_key`, `meeting_key`, `driver_number`, `date`, `interval`, `gap_to_leader` |
| `stints` | `stints_pneus` | `session_key`, `meeting_key`, `driver_number`, `stint_number`, `compound`, `lap_start` |
| `pit` | `paradas_box` | `session_key`, `meeting_key`, `driver_number`, `lap_number`, `date` |
| `weather` | `clima` | `session_key`, `meeting_key`, `date`, `air_temperature`, `track_temperature`, `rainfall` |
| `race_control` | `controle_corrida` | `session_key`, `meeting_key`, `date`, `category`, `flag`, `driver_number`, `lap_number` |
| `session_result` | `resultados_sessao` | `session_key`, `meeting_key`, `driver_number`, `position`, `dnf`, `dns`, `dsq` |
| `starting_grid` | `grid_largada` | `session_key`, `meeting_key`, `driver_number`, `position` |
| `overtakes` | `ultrapassagens` | `session_key`, `meeting_key`, `date`, `overtaking_driver_number`, `overtaken_driver_number` |
| `team_radio` | `radio_equipes` | `session_key`, `meeting_key`, `driver_number`, `date` |
| `championship_drivers` | `campeonato_pilotos` | `session_key`, `meeting_key`, `driver_number`, `position_current` |
| `championship_teams` | `campeonato_equipes` | `session_key`, `meeting_key`, `team_name`, `position_current` |

### Disponibilidade e granularidade

- Consultas devem respeitar a temporada e a sessão em que cada endpoint possui dados.
- Ausência de registros para um contexto válido deve ser registrada como `SEM_DADOS`,
	não como falha da execução.
- Não criar registros artificiais para preencher lacunas da API.
- Considerar as diferenças de disponibilidade e granularidade entre endpoints antes
	de definir chaves, janelas de extração ou relacionamentos.
- A ausência de dados e uma falha HTTP, de validação ou de persistência são estados
	distintos e devem permanecer distinguíveis nos metadados.

## Camada RAW

**Schema:** `raw`.

### Objetivo e colunas

A camada RAW preserva a resposta da API para auditoria e reprocessamento. Cada tabela
deve manter os campos originais e, conforme aplicável ao endpoint, os seguintes campos
de contexto:

| Campo | Finalidade |
| --- | --- |
| `payload_original` | JSON original recebido da API. |
| `id_ingestao` | Identificador da ingestão responsável pelo registro. |
| `data_extracao` | Data e hora da extração. |
| `endpoint_origem` | Endpoint consultado. |
| `ano_referencia` | Temporada dos dados. |
| `meeting_key` | Identificador do Grande Prêmio, quando aplicável. |
| `session_key` | Identificador da sessão, quando aplicável. |
| `hash_conteudo` | SHA-256 do conteúdo canônico. |

### Política de armazenamento

- Preservar todas as extrações sem sobrescrever versões históricas.
- Não corrigir regras de negócio nem remover duplicidades na origem nesta camada.
- Manter o JSON original junto de colunas consultáveis para SQL.
- Registrar a execução que produziu cada extração.
- Calcular o hash sobre uma representação JSON canônica para comparar conteúdos,
	detectar alterações e apoiar o controle incremental. O hash não substitui chaves
	naturais da API.

### Endpoints de alto volume

`car_data` e `location` exigem extração segmentada por sessão e intervalo temporal. O
pipeline deve controlar o tamanho das respostas, persistir cada segmento e registrar o
estado da execução para permitir retomada sem perda ou duplicação indevida.

### Team Radio

`raw.radio_equipes` armazena os metadados do registro e a URL da gravação. O pipeline
não baixa nem armazena o arquivo de áudio.

## Camada METADATA

**Schema:** `metadata`. Esta camada controla o estado operacional, o histórico de
extrações e a rastreabilidade das transformações.

| Tabela | Granularidade e campos previstos |
| --- | --- |
| `metadata.execucoes` | Uma linha por execução: `id_execucao`, `tipo_execucao`, `data_inicio`, `data_fim`, `status`, `temporadas`, `total_endpoints`, `total_registros`, `mensagem_erro`. |
| `metadata.historico_extracoes` | Uma linha por operação, endpoint e contexto: `id_extracao`, `id_execucao`, `endpoint`, `meeting_key`, `session_key`, `data_inicio`, `data_fim`, `status`, `quantidade_registros`, `hash_conteudo`, `mensagem_erro`. |
| `metadata.controle_sessoes` | Estado por sessão: `session_key`, `meeting_key`, `ano_referencia`, `ultima_extracao`, `ultimo_hash`, `status_processamento`, `data_ultima_alteracao`. |

### Estados operacionais

| Status | Significado |
| --- | --- |
| `EXECUTANDO` | Operação em andamento. |
| `CONCLUIDA` | Operação finalizada com sucesso. |
| `FALHA` | Operação interrompida por erro. |
| `PARCIAL` | Parte dos dados foi processada. |
| `SEM_DADOS` | Endpoint sem registros para o contexto consultado. |

Toda transformação deve permitir identificar a execução e extração de origem, a sessão
relacionada, a versão dos dados processados e o momento do processamento.

## Camada REFINED

**Schema:** `refined`. Os dados brutos são convertidos em estruturas tipadas,
consistentes e relacionáveis.

### Dimensões

| Tabela | Chave natural | Conteúdo |
| --- | --- | --- |
| `dim_grandes_premios` | `meeting_key` | Grandes Prêmios. |
| `dim_sessoes` | `session_key` | Treinos, classificação, sprint e corrida. |
| `dim_pilotos` | Identificador natural com contexto histórico | Pilotos. |
| `dim_equipes` | Identificador natural com contexto histórico | Equipes. |
| `dim_circuitos` | `circuit_key` | Circuitos. |

As dimensões de pilotos e equipes devem preservar histórico por SCD Tipo 2: chave
substituta, identificador natural, início e fim de validade, indicador da versão atual e
atributos históricos. Alterações geram nova versão; versões anteriores não são apagadas.

### Tabelas fato e granularidade

| Tabela | Granularidade |
| --- | --- |
| `fato_voltas` | Piloto por volta. |
| `fato_telemetria` | Piloto por instante. |
| `fato_localizacao` | Piloto por instante. |
| `fato_posicoes` | Piloto por instante. |
| `fato_intervalos` | Piloto por instante. |
| `fato_stints` | Piloto por stint. |
| `fato_pit_stops` | Piloto por parada. |
| `fato_clima` | Registro meteorológico por instante. |
| `fato_controle_corrida` | Evento de controle. |
| `fato_ultrapassagens` | Evento de ultrapassagem. |
| `fato_resultados` | Piloto por sessão. |
| `fato_grid_largada` | Piloto por posição inicial. |
| `fato_campeonato_pilotos` | Piloto por sessão. |
| `fato_campeonato_equipes` | Equipe por sessão. |

Rádio de equipe é um evento relacionado à sessão e ao piloto quando esses dados
estiverem disponíveis.

### Qualidade e rejeições

As transformações devem padronizar nomes e tipos, converter datas para `TIMESTAMP` em
UTC, preservar valores nulos, validar chaves naturais e estrangeiras, tratar duplicidade
conforme a granularidade, manter histórico dimensional e permitir reprocessamento
idempotente.

Registros inválidos devem ser registrados em `refined.rejeicoes`, sem descarte
silencioso:

`id_rejeicao`, `id_execucao`, `endpoint_origem`, `tabela_origem`, `session_key`,
`registro_original`, `campo_rejeitado`, `valor_rejeitado`, `motivo_rejeicao` e
`data_rejeicao`.

## Relacionamentos e JOINs

| Chave | Utilização |
| --- | --- |
| `meeting_key` | Relacionar dados ao Grande Prêmio. |
| `session_key` | Relacionar dados à sessão. |
| `driver_number` | Identificar piloto dentro do contexto de uma sessão. |
| `circuit_key` | Relacionar dados ao circuito. |
| `lap_number` | Relacionar registros à volta. |
| `stint_number` | Relacionar registros ao stint. |

`driver_number` não é identificador global suficiente entre temporadas. Preserve o
contexto da sessão e o histórico dimensional em toda associação.

Exemplo de consulta analítica planejada, após a criação das tabelas REFINED:

```sql
SELECT
		gp.meeting_name,
		sess.session_name,
		volta.driver_number,
		volta.lap_number,
		volta.lap_duration
FROM refined.fato_voltas AS volta
JOIN refined.dim_sessoes AS sess
		ON sess.session_key = volta.session_key
JOIN refined.dim_grandes_premios AS gp
		ON gp.meeting_key = sess.meeting_key
WHERE sess.year = 2024
ORDER BY gp.meeting_name, volta.driver_number, volta.lap_number;
```
