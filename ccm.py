# ============================================================
# CCM - ANALISI FILE .CAP
# Versione Streamlit
# ============================================================

import streamlit as st
import pandas as pd
import re
from io import BytesIO


# ============================================================
# CONFIGURAZIONE
# ============================================================

MAX_FIELDS = 6

ANALOG_SIGNALS = [
    "vTVL",
    "vTV1",
    "iTA1M",
    "iTA2M",
    "iTA",
    "vTVI",
]


# ============================================================
# WORD LIST
# ============================================================

WORD_LIST = [
    "sCCa",
    "PSWA",
    "PSWB",
    "flcom",
    "stdi",
    "PCUc",
    "msf",
    "PHW1",
    "PHW2",
    "PHW3",
    "PHW4",
    "stdo",
    "PCUs",
]


# ============================================================
# DECODIFICA BIT
# ============================================================

BIT_MAP = {

    "sCCa": {
        0: "Test",
        1: "c2qok",
        2: "chAok",
        3: "chBokw",
        4: "abPhw",
        5: "civc",
        6: "pwm2q",
        7: "my_dspok",
        8: "anticipoTT",
        9: "3KON",
        10: "SCAR2Q",
        11: "okThCHPIND1",
        12: "okThCHPIND2",
        13: "okThINTAIR",
        14: "okThHEATSINK",
        15: "parzCCon",
    },

    "PSWA": {
        0: "UNDERVOLTPRIM3K",
        1: "CHPIND1_HOT",
        2: "CHPIND2_HOT",
        3: "INTAIR_HOT",
        4: "HEATSINK_HOT",
        5: "koThCHPIND1",
        6: "koThCHPIND2",
        7: "koThINTAIR",
        8: "koThHEATSINK",
        9: "PcuKO",
        10: "pswCHPIND1_HOTMAX",
        11: "pswUNDERVOLTPRIM",
        12: "pswTV1SUPERV",
        13: "pswCHPIND2_HOTMAX",
        14: "pswUNDERVOLTSEC",
        15: "pswTVISUPERV",
    },

    "PSWB": {
        0: "pswINTAIR_HOTMAX",
        1: "pswUNBASUPERV",
        2: "pswTA1SUPERV",
        3: "pswTA2SUPERV",
        4: "UNDERVOLTLINE3K",
        5: "EARTHFAULT",
        6: "DISCHA_FAIL",
        7: "HEATSINK_HOTMAX",
        8: "COMPVTVIMCM1",
        9: "TASUPERV",
        10: "CCMESCL",
        11: "CHARGESUPERV",
        12: "OVPRESHOT",
        13: "TEMPSCHEDHOT",
        14: "UNDERVOLTLINE",
        15: "CIDko",
    },

    "PHW1": {
        0: "-----",
        1: "VLDC",
        2: "TVI",
        3: "-----",
        4: "-----",
        5: "-----",
        6: "-----",
        7: "TA1",
        8: "TA2",
        9: "TA",
        10: "TV1",
        11: "-----",
        12: "-----",
        13: "-----",
        14: "-----",
        15: "-----",
    },

    "flcom": {
        0: "euroDC",
        1: "euroAC",
        2: "Bianco",
        3: "linea3k",
        4: "kv1_5",
        5: "chfresc",
        6: "cllon",
        7: "mant",
        8: "scafil2Q",
        9: "scafilOVP",
        10: "PrtSd",
        11: "FstSd",
        12: "SftSd",
        13: "PrtBlk",
        14: "testCID",
        15: "trNeutro",
    },

    "PHW3": {
        0: "DiaUp1",
        1: "DiaUp2",
        2: "DiaUp3",
        3: "DiaUp4",
        4: "DiaUp5",
        5: "DiaDown1",
        6: "DiaDown2",
        7: "DiaDown3",
        8: "DiaDown4",
        9: "DiaDown5",
        10: "-----",
        11: "-----",
        12: "-----",
        13: "-----",
        14: "-----",
        15: "-----",
    },

    "stdi": {
        0: "copenfb",
        1: "cclosefb",
        2: "coveropen",
        3: "fastopenLCB",
        4: "-----",
        5: "earthfail",
        6: "-----",
        7: "device-address0",
        8: "device-address1",
        9: "device-address2",
        10: "-----",
        11: "-----",
        12: "-----",
        13: "-----",
        14: "-----",
        15: "-----",
    },

    "stdo": {
        0: "closeby",
        1: "cidactive",
        2: "cidclose",
        3: "earth",
        4: "-----",
        5: "-----",
        6: "-----",
        7: "-----",
        8: "-----",
        9: "-----",
        10: "-----",
        11: "-----",
        12: "-----",
        13: "-----",
        14: "-----",
        15: "-----",
    },

    "PCUc": {
        0: "Bianco",
        1: "AcLCBclosed",
        2: "DcLCBclosed",
        3: "Chfresc",
        4: "StartCCM",
        5: "StartLCM",
        6: "Mant",
        7: "FPA",
        8: "resetEsc",
        9: "TestCID",
        10: "TrNeutro",
        11: "scafil2Q",
        12: "scafilOVP",
        13: "-----",
        14: "-----",
        15: "-----",
    },

    "PCUs": {
        0: "Dc1_5kV_SEL",
        1: "Dc1_5kV_CONF",
        2: "Dc1_5kV_LINEoN",
        3: "Dc3kV_SEL",
        4: "Dc3kV_CONF",
        5: "Dc3kV_LINEoN",
        6: "Ac15kV_SEL",
        7: "Ac25kV_SEL",
        8: "setHIL",
        9: "Dc3kV_LcbClosed",
        10: "Dc1_5kV_LcbClosed",
        11: "-----",
        12: "-----",
        13: "-----",
        14: "-----",
        15: "-----",
    },

    "msf": {
        0: "NOCGF",
        1: "2QOFF",
        2: "2QBIA",
        3: "3KON",
        4: "SCAR2Q",
        5: "1,5K ON",
        6: "PROT",
        7: "PROTBLO",
        8: "FASTSHUT",
        9: "SOFTSHUT",
        10: "-----",
        11: "AUTORESET",
        12: "-----",
        13: "ESCL",
        14: "-----",
        15: "-----",
    },
}


# ============================================================
# PARSER
# ============================================================

SM_RE = re.compile(
    r"^Rec:\s+(\d+)\s+Code:\s+([0-9A-Fa-f]+)\s+"
    r"Date:(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{2}:\d{2}:\d{2}\.\d{2})\s+-\s+(.*)$"
)

LL_HEADER_RE = re.compile(r"^\s*N\.\s+")
LL_ROW_RE = re.compile(r"^\s*(-?\d+)\s+(.*)$")


# ============================================================
# SPLIT DESCRIPTION
# ============================================================

def split_description(desc):

    descrizione = ""

    if " - " in desc:
        left, descrizione = desc.split(" - ", 1)
    else:
        left = desc

    fields = [
        p.strip()
        for p in left.split(";")
        if p.strip()
    ]

    fields = fields[:MAX_FIELDS]

    while len(fields) < MAX_FIELDS:
        fields.append("")

    return fields, descrizione.strip()


# ============================================================
# PARSE FILE
# ============================================================

def parse_file(file_bytes):

    summary = []
    ll_blocks = {}

    current_rec = None
    in_ll = False
    columns = []

    text = file_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    for line in text.splitlines():

        m = SM_RE.match(line)

        if m:

            rec = int(m.group(1))
            code = m.group(2)
            date = m.group(3)
            time = m.group(4)
            desc = m.group(5)

            fields, descrizione = split_description(desc)

            summary.append(
                [rec, code, date, time]
                + fields
                + [descrizione]
            )

            ll_blocks[rec] = []

            current_rec = rec
            in_ll = False

            continue

        if LL_HEADER_RE.match(line):

            columns = line.split()
            in_ll = True

            continue

        if in_ll and current_rec is not None:

            m = LL_ROW_RE.match(line)

            if not m:
                continue

            values = m.group(2).split()

            if len(values) < len(columns) - 1:
                continue

            row = {
                "N": int(m.group(1))
            }

            for i, col in enumerate(columns[1:]):
                row[col] = values[i]

            ll_blocks[current_rec].append(row)

    return summary, ll_blocks


# ============================================================
# DECODIFICA WORD
# ============================================================

def decode_word(hex_value, bit_map):

    try:
        value = int(
            str(hex_value),
            16
        )
    except Exception:
        value = 0

    return {
        name: (value >> bit) & 1
        for bit, name in bit_map.items()
    }


# ============================================================
# DECODIFICA REC
# ============================================================

def decode_rec(rec_row):

    states = {}

    for word in WORD_LIST:

        if (
            word in BIT_MAP
            and word in rec_row
        ):

            states.update(
                decode_word(
                    rec_row[word],
                    BIT_MAP[word]
                )
            )

    return states


# ============================================================
# FUNZIONE DISPLAY DIGITALE
# ============================================================

def digital_signal(name, value):

    if value:

        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                margin-bottom:4px;
            ">
                <div style="
                    width:14px;
                    height:14px;
                    background:#00c853;
                    border-radius:50%;
                    margin-right:8px;
                "></div>
                <span>{name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                margin-bottom:4px;
            ">
                <div style="
                    width:14px;
                    height:14px;
                    background:#d0d0d0;
                    border-radius:50%;
                    margin-right:8px;
                "></div>
                <span>{name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PAGINA CCM
# ============================================================

def ccm_page():

    st.title("⚡ Analisi Log CCM")

    st.markdown(
        "Carica un file **.CAP** per analizzare il log CCM."
    )

    # ========================================================
    # UPLOAD
    # ========================================================

    uploaded_file = st.file_uploader(
        "📂 Seleziona file CCM",
        type=["CAP", "cap"],
        key="ccm_uploader"
    )

    if uploaded_file is None:

        st.info(
            "Carica un file .CAP per iniziare l'analisi."
        )

        return

    # ========================================================
    # PARSE
    # ========================================================

    try:

        file_bytes = uploaded_file.getvalue()

        summary, ll_blocks = parse_file(
            file_bytes
        )

    except Exception as e:

        st.error(
            f"Errore durante la lettura del file: {e}"
        )

        return

    if not summary:

        st.error(
            "Nessun Summary trovato nel file."
        )

        return

    # ========================================================
    # DATAFRAME SUMMARY
    # ========================================================

    columns = (
        ["REC", "CODE", "DATE", "TIME"]
        + [f"F{i+1}" for i in range(MAX_FIELDS)]
        + ["DESCRIZIONE"]
    )

    summary_df = pd.DataFrame(
        summary,
        columns=columns
    )

    # ========================================================
    # INFO FILE
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "REC",
            len(summary_df)
        )

    with col2:
        st.metric(
            "LL disponibili",
            sum(
                1
                for rec in ll_blocks
                if ll_blocks[rec]
            )
        )

    with col3:
        st.metric(
            "Campioni LL",
            sum(
                len(v)
                for v in ll_blocks.values()
            )
        )

    st.divider()

    # ========================================================
    # RICERCA
    # ========================================================

    ricerca = st.text_input(
        "🔎 Cerca nel Summary",
        placeholder=(
            "REC, CODE, descrizione, F1, F2..."
        ),
        key="ccm_search"
    )

    filtered_df = summary_df.copy()

    if ricerca:

        mask = filtered_df.astype(str).apply(
            lambda col:
                col.str.contains(
                    ricerca,
                    case=False,
                    na=False
                )
        ).any(axis=1)

        filtered_df = filtered_df[mask]

    st.markdown("### 📋 SUMMARY")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=350
    )

    if filtered_df.empty:

        st.warning(
            "Nessun REC corrisponde alla ricerca."
        )

        return

    # ========================================================
    # SELEZIONE REC
    # ========================================================

    rec_options = filtered_df["REC"].tolist()

    selected_rec = st.selectbox(
        "Seleziona REC da analizzare",
        rec_options,
        key="ccm_selected_rec"
    )

    # ========================================================
    # DATI REC
    # ========================================================

    selected_row = summary_df[
        summary_df["REC"] == selected_rec
    ].iloc[0]

    st.divider()

    st.markdown(
        f"### 🔍 Analisi REC {selected_rec}"
    )

    info1, info2, info3, info4 = st.columns(4)

    with info1:
        st.write("**CODE**")
        st.write(selected_row["CODE"])

    with info2:
        st.write("**DATA**")
        st.write(selected_row["DATE"])

    with info3:
        st.write("**ORA**")
        st.write(selected_row["TIME"])

    with info4:
        st.write("**LL**")
        st.write(
            len(
                ll_blocks.get(
                    selected_rec,
                    []
                )
            )
        )

    descrizione = selected_row["DESCRIZIONE"]

    if descrizione:

        st.info(
            f"**Descrizione:** {descrizione}"
        )

    # ========================================================
    # LL
    # ========================================================

    ll = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll:

        st.warning(
            f"Nessuna LL disponibile per REC {selected_rec}."
        )

        return

    st.divider()

    st.markdown(
        f"### 📊 Analisi LL — REC {selected_rec}"
    )

    # ========================================================
    # SESSION STATE INDICE
    # ========================================================

    state_key = f"ccm_idx_{selected_rec}"

    if state_key not in st.session_state:

        st.session_state[state_key] = 0

    index = st.session_state[state_key]

    index = max(
        0,
        min(
            index,
            len(ll) - 1
        )
    )

    # ========================================================
    # PULSANTI NAVIGAZIONE
    # ========================================================

    col_prev, col_info, col_next = st.columns(
        [1, 3, 1]
    )

    with col_prev:

        if st.button(
            "⬅️ Indietro",
            use_container_width=True,
            key=f"ccm_prev_{selected_rec}"
        ):

            st.session_state[state_key] = max(
                0,
                index - 1
            )

            st.rerun()

    with col_info:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-size:20px;
                font-weight:bold;
                padding-top:5px;
            ">
                Campione {index + 1} / {len(ll)}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_next:

        if st.button(
            "Avanti ➡️",
            use_container_width=True,
            key=f"ccm_next_{selected_rec}"
        ):

            st.session_state[state_key] = min(
                len(ll) - 1,
                index + 1
            )

            st.rerun()

    # ========================================================
    # SLIDER
    # ========================================================

    index = st.slider(
        "Timeline LL",
        min_value=0,
        max_value=len(ll) - 1,
        value=index,
        key=f"ccm_slider_{selected_rec}"
    )

    st.session_state[state_key] = index

    row = ll[index]

    # ========================================================
    # NUMERO CAMPIONE
    # ========================================================

    st.markdown(
        f"""
        **N = {row.get("N", "---")}**
        """
    )

    # ========================================================
    # DECODIFICA
    # ========================================================

    states = decode_rec(row)

    # ========================================================
    # LAYOUT DIGITALE / ANALOGICO
    # ========================================================

    col_digital, col_analog = st.columns(
        [2.5, 1]
    )

    # ========================================================
    # DIGITALI
    # ========================================================

    with col_digital:

        st.markdown(
            "### 🔌 Segnali digitali"
        )

        digital_cols = st.columns(3)

        groups = [
            "sCCa",
            "PSWA",
            "PSWB",
            "PHW1",
            "flcom",
            "PHW3",
            "stdi",
            "stdo",
            "PCUc",
            "PCUs",
            "msf",
        ]

        for i, word in enumerate(groups):

            if word not in BIT_MAP:
                continue

            with digital_cols[i % 3]:

                st.markdown(
                    f"**{word}**"
                )

                for signal in BIT_MAP[word].values():

                    if signal == "-----":
                        continue

                    value = states.get(
                        signal,
                        0
                    )

                    digital_signal(
                        signal,
                        value
                    )

    # ========================================================
    # ANALOGICI
    # ========================================================

    with col_analog:

        st.markdown(
            "### 📈 Segnali analogici"
        )

        for signal in ANALOG_SIGNALS:

            value = row.get(
                signal,
                "---"
            )

            st.metric(
                signal,
                str(value)
            )

    # ========================================================
    # VALORI RAW
    # ========================================================

    with st.expander(
        "🔧 Visualizza valori RAW della LL"
    ):

        raw_df = pd.DataFrame(
            [row]
        )

        st.dataframe(
            raw_df,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # BIT ATTIVI
    # ========================================================

    active_signals = [
        name
        for name, value in states.items()
        if value == 1
    ]

    with st.expander(
        f"🟢 Segnali attivi ({len(active_signals)})"
    ):

        if active_signals:

            st.write(
                ", ".join(
                    active_signals
                )
            )

        else:

            st.info(
                "Nessun segnale digitale attivo."
            )
