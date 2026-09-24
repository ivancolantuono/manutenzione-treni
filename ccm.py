import streamlit as st
import pandas as pd
import re
import time


# =========================================================
# CONFIGURAZIONE
# =========================================================

MAX_FIELDS = 6

ANALOG_SIGNALS = [
    "vTVL",
    "vTV1",
    "iTA1M",
    "iTA2M",
    "iTA",
    "vTVI",
]


# =========================================================
# BIT MAP
# =========================================================

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


# =========================================================
# ORDINE VISUALIZZAZIONE
# =========================================================

DIGITAL_GROUPS = [
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


# =========================================================
# REGEX PARSER
# =========================================================

SM_RE = re.compile(
    r"^Rec:\s+(\d+)\s+Code:\s+([0-9A-Fa-f]+)\s+"
    r"Date:(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{2}:\d{2}:\d{2}\.\d{2})\s+-\s+(.*)$"
)

LL_HEADER_RE = re.compile(r"^\s*N\.\s+")

LL_ROW_RE = re.compile(
    r"^\s*(-?\d+)\s+(.*)$"
)


# =========================================================
# DECODIFICA WORD
# =========================================================

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


def decode_rec(rec_row):

    states = {}

    for word in BIT_MAP:

        if word in rec_row:

            states.update(
                decode_word(
                    rec_row[word],
                    BIT_MAP[word]
                )
            )

    return states


# =========================================================
# DESCRIZIONE
# =========================================================

def split_description(desc):

    descrizione = ""

    if " - " in desc:

        left, descrizione = desc.split(
            " - ",
            1
        )

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

    return (
        fields,
        descrizione.strip()
    )


# =========================================================
# PARSER CAP
# =========================================================

def parse_file(uploaded_file):

    summary = []
    ll_blocks = {}

    current_rec = None
    in_ll = False
    columns = []

    content = uploaded_file.read()

    if isinstance(content, bytes):

        content = content.decode(
            "utf-8",
            errors="ignore"
        )

    for line in content.splitlines():

        # -----------------------------------------------
        # SUMMARY
        # -----------------------------------------------

        m = SM_RE.match(line)

        if m:

            rec = int(m.group(1))
            code = m.group(2)
            date = m.group(3)
            time_value = m.group(4)
            desc = m.group(5)

            fields, descrizione = (
                split_description(desc)
            )

            summary.append(
                [
                    rec,
                    code,
                    date,
                    time_value
                ]
                + fields
                + [descrizione]
            )

            ll_blocks[rec] = []

            current_rec = rec
            in_ll = False

            continue

        # -----------------------------------------------
        # HEADER LL
        # -----------------------------------------------

        if LL_HEADER_RE.match(line):

            columns = line.split()

            in_ll = True

            continue

        # -----------------------------------------------
        # RIGA LL
        # -----------------------------------------------

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

            for i, col in enumerate(
                columns[1:]
            ):

                row[col] = values[i]

            ll_blocks[current_rec].append(
                row
            )

    return summary, ll_blocks


# =========================================================
# DIGITAL SIGNAL
# =========================================================

def digital_signal(name, value):

    if value:

        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                padding:3px 6px;
                margin-bottom:2px;
                border-radius:5px;
                background-color:#ffe5e5;
                border-left:5px solid #d32f2f;
            ">
                <span style="
                    width:12px;
                    height:12px;
                    background:#d32f2f;
                    border-radius:50%;
                    display:inline-block;
                    margin-right:8px;
                "></span>

                <span style="
                    font-weight:600;
                ">
                    {name}
                </span>

                <span style="
                    margin-left:auto;
                    font-weight:bold;
                    color:#d32f2f;
                ">
                    1
                </span>
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
                padding:3px 6px;
                margin-bottom:2px;
                border-radius:5px;
                background-color:#f5f5f5;
                border-left:5px solid #bdbdbd;
            ">
                <span style="
                    width:12px;
                    height:12px;
                    background:#bdbdbd;
                    border-radius:50%;
                    display:inline-block;
                    margin-right:8px;
                "></span>

                <span>
                    {name}
                </span>

                <span style="
                    margin-left:auto;
                    color:#777;
                ">
                    0
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# PAGINA STREAMLIT
# =========================================================

def ccm_page():

    st.title("⚡ CCM")

    st.caption(
        "Analisi file CCM / MCM – Summary e segnali LL"
    )

    # =====================================================
    # UPLOAD
    # =====================================================

    uploaded_file = st.file_uploader(
        "Seleziona file CCM",
        type=["CAP", "cap"],
        key="ccm_file"
    )

    if uploaded_file is None:

        st.info(
            "Carica un file .CAP per iniziare l'analisi."
        )

        return

    # =====================================================
    # PARSE
    # =====================================================

    try:

        summary, ll_blocks = parse_file(
            uploaded_file
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

    # =====================================================
    # SUMMARY DATAFRAME
    # =====================================================

    columns = (
        ["REC", "CODE", "DATE", "TIME"]
        +
        [
            f"F{i+1}"
            for i in range(MAX_FIELDS)
        ]
        +
        ["DESCRIZIONE"]
    )

    summary_df = pd.DataFrame(
        summary,
        columns=columns
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    st.subheader(
        "📋 Summary"
    )

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # SELEZIONE REC
    # =====================================================

    st.divider()

    st.subheader(
        "🔎 Analisi REC"
    )

    rec_values = summary_df[
        "REC"
    ].tolist()

    selected_rec = st.selectbox(
        "Seleziona REC",
        rec_values,
        format_func=lambda x: (
            f"REC {x}"
        )
    )

    selected_row = summary_df[
        summary_df["REC"] == selected_rec
    ].iloc[0]

    descrizione = selected_row[
        "DESCRIZIONE"
    ]

    if descrizione:

        st.info(
            f"**Descrizione:** {descrizione}"
        )

    # =====================================================
    # LL
    # =====================================================

    ll = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll:

        st.warning(
            "Nessuna LL disponibile per questo REC."
        )

        return

    # =====================================================
    # SESSION STATE
    # =====================================================

    state_key = (
        f"ccm_idx_{selected_rec}"
    )

    if state_key not in st.session_state:

        st.session_state[
            state_key
        ] = 0

    index = st.session_state[
        state_key
    ]

    index = max(
        0,
        min(
            index,
            len(ll) - 1
        )
    )

    # =====================================================
    # CONTROLLI
    # =====================================================

    st.markdown(
        "### 🎛️ Navigazione"
    )

    col1, col2, col3, col4 = st.columns(
        [1, 1, 3, 1]
    )

    with col1:

        if st.button(
            "◀ Indietro",
            use_container_width=True
        ):

            index = max(
                0,
                index - 1
            )

            st.session_state[
                state_key
            ] = index

            st.rerun()

    with col2:

        if st.button(
            "Avanti ▶",
            use_container_width=True
        ):

            index = min(
                len(ll) - 1,
                index + 1
            )

            st.session_state[
                state_key
            ] = index

            st.rerun()

    with col3:

        new_index = st.slider(
            "Campione",
            min_value=0,
            max_value=len(ll) - 1,
            value=index,
            key=f"ccm_slider_{selected_rec}"
        )

        if new_index != index:

            st.session_state[
                state_key
            ] = new_index

            index = new_index

    with col4:

        st.metric(
            "N",
            ll[index].get(
                "N",
                "---"
            )
        )

    # =====================================================
    # RECORD CORRENTE
    # =====================================================

    row = ll[index]

    states = decode_rec(row)

    st.caption(
        f"Campione {index + 1} di {len(ll)}"
    )

    # =====================================================
    # DIGITALI
    # =====================================================

    st.divider()

    st.subheader(
        "🔌 Segnali digitali"
    )

    # 3 colonne
    digital_cols = st.columns(3)

    for i, word in enumerate(
        DIGITAL_GROUPS
    ):

        if word not in BIT_MAP:
            continue

        with digital_cols[
            i % 3
        ]:

            st.markdown(
                f"#### {word}"
            )

            for signal in BIT_MAP[
                word
            ].values():

                # salta bit inutilizzati
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

    # =====================================================
    # ANALOGICI
    # =====================================================

    st.divider()

    st.subheader(
        "📈 Segnali analogici"
    )

    analog_cols = st.columns(
        len(ANALOG_SIGNALS)
    )

    for col, signal in zip(
        analog_cols,
        ANALOG_SIGNALS
    ):

        value = row.get(
            signal,
            "---"
        )

        with col:

            st.metric(
                signal,
                str(value)
            )

    # =====================================================
    # TABELLA LL
    # =====================================================

    st.divider()

    with st.expander(
        "📄 Visualizza dati LL completi"
    ):

        ll_df = pd.DataFrame(
            ll
        )

        st.dataframe(
            ll_df,
            use_container_width=True,
            hide_index=True
        )
