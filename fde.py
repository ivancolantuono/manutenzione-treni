import streamlit as st
import pandas as pd
import re
from datetime import datetime
import plotly.graph_objects as go


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
# DECODIFICA CASSE
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


def decodifica_cassa(valore):

    return DECODIFICA_CASSA.get(
        str(valore).strip(),
        str(valore)
    )


# ==========================================================
# DECODIFICA NUMBER SENSORI FUMO
# ==========================================================

DECODIFICA_NUMBER_SMOKE = {

    str(i): f"SD{i + 1}"
    for i in range(74)
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
# COLORI
# ==========================================================

COLORI_EVENTO = {

    "SENSORE FUMO": "#ff3b30",

    "ALLARME INCENDIO": "#ff0000",

    "BASSA PRESSIONE": "#007aff",

    "CONDOTTA ACQUA PRESSURIZZATA": "#34c759",

}


# ==========================================================
# NORMALIZZAZIONE SEGNALE
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

        "%d/%m/%Y %H:%M:%S",

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

        data = match.group(1)

    return cassa, number, data


# ==========================================================
# DECODIFICA SEGNALE
# ==========================================================

def decodifica_segnale(
    segnale,
    valore
):

    segnale = str(
        segnale
    ).upper().strip()

    valore = str(
        valore
    )

    mapping = None

    for nome, valori in DECODIFICHE.items():

        if segnale.startswith(nome):

            mapping = valori
            break

    cassa, number, data = estrai_parametri(
        valore
    )

    descrizione = data

    if mapping:

        descrizione = mapping.get(
            str(data),
            str(data)
        )

    # ======================================================
    # SENSORI FUMO
    # ======================================================

    if segnale.startswith(
        "ISMOKESENSSTATE"
    ):

        number_decodificato = (
            DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                str(number)
            )
        )

    # ======================================================
    # DIAGNOSTICA SENSORI FUMO
    # ======================================================

    elif segnale.startswith(
        "FSMOKESENS"
    ):

        number_decodificato = (
            DECODIFICA_NUMBER_SMOKE.get(
                str(number),
                str(number)
            )
        )

    # ======================================================
    # MAU
    # ======================================================

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
        data,
        descrizione
    )


# ==========================================================
# CLASSIFICAZIONE DEGLI EVENTI IMPORTANTI
# ==========================================================

def classifica_evento(
    segnale,
    number,
    descrizione
):

    segnale = str(
        segnale
    ).upper()

    number = str(
        number
    ).upper()

    descrizione = str(
        descrizione
    ).upper()

    # ======================================================
    # SENSORE FUMO
    # ======================================================

    if (
        segnale.startswith("ISMOKESENSSTATE")
        and
        (
            "ALLARME FUMO" in descrizione
            or
            "ALLARME TERMICO" in descrizione
            or
            "FUMO E TERMICO" in descrizione
        )
    ):

        return "SENSORE FUMO"

    # ======================================================
    # ALLARME INCENDIO
    # ======================================================

    if (
        "ALLARME INCENDIO" in descrizione
        or
        (
            segnale.startswith(
                "IFIREGENERALALARM"
            )
            and
            descrizione != "NESSUN ALLARME"
        )
        or
        (
            segnale.startswith(
                "ICARFIREALARM"
            )
            and
            "ALLARME" in descrizione
        )
    ):

        return "ALLARME INCENDIO"

    # ======================================================
    # BASSA PRESSIONE
    # ======================================================

    if (
        "BASSA PRESSIONE" in descrizione
        or
        (
            segnale.startswith(
                "IMAUINPUTSTATE"
            )
            and
            number in [
                "BASSA PRESSIONE"
            ]
        )
    ):

        return "BASSA PRESSIONE"

    # ======================================================
    # ACQUA PRESSURIZZATA
    # ======================================================

    if (
        "CONDOTTA ACQUA PRESSURIZZATA"
        in descrizione
        or
        (
            segnale.startswith(
                "IMAUINPUTSTATE"
            )
            and
            number
            == "CONDOTTA ACQUA PRESSURIZZATA"
        )
    ):

        return "CONDOTTA ACQUA PRESSURIZZATA"

    return None


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

    try:

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

    except Exception as e:

        st.error(
            f"Errore lettura file: {e}"
        )

        return pd.DataFrame()

    # ======================================================
    # RIGHE
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
        subset=["timestamp"]
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
            number,
            descrizione
        )

        casse.append(cassa)

        numbers.append(number)

        date_valori.append(data)

        descrizioni.append(descrizione)

        eventi.append(evento)

    df["cassa"] = casse

    df["number"] = numbers

    df["data_val"] = date_valori

    df["descrizione"] = descrizioni

    df["evento"] = eventi

    return df


# ==========================================================
# FILTRO EVENTI IMPORTANTI
# ==========================================================

def filtra_eventi_importanti(df):

    if df.empty:
        return df

    eventi_validi = [

        "SENSORE FUMO",

        "ALLARME INCENDIO",

        "BASSA PRESSIONE",

        "CONDOTTA ACQUA PRESSURIZZATA",

    ]

    return df[
        df["evento"].isin(
            eventi_validi
        )
    ].copy()


# ==========================================================
# RICERCA
# ==========================================================

def filtra_ricerca(
    df,
    ricerca
):

    if not ricerca:
        return df

    ricerca = str(
        ricerca
    ).lower().strip()

    if not ricerca:
        return df

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

        if colonna in df.columns:

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
# TIMELINE A ONDA QUADRA
# ==========================================================

def crea_timeline(df):

    fig = go.Figure()

    if df.empty:
        return fig

    df = df.sort_values("timestamp").copy()

    # ======================================================
    # CATEGORIE
    # ======================================================

    categorie = [
        "SENSORE FUMO",
        "ALLARME INCENDIO",
        "BASSA PRESSIONE",
        "CONDOTTA ACQUA PRESSURIZZATA",
    ]

    # Posizione delle 4 righe
    y_map = {
        "SENSORE FUMO": 3,
        "ALLARME INCENDIO": 2,
        "BASSA PRESSIONE": 1,
        "CONDOTTA ACQUA PRESSURIZZATA": 0,
    }

    # ======================================================
    # COLORI
    # ======================================================

    colori = {
        "SENSORE FUMO": "#ff3b30",
        "ALLARME INCENDIO": "#ff0000",
        "BASSA PRESSIONE": "#007aff",
        "CONDOTTA ACQUA PRESSURIZZATA": "#34c759",
    }

    # ======================================================
    # LEGENDA
    # ======================================================

    for categoria in categorie:

        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                line=dict(
                    color=colori[categoria],
                    width=4
                ),
                name=categoria,
                showlegend=True
            )
        )

    # ======================================================
    # CREAZIONE ONDE
    # ======================================================

    for categoria in categorie:

        dati = df[
            df["evento"] == categoria
        ].sort_values("timestamp").copy()

        if dati.empty:
            continue

        base = y_map[categoria]

        # --------------------------------------------------
        # ONDA:
        #
        # 0 = base
        # 1 = base + 0.65
        #
        # Usiamo "hv" per ottenere una vera onda quadra.
        # --------------------------------------------------

        x = []
        y = []

        testi = []

        stato_precedente = 0

        for _, riga in dati.iterrows():

            timestamp = riga["timestamp"]

            # ==================================================
            # DETERMINAZIONE STATO
            # ==================================================

            stato = 1

            # ==================================================
            # PUNTO PRECEDENTE
            # ==================================================

            if not x:

                x.append(timestamp)
                y.append(base)

            # ==================================================
            # SALITA
            # ==================================================

            if stato == 1 and stato_precedente == 0:

                x.append(timestamp)
                y.append(base)

                x.append(timestamp)
                y.append(base + 0.65)

            # ==================================================
            # MANTIENI ALTO
            # ==================================================

            elif stato == 1 and stato_precedente == 1:

                x.append(timestamp)
                y.append(base + 0.65)

            # ==================================================
            # DISCESA
            # ==================================================

            elif stato == 0 and stato_precedente == 1:

                x.append(timestamp)
                y.append(base + 0.65)

                x.append(timestamp)
                y.append(base)

            # ==================================================
            # RIMANI BASSO
            # ==================================================

            else:

                x.append(timestamp)
                y.append(base)

            # ==================================================
            # TOOLTIP
            # ==================================================

            numero = str(
                riga.get(
                    "number",
                    ""
                )
            )

            descrizione = str(
                riga.get(
                    "descrizione",
                    ""
                )
            )

            testo = (
                f"<b>{categoria}</b><br>"
                f"<b>Ora:</b> "
                f"{timestamp.strftime('%d-%m-%Y %H:%M:%S')}<br>"
                f"<b>Origine:</b> "
                f"{riga.get('origine', '')}<br>"
                f"<b>Dataset:</b> "
                f"{riga.get('dataset', '')}<br>"
                f"<b>Segnale:</b> "
                f"{riga.get('segnale', '')}<br>"
                f"<b>Cassa:</b> "
                f"{riga.get('cassa', '')}<br>"
                f"<b>NUMBER / SENSORE:</b> "
                f"{numero}<br>"
                f"<b>Valore:</b> "
                f"{riga.get('valore', '')}<br>"
                f"<b>Descrizione:</b> "
                f"{descrizione}"
            )

            testi.append(testo)

            stato_precedente = stato

        # ==================================================
        # LINEA
        # ==================================================

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,

                mode="lines",

                line=dict(
                    color=colori[categoria],
                    width=3,
                    shape="hv"
                ),

                hoverinfo="text",

                text=testi,

                connectgaps=False,

                name=categoria,

                showlegend=False
            )
        )

    # ======================================================
    # LINEE ORIZZONTALI DI BASE
    # ======================================================

    for categoria in categorie:

        base = y_map[categoria]

        fig.add_shape(
            type="line",

            x0=df["timestamp"].min(),
            x1=df["timestamp"].max(),

            y0=base,
            y1=base,

            line=dict(
                color="rgba(120,120,120,0.25)",
                width=1
            ),

            layer="below"
        )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(

        height=600,

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=30
        ),

        hovermode="closest",

        # --------------------------------------------------
        # ASSE X
        # --------------------------------------------------

        xaxis=dict(

            title="Data / Ora",

            type="date",

            showgrid=True,

            rangeslider=dict(
                visible=True
            ),

            rangeselector=dict(

                buttons=[

                    dict(
                        count=10,
                        label="10 min",
                        step="minute",
                        stepmode="backward"
                    ),

                    dict(
                        count=30,
                        label="30 min",
                        step="minute",
                        stepmode="backward"
                    ),

                    dict(
                        count=1,
                        label="1 h",
                        step="hour",
                        stepmode="backward"
                    ),

                    dict(
                        count=6,
                        label="6 h",
                        step="hour",
                        stepmode="backward"
                    ),

                    dict(
                        step="all",
                        label="Tutto"
                    ),
                ]
            )
        ),

        # --------------------------------------------------
        # ASSE Y
        # --------------------------------------------------

        yaxis=dict(

            title="",

            tickmode="array",

            tickvals=[
                3,
                2,
                1,
                0
            ],

            ticktext=[
                "🔥 SENSORE FUMO",
                "🚨 ALLARME INCENDIO",
                "🔵 BASSA PRESSIONE",
                "🟢 ACQUA PRESSURIZZATA",
            ],

            range=[
                -0.7,
                3.9
            ],

            showgrid=True,

            zeroline=False
        ),

        # --------------------------------------------------
        # LEGENDA
        # --------------------------------------------------

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="left",

            x=0
        ),

        hoverlabel=dict(
            align="left"
        )
    )

    return fig


# ==========================================================
# PAGINA FDE
# ==========================================================

def fde_page():

    st.title(
        "📊 Analizzatore Log FDE"
    )

    st.caption(
        "Analisi degli eventi incendio e pressione"
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
    # LETTURA FILE
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

            df_dm1 = filtra_eventi_importanti(
                df_dm1
            )

        if not df_dm1.empty:

            frames.append(
                df_dm1
            )

            st.success(
                f"✅ DM1: {len(df_dm1)} eventi importanti"
            )

        else:

            st.warning(
                "⚠️ Nessun evento importante nel DM1."
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

            df_dm8 = filtra_eventi_importanti(
                df_dm8
            )

        if not df_dm8.empty:

            frames.append(
                df_dm8
            )

            st.success(
                f"✅ DM8: {len(df_dm8)} eventi importanti"
            )

        else:

            st.warning(
                "⚠️ Nessun evento importante nel DM8."
            )

    if not frames:

        st.error(
            "❌ Nessun evento importante riconosciuto."
        )

        return

    # ======================================================
    # UNIONE
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

            key="fde_data_da"

        )

    with col2:

        data_a = st.date_input(

            "📅 A",

            value=data_max,

            min_value=data_min,

            max_value=data_max,

            key="fde_data_a"

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

            key="fde_origini"

        )

    # ======================================================
    # FILTRO EVENTI
    # ======================================================

    eventi_disponibili = [

        "SENSORE FUMO",

        "ALLARME INCENDIO",

        "BASSA PRESSIONE",

        "CONDOTTA ACQUA PRESSURIZZATA",

    ]

    eventi_selezionati = st.multiselect(

        "🚨 Eventi da visualizzare",

        eventi_disponibili,

        default=eventi_disponibili,

        key="fde_eventi"

    )

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(

        "🔍 Ricerca",

        placeholder=(

            "SD23, DM1, allarme, "
            "pressione, cassa..."

        ),

        key="fde_ricerca"

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

    # ======================================================
    # ORIGINE
    # ======================================================

    if origini:

        filtrato = filtrato[

            filtrato[
                "origine"
            ].isin(

                origini

            )

        ]

    else:

        filtrato = filtrato.iloc[0:0]

    # ======================================================
    # EVENTI
    # ======================================================

    if eventi_selezionati:

        filtrato = filtrato[

            filtrato[
                "evento"
            ].isin(

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

    # ==========================================================
    # METRICHE
    # ==========================================================
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "📋 Eventi",
        len(filtrato)
    )
    
    col2.metric(
        "🔥 Sensori",
        int(
            (
                filtrato["evento"] == "SENSORE FUMO"
            ).sum()
        )
    )
    
    col3.metric(
        "🚨 Incendi",
        int(
            (
                filtrato["evento"] == "ALLARME INCENDIO"
            ).sum()
        )
    )
    
    col4.metric(
        "💧 Pressione",
        int(
            (
                filtrato["evento"].isin(
                    [
                        "BASSA PRESSIONE",
                        "CONDOTTA ACQUA PRESSURIZZATA",
                    ]
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
    # TIMELINE
    # ======================================================

    with tab1:

        st.subheader(
            "📈 Timeline eventi FDE"
        )

        st.info(
            "La timeline mostra solo gli eventi "
            "significativi: sensore fumo, allarme "
            "incendio e pressione acqua."
        )

        fig = crea_timeline(
            filtrato
        )

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
    # TABELLA
    # ======================================================

    with tab2:

        st.subheader(

            f"📋 Eventi: {len(filtrato)}"

        )

        tabella = filtrato.copy()

        tabella["Time"] = (

            tabella[
                "timestamp"
            ]

            .dt

            .strftime(
                "%d-%m-%Y %H:%M:%S"
            )

        )

        tabella = tabella[

            [

                "Time",

                "evento",

                "origine",

                "dataset",

                "segnale",

                "cassa",

                "number",

                "data_val",

                "descrizione",

                "valore",

            ]

        ]

        tabella = tabella.rename(

            columns={

                "evento":
                    "Evento",

                "origine":
                    "Origine",

                "dataset":
                    "Dataset",

                "segnale":
                    "Segnale",

                "cassa":
                    "Cassa",

                "number":
                    "NUMBER / SENSORE",

                "data_val":
                    "DATA",

                "descrizione":
                    "Descrizione",

                "valore":
                    "Valore grezzo",

            }

        )

        st.dataframe(

            tabella,

            use_container_width=True,

            hide_index=True,

            height=600

        )

        # ==================================================
        # DOWNLOAD CSV
        # ==================================================

        csv = tabella.to_csv(

            index=False

        ).encode(

            "utf-8-sig"

        )

        st.download_button(

            "📥 Scarica CSV",

            data=csv,

            file_name="analisi_fde_eventi_importanti.csv",

            mime="text/csv"

        )
