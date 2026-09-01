import streamlit as st
import pandas as pd
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# DATASET PRESENTI NEI LOG FDE
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
# DATA -> TESTO
# ==========================================================

DECODIFICHE = {

    # ------------------------------------------------------
    # SMOKE SENSOR
    # ------------------------------------------------------

    "ISMOKESENSSTATE": {
        "0": "NESSUN ALLARME",
        "1": "ALLARME TERMICO",
        "2": "ALLARME FUMO",
        "3": "ALLARME FUMO E TERMICO",
        "4": "FAULT",
        "5": "SENSORE DISABILITATO",
    },

    # ------------------------------------------------------
    # HVAC
    # ------------------------------------------------------

    "IHVACCMDSTATE": {
        "0": "STANDBY",
        "1": "HVAC SPENTO PER INCENDIO A BORDO",
        "2": "FAIL",
    },

    # ------------------------------------------------------
    # PORTE
    # ------------------------------------------------------

    "IGWAYDOORCMDSTATE": {
        "0": "STANDBY",
        "1": "CHIUSURA PORTA ATTIVA",
        "2": "FAIL",
    },

    # ------------------------------------------------------
    # PGR AREA MODE
    # ------------------------------------------------------

    "IPGRAREAMODE": {
        "1": "START",
        "2": "STANDBY",
        "3": "PRE-ALLARME",
        "4": "PRE-ATTIVAZIONE SPRINKLERS",
        "5": "ATTIVAZIONE SPRINKLERS",
        "6": "SCARICO DISABILITATO",
        "7": "TEST/MANUTENZIONE",
    },

    # ------------------------------------------------------
    # IO CARDS
    # ------------------------------------------------------

    "FIOCARDS": {
        "0": "OK",
        "1": "110V NON PRESENTE",
        "2": "FAULT",
        "3": "SCHEDA NON PRESENTE",
    },

    # ------------------------------------------------------
    # FIRE GENERAL ALARM
    # ------------------------------------------------------

    "IFIREGENERALALARM": {
        "0": "NESSUN ALLARME",
        "1": "ALLARME INCENDIO",
    },

    # ------------------------------------------------------
    # ELETTROVALVOLA DMX
    # ------------------------------------------------------

    "IELECTROVALVEDMX": {
        "0": "STANDBY",
        "1": "ELETTROVALVOLA MAU ATTIVA",
        "2": "FAIL",
    },

    # ------------------------------------------------------
    # SCU COM
    # ------------------------------------------------------

    "FSCUCOM": {
        "0": "COMUNICAZIONE TRA CENTRALINE OK",
        "1": "COMUNICAZIONE TRA CENTRALINE FALLITA",
    },

    # ------------------------------------------------------
    # CCU COM
    # ------------------------------------------------------

    "FCCUCOM": {
        "0": "COMUNICAZIONE CON CCU OK",
        "1": "COMUNICAZIONE CON CCU FALLITA",
    },

    # ------------------------------------------------------
    # FIRE SMOKE SENSOR
    # ------------------------------------------------------

    "FSMOKESENS": {
        "0": "OK",
        "1": "MANUTENZIONE RICHIESTA SU SENSORE",
        "2": "SENSORE SPORCO",
        "3": "FAULT",
        "4": "SENSORE NON PRESENTE",
    },

    # ------------------------------------------------------
    # AEROSOL
    # ------------------------------------------------------

    "FAEROSOL": {
        "0": "OK",
        "1": "CIRCUITO APERTO AEROSOL",
        "2": "VALORE INSTABILE AEROSOL",
        "3": "CANALE INSTABILE AEROSOL",
        "4": "COMANDO AEROSOL ATTIVO",
        "5": "24V NON PRESENTE",
    },

    # ------------------------------------------------------
    # AEROSOL CARTRIDGE
    # ------------------------------------------------------

    "IAEROCARTRIDGESTATE": {
        "0": "OK",
        "1": "CARTUCCIA ATTIVA",
        "2": "CARTUCCIA SPARATA",
        "3": "FAULT",
        "4": "NESSUNA CARTUCCIA",
    },

    # ------------------------------------------------------
    # CAR FIRE ALARM
    # ------------------------------------------------------

    "ICARFIREALARM": {
        "0": "NESSUN ALLARME",
        "1": "PRE-ALLARME AREA PASSEGGERI",
        "2": "ALLARME AREA PASSEGGERI",
        "3": "ALLARME AREA TECNICA",
        "4": "PRE-ALLARME AREA PASSEGGERI E ALLARME AREA TECNICA",
        "5": "ALLARME AREA TECNICA E PASSEGGERI",
    },

    # ------------------------------------------------------
    # ELECTROVALVES
    # ------------------------------------------------------

    "FELECTROVALVES": {
        "0": "ELETTROVALVOLA OK",
        "1": "CIRCUITO APERTO",
        "2": "VALORE INSTABILE",
        "3": "CANALE INSTABILE",
        "4": "24V NON PRESENTE",
    },

    # ------------------------------------------------------
    # TECH AREA MODE
    # ------------------------------------------------------

    "ITECHAREAMODE": {
        "1": "STARTING",
        "2": "STANDBY",
        "3": "ALLARME",
        "4": "SPEGNIMENTO FUOCO AREA TECNICA",
        "5": "TEST/MANUTENZIONE",
    },

    # ------------------------------------------------------
    # FIRE ON BOARD TX
    # ------------------------------------------------------

    "FFIREONBOARDTX": {
        "0": "NESSUN FUOCO A BORDO TRASMESSO",
        "1": "FUOCO A BORDO TRASMESSO",
    },

    # ------------------------------------------------------
    # FIRE ON BOARD TX ACCOPPIATA
    # ------------------------------------------------------

    "IFIREONBOARDTX": {
        "0": "ALLARME TRASMESSO IN ACCOPPIATA",
        "1": "NESSUN ALLARME TRASMESSO IN ACCOPPIATA",
    },

    # ------------------------------------------------------
    # SMOKE SENSOR LOOP
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # GENERAL SYSTEM MODE
    # ------------------------------------------------------

    "IGENSYSTEMMODE": {
        "0": "NON ALIMENTATO",
        "1": "SISTEMA IN SERVIZIO",
        "2": "SISTEMA DEGRADATO",
        "3": "SISTEMA FUORI SERVIZIO",
        "4": "INIZIALIZZAZIONE",
        "10": "MODALITA' TEST",
        "11": "MODALITA' CARICAMENTO SW",
    },

    # ------------------------------------------------------
    # SPEC SYSTEM OK MODE
    # ------------------------------------------------------

    "ISPECSYSTOKMODE": {
        "0": "MASTER",
        "1": "SLAVE",
    },

    # ------------------------------------------------------
    # MAU INPUT
    # ------------------------------------------------------

    "IMAUINPUTSTATE": {
        "0": "NON ATTIVO",
        "1": "ATTIVO",
    },
}


# ==========================================================
# DECODIFICA NUMBER MAU
# ==========================================================

DECODIFICA_NUMBER_MAU = {

    "0": "BASSA PRESSIONE",
    "1": "CONDOTTA ACQUA PRESSURIZZATA",
    "2": "BASSA PRESSIONE",
    "3": "CONDOTTA ACQUA PRESSURIZZATA",

}


# ==========================================================
# DECODIFICA NUMBER SENSORI FUMO
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
# COLORI EVENTI
# ==========================================================

COLORI_EVENTO = {

    "FUMO": "#ff7f50",

    "TERMICO": "#ff7f50",

    "FAULT_SMOKE": "#9e9e9e",

    "ALLARME INCENDIO": "#ff4d4d",

    "FUORI SERVIZIO": "#ff4d4d",

    "BASSA PRESSIONE": "#008f39",

    "CONDOTTA ACQUA PRESSURIZZATA": "#008f39",

    "NORMALE": "#808080",

}


# ==========================================================
# DECODIFICA CASSA
# ==========================================================

def decodifica_cassa(val):

    MAPPA_CASSA = {

        "1": "DM1",
        "2": "TT2",
        "3": "M3",
        "4": "T4",
        "5": "T5",
        "6": "M6",
        "7": "TT7",
        "8": "DM8",

    }

    return MAPPA_CASSA.get(str(val), val)


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
# PARSE DATO
# ==========================================================

def parse_dato(valore):

    valore = str(valore)

    coach = "-"
    number = "-"
    data = "-"

    # ------------------------------------------------------
    # COACH
    # ------------------------------------------------------

    m = re.search(
        r"COACH\s*N\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if m:
        coach = decodifica_cassa(m.group(1))

    # ------------------------------------------------------
    # NUMBER
    # ------------------------------------------------------

    m = re.search(
        r"NUMBER\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if m:
        number = m.group(1)

    # ------------------------------------------------------
    # DATA
    # ------------------------------------------------------

    m = re.search(
        r"DATA\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if m:
        data = m.group(1)

    return coach, number, data


# ==========================================================
# DECODIFICA DATA
# ==========================================================

def decodifica_data_segnale(
    segnale_norm,
    data_val
):

    seg = str(segnale_norm).upper()

    for key, mapping in DECODIFICHE.items():

        if seg.startswith(key):

            return mapping.get(
                str(data_val),
                data_val
            )

    return data_val


# ==========================================================
# TIMESTAMP
# ==========================================================

def parse_timestamp(ts_raw):

    if not ts_raw:
        return None

    ts_raw = " ".join(
        str(ts_raw).split()
    )

    formati = [

        "%a %b %d %H:%M:%S %Y",

        "%a %b %d %H:%M:%S.%f %Y",

        "%Y-%m-%d %H:%M:%S",

        "%d-%m-%Y %H:%M:%S",

    ]

    for formato in formati:

        try:

            return datetime.strptime(
                ts_raw,
                formato
            )

        except:

            pass

    return None


# ==========================================================
# PARSER GENERALE
# ==========================================================

def importa_log_streamlit(uploaded_file):

    dati = []

    timestamp = None
    dataset = None
    segnale = None

    try:

        contenuto = uploaded_file.getvalue()

        testo = contenuto.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        try:

            testo = uploaded_file.getvalue().decode(
                "latin-1",
                errors="ignore"
            )

        except Exception as e:

            st.error(
                f"Errore lettura file: {e}"
            )

            return pd.DataFrame()

    # ======================================================
    # LETTURA RIGHE
    # ======================================================

    for riga in testo.splitlines():

        r = riga.strip()

        # --------------------------------------------------
        # TIMESTAMP
        # --------------------------------------------------

        if r.startswith("------->"):

            timestamp = parse_timestamp(
                r.replace(
                    "------->",
                    ""
                ).strip()
            )

            dataset = None
            segnale = None

            continue

        if timestamp is None:

            continue

        # --------------------------------------------------
        # VALORE DEL SEGNALE
        # --------------------------------------------------

        if (
            segnale
            and r
            and "/" not in r
        ):

            valore = (
                r
                .replace(
                    "\x00",
                    ""
                )
                .strip()
            )

            dati.append(
                [
                    timestamp,
                    dataset,
                    segnale,
                    valore
                ]
            )

            segnale = None
            dataset = None

            continue

        # --------------------------------------------------
        # RICERCA DATASET
        # --------------------------------------------------

        for ds in DATASETS:

            token = ds + "/"

            if token in r:

                parte = r.split(
                    token,
                    1
                )[1]

                segnale = (
                    parte
                    .split(
                        ":",
                        1
                    )[0]
                    .strip()
                )

                dataset = ds

                break

    # ======================================================
    # DATAFRAME
    # ======================================================

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

    # ======================================================
    # NORMALIZZAZIONE
    # ======================================================

    df["segnale_norm"] = (
        df["segnale"]
        .astype(str)
        .apply(normalizza_segnale)
    )

    return df


# ==========================================================
# PREPARAZIONE EVENTI
# ==========================================================

def prepara_eventi(
    df,
    origine
):

    if df is None or df.empty:

        return pd.DataFrame()

    df = df.copy()

    df["origine"] = origem = origem if False else origine

    casse = []
    numbers = []
    date_valori = []
    descrizioni = []
    tags = []

    # ======================================================
    # ELABORAZIONE
    # ======================================================

    for _, r in df.iterrows():

        valore = str(
            r.get(
                "valore",
                ""
            )
        )

        segnale_norm = str(
            r.get(
                "segnale_norm",
                ""
            )
        )

        cassa, number, data_val = parse_dato(
            valore
        )

        # --------------------------------------------------
        # DECODIFICA DATA
        # --------------------------------------------------

        data_dec = decodifica_data_segnale(
            segnale_norm,
            data_val
        )

        segnale = segnale_norm.upper()

        # --------------------------------------------------
        # SENSORI FUMO
        # --------------------------------------------------

        if segnale.startswith(
            "ISMOKESENSSTATE"
        ):

            number = DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                number
            )

        elif segnale.startswith(
            "FSMOKESENS"
        ):

            number = DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                number
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
                data_val
            )

            number = DECODIFICA_NUMBER_MAU.get(
                str(number),
                data_dec
            )

        # --------------------------------------------------
        # TAG EVENTO
        # --------------------------------------------------

        tag = "NORMALE"

        # ==================================================
        # SENSORI FUMO
        # ==================================================

        if (
            segnale.startswith(
                "ISMOKESENSSTATE"
            )
            or
            segnale.startswith(
                "FSMOKESENS"
            )
        ):

            if data_dec in (
                "ALLARME FUMO",
                "ALLARME FUMO E TERMICO"
            ):

                tag = "FUMO"

            elif data_dec == "ALLARME TERMICO":

                tag = "TERMICO"

            elif data_dec == "FAULT":

                tag = "FAULT_SMOKE"

        # ==================================================
        # ALTRI SEGNALI
        # ==================================================

        else:

            if data_dec == "SISTEMA FUORI SERVIZIO":

                tag = "FUORI SERVIZIO"

            elif data_dec == "ALLARME INCENDIO":

                tag = "ALLARME INCENDIO"

            elif number == "BASSA PRESSIONE":

                tag = "BASSA PRESSIONE"

            elif number == "CONDOTTA ACQUA PRESSURIZZATA":

                tag = "CONDOTTA ACQUA PRESSURIZZATA"

        # --------------------------------------------------
        # SALVATAGGIO
        # --------------------------------------------------

        casse.append(cassa)

        numbers.append(number)

        date_valori.append(data_val)

        descrizioni.append(data_dec)

        tags.append(tag)

    # ======================================================
    # AGGIUNTA COLONNE
    # ======================================================

    df["cassa"] = casse

    df["number"] = numbers

    df["data_val"] = date_valori

    df["descrizione"] = descrizioni

    df["evento"] = tags

    return df


# ==========================================================
# FUNZIONE DI RICERCA
# ==========================================================

def applica_ricerca(
    df,
    ricerca
):

    if df.empty:

        return df

    if not ricerca:

        return df

    q = str(
        ricerca
    ).strip().lower()

    if not q:

        return df

    mask = pd.Series(
        False,
        index=df.index
    )

    colonne = [

        "origine",
        "dataset",
        "segnale_norm",
        "valore",
        "cassa",
        "number",
        "descrizione",
        "evento",

    ]

    for colonna in colonne:

        if colonna in df.columns:

            mask |= (
                df[colonna]
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                    regex=False
                )
            )

    return df[mask]


# ==========================================================
# PAGINA STREAMLIT
# ==========================================================

def fde_page():

    st.title(
        "📊 Analizzatore Log FDE"
    )

    st.caption(
        "Analisi interattiva dei log FDE DM1 + DM8"
    )

    st.divider()

    # ======================================================
    # CARICAMENTO FILE
    # ======================================================

    col1, col2 = st.columns(2)

    with col1:

        file_dm1 = st.file_uploader(
            "📥 Carica Log DM1",
            type=None,
            key="fde_dm1"
        )

    with col2:

        file_dm8 = st.file_uploader(
            "📥 Carica Log DM8",
            type=None,
            key="fde_dm8"
        )

    # ======================================================
    # CONTROLLO FILE
    # ======================================================

    if (
        file_dm1 is None
        and file_dm8 is None
    ):

        st.info(
            "Carica almeno un Log DM1 o DM8 per iniziare."
        )

        return

    # ======================================================
    # ELABORAZIONE FILE
    # ======================================================

    frames = []

    # ------------------------------------------------------
    # DM1
    # ------------------------------------------------------

    if file_dm1 is not None:

        with st.spinner(
            "🔄 Analisi Log DM1..."
        ):

            df_dm1 = importa_log_streamlit(
                file_dm1
            )

        if df_dm1.empty:

            st.warning(
                "⚠️ Il Log DM1 non contiene eventi riconosciuti."
            )

        else:

            df_dm1 = prepara_eventi(
                df_dm1,
                "DM1"
            )

            frames.append(
                df_dm1
            )

            st.success(
                f"✅ DM1: {len(df_dm1)} eventi"
            )

    # ------------------------------------------------------
    # DM8
    # ------------------------------------------------------

    if file_dm8 is not None:

        with st.spinner(
            "🔄 Analisi Log DM8..."
        ):

            df_dm8 = importa_log_streamlit(
                file_dm8
            )

        if df_dm8.empty:

            st.warning(
                "⚠️ Il Log DM8 non contiene eventi riconosciuti."
            )

        else:

            df_dm8 = prepara_eventi(
                df_dm8,
                "DM8"
            )

            frames.append(
                df_dm8
            )

            st.success(
                f"✅ DM8: {len(df_dm8)} eventi"
            )

    # ======================================================
    # CONTROLLO
    # ======================================================

    if not frames:

        st.error(
            "❌ Nessun evento riconosciuto nei file caricati."
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
    # RANGE DATE
    # ======================================================

    dmin = df[
        "timestamp"
    ].min().date()

    dmax = df[
        "timestamp"
    ].max().date()

    st.divider()

    st.subheader(
        "🔎 Filtri"
    )

    col1, col2, col3, col4 = st.columns(4)

    # ======================================================
    # DATA DA
    # ======================================================

    with col1:

        data_da = st.date_input(
            "📅 Da",
            value=dmin,
            min_value=dmin,
            max_value=dmax,
            key="fde_da"
        )

    # ======================================================
    # DATA A
    # ======================================================

    with col2:

        data_a = st.date_input(
            "📅 A",
            value=dmax,
            min_value=dmin,
            max_value=dmax,
            key="fde_a"
        )

    # ======================================================
    # ORIGINE
    # ======================================================

    with col3:

        origini = st.multiselect(
            "💻 Origine",
            [
                "DM1",
                "DM8"
            ],
            default=[
                "DM1",
                "DM8"
            ],
            key="fde_orig"
        )

    # ======================================================
    # EVENTI
    # ======================================================

    with col4:

        eventi_disponibili = sorted(
            df[
                "evento"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        eventi_selezionati = st.multiselect(
            "🚨 Tipo evento",
            eventi_disponibili,
            key="fde_ev"
        )

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(
        "🔍 Cerca",
        placeholder=(
            "Segnale, dataset, valore, cassa, "
            "sensore, descrizione..."
        ),
        key="fde_search"
    )

    # ======================================================
    # FILTRO DATE
    # ======================================================

    da = datetime.combine(
        data_da,
        datetime.min.time()
    )

    a = datetime.combine(
        data_a,
        datetime.max.time()
    )

    out = df[
        (
            df["timestamp"] >= da
        )
        &
        (
            df["timestamp"] <= a
        )
    ].copy()

    # ======================================================
    # FILTRO ORIGINE
    # ======================================================

    if origini:

        out = out[
            out["origine"].isin(
                origini
            )
        ]

    # ======================================================
    # FILTRO EVENTO
    # ======================================================

    if eventi_selezionati:

        out = out[
            out["evento"].isin(
                eventi_selezionati
            )
        ]

    # ======================================================
    # RICERCA TESTUALE
    # ======================================================

    out = applica_ricerca(
        out,
        ricerca
    )

    # ======================================================
    # METRICHE
    # ======================================================

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📋 Eventi",
        len(out)
    )

    col2.metric(
        "💻 DM1",
        int(
            (
                out["origine"] == "DM1"
            ).sum()
        )
    )

    col3.metric(
        "💻 DM8",
        int(
            (
                out["origine"] == "DM8"
            ).sum()
        )
    )

    col4.metric(
        "🚨 Allarmi / Fault",
        int(
            (
                out["evento"] != "NORMALE"
            ).sum()
        )
    )

    # ======================================================
    # NESSUN RISULTATO
    # ======================================================

    if out.empty:

        st.warning(
            "⚠️ Nessun evento trovato "
            "con i filtri selezionati."
        )

        return

    # ======================================================
    # TABS
    # ======================================================

    tab1, tab2 = st.tabs(
        [
            "📈 Timeline",
            "📋 Eventi"
        ]
    )

    # ======================================================
# TAB TIMELINE
# ======================================================

with tab1:

    st.subheader(
        "📈 Timeline FDE"
    )

    plot = out.copy()

    # ==================================================
    # ORDINE CRONOLOGICO
    # ==================================================

    plot = plot.sort_values(
        "timestamp"
    ).copy()

    # ==================================================
    # SEGNALI
    # ==================================================

    segnali = (
        plot["segnale_norm"]
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    # ==================================================
    # POSIZIONE DEI SEGNALI
    # ==================================================

    posizione_segnale = {
        segnale: i
        for i, segnale in enumerate(segnali)
    }

    fig = go.Figure()

    # ==================================================
    # TIMELINE A ONDA QUADRA
    # ==================================================

    for segnale in segnali:

        dati = plot[
            plot["segnale_norm"].astype(str)
            == segnale
        ].sort_values(
            "timestamp"
        ).copy()

        if dati.empty:
            continue

        x = []
        y = []
        colori = []

        base = posizione_segnale[segnale]

        # --------------------------------------------------
        # COSTRUZIONE ONDA
        # --------------------------------------------------

        precedente_y = base

        for _, riga in dati.iterrows():

            timestamp = riga["timestamp"]

            # ----------------------------------------------
            # VALORE
            # ----------------------------------------------

            valore = riga.get(
                "data_val",
                0
            )

            try:
                valore_num = float(
                    str(valore)
                    .replace(",", ".")
                )
            except:
                valore_num = 0

            # ----------------------------------------------
            # ONDA:
            #
            # 0 -> livello basso
            # 1 -> livello alto
            #
            # Per valori > 1 manteniamo comunque
            # il livello alto.
            # ----------------------------------------------

            if valore_num == 0:

                livello = base

            else:

                livello = base + 0.7

            evento = str(
                riga.get(
                    "evento",
                    "NORMALE"
                )
            )

            colore = COLORI_EVENTO.get(
                evento,
                COLORI_EVENTO["NORMALE"]
            )

            # ----------------------------------------------
            # PRIMO PUNTO
            # ----------------------------------------------

            if not x:

                x.append(timestamp)
                y.append(livello)
                colori.append(colore)

            else:

                # ------------------------------------------
                # MANTIENI IL LIVELLO PRECEDENTE FINO
                # ALL'ISTANTE DEL CAMBIO
                # ------------------------------------------

                x.append(timestamp)
                y.append(precedente_y)
                colori.append(colore)

                # ------------------------------------------
                # SALITA / DISCESA VERTICALE
                # ------------------------------------------

                x.append(timestamp)
                y.append(livello)
                colori.append(colore)

            precedente_y = livello

        # ==================================================
        # DISEGNO DELLA LINEA
        # ==================================================

        # Plotly non permette un colore diverso per ogni
        # segmento della stessa linea in modo semplice.
        # Creiamo quindi i segmenti separati per colore.

        for i in range(
            len(x) - 1
        ):

            fig.add_trace(
                go.Scatter(
                    x=[
                        x[i],
                        x[i + 1]
                    ],

                    y=[
                        y[i],
                        y[i + 1]
                    ],

                    mode="lines",

                    line=dict(
                        color=colori[i],
                        width=3,
                        shape="linear"
                    ),

                    hoverinfo="skip",

                    showlegend=False
                )
            )

        # ==================================================
        # PUNTI INVISIBILI PER HOVER
        # ==================================================

        hover_text = []

        for _, riga in dati.iterrows():

            timestamp = riga["timestamp"]

            hover_text.append(
                f"<b>Data/Ora:</b> "
                f"{timestamp.strftime('%d-%m-%Y %H:%M:%S')}"
                f"<br>"
                f"<b>Origine:</b> "
                f"{riga.get('origine', '')}"
                f"<br>"
                f"<b>Dataset:</b> "
                f"{riga.get('dataset', '')}"
                f"<br>"
                f"<b>Segnale:</b> "
                f"{segnale}"
                f"<br>"
                f"<b>Cassa:</b> "
                f"{riga.get('cassa', '')}"
                f"<br>"
                f"<b>Number:</b> "
                f"{riga.get('number', '')}"
                f"<br>"
                f"<b>Valore:</b> "
                f"{riga.get('data_val', '')}"
                f"<br>"
                f"<b>Descrizione:</b> "
                f"{riga.get('descrizione', '')}"
                f"<br>"
                f"<b>Evento:</b> "
                f"{riga.get('evento', '')}"
            )

        # ==================================================
        # HOVER
        # ==================================================

        fig.add_trace(
            go.Scatter(
                x=dati["timestamp"],
                y=[
                    (
                        base + 0.7
                        if str(v) not in ["0", "0.0"]
                        else base
                    )
                    for v in dati["data_val"]
                ],

                mode="markers",

                marker=dict(
                    size=7,
                    opacity=0
                ),

                text=hover_text,

                hoverinfo="text",

                showlegend=False
            )
        )

    # ======================================================
    # LEGENDA COLORI
    # ======================================================

    for evento, colore in COLORI_EVENTO.items():

        # Mostra in legenda solo gli eventi presenti
        if evento not in plot["evento"].astype(str).values:
            continue

        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],

                mode="lines",

                line=dict(
                    color=colore,
                    width=4
                ),

                name=evento,

                showlegend=True
            )
        )

    # ======================================================
    # ALTEZZA
    # ======================================================

    altezza = max(
        550,
        min(
            1100,
            350 + len(segnali) * 35
        )
    )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(

        height=altezza,

        hovermode="closest",

        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10
        ),

        legend_title_text="Tipo evento",

        xaxis=dict(
            title="Data / Ora",

            type="date",

            rangeslider=dict(
                visible=True
            ),

            showgrid=True
        ),

        yaxis=dict(

            title="Segnale",

            tickmode="array",

            tickvals=[
                posizione_segnale[s]
                for s in segnali
            ],

            ticktext=segnali,

            autorange="reversed",

            showgrid=True,

            zeroline=False
        )
    )

    # ======================================================
    # VISUALIZZAZIONE
    # ======================================================

    st.plotly_chart(

        fig,

        use_container_width=True,

        config={

            "displaylogo":
                False,

            "scrollZoom":
                True,

            "responsive":
                True,

        }

    )

    # ======================================================
    # TAB EVENTI
    # ======================================================

    with tab2:

        st.subheader(
            f"📋 Eventi ({len(out)})"
        )

        tabella = out.copy()

        tabella["Time"] = (
            tabella[
                "timestamp"
            ]
            .dt
            .strftime(
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
        ]

        tabella = tabella.rename(

            columns={

                "origine":
                    "Origine",

                "dataset":
                    "Dataset",

                "segnale_norm":
                    "Segnale",

                "cassa":
                    "Cassa",

                "number":
                    "Number",

                "data_val":
                    "Data",

                "descrizione":
                    "Descrizione",

                "evento":
                    "Evento",

                "valore":
                    "Valore grezzo",

            }

        )

        # --------------------------------------------------
        # TABELLA
        # --------------------------------------------------

        st.dataframe(

            tabella,

            use_container_width=True,

            hide_index=True,

            height=600

        )

        # --------------------------------------------------
        # DOWNLOAD CSV
        # --------------------------------------------------

        csv = tabella.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(

            "📥 Scarica risultati CSV",

            data=csv,

            file_name="analisi_fde.csv",

            mime="text/csv",

            use_container_width=False

        )
