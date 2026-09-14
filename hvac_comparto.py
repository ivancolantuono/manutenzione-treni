from io import BytesIO
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events

DATE_REGEX = re.compile(
    r"DATE:\s*(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})"
)

HVAC1_ANALOG = {
    "Saloon Temp": "AN HVAC1 Saloon temperature",
    "Supply Temp": "AN HVAC1 Supply temperature",
    "HP": "AN HVAC1 HP",
    "LP": "AN HVAC1 LP",
    "Current": "AN HVAC1 Current sensor",
    "SetPoint": "HVAC1 Supply Set Point Temperature",
    "Mixed richiesta": "MPBUS HVAC1 mixed request",
    "Mixed feedback": "MPBUS HVAC1 mixed feedback",
    "Bypass richiesta": "MPBUS HVAC1 bypass request",
    "Bypass feedback": "MPBUS HVAC1 bypass feedback",
}

HVAC2_ANALOG = {
    "Saloon Temp": "AN HVAC2 Saloon temperature",
    "Supply Temp": "AN HVAC2 Supply temperature",
    "HP": "AN HVAC2 HP",
    "LP": "AN HVAC2 LP",
    "Current": "AN HVAC2 Current sensor",
    "SetPoint": "HVAC2 Supply Set Point Temperature",
}

HVAC1_DIGITAL = {
    "Compressor": "OUT HVAC1 Compressor",
    "Evaporator": "OUT HVAC1 Evaporator",
    "Condenser": "OUT HVAC1 Condenser",
    "Heater 1": "OUT HVAC1 Airheater 1",
    "Heater 2": "OUT HVAC1 Airheater 2",
    "Emergency": "TCMS IN HVAC1 CEmergSwitchOff",
    "Exhaust": "OUT HVAC1 Exhaust",
    "Pneumatic dampers": "OUT HVAC1 Pneumatic dampers",
    "Emergency inverter": "OUT HVAC1 Emergency inverter",
    "Liquid line valve": "OUT HVAC1 Liquid line valve",
    "Air flow detector 1": "IN HVAC1 Air flow detector 1",
    "Air flow detector 2": "IN HVAC1 Air flow detector 2",
    "Pneumatic fresh dumper 1": "IN HVAC1 Pneumatic fresh dumper 1",
    "Pneumatic fresh dumper 2": "IN HVAC1 Pneumatic fresh dumper 2",
    "Pneumatic Exhaust dumper": "IN HVAC1 Pneumatic Exhaust dumper",
    "HP switch": "IN HVAC1 HP switch",
}

HVAC2_DIGITAL = {
    "Compressor": "OUT HVAC2 Compressor",
    "Evaporator": "OUT HVAC2 Evaporator",
    "Condenser": "OUT HVAC2 Condenser",
    "Heater 1": "OUT HVAC2 Airheater 1",
    "Heater 2": "OUT HVAC2 Airheater 2",
    "Emergency": "TCMS IN HVAC2 CEmergSwitchOff",
    "Exhaust": "OUT HVAC2 Exhaust",
    "Pneumatic dampers": "OUT HVAC2 Pneumatic dampers",
    "Emergency inverter": "OUT HVAC2 Emergency inverter",
    "Liquid line valve": "OUT HVAC2 Liquid line valve",
    "Air flow detector 1": "IN HVAC2 Air flow detector 1",
    "Air flow detector 2": "IN HVAC2 Air flow detector 2",
    "Pneumatic fresh dumper 1": "IN HVAC2 Pneumatic fresh dumper 1",
    "Pneumatic fresh dumper 2": "IN HVAC2 Pneumatic fresh dumper 2",
    "Pneumatic Exhaust dumper": "IN HVAC2 Pneumatic Exhaust dumper",
    "HP switch": "IN HVAC2 HP switch",
}


def safe_text(row, col):
    if col and col in row.index and pd.notna(row[col]):
        value = str(row[col]).strip()
        return value if value else "—"
    return "—"


def digital_state(value):
    if pd.isna(value):
        return "N/D", "unknown"
    text = str(value).strip().upper()
    if text in {"1", "ON", "TRUE", "YES"}:
        return "ON", "on"
    if text in {"0", "OFF", "FALSE", "NO"}:
        return "OFF", "off"
    return str(value), "unknown"


def find_event_columns(df):
    result = {"description": None, "id": None, "state": None}
    normalized = {
        c: " ".join(str(c).strip().lower().replace("_", " ").replace("-", " ").split())
        for c in df.columns
    }
    for c, compact in normalized.items():
        if result["description"] is None and (
            "event description" in compact
            or compact in {"event", "event name", "event text"}
        ):
            result["description"] = c
        elif result["id"] is None and (
            "event id" in compact
            or compact in {"eventid", "event code", "event number"}
        ):
            result["id"] = c
        elif result["state"] is None and (
            "event state" in compact
            or compact in {"eventstate", "state"}
        ):
            result["state"] = c
    return result


def extract_event(row, event_cols):
    desc = safe_text(row, event_cols.get("description"))
    event_id = safe_text(row, event_cols.get("id"))
    state = safe_text(row, event_cols.get("state"))

    if desc != "—":
        match = re.search(r"event\s*id\s*[:=]\s*([A-Za-z0-9_-]+)", desc, re.I)
        if match:
            event_id = match.group(1)
        match = re.search(r"(?:event\s*)?state\s*[:=]\s*([A-Za-z0-9_-]+)", desc, re.I)
        if match:
            state = match.group(1)
    return desc, event_id, state


@st.cache_data(show_spinner=False)
def load_comparto(file_bytes: bytes) -> pd.DataFrame:
    raw = pd.read_excel(BytesIO(file_bytes), header=None)

    header_row = 0
    for i in range(min(50, len(raw))):
        row_text = " ".join(str(x) for x in raw.iloc[i] if pd.notna(x)).lower()
        if row_text.count("hvac") > 5:
            header_row = i
            break

    df = pd.read_excel(BytesIO(file_bytes), header=header_row)
    df.columns = (
        df.columns.astype(str)
        .str.replace("\xa0", " ", regex=False)
        .str.replace("\t", " ", regex=False)
        .str.replace(" +", " ", regex=True)
        .str.strip()
    )

    time_col = None
    for col in df.columns:
        if df[col].astype(str).str.contains("DATE:", regex=False).any():
            time_col = col
            break

    if time_col is None:
        raise ValueError("Colonna DATE non trovata nel file HVAC COMPARTO")

    def extract_timestamp(value):
        if not isinstance(value, str):
            return pd.NaT
        match = DATE_REGEX.search(value)
        if not match:
            return pd.NaT
        return pd.to_datetime(
            match.group(1),
            format="%Y/%m/%d %H:%M:%S",
            errors="coerce",
        )

    df["Timestamp"] = df[time_col].apply(extract_timestamp)
    df = df.dropna(subset=["Timestamp"]).reset_index(drop=True)
    return df


def _card_style():
    st.markdown(
        """
        <style>
        .stButton > button {
            background: #f5f7fa !important;
            color: #243447 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 7px !important;
            font-weight: 700 !important;
            min-height: 40px !important;
            box-shadow: none !important;
        }
        .stButton > button:hover {
            background: #e9eef3 !important;
            color: #111827 !important;
            border-color: #94a3b8 !important;
        }
        .selected-bar {
            border: 1px solid #d7e2ef;
            background: #f7fbff;
            border-radius: 8px;
            padding: 8px 12px;
            text-align: center;
            color: #23476b;
            font-size: 14px;
            font-weight: 700;
            margin: 4px 0 10px;
        }
        .hvac-panel-title {
            font-size: 18px;
            font-weight: 800;
            margin: 6px 0 8px;
        }
        .digital-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 8px;
        }
        .digital-card {
            border: 1px solid #d8e0e8;
            border-radius: 8px;
            padding: 8px 10px;
            background: #fff;
            min-height: 57px;
        }
        .digital-card.on { background:#f0fdf4; border-color:#86efac; }
        .digital-card.off { background:#f8fafc; border-color:#cbd5e1; }
        .digital-card.unknown { background:#fffbeb; border-color:#fcd34d; }
        .digital-name { font-size:12px; font-weight:700; color:#334155; }
        .digital-state { margin-top:4px; font-size:15px; font-weight:800; }
        .digital-state.on { color:#15803d; }
        .digital-state.off { color:#64748b; }
        .digital-state.unknown { color:#a16207; }
        .analog-grid {
            display:grid;
            grid-template-columns:repeat(3, minmax(0,1fr));
            gap:8px;
        }
        .analog-card {
            border:1px solid #d8e0e8;
            border-radius:8px;
            background:#fff;
            padding:8px 10px;
            min-height:62px;
            text-align:center;
        }
        .analog-label { color:#64748b; font-size:11px; font-weight:700; }
        .analog-value { color:#111827; font-size:18px; font-weight:800; margin-top:3px; }
        @media (max-width: 1050px) {
            .digital-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .analog-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
        }
        @media (max-width: 600px) {
            .digital-grid, .analog-grid { grid-template-columns:1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_analog(analog, row):
    html = ['<div class="analog-grid">']
    for name, col in analog.items():
        value = safe_text(row, col)
        html.append(
            f'<div class="analog-card"><div class="analog-label">{name}</div>'
            f'<div class="analog-value">{value}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_digital(digital, row):
    html = ['<div class="digital-grid">']
    for name, col in digital.items():
        value = row[col] if col in row.index else pd.NA
        status, css = digital_state(value)
        symbol = "●" if status == "ON" else "○"
        html.append(
            f'<div class="digital-card {css}"><div class="digital-name">{name}</div>'
            f'<div class="digital-state {css}">{symbol} {status}</div></div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def hvac_comparto_page():
    st.title("🚃 HVAC COMPARTO")
    st.caption("Clicca una volta sul punto del grafico che vuoi analizzare.")
    _card_style()

    uploaded = st.file_uploader(
        "📥 Carica file HVAC COMPARTO",
        type=["xlsx", "xls"],
        key="hvac_comparto_file",
    )
    if uploaded is None:
        st.info("Carica il file Excel HVAC del comparto per iniziare l'analisi.")
        return

    try:
        df = load_comparto(uploaded.getvalue())
    except Exception as exc:
        st.error(f"Errore durante la lettura del file: {exc}")
        return

    if df.empty:
        st.warning("Il file non contiene campioni HVAC validi.")
        return

    required = list(HVAC1_ANALOG.values()) + list(HVAC2_ANALOG.values())
    missing_analog = [c for c in required if c not in df.columns]
    if missing_analog:
        st.error("Colonne analogiche mancanti:\n\n" + "\n".join(f"- {c}" for c in missing_analog))
        return

    index_key = "hvac_comparto_index"
    file_key = "hvac_comparto_signature"
    signature = f"{uploaded.name}:{len(uploaded.getvalue())}"
    if st.session_state.get(file_key) != signature:
        st.session_state[file_key] = signature
        st.session_state[index_key] = 0

    max_index = len(df) - 1
    index = int(st.session_state.get(index_key, 0))
    index = max(0, min(index, max_index))
    st.session_state[index_key] = index

    event_cols = find_event_columns(df)

    # GRAFICO: nel codice originale del progetto i due segnali termici
    # corretti erano quelli di regolazione comuni del comparto.
    # I campi "AN HVACx ..." sono segnali analogici e non vanno usati
    # come temperatura ambiente del grafico: portano a scale non in °C.
    GRAPH_TEMP_COL = "Saloon temperature for regulation"
    GRAPH_SP_COL = "Set Point Temperature"

    missing_graph = [c for c in (GRAPH_TEMP_COL, GRAPH_SP_COL) if c not in df.columns]
    if missing_graph:
        st.error(
            "Nel file HVAC COMPARTO mancano le colonne corrette per il grafico:\n\n"
            + "\n".join(f"- {c}" for c in missing_graph)
        )
        return

    chart_df = pd.DataFrame({
        "Timestamp": df["Timestamp"],
        "Temperature": pd.to_numeric(df[GRAPH_TEMP_COL], errors="coerce"),
        "SetPoint": pd.to_numeric(df[GRAPH_SP_COL], errors="coerce"),
    })
    points = list(range(len(df)))
    current_time = df.iloc[index]["Timestamp"]

    fig = go.Figure()
    series = [
        ("Temperatura Salone", "Temperature", None, 2),
        ("Set Point", "SetPoint", "dot", 1.5),
    ]
    for name, ycol, dash, width in series:
        fig.add_trace(
            go.Scatter(
                x=chart_df["Timestamp"],
                y=chart_df[ycol],
                mode="lines+markers",
                name=name,
                customdata=points,
                line=dict(width=width, dash=dash) if dash else dict(width=width),
                marker=dict(size=5),
                connectgaps=False,
                hovertemplate=f"<b>%{{x|%d/%m/%Y %H:%M:%S}}</b><br>{name}: %{{y:.2f}} °C<extra></extra>",
            )
        )

    fig.add_vline(
        x=current_time,
        line_width=2,
        line_dash="dash",
        annotation_text=f"Campione {index + 1}",
        annotation_position="top left",
    )

    # Evidenzia il punto selezionato sulle due curve realmente presenti nel grafico.
    for ycol in ("Temperature", "SetPoint"):
        value = chart_df.iloc[index][ycol]
        if pd.notna(value):
            fig.add_trace(
                go.Scatter(
                    x=[current_time],
                    y=[value],
                    mode="markers",
                    marker=dict(size=13, symbol="circle-open", line=dict(width=3)),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    fig.update_layout(
        height=500,
        margin=dict(l=50, r=20, t=45, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
        xaxis=dict(
            title="Tempo",
            type="date",
            rangeslider=dict(visible=True, thickness=0.08),
            fixedrange=False,
        ),
        yaxis=dict(title="Temperatura (°C)"),
        dragmode="zoom",
    )

    click_data = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=500,
        override_width="100%",
        key=f"hvac_comparto_chart_{signature}",
    )

    if click_data:
        raw_index = click_data[0].get("pointIndex")
        try:
            selected_index = int(raw_index)
        except (TypeError, ValueError):
            selected_index = None

        if selected_index is not None and 0 <= selected_index <= max_index and selected_index != index:
            st.session_state[index_key] = selected_index
            st.rerun()

    current_time = df.iloc[index]["Timestamp"]
    st.markdown(
        f'<div class="selected-bar">🕐 {current_time.strftime("%d/%m/%Y %H:%M:%S")} &nbsp;·&nbsp; '
        f'Campione {index + 1} / {len(df)}</div>',
        unsafe_allow_html=True,
    )

    left, gap, right = st.columns([1, 0.35, 1])
    with left:
        if st.button("◀  INDIETRO", use_container_width=True, key="hvac_comparto_prev"):
            st.session_state[index_key] = max(0, index - 1)
            st.rerun()
    with gap:
        st.write("")
    with right:
        if st.button("AVANTI  ▶", use_container_width=True, key="hvac_comparto_next"):
            st.session_state[index_key] = min(max_index, index + 1)
            st.rerun()

    row = df.iloc[index]

    st.markdown("### 🚨 Evento Cabina/Comparto")
    event_id_series = (
        pd.to_numeric(df[event_cols["id"]], errors="coerce")
        if event_cols.get("id") and event_cols["id"] in df.columns
        else pd.Series(0, index=df.index, dtype="float64")
    )
    significant_mask = event_id_series.fillna(0).ne(0)
    prior_events = df.index[(df.index <= index) & significant_mask]

    if len(prior_events):
        event_index = int(prior_events[-1])
        event_row = df.iloc[event_index]
        desc, event_id, event_state = extract_event(event_row, event_cols)
        event_time = event_row["Timestamp"].strftime("%d/%m/%Y %H:%M:%S")
        event_text = desc if desc != "—" else "Evento rilevato"
        st.warning(f"{event_text}  ·  Event ID: {event_id}  ·  State: {event_state}  ·  Evento: {event_time}")
        if event_index != index:
            st.caption(f"Ultimo evento significativo: campione {event_index + 1}.")
    else:
        desc, event_id, event_state = extract_event(row, event_cols)
        if desc != "—" or event_id != "—" or event_state != "—":
            st.info(f"{desc if desc != '—' else 'Evento rilevato'}  ·  Event ID: {event_id}  ·  State: {event_state}")
        else:
            st.success("Nessun evento HVAC")

    # =========================================================
    # HVAC 1 e HVAC 2
    # =========================================================
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="hvac-panel-title">❄️ HVAC 1</div>', unsafe_allow_html=True)
        _render_analog(HVAC1_ANALOG, row)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _render_digital(HVAC1_DIGITAL, row)

    with col2:
        st.markdown('<div class="hvac-panel-title">❄️ HVAC 2</div>', unsafe_allow_html=True)
        _render_analog(HVAC2_ANALOG, row)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _render_digital(HVAC2_DIGITAL, row)
