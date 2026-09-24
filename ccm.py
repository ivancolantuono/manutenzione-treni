import streamlit as st
import re


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
# DECODIFICA BIT
# =========================================================

BIT_MAP = {

    # -----------------------------------------------------
    # sCCa
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PSWA
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PSWB
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PHW1
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PHW2
    # -----------------------------------------------------
    # Nel codice originale che mi avevi mandato PHW2
    # non aveva una BIT_MAP completa.
    # Manteniamo almeno il segnale che compare nella
    # visualizzazione che hai mostrato.
    # -----------------------------------------------------
    "PHW2": {
        0: "earthfault",
    },

    # -----------------------------------------------------
    # flcom
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PHW3
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # stdi
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # stdo
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PCUc
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # PCUs
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # msf
    # -----------------------------------------------------
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

DIGITAL_WORDS = [
    "sCCa",
    "PSWA",
    "PSWB",
    "PHW1",
    "PHW2",
    "PHW3",
    "PHW4",
    "flcom",
    "stdi",
    "stdo",
    "PCUc",
    "PCUs",
    "msf",
]


# =========================================================
# PARSER
# =========================================================

SM_RE = re.compile(
    r"^Rec:\s+(\d+)\s+Code:\s+([0-9A-Fa-f]+)"
    r"\s+Date:(\d{2}/\d{2}/\d{4})"
    r"\s+(\d{2}:\d{2}:\d{2}\.\d{2})"
    r"\s+-\s+(.*)$"
)

LL_HEADER_RE = re.compile(r"^\s*N\.\s+")
LL_ROW_RE = re.compile(r"^\s*(-?\d+)\s+(.*)$")


# =========================================================
# DESCRIZIONE
# =========================================================

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


# =========================================================
# PARSE FILE
# =========================================================

def parse_file(uploaded_file):

    summary = []
    ll_blocks = {}

    current_rec = None
    in_ll = False
    columns = []

    text = uploaded_file.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    for line in text.splitlines():

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

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

        # -------------------------------------------------
        # HEADER LL
        # -------------------------------------------------

        if LL_HEADER_RE.match(line):

            columns = line.split()

            in_ll = True

            continue

        # -------------------------------------------------
        # RIGHE LL
        # -------------------------------------------------

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


# =========================================================
# DECODE WORD
# =========================================================

def decode_word(hex_value, bit_map):

    try:
        value = int(
            str(hex_value),
            16
        )
    except Exception:
        value = 0

    states = {}

    for bit, name in bit_map.items():

        states[name] = (
            value >> bit
        ) & 1

    return states


# =========================================================
# DECODE RECORD
# =========================================================

def decode_rec(rec_row):

    states = {}

    for word in DIGITAL_WORDS:

        if word not in BIT_MAP:
            continue

        if word not in rec_row:
            continue

        decoded = decode_word(
            rec_row[word],
            BIT_MAP[word]
        )

        states.update(decoded)

    return states


# =========================================================
# CSS
# =========================================================

def load_css():

    st.markdown(
        """
        <style>

        /* ---------------------------------------------
           DIGITALI
        --------------------------------------------- */

        .ccm-box {

            border: 1px solid #d9d9d9;

            border-radius: 6px;

            background: #ffffff;

            padding: 5px;

            margin-bottom: 6px;

        }

        .ccm-title {

            font-size: 13px;

            font-weight: 700;

            color: #222;

            padding: 4px 5px;

            border-bottom: 1px solid #eeeeee;

            margin-bottom: 4px;

        }

        .ccm-signal {

            height: 20px;

            line-height: 20px;

            font-size: 11px;

            padding: 0px 5px;

            margin: 1px 0px;

            border-radius: 3px;

            white-space: nowrap;

            overflow: hidden;

            text-overflow: ellipsis;

        }

        .ccm-on {

            background: #ffdede;

            color: #b00000;

            font-weight: 600;

            border-left: 4px solid #e30613;

        }

        .ccm-off {

            background: #f2f2f2;

            color: #555;

            border-left: 4px solid #d0d0d0;

        }


        /* ---------------------------------------------
           ANALOGICI
        --------------------------------------------- */

        .ccm-analog-box {

            border: 1px solid #d9d9d9;

            border-radius: 6px;

            padding: 10px;

            background: white;

            text-align: center;

        }

        .ccm-analog-name {

            font-size: 12px;

            color: #555;

        }

        .ccm-analog-value {

            font-size: 18px;

            font-weight: 700;

            margin-top: 4px;

        }


        /* ---------------------------------------------
           INFO TIMELINE
        --------------------------------------------- */

        .ccm-info {

            border: 1px solid #d9e2f3;

            background: #f7faff;

            border-radius: 6px;

            padding: 8px 12px;

            margin-bottom: 10px;

            font-size: 13px;

        }

        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# BLOCCO DIGITALE
# =========================================================

def render_digital_block(word, states):

    if word not in BIT_MAP:
        return

    st.markdown(
        f"""
        <div class="ccm-box">

            <div class="ccm-title">
                {word}
            </div>
        """,
        unsafe_allow_html=True
    )

    for bit, signal in BIT_MAP[word].items():

        # Non visualizziamo i bit -----
        if signal == "-----":
            continue

        value = states.get(
            signal,
            0
        )

        if value:

            html = f"""
            <div class="ccm-signal ccm-on">
                🔴 {signal}
            </div>
            """

        else:

            html = f"""
            <div class="ccm-signal ccm-off">
                ⚪ {signal}
            </div>
            """

        st.markdown(
            html,
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# BLOCCO ANALOGICO
# =========================================================

def render_analog_signal(signal, row):

    value = row.get(
        signal,
        ""
    )

    if value == "":
        value = "—"

    st.markdown(
        f"""
        <div class="ccm-analog-box">

            <div class="ccm-analog-name">
                {signal}
            </div>

            <div class="ccm-analog-value">
                {value}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PAGINA CCM
# =========================================================

def ccm_page():

    load_css()

    st.title("⚡ Analisi CCM")

    # =====================================================
    # UPLOAD
    # =====================================================

    uploaded_file = st.file_uploader(
        "📤 Carica file CCM",
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
            f"Errore nella lettura del file: {e}"
        )

        return

    if not summary:

        st.warning(
            "Nessun Summary trovato nel file CCM."
        )

        return

    # =====================================================
    # SELEZIONE REC
    # =====================================================

    rec_options = list(
        range(len(summary))
    )

    # =====================================================
    # DEFAULT
    # =====================================================

    if "ccm_index" not in st.session_state:

        st.session_state.ccm_index = 0

    # Evita indice fuori limite
    if st.session_state.ccm_index >= len(summary):

        st.session_state.ccm_index = (
            len(summary) - 1
        )

    # =====================================================
    # TIMELINE
    # =====================================================

    st.markdown(
        "### ⏱️ Timeline"
    )

    index = st.slider(
        "Campione",
        min_value=0,
        max_value=len(summary) - 1,
        value=st.session_state.ccm_index,
        key="ccm_timeline",
        label_visibility="collapsed"
    )

    st.session_state.ccm_index = index

    # =====================================================
    # DATI CAMPIONE
    # =====================================================

    selected_summary = summary[index]

    rec = int(
        selected_summary[0]
    )

    code = selected_summary[1]
    date = selected_summary[2]
    time = selected_summary[3]

    descrizione = selected_summary[-1]

    # =====================================================
    # REC INFO
    # =====================================================

    st.markdown(
        f"""
        <div class="ccm-info">

        <b>Campione:</b>
        {index + 1} / {len(summary)}

        &nbsp;&nbsp; | &nbsp;&nbsp;

        <b>REC:</b>
        {rec}

        &nbsp;&nbsp; | &nbsp;&nbsp;

        <b>Data:</b>
        {date}

        &nbsp;&nbsp; | &nbsp;&nbsp;

        <b>Ora:</b>
        {time}

        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # LL
    # =====================================================

    ll = ll_blocks.get(
        rec,
        []
    )

    if not ll:

        st.warning(
            f"Nessuna LL disponibile per REC {rec}."
        )

        return

    # =====================================================
    # SELEZIONE RIGA LL
    # =====================================================

    # Per la visualizzazione utilizziamo la prima riga
    # LL come riferimento iniziale.
    #
    # Se il file contiene più campioni LL, viene
    # utilizzato l'indice della timeline quando possibile.

    ll_index = index

    if ll_index >= len(ll):

        ll_index = len(ll) - 1

    row = ll[ll_index]

    # =====================================================
    # DECODIFICA
    # =====================================================

    states = decode_rec(row)

    # =====================================================
    # DESCRIZIONE
    # =====================================================

    if descrizione:

        st.caption(
            descrizione
        )

    # =====================================================
    # DIGITALI
    # =====================================================

    st.markdown(
        "### 🔌 Segnali digitali"
    )

    # -----------------------------------------------------
    # 4 COLONNE
    # -----------------------------------------------------

    columns = st.columns(
        4,
        gap="small"
    )

    for i, word in enumerate(
        DIGITAL_WORDS
    ):

        col = columns[
            i % 4
        ]

        with col:

            render_digital_block(
                word,
                states
            )

    # =====================================================
    # ANALOGICI
    # =====================================================

    st.markdown(
        "---"
    )

    st.markdown(
        "### 📊 Segnali analogici"
    )

    analog_columns = st.columns(
        6,
        gap="small"
    )

    for i, signal in enumerate(
        ANALOG_SIGNALS
    ):

        with analog_columns[i]:

            render_analog_signal(
                signal,
                row
            )

    # =====================================================
    # DEBUG FACOLTATIVO
    # =====================================================

    # Non visualizziamo i valori 0/1 all'utente.
    # I valori vengono usati solamente internamente
    # per determinare il colore del segnale.


# =========================================================
# AVVIO DIRETTO
# =========================================================

if __name__ == "__main__":

    ccm_page()
