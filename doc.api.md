# Documentação da API OpenF1

> Documentação técnica completa e estruturada da API pública [OpenF1](https://openf1.org/docs/#api-endpoints).

---

## 1. Visão Geral

A **OpenF1** é uma API aberta que disponibiliza dados detalhados de telemetria, cronometragem, rádio e eventos das sessões de Fórmula 1 em formatos **JSON** e **CSV**.

- **URL Base:** `https://api.openf1.org/v1`
- **Autenticação:** Não necessária para dados históricos (disponíveis a partir da temporada de 2023). Acesso a telemetria em tempo real (live timing) requer assinatura com token de acesso.
- **Formato padrão:** `application/json`
- **Formato alternativo:** CSV (basta adicionar o parâmetro `csv=true` na query string).
- **Aviso Legal:** Projeto não-oficial sem afiliação direta com a Formula One Licensing B.V. ou o Grupo Formula 1.

---

## 2. Mecanismos de Filtro e Parâmetros de Consulta

Qualquer atributo dos endpoints (exceto campos do tipo vetor/array) pode ser utilizado como filtro na URL (Query String).

### 2.1 Operadores de Comparação
A API suporta múltiplos operadores em parâmetros numéricos e de data:

| Operador | Significado | Exemplo |
| :--- | :--- | :--- |
| `=` | Igual | `driver_number=1` |
| `<` | Menor que | `position<3` |
| `<=` | Menor ou igual | `speed<=300` |
| `>` | Maior que | `track_temperature>45` |
| `>=` | Maior ou igual | `lap_duration>=120` |

### 2.2 Filtros de Múltiplos Valores
É possível passar a mesma chave várias vezes para buscar múltiplos valores:
```text
https://api.openf1.org/v1/championship_drivers?session_key=9839&driver_number=4&driver_number=81
```

### 2.3 Identificador Especial `latest`
Nos parâmetros `meeting_key` e `session_key`, é possível passar o valor especial `latest` para obter automaticamente o evento ou sessão mais recente:
```text
https://api.openf1.org/v1/sessions?session_key=latest
```

### 2.4 Filtros Temporais e Formatos de Data
Para filtrar períodos (por exemplo, em `date`, `date_start`, `date_end`), pode-se combinar operadores `>=` e `<=`. A API aceita qualquer formato interpretável pelo módulo `dateutil.parser.parse` do Python, incluindo:
- `YYYY-MM-DD` (ex: `2023-09-10`)
- `YYYY-MM-DDTHH:MM:SS` ou `YYYY-MM-DDTHH:MM:SS+00:00` (ISO 8601 UTC)
- `DD/MM/YYYY` ou `MM/DD/YYYY`
- Formatos por extenso (ex: `10 September 2023`, `Sep 10, 2023`)

Exemplo de busca por período:
```text
https://api.openf1.org/v1/sessions?date_start>=2023-09-01&date_end<=2023-09-30
```

### 2.5 Exportação para Formato CSV
Para exportar os resultados diretamente em arquivo tabular CSV (ideal para análise em Excel, Sheets ou Pandas):
```text
https://api.openf1.org/v1/sessions?year=2023&csv=true
```

---

## 3. Catálogo de Endpoints

### 3.1 `GET /v1/car_data`
Telemetria em alta frequência (~3.7 Hz) de cada carro na pista (velocidade, rotação do motor, marcha, acelerador, freio e DRS).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/car_data?driver_number=55&session_key=9159&speed>=315"
```

```python
from urllib.request import urlopen
import json

url = "https://api.openf1.org/v1/car_data?driver_number=55&session_key=9159&speed>=315"
response = urlopen(url)
data = json.loads(response.read().decode("utf-8"))
```

#### Exemplo de Resposta
```json
[
  {
    "brake": 0,
    "date": "2023-09-15T13:08:19.923000+00:00",
    "driver_number": 55,
    "drs": 12,
    "meeting_key": 1219,
    "n_gear": 8,
    "rpm": 11141,
    "session_key": 9159,
    "speed": 315,
    "throttle": 99
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `brake` | `integer` | Status do freio: `0` (não pressionado) ou `100` (pressionado). |
| `date` | `string` | Data e hora em formato ISO 8601 (UTC). |
| `driver_number` | `integer` | Número permanente do piloto na temporada. |
| `drs` | `integer` | Código do status do DRS (ver tabela abaixo). |
| `meeting_key` | `integer` / `string` | ID do final de semana (aceita `latest`). |
| `n_gear` | `integer` | Marcha atual engatada (1 a 8; `0` indica neutro ou desacoplado). |
| `rpm` | `integer` | Rotações por minuto do motor. |
| `session_key` | `integer` / `string` | ID da sessão (aceita `latest`). |
| `speed` | `integer` | Velocidade do veículo em km/h. |
| `throttle` | `integer` | Porcentagem do acelerador (0 a 100). |

#### Mapeamento de Status do DRS
| Valor DRS | Interpretação |
| :--- | :--- |
| `0`, `1` | DRS desligado / fechado |
| `2`, `3`, `9` | Indeterminado / transitório |
| `8` | Detectado; elegível para abertura na zona de ativação |
| `10`, `12`, `14` | DRS ativado / aberto |

---

### 3.2 `GET /v1/championship_drivers` (Beta)
Classificação atualizada e pontuação do Campeonato Mundial de Pilotos (disponível apenas para sessões de Corrida).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/championship_drivers?session_key=9839&driver_number=4&driver_number=81"
```

#### Exemplo de Resposta
```json
[
  {
    "driver_number": 4,
    "meeting_key": 1276,
    "points_current": 423,
    "points_start": 408,
    "position_current": 1,
    "position_start": 1,
    "session_key": 9839
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `driver_number` | `integer` | Número do piloto. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `points_current` | `number` | Pontos no campeonato durante/após a corrida. |
| `points_start` | `number` | Pontos no campeonato antes do início da corrida. |
| `position_current` | `integer` | Posição no campeonato durante/após a corrida. |
| `position_start` | `integer` | Posição no campeonato antes do início da corrida. |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.3 `GET /v1/championship_teams` (Beta)
Classificação atualizada e pontuação do Campeonato Mundial de Construtores/Equipes (disponível apenas para sessões de Corrida).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/championship_teams?session_key=9839&team_name=McLaren"
```

#### Exemplo de Resposta
```json
[
  {
    "meeting_key": 1276,
    "points_current": 833,
    "points_start": 800,
    "position_current": 1,
    "position_start": 1,
    "session_key": 9839,
    "team_name": "McLaren"
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `points_current` | `number` | Pontos da equipe durante/após a corrida. |
| `points_start` | `number` | Pontos da equipe antes do início da corrida. |
| `position_current` | `integer` | Posição da equipe no campeonato durante/após a corrida. |
| `position_start` | `integer` | Posição da equipe no campeonato antes do início da corrida. |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `team_name` | `string` | Nome da equipe/construtor. |

---

### 3.4 `GET /v1/drivers`
Informações e metadados sobre os pilotos participantes de uma sessão específica.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/drivers?driver_number=1&session_key=9158"
```

#### Exemplo de Resposta
```json
[
  {
    "broadcast_name": "M VERSTAPPEN",
    "driver_number": 1,
    "first_name": "Max",
    "full_name": "Max VERSTAPPEN",
    "headshot_url": "https://www.formula1.com/.../maxver01.png",
    "last_name": "Verstappen",
    "meeting_key": 1219,
    "name_acronym": "VER",
    "session_key": 9158,
    "team_colour": "3671C6",
    "team_name": "Red Bull Racing"
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `broadcast_name` | `string` | Nome do piloto exibido na transmissão oficial. |
| `country_code` | `string` | *(Obsoleto)* Código do país (será descontinuado ao fim de 2026). |
| `driver_number` | `integer` | Número do piloto. |
| `first_name` | `string` | Primeiro nome do piloto. |
| `full_name` | `string` | Nome completo do piloto. |
| `headshot_url` | `string` | URL com foto do rosto do piloto. |
| `last_name` | `string` | Sobrenome do piloto. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `name_acronym` | `string` | Sigla de 3 letras do piloto (ex: `VER`, `HAM`, `NOR`). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `team_colour` | `string` | Cor oficial da equipe em formato hexadecimal (RRGGBB). |
| `team_name` | `string` | Nome da equipe. |

---

### 3.5 `GET /v1/intervals`
Intervalos de tempo em tempo real entre pilotos e a diferença (gap) para o líder da prova. Atualizado a cada ~4 segundos durante a corrida.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/intervals?session_key=9165&interval>0&interval<0.005"
```

#### Exemplo de Resposta
```json
[
  {
    "date": "2023-09-17T13:31:02.395000+00:00",
    "driver_number": 1,
    "gap_to_leader": 41.019,
    "interval": 0.003,
    "meeting_key": 1219,
    "session_key": 9165
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date` | `string` | Timestamp ISO 8601 da medição. |
| `driver_number` | `integer` | Número do piloto. |
| `gap_to_leader` | `number` / `string` / `null` | Diferença em segundos para o líder; `+1 LAP` se tomou volta; `null` para o próprio líder. |
| `interval` | `number` / `string` / `null` | Diferença em segundos para o carro à frente; `+1 LAP` se retardatário; `null` para o líder. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.6 `GET /v1/laps`
Informações completas volta a volta: tempos de volta, setores, mini-setores, velocidades intermediárias e passagens pelos boxes.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/laps?session_key=9161&driver_number=63&lap_number=8"
```

#### Exemplo de Resposta
```json
[
  {
    "date_start": "2023-09-16T13:59:07.606000+00:00",
    "driver_number": 63,
    "duration_sector_1": 26.966,
    "duration_sector_2": 38.657,
    "duration_sector_3": 26.12,
    "i1_speed": 307,
    "i2_speed": 277,
    "is_pit_out_lap": false,
    "lap_duration": 91.743,
    "lap_number": 8,
    "meeting_key": 1219,
    "segments_sector_1": [2049, 2049, 2049, 2051, 2049, 2051, 2049, 2049],
    "segments_sector_2": [2049, 2049, 2049, 2049, 2049, 2049, 2049, 2049],
    "segments_sector_3": [2048, 2048, 2048, 2048, 2048, 2064, 2064, 2064],
    "session_key": 9161,
    "st_speed": 298
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date_start` | `string` | Data e hora estimada do início da volta (ISO 8601). |
| `driver_number` | `integer` | Número do piloto. |
| `duration_sector_1` | `number` | Tempo do 1º setor em segundos. |
| `duration_sector_2` | `number` | Tempo do 2º setor em segundos. |
| `duration_sector_3` | `number` | Tempo do 3º setor em segundos. |
| `i1_speed` | `integer` | Velocidade (km/h) no 1º ponto intermediário. |
| `i2_speed` | `integer` | Velocidade (km/h) no 2º ponto intermediário. |
| `is_pit_out_lap` | `boolean` | `true` se for volta de saída dos boxes (out-lap). |
| `lap_duration` | `number` | Duração total da volta em segundos. |
| `lap_number` | `integer` | Número sequencial da volta na sessão (inicia em 1). |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `segments_sector_1` | `array[int]` | Lista de códigos de mini-setores do setor 1. |
| `segments_sector_2` | `array[int]` | Lista de códigos de mini-setores do setor 2. |
| `segments_sector_3` | `array[int]` | Lista de códigos de mini-setores do setor 3. |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `st_speed` | `integer` | Velocidade no radar de velocidade máxima (Speed Trap) em km/h. |

#### Tabela de Cores dos Mini-Setores (`segments`)
*Nota: Mini-setores não estão disponíveis durante corridas.*

| Código | Significado / Cor |
| :--- | :--- |
| `0` | Não disponível |
| `2048` | Amarelo (Setor lento ou abaixo da melhor marca pessoal) |
| `2049` | Verde (Melhor marca pessoal) |
| `2051` | Roxo (Melhor marca absoluta da sessão) |
| `2064` | Pit lane |
| `2050`, `2052`, `2068` | Outros estados/não documentados |

---

### 3.7 `GET /v1/location`
Coordenadas espaciais tridimensionais (X, Y, Z) dos carros no circuito, amostradas a ~3.7 Hz.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/location?session_key=9161&driver_number=81&date>2023-09-16T13:03:35.200&date<2023-09-16T13:03:35.800"
```

#### Exemplo de Resposta
```json
[
  {
    "date": "2023-09-16T13:03:35.292000+00:00",
    "driver_number": 81,
    "meeting_key": 1219,
    "session_key": 9161,
    "x": 567,
    "y": 3195,
    "z": 187
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date` | `string` | Data/hora ISO 8601 da leitura. |
| `driver_number` | `integer` | Número do piloto. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `x` | `integer` | Posição cartesiana no eixo X. |
| `y` | `integer` | Posição cartesiana no eixo Y. |
| `z` | `integer` | Posição cartesiana no eixo Z (elevação). |

---

### 3.8 `GET /v1/meetings`
Informações sobre finais de semana de corrida (Grandes Prêmios ou testes). Atualizado diariamente à meia-noite UTC.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/meetings?year=2024&country_name=Singapore"
```

#### Exemplo de Resposta
```json
[
  {
    "circuit_key": 61,
    "circuit_info_url": "https://api.multiviewer.app/api/v1/circuits/61/2024",
    "circuit_image": "https://media.formula1.com/.../Singapore%20carbon.png",
    "circuit_short_name": "Singapore",
    "circuit_type": "Temporary - Street",
    "country_code": "SGP",
    "country_flag": "https://media.formula1.com/.../singapore-flag.png",
    "country_key": 157,
    "country_name": "Singapore",
    "date_end": "2024-09-22T14:00:00+00:00",
    "date_start": "2024-09-20T09:30:00+00:00",
    "gmt_offset": "08:00:00",
    "is_cancelled": false,
    "location": "Marina Bay",
    "meeting_key": 1246,
    "meeting_name": "Singapore Grand Prix",
    "meeting_official_name": "FORMULA 1 SINGAPORE AIRLINES SINGAPORE GRAND PRIX 2024",
    "year": 2024
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `circuit_key` | `integer` | Identificador único do circuito. |
| `circuit_image` | `string` | Link para imagem do traçado do circuito. |
| `circuit_info_url` | `string` | Link com JSON contendo dados detalhados do circuito (MultiViewer). |
| `circuit_short_name` | `string` | Nome curto ou popular do circuito. |
| `circuit_type` | `string` | Tipo de circuito (`Permanent`, `Temporary - Street`, `Temporary - Road`). |
| `country_code` | `string` | Código ISO do país (3 letras). |
| `country_flag` | `string` | Imagem da bandeira do país. |
| `country_key` | `integer` | Identificador único do país. |
| `country_name` | `string` | Nome completo do país. |
| `date_end` | `string` | Data e hora de término do evento (ISO 8601). |
| `date_start` | `string` | Data e hora de início do evento (ISO 8601). |
| `gmt_offset` | `string` | Diferença de fuso horário local em relação ao GMT (`HH:MM:SS`). |
| `is_cancelled` | `boolean` | `true` se o evento tiver sido cancelado. |
| `location` | `string` | Cidade ou localização geográfica do circuito. |
| `meeting_key` | `integer` | Identificador do evento (aceita `latest`). |
| `meeting_name` | `string` | Nome comum do GP (ex: "Singapore Grand Prix"). |
| `meeting_official_name` | `string` | Nome oficial comercial do Grande Prêmio. |
| `year` | `integer` | Ano da temporada correspondente. |

---

### 3.9 `GET /v1/overtakes`
Registros de ultrapassagens durante corridas (troca de posições entre pilotos em pista ou decorrentes de pit stops/penalidades).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/overtakes?session_key=9636&overtaking_driver_number=63&overtaken_driver_number=4&position=1"
```

#### Exemplo de Resposta
```json
[
  {
    "date": "2024-11-03T15:50:07.565000+00:00",
    "meeting_key": 1249,
    "overtaken_driver_number": 4,
    "overtaking_driver_number": 63,
    "position": 1,
    "session_key": 9636
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date` | `string` | Momento exato da ultrapassagem (ISO 8601). |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `overtaken_driver_number` | `integer` | Número do piloto ultrapassado. |
| `overtaking_driver_number` | `integer` | Número do piloto que realizou a ultrapassagem. |
| `position` | `integer` | Posição assumida pelo piloto após a conclusão da ultrapassagem. |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.10 `GET /v1/pit`
Dados de passagem e paradas dos carros no pit lane.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/pit?session_key=9877&stop_duration<2.3"
```

#### Exemplo de Resposta
```json
[
  {
    "date": "2025-10-26T20:46:37.358000+00:00",
    "driver_number": 16,
    "lane_duration": 22.215,
    "lap_number": 31,
    "meeting_key": 1272,
    "pit_duration": 22.215,
    "session_key": 9877,
    "stop_duration": 2.2
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date` | `string` | Data e hora de entrada nos boxes (ISO 8601). |
| `driver_number` | `integer` | Número do piloto. |
| `lane_duration` | `number` | Tempo total gasto no pit lane (em segundos). |
| `lap_number` | `integer` | Número da volta em que ocorreu o pit stop. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `pit_duration` | `number` | *(Obsoleto)* Sinônimo de `lane_duration` (será removido ao fim de 2026). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `stop_duration` | `number` | Tempo parado para troca de pneus/ajustes (disponível a partir do GP dos EUA de 2024). |

---

### 3.11 `GET /v1/position`
Rastreamento cronológico de posições dos pilotos ao longo da sessão (largada e mudanças de posição).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/position?meeting_key=1217&driver_number=40&position<=3"
```

#### Exemplo de Resposta
```json
[
  {
    "date": "2023-08-26T09:30:47.199000+00:00",
    "driver_number": 40,
    "meeting_key": 1217,
    "position": 2,
    "session_key": 9144
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date` | `string` | Momento em que a posição foi registrada (ISO 8601). |
| `driver_number` | `integer` | Número do piloto. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `position` | `integer` | Posição do piloto (iniciando em 1). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.12 `GET /v1/race_control`
Mensagens emitidas pela Direção de Prova (status da sessão, incidentes sob investigação, bandeiras, safety car, penalidades).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/race_control?flag=BLACK AND WHITE&driver_number=1&date>=2023-01-01&date<2023-09-01"
```

#### Exemplo de Resposta
```json
[
  {
    "category": "Flag",
    "date": "2023-06-04T14:21:01+00:00",
    "driver_number": 1,
    "flag": "BLACK AND WHITE",
    "lap_number": 59,
    "meeting_key": 1211,
    "message": "BLACK AND WHITE FLAG FOR CAR 1 (VER) - TRACK LIMITS",
    "qualifying_phase": null,
    "scope": "Driver",
    "sector": null,
    "session_key": 9102
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `category` | `string` | Categoria do evento (`SessionStatus`, `CarEvent`, `Drs`, `Flag`, `SafetyCar`, etc.). |
| `date` | `string` | Timestamp do evento em ISO 8601. |
| `driver_number` | `integer` / `null` | Número do piloto envolvido (se aplicável). |
| `flag` | `string` / `null` | Tipo de bandeira (`GREEN`, `YELLOW`, `DOUBLE YELLOW`, `RED`, `CHEQUERED`, `BLACK AND WHITE`, etc.). |
| `lap_number` | `integer` / `null` | Volta da corrida em que ocorreu o evento. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `message` | `string` | Texto descritivo emitido pela FIA/Direção de prova. |
| `qualifying_phase` | `integer` / `null` | Fase da classificação (`1`, `2` ou `3`), se sessão de Qualificação. |
| `scope` | `string` | Escopo do aviso (`Track`, `Driver`, `Sector`, etc.). |
| `sector` | `integer` / `null` | Setor da pista afetado. |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.13 `GET /v1/sessions`
Informações sobre cada sessão específica de pista de um final de semana (treinos livres, qualificação, sprint shootout, sprint, corrida). Atualizado diariamente à meia-noite UTC.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/sessions?country_name=Belgium&session_name=Sprint%20Qualifying&year=2023"
```

#### Exemplo de Resposta
```json
[
  {
    "circuit_key": 7,
    "circuit_short_name": "Spa-Francorchamps",
    "country_code": "BEL",
    "country_key": 16,
    "country_name": "Belgium",
    "date_end": "2023-07-29T15:35:00+00:00",
    "date_start": "2023-07-29T15:05:00+00:00",
    "gmt_offset": "02:00:00",
    "is_cancelled": false,
    "location": "Spa-Francorchamps",
    "meeting_key": 1216,
    "session_key": 9140,
    "session_name": "Sprint Qualifying",
    "session_type": "Sprint Qualifying",
    "year": 2023
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `circuit_key` | `integer` | ID do circuito. |
| `circuit_short_name` | `string` | Nome popular do circuito. |
| `country_code` | `string` | Código do país. |
| `country_key` | `integer` | ID do país. |
| `country_name` | `string` | Nome do país. |
| `date_end` | `string` | Término previsto/efetivo da sessão (ISO 8601). |
| `date_start` | `string` | Início previsto/efetivo da sessão (ISO 8601). |
| `gmt_offset` | `string` | Diferença para o GMT local (`HH:MM:SS`). |
| `is_cancelled` | `boolean` | Indica se a sessão foi cancelada. |
| `location` | `string` | Localização do circuito. |
| `meeting_key` | `integer` | ID do evento correspondente (aceita `latest`). |
| `session_key` | `integer` | Identificador único da sessão (aceita `latest`). |
| `session_name` | `string` | Nome da sessão (`Practice 1`, `Qualifying`, `Race`, etc.). |
| `session_type` | `string` | Tipo da sessão (`Practice`, `Qualifying`, `Sprint`, `Race`). |
| `year` | `integer` | Ano da temporada. |

---

### 3.14 `GET /v1/session_result`
Resultados e classificação oficial final após o término da sessão (disponibilizado minutos após a homologação no site oficial da F1).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/session_result?session_key=7782&position<=3"
```

#### Exemplo de Resposta
```json
[
  {
    "dnf": false,
    "dns": false,
    "dsq": false,
    "driver_number": 1,
    "duration": 77.565,
    "gap_to_leader": 0,
    "number_of_laps": 24,
    "meeting_key": 1143,
    "position": 1,
    "session_key": 7782
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `dnf` | `boolean` | `true` se o piloto abandonou (*Did Not Finish*). Válido para classificação e corrida. |
| `dns` | `boolean` | `true` se o piloto não largou (*Did Not Start*). |
| `dsq` | `boolean` | `true` se o piloto foi desqualificado. |
| `driver_number` | `integer` | Número do piloto. |
| `duration` | `number` / `array[number]` | Melhor volta (em treinos/qualificação) ou tempo total de corrida (em segundos). Na qualificação, é um array de 3 valores para Q1, Q2 e Q3. |
| `gap_to_leader` | `number` / `string` / `array` | Diferença em segundos para o líder ou `+N LAP(S)`. Na qualificação, é um array de 3 valores para Q1, Q2 e Q3. |
| `number_of_laps` | `integer` | Total de voltas completadas na sessão. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `position` | `integer` | Posição final na sessão. |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.15 `GET /v1/starting_grid`
Grid de largada oficial para a corrida ou sprint (disponível pouco após a divulgação dos resultados oficiais).

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/starting_grid?session_key=7783&position<=3"
```

#### Exemplo de Resposta
```json
[
  {
    "position": 1,
    "driver_number": 1,
    "lap_duration": 76.732,
    "meeting_key": 1143,
    "session_key": 7783
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `driver_number` | `integer` | Número do piloto. |
| `lap_duration` | `number` | Tempo em segundos da melhor volta da sessão classificatória. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `position` | `integer` | Posição de largada no grid. |
| `session_key` | `integer` | ID da sessão de corrida (aceita `latest`). |

---

### 3.16 `GET /v1/stints`
Informações sobre cada *stint* (período contínuo de pista com um mesmo jogo de pneus) percorrido pelo piloto durante a sessão.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/stints?session_key=9165&tyre_age_at_start>=3"
```

#### Exemplo de Resposta
```json
[
  {
    "compound": "SOFT",
    "driver_number": 16,
    "lap_end": 20,
    "lap_start": 1,
    "meeting_key": 1219,
    "session_key": 9165,
    "stint_number": 1,
    "tyre_age_at_start": 3
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `compound` | `string` | Composto de pneu utilizado (`SOFT`, `MEDIUM`, `HARD`, `INTERMEDIATE`, `WET`). |
| `driver_number` | `integer` | Número do piloto. |
| `lap_end` | `integer` | Última volta completada neste stint. |
| `lap_start` | `integer` | Primeira volta deste stint (inicia em 1). |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `stint_number` | `integer` | Número sequencial do stint na sessão (inicia em 1). |
| `tyre_age_at_start` | `integer` | Idade prévia do pneu no início do stint (quantidade de voltas já rodadas). |

---

### 3.17 `GET /v1/team_radio`
Gravações de áudio dos rádios trocados entre pilotos e engenheiros de equipe durante a sessão.

> **Aviso de Disponibilidade:** A FOM/F1 não libera áudios de rádio para todas as sessões. A cobertura foi severamente reduzida a partir da temporada de 2026, com a maioria das etapas não fornecendo nenhum áudio por limitações externas da própria F1.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/team_radio?session_key=9158&driver_number=11"
```

#### Exemplo de Resposta
```json
[
  {
    "date": "2023-09-15T09:40:43.005000+00:00",
    "driver_number": 11,
    "meeting_key": 1219,
    "recording_url": "https://livetiming.formula1.com/static/.../TeamRadio/SERPER01_11_20230915_104008.mp3",
    "session_key": 9158
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `date` | `string` | Momento da comunicação (ISO 8601). |
| `driver_number` | `integer` | Número do piloto. |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `recording_url` | `string` | URL direta para o arquivo de áudio (`.mp3`). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |

---

### 3.18 `GET /v1/weather`
Condições climáticas e meteorológicas monitoradas na pista a cada minuto.

#### Exemplo de Requisição
```bash
curl "https://api.openf1.org/v1/weather?meeting_key=1208&wind_direction>=130&track_temperature>=52"
```

#### Exemplo de Resposta
```json
[
  {
    "air_temperature": 27.8,
    "date": "2023-05-07T18:42:25.233000+00:00",
    "humidity": 58,
    "meeting_key": 1208,
    "pressure": 1018.7,
    "rainfall": 0,
    "session_key": 9078,
    "track_temperature": 52.5,
    "wind_direction": 136,
    "wind_speed": 2.4
  }
]
```

#### Atributos
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `air_temperature` | `number` | Temperatura do ar em graus Celsius (°C). |
| `date` | `string` | Timestamp da medição (ISO 8601). |
| `humidity` | `number` | Umidade relativa do ar (%). |
| `meeting_key` | `integer` | ID do evento (aceita `latest`). |
| `pressure` | `number` | Pressão atmosférica em milibares (mbar). |
| `rainfall` | `integer` | Indicação de chuva (`0` = sem chuva, `1` = chuva). |
| `session_key` | `integer` | ID da sessão (aceita `latest`). |
| `track_temperature` | `number` | Temperatura do asfalto em graus Celsius (°C). |
| `wind_direction` | `integer` | Direção do vento em graus (de 0° a 359°). |
| `wind_speed` | `number` | Velocidade do vento em metros por segundo (m/s). |

---

## 4. Guia de Integração em Python

### 4.1 Carregando dados diretamente com `requests` e `pandas`
```python
import requests
import pandas as pd

# Consultar pilotos da última sessão
url = "https://api.openf1.org/v1/drivers?session_key=latest"
response = requests.get(url)
response.raise_for_status()

df_drivers = pd.DataFrame(response.json())
print(df_drivers[["driver_number", "name_acronym", "team_name"]].head())
```

### 4.2 Carregando dados diretamente do endpoint CSV
```python
import pandas as pd

# Usando o parâmetro nativo de CSV da OpenF1
csv_url = "https://api.openf1.org/v1/meetings?year=2024&csv=true"
df_meetings = pd.read_csv(csv_url)
print(df_meetings[["meeting_name", "location", "date_start"]])
```
