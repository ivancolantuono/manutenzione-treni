import streamlit as st
import pandas as pd
import re
import html

MAX_FIELDS = 6

# Aggiungi qui i segnali analogici che vuoi visualizzare.
ANALOG_SIGNALS = [
    "vTVL", "vTV1", "iTA1M", "iTA2M", "iTA", "vTVI",
    "da1", "db1", "ta1", "tb1", "dfr", "tcha", "tchb",
    "vref", "Vref", "OVPD", "TOVPD", "vF", "dvF",
    "vL", "dvL", "vFdvf", "vLdvL",
]

DIGITAL_WORDS = [
    "sCCa", "PSWA", "PSWB", "PHW1", "PHW2", "PHW3", "PHW4",
    "flcom", "stdi", "stdo", "PCUc", "PCUs", "msf",
]

BIT_MAP = {
    "sCCa": {
        0:"Test",1:"c2qok",2:"chAok",3:"chBokw",4:"abPhw",5:"civc",
        6:"pwm2q",7:"my_dspok",8:"anticipoTT",9:"3KON",10:"SCAR2Q",
        11:"okThCHPIND1",12:"okThCHPIND2",13:"okThINTAIR",
        14:"okThHEATSINK",15:"parzCCon"},
    "PSWA": {
        0:"UNDERVOLTPRIM3K",1:"CHPIND1_HOT",2:"CHPIND2_HOT",3:"INTAIR_HOT",
        4:"HEATSINK_HOT",5:"koThCHPIND1",6:"koThCHPIND2",7:"koThINTAIR",
        8:"koThHEATSINK",9:"PcuKO",10:"pswCHPIND1_HOTMAX",
        11:"pswUNDERVOLTPRIM",12:"pswTV1SUPERV",13:"pswCHPIND2_HOTMAX",
        14:"pswUNDERVOLTSEC",15:"pswTVISUPERV"},
    "PSWB": {
        0:"pswINTAIR_HOTMAX",1:"pswUNBASUPERV",2:"pswTA1SUPERV",
        3:"pswTA2SUPERV",4:"UNDERVOLTLINE3K",5:"EARTHFAULT",
        6:"DISCHA_FAIL",7:"HEATSINK_HOTMAX",8:"COMPVTVIMCM1",
        9:"TASUPERV",10:"CCMESCL",11:"CHARGESUPERV",12:"OVPRESHOT",
        13:"TEMPSCHEDHOT",14:"UNDERVOLTLINE",15:"CIDko"},
    "PHW1": {
        0:"-----",1:"VLDC",2:"TVI",3:"-----",4:"-----",5:"-----",
        6:"-----",7:"TA1",8:"TA2",9:"TA",10:"TV1",11:"-----",
        12:"-----",13:"-----",14:"-----",15:"-----"},
    "PHW2": {0:"earthfault"},
    "PHW3": {
        0:"DiaUp1",1:"DiaUp2",2:"DiaUp3",3:"DiaUp4",4:"DiaUp5",
        5:"DiaDown1",6:"DiaDown2",7:"DiaDown3",8:"DiaDown4",9:"DiaDown5",
        10:"-----",11:"-----",12:"-----",13:"-----",14:"-----",15:"-----"},
    "PHW4": {},
    "flcom": {
        0:"euroDC",1:"euroAC",2:"Bianco",3:"linea3k",4:"kv1_5",5:"chfresc",
        6:"cllon",7:"mant",8:"scafil2Q",9:"scafilOVP",10:"PrtSd",
        11:"FstSd",12:"SftSd",13:"PrtBlk",14:"testCID",15:"trNeutro"},
    "stdi": {
        0:"copenfb",1:"cclosefb",2:"coveropen",3:"fastopenLCB",4:"-----",
        5:"earthfail",6:"-----",7:"device-address0",8:"device-address1",
        9:"device-address2",10:"-----",11:"-----",12:"-----",13:"-----",
        14:"-----",15:"-----"},
    "stdo": {
        0:"closeby",1:"cidactive",2:"cidclose",3:"earth",4:"-----",
        5:"-----",6:"-----",7:"-----",8:"-----",9:"-----",10:"-----",
        11:"-----",12:"-----",13:"-----",14:"-----",15:"-----"},
    "PCUc": {
        0:"Bianco",1:"AcLCBclosed",2:"DcLCBclosed",3:"Chfresc",
        4:"StartCCM",5:"StartLCM",6:"Mant",7:"FPA",8:"resetEsc",
        9:"TestCID",10:"TrNeutro",11:"scafil2Q",12:"scafilOVP",
        13:"-----",14:"-----",15:"-----"},
    "PCUs": {
        0:"Dc1_5kV_SEL",1:"Dc1_5kV_CONF",2:"Dc1_5kV_LINEoN",
        3:"Dc3kV_SEL",4:"Dc3kV_CONF",5:"Dc3kV_LINEoN",6:"Ac15kV_SEL",
        7:"Ac25kV_SEL",8:"setHIL",9:"Dc3kV_LcbClosed",
        10:"Dc1_5kV_LcbClosed",11:"-----",12:"-----",13:"-----",
        14:"-----",15:"-----"},
    "msf": {
        0:"NOCGF",1:"2QOFF",2:"2QBIA",3:"3KON",4:"SCAR2Q",5:"1,5K ON",
        6:"PROT",7:"PROTBLO",8:"FASTSHUT",9:"SOFTSHUT",10:"-----",
        11:"AUTORESET",12:"-----",13:"ESCL",14:"-----",15:"-----"},
}

SM_RE = re.compile(
    r"^Rec:\s+(\d+)\s+Code:\s+([0-9A-Fa-f]+)\s+Date:(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{2}:\d{2}:\d{2}\.\d{2})\s+-\s+(.*)$")
LL_HEADER_RE = re.compile(r"^\s*N\.\s+")
LL_ROW_RE = re.compile(r"^\s*(-?\d+)\s+(.*)$")


def split_description(desc):
    if " - " in desc:
        left, descrizione = desc.split(" - ", 1)
    else:
        left, descrizione = desc, ""
    fields = [p.strip() for p in left.split(";") if p.strip()][:MAX_FIELDS]
    fields += [""] * (MAX_FIELDS - len(fields))
    return fields, descrizione.strip()


def parse_file(uploaded_file):
    summary, ll_blocks = [], {}
    current_rec, in_ll, columns = None, False, []
    text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

    for line in text.splitlines():
        m = SM_RE.match(line)
        if m:
            rec, code, date, time, desc = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)
            fields, descrizione = split_description(desc)
            summary.append([rec, code, date, time] + fields + [descrizione])
            ll_blocks[rec] = []
            current_rec, in_ll, columns = rec, False, []
            continue

        if LL_HEADER_RE.match(line):
            columns, in_ll = line.split(), True
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


def decode_word(hex_value, bit_map):
    try:
        value = int(str(hex_value), 16)
    except Exception:
        value = 0
    return {
        name: (value >> bit) & 1
        for bit, name in bit_map.items()
        if name != "-----"
    }


def load_css():
    st.markdown("""
    <style>
    .digital-title{font-size:22px;font-weight:700;margin:8px 0 12px}
    .digital-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:7px}
    .digital-card{border:1px solid #d7dce2;border-radius:6px;background:#fff;overflow:hidden;margin-bottom:7px}
    .digital-card-title{background:#f4f6f8;border-bottom:1px solid #d7dce2;padding:6px 8px;font-size:12px;font-weight:700}
    .digital-signal{height:18px;line-height:18px;padding:0 7px;margin:1px 2px;border-radius:2px;
                    background:#f0f0f0;color:#4d4d4d;font-size:10px;white-space:nowrap;
                    overflow:hidden;text-overflow:ellipsis}
    .digital-signal.on{background:#ffdfe2;color:#b40018;font-weight:700;border-left:3px solid #e0001b}
    .digital-signal.on:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;
                               background:#e0001b;margin-right:5px}
    .digital-signal.off:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;
                                background:#d9c8eb;margin-right:5px}
    .analog-title{font-size:22px;font-weight:700;margin:18px 0 10px}
    .analog-wrap{width:100%;overflow-x:auto}
    .analog-table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:12px}
    .analog-table th{background:#f1f3f6;padding:7px 8px;border:1px solid #d7dce2;text-align:left}
    .analog-table td{padding:7px 8px;border:1px solid #d7dce2;white-space:nowrap}
    .analog-name{font-weight:600}.analog-value{font-family:Consolas,monospace;font-weight:700;text-align:right}
    </style>
    """, unsafe_allow_html=True)


def render_summary(df):
    st.markdown("### 📋 Summary")

    # UNA SOLA ricerca.
    search_text = st.text_input(
        "🔎 Cerca nella descrizione",
        placeholder="Parola o parte della descrizione...",
        key="ccm_search"
    )

    filtered = df.copy()
    if search_text.strip():
        filtered = filtered[
            filtered["DESCRIZIONE"].fillna("").astype(str)
            .str.contains(search_text.strip(), case=False, regex=False)
        ].copy()

    st.dataframe(filtered, use_container_width=True, hide_index=True, height=300)
    return filtered


def render_digital_card(word, row):
    if word not in BIT_MAP:
        return

    st.markdown('<div class="digital-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="digital-card-title">{html.escape(word)}</div>', unsafe_allow_html=True)

    states = decode_word(row.get(word, "0"), BIT_MAP[word])

    for signal in BIT_MAP[word].values():
        if signal == "-----":
            continue
        cls = "on" if states.get(signal, 0) else "off"
        st.markdown(
            f'<div class="digital-signal {cls}">{html.escape(signal)}</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_digital_signals(row):
    st.markdown('<div class="digital-title">🔌 Segnali digitali</div>', unsafe_allow_html=True)

    cols = st.columns(7, gap="small")

    for i, word in enumerate(DIGITAL_WORDS):
        with cols[i % 7]:
            render_digital_card(word, row)


def render_analog_signals(row):
    st.markdown('<div class="analog-title">📈 Segnali analogici</div>', unsafe_allow_html=True)

    pair_columns = 4
    rows = [ANALOG_SIGNALS[i:i + pair_columns]
            for i in range(0, len(ANALOG_SIGNALS), pair_columns)]

    out = [
        "<div class='analog-wrap'><table class='analog-table'><tr>"
    ]

    for _ in range(pair_columns):
        out += ["<th>Segnale</th><th>Valore</th>"]
    out.append("</tr>")

    for signals in rows:
        out.append("<tr>")
        for sig in signals:
            value = row.get(sig, "—")
            if value is None or str(value).strip() == "":
                value = "—"
            out.append(f"<td class='analog-name'>{html.escape(str(sig))}</td>")
            out.append(f"<td class='analog-value'>{html.escape(str(value))}</td>")

        for _ in range(pair_columns - len(signals)):
            out += ["<td></td><td></td>"]

        out.append("</tr>")

    out.append("</table></div>")
    st.markdown("".join(out), unsafe_allow_html=True)


def ccm_page():
    load_css()
    st.title("⚡ Analisi CCM")

    uploaded_file = st.file_uploader(
        "Apri file CCM",
        type=["CAP", "cap"],
        key="ccm_file"
    )

    if uploaded_file is None:
        st.info("Carica un file .CAP per iniziare.")
        return

    signature = (uploaded_file.name, uploaded_file.size)

    if st.session_state.get("ccm_signature") != signature:
        try:
            summary, ll_blocks = parse_file(uploaded_file)
        except Exception as exc:
            st.error(f"Errore nella lettura del CCM: {exc}")
            return

        st.session_state.ccm_signature = signature
        st.session_state.ccm_summary = summary
        st.session_state.ccm_ll_blocks = ll_blocks
        st.session_state.ccm_selected_rec = None

    summary = st.session_state.get("ccm_summary", [])
    ll_blocks = st.session_state.get("ccm_ll_blocks", {})

    if not summary:
        st.error("Nessun Summary trovato nel file.")
        return

    columns = ["REC", "CODE", "DATE", "TIME"] + [f"F{i+1}" for i in range(MAX_FIELDS)] + ["DESCRIZIONE"]
    df = pd.DataFrame(summary, columns=columns)

    filtered = render_summary(df)
    if filtered.empty:
        st.warning("Nessun REC corrisponde alla ricerca.")
        return

    st.divider()

    recs = filtered["REC"].tolist()
    old_rec = st.session_state.get("ccm_selected_rec")
    default = recs.index(old_rec) if old_rec in recs else 0

    selected_rec = st.selectbox(
        "REC da analizzare",
        recs,
        index=default,
        format_func=lambda x: f"REC {x}",
        key="ccm_rec"
    )
    st.session_state.ccm_selected_rec = selected_rec

    selected_summary = filtered[filtered["REC"] == selected_rec].iloc[0]
    descrizione = str(selected_summary.get("DESCRIZIONE", ""))

    st.markdown(f"**REC {selected_rec} — {html.escape(descrizione)}**")

    ll = ll_blocks.get(int(selected_rec), [])
    if not ll:
        st.warning(f"Nessuna LL disponibile per REC {selected_rec}.")
        return

    total = len(ll)

    # Timeline manuale: nessun pulsante PLAY/PAUSE.
    index_key = f"ccm_index_{selected_rec}"
    current = int(st.session_state.get(index_key, 0))
    current = min(max(current, 0), total - 1)

    new_index = st.slider(
        "Timeline",
        min_value=0,
        max_value=max(0, total - 1),
        value=current,
        key=f"ccm_timeline_{selected_rec}",
        label_visibility="visible"
    )

    st.session_state[index_key] = new_index

    row = ll[new_index]

    st.caption(
        f"Campione: {new_index + 1} / {total}   |   N: {row.get('N', '—')}"
    )

    render_digital_signals(row)

    st.divider()

    render_analog_signals(row)
