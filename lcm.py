import streamlit as st
import pandas as pd
import re
import html

# =========================================================
# CONFIGURAZIONE
# =========================================================

MAX_FIELDS = 6

ANALOG_SIGNALS = [
    "vleff",
    "vTVLAC",
    "vTV1",
    "iTAC",
    "iTA2",
    "iTA4",
]

ANALOG_DESCRIPTIONS = {
    "vleff": "Valore efficace della tensione di linea",
    "vTVLAC": "Tensione TVL AC",
    "vTV1": "Tensione TV1",
    "iTAC": "Corrente TAC",
    "iTA2": "Corrente TA2",
    "iTA4": "Corrente TA4",
}

# =========================================================
# BIT MAP LCM
# =========================================================

BIT_MAP = {
    "sCCa": {
        0: "c4qok1",
        1: "c4qok2",
        2: "c4qok",
        3: "abPhaw",
        4: "Test",
        5: "okThHARMO",
        6: "okThINTAIR",
        7: "okTHEATSINK",
        8: "VUOTO",
        9: "VUOTO",
        10: "VUOTO",
        11: "VUOTO",
        12: "VUOTO",
        13: "VUOTO",
        14: "VUOTO",
        15: "VUOTO",
    },

    "PSWa": {
        0: "HARMO_HOT",
        1: "INTAIR_HOT",
        2: "HEATSINK_HOT",
        3: "HARMO",
        4: "INTAIR",
        5: "HEATSINK",
        6: "UNDERVOLTSEC",
        7: "TACSUPERV",
        8: "HARMLKSUPERV",
        9: "LINEFREQMIN",
        10: "LINEFREQMAX",
        11: "DISCHA_FAIL",
        12: "TEMPSCHEDHOT",
        13: "UNDERVOLTLINEAC",
        14: "PCUKO",
        15: "PHSHIFT",
    },

    "PSWb": {
        0: "DSPKO",
        1: "VUOTO",
        2: "VUOTO",
        3: "VUOTO",
        4: "VUOTO",
        5: "VUOTO",
        6: "VUOTO",
        7: "VUOTO",
        8: "VUOTO",
        9: "VUOTO",
        10: "VUOTO",
        11: "VUOTO",
        12: "VUOTO",
        13: "VUOTO",
        14: "VUOTO",
        15: "VUOTO",
    },

    "PHW1": {
        0: "VLAC",
        1: "TAC",
        2: "VUOTO",
        3: "VUOTO",
        4: "VUOTO",
        5: "VUOTO",
        6: "TV1",
        7: "TA2",
        8: "TA4",
        9: "VUOTO",
        10: "VUOTO",
        11: "VUOTO",
        12: "SCMiS",
        13: "VUOTO",
        14: "VUOTO",
        15: "VUOTO",
    },

    "PHW2": {
        0: "VUOTO",
        1: "VUOTO",
        2: "VUOTO",
        3: "VUOTO",
        4: "VUOTO",
        5: "VUOTO",
        6: "VUOTO",
        7: "VUOTO",
        8: "VUOTO",
        9: "VUOTO",
        10: "VUOTO",
        11: "VUOTO",
        12: "VUOTO",
        13: "VUOTO",
        14: "VUOTO",
        15: "VUOTO",
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
        10: "VUOTO",
        11: "VUOTO",
        12: "VUOTO",
        13: "VUOTO",
        14: "VUOTO",
        15: "VUOTO",
    },

    "PHW4": {
        0: "VUOTO",
        1: "VUOTO",
        2: "VUOTO",
        3: "PG1",
        4: "VUOTO",
        5: "VUOTO",
        6: "VUOTO",
        7: "VUOTO",
        8: "VUOTO",
        9: "VUOTO",
        10: "VUOTO",
        11: "VUOTO",
        12: "VUOTO",
        13: "VUOTO",
        14: "VUOTO",
        15: "VUOTO",
    },
}

DIGITAL_DESCRIPTIONS = {
    "c4qok1": "Stato c4qok1",
    "c4qok2": "Stato c4qok2",
    "c4qok": "Stato generale c4qok",
    "abPhaw": "Stato abPhaw",
    "Test": "Stato di test",
    "okThHARMO": "Temperatura armoniche OK",
    "okThINTAIR": "Temperatura aria interna OK",
    "okTHEATSINK": "Temperatura heatsink OK",

    "HARMO_HOT": "Sovra-temperatura armoniche",
    "INTAIR_HOT": "Sovra-temperatura aria interna",
    "HEATSINK_HOT": "Sovra-temperatura dissipatore",
    "HARMO": "Anomalia armoniche",
    "INTAIR": "Anomalia aria interna",
    "HEATSINK": "Anomalia dissipatore",
    "UNDERVOLTSEC": "Sottotensione secondaria",
    "TACSUPERV": "Supervisione TAC",
    "HARMLKSUPERV": "Supervisione armoniche",
    "LINEFREQMIN": "Frequenza linea sotto il minimo",
    "LINEFREQMAX": "Frequenza linea sopra il massimo",
    "DISCHA_FAIL": "Scarica filtri non riuscita",
    "TEMPSCHEDHOT": "Sovra-temperatura scheda",
    "UNDERVOLTLINEAC": "Sottotensione linea AC",
    "PCUKO": "Anomalia PCU",
    "PHSHIFT": "Phase shift",

    "DSPKO": "Anomalia DSP",

    "VLAC": "Tensione VLAC",
    "TAC": "Corrente TAC",
    "TV1": "Tensione TV1",
    "TA2": "Corrente TA2",
    "TA4": "Corrente TA4",
    "SCMiS": "Stato SCMiS",

    "DiaUp1": "Diagnostica UP 1",
    "DiaUp2": "Diagnostica UP 2",
    "DiaUp3": "Diagnostica UP 3",
    "DiaUp4": "Diagnostica UP 4",
    "DiaUp5": "Diagnostica UP 5",
    "DiaDown1": "Diagnostica DOWN 1",
    "DiaDown2": "Diagnostica DOWN 2",
    "DiaDown3": "Diagnostica DOWN 3",
    "DiaDown4": "Diagnostica DOWN 4",
    "DiaDown5": "Diagnostica DOWN 5",

    "PG1": "Power Good 1",
}

# Ordine di visualizzazione LCM
DIGITAL_WORDS = [
    "sCCa",
    "PSWa",
    "PSWb",
    "PHW1",
    "PHW2",
    "PHW3",
    "PHW4",
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
        if name == "VUOTO":
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
        text = text.decode("utf-8", errors="ignore")

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

        .lcm-container {
            width: 100%;
        }

        .lcm-title {
            font-size: 13px;
            font-weight: 700;
            padding: 6px 8px;
            background: #f7f8fa;
            border-bottom: 1px solid #ddd;
            margin-bottom: 3px;
        }

        .lcm-word {
            border: 1px solid #d8dce2;
            border-radius: 5px;
            overflow: hidden;
            background: white;
            margin-bottom: 6px;
        }

        .lcm-signal {
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

        .lcm-off {
            background: #f1f1f1;
            color: #555;
        }

        .lcm-on {
            background: #ffdede;
            color: #b00020;
            font-weight: 700;
            border-left: 4px solid #e00020;
        }

        .lcm-led {
            display: inline-block;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            margin-right: 6px;
            vertical-align: middle;
        }

        .lcm-led-off {
            background: #d8cce9;
        }

        .lcm-led-on {
            background: #e00020;
        }

        .lcm-info {
            background: #f7f8fa;
            border: 1px solid #d8dce2;
            border-radius: 5px;
            padding: 7px 10px;
            margin: 8px 0 12px 0;
            font-size: 13px;
        }

        .analog-row {
            display: flex;
            align-items: center;
            width: 100%;
            margin: 6px 0;
            gap: 10px;
        }

        .analog-name {
            width: 75px;
            min-width: 75px;
            font-size: 12px;
            font-weight: 600;
        }

        .analog-value {
            width: 80px;
            min-width: 80px;
            text-align: right;
            font-family: Consolas, monospace;
            font-size: 13px;
            font-weight: bold;
        }

        .analog-track {
            flex: 1;
            height: 14px;
            background: #eeeeee;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            overflow: hidden;
        }

        .analog-fill {
            height: 100%;
            background: #7b61a8;
            border-radius: 8px;
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
        '<div class="lcm-word">',
        f'<div class="lcm-title">{html.escape(word)}</div>'
    ]

    for bit, signal in signals.items():

        if signal == "VUOTO":
            continue

        value = states.get(signal, 0)

        if value:
            css_class = "lcm-on"
            led_class = "lcm-led-on"
        else:
            css_class = "lcm-off"
            led_class = "lcm-led-off"

        description = DIGITAL_DESCRIPTIONS.get(signal, "")

        html_parts.append(
            f'<div class="lcm-signal {css_class}" '
            f'title="{html.escape(description)}">'
            f'<span class="lcm-led {led_class}"></span>'
            f'{html.escape(signal)}'
            f'</div>'
        )

    html_parts.append("</div>")

    st.markdown(
        "\n".join(html_parts),
        unsafe_allow_html=True
    )


# =========================================================
# RICERCA
# =========================================================

def filter_summary(summary, search_text):

    if not search_text:
        return summary

    text = str(search_text).strip().lower()

    if not text:
        return summary

    return [
        row
        for row in summary
        if text in str(row[-1]).lower()
    ]


# =========================================================
# SUMMARY
# =========================================================

def render_summary(summary):

    columns = (
        ["REC", "CODE", "DATE", "TIME"]
        + [f"F{i+1}" for i in range(MAX_FIELDS)]
        + ["DESCRIZIONE"]
    )

    if not summary:
        st.info("Nessun evento da visualizzare.")
        return

    df = pd.DataFrame(summary, columns=columns)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# ANALOGICI
# =========================================================

def show_analogicals(row):

    ANALOG_MAX = {
        "vleff": 5000,
        "vTVLAC": 5000,
        "vTV1": 5000,
        "iTAC": 100,
        "iTA2": 100,
        "iTA4": 100,
    }

    for signal in ANALOG_SIGNALS:

        value = row.get(signal, "")

        if value in ("", None):
            value_text = "—"
            numeric_value = None

        else:
            value_text = str(value)

            try:
                numeric_value = float(
                    str(value).replace(",", ".")
                )
            except Exception:
                numeric_value = None

        max_value = ANALOG_MAX.get(signal, 100)

        if numeric_value is not None and max_value > 0:

            percentage = (
                abs(numeric_value)
                / max_value
                * 100
            )

            percentage = min(
                max(percentage, 0),
                100
            )

        else:
            percentage = 0

        analog_html = f"""
        <div class="analog-row">
            <div class="analog-name"
                 title="{html.escape(ANALOG_DESCRIPTIONS.get(signal, ""))}">
                {html.escape(signal)}
            </div>

            <div class="analog-value">
                {html.escape(value_text)}
            </div>

            <div class="analog-track">
                <div class="analog-fill"
                     style="width:{percentage:.1f}%;">
                </div>
            </div>
        </div>
        """

        st.markdown(
            analog_html,
            unsafe_allow_html=True
        )


# =========================================================
# LCM PAGE
# =========================================================

def lcm_page():

    inject_css()

    st.title("LCM")

    # =====================================================
    # CARICAMENTO FILE
    # =====================================================

    uploaded_file = st.file_uploader(
        "Carica file LCM",
        type=["CAP", "cap"],
        key="lcm_upload"
    )

    if uploaded_file is None:
        st.info("Carica un file .CAP per iniziare l'analisi.")
        return

    # =====================================================
    # PARSING
    # =====================================================

    try:
        summary, ll_blocks = parse_file(uploaded_file)
    except Exception as error:
        st.error(
            f"Errore nella lettura del file LCM: {error}"
        )
        return

    if not summary:
        st.warning("Nessun evento Summary trovato nel file.")
        return

    # =====================================================
    # RICERCA
    # =====================================================

    search_text = st.text_input(
        "🔎 Cerca nella descrizione",
        placeholder="Inserisci una parola o parte della descrizione...",
        key="lcm_search_description"
    )

    filtered_summary = filter_summary(
        summary,
        search_text
    )

    if search_text.strip():
        st.caption(
            f"Trovati {len(filtered_summary)} eventi su {len(summary)}"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    render_summary(filtered_summary)

    if not filtered_summary:
        st.warning(
            "Nessun evento trovato nella descrizione."
        )
        return

    # =====================================================
    # SELEZIONE REC
    # =====================================================

    st.markdown("---")

    options = {}

    for row in filtered_summary:

        rec = int(row[0])
        description = str(row[-1]).strip()

        if description:
            label = f"REC {rec} — {description}"
        else:
            label = f"REC {rec}"

        options[label] = rec

    selected_label = st.selectbox(
        "Seleziona REC",
        list(options.keys()),
        key="lcm_selected_rec"
    )

    selected_rec = options[selected_label]

    ll_rows = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll_rows:
        st.warning(
            f"Nessun campione LL disponibile per REC {selected_rec}."
        )
        return

    # =====================================================
    # DESCRIZIONE
    # =====================================================

    selected_summary = next(
        (
            row
            for row in filtered_summary
            if int(row[0]) == selected_rec
        ),
        None
    )

    if selected_summary:

        description = str(
            selected_summary[-1]
        ).strip()

        if description:
            st.caption(
                f"Descrizione: {description}"
            )

    # =====================================================
    # TIMELINE
    # =====================================================

    max_index = len(ll_rows) - 1

    current_index = st.session_state.get(
        "lcm_current_index",
        0
    )

    if current_index > max_index:
        current_index = max_index

    current_index = st.slider(
        "⏱️ Timeline",
        min_value=0,
        max_value=max_index,
        value=current_index,
        key=f"lcm_timeline_{selected_rec}"
    )

    st.session_state["lcm_current_index"] = current_index

    # =====================================================
    # CAMPIONE CORRENTE
    # =====================================================

    current_row = ll_rows[current_index]

    states = decode_rec(
        current_row
    )

    st.markdown(
        f"""
        <div class="lcm-info">
            Campione:
            <b>{current_index + 1} / {len(ll_rows)}</b>
            &nbsp;&nbsp;&nbsp;
            N:
            <b>{current_row.get("N", "—")}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # DIGITALI - 7 COLONNE
    # =====================================================

    st.subheader("🔌 Segnali digitali")

    for row_start in range(
        0,
        len(DIGITAL_WORDS),
        7
    ):

        row_words = DIGITAL_WORDS[
            row_start:row_start + 7
        ]

        columns = st.columns(
            7,
            gap="small"
        )

        for column, word in zip(
            columns,
            row_words
        ):

            with column:
                render_word(
                    word,
                    states
                )

    # =====================================================
    # ANALOGICI
    # =====================================================

    st.markdown("---")

    st.subheader("📈 Segnali analogici")

    show_analogicals(
        current_row
    )


# =========================================================
# START
# =========================================================

def main():

    st.set_page_config(
        page_title="LCM",
        page_icon="⚡",
        layout="wide"
    )

    lcm_page()


if __name__ == "__main__":
    main()
