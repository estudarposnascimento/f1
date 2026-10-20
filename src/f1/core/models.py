"""Modelos Pydantic v2 para as entidades da OpenF1 API."""

from pydantic import BaseModel, ConfigDict, Field


class OpenF1BaseModel(BaseModel):
    """Modelo base com configuraÃ§Ãµes padrÃ£o de serializaÃ§Ã£o e tolerÃ¢ncia a novos campos."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )


class CarData(OpenF1BaseModel):
    """Telemetria veicular de alta frequÃªncia (~3.7 Hz)."""

    brake: int = Field(
        ..., description="Status do freio: 0 (nÃ£o pressionado) ou 100 (pressionado)"
    )
    date: str = Field(..., description="Timestamp ISO 8601 UTC")
    driver_number: int = Field(..., description="NÃºmero permanente do piloto")
    drs: int = Field(..., description="CÃ³digo de status do DRS")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    n_gear: int = Field(..., description="Marcha atual engatada (1-8, 0 para neutro)")
    rpm: int = Field(..., description="RotaÃ§Ãµes por minuto do motor")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    speed: int = Field(..., description="Velocidade em km/h")
    throttle: int = Field(..., description="Porcentagem do acelerador (0-100)")


class ChampionshipDriver(OpenF1BaseModel):
    """PontuaÃ§Ã£o e classificaÃ§Ã£o no Mundial de Pilotos."""

    driver_number: int = Field(..., description="NÃºmero do piloto")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    points_current: float = Field(..., description="PontuaÃ§Ã£o atual no campeonato")
    points_start: float = Field(..., description="PontuaÃ§Ã£o anterior Ã  prova")
    position_current: int = Field(..., description="PosiÃ§Ã£o atual no campeonato")
    position_start: int = Field(..., description="PosiÃ§Ã£o anterior Ã  prova")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class ChampionshipTeam(OpenF1BaseModel):
    """PontuaÃ§Ã£o e classificaÃ§Ã£o no Mundial de Construtores/Equipes."""

    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    points_current: float = Field(..., description="Pontos atuais da equipe")
    points_start: float = Field(..., description="Pontos anteriores Ã  prova")
    position_current: int = Field(..., description="PosiÃ§Ã£o atual da equipe")
    position_start: int = Field(..., description="PosiÃ§Ã£o anterior Ã  prova")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    team_name: str = Field(..., description="Nome da equipe/construtor")


class Driver(OpenF1BaseModel):
    """InformaÃ§Ãµes cadastrais e metadados dos pilotos em uma sessÃ£o."""

    broadcast_name: str | None = Field(
        default=None, description="Nome na transmissÃ£o de TV"
    )
    country_code: str | None = Field(
        default=None, description="CÃ³digo do paÃ­s (obsoleto)"
    )
    driver_number: int = Field(..., description="NÃºmero do piloto")
    first_name: str | None = Field(default=None, description="Primeiro nome")
    full_name: str = Field(..., description="Nome completo")
    headshot_url: str | None = Field(default=None, description="URL da foto oficial")
    last_name: str | None = Field(default=None, description="Sobrenome")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    name_acronym: str = Field(..., description="Sigla de 3 letras (ex: VER)")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    team_colour: str | None = Field(
        default=None, description="Cor hexadecimal da equipe (RRGGBB)"
    )
    team_name: str | None = Field(default=None, description="Nome da equipe")


class Interval(OpenF1BaseModel):
    """Intervalos de tempo entre pilotos e gap para o lÃ­der."""

    date: str = Field(..., description="Timestamp ISO 8601")
    driver_number: int = Field(..., description="NÃºmero do piloto")
    gap_to_leader: float | str | None = Field(
        default=None, description="DiferenÃ§a para o lÃ­der em segundos ou '+1 LAP'"
    )
    interval: float | str | None = Field(
        default=None, description="DiferenÃ§a para o carro Ã  frente em segundos"
    )
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class Lap(OpenF1BaseModel):
    """Tempos de volta e setores de desempenho."""

    date_start: str | None = Field(
        default=None, description="Data/hora de inÃ­cio da volta (ISO 8601)"
    )
    driver_number: int = Field(..., description="NÃºmero do piloto")
    duration_sector_1: float | None = Field(
        default=None, description="Tempo do setor 1 em segundos"
    )
    duration_sector_2: float | None = Field(
        default=None, description="Tempo do setor 2 em segundos"
    )
    duration_sector_3: float | None = Field(
        default=None, description="Tempo do setor 3 em segundos"
    )
    i1_speed: int | None = Field(
        default=None, description="Velocidade na primeira mediÃ§Ã£o (km/h)"
    )
    i2_speed: int | None = Field(
        default=None, description="Velocidade na segunda mediÃ§Ã£o (km/h)"
    )
    is_pit_out_lap: bool = Field(
        default=False, description="Indica se Ã© volta de saÃ­da do pit lane"
    )
    lap_duration: float | None = Field(
        default=None, description="DuraÃ§Ã£o total da volta em segundos"
    )
    lap_number: int = Field(..., description="NÃºmero da volta na sessÃ£o")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    segments_sector_1: list[int | None] | None = Field(
        default=None, description="CÃ³digos de status dos mini-setores 1"
    )
    segments_sector_2: list[int | None] | None = Field(
        default=None, description="CÃ³digos de status dos mini-setores 2"
    )
    segments_sector_3: list[int | None] | None = Field(
        default=None, description="CÃ³digos de status dos mini-setores 3"
    )
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    st_speed: int | None = Field(
        default=None, description="Velocidade no Speed Trap (km/h)"
    )


class CarLocation(OpenF1BaseModel):
    """Coordenadas tridimensionais (X, Y, Z) na pista amostradas a ~3.7 Hz."""

    date: str = Field(..., description="Timestamp ISO 8601")
    driver_number: int = Field(..., description="NÃºmero do piloto")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    x: int = Field(..., description="Coordenada X")
    y: int = Field(..., description="Coordenada Y")
    z: int = Field(..., description="Coordenada Z (elevaÃ§Ã£o)")


class Meeting(OpenF1BaseModel):
    """Grandes PrÃªmios e fins de semana de corrida."""

    circuit_key: int = Field(..., description="ID do circuito")
    circuit_image: str | None = Field(default=None, description="URL do mapa da pista")
    circuit_info_url: str | None = Field(
        default=None, description="URL de telemetria externa"
    )
    circuit_short_name: str = Field(..., description="Nome simplificado da pista")
    circuit_type: str | None = Field(default=None, description="Tipo do circuito")
    country_code: str | None = Field(
        default=None, description="CÃ³digo ISO do paÃ­s (3 letras)"
    )
    country_flag: str | None = Field(
        default=None, description="URL da imagem da bandeira"
    )
    country_key: int | None = Field(default=None, description="ID do paÃ­s")
    country_name: str = Field(..., description="Nome do paÃ­s")
    date_end: str | None = Field(
        default=None, description="Data/hora final da etapa (ISO 8601)"
    )
    date_start: str | None = Field(
        default=None, description="Data/hora inicial da etapa (ISO 8601)"
    )
    gmt_offset: str | None = Field(default=None, description="Fuso horÃ¡rio GMT local")
    is_cancelled: bool = Field(
        default=False, description="Indica se a etapa foi cancelada"
    )
    location: str | None = Field(default=None, description="Cidade/regiÃ£o")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    meeting_name: str = Field(..., description="Nome popular do evento")
    meeting_official_name: str | None = Field(
        default=None, description="Nome oficial do GP"
    )
    year: int = Field(..., description="Ano da temporada")


class Overtake(OpenF1BaseModel):
    """Registros de ultrapassagens e trocas de posiÃ§Ãµes."""

    date: str = Field(..., description="Timestamp ISO 8601 da manobra")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    overtaken_driver_number: int = Field(..., description="Piloto ultrapassado")
    overtaking_driver_number: int = Field(
        ..., description="Piloto que fez a ultrapassagem"
    )
    position: int = Field(..., description="PosiÃ§Ã£o assumida apÃ³s ultrapassagem")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class PitStop(OpenF1BaseModel):
    """Paradas no box e tempo no pit lane."""

    date: str = Field(..., description="Data/hora da entrada no pit")
    driver_number: int = Field(..., description="NÃºmero do piloto")
    lane_duration: float | None = Field(
        default=None, description="Tempo total no pit lane em segundos"
    )
    lap_number: int = Field(..., description="Volta em que ocorreu a parada")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    pit_duration: float | None = Field(
        default=None, description="SinÃ´nimo de lane_duration (obsoleto)"
    )
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    stop_duration: float | None = Field(
        default=None, description="Tempo parado para troca de pneus em segundos"
    )


class Position(OpenF1BaseModel):
    """Posicionamento cronolÃ³gico dos pilotos ao longo da prova."""

    date: str = Field(..., description="Timestamp ISO 8601")
    driver_number: int = Field(..., description="NÃºmero do piloto")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    position: int = Field(..., description="PosiÃ§Ã£o na prova")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class RaceControlMessage(OpenF1BaseModel):
    """Mensagens oficiais emitidas pela DireÃ§Ã£o de Prova da FIA."""

    category: str = Field(..., description="Categoria da notificaÃ§Ã£o")
    date: str = Field(..., description="Timestamp ISO 8601")
    driver_number: int | None = Field(
        default=None, description="Piloto envolvido, se aplicÃ¡vel"
    )
    flag: str | None = Field(default=None, description="Tipo de bandeira")
    lap_number: int | None = Field(
        default=None, description="Volta em que ocorreu o evento"
    )
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    message: str = Field(..., description="Texto emitido pela DireÃ§Ã£o de Prova")
    qualifying_phase: int | None = Field(
        default=None, description="Fase classificatÃ³ria (1, 2 ou 3)"
    )
    scope: str | None = Field(default=None, description="Escopo (Track, Driver, etc.)")
    sector: int | None = Field(default=None, description="Setor afetado")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class Session(OpenF1BaseModel):
    """SessÃµes oficiais na pista (Treinos, QualificaÃ§Ã£o, Sprint, Corrida)."""

    circuit_key: int = Field(..., description="ID do circuito")
    circuit_short_name: str | None = Field(
        default=None, description="Nome simplificado da pista"
    )
    country_code: str | None = Field(default=None, description="CÃ³digo ISO do paÃ­s")
    country_key: int | None = Field(default=None, description="ID do paÃ­s")
    country_name: str | None = Field(default=None, description="Nome do paÃ­s")
    date_end: str | None = Field(
        default=None, description="Data/hora de encerramento (ISO 8601)"
    )
    date_start: str | None = Field(
        default=None, description="Data/hora de inÃ­cio (ISO 8601)"
    )
    gmt_offset: str | None = Field(default=None, description="Fuso horÃ¡rio local")
    is_cancelled: bool = Field(
        default=False, description="Indica se a sessÃ£o foi cancelada"
    )
    location: str | None = Field(default=None, description="Cidade/localidade")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    session_name: str = Field(..., description="Nome da sessÃ£o (ex: Race, Practice 1)")
    session_type: str | None = Field(
        default=None, description="Tipo da sessÃ£o (Practice, Race, etc.)"
    )
    year: int = Field(..., description="Ano da temporada")


class SessionResult(OpenF1BaseModel):
    """Resultados finais e homologaÃ§Ã£o oficial da sessÃ£o."""

    dnf: bool = Field(default=False, description="Did Not Finish")
    dns: bool = Field(default=False, description="Did Not Start")
    dsq: bool = Field(default=False, description="Desqualificado")
    driver_number: int = Field(..., description="NÃºmero do piloto")
    duration: float | list[float | None] | None = Field(
        default=None, description="Tempo total ou melhor volta (ou lista Q1/Q2/Q3)"
    )
    gap_to_leader: float | str | list[float | str | None] | None = Field(
        default=None, description="DiferenÃ§a para o lÃ­der ou lista por fases"
    )
    number_of_laps: int | None = Field(
        default=None, description="Total de voltas percorridas"
    )
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    position: int | None = Field(default=None, description="PosiÃ§Ã£o final homologada")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class StartingGrid(OpenF1BaseModel):
    """Posicionamento de largada no grid."""

    driver_number: int = Field(..., description="NÃºmero do piloto")
    lap_duration: float | None = Field(
        default=None, description="Tempo classificatÃ³rio de referÃªncia"
    )
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    position: int = Field(..., description="PosiÃ§Ã£o de largada no grid")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class Stint(OpenF1BaseModel):
    """PerÃ­odo contÃ­nuo na pista utilizando o mesmo jogo de pneus."""

    compound: str | None = Field(
        default=None, description="Composto de pneu (SOFT, MEDIUM, HARD, etc.)"
    )
    driver_number: int = Field(..., description="NÃºmero do piloto")
    lap_end: int | None = Field(default=None, description="Ãšltima volta do stint")
    lap_start: int | None = Field(default=None, description="Primeira volta do stint")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    stint_number: int = Field(..., description="NÃºmero sequencial do stint")
    tyre_age_at_start: int | None = Field(
        default=None, description="Voltas jÃ¡ rodadas pelo composto antes do stint"
    )


class TeamRadio(OpenF1BaseModel):
    """ComunicaÃ§Ãµes de rÃ¡dio entre equipe e piloto."""

    date: str = Field(..., description="Timestamp ISO 8601 da gravaÃ§Ã£o")
    driver_number: int = Field(..., description="NÃºmero do piloto")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    recording_url: str = Field(
        ..., description="URL direta para o arquivo de Ã¡udio (.mp3)"
    )
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")


class Weather(OpenF1BaseModel):
    """CondiÃ§Ãµes meteorolÃ³gicas monitoradas na pista minuto a minuto."""

    air_temperature: float | None = Field(
        default=None, description="Temperatura do ar em Â°C"
    )
    date: str = Field(..., description="Timestamp ISO 8601 da leitura")
    humidity: float | None = Field(default=None, description="Umidade relativa do ar (%)")
    meeting_key: int | str = Field(..., description="ID do evento ou 'latest'")
    pressure: float | None = Field(
        default=None, description="PressÃ£o atmosfÃ©rica em mbar"
    )
    rainfall: int | None = Field(
        default=None, description="IndicaÃ§Ã£o de chuva (0=nÃ£o, 1=sim)"
    )
    session_key: int | str = Field(..., description="ID da sessÃ£o ou 'latest'")
    track_temperature: float | None = Field(
        default=None, description="Temperatura da pista em Â°C"
    )
    wind_direction: int | None = Field(
        default=None, description="DireÃ§Ã£o do vento em graus (0-359)"
    )
    wind_speed: float | None = Field(
        default=None, description="Velocidade do vento em m/s"
    )

