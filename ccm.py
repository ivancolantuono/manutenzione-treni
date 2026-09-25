import streamlit as st
import pandas as pd
import re
import html

MAX_FIELDS = 6

# =========================================================
# SEGNALI ANALOGICI
# =========================================================
# Aggiungi qui eventuali nuovi segnali analogici.
ANALOG_SIGNALS = [
    "vTVL", "vTV1", "iTA1M", "iTA2M", "iTA", "vTVI",
    "da1", "db1", "ta1", "tb1", "dfr", "tcha", "tchb",
    "vref", "Vref", "OVPD", "TOVPD", "vF", "dvF",
    "vL", "dvL", "vFdvf", "vLdvL",
]

# =========================================================
# PAROLE DIGITALI CCM
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
# DECODIFICA BIT
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

    "PHW4": {
        # Lasciato predisposto per i segnali PHW4.
        # Inserisci qui la decodifica quando disponibile.
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
# REGEX PARSER CCM
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
# DESCRIZIONE SUMMARY
# =========================================================
def split_description(desc):
    if " - " in desc:
        left, descrizione = desc.split(" - ", 1)
    else:
        left = desc
        descrizione = ""

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
# PARSER FILE
# =========================================================
def parse_file(uploaded_file):
    summary = []
    ll_blocks = {}

    current_rec = None
    in_ll = False
    columns = []

    raw = uploaded_file.getvalue()
    text = raw.decode("utf-8", errors="ignore")

    for line in text.splitlines():

        # -----------------------------
        # SUMMARY / REC
        # -----------------------------
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
            columns = []

            continue

        # -----------------------------
        # HEADER LL
        # -----------------------------
        if LL_HEADER_RE.match(line):
            columns = line.split()
            in_ll = True
            continue

        # -----------------------------
        # RIGA LL
        # -----------------------------
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
# DECODIFICA WORD
# =========================================================
def decode_word(hex_value, bit_map):

    try:
        value = int(str(hex_value), 16)
    except Exception:
        value = 0

    states = {}

    for bit, name in bit_map.items():

        if name == "-----":
            continue

        states[name] = (
            value >> bit
        ) & 1

    return states


# =========================================================
# CSS
# =========================================================
def load_css():

    st.markdown(
        """
        <style>

        /* ================================
           DIGITALI
           ================================ */

        .digital-title {
            font-size: 22px;
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 12px;
        }

        .digital-card {
            border: 1px solid #d7dce2;
            border-radius: 6px;
            background: white;
            overflow: hidden;
            margin-bottom: 7px;
        }

        .digital-card-title {
            background: #f4f6f8;
            border-bottom: 1px solid #d7dce2;
            padding: 6px 8px;
            font-size: 12px;
            font-weight: 700;
        }

        .digital-signal {
            height: 18px;
            line-height: 18px;
            padding: 0 7px;
            margin: 1px 2px;
            border-radius: 2px;
            background: #f0f0f0;
            color: #4d4d4d;
            font-size: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .digital-signal.on {
            background: #ffdfe2;
            color: #b40018;
            font-weight: 700;
            border-left: 3px solid #e0001b;
        }

        .digital-signal.on:before {
            content: "";
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #e0001b;
            margin-right: 5px;
        }

        .digital-signal.off:before {
            content: "";
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #d9c8eb;
            margin-right: 5px;
        }

        /* ================================
           ANALOGICI
           ================================ */

        .analog-title {
            font-size: 22px;
            font-weight: 700;
            margin-top: 18px;
            margin-bottom: 12px;
        }

        .analog-row {
            display: flex;
            align-items: center;
            gap: 10px;
            width: 100%;
            margin: 6px 0;
        }

        .analog-name {
            width: 75px;
            min-width: 75px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }

        .analog-value {
            width: 80px;
            min-width: 80px;
            font-family: Consolas, monospace;
            font-size: 13px;
            font-weight: bold;
            text-align: right;
            white-space: nowrap;
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
        unsafe_allow_html=True,
    )


# =========================================================
# SUMMARY
# =========================================================
def render_summary(df):

    st.markdown("### 📋 Summary")

    # UNA SOLA RICERCA
    search_text = st.text_input(
        "🔎 Cerca nella descrizione",
        placeholder="Parola o parte della descrizione...",
        key="ccm_search",
    )

    filtered = df.copy()

    if search_text.strip():

        filtered = filtered[
            filtered["DESCRIZIONE"]
            .fillna("")
            .astype(str)
            .str.contains(
                search_text.strip(),
                case=False,
                regex=False,
            )
        ].copy()

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        height=300,
    )

    return filtered


# =========================================================
# CARD DIGITALE
# =========================================================
def render_digital_card(word, row):

    if word not in BIT_MAP:
        return

    st.markdown(
        '<div class="digital-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="digital-card-title">'
        f'{html.escape(word)}'
        f'</div>',
        unsafe_allow_html=True,
    )

    states = decode_word(
        row.get(word, "0"),
        BIT_MAP[word],
    )

    for signal in BIT_MAP[word].values():

        if signal == "-----":
            continue

        active = states.get(signal, 0)

        cls = (
            "on"
            if active
            else "off"
        )

        st.markdown(
            f'<div class="digital-signal {cls}">'
            f'{html.escape(signal)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# SEGNALI DIGITALI
# =========================================================
def render_digital_signals(row):

    st.markdown(
        '<div class="digital-title">'
        '🔌 Segnali digitali'
        '</div>',
        unsafe_allow_html=True,
    )

    # 7 colonne
    cols = st.columns(
        7,
        gap="small",
    )

    for i, word in enumerate(DIGITAL_WORDS):

        with cols[i % 7]:
            render_digital_card(
                word,
                row,
            )


# =========================================================
# SEGNALI ANALOGICI - BARRA
# =========================================================
def render_analog_signals(row):

    st.markdown(
        '<div class="analog-title">'
        '📈 Segnali analogici'
        '</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # Fondo scala grafico
    # -----------------------------------------------------
    # Questi valori servono SOLTANTO a dimensionare
    # graficamente la barra.
    # Non sono soglie tecniche del CCM.
    ANALOG_MAX = {

        "vTVL": 5000,
        "vTV1": 5000,
        "iTA1M": 100,
        "iTA2M": 100,
        "iTA": 100,
        "vTVI": 5000,

        "da1": 100,
        "db1": 100,

        "ta1": 100,
        "tb1": 100,

        "dfr": 100,

        "tcha": 100,
        "tchb": 100,

        "vref": 100,
        "Vref": 100,

        "OVPD": 5000,
        "TOVPD": 100,

        "vF": 5000,
        "dvF": 5000,

        "vL": 5000,
        "dvL": 5000,

        "vFdvf": 5000,
        "vLdvL": 5000,
    }

    # -----------------------------------------------------
    # Rendering
    # -----------------------------------------------------
    for sig in ANALOG_SIGNALS:

        raw_value = row.get(
            sig,
            "",
        )

        # -----------------------------
        # Valore
        # -----------------------------
        if (
            raw_value is None
            or str(raw_value).strip() == ""
        ):
            value_text = "—"
            numeric_value = None

        else:

            value_text = str(
                raw_value
            )

            try:
                numeric_value = float(
                    str(raw_value)
                    .replace(",", ".")
                )

            except Exception:
                numeric_value = None

        # -----------------------------
        # Percentuale barra
        # -----------------------------
        max_value = ANALOG_MAX.get(
            sig,
            100,
        )

        if (
            numeric_value is not None
            and max_value > 0
        ):

            percentage = (
                abs(numeric_value)
                / max_value
                * 100
            )

            percentage = min(
                max(
                    percentage,
                    0,
                ),
                100,
            )

        else:
            percentage = 0

        # -----------------------------
        # HTML
        # -----------------------------
        st.markdown(
            f"""
            <div class="analog-row">

                <div class="analog-name">
                    {html.escape(str(sig))}
                </div>

                <div class="analog-value">
                    {html.escape(value_text)}
                </div>

                <div class="analog-track">

                    <div
                        class="analog-fill"
                        style="width:{percentage:.1f}%;">
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# PAGINA CCM
# =========================================================
def ccm_page():

    load_css()

    st.title(
        "⚡ Analisi CCM"
    )

    # =====================================================
    # UPLOAD
    # =====================================================
    uploaded_file = st.file_uploader(
        "Apri file CCM",
        type=["CAP", "cap"],
        key="ccm_file",
    )

    if uploaded_file is None:

        st.info(
            "Carica un file .CAP per iniziare."
        )

        return

    # =====================================================
    # IDENTIFICAZIONE FILE
    # =====================================================
    signature = (
        uploaded_file.name,
        uploaded_file.size,
    )

    if (
        st.session_state.get(
            "ccm_signature"
        )
        != signature
    ):

        try:

            summary, ll_blocks = parse_file(
                uploaded_file
            )

        except Exception as exc:

            st.error(
                f"Errore nella lettura del CCM: {exc}"
            )

            return

        st.session_state.ccm_signature = signature
        st.session_state.ccm_summary = summary
        st.session_state.ccm_ll_blocks = ll_blocks
        st.session_state.ccm_selected_rec = None

    summary = st.session_state.get(
        "ccm_summary",
        [],
    )

    ll_blocks = st.session_state.get(
        "ccm_ll_blocks",
        {},
    )

    # =====================================================
    # CONTROLLO SUMMARY
    # =====================================================
    if not summary:

        st.error(
            "Nessun Summary trovato nel file."
        )

        return

    # =====================================================
    # DATAFRAME SUMMARY
    # =====================================================
    columns = (
        ["REC", "CODE", "DATE", "TIME"]
        + [
            f"F{i+1}"
            for i in range(MAX_FIELDS)
        ]
        + ["DESCRIZIONE"]
    )

    df = pd.DataFrame(
        summary,
        columns=columns,
    )

    # =====================================================
    # SUMMARY + RICERCA
    # =====================================================
    filtered = render_summary(df)

    if filtered.empty:

        st.warning(
            "Nessun REC corrisponde alla ricerca."
        )

        return

    st.divider()

    # =====================================================
    # SELEZIONE REC
    # =====================================================
    recs = filtered["REC"].tolist()

    old_rec = st.session_state.get(
        "ccm_selected_rec"
    )

    if old_rec in recs:
        default_index = recs.index(
            old_rec
        )
    else:
        default_index = 0

    selected_rec = st.selectbox(
        "REC da analizzare",
        recs,
        index=default_index,
        format_func=lambda x:
            f"REC {x}",
        key="ccm_rec",
    )

    st.session_state.ccm_selected_rec = (
        selected_rec
    )

    # =====================================================
    # DESCRIZIONE
    # =====================================================
    selected_summary = filtered[
        filtered["REC"] == selected_rec
    ].iloc[0]

    descrizione = str(
        selected_summary.get(
            "DESCRIZIONE",
            "",
        )
    )

    st.markdown(
        f"**REC {selected_rec} — "
        f"{html.escape(descrizione)}**"
    )

    # =====================================================
    # LL
    # =====================================================
    ll = ll_blocks.get(
        int(selected_rec),
        [],
    )

    if not ll:

        st.warning(
            f"Nessuna LL disponibile per REC "
            f"{selected_rec}."
        )

        return

    total = len(ll)

    # =====================================================
    # TIMELINE
    # =====================================================
    index_key = (
        f"ccm_index_{selected_rec}"
    )

    current = int(
        st.session_state.get(
            index_key,
            0,
        )
    )

    current = min(
        max(
            current,
            0,
        ),
        total - 1,
    )

    new_index = st.slider(
        "Timeline",
        min_value=0,
        max_value=max(
            0,
            total - 1,
        ),
        value=current,
        key=f"ccm_timeline_{selected_rec}",
    )

    st.session_state[index_key] = (
        new_index
    )

    # =====================================================
    # RIGA ATTUALE
    # =====================================================
    row = ll[new_index]

    st.caption(
        f"Campione: {new_index + 1} / {total}"
        f"   |   N: {row.get('N', '—')}"
    )

    # =====================================================
    # DIGITALI
    # =====================================================
    render_digital_signals(
        row
    )

    st.divider()

    # =====================================================
    # ANALOGICI
    # =====================================================
    render_analog_signals(
        row
    )


# =========================================================
# AVVIO DIRETTO
# =========================================================
if __name__ == "__main__":
    ccm_page()
