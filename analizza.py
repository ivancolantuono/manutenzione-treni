import streamlit as st
import pandas as pd
from datetime import datetime
import re


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

st.set_page_config(
    page_title="Analizza Log FDE",
    page_icon="🔎",
    layout="wide"
)


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
# DECODIFICA NUMBER MAU
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

    "0": "SD1",
    "1": "SD2",
    "2": "SD3",
    "3": "SD4",
    "4": "SD5",
    "5": "SD6",
    "6": "SD7",
    "7": "SD8",
    "8": "SD9",
    "9": "SD10",

    "10": "SD11",
    "11": "SD12",
    "12": "SD13",
    "13": "SD14",
    "14": "SD15",
    "15": "SD16",
    "16": "SD17",
    "17": "SD18",
    "18": "SD19",
    "19": "SD20",

    "20": "SD21",
    "21": "SD22",
    "22": "SD23",
    "23": "SD24",
    "24": "SD25",
    "25": "SD26",
    "26": "SD27",
    "27": "SD28",
    "28": "SD29",
    "29": "SD30",

    "30": "SD31",
    "31": "SD32",
    "32": "SD33",
    "33": "SD34",
    "34": "SD35",
    "35": "SD36",
    "36": "SD37",
    "37": "SD38",
    "38": "SD39",
    "39": "SD40",

    "40": "SD41",
    "41": "SD42",
    "42": "SD43",
    "43": "SD44",
    "44": "SD45",
    "45": "SD46",
    "46": "SD47",
    "47": "SD48",
    "48": "SD49",
    "49": "SD50",

    "50": "SD51",
    "51": "SD52",
    "52": "SD53",
    "53": "SD54",
    "54": "SD55",
    "55": "SD56",
    "56": "SD57",
    "57": "SD58",
    "58": "SD59",
    "59": "SD60",

    "60": "SD61",
    "61": "SD62",
    "62": "SD63",
    "63": "SD64",
    "64": "SD65",
    "65": "SD66",
    "66": "SD67",
    "67": "SD68",
    "68": "SD69",
    "69": "SD70",

    "70": "SD71",
    "71": "SD72",
    "72": "SD73",
    "73": "SD74",
}


# ==========================================================
# DECODIFICA CASSA
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
# DECODIFICA CASSA
# ==========================================================

def decodifica_cassa(valore):

    return DECODIFICA_CASSA.get(
        str(valore),
        str(valore)
    )


# ==========================================================
# NORMALIZZA SEGNALE
# ==========================================================

def normalizza_segnale(segnale):

    if segnale is None:
        return ""

    segnale = str(
        segnale
    ).strip()

    segnale = re.split(
        r"[\[_]",
        segnale
    )[0]

    return segnale.strip()


# ==========================================================
# PARSE TIMESTAMP
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

    valore = str(
        valore
    )

    cassa = "-"
    number = "-"
    data_val = "-"

    # ------------------------------------------------------
    # COACH N
    # ------------------------------------------------------

    match = re.search(
        r"COACH\s*N\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if match:

        cassa = decodifica_cassa(
            match.group(1)
        )

    # ------------------------------------------------------
    # NUMBER
    # ------------------------------------------------------

    match = re.search(
        r"NUMBER\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if match:

        number = match.group(1)

    # ------------------------------------------------------
    # DATA
    # ------------------------------------------------------

    match = re.search(
        r"DATA\s*:\s*(\d+)",
        valore,
        re.IGNORECASE
    )

    if match:

        data_val = match.group(1)

    return (
        cassa,
        number,
        data_val
    )


# ==========================================================
# DECODIFICA SEGNALE
# ==========================================================

def decodifica_segnale(
    segnale,
    valore
):

    segnale = str(
        segnale
    ).upper()

    cassa, number, data_val = estrai_parametri(
        valore
    )

    descrizione = str(
        data_val
    )

    # ------------------------------------------------------
    # DECODIFICA DATA
    # ------------------------------------------------------

    for nome, mapping in DECODIFICHE.items():

        if segnale.startswith(nome):

            descrizione = mapping.get(
                str(data_val),
                str(data_val)
            )

            break

    # ------------------------------------------------------
    # SENSORI FUMO
    # ------------------------------------------------------

    if (
        segnale.startswith(
            "ISMOKESENSSTATE"
        )
        or
        segnale.startswith(
            "FSMOKESENS"
        )
    ):

        number_decodificato = (
            DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                str(number)
            )
        )

    # ------------------------------------------------------
    # MAU
    # ------------------------------------------------------

    elif segnale.startswith(
        "IMAUINPUTSTATE"
    ):

        number_decodificato = (
            DECODIFICA_NUMBER_MAU.get(
                str(number),
                str(number)
            )
        )

    else:

        number_decodificato = str(
            number
        )

    return (
        cassa,
        number_decodificato,
        data_val,
        descrizione
    )


# ==========================================================
# CLASSIFICA EVENTO
# ==========================================================

def classifica_evento(
    segnale,
    descrizione,
    number
):

    segnale = str(
        segnale
    ).upper()

    descrizione = str(
        descrizione
    ).upper()

    number = str(
        number
    ).upper()

    # ------------------------------------------------------
    # FUMO
    # ------------------------------------------------------

    if (
        "ALLARME FUMO" in descrizione
    ):

        return "FUMO"

    # ------------------------------------------------------
    # TERMICO
    # ------------------------------------------------------

    if (
        "ALLARME TERMICO" in descrizione
    ):

        return "TERMICO"

    # ------------------------------------------------------
    # ALLARME INCENDIO
    # ------------------------------------------------------

    if (
        "ALLARME INCENDIO" in descrizione
    ):

        return "ALLARME INCENDIO"

    # ------------------------------------------------------
    # BASSA PRESSIONE
    # ------------------------------------------------------

    if (
        "BASSA PRESSIONE" in number
    ):

        return "BASSA PRESSIONE"

    # ------------------------------------------------------
    # ACQUA PRESSURIZZATA
    # ------------------------------------------------------

    if (
        "CONDOTTA ACQUA PRESSURIZZATA"
        in number
    ):

        return "CONDOTTA ACQUA PRESSURIZZATA"

    # ------------------------------------------------------
    # FUORI SERVIZIO
    # ------------------------------------------------------

    if (
        "FUORI SERVIZIO" in descrizione
    ):

        return "FUORI SERVIZIO"

    # ------------------------------------------------------
    # FAULT
    # ------------------------------------------------------

    if (
        descrizione == "FAULT"
        or
        "FAULT" in descrizione
        or
        "FAIL" in descrizione
    ):

        return "FAULT"

    return ""


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

    except Exception:

        testo = contenuto.decode(
            "latin-1",
            errors="ignore"
        )

    # ======================================================
    # LETTURA RIGHE
    # ======================================================

    for riga in testo.splitlines():

        riga = riga.strip()

        if not riga:
            continue

        # ==================================================
        # TIMESTAMP
        # ==================================================

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

        # ==================================================
        # DATASET / SEGNALE
        # ==================================================

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

                segnale_corrente = (
                    normalizza_segnale(
                        segnale
                    )
                )

                trovato = True

                break

        if trovato:
            continue

        # ==================================================
        # VALORE
        # ==================================================

        if (
            dataset_corrente
            and
            segnale_corrente
        ):

            valore = riga

            dati.append({

                "timestamp":
                    timestamp,

                "dataset":
                    dataset_corrente,

                "segnale":
                    segnale_corrente,

                "valore":
                    valorе

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

    df[
        "timestamp"
    ] = pd.to_datetime(
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
    data_valori = []
    descrizioni = []
    eventi = []

    for _, riga in df.iterrows():

        (
            cassa,
            number,
            data_val,
            descrizione
        ) = decodifica_segnale(

            riga["segnale"],

            riga["valore"]
        )

        evento = classifica_evento(

            riga["segnale"],

            descrizione,

            number
        )

        casse.append(
            cassa
        )

        numbers.append(
            number
        )

        data_valori.append(
            data_val
        )

        descrizioni.append(
            descrizione
        )

        eventi.append(
            evento
        )

    df["cassa"] = casse

    df["number"] = numbers

    df["data_val"] = data_valori

    df["descrizione"] = descrizioni

    df["evento"] = eventi

    return df


# ==========================================================
# COLORAZIONE RIGHE
# ==========================================================

def colora_riga(row):

    evento = str(
        row.get(
            "Evento",
            ""
        )
    ).upper().strip()

    # ------------------------------------------------------
    # ALLARME INCENDIO
    # ------------------------------------------------------

    if evento == "ALLARME INCENDIO":

        return [
            "background-color: #ff0000; color: white; font-weight: bold"
        ] * len(row)

    # ------------------------------------------------------
    # FUMO
    # ------------------------------------------------------

    if evento == "FUMO":

        return [
            "background-color: #ff9500; color: black; font-weight: bold"
        ] * len(row)

    # ------------------------------------------------------
    # TERMICO
    # ------------------------------------------------------

    if evento == "TERMICO":

        return [
            "background-color: #ff9500; color: black; font-weight: bold"
        ] * len(row)

    # ------------------------------------------------------
    # BASSA PRESSIONE
    # ------------------------------------------------------

    if evento == "BASSA PRESSIONE":

        return [
            "background-color: #007aff; color: white; font-weight: bold"
        ] * len(row)

    # ------------------------------------------------------
    # ACQUA PRESSURIZZATA
    # ------------------------------------------------------

    if evento == "CONDOTTA ACQUA PRESSURIZZATA":

        return [
            "background-color: #34c759; color: white; font-weight: bold"
        ] * len(row)

    # ------------------------------------------------------
    # FUORI SERVIZIO
    # ------------------------------------------------------

    if evento == "FUORI SERVIZIO":

        return [
            "background-color: #af52de; color: white; font-weight: bold"
        ] * len(row)

    # ------------------------------------------------------
    # FAULT
    # ------------------------------------------------------

    if evento == "FAULT":

        return [
            "background-color: #8e8e93; color: white; font-weight: bold"
        ] * len(row)

    return [
        ""
    ] * len(row)


# ==========================================================
# PAGINA ANALIZZA
# ==========================================================

def analizza_page():

    st.title(
        "🔎 Analizza Log FDE"
    )

    st.caption(
        "Analisi completa dei log DM1 e DM8"
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
            key="analizza_file_dm1"
        )

    with col2:

        file_dm8 = st.file_uploader(
            "📥 Carica Log DM8",
            type=None,
            key="analizza_file_dm8"
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
    # LETTURA
    # ======================================================

    frames = []

    # ======================================================
    # DM1
    # ======================================================

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
                f"✅ DM1: {len(df_dm1)} eventi"
            )

        else:

            st.warning(
                "⚠️ Nessun evento riconosciuto nel DM1."
            )

    # ======================================================
    # DM8
    # ======================================================

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
                f"✅ DM8: {len(df_dm8)} eventi"
            )

        else:

            st.warning(
                "⚠️ Nessun evento riconosciuto nel DM8."
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
    # METRICHE GENERALI
    # ======================================================

    numero_eventi = len(df)

    numero_dm1 = int(
        (
            df["origine"]
            == "DM1"
        ).sum()
    )

    numero_dm8 = int(
        (
            df["origine"]
            == "DM8"
        ).sum()
    )

    numero_importanti = int(
        (
            df["evento"]
            != ""
        ).sum()
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📋 Eventi totali",
            numero_eventi
        )

    with col2:

        st.metric(
            "DM1",
            numero_dm1
        )

    with col3:

        st.metric(
            "DM8",
            numero_dm8
        )

    with col4:

        st.metric(
            "🚨 Eventi importanti",
            numero_importanti
        )

    # ======================================================
    # LEGENDA
    # ======================================================

    st.divider()

    st.subheader(
        "🎨 Legenda eventi"
    )

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        st.markdown(
            "🔴 **ALLARME INCENDIO**"
        )

    with col2:
        st.markdown(
            "🟠 **FUMO / TERMICO**"
        )

    with col3:
        st.markdown(
            "🔵 **BASSA PRESSIONE**"
        )

    with col4:
        st.markdown(
            "🟢 **ACQUA PRESSURIZZATA**"
        )

    with col5:
        st.markdown(
            "🟣 **FUORI SERVIZIO**"
        )

    with col6:
        st.markdown(
            "⚫ **FAULT**"
        )

    with col7:
        st.markdown(
            "⚪ **NORMALE**"
        )

    # ======================================================
    # TABELLA COMPLETA
    # ======================================================

    st.divider()

    st.subheader(
        f"📋 TUTTI GLI EVENTI — {len(df)}"
    )

    tabella_completa = df.copy()

    tabella_completa["Time"] = (
        tabella_completa[
            "timestamp"
        ]
        .dt.strftime(
            "%d-%m-%Y // %H:%M:%S"
        )
    )

    tabella_completa = tabella_completa[
        [
            "Time",
            "origine",
            "dataset",
            "segnale",
            "cassa",
            "number",
            "data_val",
            "descrizione",
            "evento",
            "valore",
        ]
    ].copy()

    tabella_completa = tabella_completa.rename(
        columns={
            "origine":
                "Origine",

            "dataset":
                "Dataset",

            "segnale":
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

    st.dataframe(

        tabella_completa.style.apply(
            colora_riga,
            axis=1
        ),

        use_container_width=True,

        hide_index=True,

        height=700
    )

    # ======================================================
    # DOWNLOAD COMPLETO
    # ======================================================

    csv_completo = (
        tabella_completa
        .to_csv(
            index=False
        )
        .encode(
            "utf-8-sig"
        )
    )

    st.download_button(

        "📥 Scarica tutti gli eventi",

        data=csv_completo,

        file_name="analisi_completa_fde.csv",

        mime="text/csv",

        key="download_completo_fde"
    )

    # ======================================================
    # FILTRI
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Filtra gli eventi"
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
            [
                "DM1",
                "DM8"
            ],
            default=[
                "DM1",
                "DM8"
            ],
            key="analizza_origine"
        )

    # ======================================================
    # EVENTI
    # ======================================================

    eventi_disponibili = sorted(
        [
            x
            for x in df[
                "evento"
            ]
            .dropna()
            .astype(str)
            .unique()
            if x
        ]
    )

    eventi_selezionati = st.multiselect(

        "🚨 Tipo evento",

        eventi_disponibili,

        key="analizza_tipo_evento"
    )

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(

        "🔍 Ricerca",

        placeholder=(
            "Segnale, sensore, "
            "cassa, number, "
            "allarme..."
        ),

        key="analizza_ricerca"
    )

    # ======================================================
    # APPLICA FILTRI
    # ======================================================

    data_da_dt = datetime.combine(
        data_da,
        datetime.min.time()
    )

    data_a_dt = datetime.combine(
        data_a,
        datetime.max.time()
    )

    filtrato = df[
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

    # ------------------------------------------------------
    # ORIGINE
    # ------------------------------------------------------

    if origini:

        filtrato = filtrato[
            filtrato[
                "origine"
            ].isin(
                origini
            )
        ]

    # ------------------------------------------------------
    # EVENTO
    # ------------------------------------------------------

    if eventi_selezionati:

        filtrato = filtrato[
            filtrato[
                "evento"
            ].isin(
                eventi_selezionati
            )
        ]

    # ------------------------------------------------------
    # RICERCA
    # ------------------------------------------------------

    if ricerca:

        testo_ricerca = ricerca.lower().strip()

        colonne_ricerca = [

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
            index=filtrato.index
        )

        for colonna in colonne_ricerca:

            mask |= (
                filtrato[
                    colonna
                ]
                .astype(str)
                .str.lower()
                .str.contains(
                    testo_ricerca,
                    regex=False,
                    na=False
                )
            )

        filtrato = filtrato[
            mask
        ]

    # ======================================================
    # RISULTATI FILTRATI
    # ======================================================

    st.divider()

    st.subheader(
        f"🔎 Risultati filtrati: {len(filtrato)}"
    )

    if filtrato.empty:

        st.warning(
            "⚠️ Nessun evento corrisponde "
            "ai filtri selezionati."
        )

    else:

        tabella_filtrata = filtrato.copy()

        tabella_filtrata["Time"] = (
            tabella_filtrata[
                "timestamp"
            ]
            .dt.strftime(
                "%d-%m-%Y // %H:%M:%S"
            )
        )

        tabella_filtrata = tabella_filtrata[
            [
                "Time",
                "origine",
                "dataset",
                "segnale",
                "cassa",
                "number",
                "data_val",
                "descrizione",
                "evento",
                "valore",
            ]
        ].copy()

        tabella_filtrata = tabella_filtrata.rename(
            columns={
                "origine":
                    "Origine",

                "dataset":
                    "Dataset",

                "segnale":
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

        st.dataframe(

            tabella_filtrata.style.apply(
                colora_riga,
                axis=1
            ),

            use_container_width=True,

            hide_index=True,

            height=600
        )

        # --------------------------------------------------
        # DOWNLOAD FILTRATI
        # --------------------------------------------------

        csv_filtrato = (
            tabella_filtrata
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )

        st.download_button(

            "📥 Scarica eventi filtrati",

            data=csv_filtrato,

            file_name="eventi_filtrati_fde.csv",

            mime="text/csv",

            key="download_filtrati_fde"
        )
