import re

import streamlit as st
import pandas as pd
import html

MAX_FIELDS = 6

ANALOG_SIGNALS = ["vLIN", "vFIL", "Vel", "Vref", "fmRef", "fm1", "fm1s", "Imot", "Irif", "iLIN", "Paps", "RifM", "RifF", "RifH", "CpAsk", "Reo",]

WORD_LIST = [
    "sTCa", "sTCb", "sTCc", "sTCd",
    "cPCUa", "cPCUb",
    "cWa", "cWb", "cWc", "cWd", "cWe",
    "PH1", "PH2", "PH3", "PH4"
]

BIT_MAP = {
    "sTCa": {
        0:"ivok",1:"Test",2:"chokLed",3:"afchLed",4:"fasind",5:"pkav",6:"edbOff",7:"edbFault",
        8:"EPNullTrain",9:"fwd",10:"safetyBrk",11:"dirdec",12:"autoEsclTcu",13:"sfioLed",14:"pswTripLine",15:"bkwd"},
    "sTCb": {
        0:"back",1:"backFil",2:"AskExtEsclTacu",3:"clLoop",4:"Stopping",5:"WSP_Hold",6:"TripLineClose",7:"WSP_Vent",
        8:"velNull",9:"CopNull",10:"vFilNull",11:"-------",12:"slidErrLatch",13:"PropCutOutOIE",14:"fluxRiag",15:"delfuxEnd"},
    "sTCc": {
        0:"koswtcu",1:"slideErr",2:"edbOffFre",3:"RidCoppia",4:"civcHW",5:"vFOK",6:"sliTra",7:"patMot",
        8:"rising",9:"pswTripLine",10:"tcuOff",11:"WSP_OK",12:"civc",13:"cch",14:"apTripLine",15:"civl"},
    "sTCd": {
        0:"venton_A",1:"venton_B",2:"dvf",3:"InParkingMode",4:"scaFil",5:"HILactive",6:"PotLin1",7:"PotLin2",
        8:"UseOptSSctrl",9:"WSPedbOff",10:"-----",11:"-----",12:"-----",13:"-----",14:"-----",15:"-----"},
    "cWa": {
        0:"errcom",1:"LineOverCurrent",2:"PCUko",3:"-----",4:"-----",5:"-----",6:"GEWko",7:"pwGoodKo",
        8:"svfProl",9:"-----",10:"avAIPk1",11:"-----",12:"erSeqFas",13:"erDirPK",14:"-----",15:"errHW"},
    "cWb": {
        0:"-----",1:"ccTripLine",2:"BCUDigFail",3:"slidErrLatch",4:"pcuEsclTcu",5:"VFHIGHPerm",6:"-----",7:"DlerrCode",
        8:"DOFailure",9:"blkTripLine",10:"-----",11:"-----",12:"-----",13:"-----",14:"chReoKO",15:"hotReo"},
    "cWc": {
        0:"-----",1:"-----",2:"-----",3:"-----",4:"-----",5:"PhaseRFail",6:"PhaseSFail",7:"PhaseTFail",8:"koTVF",9:"-----",
        10:"-----",11:"-----",12:"MaxMotMechFreq",13:"Overspeed",14:"-----",15:"hotMot"},
    "cWd": {
        0:"dprbusKo",1:"koTAR",2:"koTAS",3:"koTAT",4:"pkFail1",5:"WSPedbOff",6:"PropCutOutKo",7:"-----",
        8:"-----",9:"diagAtt",10:"-----",11:"-----",12:"diagPerm",13:"-----",14:"hotHeatSink",15:"hotThAir"},
    "cWe": {
        0:"-----",1:"koAllThlGbt",2:"koThAir",3:"koThHeatSink",4:"HotThHeatSinkLong",5:"-----",6:"-----",7:"-----",
        8:"-----",9:"-----",10:"-----",11:"-----",12:"-----",13:"koThM1",14:"-----",15:"-----"},
    "PH1": {
        0:"-----",1:"-----",2:"-----",3:"-----",4:"-----",5:"-----",6:"-----",7:"SCMiR",8:"SCMiT",
        9:"-----",10:"-----",11:"-----",12:"SCMiS",13:"-----",14:"-----",15:"-----"},
    "PH2": {
        0:"-----",1:"-----",2:"-----",3:"-----",4:"-----",5:"-----",6:"SVF2",7:"-----",8:"-----",
        9:"-----",10:"-----",11:"-----",12:"-----",13:"-----",14:"-----",15:"-----"},
    "PH3": {
        0:"DiaR_UP",1:"DiaS_UP",2:"DiaT_UP",3:"DiaCH_UP",4:"-----",5:"DiaR_DWN",6:"DiaS_DWN",7:"DiaT_DWN",8:"CH_DW",
        9:"VUOTO",10:"VUOTO",11:"VUOTO",12:"VUOTO",13:"VUOTO",14:"VUOTO",15:"VUOTO"},
    "PH4": {
        0:"SBF",1:"-----",2:"-----",3:"PG1",4:"-----",5:"ALPK1KO",6:"-----",7:"-----",
        8:"-----",9:"-----",10:"-----",11:"-----",12:"-----",13:"-----",14:"-----",15:"-----"},
    "cPCUa": {
        0:"PropCutOut",1:"startMCM",2:"trz",3:"frn",4:"av",5:"ind",6:"FremCCU",7:"VUOTO",8:"Stopping",
        9:"setHil",10:"ComDescarge",11:"CalWhDiam",12:"UseOptSSCtrl",13:"inibRecup",14:"PcuMisReoOK",15:"inibBraking"},
    "cPCUb": {
        0:"lin25Kv",1:"lin15kv",2:"lin3kv",3:"EscTCU",4:"PrtSd",5:"FstSd",6:"SftSd",7:"PrtBlk",8:"SftBlk",
        9:"boostActive",10:"VUOTO",11:"VUOTO",12:"VUOTO",13:"VUOTO",14:"VUOTO",15:"VUOTO"},
}

SM_RE = re.compile(r"^Rec:\s+(\d+)\s+Code:\s+([0-9A-Fa-f]+)\s+Date:(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2}\.\d{2})\s+-\s+(.*)$")
LL_HEADER_RE = re.compile(r"^\s*N\.\s+")
LL_ROW_RE = re.compile(r"^\s*(-?\d+)\s+(.*)$")

def decode_word(hex_value, bit_map):
    try:
        value = int(hex_value, 16)
    except Exception:
        value = 0
    return {name: (value >> bit) & 1 for bit, name in bit_map.items()}

def decode_rec(rec_row):
    states = {}
    for word in WORD_LIST:
        if word in BIT_MAP and word in rec_row:
            states.update(decode_word(rec_row[word], BIT_MAP[word]))
    return states

def split_description(desc):
    descrizione = ""
    if " - " in desc:
        left, descrizione = desc.split(" - ", 1)
    else:
        left = desc
    fields = [p.strip() for p in left.split(";") if p.strip()]
    fields = fields[:MAX_FIELDS]
    while len(fields) < MAX_FIELDS:
        fields.append("")
    return fields, descrizione.strip()

def parse_text(text):
    summary = []
    ll_blocks = {}
    current_rec = None
    in_ll = False
    columns = []

    for line in text.splitlines():
        m = SM_RE.match(line)
        if m:
            rec = int(m.group(1))
            code = m.group(2)
            date = m.group(3)
            time = m.group(4)
            desc = m.group(5)
            fields, descrizione = split_description(desc)
            summary.append([rec, code, date, time] + fields + [descrizione])
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
            row = {"N": int(m.group(1))}
            for i, col in enumerate(columns[1:]):
                row[col] = values[i]
            ll_blocks[current_rec].append(row)

    return summary, ll_blocks

DIGITAL_GROUPS = [
    ["sTCa", "sTCb", "sTCc", "sTCd", "PH1", "PH2", "cPCUa"],
    ["cWa", "cWb", "cWc", "cWd", "cWe", "PH3", "cPCUb"],
]

# Descrizioni iniziali: volutamente conservative; i nomi ufficiali possono essere
# aggiornati in seguito senza toccare la decodifica.
DIGITAL_DESCRIPTIONS = {
    "ivok": "IV OK",
    "Test": "Test",
    "chokLed": "CH OK",
    "afchLed": "AFCH",
    "fasind": "Indicazione fascia",
    "edbOff": "EDB OFF",
    "edbFault": "Guasto EDB",
    "safetyBrk": "Freno di sicurezza",
    "pswTripLine": "Trip linea",
    "Stopping": "Arresto",
    "WSP_Hold": "WSP Hold",
    "WSP_Vent": "WSP Vent",
    "velNull": "Velocità nulla",
    "WSP_OK": "WSP OK",
    "venton_A": "Ventilazione A ON",
    "venton_B": "Ventilazione B ON",
    "LineOverCurrent": "Sovracorrente linea",
    "CCUEthKo": "Errore comunicazione CCU Ethernet",
    "GEWko": "GEW non OK",
    "pwGood": "Power Good",
    "PhaseRFail": "Guasto fase R",
    "PhaseSFail": "Guasto fase S",
    "PhaseTFail": "Guasto fase T",
    "Overspeed": "Sovravelocità",
    "hotMot": "Motore caldo",
    "hotHeatSink": "Heatsink caldo",
    "hotThAir": "Aria termica calda",
    "koThAir": "Guasto temperatura aria",
    "koThHeatSink": "Guasto temperatura heatsink",
    "SCMiR": "SCM fase R",
    "SCMiS": "SCM fase S",
    "SCMiT": "SCM fase T",
    "SVF2": "SVF2",
    "PropCutOut": "Propulsione esclusa",
    "startMCM": "Avvio MCM",
    "Stopping": "Arresto",
    "PcuMisReoOK": "PCU misure/recupero OK",
    "lin25Kv": "Linea 25 kV",
    "lin15kv": "Linea 15 kV",
    "lin3kv": "Linea 3 kV",
}

ANALOG_MAX = {
    "vLIN": 5000,
    "vFIL": 5000,
    "Vel": 500,
    "fmRef": 500,
    "fm1": 500,
    "fm1s": 500,
    "Imot": 1000,
}

def _css():
    st.markdown("""
    <style>

    /* =====================================================
       CARD MCM - stesso stile grafico del CCM
       ===================================================== */

    .ccm-word {
        border: 1px solid #d8dce2;
        border-radius: 5px;
        overflow: hidden;
        background: white;
        margin-bottom: 6px;
    }

    .ccm-title {
        font-size: 13px;
        font-weight: 700;
        padding: 6px 8px;
        background: #f7f8fa;
        border-bottom: 1px solid #ddd;
        margin-bottom: 3px;
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

    /* =====================================================
       ANALOGICI
       ===================================================== */

    .analog-row {
        display: flex;
        align-items: center;
        width: 100%;
        margin: 5px 0;
        gap: 10px;
    }

    .analog-name {
        width: 60px;
        min-width: 60px;
        font-size: 12px;
        font-weight: 600;
    }

    .analog-value {
        width: 85px;
        min-width: 85px;
        text-align: right;
        font-family: Consolas, monospace;
        font-size: 12px;
        font-weight: bold;
    }

    .analog-track {
        flex: 1;
        height: 13px;
        background: #eee;
        border: 1px solid #d0d0d0;
        border-radius: 7px;
        overflow: hidden;
    }

    .analog-fill {
        height: 100%;
        background: #7b61a8;
        border-radius: 7px;
    }

    </style>
    """, unsafe_allow_html=True)


def render_word(word, states):
    """
    Visualizzazione MCM identica al renderer grafico CCM.
    La decodifica BIT_MAP e gli stati non vengono modificati.
    """

    signals = BIT_MAP.get(word, {})

    if not signals:
        return

    html_parts = [
        '<div class="ccm-word">',
        f'<div class="ccm-title">{html.escape(word)}</div>'
    ]

    for bit, signal in signals.items():

        # Non mostrare placeholder / bit vuoti
        if signal in {"VUOTO", "-------", "-----"}:
            continue

        value = states.get(signal, 0)

        if value:
            css_class = "ccm-on"
            led_class = "ccm-led-on"
        else:
            css_class = "ccm-off"
            led_class = "ccm-led-off"

        description = DIGITAL_DESCRIPTIONS.get(signal, "")

        html_parts.append(
            f'<div class="ccm-signal {css_class}" '
            f'title="{html.escape(description)}">'
            f'<span class="ccm-led {led_class}"></span>'
            f'{html.escape(signal)}'
            f'</div>'
        )

    html_parts.append("</div>")

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)


def render_digitals(states):
    st.subheader("🔌 Segnali digitali")
    for group in DIGITAL_GROUPS:
        cols = st.columns(7, gap="small")
        for col, word in zip(cols, group):
            with col:
                render_word(word, states)

def render_analogicals(row):
    st.subheader("📈 Segnali analogici")
    for signal in ANALOG_SIGNALS:
        raw = row.get(signal, "")
        text = "—" if raw in ("", None) else str(raw)
        try:
            num = float(str(raw).replace(",", "."))
        except Exception:
            num = None
        maxv = ANALOG_MAX.get(signal, 100)
        pct = 0 if num is None else min(max(abs(num) / maxv * 100, 0), 100)
        st.markdown(
            f"""<div class="analog-row">
<div class="analog-name">{html.escape(signal)}</div>
<div class="analog-value">{html.escape(text)}</div>
<div class="analog-track"><div class="analog-fill" style="width:{pct:.1f}%;"></div></div>
</div>""",
            unsafe_allow_html=True,
        )

def mcm_page():
    _css()
    st.title("MCM")

    uploaded = st.file_uploader("Carica file MCM (.CAP)", type=["CAP","cap"], key="mcm_file")
    if uploaded is None:
        st.info("Carica un file MCM per iniziare l'analisi.")
        return

    try:
        text = uploaded.getvalue().decode("utf-8", errors="ignore")
        summary, ll_blocks = parse_text(text)
    except Exception as e:
        st.error(f"Errore durante la lettura del file: {e}")
        return

    if not summary:
        st.warning("Nessun Summary trovato nel file.")
        return

    columns = ["REC","CODE","DATE","TIME"] + [f"F{i+1}" for i in range(MAX_FIELDS)] + ["DESCRIZIONE"]
    df = pd.DataFrame(summary, columns=columns)

    st.subheader("📋 Summary")
    search = st.text_input("🔎 Cerca nella descrizione", key="mcm_summary_search")
    filtered = df
    if search.strip():
        filtered = df[df["DESCRIZIONE"].astype(str).str.contains(search.strip(), case=False, na=False)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    if filtered.empty:
        st.info("Nessun record corrisponde alla ricerca.")
        return

    options = filtered["REC"].tolist()
    selected = st.selectbox(
        "Seleziona REC",
        options,
        format_func=lambda r: f"REC {r} — {str(df.loc[df['REC']==r,'DESCRIZIONE'].iloc[0])}",
        key="mcm_selected_rec",
    )

    ll = ll_blocks.get(int(selected), [])
    if not ll:
        st.warning(f"Nessuna LL disponibile per REC {selected}.")
        return

    st.subheader(f"REC {selected}")
    idx = st.slider("Timeline", 0, len(ll)-1, 0, key=f"mcm_timeline_{selected}")
    row = ll[idx]
    states = decode_rec(row)

    st.caption(f"N = {row.get('N','')}  |  Campione {idx+1} / {len(ll)}")
    render_digitals(states)
    render_analogicals(row)

if __name__ == "__main__":
    import pandas as pd
    mcm_page()
