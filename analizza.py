import streamlit as st
import pandas as pd
from datetime import datetime, date
import re


# ==========================================================
# DATASET PRESENTI NEL LOG
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
# DECODIFICHE SEGNALI
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
# DECODIFICA MAU
# ==========================================================

DECODIFICA_NUMBER_MAU = {
    "0": "BASSA PRESSIONE",
    "1": "CONDOTTA ACQUA PRESSURIZZATA",
    "2": "BASSA PRESSIONE",
    "3": "CONDOTTA ACQUA PRESSURIZZATA",
}


# ==========================================================
# DECODIFICA SENSORI FUMO
# ==========================================================

DECODIFICA_NUMBER_SMOKE = {
    "0": "SD1-SENSORE CABINA",
    "1": "SD2-SENSORE ELECTRONIC ROOM",
    "2": "SD3-SENSORE SALONE 1",
    "3": "SD4-SENSORE SALONE 2",
    "4": "SD5-SENSORE CORRIDOIO",
    "5": "SD6-SENSORE MEETING",
    "6": "SD7-SENSORE GALLEY",
    "7": "SD8-SENSORE TOI-EXECUTIVE",
    "8": "SD9-SENSORE VESTIBOLO",
    "9": "SD10-SENSORE VESTIBOLO PICCOLO",
    "10": "SD11-SENSORE SALONE 1",
    "11": "SD12-SENSORE SALONE 2",
    "12": "SD13-SENSORE SALONE 3",
    "13": "SD14-SENSORE SALONE 4",
    "14": "SD15-SENSORE SALONE 5",
    "15": "SD16-SENSORE TOI 1",
    "16": "SD17-SENSORE TOI 2",
    "17": "SD18-SENSORE VESTIBOLO GRANDE",
    "18": "SD19-SENSORE VESTIBOLO PICCOLO",
    "19": "SD20-SENSORE SALONE 1",
    "20": "SD21-SENSORE SALONE 2",
    "21": "SD22-SENSORE SALONE 3",
    "22": "SD23-SENSORE STAFF",
    "23": "SD24-SENSORE TOI HK",
    "24": "SD25-SENSORE CORRIDOIO 1",
    "25": "SD26-SENSORE CORRIDOIO 2",
    "26": "SD27-SENSORE CREW",
    "27": "SD28-SENSORE CREW-TOI",
    "28": "SD29-SENSORE BISTROT 1",
    "29": "SD30-SENSORE BISTROT 2",
    "30": "SD31-SENSORE VESTIBOLO PICCOLO",
    "31": "SD32-SENSORE SALONE 1",
    "32": "SD33-SENSORE SALONE 2",
    "33": "SD34-SENSORE SALONE 3",
    "34": "SD35-SENSORE SALONE 4",
    "35": "SD36-SENSORE SALONE 5",
    "36": "SD37-SENSORE TOI 1",
    "37": "SD38-SENSORE TOI 2",
    "38": "SD39-SENSORE VESTIBOLO GRANDE",
    "39": "SD40-SENSORE VESTIBOLO GRANDE",
    "40": "SD41-SENSORE TOI 1",
    "41": "SD42-SENSORE TOI 2",
    "42": "SD43-SENSORE SALONE 5",
    "43": "SD44-SENSORE SALONE 4",
    "44": "SD45-SENSORE SALONE 3",
    "45": "SD46-SENSORE SALONE 2",
    "46": "SD47-SENSORE SALONE 1",
    "47": "SD48-SENSORE VESTIBOLO PICCOLO",
    "48": "SD49-SENSORE VESTIBOLO GRANDE",
    "49": "SD50-SENSORE TOI 1",
    "50": "SD51-SENSORE TOI 2",
    "51": "SD52-SENSORE SALONE 5",
    "52": "SD53-SENSORE SALONE 4",
    "53": "SD54-SENSORE SALONE 3",
    "54": "SD55-SENSORE SALONE 2",
    "55": "SD56-SENSORE SALONE 1",
    "56": "SD57-SENSORE VESTIBOLO PICCOLO",
    "57": "SD58-SENSORE VESTIBOLO PICCOLO",
    "58": "SD59-SENSORE TOI 1",
    "59": "SD60-SENSORE TOI 2",
    "60": "SD61-SENSORE SALONE 5",
    "61": "SD62-SENSORE SALONE 4",
    "62": "SD63-SENSORE SALONE 3",
    "63": "SD64-SENSORE SALONE 2",
    "64": "SD65-SENSORE SALONE 1",
    "65": "SD66-SENSORE VESTIBOLO PICCOLO",
    "66": "SD67-SENSORE VESTIBOLO GRANDE",
    "67": "SD68-SENSORE TOI",
    "68": "SD69-SENSORE SALONE 4",
    "69": "SD70-SENSORE SALONE 3",
    "70": "SD71-SENSORE SALONE 2",
    "71": "SD72-SENSORE SALONE 1",
    "72": "SD73-SENSORE ELECTRONIC ROOM",
    "73": "SD74-SENSORE CABINA",
}


# ==========================================================
# DECODIFICA CASSA
# ==========================================================

def decodifica_cassa(val):

    mappa = {
        "1": "DM1",
        "2": "TT2",
        "3": "M3",
        "4": "T4",
        "5": "T5",
        "6": "M6",
        "7": "TT7",
        "8": "DM8",
    }

    return mappa.get(
        str(val),
        str(val)
    )


# ==========================================================
# NORMALIZZA SEGNALE
# ==========================================================

def normalizza_segnale(segnale):

    if segnale is None:
        return ""

    return re.split(
        r"[\[_]",
        str(segnale)
    )[0].strip()


# ==========================================================
# PARSE PARAMETRI
# ==========================================================

def parse_dato(valore):

    coach = "-"
    number = "-"
    data_val = "-"

    valore = str(valore)

    m = re.search(
        r"COACH\s*N\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if m:

        coach = decodifica_cassa(
            m.group(1)
        )

    m = re.search(
        r"NUMBER\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if m:

        number = m.group(1)

    m = re.search(
        r"DATA\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if m:

        data_val = m.group(1)

    return (
        coach,
        number,
        data_val
    )


# ==========================================================
# DECODIFICA DATA
# ==========================================================

def decodifica_data_segnale(
    segnale_norm,
    data_val
):

    segnale = str(
        segnale_norm
    ).upper()

    for key, mapping in DECODIFICHE.items():

        if segnale.startswith(key):

            return mapping.get(
                str(data_val),
                str(data_val)
            )

    return str(data_val)


# ==========================================================
# TIMESTAMP
# ==========================================================

def parse_timestamp(ts_raw):

    if not ts_raw:
        return None

    testo = " ".join(
        str(ts_raw).split()
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
                testo,
                formato
            )

        except ValueError:
            pass

    return None


# ==========================================================
# IMPORTA LOG
# ==========================================================

def importa_log(uploaded_file):

    dati = []

    timestamp = None
    dataset = None
    segnale = None

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

    for riga in testo.splitlines():

        r = riga.strip()

        if not r:
            continue

        # --------------------------------------------------
        # TIMESTAMP
        # --------------------------------------------------

        if r.startswith(
            "------->"
        ):

            timestamp = parse_timestamp(
                r.replace(
                    "------->",
                    "",
                    1
                ).strip()
            )

            dataset = None
            segnale = None

            continue

        if timestamp is None:
            continue

        # --------------------------------------------------
        # VALORE
        # --------------------------------------------------

        if (
            segnale
            and
            r
            and
            "/" not in r
        ):

            dati.append([
                timestamp,
                dataset,
                segnale,
                r.replace(
                    "\x00",
                    ""
                ).strip()
            ])

            segnale = None
            dataset = None

            continue

        # --------------------------------------------------
        # DATASET / SEGNALE
        # --------------------------------------------------

        for ds in DATASETS:

            token = ds + "/"

            if token in r:

                parte = r.split(
                    token,
                    1
                )[1]

                segnale = parte.split(
                    ":",
                    1
                )[0].strip()

                dataset = ds

                break

    df = pd.DataFrame(
        dati,
        columns=[
            "timestamp",
            "dataset",
            "segnale",
            "valore"
        ]
    )

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["timestamp"]
    )

    df["segnale_norm"] = (
        df["segnale"]
        .apply(normalizza_segnale)
    )

    return df


# ==========================================================
# PREPARA ANALISI
# ==========================================================

def prepara_analisi(df):

    if df.empty:
        return df

    risultato = df.copy()

    casse = []
    numbers = []
    data_valori = []
    descrizioni = []
    tags = []

    for _, riga in risultato.iterrows():

        (
            cassa,
            number,
            data_val
        ) = parse_dato(
            riga["valore"]
        )

        segnale = str(
            riga["segnale_norm"]
        ).upper()

        # --------------------------------------------------
        # DECODIFICA DATA
        # --------------------------------------------------

        data_dec = decodifica_data_segnale(
            segnale,
            data_val
        )

        # --------------------------------------------------
        # SENSORI FUMO
        # --------------------------------------------------

        if (
            segnale.startswith(
                "ISMOKESENSSTATE"
            )
            or
            segnale.startswith(
                "FSMOKESENS"
            )
        ):

            number = DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                str(number)
            )

        # --------------------------------------------------
        # MAU
        # --------------------------------------------------

        elif segnale.startswith(
            "IMAUINPUTSTATE"
        ):

            data_dec = DECODIFICHE[
                "IMAUINPUTSTATE"
            ].get(
                str(data_val),
                str(data_val)
            )

            number = DECODIFICA_NUMBER_MAU.get(
                str(number),
                data_dec
            )

        # --------------------------------------------------
        # TAG EVENTO
        # --------------------------------------------------

        tag = ""

        # Smoke
        if (
            segnale.startswith(
                "ISMOKESENSSTATE"
            )
            or
            segnale.startswith(
                "FSMOKESENS"
            )
        ):

            if data_dec in [
                "ALLARME FUMO",
                "ALLARME FUMO E TERMICO"
            ]:

                tag = "FUMO"

            elif data_dec == "ALLARME TERMICO":

                tag = "TERMICO"

            elif data_dec == "FAULT":

                tag = "FAULT_SMOKE"

        # Altri segnali
        else:

            if data_dec == "SISTEMA FUORI SERVIZIO":

                tag = "FUORI SERVIZIO"

            elif data_dec == "ALLARME INCENDIO":

                tag = "ALLARME INCENDIO"

            elif number == "BASSA PRESSIONE":

                tag = "BASSA PRESSIONE"

            elif number == "CONDOTTA ACQUA PRESSURIZZATA":

                tag = "CONDOTTA ACQUA PRESSURIZZATA"

        casse.append(cassa)
        numbers.append(number)
        data_valori.append(data_val)
        descrizioni.append(data_dec)
        tags.append(tag)

    risultato["cassa"] = casse
    risultato["number"] = numbers
    risultato["data_val"] = data_valori
    risultato["descrizione"] = descrizioni
    risultato["evento"] = tags

    return risultato


# ==========================================================
# FILTRO RICERCA
# ==========================================================

def applica_ricerca(
    df,
    ricerca
):

    if df.empty:
        return df

    ricerca = str(
        ricerca
    ).strip().lower()

    if not ricerca:
        return df

    colonne = [
        "origine",
        "dataset",
        "segnale",
        "segnale_norm",
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
# COLORE RIGA
# ==========================================================

def evidenzia_eventi(row):

    evento = str(
        row.get(
            "evento",
            ""
        )
    )

    if evento == "FUMO":
        return [
            "background-color: #ff7f50"
        ] * len(row)

    if evento == "TERMICO":
        return [
            "background-color: #ff7f50"
        ] * len(row)

    if evento == "FAULT_SMOKE":
        return [
            "background-color: #9e9e9e"
        ] * len(row)

    if evento == "ALLARME INCENDIO":
        return [
            "background-color: #ff4d4d; font-weight: bold"
        ] * len(row)

    if evento == "FUORI SERVIZIO":
        return [
            "background-color: #ff4d4d; color: white; font-weight: bold"
        ] * len(row)

    if evento == "BASSA PRESSIONE":
        return [
            "background-color: #008f39; color: white; font-weight: bold"
        ] * len(row)

    if evento == "CONDOTTA ACQUA PRESSURIZZATA":
        return [
            "background-color: #008f39; color: white; font-weight: bold"
        ] * len(row)

    return [""] * len(row)


# ==========================================================
# PAGINA ANALIZZA
# ==========================================================

def analizza_page():

    st.title(
        "🔎 Analizza Log FDE"
    )

    st.caption(
        "Analisi dei log DM1 e DM8"
    )

    st.divider()

    # ======================================================
    # CARICAMENTO
    # ======================================================

    col1, col2 = st.columns(2)

    with col1:

        file_dm1 = st.file_uploader(
            "📥 Carica Log DM1",
            type=None,
            key="analizza_dm1"
        )

    with col2:

        file_dm8 = st.file_uploader(
            "📥 Carica Log DM8",
            type=None,
            key="analizza_dm8"
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
    # IMPORTAZIONE
    # ======================================================

    frames = []

    if file_dm1 is not None:

        with st.spinner(
            "🔄 Analisi Log DM1..."
        ):

            df_dm1 = importa_log(
                file_dm1
            )

        if not df_dm1.empty:

            df_dm1["origine"] = "DM1"

            frames.append(
                df_dm1
            )

            st.success(
                f"✅ DM1: {len(df_dm1)} eventi"
            )

        else:

            st.warning(
                "⚠️ Nessun evento trovato nel DM1."
            )

    if file_dm8 is not None:

        with st.spinner(
            "🔄 Analisi Log DM8..."
        ):

            df_dm8 = importa_log(
                file_dm8
            )

        if not df_dm8.empty:

            df_dm8["origine"] = "DM8"

            frames.append(
                df_dm8
            )

            st.success(
                f"✅ DM8: {len(df_dm8)} eventi"
            )

        else:

            st.warning(
                "⚠️ Nessun evento trovato nel DM8."
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
    # DECODIFICA
    # ======================================================

    df = prepara_analisi(
        df
    )

    # ======================================================
    # FILTRI
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Filtri"
    )

    data_min = df[
        "timestamp"
    ].min().date()

    data_max = df[
        "timestamp"
    ].max().date()

    col1, col2, col3 = st.columns(3)

    with col1:

        data_da = st.date_input(
            "📅 Da",
            value=data_min,
            min_value=data_min,
            max_value=data_max,
            key="analizza_data_da"
        )

    with col2:

        data_a = st.date_input(
            "📅 A",
            value=data_max,
            min_value=data_min,
            max_value=data_max,
            key="analizza_data_a"
        )

    with col3:

        origini = st.multiselect(
            "💻 Origine",
            ["DM1", "DM8"],
            default=["DM1", "DM8"],
            key="analizza_origini"
        )

    # ======================================================
    # FILTRO EVENTO
    # ======================================================

    eventi_disponibili = sorted(
        [
            x
            for x in df["evento"]
            .dropna()
            .astype(str)
            .unique()
            if x
        ]
    )

    eventi_selezionati = st.multiselect(
        "🚨 Tipo evento",
        eventi_disponibili,
        key="analizza_eventi"
    )

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(
        "🔍 Cerca",
        placeholder=(
            "Segnale, dataset, sensore, "
            "allarme, cassa..."
        ),
        key="analizza_ricerca"
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

    risultato = df[
        (
            df["timestamp"]
            >= data_da_dt
        )
        &
        (
            df["timestamp"]
            <= data_a_dt
        )
    ].copy()

    # ======================================================
    # FILTRO ORIGINE
    # ======================================================

    if origini:

        risultato = risultato[
            risultato["origine"].isin(
                origini
            )
        ]

    # ======================================================
    # FILTRO EVENTI
    # ======================================================

    if eventi_selezionati:

        risultato = risultato[
            risultato["evento"].isin(
                eventi_selezionati
            )
        ]

    # ======================================================
    # RICERCA
    # ======================================================

    risultato = applica_ricerca(
        risultato,
        ricerca
    )

    # ======================================================
    # METRICHE
    # ======================================================

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📋 Eventi",
            len(risultato)
        )

    with col2:

        st.metric(
            "DM1",
            int(
                (
                    risultato["origine"]
                    == "DM1"
                ).sum()
            )
        )

    with col3:

        st.metric(
            "DM8",
            int(
                (
                    risultato["origine"]
                    == "DM8"
                ).sum()
            )
        )

    with col4:

        st.metric(
            "🚨 Eventi classificati",
            int(
                (
                    risultato["evento"]
                    != ""
                ).sum()
            )
        )

    # ======================================================
    # RISULTATI
    # ======================================================

    st.divider()

    if risultato.empty:

        st.warning(
            "⚠️ Nessun risultato con "
            "i filtri selezionati."
        )

        return

    # ======================================================
    # PREPARA TABELLA
    # ======================================================

    tabella = risultato.copy()

    tabella["Time"] = (
        tabella["timestamp"]
        .dt.strftime(
            "%d-%m-%Y // %H:%M:%S"
        )
    )

    tabella = tabella[
        [
            "Time",
            "origine",
            "dataset",
            "segnale_norm",
            "cassa",
            "number",
            "data_val",
            "descrizione",
            "evento",
            "valore",
        ]
    ].copy()

    tabella = tabella.rename(
        columns={
            "origine": "Origine",
            "dataset": "Dataset",
            "segnale_norm": "Segnale",
            "cassa": "Cassa",
            "number": "Number",
            "data_val": "Data",
            "descrizione": "Descrizione",
            "evento": "Evento",
            "valore": "Valore grezzo",
        }
    )

    # ======================================================
    # TABELLA
    # ======================================================

    st.subheader(
        f"📋 Risultati: {len(tabella)}"
    )

    st.dataframe(
        tabella.style.apply(
            evidenzia_eventi,
            axis=1
        ),
        use_container_width=True,
        hide_index=True,
        height=650
    )

    # ======================================================
    # DOWNLOAD
    # ======================================================

    csv = (
        tabella
        .to_csv(
            index=False
        )
        .encode(
            "utf-8-sig"
        )
    )

    st.download_button(
        "📥 Scarica risultati CSV",
        data=csv,
        file_name="analisi_log_fde.csv",
        mime="text/csv"
    )