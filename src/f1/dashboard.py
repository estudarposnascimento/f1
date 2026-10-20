"""Dashboard analítico interativo da Fórmula 1 construído com Streamlit e OpenF1 SDK."""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from f1.clients.openf1 import OpenF1Client
from f1.exceptions import OpenF1Exception
from f1.utils.dataframe import to_dataframe

# -----------------------------------------------------------------------------
# Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OpenF1 - Analytics & Telemetry Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS com identidade visual da Fórmula 1
st.markdown(
    """
    <style>
    .f1-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #E10600;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
    }
    .f1-subtitle {
        color: #8D99AE;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1E1E24;
        border-left: 4px solid #E10600;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_client() -> OpenF1Client:
    """Inicializa e armazena em cache o cliente OpenF1."""
    return OpenF1Client()


client = get_client()


# -----------------------------------------------------------------------------
# Funções de Carregamento com Cache (TTL 10 min)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_meetings(year: int) -> list[dict[str, Any]]:
    """Carrega Grandes Prêmios do ano selecionado."""
    try:
        meetings = client.get_meetings(year=year)
        return [m.model_dump() for m in meetings]
    except OpenF1Exception:
        return []


@st.cache_data(ttl=600)
def load_sessions(meeting_key: int | str) -> list[dict[str, Any]]:
    """Carrega as sessões de um Grande Prêmio."""
    try:
        sessions = client.get_sessions(meeting_key=meeting_key)
        return [s.model_dump() for s in sessions]
    except OpenF1Exception:
        return []


@st.cache_data(ttl=600)
def load_drivers(session_key: int | str) -> list[dict[str, Any]]:
    """Carrega os pilotos de uma sessão."""
    try:
        drivers = client.get_drivers(session_key=session_key)
        return [d.model_dump() for d in drivers]
    except OpenF1Exception:
        return []


@st.cache_data(ttl=600)
def load_session_results(session_key: int | str) -> pd.DataFrame:
    """Carrega o resultado final da sessão."""
    try:
        results = client.get_session_results(session_key=session_key)
        return to_dataframe(results)
    except OpenF1Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_laps(session_key: int | str, driver_number: int) -> pd.DataFrame:
    """Carrega os tempos de volta de um piloto."""
    try:
        laps = client.get_laps(
            session_key=session_key, driver_number=driver_number
        )
        return to_dataframe(laps)
    except OpenF1Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_telemetry(
    session_key: int | str, driver_number: int, limit: int = 1500
) -> pd.DataFrame:
    """Carrega telemetria em alta frequência."""
    try:
        telemetry = client.get_car_data(
            session_key=session_key, driver_number=driver_number
        )
        df = to_dataframe(telemetry)
        if not df.empty and len(df) > limit:
            df = df.iloc[:limit]
        return df
    except OpenF1Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_weather(session_key: int | str) -> pd.DataFrame:
    """Carrega as condições meteorológicas da pista."""
    try:
        weather = client.get_weather(session_key=session_key)
        return to_dataframe(weather)
    except OpenF1Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_race_control(session_key: int | str) -> pd.DataFrame:
    """Carrega notificações da Direção de Prova."""
    try:
        rc = client.get_race_control(session_key=session_key)
        return to_dataframe(rc)
    except OpenF1Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_team_radio(session_key: int | str) -> pd.DataFrame:
    """Carrega os áudios de rádio disponíveis."""
    try:
        radios = client.get_team_radio(session_key=session_key)
        return to_dataframe(radios)
    except OpenF1Exception:
        return pd.DataFrame()


# -----------------------------------------------------------------------------
# Barra Lateral (Seletores de Navegação)
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🏎️ Navegação F1")

selected_year = st.sidebar.selectbox(
    "Temporada (Ano)",
    options=[2024, 2023],
    index=0,
)

meetings_data = load_meetings(selected_year)
if not meetings_data:
    st.sidebar.warning(
        "Nenhum evento retornado da API para o ano. Usando fallback para 2023."
    )
    meetings_data = load_meetings(2023)

meeting_options = {
    f"{m.get('meeting_name', 'GP')} - {m.get('location', '')}": m
    for m in meetings_data
}

if meeting_options:
    selected_meeting_label = st.sidebar.selectbox(
        "Grande Prêmio",
        options=list(meeting_options.keys()),
        index=0,
    )
    current_meeting = meeting_options[selected_meeting_label]
    current_meeting_key = current_meeting.get("meeting_key")
else:
    current_meeting = {}
    current_meeting_key = 1246

# Seleção da Sessão
sessions_data = load_sessions(current_meeting_key)
session_options = {
    f"{s.get('session_name', 'Sessão')} ({s.get('session_type', '')})": s
    for s in sessions_data
}

if session_options:
    # Prioriza 'Race' ou a última sessão da lista
    race_keys = [k for k in session_options if "Race" in k]
    default_session_idx = (
        list(session_options.keys()).index(race_keys[0])
        if race_keys
        else len(session_options) - 1
    )
    selected_session_label = st.sidebar.selectbox(
        "Sessão de Pista",
        options=list(session_options.keys()),
        index=default_session_idx,
    )
    current_session = session_options[selected_session_label]
    current_session_key = current_session.get("session_key")
else:
    current_session = {}
    current_session_key = 9158

# Pilotos da sessão
drivers_data = load_drivers(current_session_key)
drivers_map = {
    f"#{d.get('driver_number')} - {d.get('name_acronym', '')} ({d.get('last_name', '')})": d
    for d in drivers_data
}

st.sidebar.markdown("---")
st.sidebar.caption(
    f"**OpenF1 SDK v0.1.0**  \nAPI Base: `https://api.openf1.org/v1`  \nMeeting Key: `{current_meeting_key}` | Session: `{current_session_key}`"
)

# -----------------------------------------------------------------------------
# Cabeçalho Principal
# -----------------------------------------------------------------------------
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.markdown(
        f"<div class='f1-header'>{current_meeting.get('meeting_name', 'Fórmula 1')} {selected_year}</div>",
        unsafe_allow_html=True,
    )
    circ_name = current_meeting.get("circuit_short_name", "")
    country = current_meeting.get("country_name", "")
    sess_name = current_session.get("session_name", "Sessão")
    st.markdown(
        f"<div class='f1-subtitle'>📍 {circ_name}, {country} | 🏁 <b>{sess_name}</b></div>",
        unsafe_allow_html=True,
    )

with col_logo:
    flag_url = current_meeting.get("country_flag")
    if flag_url:
        st.image(flag_url, width=90)


# -----------------------------------------------------------------------------
# Abas de Conteúdo
# -----------------------------------------------------------------------------
tab_overview, tab_telemetry, tab_laps, tab_weather, tab_radio = st.tabs(
    [
        "🏆 Visão Geral & Grid",
        "⚡ Telemetria Comparativa",
        "⏱️ Tempos de Volta",
        "⛅ Meteorologia",
        "📻 Rádio & Direção de Prova",
    ]
)

# =============================================================================
# Aba 1: Visão Geral e Grid
# =============================================================================
with tab_overview:
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric(
            label="Circuito",
            value=current_meeting.get("circuit_short_name", "N/A"),
        )
    with col_info2:
        st.metric(
            label="Tipo de Pista",
            value=current_meeting.get("circuit_type", "Permanente"),
        )
    with col_info3:
        st.metric(
            label="Total de Pilotos",
            value=len(drivers_data) if drivers_data else "20",
        )
    with col_info4:
        st.metric(
            label="Fuso Local",
            value=f"GMT {current_meeting.get('gmt_offset', '00:00')}",
        )

    st.markdown("### 📊 Resultado da Sessão")
    df_results = load_session_results(current_session_key)

    if not df_results.empty and "position" in df_results.columns:
        # Merge com detalhes dos pilotos se disponível
        if drivers_data:
            df_drivers_lookup = pd.DataFrame(drivers_data)
            df_merged = df_results.merge(
                df_drivers_lookup[
                    [
                        "driver_number",
                        "full_name",
                        "name_acronym",
                        "team_name",
                        "team_colour",
                    ]
                ],
                on="driver_number",
                how="left",
            )
        else:
            df_merged = df_results

        display_cols = [
            c
            for c in [
                "position",
                "driver_number",
                "name_acronym",
                "full_name",
                "team_name",
                "number_of_laps",
                "duration",
                "gap_to_leader",
            ]
            if c in df_merged.columns
        ]
        df_display = df_merged[display_cols].sort_values(
            by="position", ascending=True
        )
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info(
            "Classificação oficial ainda não disponível ou homologada para esta sessão. Exibindo grid de participantes abaixo."
        )

    # Cards dos Pilotos
    st.markdown("### 🏎️ Pilotos Participantes")
    if drivers_data:
        driver_cols = st.columns(4)
        for idx, d in enumerate(drivers_data):
            col = driver_cols[idx % 4]
            with col:
                team_color = d.get("team_colour") or "E10600"
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid #{team_color}; background-color: #17181C; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <b style="font-size: 1.1rem; color: #FFF;">#{d.get('driver_number')} {d.get('name_acronym')}</b><br/>
                        <span style="color: #A0AAB2; font-size: 0.9rem;">{d.get('full_name')}</span><br/>
                        <span style="color: #{team_color}; font-weight: 600; font-size: 0.85rem;">{d.get('team_name')}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.write("Nenhum dado cadastral de piloto disponível para a sessão.")


# =============================================================================
# Aba 2: Telemetria Comparativa
# =============================================================================
with tab_telemetry:
    st.markdown("### ⚡ Telemetria de Alta Frequência (~3.7 Hz)")

    if drivers_map:
        col_sel1, col_sel2 = st.columns(2)
        driver_keys = list(drivers_map.keys())

        with col_sel1:
            sel_driver_1 = st.selectbox(
                "Piloto Principal",
                options=driver_keys,
                index=0,
                key="telemetry_driver_1",
            )
            d1_num = drivers_map[sel_driver_1]["driver_number"]
            d1_color = (
                "#" + (drivers_map[sel_driver_1].get("team_colour") or "E10600")
            )

        with col_sel2:
            sel_driver_2 = st.selectbox(
                "Piloto de Comparação (Opcional)",
                options=["Nenhum"] + driver_keys,
                index=1 if len(driver_keys) > 1 else 0,
                key="telemetry_driver_2",
            )
            d2_num = (
                drivers_map[sel_driver_2]["driver_number"]
                if sel_driver_2 != "Nenhum"
                else None
            )
            d2_color = (
                "#"
                + (
                    drivers_map[sel_driver_2].get("team_colour")
                    if sel_driver_2 != "Nenhum"
                    else "3671C6"
                )
                if sel_driver_2 != "Nenhum"
                else "#00D2BE"
            )

        with st.spinner("Carregando telemetria veicular..."):
            df_tel_1 = load_telemetry(current_session_key, d1_num)
            df_tel_2 = (
                load_telemetry(current_session_key, d2_num)
                if d2_num
                else pd.DataFrame()
            )

        if not df_tel_1.empty:
            # Gráfico de Velocidade
            fig_speed = go.Figure()
            fig_speed.add_trace(
                go.Scatter(
                    y=df_tel_1["speed"],
                    name=f"#{d1_num} Velocidade (km/h)",
                    line=dict(color=d1_color, width=2),
                )
            )
            if not df_tel_2.empty:
                fig_speed.add_trace(
                    go.Scatter(
                        y=df_tel_2["speed"],
                        name=f"#{d2_num} Velocidade (km/h)",
                        line=dict(color=d2_color, width=2, dash="dash"),
                    )
                )

            fig_speed.update_layout(
                title="Perfil de Velocidade Instantânea (km/h)",
                template="plotly_dark",
                height=350,
                xaxis_title="Amostra de Telemetria",
                yaxis_title="Velocidade (km/h)",
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig_speed, use_container_width=True)

            # Gráficos de Acelerador, Freio e RPM em 2 colunas
            col_graph1, col_graph2 = st.columns(2)

            with col_graph1:
                fig_throttle = go.Figure()
                fig_throttle.add_trace(
                    go.Scatter(
                        y=df_tel_1["throttle"],
                        name="Acelerador (%)",
                        line=dict(color="#00D2BE"),
                    )
                )
                if "brake" in df_tel_1.columns:
                    fig_throttle.add_trace(
                        go.Scatter(
                            y=df_tel_1["brake"],
                            name="Freio",
                            line=dict(color="#E10600"),
                        )
                    )
                fig_throttle.update_layout(
                    title=f"#{d1_num} - Acelerador (%) e Frenagem",
                    template="plotly_dark",
                    height=280,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig_throttle, use_container_width=True)

            with col_graph2:
                fig_rpm = go.Figure()
                fig_rpm.add_trace(
                    go.Scatter(
                        y=df_tel_1["rpm"],
                        name="RPM",
                        line=dict(color="#FFD166"),
                    )
                )
                fig_rpm.update_layout(
                    title=f"#{d1_num} - Rotação do Motor (RPM)",
                    template="plotly_dark",
                    height=280,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig_rpm, use_container_width=True)

        else:
            st.info(
                f"Sem dados de telemetria retornados para o piloto #{d1_num} nesta sessão."
            )
    else:
        st.warning("Selecione uma sessão com pilotos ativos para ver telemetria.")


# =============================================================================
# Aba 3: Tempos de Volta (Laps)
# =============================================================================
with tab_laps:
    st.markdown("### ⏱️ Análise de Cronometragem e Setores")

    if drivers_map:
        sel_lap_driver = st.selectbox(
            "Selecione o Piloto para Histórico de Voltas",
            options=list(drivers_map.keys()),
            key="lap_driver_select",
        )
        drv_num = drivers_map[sel_lap_driver]["driver_number"]

        df_laps = load_laps(current_session_key, drv_num)

        if not df_laps.empty and "lap_duration" in df_laps.columns:
            valid_laps = df_laps[df_laps["lap_duration"] > 0]

            if not valid_laps.empty:
                col_lap1, col_lap2, col_lap3 = st.columns(3)
                best_lap = valid_laps["lap_duration"].min()
                avg_lap = valid_laps["lap_duration"].mean()
                total_laps = len(valid_laps)

                with col_lap1:
                    st.metric(label="Melhor Volta", value=f"{best_lap:.3f} s")
                with col_lap2:
                    st.metric(label="Média de Volta", value=f"{avg_lap:.3f} s")
                with col_lap3:
                    st.metric(label="Total de Voltas", value=str(total_laps))

                # Gráfico de evolução de tempo de volta
                fig_laps = px.line(
                    valid_laps,
                    x="lap_number",
                    y="lap_duration",
                    markers=True,
                    title=f"Evolução dos Tempos de Volta - Piloto #{drv_num}",
                    labels={
                        "lap_number": "Número da Volta",
                        "lap_duration": "Tempo (s)",
                    },
                    template="plotly_dark",
                )
                fig_laps.add_hline(
                    y=best_lap,
                    line_dash="dash",
                    line_color="#E10600",
                    annotation_text="Melhor Marca",
                )
                fig_laps.update_layout(height=360)
                st.plotly_chart(fig_laps, use_container_width=True)

                # Setores 1, 2, 3
                sector_cols = [
                    c
                    for c in [
                        "duration_sector_1",
                        "duration_sector_2",
                        "duration_sector_3",
                    ]
                    if c in valid_laps.columns
                ]
                if sector_cols:
                    st.markdown("#### 🔍 Tempos por Setor")
                    fig_sectors = go.Figure()
                    for col_sec, sec_name, sec_color in zip(
                        sector_cols,
                        ["Setor 1", "Setor 2", "Setor 3"],
                        ["#06D6A0", "#118AB2", "#EF476F"],
                        strict=False,
                    ):
                        fig_sectors.add_trace(
                            go.Bar(
                                x=valid_laps["lap_number"],
                                y=valid_laps[col_sec],
                                name=sec_name,
                                marker_color=sec_color,
                            )
                        )
                    fig_sectors.update_layout(
                        barmode="stack",
                        title="Composição dos Setores por Volta (s)",
                        template="plotly_dark",
                        height=320,
                    )
                    st.plotly_chart(fig_sectors, use_container_width=True)
            else:
                st.info("Nenhuma volta cronometrada válida encontrada.")
        else:
            st.info(f"Sem registros de voltas para o piloto #{drv_num}.")
    else:
        st.warning("Lista de pilotos não disponível para esta sessão.")


# =============================================================================
# Aba 4: Meteorologia
# =============================================================================
with tab_weather:
    st.markdown("### ⛅ Monitor Climático da Pista Minuto a Minuto")
    df_weather = load_weather(current_session_key)

    if not df_weather.empty and "date" in df_weather.columns:
        last_weather = df_weather.iloc[-1]

        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            st.metric(
                "Temp. do Asfalto",
                f"{last_weather.get('track_temperature', 0):.1f} °C",
            )
        with col_w2:
            st.metric(
                "Temp. do Ar",
                f"{last_weather.get('air_temperature', 0):.1f} °C",
            )
        with col_w3:
            st.metric(
                "Umidade",
                f"{last_weather.get('humidity', 0):.0f}%",
            )
        with col_w4:
            st.metric(
                "Vento",
                f"{last_weather.get('wind_speed', 0):.1f} m/s",
            )

        # Gráfico temporal de Temperatura
        fig_temp = go.Figure()
        fig_temp.add_trace(
            go.Scatter(
                y=df_weather["track_temperature"],
                name="Temp. Pista (°C)",
                line=dict(color="#FF4B4B", width=2),
            )
        )
        fig_temp.add_trace(
            go.Scatter(
                y=df_weather["air_temperature"],
                name="Temp. Ar (°C)",
                line=dict(color="#00D2BE", width=2),
            )
        )
        fig_temp.update_layout(
            title="Evolução Térmica da Sessão (Pista vs Ar)",
            template="plotly_dark",
            height=320,
            yaxis_title="Temperatura (°C)",
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    else:
        st.info("Nenhum registro meteorológico disponível para a sessão.")


# =============================================================================
# Aba 5: Rádio & Direção de Prova
# =============================================================================
with tab_radio:
    col_rc, col_rad = st.columns([1, 1])

    with col_rc:
        st.markdown("### 🏁 Mensagens da Direção de Prova")
        df_rc = load_race_control(current_session_key)
        if not df_rc.empty and "message" in df_rc.columns:
            for _, row in df_rc.tail(15).iloc[::-1].iterrows():
                flag = row.get("flag") or "AVISO"
                cat = row.get("category") or "Geral"
                msg = row.get("message") or ""
                lap_num = row.get("lap_number")
                lap_str = f" • Volta {lap_num}" if pd.notna(lap_num) else ""
                st.markdown(
                    f"""
                    <div style="background-color: #17181C; border-left: 3px solid #FFD166; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px;">
                        <span style="font-size: 0.8rem; color: #8D99AE;">[{cat}] {flag}{lap_str}</span><br/>
                        <span style="font-size: 0.95rem; color: #FFF;">{msg}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhuma ocorrência registrada pela Direção de Prova.")

    with col_rad:
        st.markdown("### 📻 Rádios das Equipes")
        df_radios = load_team_radio(current_session_key)
        if not df_radios.empty and "recording_url" in df_radios.columns:
            for _, row in df_radios.tail(6).iterrows():
                driver_num = row.get("driver_number")
                audio_url = row.get("recording_url")
                st.write(f"🎙️ **Piloto #{driver_num}**")
                st.audio(audio_url)
        else:
            st.info(
                "Nenhum áudio de rádio disponibilizado para esta sessão pela FOM."
            )
