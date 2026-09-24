import streamlit as st
import pandas as pd
import re


# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================

st.set_page_config(
    page_title="CCM - Analisi",
    page_icon="🔌",
    layout="wide"
)


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
# ORDINE DEI WORD DIGITALI
# ============================================================

WORD_LIST = [
    "sCCa",
    "PSWA",
    "PSWB",
    "PHW1",
    "PHW2",
    "PHW3",
    "PHW4",
    "flcom",
    "stdi",
    "PCUc",
    "msf",
    "stdo",
    "PCUs",
]


# ============================================================
# MAPPATURA BIT
# ============================================================

BIT_MAP = {

    # --------------------------------------------------------
    # sCCa
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PSWA
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PSWB
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PHW1
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PHW2
    # --------------------------------------------------------

    "PHW2": {
        0: "earthfault",
    },

    # --------------------------------------------------------
    # PHW3
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PHW4
    # --------------------------------------------------------

    "PHW4": {},

    # --------------------------------------------------------
    # flcom
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # stdi
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # stdo
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PCUc
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PCUs
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # msf
    # --------------------------------------------------------

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
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ------------------------------------------------------
       TITOLO
    ------------------------------------------------------ */

    .ccm-section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 12px;
    }

    /* ------------------------------------------------------
       CARD WORD
    ------------------------------------------------------ */

    .ccm-card {
        border: 1px solid #d8dde5;
        border-radius: 7px;
        background: white;
        margin-bottom: 8px;
        overflow: hidden;
    }

    .ccm-card-title {
        background: #f5f7fa;
        border-bottom: 1px solid #d8dde5;
        padding: 7px 9px;
        font-size: 14px;
        font-weight: 700;
        color: #172033;
    }

    /* ------------------------------------------------------
       SEGNALE OFF
    ------------------------------------------------------ */

    .ccm-signal-off {
        height: 21px;
        line-height: 21px;
        margin: 2px 4px;
        padding: 0 7px;
        border-radius: 3px;
        background: #f1f1f1;
        color: #777;
        font-size: 11px;
        border-left: 3px solid #d7d7d7;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ------------------------------------------------------
       SEGNALE ON
    ------------------------------------------------------ */

    .ccm-signal-on {
        height: 21px;
        line-height: 21px;
        margin: 2px 4px;
        padding: 0 7px;
        border-radius: 3px;
        background: #ffe1e1;
        color: #c40000;
        font-size: 11px;
        font-weight: 700;
        border-left: 3px solid #e00000;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ------------------------------------------------------
       ANALOGICO
    ------------------------------------------------------ */

    .ccm-analog-card {
        border: 1px solid #d8dde5;
        border-radius: 7px;
        background: white;
        padding: 10px 12px;
        text-align: center;
    }

    .ccm-analog-name {
        font-size: 12px;
        color: #666;
        margin-bottom: 5px;
    }

    .ccm-analog-value {
        font-size: 19px;
        font-weight: 700;
        color: #172033;
    }

    /* ------------------------------------------------------
       SUMMARY
    ------------------------------------------------------ */

    .ccm-info {
        border: 1px solid #d8dde5;
        border-radius: 7px;
        padding: 10px 14px;
        background: #f8fafc;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DECODIFICA WORD
# ============================================================

def decode_word(hex_value, bit_map):

    try:
        value = int(str(hex_value), 16)
    except Exception:
        value = 0

    states = {}

    for bit, name in bit_map.items():

        if name == "-----":
            continue

        states[name] = (value >> bit) & 1

    return states


# ============================================================
# DECODIFICA RECORD
# ============================================================

def decode_rec(rec_row):

    states = {}

    for word in WORD_LIST:

        if word in BIT_MAP and word in rec_row:

            decoded = decode_word(
                rec_row[word],
                BIT_MAP[word]
            )

            states.update(decoded)

    return states


# ============================================================
# REGEX PARSER
# ============================================================

SM_RE = re.compile(
    r"^Rec:\s+(\d+)\s+"
    r"Code:\s+([0-9A-Fa-f]+)\s+"
    r"Date:(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{2}:\d{2}:\d{2}\.\d{2})"
    r"\s+-\s+(.*)$"
)

LL_HEADER_RE = re.compile(
    r"^\s*N\.\s+"
)

LL_ROW_RE = re.compile(
    r"^\s*(-?\d+)\s+(.*)$"
)


# ============================================================
# SEPARAZIONE DESCRIZIONE
# ============================================================

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


# ============================================================
# PARSER FILE CAP
# ============================================================

def parse_file(uploaded_file):

    summary = []

    ll_blocks = {}

    current_rec = None

    in_ll = False

    columns = []

    try:

        content = uploaded_file.read()

        if isinstance(content, bytes):

            text = content.decode(
                "utf-8",
                errors="ignore"
            )

        else:

            text = content

        lines = text.splitlines()

    except Exception as e:

        st.error(
            f"Errore nella lettura del file: {e}"
        )

        return [], {}


    for line in lines:

        # ----------------------------------------------------
        # NUOVO RECORD SUMMARY
        # ----------------------------------------------------

        m = SM_RE.match(line)

        if m:

            rec = int(m.group(1))

            code = m.group(2)

            date = m.group(3)

            time = m.group(4)

            desc = m.group(5)

            fields, descrizione = split_description(
                desc
            )

            summary.append(
                [
                    rec,
                    code,
                    date,
                    time
                ]
                +
                fields
                +
                [descrizione]
            )

            ll_blocks[rec] = []

            current_rec = rec

            in_ll = False

            columns = []

            continue


        # ----------------------------------------------------
        # HEADER LL
        # ----------------------------------------------------

        if LL_HEADER_RE.match(line):

            columns = line.split()

            in_ll = True

            continue


        # ----------------------------------------------------
        # RIGA LL
        # ----------------------------------------------------

        if in_ll and current_rec is not None:

            m = LL_ROW_RE.match(line)

            if not m:
                continue

            try:

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

            except Exception:
                continue


    return summary, ll_blocks


# ============================================================
# MOSTRA SEGNALE DIGITALE
# ============================================================

def render_signal(name, value):

    if value:

        st.markdown(
            f"""
            <div class="ccm-signal-on">
                🔴 {name}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="ccm-signal-off">
                🟣 {name}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# MOSTRA WORD DIGITALE
# ============================================================

def render_word_card(word, states):

    if word not in BIT_MAP:
        return

    signals = [
        name
        for name in BIT_MAP[word].values()
        if name != "-----"
    ]

    if not signals:
        return

    st.markdown(
        f"""
        <div class="ccm-card">
            <div class="ccm-card-title">
                {word}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Le righe vengono messe subito sotto il titolo.
    # Usiamo HTML per evitare spazi enormi tra i segnali.

    html = ""

    for name in signals:

        value = states.get(
            name,
            0
        )

        if value:

            html += f"""
            <div class="ccm-signal-on">
                🔴 {name}
            </div>
            """

        else:

            html += f"""
            <div class="ccm-signal-off">
                🟣 {name}
            </div>
            """

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# MOSTRA CARD WORD COMPLETA
# ============================================================

def render_word(word, states):

    if word not in BIT_MAP:
        return

    signals = [
        name
        for name in BIT_MAP[word].values()
        if name != "-----"
    ]

    if not signals:
        return

    html = f"""
    <div class="ccm-card">

        <div class="ccm-card-title">
            {word}
        </div>
    """

    for name in signals:

        value = states.get(
            name,
            0
        )

        if value:

            html += f"""
            <div class="ccm-signal-on">
                🔴 {name}
            </div>
            """

        else:

            html += f"""
            <div class="ccm-signal-off">
                🟣 {name}
            </div>
            """

    html += "</div>"

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# MOSTRA ANALOGICI
# ============================================================

def render_analog(row):

    st.markdown(
        """
        <div class="ccm-section-title">
            📈 Segnali analogici
        </div>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(
        len(ANALOG_SIGNALS),
        gap="small"
    )

    for col, signal in zip(
        cols,
        ANALOG_SIGNALS
    ):

        value = row.get(
            signal,
            "—"
        )

        with col:

            st.markdown(
                f"""
                <div class="ccm-analog-card">

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


# ============================================================
# SUMMARY
# ============================================================

def render_summary(summary):

    st.markdown(
        """
        <div class="ccm-section-title">
            📋 CCM Summary
        </div>
        """,
        unsafe_allow_html=True
    )

    columns = (
        ["REC", "CODE", "DATE", "TIME"]
        +
        [f"F{i+1}" for i in range(MAX_FIELDS)]
        +
        ["DESCRIZIONE"]
    )

    df = pd.DataFrame(
        summary,
        columns=columns
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=350
    )

    return df


# ============================================================
# ANALISI REC
# ============================================================

def render_analysis(
    summary,
    ll_blocks
):

    # --------------------------------------------------------
    # SELEZIONE REC
    # --------------------------------------------------------

    rec_list = [
        row[0]
        for row in summary
    ]

    selected_rec = st.selectbox(
        "Seleziona il REC da analizzare",
        rec_list,
        format_func=lambda x: (
            f"REC {x}"
        )
    )

    # --------------------------------------------------------
    # INFORMAZIONI REC
    # --------------------------------------------------------

    summary_row = next(
        (
            row
            for row in summary
            if row[0] == selected_rec
        ),
        None
    )

    if summary_row is None:
        return

    code = summary_row[1]

    date = summary_row[2]

    time = summary_row[3]

    descrizione = summary_row[-1]

    st.markdown(
        f"""
        <div class="ccm-info">

            <b>REC:</b> {selected_rec}
            &nbsp;&nbsp;&nbsp;

            <b>CODE:</b> {code}
            &nbsp;&nbsp;&nbsp;

            <b>DATA:</b> {date}
            &nbsp;&nbsp;&nbsp;

            <b>ORA:</b> {time}

            <br>

            <b>Descrizione:</b>
            {descrizione}

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LL
    # --------------------------------------------------------

    ll = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll:

        st.warning(
            f"Nessuna LL disponibile per REC {selected_rec}."
        )

        return

    # --------------------------------------------------------
    # TIMELINE
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="ccm-section-title">
            ⏱️ Timeline
        </div>
        """,
        unsafe_allow_html=True
    )

    max_index = len(ll) - 1

    index = st.slider(
        "Campione",
        min_value=0,
        max_value=max_index,
        value=0,
        step=1,
        label_visibility="collapsed"
    )

    row = ll[index]

    st.markdown(
        f"""
        **Campione:** {index + 1} / {len(ll)}

        **N:** {row.get("N", "—")}
        """,
    )

    # --------------------------------------------------------
    # DECODIFICA
    # --------------------------------------------------------

    states = decode_rec(row)

    # --------------------------------------------------------
    # DIGITALI
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="ccm-section-title">
            🔌 Segnali digitali
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # 4 COLONNE
    # --------------------------------------------------------

    digital_words = [
        word
        for word in WORD_LIST
        if word in BIT_MAP
        and any(
            name != "-----"
            for name in BIT_MAP[word].values()
        )
    ]

    columns = st.columns(
        4,
        gap="small"
    )

    for i, word in enumerate(
        digital_words
    ):

        col = columns[
            i % 4
        ]

        with col:

            render_word(
                word,
                states
            )

    # --------------------------------------------------------
    # ANALOGICI
    # --------------------------------------------------------

    st.divider()

    render_analog(row)


# ============================================================
# APPLICAZIONE PRINCIPALE
# ============================================================

def main():

    st.title(
        "🔌 Analisi CCM"
    )

    st.caption(
        "Analisi dei file CCM / CAP"
    )

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "📂 Carica file CCM",
        type=[
            "CAP",
            "cap",
            "txt"
        ],
        key="ccm_file"
    )

    if uploaded_file is None:

        st.info(
            "Carica un file CCM (.CAP) per iniziare."
        )

        return

    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    summary, ll_blocks = parse_file(
        uploaded_file
    )

    if not summary:

        st.error(
            "Nessun Summary CCM trovato nel file."
        )

        return

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    render_summary(
        summary
    )

    st.divider()

    # --------------------------------------------------------
    # ANALISI
    # --------------------------------------------------------

    render_analysis(
        summary,
        ll_blocks
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
