import streamlit as st
import pandas as pd
import re
from datetime import datetime


# ==========================================================
# DATASET FDE
# ==========================================================

DATASETS = [
    "iFDE1Status1",
    "iFDEStatus2",
    "iFDE1Diag1",
    "iFDEDiag2",
    "iFDECount",
    "iFDECtrlOp",
    "iFDEIdent2",
    "SCU-MAIN VERSION.RELEASE",
    "SCU-DIAG VERSION.RELEASE",
]


# ==========================================================
# DECODIFICHE
# ==========================================================

DECODIFICHE = {

    "ISMOKESENSSTATE": {
        "0": "NESSUN ALLARME",
        "1": "ALLARME TERMICO",
        "2": "ALLARME FUMO",
        "3": "ALLARME FUMO E TERMICO",
        "4": "FAULT",
        "5": "SENSORE DISABILITATO",
    },

    "IHVACCMDSTATE": {
        "0": "STANDBY",
        "1": "HVAC SPENTO PER INCENDIO A BORDO",
        "2": "FAIL",
    },

    "IGWAYDOORCMDSTATE": {
        "0": "STANDBY",
        "1": "CHIUSURA PORTA ATTIVA",
        "2": "FAIL",
    },

    "IPGRAREAMODE": {
        "1": "START",
        "2": "STANDBY",
        "3": "PRE-ALLARME",
        "4": "PRE-ATTIVAZIONE SPRINKLERS",
        "5": "ATTIVAZIONE SPRINKLERS",
        "6": "SCARICO DISABILITATO",
        "7": "TEST/MANUTENZIONE",
    },

    "FIOCARDS": {
        "0": "OK",
        "1": "110V NON PRESENTE",
        "2": "FAULT",
        "3": "SCHEDA NON PRESENTE",
    },

    "IFIREGENERALALARM": {
        "0": "NESSUN ALLARME",
        "1": "ALLARME INCENDIO",
    },

    "IELECTROVALVEDMX": {
        "0": "STANDBY",
        "1": "ELETTROVALVOLA MAU ATTIVA",
        "2": "FAIL",
    },

    "FSCUCOM": {
        "0": "COMUNICAZIONE TRA CENTRALINE OK",
        "1": "COMUNICAZIONE TRA CENTRALINE FALLITA",
    },

    "FCCUCOM": {
        "0": "COMUNICAZIONE CON CCU OK",
        "1": "COMUNICAZIONE CON CCU FALLITA",
    },

    "FSMOKESENS": {
        "0": "OK",
        "1": "MANUTENZIONE RICHIESTA SU SENSORE",
        "2": "SENSORE SPORCO",
        "3": "FAULT",
        "4": "SENSORE NON PRESENTE",
    },

    "FAEROSOL": {
        "0": "OK",
        "1": "CIRCUITO APERTO AEROSOL",
        "2": "VALORE INSTABILE AEROSOL",
        "3": "CANALE INSTABILE AEROSOL",
        "4": "COMANDO AEROSOL ATTIVO",
        "5": "24V NON PRESENTE",
    },

    "IAEROCARTRIDGESTATE": {
        "0": "OK",
        "1": "CARTUCCIA ATTIVA",
        "2": "CARTUCCIA SPARATA",
        "3": "FAULT",
        "4": "NESSUNA CARTUCCIA",
    },

    "ICARFIREALARM": {
        "0": "NESSUN ALLARME",
        "1": "PRE-ALLARME AREA PASSEGGERI",
        "2": "ALLARME AREA PASSEGGERI",
        "3": "ALLARME AREA TECNICA",
        "4": "PRE-ALLARME AREA PASSEGGERI E ALLARME AREA TECNICA",
        "5": "ALLARME AREA TECNICA E PASSEGGERI",
    },

    "FELECTROVALVES": {
        "0": "ELETTROVALVOLA OK",
        "1": "CIRCUITO APERTO",
        "2": "VALORE INSTABILE",
        "3": "CANALE INSTABILE",
        "4": "24V NON PRESENTE",
    },

    "ITECHAREAMODE": {
        "1": "STARTING",
        "2": "STANDBY",
        "3": "ALLARME",
        "4": "SPEGNIMENTO FUOCO AREA TECNICA",
        "5": "TEST/MANUTENZIONE",
    },

    "FFIREONBOARDTX": {
        "0": "NESSUN FUOCO A BORDO TRASMESSO",
        "1": "FUOCO A BORDO TRASMESSO",
    },

    "IFIREONBOARDTX": {
        "0": "ALLARME TRASMESSO IN ACCOPPIATA",
        "1": "NESSUN ALLARME TRASMESSO IN ACCOPPIATA",
    },

    "FSMOKESENSLOOP": {
        "0": "LOOP OK",
        "1": "LOOP INTERROTTO IN DM1",
        "2": "LOOP INTERROTTO IN TT2",
        "3": "LOOP INTERROTTO IN M3",
        "4": "LOOP INTERROTTO IN T4",
        "5": "LOOP INTERROTTO IN T5",
        "6": "LOOP INTERROTTO IN M6",
        "7": "LOOP INTERROTTO IN TT7",
        "8": "LOOP INTERROTTO IN DM8",
    },

    "IGENSYSTEMMODE": {
        "0": "NON ALIMENTATO",
        "1": "SISTEMA IN SERVIZIO",
        "2": "SISTEMA DEGRADATO",
        "3": "SISTEMA FUORI SERVIZIO",
        "4": "INIZIALIZZAZIONE",
        "10": "MODALITA' TEST",
        "11": "MODALITA' CARICAMENTO SW",
    },

    "ISPECSYSTOKMODE": {
        "0": "MASTER",
        "1": "SLAVE",
    },

    "IMAUINPUTSTATE": {
        "0": "NON ATTIVO",
        "1": "ATTIVO",
    },
}


# ==========================================================
# CASSE
# ==========================================================

DECODIFICA_CASSA = {
    "1": "DM1",
    "2": "TT2",
    "3": "M3",
    "4": "T4",
    "5": "T5",
    "6": "M6",
    "7": "TT7",
    "8": "DM8",
}


# ==========================================================
# SENSORI FUMO
# ==========================================================

DECODIFICA_NUMBER_SMOKE = {
    str(i): f"SD{i + 1}"
    for i in range(74)
}


# ==========================================================
# MAU
# ==========================================================

DECODIFICA_NUMBER_MAU = {
    "0": "BASSA PRESSIONE",
    "1": "CONDOTTA ACQUA PRESSURIZZATA",
    "2": "BASSA PRESSIONE",
    "3": "CONDOTTA ACQUA PRESSURIZZATA",
}


# ==========================================================
# COLORI
# ==========================================================

COLORI_EVENTO = {

    "SENSORE FUMO": "#ff3b30",

    "ALLARME INCENDIO": "#ff0000",

    "BASSA PRESSIONE": "#007aff",

    "CONDOTTA ACQUA PRESSURIZZATA": "#34c759",

}


# ==========================================================
# NORMALIZZA SEGNALE
# ==========================================================

def normalizza_segnale(segnale):

    if segnale is None:
        return ""

    segnale = str(segnale).strip()

    segnale = re.split(
        r"[\[_]",
        segnale
    )[0]

    return segnale.strip()


# ==========================================================
# TIMESTAMP
# ==========================================================

def parse_timestamp(valore):

    if not valore:
        return None

    valore = " ".join(
        str(valore).split()
    )

    formati = [

        "%a %b %d %H:%M:%S %Y",

        "%a %b %d %H:%M:%S.%f %Y",

        "%Y-%m-%d %H:%M:%S",

        "%Y-%m-%d %H:%M:%S.%f",

        "%d-%m-%Y %H:%M:%S",

    ]

    for formato in formati:

        try:

            return datetime.strptime(
                valore,
                formato
            )

        except ValueError:
            pass

    return None


# ==========================================================
# ESTRAI PARAMETRI
# ==========================================================

def estrai_parametri(valore):

    valore = str(valore)

    cassa = "-"
    number = "-"
    data = "-"

    # COACH N
    match = re.search(
        r"COACH\s*N\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if match:

        cassa = DECODIFICA_CASSA.get(
            match.group(1),
            match.group(1)
        )

    # NUMBER
    match = re.search(
        r"NUMBER\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if match:

        number = match.group(1)

    # DATA
    match = re.search(
        r"DATA\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if match:

        data = match.group(1)

    return cassa, number, data


# ==========================================================
# DECODIFICA
# ==========================================================

def decodifica_segnale(
    segnale,
    valore
):

    segnale_upper = str(
        segnale
    ).upper()

    cassa, number, data = estrai_parametri(
        valore
    )

    descrizione = str(data)

    mapping = None

    for nome, valori in DECODIFICHE.items():

        if segnale_upper.startswith(nome):

            mapping = valori
            break

    if mapping:

        descrizione = mapping.get(
            str(data),
            str(data)
        )

    # SENSORI FUMO
    if (
        segnale_upper.startswith(
            "ISMOKESENSSTATE"
        )
        or
        segnale_upper.startswith(
            "FSMOKESENS"
        )
    ):

        number_decodificato = (
            DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                str(number)
            )
        )

    # MAU
    elif segnale_upper.startswith(
        "IMAUINPUTSTATE"
    ):

        number_decodificato = (
            DECODIFICA_NUMBER_MAU.get(
                str(number),
                str(number)
            )
        )

    else:

        number_decodificato = str(number)

    return (
        cassa,
        number_decodificato,
        data,
        descrizione
    )


# ==========================================================
# CLASSIFICA EVENTO
# ==========================================================

def classifica_evento(
    segnale,
    descrizione
):

    segnale = str(
        segnale
    ).upper()

    descrizione = str(
        descrizione
    ).upper()

    # ------------------------------------------------------
    # SENSORE FUMO
    # ------------------------------------------------------

    if (
        "ALLARME FUMO" in descrizione
        or
        "ALLARME TERMICO" in descrizione
        or
        "FUMO E TERMICO" in descrizione
    ):

        return "SENSORE FUMO"

    # ------------------------------------------------------
    # ALLARME INCENDIO
    # ------------------------------------------------------

    if "ALLARME INCENDIO" in descrizione:

        return "ALLARME INCENDIO"

    # ------------------------------------------------------
    # BASSA PRESSIONE
    # ------------------------------------------------------

    if "BASSA PRESSIONE" in descrizione:

        return "BASSA PRESSIONE"

    # ------------------------------------------------------
    # ACQUA PRESSURIZZATA
    # ------------------------------------------------------

    if "CONDOTTA ACQUA PRESSURIZZATA" in descrizione:

        return "CONDOTTA ACQUA PRESSURIZZATA"

    return "NORMALE"


# ==========================================================
# IMPORTA LOG
# ==========================================================

def importa_log(
    uploaded_file
):

    dati = []

    timestamp = None

    dataset_corrente = None

    segnale_corrente = None

    contenuto = uploaded_file.getvalue()

    try:

        testo = contenuto.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        testo = contenuto.decode(
            "latin-1",
            errors="ignore"
        )

    # ======================================================
    # LETTURA
    # ======================================================

    for riga in testo.splitlines():

        riga = riga.strip()

        if not riga:
            continue

        # --------------------------------------------------
        # TIMESTAMP
        # --------------------------------------------------

        if riga.startswith(
            "------->"
        ):

            timestamp = parse_timestamp(
                riga.replace(
                    "------->",
                    "",
                    1
                ).strip()
            )

            dataset_corrente = None
            segnale_corrente = None

            continue

        if timestamp is None:
            continue

        # --------------------------------------------------
        # DATASET
        # --------------------------------------------------

        trovato = False

        for dataset in DATASETS:

            token = dataset + "/"

            if token in riga:

                parte = riga.split(
                    token,
                    1
                )[1]

                if ":" in parte:

                    segnale = parte.split(
                        ":",
                        1
                    )[0].strip()

                else:

                    segnale = parte.strip()

                dataset_corrente = dataset

                segnale_corrente = normalizza_segnale(
                    segnale
                )

                trovato = True

                break

        if trovato:
            continue

        # --------------------------------------------------
        # VALORE
        # --------------------------------------------------

        if (
            dataset_corrente
            and
            segnale_corrente
        ):

            dati.append({

                "timestamp":
                    timestamp,

                "dataset":
                    dataset_corrente,

                "segnale":
                    segnale_corrente,

                "valore":
                    riga,

            })

            dataset_corrente = None
            segnale_corrente = None

    # ======================================================
    # DATAFRAME
    # ======================================================

    df = pd.DataFrame(
        dati
    )

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "timestamp"
        ]
    )

    return df


# ==========================================================
# PREPARA EVENTI
# ==========================================================

def prepara_eventi(
    df,
    origine
):

    if df.empty:
        return df

    df = df.copy()

    df["origine"] = origine

    casse = []
    numbers = []
    date_valori = []
    descrizioni = []
    eventi = []

    for _, riga in df.iterrows():

        (
            cassa,
            number,
            data,
            descrizione
        ) = decodifica_segnale(
            riga["segnale"],
            riga["valore"]
        )

        evento = classifica_evento(
            riga["segnale"],
            descrizione
        )

        casse.append(cassa)

        numbers.append(number)

        date_valori.append(data)

        descrizioni.append(
            descrizione
        )

        eventi.append(evento)

    df["cassa"] = casse

    df["number"] = numbers

    df["data_val"] = date_valori

    df["descrizione"] = descrizioni

    df["evento"] = eventi

    return df


# ==========================================================
# RICERCA
# ==========================================================

def filtra_ricerca(
    df,
    ricerca
):

    if df.empty or not ricerca:
        return df

    ricerca = str(
        ricerca
    ).strip().lower()

    colonne = [

        "origine",
        "dataset",
        "segnale",
        "valore",
        "cassa",
        "number",
        "data_val",
        "descrizione",
        "evento",

    ]

    mask = pd.Series(
        False,
        index=df.index
    )

    for colonna in colonne:

        if colonna not in df.columns:
            continue

        mask |= (
            df[colonna]
            .astype(str)
            .str.lower()
            .str.contains(
                ricerca,
                regex=False,
                na=False
            )
        )

    return df[mask]


# ==========================================================
# TIMELINE HTML
# ==========================================================

def crea_timeline_html(df):

    if df.empty:

        return """
        <div style="
            padding:30px;
            text-align:center;
            color:#777;
            border:1px solid #ddd;
            border-radius:10px;
        ">
            Nessun evento da visualizzare
        </div>
        """

    df = df.sort_values(
        "timestamp"
    ).copy()

    tempo_min = df["timestamp"].min()

    tempo_max = df["timestamp"].max()

    durata = (
        tempo_max - tempo_min
    ).total_seconds()

    if durata <= 0:
        durata = 1

    # ======================================================
    # HTML
    # ======================================================

    html = """

    <style>

    .fde-timeline {
        width:100%;
        overflow-x:auto;
        font-family:Arial, sans-serif;
    }

    .fde-header {
        display:flex;
        min-width:1100px;
        border-bottom:2px solid #333;
        background:#f5f5f5;
        font-weight:bold;
    }

    .fde-label {
        width:270px;
        min-width:270px;
        padding:12px;
        border-right:1px solid #ccc;
        box-sizing:border-box;
    }

    .fde-time {
        position:relative;
        flex:1;
        height:45px;
    }

    .fde-row {
        display:flex;
        min-width:1100px;
        min-height:62px;
        border-bottom:1px solid #ddd;
    }

    .fde-row-label {
        width:270px;
        min-width:270px;
        padding:8px;
        border-right:1px solid #ccc;
        box-sizing:border-box;
        background:white;
    }

    .fde-signal {
        font-weight:bold;
        font-size:14px;
    }

    .fde-source {
        font-size:11px;
        color:#777;
        margin-top:3px;
    }

    .fde-line {
        position:relative;
        flex:1;
        min-height:62px;
        background:
            repeating-linear-gradient(
                90deg,
                #ffffff 0px,
                #ffffff 99px,
                #eeeeee 100px
            );
    }

    .fde-event {
        position:absolute;
        top:17px;
        height:28px;
        border-radius:5px;
        min-width:10px;
        box-shadow:0 1px 3px rgba(0,0,0,.25);
        cursor:pointer;
    }

    .fde-event:hover {
        transform:scaleY(1.15);
        z-index:10;
    }

    .fde-event-label {
        color:white;
        font-size:10px;
        font-weight:bold;
        padding:7px 5px;
        white-space:nowrap;
        overflow:hidden;
        text-overflow:ellipsis;
    }

    .fde-time-label {
        position:absolute;
        top:12px;
        font-size:10px;
        color:#555;
        transform:translateX(-50%);
    }

    .fde-legend {
        display:flex;
        flex-wrap:wrap;
        gap:15px;
        margin-top:15px;
        padding:12px;
        border:1px solid #ddd;
        border-radius:8px;
        background:#fafafa;
    }

    .fde-legend-item {
        display:flex;
        align-items:center;
        gap:6px;
        font-size:13px;
    }

    .fde-color {
        width:15px;
        height:15px;
        border-radius:3px;
    }

    </style>

    <div class="fde-timeline">

    """

    # ======================================================
    # HEADER
    # ======================================================

    html += """

    <div class="fde-header">

        <div class="fde-label">
            SEGNALE / EVENTO
        </div>

        <div class="fde-time">
    """

    # 6 riferimenti temporali

    for i in range(6):

        percentuale = (
            i / 5
        ) * 100

        tempo = (
            tempo_min
            +
            (
                tempo_max - tempo_min
            )
            * (
                i / 5
            )
        )

        html += f"""

        <div
            class="fde-time-label"
            style="left:{percentuale}%"
        >
            {tempo.strftime("%d/%m %H:%M:%S")}
        </div>

        """

    html += """

        </div>

    </div>

    """

    # ======================================================
    # UNA RIGA PER OGNI SEGNALE / NUMBER
    # ======================================================

    gruppi = df.groupby(
        [
            "segnale",
            "number"
        ],
        dropna=False
    )

    for (segnale, number), gruppo in gruppi:

        # descrizione evento prevalente
        eventi = gruppo[
            "evento"
        ].tolist()

        evento_nome = "EVENTO"

        for e in eventi:

            if e != "NORMALE":

                evento_nome = e

                break

        html += """

        <div class="fde-row">

        """

        # --------------------------------------------------
        # LABEL
        # --------------------------------------------------

        html += f"""

        <div class="fde-row-label">

            <div class="fde-signal">
                {segnale}
            </div>

            <div>
                <b>{number}</b>
            </div>

        """

        # descrizione

        descrizioni = [
            str(x)
            for x in gruppo["descrizione"].tolist()
            if str(x) not in ["", "nan", "-"]
        ]

        if descrizioni:

            html += f"""

            <div class="fde-source">
                {descrizioni[0]}
            </div>

            """

        html += """

        </div>

        """

        # --------------------------------------------------
        # LINEA
        # --------------------------------------------------

        html += """

        <div class="fde-line">

        """

        # --------------------------------------------------
        # EVENTI
        # --------------------------------------------------

        for _, riga in gruppo.iterrows():

            timestamp = riga["timestamp"]

            posizione = (
                (
                    timestamp - tempo_min
                ).total_seconds()
                /
                durata
            ) * 100

            evento = str(
                riga["evento"]
            )

            if evento == "NORMALE":
                continue

            colore = COLORI_EVENTO.get(
                evento,
                "#808080"
            )

            descrizione = str(
                riga.get(
                    "descrizione",
                    ""
                )
            )

            origine = str(
                riga.get(
                    "origine",
                    ""
                )
            )

            cassa = str(
                riga.get(
                    "cassa",
                    ""
                )
            )

            valore = str(
                riga.get(
                    "valore",
                    ""
                )
            )

            tooltip = (
                f"{timestamp.strftime('%d/%m/%Y %H:%M:%S')} | "
                f"{origine} | "
                f"{segnale} | "
                f"{number} | "
                f"{cassa} | "
                f"{descrizione} | "
                f"{valore}"
            )

            html += f"""

            <div
                class="fde-event"
                style="
                    left:{posizione}%;
                    background:{colore};
                "
                title="{tooltip}"
            >

                <div class="fde-event-label">
                    {evento}
                </div>

            </div>

            """

        html += """

        </div>

        </div>

        """

    # ======================================================
    # LEGENDA
    # ======================================================

    html += """

    <div class="fde-legend">

    """

    for nome, colore in COLORI_EVENTO.items():

        html += f"""

        <div class="fde-legend-item">

            <div
                class="fde-color"
                style="background:{colore};"
            ></div>

            {nome}

        </div>

        """

    html += """

    </div>

    </div>

    """

    return html


# ==========================================================
# PAGINA FDE
# ==========================================================

def fde_page():

    st.title(
        "📊 Analizzatore Log FDE"
    )

    st.caption(
        "Analisi integrata Log DM1 + DM8"
    )

    st.divider()

    # ======================================================
    # UPLOAD
    # ======================================================

    col1, col2 = st.columns(2)

    with col1:

        file_dm1 = st.file_uploader(
            "📥 Carica Log DM1",
            type=None,
            key="fde_file_dm1"
        )

    with col2:

        file_dm8 = st.file_uploader(
            "📥 Carica Log DM8",
            type=None,
            key="fde_file_dm8"
        )

    if (
        file_dm1 is None
        and
        file_dm8 is None
    ):

        st.info(
            "Carica almeno un log DM1 o DM8."
        )

        return

    # ======================================================
    # ANALISI
    # ======================================================

    frames = []

    # ------------------------------------------------------
    # DM1
    # ------------------------------------------------------

    if file_dm1 is not None:

        with st.spinner(
            "🔄 Analisi DM1..."
        ):

            df_dm1 = importa_log(
                file_dm1
            )

            df_dm1 = prepara_eventi(
                df_dm1,
                "DM1"
            )

        if not df_dm1.empty:

            frames.append(
                df_dm1
            )

            st.success(
                f"✅ DM1: {len(df_dm1)} eventi letti"
            )

        else:

            st.warning(
                "⚠️ DM1: nessun dato riconosciuto."
            )

    # ------------------------------------------------------
    # DM8
    # ------------------------------------------------------

    if file_dm8 is not None:

        with st.spinner(
            "🔄 Analisi DM8..."
        ):

            df_dm8 = importa_log(
                file_dm8
            )

            df_dm8 = prepara_eventi(
                df_dm8,
                "DM8"
            )

        if not df_dm8.empty:

            frames.append(
                df_dm8
            )

            st.success(
                f"✅ DM8: {len(df_dm8)} eventi letti"
            )

        else:

            st.warning(
                "⚠️ DM8: nessun dato riconosciuto."
            )

    if not frames:

        st.error(
            "❌ Nessun dato riconosciuto."
        )

        return

    # ======================================================
    # UNIONE DM1 + DM8
    # ======================================================

    df = pd.concat(
        frames,
        ignore_index=True
    )

    df = df.sort_values(
        "timestamp"
    ).reset_index(
        drop=True
    )

    # ======================================================
    # EVENTI INTERESSANTI
    # ======================================================

    eventi_interessanti = [

        "SENSORE FUMO",

        "ALLARME INCENDIO",

        "BASSA PRESSIONE",

        "CONDOTTA ACQUA PRESSURIZZATA",

    ]

    df_eventi = df[
        df["evento"].isin(
            eventi_interessanti
        )
    ].copy()

    # ======================================================
    # FILTRI
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Filtri"
    )

    data_min = df["timestamp"].min().date()

    data_max = df["timestamp"].max().date()

    col1, col2 = st.columns(2)

    with col1:

        data_da = st.date_input(
            "📅 Da",
            value=data_min,
            min_value=data_min,
            max_value=data_max
        )

    with col2:

        data_a = st.date_input(
            "📅 A",
            value=data_max,
            min_value=data_min,
            max_value=data_max
        )

    # ======================================================
    # ORIGINE
    # ======================================================

    origini_disponibili = sorted(
        df_eventi[
            "origine"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    origini = st.multiselect(
        "💻 Origine",
        origini_disponibili,
        default=origini_disponibili
    )

    # ======================================================
    # EVENTI
    # ======================================================

    eventi_selezionati = st.multiselect(

        "🚨 Eventi",

        eventi_interessanti,

        default=eventi_interessanti

    )

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(

        "🔍 Ricerca",

        placeholder=(
            "SD1, SD25, DM1, DM8, "
            "BASSA PRESSIONE..."
        )

    )

    # ======================================================
    # FILTRO DATE
    # ======================================================

    data_da_dt = datetime.combine(
        data_da,
        datetime.min.time()
    )

    data_a_dt = datetime.combine(
        data_a,
        datetime.max.time()
    )

    filtrato = df_eventi[
        (
            df_eventi["timestamp"]
            >= data_da_dt
        )
        &
        (
            df_eventi["timestamp"]
            <= data_a_dt
        )
    ].copy()

    # ======================================================
    # ORIGINE
    # ======================================================

    if origini:

        filtrato = filtrato[
            filtrato["origine"].isin(
                origini
            )
        ]

    # ======================================================
    # EVENTI
    # ======================================================

    if eventi_selezionati:

        filtrato = filtrato[
            filtrato["evento"].isin(
                eventi_selezionati
            )
        ]

    else:

        filtrato = filtrato.iloc[0:0]

    # ======================================================
    # RICERCA
    # ======================================================

    filtrato = filtra_ricerca(
        filtrato,
        ricerca
    )

    # ======================================================
    # METRICHE
    # ======================================================

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📋 Eventi",
        len(filtrato)
    )

    col2.metric(
        "🔥 Incendio",
        int(
            (
                filtrato["evento"]
                == "ALLARME INCENDIO"
            ).sum()
        )
    )

    col3.metric(
        "💨 Sensore fumo",
        int(
            (
                filtrato["evento"]
                == "SENSORE FUMO"
            ).sum()
        )
    )

    col4.metric(
        "💧 Pressione",
        int(
            (
                (
                    filtrato["evento"]
                    == "BASSA PRESSIONE"
                )
                |
                (
                    filtrato["evento"]
                    == "CONDOTTA ACQUA PRESSURIZZATA"
                )
            ).sum()
        )
    )

    # ======================================================
    # NESSUN RISULTATO
    # ======================================================

    if filtrato.empty:

        st.warning(
            "⚠️ Nessun evento trovato."
        )

        # DEBUG UTILE
        with st.expander(
            "🔧 Diagnostica"
        ):

            st.write(
                "Eventi presenti nel log:"
            )

            st.dataframe(
                df[
                    [
                        "timestamp",
                        "origine",
                        "segnale",
                        "number",
                        "descrizione",
                        "evento"
                    ]
                ].head(100),
                use_container_width=True
            )

        return

    # ======================================================
    # TIMELINE
    # ======================================================

    st.divider()

    st.subheader(
        "🕒 Timeline FDE"
    )

    st.markdown(
        crea_timeline_html(
            filtrato
        ),
        unsafe_allow_html=True
    )

    # ======================================================
    # TABELLA DETTAGLIATA
    # ======================================================

    st.divider()

    st.subheader(
        f"📋 Dettaglio eventi ({len(filtrato)})"
    )

    tabella = filtrato.copy()

    tabella["Ora"] = (
        tabella["timestamp"]
        .dt
        .strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    tabella = tabella[
        [
            "Ora",
            "origine",
            "dataset",
            "segnale",
            "number",
            "cassa",
            "data_val",
            "descrizione",
            "evento",
            "valore"
        ]
    ]

    tabella = tabella.rename(
        columns={

            "origine": "Origine",

            "dataset": "Dataset",

            "segnale": "Segnale",

            "number": "Sensore / Number",

            "cassa": "Cassa",

            "data_val": "Data",

            "descrizione": "Descrizione",

            "evento": "Evento",

            "valore": "Valore grezzo",

        }
    )

    st.dataframe(
        tabella,
        use_container_width=True,
        hide_index=True,
        height=600
    )

    # ======================================================
    # DOWNLOAD
    # ======================================================

    csv = tabella.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )

    st.download_button(

        "📥 Scarica CSV",

        data=csv,

        file_name="analisi_fde_eventi.csv",

        mime="text/csv"

    )
