
from io import BytesIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DATE_REGEX = re.compile(
    r"DATE:\s*(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})"
)

CABINA_ANALOG = {
    "Temperatura Cabina": "Cabin temperature",
    "Set Point": "Set Point Temperature",
    "Fresh Temp": "Fresh temperature",
    "Supply Temp": "AN Supply temperature",
    "Modalità": "Mode",
    "Current": "AN Current sensor",
    "HP": "AN HP",
    "LP": "AN LP",
    "Tem. Refrig.": "AN Refrigerant",
}

CABINA_DIGITAL = {
    "Compressore": "OUT Compressor",
    "Condensatore": "OUT Condenser",
    "Evaporatore": "OUT Evaporator",
    "Riscaldatore": "OUT Airheater",
    "Serranda pneumatica": "OUT Pneumatic damper",
    "Emergenza": "TCMS IN CEmergSwitchOff",
    "Flusso aria": "IN Air flow detector",
    "HP Switch": "IN HP switch",
}


def safe_text(row, col):
    if col in row.index and pd.notna(row[col]):
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
    """Individua le colonne evento anche con piccole differenze di nome."""
    result = {"description": None, "id": None, "state": None}
    cols = list(df.columns)

    normalized = {
        c: str(c).strip().lower().replace("_", " ").replace("-", " ")
        for c in cols
    }

    for c, n in normalized.items():
        compact = " ".join(n.split())
        if result["description"] is None and (
            "event description" in compact
            or compact in {"event", "event name", "event text"}
            or ("event" in compact and "description" in compact)
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
    """Legge l'evento del campione selezionato senza dipendere da nomi rigidi."""
    desc = safe_text(row, event_cols.get("description")) if event_cols.get("description") else "—"
    event_id = safe_text(row, event_cols.get("id")) if event_cols.get("id") else "—"
    state = safe_text(row, event_cols.get("state")) if event_cols.get("state") else "—"

    # Alcuni export HVAC riportano tutto in una singola stringa, per esempio:
    # "HVAC ... - Event ID: 12 - State: ON".
    combined = desc if desc != "—" else ""
    import re as _re
    m_id = _re.search(r"event\s*id\s*[:=]\s*([A-Za-z0-9_-]+)", combined, _re.I)
    m_state = _re.search(r"(?:event\s*)?state\s*[:=]\s*([A-Za-z0-9_-]+)", combined, _re.I)
    if m_id:
        event_id = m_id.group(1)
    if m_state:
        state = m_state.group(1)

    return desc, event_id, state


@st.cache_data(show_spinner=False)
def load_cabina(file_bytes: bytes) -> pd.DataFrame:
    raw = pd.read_excel(BytesIO(file_bytes), header=None)

    header_row = None
    for i in range(min(50, len(raw))):
        row_text = " ".join(str(x) for x in raw.iloc[i] if pd.notna(x))
        if "HVAC Cabin Configuration" in row_text:
            header_row = i
            break

    if header_row is None:
        raise ValueError("Intestazione CABINA non trovata nel file")

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
        raise ValueError("Colonna DATE non trovata nel file cabina")

    def extract_ts(value):
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

    df["Timestamp"] = df[time_col].apply(extract_ts)
    df = df.dropna(subset=["Timestamp"]).reset_index(drop=True)
    return df


def hvac_cabina_page():
    st.title("❄️ HVAC CABINA")
    st.caption("Clicca direttamente sul grafico nel punto che vuoi analizzare.")

    # Qui neutralizziamo il tema globale del progetto che rende i bottoni rossi.
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
        .stButton > button:focus {
            box-shadow: 0 0 0 2px rgba(100,116,139,.18) !important;
        }
        .hvac-selected-bar {
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
        .digital-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 9px;
        }
        .digital-card {
            border: 1px solid #d8e0e8;
            border-radius: 8px;
            padding: 9px 11px;
            background: #fff;
            min-height: 58px;
        }
        .digital-card.on {
            background: #f0fdf4;
            border-color: #86efac;
        }
        .digital-card.off {
            background: #f8fafc;
            border-color: #cbd5e1;
        }
        .digital-card.unknown {
            background: #fffbeb;
            border-color: #fcd34d;
        }
        .digital-name {
            font-size: 12px;
            font-weight: 700;
            color: #334155;
        }
        .digital-state {
            margin-top: 4px;
            font-size: 15px;
            font-weight: 800;
        }
        .digital-state.on { color: #15803d; }
        .digital-state.off { color: #64748b; }
        .digital-state.unknown { color: #a16207; }
        .analog-card {
            border: 1px solid #d8e0e8;
            border-radius: 8px;
            background: #fff;
            padding: 9px 10px;
            min-height: 64px;
            text-align: center;
        }
        .analog-label {
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
        }
        .analog-value {
            color: #111827;
            font-size: 19px;
            font-weight: 800;
            margin-top: 3px;
        }
        @media (max-width: 900px) {
            .digital-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 560px) {
            .digital-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "📥 Carica file HVAC CABINA",
        type=["xlsx", "xls"],
        key="hvac_cabina_click_file",
    )

    if uploaded is None:
        st.info("Carica il file Excel HVAC della cabina per iniziare l'analisi.")
        return

    try:
        df = load_cabina(uploaded.getvalue())
    except Exception as exc:
        st.error(f"Errore durante la lettura del file: {exc}")
        return

    if df.empty:
        st.warning("Il file non contiene campioni HVAC validi.")
        return

    missing = [col for col in CABINA_ANALOG.values() if col not in df.columns]
    if missing:
        st.error("Colonne analogiche mancanti:\n\n" + "\n".join(f"- {c}" for c in missing))
        return

    # Nuova session key, così non ereditiamo l'indice di una vecchia versione.
    index_key = "hvac_cabina_click_index"
    file_key = "hvac_cabina_click_file_signature"
    file_signature = f"{uploaded.name}:{len(uploaded.getvalue())}"

    if st.session_state.get(file_key) != file_signature:
        st.session_state[file_key] = file_signature
        st.session_state[index_key] = 0

    max_index = len(df) - 1
    index = int(st.session_state.get(index_key, 0))

    # Rilevazione robusta delle colonne evento del file reale.
    event_cols = find_event_columns(df)
    index = max(0, min(index, max_index))

    chart_df = pd.DataFrame(
        {
            "Timestamp": df["Timestamp"],
            "Temperatura": pd.to_numeric(df[CABINA_ANALOG["Temperatura Cabina"]], errors="coerce"),
            "SetPoint": pd.to_numeric(df[CABINA_ANALOG["Set Point"]], errors="coerce"),
        }
    )

    points_index = list(range(len(chart_df)))
    current_time = df.iloc[index]["Timestamp"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["Timestamp"],
            y=chart_df["Temperatura"],
            mode="lines+markers",
            name="Temperatura Cabina",
            line=dict(width=2),
            marker=dict(size=6),
            customdata=points_index,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y %H:%M:%S}</b>"
                "<br>Temperatura: %{y:.2f} °C"
                "<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["Timestamp"],
            y=chart_df["SetPoint"],
            mode="lines+markers",
            name="Set Point",
            line=dict(width=2, dash="dot"),
            marker=dict(size=5),
            customdata=points_index,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y %H:%M:%S}</b>"
                "<br>Set Point: %{y:.2f} °C"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=current_time,
        line_width=2,
        line_dash="dash",
        annotation_text=f"Campione {index + 1}",
        annotation_position="top left",
    )

    temp = chart_df.iloc[index]["Temperatura"]
    setpoint = chart_df.iloc[index]["SetPoint"]
    if pd.notna(temp):
        fig.add_trace(
            go.Scatter(
                x=[current_time],
                y=[temp],
                mode="markers",
                marker=dict(size=15, symbol="circle-open", line=dict(width=3)),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    if pd.notna(setpoint):
        fig.add_trace(
            go.Scatter(
                x=[current_time],
                y=[setpoint],
                mode="markers",
                marker=dict(size=13, symbol="circle-open", line=dict(width=3)),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        height=470,
        margin=dict(l=55, r=20, t=38, b=20),
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

    chart_event = st.plotly_chart(
        fig,
        use_container_width=True,
        key="hvac_cabina_click_chart",
        on_select="rerun",
        selection_mode=["points"],
        config={
            "displaylogo": False,
            "displayModeBar": False,
            "responsive": True,
            "scrollZoom": False,
        },
    )

    # Il click sul grafico aggiorna direttamente l'indice del campione.
    selected_index = None
    try:
        selected_points = chart_event.selection.points
    except Exception:
        selected_points = []

    for point in selected_points or []:
        raw_index = point.get("customdata", point.get("point_number"))
        if isinstance(raw_index, (list, tuple)) and raw_index:
            raw_index = raw_index[0]
        try:
            candidate = int(raw_index)
        except (TypeError, ValueError):
            candidate = None
        if candidate is not None and 0 <= candidate <= max_index:
            selected_index = candidate
            break

    if selected_index is not None:
        index = selected_index
        st.session_state[index_key] = index
        current_time = df.iloc[index]["Timestamp"]

    # Solo i due comandi richiesti.
    st.markdown(
        f'<div class="hvac-selected-bar">🕐 {current_time.strftime("%d/%m/%Y %H:%M:%S")} &nbsp;·&nbsp; Campione {index + 1} / {len(df)}</div>',
        unsafe_allow_html=True,
    )

    _, prev_col, next_col, _ = st.columns([1.8, 1, 1, 1.8])
    with prev_col:
        if st.button("◀  INDIETRO", use_container_width=True, key="hvac_cabina_click_prev"):
            st.session_state[index_key] = max(0, index - 1)
            st.rerun()
    with next_col:
        if st.button("AVANTI  ▶", use_container_width=True, key="hvac_cabina_click_next"):
            st.session_state[index_key] = min(max_index, index + 1)
            st.rerun()

    row = df.iloc[index]

    st.markdown("### 🚨 Evento Cabina")

    # Nel file reale molti campioni sono "HVAC CAB Periodic Recording"
    # con Event Id = 0. L'evento diagnostico vero è invece la riga
    # con Event Id diverso da 0. Quando l'utente si sposta sul grafico,
    # mostriamo quindi l'ultimo evento significativo raggiunto, compreso
    # l'eventuale evento del campione selezionato.
    event_id_series = pd.to_numeric(df[event_cols["id"]], errors="coerce") if event_cols.get("id") else pd.Series(pd.NA, index=df.index)
    significant_mask = event_id_series.fillna(0).ne(0)

    prior_events = df.index[(df.index <= index) & significant_mask]

    if len(prior_events) > 0:
        event_index = int(prior_events[-1])
        event_row = df.iloc[event_index]
        desc, event_id, event_state = extract_event(event_row, event_cols)
        event_time = event_row["Timestamp"].strftime("%d/%m/%Y %H:%M:%S")

        event_text = desc if desc != "—" else "Evento rilevato"
        st.warning(
            f"{event_text}  ·  Event ID: {event_id}  ·  State: {event_state}  ·  Evento: {event_time}"
        )

        # Se il campione selezionato non coincide con la riga evento,
        # lo rendiamo esplicito per non confondere l'evento con il campione.
        if event_index != index:
            st.caption(
                f"Ultimo evento significativo prima/durante il campione selezionato: campione {event_index + 1}."
            )
    else:
        # Prima del primo evento significativo mostriamo il contenuto
        # del campione selezionato, senza inventare un evento.
        desc, event_id, event_state = extract_event(row, event_cols)
        if desc != "—" or event_id != "—" or event_state != "—":
            event_text = desc if desc != "—" else "Evento rilevato"
            st.info(f"{event_text}  ·  Event ID: {event_id}  ·  State: {event_state}")
        else:
            st.success("Nessun evento cabina")

    st.markdown("### 💡 Stati Digitali")
    cards = []
    for name, col_name in CABINA_DIGITAL.items():
        raw_value = row[col_name] if col_name in df.columns else pd.NA
        status, css = digital_state(raw_value)
        symbol = "●" if status == "ON" else "○"
        cards.append(
            f'<div class="digital-card {css}">'
            f'<div class="digital-name">{name}</div>'
            f'<div class="digital-state {css}">{symbol} {status}</div>'
            f'</div>'
        )
    st.markdown('<div class="digital-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)

    st.markdown("### 📊 Valori Analogici — campione selezionato")
    analog_items = list(CABINA_ANALOG.items())
    for start in range(0, len(analog_items), 3):
        cols = st.columns(3)
        for ui_col, (name, col_name) in zip(cols, analog_items[start:start + 3]):
            value = safe_text(row, col_name)
            with ui_col:
                st.markdown(
                    f'<div class="analog-card">'
                    f'<div class="analog-label">{name}</div>'
                    f'<div class="analog-value">{value}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
