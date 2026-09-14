import streamlit as st
import pandas as pd
import re
import time
from io import BytesIO
import plotly.graph_objects as go

PLAYBACK_SECONDS = 1.0

DATE_REGEX = re.compile(
    r"DATE:\s*(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})"
)


def safe_text(row, col):
    if col in row.index and pd.notna(row[col]):
        value = str(row[col]).strip()
        return value if value else "—"
    return "—"


def digital_state(value):
    if pd.isna(value):
        return "N/D", "unknown", "🟡"

    s = str(value).strip().upper()

    if s in ("1", "ON", "TRUE", "YES"):
        return "ON", "on", "🟢"
    if s in ("0", "OFF", "FALSE", "NO"):
        return "OFF", "off", "⚫"

    return str(value), "unknown", "🟡"


@st.cache_data(show_spinner=False)
def load_cabina(file_bytes):
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
    for c in df.columns:
        if df[c].astype(str).str.contains("DATE:", regex=False).any():
            time_col = c
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
    st.caption("Analisi e riproduzione dei dati HVAC della cabina")

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

    st.markdown(
        """
        <style>
        .hvac-digital-card {
            border: 1px solid #d8dee8;
            border-radius: 10px;
            padding: 11px 13px;
            margin-bottom: 10px;
            min-height: 74px;
            background: #ffffff;
        }
        .hvac-digital-card.on {
            border: 2px solid #22c55e;
            background: #f0fdf4;
        }
        .hvac-digital-card.off {
            border: 1px solid #cbd5e1;
            background: #f8fafc;
        }
        .hvac-digital-card.unknown {
            border: 2px solid #f59e0b;
            background: #fffbeb;
        }
        .hvac-digital-name {
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 8px;
            color: #172033;
        }
        .hvac-badge {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 800;
        }
        .hvac-badge.on { background: #dcfce7; color: #166534; }
        .hvac-badge.off { background: #e2e8f0; color: #475569; }
        .hvac-badge.unknown { background: #fef3c7; color: #92400e; }

        .hvac-current {
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 12px 16px;
            background: #f8fafc;
            text-align: center;
        }
        .hvac-current-label {
            color: #64748b;
            font-size: 12px;
            font-weight: 700;
        }
        .hvac-current-value {
            color: #111827;
            font-size: 18px;
            font-weight: 800;
            margin-top: 3px;
        }
        .hvac-timebar {
            border-radius: 9px;
            padding: 9px 13px;
            background: #eef5ff;
            border: 1px solid #d6e5ff;
            color: #174ea6;
            font-weight: 700;
            text-align: center;
        }
        .hvac-section-title {
            margin-top: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "📥 Carica file HVAC CABINA",
        type=["xlsx", "xls"],
        key="hvac_cabina_file",
    )

    if uploaded_file is None:
        st.info("Carica il file Excel HVAC della cabina per iniziare l'analisi.")
        return

    try:
        df = load_cabina(uploaded_file.getvalue())
    except Exception as exc:
        st.error(f"❌ Errore durante la lettura del file: {exc}")
        return

    if df.empty:
        st.warning("Il file non contiene campioni HVAC validi.")
        return

    missing = [c for c in CABINA_ANALOG.values() if c not in df.columns]
    if missing:
        st.error("❌ Colonne analogiche mancanti:\n\n" + "\n".join(f"- {x}" for x in missing))
        return

    max_index = len(df) - 1
    state_key = "hvac_cabina_index"
    running_key = "hvac_cabina_running"

    if state_key not in st.session_state:
        st.session_state[state_key] = 0
    if running_key not in st.session_state:
        st.session_state[running_key] = False

    st.session_state[state_key] = max(0, min(st.session_state[state_key], max_index))
    index = st.session_state[state_key]

    # -------------------------------------------------
    # PLAYER PRINCIPALE
    # -------------------------------------------------
    st.markdown("### 🎮 Navigazione registrazione")

    p1, p2, p3, p4, p5 = st.columns([1.1, 1.1, 1.5, 1.1, 1.1])

    with p1:
        if st.button("⏮️ INIZIO", use_container_width=True, key="hvac_start"):
            st.session_state[state_key] = 0
            st.session_state[running_key] = False
            st.rerun()

    with p2:
        if st.button("◀️ PRECEDENTE", use_container_width=True, key="hvac_prev"):
            st.session_state[state_key] = max(0, index - 1)
            st.rerun()

    with p3:
        play_label = "⏸️ PAUSA" if st.session_state[running_key] else "▶️ PLAY"
        if st.button(play_label, use_container_width=True, key="hvac_play"):
            st.session_state[running_key] = not st.session_state[running_key]
            st.rerun()

    with p4:
        if st.button("AVANTI ▶️", use_container_width=True, key="hvac_next"):
            st.session_state[state_key] = min(max_index, index + 1)
            st.rerun()

    with p5:
        if st.button("FINE ⏭️", use_container_width=True, key="hvac_end"):
            st.session_state[state_key] = max_index
            st.session_state[running_key] = False
            st.rerun()

    # Il controllo principale è uno slider nativo Streamlit.
    # È volutamente separato dal grafico: è affidabile, intuitivo e
    # permette anche la navigazione con le frecce della tastiera.
    selected = st.slider(
        "📍 CAMPIONE / TIMELINE — usa anche ← e → quando il cursore è selezionato",
        min_value=0,
        max_value=max_index,
        value=index,
        step=1,
        key="hvac_timeline",
    )

    if selected != index:
        st.session_state[state_key] = selected
        st.session_state[running_key] = False
        st.rerun()

    index = st.session_state[state_key]
    r = df.iloc[index]
    current_time = r["Timestamp"]

    st.markdown(
        f'<div class="hvac-timebar">🕐 {current_time.strftime("%d/%m/%Y %H:%M:%S")} &nbsp; | &nbsp; Campione {index + 1} / {len(df)}</div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------
    # GRAFICO
    # -------------------------------------------------
    st.markdown("### 📈 Andamento Temperature")
    st.caption("🖱️ CLICCA DIRETTAMENTE SU UN PUNTO DEL GRAFICO per analizzare quel momento. Ora, evento, valori analogici e stati digitali si aggiornano automaticamente.")

    chart_df = pd.DataFrame(
        {
            "Timestamp": df["Timestamp"],
            "Temperatura": pd.to_numeric(df[CABINA_ANALOG["Temperatura Cabina"]], errors="coerce"),
            "Set Point": pd.to_numeric(df[CABINA_ANALOG["Set Point"]], errors="coerce"),
        }
    )

    fig = go.Figure()

    point_index = list(range(len(chart_df)))

    fig.add_trace(
        go.Scatter(
            x=chart_df["Timestamp"],
            y=chart_df["Temperatura"],
            mode="lines+markers",
            name="Temperatura Cabina",
            line=dict(width=2),
            marker=dict(size=5),
            customdata=point_index,
            hovertemplate="%{x|%d/%m/%Y %H:%M:%S}<br>Temperatura: %{y:.2f} °C<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["Timestamp"],
            y=chart_df["Set Point"],
            mode="lines+markers",
            name="Set Point",
            line=dict(width=2),
            marker=dict(size=5),
            customdata=point_index,
            hovertemplate="%{x|%d/%m/%Y %H:%M:%S}<br>Set Point: %{y:.2f} °C<extra></extra>",
        )
    )

    temp_now = pd.to_numeric(r[CABINA_ANALOG["Temperatura Cabina"]], errors="coerce")
    set_now = pd.to_numeric(r[CABINA_ANALOG["Set Point"]], errors="coerce")

    # Linea verticale + marker: il grafico mostra sempre il campione attivo.
    fig.add_vline(x=current_time, line_width=2, line_dash="dash")

    if pd.notna(temp_now):
        fig.add_trace(
            go.Scatter(
                x=[current_time], y=[temp_now], mode="markers",
                marker=dict(size=12), name="Campione attuale",
                hovertemplate="Campione attuale<br>%{y:.2f} °C<extra></extra>",
                showlegend=False,
            )
        )

    if pd.notna(set_now):
        fig.add_trace(
            go.Scatter(
                x=[current_time], y=[set_now], mode="markers",
                marker=dict(size=10),
                hoverinfo="skip", showlegend=False,
            )
        )

    fig.update_layout(
        height=460,
        margin=dict(l=10, r=10, t=20, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="Tempo", type="date", rangeslider=dict(visible=True, thickness=0.08)),
        yaxis=dict(title="Temperatura °C"),
    )

    chart_event = st.plotly_chart(
        fig,
        use_container_width=True,
        key="hvac_temperature_chart",
        on_select="rerun",
        selection_mode="points",
        config={
            "displaylogo": False,
            "responsive": True,
            "displayModeBar": True,
            "scrollZoom": False,
        },
    )

    # Click su un punto = selezione del campione.
    # customdata contiene l'indice esatto del DataFrame.
    try:
        selected_points = chart_event.selection.points
    except Exception:
        selected_points = []

    if selected_points:
        selected_point = selected_points[0]
        clicked_index = selected_point.get("customdata", selected_point.get("point_index"))
        try:
            clicked_index = int(clicked_index)
        except (TypeError, ValueError):
            clicked_index = None

        if clicked_index is not None and 0 <= clicked_index <= max_index and clicked_index != index:
            st.session_state[state_key] = clicked_index
            st.session_state[running_key] = False
            st.rerun()

    # -------------------------------------------------
    # FRECCE GRANDI SOTTO IL GRAFICO
    # -------------------------------------------------
    g1, g2, g3, g4, g5 = st.columns([1.5, 2, 3, 2, 1.5])

    with g1:
        if st.button("⏮️", use_container_width=True, key="hvac_graph_first"):
            st.session_state[state_key] = 0
            st.rerun()
    with g2:
        if st.button("◀️  CAMPIONE PRECEDENTE", use_container_width=True, key="hvac_graph_prev"):
            st.session_state[state_key] = max(0, index - 1)
            st.rerun()
    with g3:
        st.markdown(
            f'<div style="text-align:center;padding:8px;font-weight:800;">CAMPIONE {index + 1} / {len(df)}</div>',
            unsafe_allow_html=True,
        )
    with g4:
        if st.button("CAMPIONE SUCCESSIVO  ▶️", use_container_width=True, key="hvac_graph_next"):
            st.session_state[state_key] = min(max_index, index + 1)
            st.rerun()
    with g5:
        if st.button("⏭️", use_container_width=True, key="hvac_graph_last"):
            st.session_state[state_key] = max_index
            st.rerun()

    # -------------------------------------------------
    # EVENTO
    # -------------------------------------------------
    st.markdown("### 🚨 Evento Cabina")

    desc = safe_text(r, "Event Description")
    eid = safe_text(r, "Event Id")
    est = safe_text(r, "Event State")

    if desc != "—":
        st.warning(f"⚠️ {desc}   |   Event ID: {eid}   |   State: {est}")
    else:
        st.success("✅ Nessun evento cabina")

    # -------------------------------------------------
    # DIGITALI
    # -------------------------------------------------
    st.markdown("### 💡 Stati Digitali")

    digital_items = list(CABINA_DIGITAL.items())
    for row_start in range(0, len(digital_items), 4):
        cols = st.columns(4)
        for col_ui, (name, col_name) in zip(cols, digital_items[row_start:row_start + 4]):
            raw = r[col_name] if col_name in df.columns else pd.NA
            status, css, icon = digital_state(raw)
            with col_ui:
                st.markdown(
                    f"""
                    <div class="hvac-digital-card {css}">
                        <div class="hvac-digital-name">{icon} {name}</div>
                        <span class="hvac-badge {css}">{status}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # -------------------------------------------------
    # ANALOGICI
    # -------------------------------------------------
    st.markdown("### 📊 Valori Analogici — campione selezionato")

    analog_items = list(CABINA_ANALOG.items())
    for row_start in range(0, len(analog_items), 3):
        cols = st.columns(3)
        for col_ui, (name, col_name) in zip(cols, analog_items[row_start:row_start + 3]):
            with col_ui:
                value = safe_text(r, col_name)
                st.markdown(
                    f"""
                    <div class="hvac-current">
                        <div class="hvac-current-label">{name}</div>
                        <div class="hvac-current-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # -------------------------------------------------
    # PLAY AUTOMATICO
    # -------------------------------------------------
    if st.session_state[running_key]:
        if index < max_index:
            time.sleep(PLAYBACK_SECONDS)
            st.session_state[state_key] = index + 1
            st.rerun()
        else:
            st.session_state[running_key] = False
            st.rerun()
