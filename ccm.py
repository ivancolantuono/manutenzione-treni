import streamlit as st
import pandas as pd
import re
import html
import textwrap


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
        2: "pswkoTA",
        3: "pswTA1SUPERV",
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

    "PHW2": {
        0: "earthfault",
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

    "PHW4": {},

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
# DECODIFICA
# =========================================================

def decode_word(hex_value, bit_map):

    try:
        value = int(str(hex_value), 16)
    except Exception:
        value = 0

    result = {}

    for bit, name in bit_map.items():

        if name == "-----":
            continue

        result[name] = (value >> bit) & 1

    return result


def decode_rec(rec_row):

    states = {}

    for word in DIGITAL_WORDS:

        if word in BIT_MAP and word in rec_row:

            states.update(
                decode_word(
                    rec_row[word],
                    BIT_MAP[word]
                )
            )

    return states


# =========================================================
# REGEX
# =========================================================

SM_RE = re.compile(
    r"^Rec:\s+(\d+)\s+Code:\s+([0-9A-Fa-f]+)\s+"
    r"Date:(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{2}:\d{2}:\d{2}\.\d{2})\s+-\s+(.*)$"
)

LL_HEADER_RE = re.compile(r"^\s*N\.\s+")

LL_ROW_RE = re.compile(r"^\s*(-?\d+)\s+(.*)$")


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

    return fields, descrizione.strip()


# =========================================================
# PARSER CAP
# =========================================================

def parse_file(uploaded_file):

    summary = []

    ll_blocks = {}

    current_rec = None

    in_ll = False

    columns = []

    text = uploaded_file.read()

    if isinstance(text, bytes):

        text = text.decode(
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


# =========================================================
# CSS
# =========================================================

def inject_css():

    st.markdown(
        """
        <style>

        .ccm-container {
            width: 100%;
        }

        .ccm-title {
            font-size: 13px;
            font-weight: 700;
            padding: 6px 8px;
            background: #f7f8fa;
            border-bottom: 1px solid #ddd;
            margin-bottom: 3px;
        }

        .ccm-word {
            border: 1px solid #d8dce2;
            border-radius: 5px;
            overflow: hidden;
            background: white;
            margin-bottom: 6px;
        }

        .ccm-signal {
            height: 18px;
            line-height: 18px;
            margin: 1px 2px;
            padding: 0 6px;
            border-radius: 3px;
            font-size: 11px;
            font-family: Arial, sans-serif;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .ccm-off {
            background: #f1f1f1;
            color: #555;
        }

        .ccm-on {
            background: #ffdede;
            color: #b00020;
            font-weight: 700;
            border-left: 4px solid #e00020;
        }

        .ccm-led {
            display: inline-block;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
        }

        .ccm-led-off {
            background: #d8cce9;
        }

        .ccm-led-on {
            background: #e00020;
        }

        .ccm-analog {
            background: #f7f8fa;
            border: 1px solid #d8dce2;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
        }

        .ccm-analog-name {
            font-size: 12px;
            color: #555;
        }

        .ccm-analog-value {
            font-size: 18px;
            font-weight: 700;
            margin-top: 5px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DIGITAL CARD
# =========================================================

def render_word(word, states):
    signals = BIT_MAP.get(word, {})

    if not signals:
        return

    html_parts = [
        '<div class="ccm-word">',
        f'<div class="ccm-title">{html.escape(word)}</div>'
    ]

    for bit, signal in signals.items():
        if signal == "-----":
            continue

        value = states.get(signal, 0)

        if value:
            css_class = "ccm-on"
            led_class = "ccm-led-on"
        else:
            css_class = "ccm-off"
            led_class = "ccm-led-off"

        html_parts.append(
            f'<div class="ccm-signal {css_class}">'
            f'<span class="ccm-led {led_class}"></span>'
            f'{html.escape(signal)}'
            f'</div>'
        )

    html_parts.append("</div>")

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)


# =========================================================
# SUMMARY
# =========================================================

def render_summary(summary):

    st.subheader("📋 Summary")

    columns = (
        ["REC", "CODE", "DATE", "TIME"]
        + [f"F{i+1}" for i in range(MAX_FIELDS)]
        + ["DESCRIZIONE"]
    )

    df = pd.DataFrame(
        summary,
        columns=columns
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=280
    )


# =========================================================
# CCM PAGE
# =========================================================

def ccm_page():

    inject_css()

    st.title("⚡ Analisi CCM")

    uploaded_file = st.file_uploader(
        "Carica file CCM",
        type=["CAP", "cap"],
        key="ccm_upload"
    )

    if uploaded_file is None:

        st.info(
            "Carica un file .CAP per iniziare l'analisi CCM."
        )

        return

    try:

        summary, ll_blocks = parse_file(
            uploaded_file
        )

    except Exception as e:

        st.error(
            f"Errore durante la lettura del file CCM: {e}"
        )

        return

    if not summary:

        st.warning(
            "Nessun Summary trovato nel file."
        )

        return

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    render_summary(summary)

    st.divider()

    # -----------------------------------------------------
    # SELEZIONE REC
    # -----------------------------------------------------

    rec_options = [
        row[0]
        for row in summary
        if row[0] in ll_blocks
        and ll_blocks[row[0]]
    ]

    if not rec_options:

        st.warning(
            "Nel file non sono presenti blocchi LL analizzabili."
        )

        return

    selected_rec = st.selectbox(
        "Seleziona REC",
        rec_options,
        format_func=lambda x: f"REC {x}"
    )

    # -----------------------------------------------------
    # DESCRIZIONE
    # -----------------------------------------------------

    selected_summary = next(
        (
            row
            for row in summary
            if row[0] == selected_rec
        ),
        None
    )

    if selected_summary:

        descrizione = selected_summary[-1]

        if descrizione:

            st.info(
                f"Evento: {descrizione}"
            )

    # -----------------------------------------------------
    # LL
    # -----------------------------------------------------

    ll = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll:

        st.warning(
            f"Nessuna LL per REC {selected_rec}"
        )

        return

    # -----------------------------------------------------
    # TIMELINE
    # -----------------------------------------------------

    st.subheader("⏱️ Timeline")

    idx = st.slider(
        "Campione",
        min_value=0,
        max_value=len(ll) - 1,
        value=0,
        key=f"ccm_slider_{selected_rec}"
    )

    row = ll[idx]

    states = decode_rec(row)

    st.caption(
        f"Campione: {idx + 1} / {len(ll)}"
    )

    st.caption(
        f"N: {row.get('N', '-')}"
    )

    # -----------------------------------------------------
    # SEGNALI DIGITALI
    # -----------------------------------------------------

    st.divider()

    st.subheader("🔌 Segnali digitali")

    # 4 colonne ravvicinate
    cols = st.columns(
        4,
        gap="small"
    )

    for i, word in enumerate(DIGITAL_WORDS):

        with cols[i % 4]:

            render_word(
                word,
                states
            )

    # -----------------------------------------------------
    # ANALOGICI
    # -----------------------------------------------------

    st.divider()

    st.subheader("📈 Segnali analogici")

    analog_cols = st.columns(
        len(ANALOG_SIGNALS),
        gap="small"
    )

    for col, signal in zip(
        analog_cols,
        ANALOG_SIGNALS
    ):

        value = row.get(
            signal,
            "—"
        )

        with col:

            analog_html = (
                '<div class="ccm-analog">'
                f'<div class="ccm-analog-name">{html.escape(signal)}</div>'
                f'<div class="ccm-analog-value">{html.escape(str(value))}</div>'
                '</div>'
            )

            st.markdown(
                analog_html,
                unsafe_allow_html=True
            )
