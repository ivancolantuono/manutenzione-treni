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
        str(valore),
        str(valore)
    )


# ==========================================================
# DECODIFICA NUMBER SENSORI FUMO
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
# DECODIFICA MAU
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

    "FUMO": "#ff3b30",
    "TERMICO": "#ff9500",
    "FAULT": "#8e8e93",
    "ALLARME INCENDIO": "#ff0000",
    "FUORI SERVIZIO": "#af52de",
    "BASSA PRESSIONE": "#007aff",
    "CONDOTTA ACQUA PRESSURIZZATA": "#34c759",
    "NORMALE": "#808080",

}


# ==========================================================
# COLORI SEGNALI
# ==========================================================

COLORI_SEGNALI = [

    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",

    "#393b79",
    "#637939",
    "#8c6d31",
    "#843c39",
    "#7b4173",
    "#3182bd",
    "#31a354",
    "#756bb1",
    "#636363",
    "#e6550d",

]


# ==========================================================
# NORMALIZZAZIONE SEGNALE
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

    valore = str(
        valore
    )

    cassa = "-"
    number = "-"
    data = "-"

    # ======================================================
    # COACH N
    # ======================================================

    match = re.search(

        r"COACH\s*N\s*:\s*(\d+)",

        valore,

        re.IGNORECASE

    )

    if match:

        cassa = decodifica_cassa(
            match.group(1)
        )

    # ======================================================
    # NUMBER
    # ======================================================

    match = re.search(

        r"NUMBER\s*:\s*(\d+)",

        valore,

        re.IGNORECASE

    )

    if match:

        number = match.group(1)

    # ======================================================
    # DATA
    # ======================================================

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
    ).upper()

    valore = str(
        valore
    )

    # ======================================================
    # MAPPING
    # ======================================================

    mapping = None

    for nome, valori in DECODIFICHE.items():

        if segnale.startswith(nome):

            mapping = valori

            break

    # ======================================================
    # PARAMETRI
    # ======================================================

    cassa, number, data = estrai_parametri(
        valore
    )

    # ======================================================
    # DECODIFICA DATA
    # ======================================================

    descrizione = data

    if mapping:

        descrizione = mapping.get(
            str(data),
            str(data)
        )

    # ======================================================
    # DECODIFICA NUMBER
    # ======================================================

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

    # ======================================================
    # FUMO
    # ======================================================

    if "ALLARME FUMO" in descrizione:

        return "FUMO"

    # ======================================================
    # TERMICO
    # ======================================================

    if "ALLARME TERMICO" in descrizione:

        return "TERMICO"

    # ======================================================
    # FAULT
    # ======================================================

    if (

        descrizione == "FAULT"

        or

        "FAULT" in descrizione

        or

        "FAIL" in descrizione

    ):

        return "FAULT"

    # ======================================================
    # INCENDIO
    # ======================================================

    if "ALLARME INCENDIO" in descrizione:

        return "ALLARME INCENDIO"

    # ======================================================
    # FUORI SERVIZIO
    # ======================================================

    if "FUORI SERVIZIO" in descrizione:

        return "FUORI SERVIZIO"

    # ======================================================
    # PRESSIONE
    # ======================================================

    if "BASSA PRESSIONE" in descrizione:

        return "BASSA PRESSIONE"

    if (
        "CONDOTTA ACQUA PRESSURIZZATA"
        in descrizione
    ):

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

    try:

        contenuto = uploaded_file.getvalue()

        testo = contenuto.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        testo = (
            uploaded_file
            .getvalue()
            .decode(
                "latin-1",
                errors="ignore"
            )
        )

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

            valore = riga

            dati.append({

                "timestamp":
                    timestamp,

                "dataset":
                    dataset_corrente,

                "segnale":
                    segnale_corrente,

                "valore":
                    valore,

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

    numbers_raw = []

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

        # ==================================================
        # NUMBER ORIGINALE
        # ==================================================

        _, number_raw, _ = estrai_parametri(
            riga["valore"]
        )

        # ==================================================
        # EVENTO
        # ==================================================

        evento = classifica_evento(

            riga["segnale"],

            descrizione

        )

        casse.append(
            cassa
        )

        numbers.append(
            number
        )

        numbers_raw.append(
            number_raw
        )

        date_valori.append(
            data
        )

        descrizioni.append(
            descrizione
        )

        eventi.append(
            evento
        )

    df["cassa"] = casse

    df["number"] = numbers

    df["number_raw"] = numbers_raw

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
        "number_raw",
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
# TIMELINE PLOTLY
# ==========================================================

def crea_timeline(df):

    fig = go.Figure()

    if df.empty:

        return fig

    # ======================================================
    # COPIA E ORDINAMENTO
    # ======================================================

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "timestamp"
        ]
    )

    df = df.sort_values(
        "timestamp"
    )

    # ======================================================
    # SEGNALI
    # ======================================================

    segnali = (

        df["segnale"]
        .astype(str)
        .drop_duplicates()
        .tolist()

    )

    if not segnali:

        return fig

    # ======================================================
    # POSIZIONE VERTICALE
    # ======================================================

    mappa_y = {

        segnale: i

        for i, segnale
        in enumerate(segnali)

    }

    # ======================================================
    # COLORE FISSO PER OGNI SEGNALE
    # ======================================================

    colore_segnale = {

        segnale:
            COLORI_SEGNALI[
                i % len(COLORI_SEGNALI)
            ]

        for i, segnale
        in enumerate(segnali)

    }

    # ======================================================
    # TRACCE
    # ======================================================

    for segnale in segnali:

        dati = df[
            df["segnale"].astype(str)
            == segnale
        ].sort_values(
            "timestamp"
        )

        if dati.empty:

            continue

        x = []

        y = []

        testi = []

        number_x = []

        number_y = []

        number_text = []

        number_hover = []

        # ==================================================
        # EVENTI
        # ==================================================

        for _, riga in dati.iterrows():

            timestamp = riga[
                "timestamp"
            ]

            posizione = mappa_y[
                segnale
            ]

            number_nome = str(
                riga.get(
                    "number",
                    ""
                )
            ).strip()

            number_raw = str(
                riga.get(
                    "number_raw",
                    ""
                )
            ).strip()

            evento = str(
                riga.get(
                    "evento",
                    "NORMALE"
                )
            )

            # ==============================================
            # TOOLTIP
            # ==============================================

            testo = (

                f"<b>Ora:</b> "
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
                f"{number_nome}"
                f"<br>"

                f"<b>Number originale:</b> "
                f"{number_raw}"
                f"<br>"

                f"<b>Valore:</b> "
                f"{riga.get('valore', '')}"
                f"<br>"

                f"<b>Descrizione:</b> "
                f"{riga.get('descrizione', '')}"
                f"<br>"

                f"<b>Evento:</b> "
                f"{evento}"

            )

            x.append(
                timestamp
            )

            y.append(
                posizione
            )

            testi.append(
                testo
            )

            # ==============================================
            # NUMBER SULLA TIMELINE
            # ==============================================

            if (

                number_nome

                and

                number_nome.lower()
                not in [
                    "",
                    "nan",
                    "none",
                    "-"
                ]

            ):

                number_x.append(
                    timestamp
                )

                number_y.append(
                    posizione
                )

                number_text.append(
                    number_nome
                )

                number_hover.append(
                    testo
                )

        # ==================================================
        # LINEA DEL SEGNALE
        # ==================================================

        fig.add_trace(

            go.Scatter(

                x=x,

                y=y,

                mode="lines",

                name=segnale,

                line=dict(

                    color=
                        colore_segnale[
                            segnale
                        ],

                    width=3,

                    shape="hv"

                ),

                text=testi,

                hoverinfo="text",

                connectgaps=False,

                showlegend=True

            )

        )

        # ==================================================
        # NUMBER SULLA LINEA
        # ==================================================

        if number_text:

            fig.add_trace(

                go.Scatter(

                    x=number_x,

                    y=number_y,

                    mode="text",

                    text=number_text,

                    textposition="top center",

                    textfont=dict(

                        size=10,

                        color=
                            colore_segnale[
                                segnale
                            ],

                        family="Arial"

                    ),

                    hovertext=number_hover,

                    hoverinfo="text",

                    showlegend=False

                )

            )

    # ======================================================
    # ASSE Y
    # ======================================================

    fig.update_yaxes(

        tickmode="array",

        tickvals=list(
            mappa_y.values()
        ),

        ticktext=list(
            mappa_y.keys()
        ),

        autorange="reversed",

        showgrid=True,

        zeroline=False

    )

    # ======================================================
    # LAYOUT
    # ======================================================

    fig.update_layout(

        height=max(

            650,

            len(segnali) * 38

        ),

        margin=dict(

            l=150,

            r=230,

            t=30,

            b=80

        ),

        hovermode="closest",

        # ==================================================
        # LEGENDA
        # ==================================================

        showlegend=True,

        legend=dict(

            title=dict(

                text="<b>SEGNALI</b>"

            ),

            orientation="v",

            x=1.01,

            y=1,

            xanchor="left",

            yanchor="top",

            bgcolor="rgba(255,255,255,0.95)",

            bordercolor="#cccccc",

            borderwidth=1,

            font=dict(

                size=11

            )

        ),

        # ==================================================
        # ASSE X
        # ==================================================

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

                        count=1,

                        label="1h",

                        step="hour",

                        stepmode="backward"

                    ),

                    dict(

                        count=6,

                        label="6h",

                        step="hour",

                        stepmode="backward"

                    ),

                    dict(

                        count=12,

                        label="12h",

                        step="hour",

                        stepmode="backward"

                    ),

                    dict(

                        count=1,

                        label="1g",

                        step="day",

                        stepmode="backward"

                    ),

                    dict(

                        count=3,

                        label="3g",

                        step="day",

                        stepmode="backward"

                    ),

                    dict(

                        step="all",

                        label="TUTTO"

                    )

                ]

            )

        ),

        # ==================================================
        # HOVER
        # ==================================================

        hoverlabel=dict(

            bgcolor="white",

            font_size=12,

            font_family="Arial",

            align="left"

        ),

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
        "Analisi Log FDE DM1 / DM8"
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

    # ======================================================
    # CONTROLLO FILE
    # ======================================================

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

    # ======================================================
    # NESSUN DATO
    # ======================================================

    if not frames:

        st.error(
            "❌ Nessun dato riconosciuto."
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
    # FILTRO EVENTO
    # ======================================================

    eventi = sorted(

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

        eventi,

        key="fde_eventi"

    )

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(

        "🔍 Ricerca",

        placeholder=(
            "Sensore, segnale, cassa, "
            "number, allarme..."
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

            >=

            data_da_dt

        )

        &

        (

            df["timestamp"]

            <=

            data_a_dt

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

    # ======================================================
    # EVENTO
    # ======================================================

    if eventi_selezionati:

        filtrato = filtrato[

            filtrato[
                "evento"
            ].isin(
                eventi_selezionati
            )

        ]

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

        "DM1",

        int(

            (

                filtrato[
                    "origine"
                ]

                ==

                "DM1"

            ).sum()

        )

    )

    col3.metric(

        "DM8",

        int(

            (

                filtrato[
                    "origine"
                ]

                ==

                "DM8"

            ).sum()

        )

    )

    col4.metric(

        "🚨 Anomalie",

        int(

            (

                filtrato[
                    "evento"
                ]

                !=

                "NORMALE"

            ).sum()

        )

    )

    # ======================================================
    # RISULTATI
    # ======================================================

    if filtrato.empty:

        st.warning(
            "⚠️ Nessun risultato."
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
            "📈 Timeline FDE"
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

            f"📋 Eventi: "
            f"{len(filtrato)}"

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
                "origine",
                "dataset",
                "segnale",
                "cassa",
                "number",
                "number_raw",
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

                "segnale":
                    "Segnale",

                "cassa":
                    "Cassa",

                "number":
                    "Number",

                "number_raw":
                    "Number originale",

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

            file_name="analisi_fde.csv",

            mime="text/csv"

        )
