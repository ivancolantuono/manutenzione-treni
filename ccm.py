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
        1: "dvfProtLed",
        2: "dvlProtLed",
        3: "dvfProtLed2",
        4: "dvlProtLed2",
        5: "koThCHPIND1",
        6: "koThCHPIND2",
        7: "koThINTAIR",
        8: "koThHEATSINK",
        9: "PcuKO",
        10: "pswCHPIND1_HOTMAX",
        11: "pswUNDERVOLTPRIM",
        12: "pswOPENFAILBYS",
        13: "pswCHPIND2_HOTMAX",
        14: "pswUNDERVOLTSEC",
        15: "pswOPENFAILBY",
    },

    "PSWB": {
        0: "pswINTAIR_HOTMAX",
        1: "pswUNBASUPERV",
        2: "pswkoTA",
        3: "-----",
        4: "UNDERVOLTLINE3K",
        5: "pswINCALTI",
        6: "DISCHA_FAIL",
        7: "HEATSINK_HOTMAX",
        8: "pswCLOSEFAILBY",
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
        0: "-----",
        1: "-----",
        2: "-----",
        3: "-----",
        4: "earthfault",
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

    "PHW3": {
        0: "DiaUp1",
        1: "DiaUp2",
        2: "DiaUp3",
        3: "DiaUp4",
        4: "DiaUp5",
        5: "DiaDown1",
        6: "DiaDown2",
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
# RICERCA NEL SUMMARY
# =========================================================

def filter_summary(summary, search_text):
    """
    Filtra gli eventi del Summary cercando il testo
    nella DESCRIZIONE.
    La ricerca non distingue maiuscole/minuscole.
    """

    if not search_text:
        return summary

    search_text = search_text.strip().lower()

    if not search_text:
        return summary

    filtered = []

    for row in summary:
        description = str(row[-1]).lower()

        if search_text in description:
            filtered.append(row)

    return filtered



def show_all_digitals(states):
    columns = st.columns(5, gap="small")

    for index, word in enumerate(DIGITAL_WORDS):
        with columns[index % 5]:
            render_word(word, states)


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

    # -----------------------------------------------------
    # CERCA NELLA DESCRIZIONE
    # -----------------------------------------------------

    search_text = st.text_input(
        "🔎 Cerca nella descrizione",
        placeholder="Scrivi una parola, un codice o una parte della descrizione...",
        key="ccm_summary_search"
    )

    if search_text.strip():

        mask = df["DESCRIZIONE"].astype(str).str.contains(
            search_text.strip(),
            case=False,
            na=False,
            regex=False
        )

        filtered_df = df[mask].copy()

        st.caption(
            f"Trovati {len(filtered_df)} eventi su {len(df)}"
        )

    else:

        filtered_df = df

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=280
    )

    return filtered_df


# =========================================================
# ANALOGICI
# =========================================================

def show_analogicals(row):
    columns = st.columns(len(ANALOG_SIGNALS), gap="small")

    for column, signal in zip(columns, ANALOG_SIGNALS):
        value = row.get(signal, "—")

        if value in ("", None):
            value = "—"

        analog_html = (
            '<div class="ccm-analog">'
            f'<div class="ccm-analog-name">{html.escape(signal)}</div>'
            f'<div class="ccm-analog-value">{html.escape(str(value))}</div>'
            '</div>'
        )

        with column:
            st.markdown(
                analog_html,
                unsafe_allow_html=True
            )


# =========================================================
# CCM PAGE
# =========================================================

def ccm_page():

    inject_css()

    st.title("CCM")

    # -----------------------------------------------------
    # CARICAMENTO FILE
    # -----------------------------------------------------

    uploaded_file = st.file_uploader(
        "Carica file CCM",
        type=["CAP", "cap"],
        key="ccm_upload"
    )

    if uploaded_file is None:
        st.info(
            "Carica un file .CAP per iniziare l'analisi."
        )
        return

    # -----------------------------------------------------
    # PARSING
    # -----------------------------------------------------

    try:
        summary, ll_blocks = parse_file(uploaded_file)

    except Exception as error:
        st.error(
            f"Errore nella lettura del file CCM: {error}"
        )
        return

    if not summary:
        st.warning(
            "Nessun evento Summary trovato nel file."
        )
        return

    # -----------------------------------------------------
    # RICERCA NELLA DESCRIZIONE
    # -----------------------------------------------------

    st.subheader("📋 Summary")

    search_text = st.text_input(
        "🔎 Cerca nella descrizione",
        placeholder="Inserisci una parola o parte della descrizione...",
        key="ccm_search_description"
    )

    filtered_summary = filter_summary(
        summary,
        search_text
    )

    if search_text.strip():
        st.caption(
            f"Trovati {len(filtered_summary)} eventi "
            f"su {len(summary)}"
        )

    # -----------------------------------------------------
    # SUMMARY FILTRATO
    # -----------------------------------------------------

    render_summary(filtered_summary)

    if not filtered_summary:
        st.warning(
            "Nessun evento trovato nella descrizione."
        )
        return

    # -----------------------------------------------------
    # SELEZIONE REC
    # -----------------------------------------------------

    st.markdown("---")

    options = {}

    for row in filtered_summary:

        rec = int(row[0])
        description = row[-1]

        if description:
            label = (
                f"REC {rec} — "
                f"{description}"
            )
        else:
            label = f"REC {rec}"

        options[label] = rec

    selected_label = st.selectbox(
        "Seleziona REC",
        list(options.keys()),
        key="ccm_selected_rec"
    )

    selected_rec = options[selected_label]

    ll_rows = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll_rows:
        st.warning(
            f"Nessun campione LL disponibile "
            f"per REC {selected_rec}."
        )
        return

    # -----------------------------------------------------
    # DESCRIZIONE REC
    # -----------------------------------------------------

    selected_summary = None

    for row in filtered_summary:

        if int(row[0]) == selected_rec:
            selected_summary = row
            break

    if selected_summary:

        description = selected_summary[-1]

        if description:
            st.caption(
                f"Descrizione: {description}"
            )

    # -----------------------------------------------------
    # TIMELINE
    # -----------------------------------------------------

    max_index = len(ll_rows) - 1

    current_index = st.session_state.get(
        "ccm_current_index",
        0
    )

    if current_index > max_index:
        current_index = max_index

    current_index = st.slider(
        "⏱️ Timeline",
        min_value=0,
        max_value=max_index,
        value=current_index,
        key=f"ccm_timeline_{selected_rec}"
    )

    st.session_state[
        "ccm_current_index"
    ] = current_index

    # -----------------------------------------------------
    # CAMPIONE CORRENTE
    # -----------------------------------------------------

    current_row = ll_rows[current_index]

    states = decode_rec(
        current_row
    )

    st.markdown(
        f"""
        <div class="ccm-info">
            Campione:
            <b>{current_index + 1} / {len(ll_rows)}</b>
            &nbsp;&nbsp;&nbsp;
            N:
            <b>{current_row.get("N", "—")}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # DIGITALI
    # -----------------------------------------------------

    st.subheader("🔌 Segnali digitali")

    # 5 colonne
    columns = st.columns(5, gap="small")

    for index, word in enumerate(DIGITAL_WORDS):

        column = columns[index % 5]

        with column:
            render_word(word, states)

    # -----------------------------------------------------
    # ANALOGICI
    # -----------------------------------------------------

    st.markdown("---")

    st.subheader("📈 Segnali analogici")

    show_analogicals(
        current_row
    )
