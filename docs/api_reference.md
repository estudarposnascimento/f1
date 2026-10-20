# Referência da API (OpenF1Client)

O cliente `OpenF1Client` é o ponto de entrada principal para consultar os 18 endpoints da OpenF1 API.

---

## Catálogo de Métodos do Cliente

| Endpoint | Método | Modelo de Retorno | Descrição |
| :--- | :--- | :--- | :--- |
| `/v1/car_data` | `get_car_data(...)` | `list[CarData]` | Telemetria veicular (rpm, velocidade, marcha, freio, acelerador). |
| `/v1/championship_drivers` | `get_championship_drivers(...)` | `list[ChampionshipDriver]` | Pontuação e classificação do Mundial de Pilotos. |
| `/v1/championship_teams` | `get_championship_teams(...)` | `list[ChampionshipTeam]` | Pontuação e classificação do Mundial de Construtores. |
| `/v1/drivers` | `get_drivers(...)` | `list[Driver]` | Pilotos participantes de uma sessão específica. |
| `/v1/intervals` | `get_intervals(...)` | `list[Interval]` | Diferença em segundos para o carro à frente e gap para o líder. |
| `/v1/laps` | `get_laps(...)` | `list[Lap]` | Tempos de volta, setores 1, 2, 3 e speed traps. |
| `/v1/location` | `get_location(...)` | `list[CarLocation]` | Coordenadas espaciais (X, Y, Z) na pista. |
| `/v1/meetings` | `get_meetings(...)` | `list[Meeting]` | Calendário e GPs da temporada. |
| `/v1/overtakes` | `get_overtakes(...)` | `list[Overtake]` | Manobras de ultrapassagem em pista. |
| `/v1/pit` | `get_pit(...)` | `list[PitStop]` | Tempos de passagem e paradas no pit lane. |
| `/v1/position` | `get_position(...)` | `list[Position]` | Histórico cronológico de posições. |
| `/v1/race_control` | `get_race_control(...)` | `list[RaceControlMessage]` | Mensagens e investigações da Direção de Prova. |
| `/v1/sessions` | `get_sessions(...)` | `list[Session]` | Sessões de treinos, qualificação, sprint e corrida. |
| `/v1/session_result` | `get_session_results(...)` | `list[SessionResult]` | Classificação e resultado final oficial da sessão. |
| `/v1/starting_grid` | `get_starting_grid(...)` | `list[StartingGrid]` | Ordem oficial de largada no grid. |
| `/v1/stints` | `get_stints(...)` | `list[Stint]` | Trechos com mesmo conjunto de pneus e voltas rodadas. |
| `/v1/team_radio` | `get_team_radio(...)` | `list[TeamRadio]` | URLs com áudios das conversas de rádio. |
| `/v1/weather` | `get_weather(...)` | `list[Weather]` | Temperatura da pista/ar, umidade, vento e chuva. |

---

## Sintaxe de Filtros e Operadores

Todos os métodos aceitam filtros nos argumentos nomeados:

- **Operador de Igualdade (`=`):** `driver_number=1`
- **Maior ou Igual (`>=`):** `speed__gte=300` ou `**{"speed>=": 300}`
- **Menor ou Igual (`<=`):** `position__lte=3` ou `**{"position<=": 3}`
- **Maior que (`>`):** `interval__gt=0.5`
- **Menor que (`<`):** `lap_duration__lt=90.0`
- **Valores Múltiplos:** `driver_number=[4, 81]`
- **Identificador `latest`:** `session_key="latest"` ou `meeting_key="latest"`
- **Exportação CSV:** `csv=True` para receber a resposta em texto tabular puro.

