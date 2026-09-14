import streamlit as st
import pandas as pd
import re
import time
from io import BytesIO
import plotly.graph_objects as go

PLAYBACK_MS = 1000

DATE_REGEX = re.compile(
    r"DATE:\s*(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})"
)

def safe_text(row, col):
    if col in row and pd.notna(row[col]):
        txt = str(row[col]).strip()
        return txt if txt else "—"
    return "—"

def led_color(v):
    if pd.isna(v):
        return "grey"
    s = str(v).strip().upper()
    if s in ("1", "ON", "TRUE", "YES"):
        return "green"
    return "white"

@st.cache_data
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

    def extract_ts(v):
        if not isinstance(v, str):
            return pd.NaT
        m = DATE_REGEX.search(v)
        return (
            pd.to_datetime(
                m.group(1),
                format="%Y/%m/%d %H:%M:%S",
                errors="coerce",
            )
            if m else pd.NaT
        )

    df["Timestamp"] = df[time_col].apply(extract_ts)
    return df.dropna(subset=["Timestamp"]).reset_index(drop=True)

def hvac_cabina_page():
    st.title("❄️ HVAC CABINA")
    st.caption("Analisi e riproduzione dei dati HVAC della cabina")

    COL_EVENT_DESC = "Event Description"
    COL_EVENT_ID = "Event Id"
    COL_EVENT_STATE = "Event State"

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

    # =================================================
    # STILE HVAC
    # =================================================

    st.markdown("""
    <style>
    .hvac-digital-card {
        border: 1px solid #d9dee7;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        background: #ffffff;
        min-height: 76px;
    }

    .hvac-digital-card.on {
        border-left: 6px solid #16a34a;
        background: #f0fdf4;
    }

    .hvac-digital-card.off {
        border-left: 6px solid #94a3b8;
        background: #f8fafc;
    }

    .hvac-digital-card.unknown {
        border-left: 6px solid #f59e0b;
        background: #fffbeb;
    }

    .hvac-digital-name {
        font-size: 15px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 7px;
    }

    .hvac-status-on,
    .hvac-status-off,
    .hvac-status-unknown {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
    }

    .hvac-status-on {
        color: #166534;
        background: #dcfce7;
    }

    .hvac-status-off {
        color: #475569;
        background: #e2e8f0;
    }

    .hvac-status-unknown {
        color: #92400e;
        background: #fef3c7;
    }

    .hvac-event {
        border-radius: 10px;
        padding: 12px 15px;
        border: 1px solid #fde68a;
        background: #fffbeb;
    }

    .hvac-event-title {
        font-size: 15px;
        font-weight: 700;
        color: #92400e;
    }

    .hvac-event-info {
        margin-top: 5px;
        font-size: 12px;
        color: #64748b;
    }
    </style>
    """, unsafe_allow_html=True)

    # =================================================
    # CARICAMENTO FILE
    # =================================================

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
    except Exception as e:
        st.error(f"❌ Errore durante la lettura del file: {e}")
        return

    missing = [c for c in CABINA_ANALOG.values() if c not in df.columns]
    if missing:
        st.error(
            "❌ Colonne analogiche mancanti:\n\n"
            + "\n".join(f"- {x}" for x in missing)
        )
        return

    # =================================================
    # STATO PLAYER
    # =================================================

    state_key = "hvac_cabina_index"
    running_key = "hvac_cabina_running"

    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    if running_key not in st.session_state:
        st.session_state[running_key] = False

    max_index = max(0, len(df) - 1)

    st.session_state[state_key] = min(
        max(0, st.session_state[state_key]),
        max_index,
    )

    # =================================================
    # COMANDI
    # =================================================

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("⏮️ Inizio", use_container_width=True, key="hvac_cabina_start"):
            st.session_state[state_key] = 0
            st.session_state[running_key] = False
            st.rerun()

    with c2:
        if st.button("◀️ Indietro", use_container_width=True, key="hvac_cabina_prev"):
            st.session_state[state_key] = max(
                0,
                st.session_state[state_key] - 1,
            )
            st.rerun()

    with c3:
        label = "⏸️ Pausa" if st.session_state[running_key] else "▶️ Play"
        if st.button(label, use_container_width=True, key="hvac_cabina_play"):
            st.session_state[running_key] = not st.session_state[running_key]
            st.rerun()

    with c4:
        if st.button("▶️ Avanti", use_container_width=True, key="hvac_cabina_next"):
            st.session_state[state_key] = min(
                max_index,
                st.session_state[state_key] + 1,
            )
            st.rerun()

    with c5:
        if st.button("⏭️ Fine", use_container_width=True, key="hvac_cabina_end"):
            st.session_state[state_key] = max_index
            st.session_state[running_key] = False
            st.rerun()

    # =================================================
    # TIMELINE EVENTO
    # =================================================

    index = st.slider(
        "📍 Posizione nella registrazione",
        min_value=0,
        max_value=max_index,
        value=st.session_state[state_key],
        key="hvac_cabina_slider",
    )

    if index != st.session_state[state_key]:
        st.session_state[state_key] = index
        st.rerun()

    index = st.session_state[state_key]
    r = df.iloc[index]

    st.markdown(
        f"""
        <div style="
            background:#eef5ff;
            border:1px solid #d6e5ff;
            border-radius:10px;
            padding:10px 14px;
            margin-top:5px;
            margin-bottom:16px;
            font-weight:700;
            color:#174ea6;
        ">
            🕐 {r["Timestamp"].strftime("%d/%m/%Y  %H:%M:%S")}
            &nbsp;&nbsp;•&nbsp;&nbsp;
            Campione {index + 1} / {len(df)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =================================================
    # EVENTO CABINA
    # =================================================

    st.subheader("🚨 Evento Cabina")

    desc = safe_text(r, COL_EVENT_DESC)
    eid = safe_text(r, COL_EVENT_ID)
    est = safe_text(r, COL_EVENT_STATE)

    if desc != "—":
        st.markdown(
            f"""
            <div class="hvac-event">
                <div class="hvac-event-title">⚠️ {desc}</div>
                <div class="hvac-event-info">
                    Event ID: {eid} &nbsp;•&nbsp; State: {est}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("✅ Nessun evento cabina")

    # =================================================
    # STATI DIGITALI
    # =================================================

    st.subheader("💡 Stati Digitali")

    digital_items = list(CABINA_DIGITAL.items())

    for row_start in range(0, len(digital_items), 4):
        cols = st.columns(4)

        for col_ui, (name, col) in zip(
            cols,
            digital_items[row_start:row_start + 4],
        ):
            raw_value = r[col] if col in r else None
            value = safe_text(r, col)

            if pd.isna(raw_value):
                css = "unknown"
                badge = "hvac-status-unknown"
                status_text = "N/D"
                icon = "🟡"
            else:
                s = str(raw_value).strip().upper()

                if s in ("1", "ON", "TRUE", "YES"):
                    css = "on"
                    badge = "hvac-status-on"
                    status_text = "ON"
                    icon = "🟢"
                elif s in ("0", "OFF", "FALSE", "NO"):
                    css = "off"
                    badge = "hvac-status-off"
                    status_text = "OFF"
                    icon = "⚫"
                else:
                    css = "unknown"
                    badge = "hvac-status-unknown"
                    status_text = value
                    icon = "🟡"

            with col_ui:
                st.markdown(
                    f"""
                    <div class="hvac-digital-card {css}">
                        <div class="hvac-digital-name">
                            {icon} {name}
                        </div>
                        <span class="{badge}">
                            {status_text}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # =================================================
    # VALORI ANALOGICI
    # =================================================

    st.subheader("📊 Valori Analogici")

    analog_items = list(CABINA_ANALOG.items())

    for row_start in range(0, len(analog_items), 3):
        cols = st.columns(3)

        for col_ui, (name, col) in zip(
            cols,
            analog_items[row_start:row_start + 3],
        ):
            with col_ui:
                st.metric(name, safe_text(r, col))

    # =================================================
    # GRAFICO INTERATTIVO + BARRA TEMPORALE
    # =================================================

    st.subheader("📈 Temperatura Cabina / Set Point")
    st.caption("Clicca un punto del grafico oppure usa le frecce per scorrere campione per campione. I valori HVAC vengono aggiornati automaticamente.")

    chart_df = df[
        [
            "Timestamp",
            CABINA_ANALOG["Temperatura Cabina"],
            CABINA_ANALOG["Set Point"],
        ]
    ].copy()

    chart_df = chart_df.rename(
        columns={
            CABINA_ANALOG["Temperatura Cabina"]: "Temperatura Cabina",
            CABINA_ANALOG["Set Point"]: "Set Point",
        }
    )

    chart_df["Temperatura Cabina"] = pd.to_numeric(
        chart_df["Temperatura Cabina"], errors="coerce"
    )
    chart_df["Set Point"] = pd.to_numeric(
        chart_df["Set Point"], errors="coerce"
    )
    chart_df["Campione"] = chart_df.index

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df["Timestamp"],
            y=chart_df["Temperatura Cabina"],
            mode="lines",
            name="Temperatura Cabina",
            customdata=chart_df[["Campione"]],
            line={"width": 2},
            hovertemplate=(
                "<b>%{x|%d/%m/%Y %H:%M:%S}</b><br>"
                "Temperatura: %{y:.2f} °C<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["Timestamp"],
            y=chart_df["Set Point"],
            mode="lines",
            name="Set Point",
            customdata=chart_df[["Campione"]],
            line={"width": 2},
            hovertemplate=(
                "<b>%{x|%d/%m/%Y %H:%M:%S}</b><br>"
                "Set Point: %{y:.2f} °C<extra></extra>"
            ),
        )
    )

    current_time = r["Timestamp"]

    fig.add_vline(
        x=current_time,
        line_width=3,
        line_dash="dash",
    )

    # Mostra anche il punto corrente sul grafico
    current_temp = pd.to_numeric(r[CABINA_ANALOG["Temperatura Cabina"]], errors="coerce")
    current_set = pd.to_numeric(r[CABINA_ANALOG["Set Point"]], errors="coerce")

    if pd.notna(current_temp):
        fig.add_trace(
            go.Scatter(
                x=[current_time],
                y=[current_temp],
                mode="markers",
                name="Campione attuale",
                marker={"size": 10},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    if pd.notna(current_set):
        fig.add_trace(
            go.Scatter(
                x=[current_time],
                y=[current_set],
                mode="markers",
                marker={"size": 9},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=25, b=10),
        hovermode="x unified",
        clickmode="event+select",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(
            title="Tempo",
            rangeslider=dict(
                visible=True,
                thickness=0.10,
            ),
            type="date",
        ),
        yaxis=dict(
            title="Temperatura °C",
        ),
    )

    # Frecce per navigare rapidamente tra i campioni.
    nav1, nav2, nav3, nav4 = st.columns([1, 1, 6, 1])

    with nav1:
        if st.button("⏮", use_container_width=True, key="hvac_graph_start"):
            st.session_state[state_key] = 0
            st.session_state[running_key] = False
            st.rerun()

    with nav2:
        if st.button("⬅️", use_container_width=True, key="hvac_graph_left"):
            st.session_state[state_key] = max(0, index - 1)
            st.rerun()

    with nav3:
        st.markdown(
            f"<div style='text-align:center;font-weight:700;padding:8px;'>Campione {index + 1} / {len(df)}</div>",
            unsafe_allow_html=True,
        )

    with nav4:
        if st.button("➡️", use_container_width=True, key="hvac_graph_right"):
            st.session_state[state_key] = min(max_index, index + 1)
            st.rerun()

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key="hvac_cabina_plot",
        on_select="rerun",
        selection_mode="points",
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "responsive": True,
            "displayModeBar": True,
        },
    )

    # Se l'utente clicca una misura sul grafico, il campione diventa quello attivo.
    try:
        selected_points = event.selection.point_indices
        if selected_points:
            selected_index = int(selected_points[0])
            if 0 <= selected_index <= max_index and selected_index != st.session_state[state_key]:
                st.session_state[state_key] = selected_index
                st.rerun()
    except Exception:
        pass

    # Seconda riga di navigazione, più comoda anche su touchscreen.
    nav5, nav6, nav7 = st.columns([1, 6, 1])

    with nav5:
        if st.button("◀️ Indietro campione", use_container_width=True, key="hvac_graph_prev_bottom"):
            st.session_state[state_key] = max(0, index - 1)
            st.rerun()

    with nav6:
        st.markdown(
            f"<div style='text-align:center;color:#64748b;padding:7px;'>"
            f"🕐 {current_time.strftime('%d/%m/%Y %H:%M:%S')}"
            f"</div>",
            unsafe_allow_html=True,
        )

    with nav7:
        if st.button("Avanti campione ▶️", use_container_width=True, key="hvac_graph_next_bottom"):
            st.session_state[state_key] = min(max_index, index + 1)
            st.rerun()

    # =================================================
    # PLAYER AUTOMATICO
    # =================================================

    if st.session_state[running_key] and index < max_index:
        time.sleep(PLAYBACK_MS / 1000)
        st.session_state[state_key] = index + 1
        st.rerun()

    elif st.session_state[running_key] and index >= max_index:
        st.session_state[running_key] = False
