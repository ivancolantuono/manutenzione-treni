import streamlit as st
import pandas as pd
import re
import time
from io import BytesIO

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
        st.error("❌ Colonne analogiche mancanti:\n\n" + "\n".join(f"- {x}" for x in missing))
        return

    state_key = "hvac_cabina_index"
    running_key = "hvac_cabina_running"

    if state_key not in st.session_state:
        st.session_state[state_key] = 0
    if running_key not in st.session_state:
        st.session_state[running_key] = False

    max_index = max(0, len(df) - 1)
    st.session_state[state_key] = min(st.session_state[state_key], max_index)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("⏮️ Inizio", use_container_width=True, key="hvac_cabina_start"):
            st.session_state[state_key] = 0
            st.session_state[running_key] = False
            st.rerun()

    with c2:
        if st.button("◀️ Indietro", use_container_width=True, key="hvac_cabina_prev"):
            st.session_state[state_key] = max(0, st.session_state[state_key] - 1)
            st.rerun()

    with c3:
        label = "⏸️ Pausa" if st.session_state[running_key] else "▶️ Play"
        if st.button(label, use_container_width=True, key="hvac_cabina_play"):
            st.session_state[running_key] = not st.session_state[running_key]
            st.rerun()

    with c4:
        if st.button("▶️ Avanti", use_container_width=True, key="hvac_cabina_next"):
            st.session_state[state_key] = min(max_index, st.session_state[state_key] + 1)
            st.rerun()

    with c5:
        if st.button("⏭️ Fine", use_container_width=True, key="hvac_cabina_end"):
            st.session_state[state_key] = max_index
            st.session_state[running_key] = False
            st.rerun()

    index = st.slider(
        "Timeline",
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

    st.info(f"🕐 **Time:** {r['Timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")

    st.subheader("🚨 Evento Cabina")
    desc = safe_text(r, COL_EVENT_DESC)
    eid = safe_text(r, COL_EVENT_ID)
    est = safe_text(r, COL_EVENT_STATE)

    if desc != "—":
        st.warning(desc)
        st.caption(f"Event ID: {eid}  |  State: {est}")
    else:
        st.success("Nessun evento cabina")

    st.subheader("💡 Stati Cabina")
    led_cols = st.columns(4)

    for i, (name, col) in enumerate(CABINA_DIGITAL.items()):
        val = r[col] if col in r else None
        stato = led_color(val)
        with led_cols[i % 4]:
            if stato == "green":
                st.success(f"🟢 **{name}**")
            elif stato == "grey":
                st.write(f"⚪ **{name}**")
            else:
                st.write(f"⚫ **{name}**")
            st.caption(f"Valore: {safe_text(r, col)}")

    st.subheader("📊 Valori Analogici Cabina")
    analog_cols = st.columns(3)

    for i, (name, col) in enumerate(CABINA_ANALOG.items()):
        with analog_cols[i % 3]:
            st.metric(name, safe_text(r, col))

    st.subheader("📈 Temperatura Cabina / Set Point")

    chart_df = df[
        ["Timestamp", CABINA_ANALOG["Temperatura Cabina"], CABINA_ANALOG["Set Point"]]
    ].copy()

    chart_df = chart_df.rename(columns={
        CABINA_ANALOG["Temperatura Cabina"]: "Temperatura Cabina",
        CABINA_ANALOG["Set Point"]: "Set Point",
    }).set_index("Timestamp")

    st.line_chart(chart_df, use_container_width=True)

    if st.session_state[running_key] and index < max_index:
        time.sleep(PLAYBACK_MS / 1000)
        st.session_state[state_key] = index + 1
        st.rerun()
    elif st.session_state[running_key] and index >= max_index:
        st.session_state[running_key] = False
