import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt


# ==========================================================
# ORDINE ADD DM1
# ==========================================================

ORDINE_DM1 = [
    "007", "005", "006", "004", "003", "002", "001", "008", "009",
    "010", "011", "012", "013", "014", "015", "017", "016", "018",
    "027", "029", "030", "028", "026", "025", "023", "024", "022",
    "021", "020", "019", "031", "032", "033", "034", "035", "036",
    "038", "037", "039", "040", "041", "042", "043", "044", "045",
    "046", "047", "048", "049", "050", "051", "052", "053", "054",
    "055", "056", "057", "058", "059", "060", "061", "062", "063",
    "064", "065", "066", "067", "068", "074", "073", "072", "071",
    "070", "069"
]


# ==========================================================
# ORDINE ADD DM8
# ==========================================================

ORDINE_DM8 = [
    "069", "070", "071", "072", "073", "074", "068", "067", "058",
    "059", "060", "061", "062", "063", "064", "065", "066", "049",
    "050", "051", "052", "053", "054", "055", "056", "057", "040",
    "041", "042", "043", "044", "045", "046", "047", "048", "039",
    "037", "038", "036", "035", "034", "033", "032", "031", "019",
    "020", "021", "022", "024", "023", "025", "026", "028", "030",
    "029", "027", "018", "016", "017", "015", "014", "013", "012",
    "011", "010", "009", "008", "001", "002", "003", "004", "006",
    "005", "007"
]


# ==========================================================
# RESTITUISCE L'ORDINE CORRETTO
# ==========================================================

def ottieni_ordine(cassa):

    cassa = str(cassa).upper().strip()

    if cassa == "DM1":
        return ORDINE_DM1

    if cassa == "DM8":
        return ORDINE_DM8

    return []


# ==========================================================
# RICONOSCIMENTO DM1 / DM8
# ==========================================================

def rileva_cassa(nome_file, testo):

    nome = str(nome_file).upper()

    # Prima controlliamo il nome del file
    if "DM1" in nome:
        return "DM1"

    if "DM8" in nome:
        return "DM8"

    # Poi controlliamo il contenuto del file
    testo = str(testo).upper()

    if re.search(r"\bDM1\b", testo):
        return "DM1"

    if re.search(r"\bDM8\b", testo):
        return "DM8"

    return "SCONOSCIUTA"


# ==========================================================
# NORMALIZZAZIONE ADD
# ==========================================================

def normalizza_add(valore):

    if valore is None:
        return ""

    valore = str(valore).strip()

    if valore.endswith(".0"):
        valore = valore[:-2]

    match = re.match(
        r"^(\d+)",
        valore
    )

    if match:
        return match.group(1).zfill(3)

    return valore


# ==========================================================
# LETTURA DI UNA RIGA DEL FILE MNT
# ==========================================================

def parse_riga_mnt(riga):

    riga = riga.strip()

    if not riga:
        return None

    parti = riga.split()

    if len(parti) < 2:
        return None

    # La riga deve iniziare con ADD numerico
    if not re.match(
        r"^\d{1,3}$",
        parti[0]
    ):
        return None

    colonne = [
        "Add",
        "M/S",
        "Type",
        "Man",
        "Serial N",
        "YY/WW",
        "PW1",
        "PW2",
        "PW3",
        "PW4",
        "PW5",
        "I",
        "I_I",
        "STA",
        "ISO",
    ]

    record = {
        colonna: ""
        for colonna in colonne
    }

    for indice, colonna in enumerate(colonne):

        if indice < len(parti):
            record[colonna] = parti[indice]

    record["Add"] = normalizza_add(
        record["Add"]
    )

    return record


# ==========================================================
# IMPORTAZIONE DIRETTA FILE .MNT
# ==========================================================

def importa_mnt(uploaded_file):

    # ------------------------------------------------------
    # LEGGE DIRETTAMENTE IL FILE .MNT
    # ------------------------------------------------------

    contenuto = uploaded_file.getvalue()

    testo = contenuto.decode(
        "latin-1",
        errors="ignore"
    )

    righe = testo.splitlines()

    # ------------------------------------------------------
    # IDENTIFICA DM1 / DM8
    # ------------------------------------------------------

    cassa = rileva_cassa(
        uploaded_file.name,
        testo
    )

    software = ""
    database = ""

    # ------------------------------------------------------
    # CERCA INFORMAZIONI TESTATA
    # ------------------------------------------------------

    for riga in righe[:50]:

        match = re.search(
            r"Software Version\s*:\s*(.*?)\s+Database Version\s*:\s*(.*)",
            riga,
            re.IGNORECASE
        )

        if match:

            software = match.group(1).strip()
            database = match.group(2).strip()

            break

    # ------------------------------------------------------
    # PARSE SENSORI
    # ------------------------------------------------------

    records = []

    for riga in righe:

        record = parse_riga_mnt(
            riga
        )

        if record is not None:
            records.append(record)

    df = pd.DataFrame(
        records,
        columns=[
            "Add",
            "M/S",
            "Type",
            "Man",
            "Serial N",
            "YY/WW",
            "PW1",
            "PW2",
            "PW3",
            "PW4",
            "PW5",
            "I",
            "I_I",
            "STA",
            "ISO",
        ]
    )

    if df.empty:

        return (
            df,
            cassa,
            software,
            database
        )

    # ------------------------------------------------------
    # CONVERSIONE NUMERICA
    # ------------------------------------------------------

    for colonna in [
        "I",
        "I_I",
        "STA"
    ]:

        df[colonna] = pd.to_numeric(
            df[colonna],
            errors="coerce"
        )

    # ------------------------------------------------------
    # ORDINE SENSORI
    # ------------------------------------------------------

    ordine = ottieni_ordine(
        cassa
    )

    if ordine:

        mappa_ordine = {
            add: posizione
            for posizione, add
            in enumerate(ordine)
        }

        df["_ordine"] = (
            df["Add"]
            .astype(str)
            .map(mappa_ordine)
        )

        df = df.sort_values(
            "_ordine",
            na_position="last"
        )

        df = df.drop(
            columns="_ordine"
        )

    return (
        df.reset_index(drop=True),
        cassa,
        software,
        database
    )


# ==========================================================
# GRAFICO STA / I_I
# ==========================================================

def crea_grafico(
    df,
    cassa
):

    grafico = df.copy()

    # ------------------------------------------------------
    # ORDINE ADD
    # ------------------------------------------------------

    ordine = ottieni_ordine(
        cassa
    )

    if ordine:

        mappa_ordine = {
            add: posizione
            for posizione, add
            in enumerate(ordine)
        }

        grafico["_ordine"] = (
            grafico["Add"]
            .astype(str)
            .map(mappa_ordine)
        )

        grafico = grafico.sort_values(
            "_ordine",
            na_position="last"
        )

    # ------------------------------------------------------
    # X = POSIZIONE FISICA
    # ------------------------------------------------------

    x = list(
        range(len(grafico))
    )

    fig, ax = plt.subplots(
        figsize=(16, 7)
    )

    # ------------------------------------------------------
    # STA
    # ------------------------------------------------------

    if "STA" in grafico.columns:

        ax.plot(
            x,
            grafico["STA"],
            linewidth=2,
            marker="o",
            label="STA"
        )

    # ------------------------------------------------------
    # I_I
    # ------------------------------------------------------

    if "I_I" in grafico.columns:

        ax.plot(
            x,
            grafico["I_I"],
            linewidth=2,
            marker="o",
            label="I_I"
        )

    # ------------------------------------------------------
    # ADD
    # ------------------------------------------------------

    ax.set_xticks(x)

    ax.set_xticklabels(
        grafico["Add"].astype(str),
        rotation=90
    )

    ax.set_xlabel(
        "ADD"
    )

    ax.set_ylabel(
        "Valore"
    )

    ax.set_title(
        f"Misurazione Sensori - {cassa}"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    ax.legend()

    fig.tight_layout()

    return fig


# ==========================================================
# PAGINA STREAMLIT
# ==========================================================

def misurazione_sensori_page():

    st.title(
        "🔬 Misurazione Sensori"
    )

    st.caption(
        "Analisi diretta dei file .MNT"
    )

    st.divider()

    # ======================================================
    # CARICAMENTO FILE .MNT
    # ======================================================

    uploaded_file = st.file_uploader(
        "📥 Carica file MNT",
        type=["mnt"],
        key="mnt_file"
    )

    # ======================================================
    # NESSUN FILE
    # ======================================================

    if uploaded_file is None:

        st.info(
            "Carica un file .MNT per iniziare."
        )

        return

    # ======================================================
    # CONTROLLO ESTENSIONE
    # ======================================================

    if not uploaded_file.name.lower().endswith(
        ".mnt"
    ):

        st.error(
            "❌ Il file deve avere estensione .MNT"
        )

        return

    # ======================================================
    # IMPORTAZIONE
    # ======================================================

    with st.spinner(
        "🔄 Lettura file .MNT..."
    ):

        try:

            (
                df,
                cassa,
                software,
                database
            ) = importa_mnt(
                uploaded_file
            )

        except Exception as errore:

            st.error(
                "❌ Errore durante la lettura del file .MNT"
            )

            st.exception(
                errore
            )

            return

    # ======================================================
    # NESSUN SENSORE
    # ======================================================

    if df.empty:

        st.error(
            "❌ Nessun sensore trovato nel file .MNT."
        )

        return

    # ======================================================
    # CASSA NON RICONOSCIUTA
    # ======================================================

    if cassa == "SCONOSCIUTA":

        st.warning(
            "⚠️ DM1/DM8 non riconosciuto automaticamente."
        )

        cassa = st.selectbox(
            "Seleziona la cassa",
            [
                "DM1",
                "DM8"
            ],
            key="mnt_cassa"
        )

        ordine = ottieni_ordine(
            cassa
        )

        mappa_ordine = {
            add: posizione
            for posizione, add
            in enumerate(ordine)
        }

        df["_ordine"] = (
            df["Add"]
            .astype(str)
            .map(mappa_ordine)
        )

        df = (
            df
            .sort_values(
                "_ordine",
                na_position="last"
            )
            .drop(
                columns="_ordine"
            )
            .reset_index(
                drop=True
            )
        )

    # ======================================================
    # INFORMAZIONI
    # ======================================================

    st.success(
        f"✅ File MNT caricato: {uploaded_file.name}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Cassa",
            cassa
        )

    with col2:

        st.metric(
            "Sensori",
            len(df)
        )

    with col3:

        st.metric(
            "Software",
            software or "-"
        )

    with col4:

        st.metric(
            "Database",
            database or "-"
        )

    st.divider()

    # ======================================================
    # RICERCA
    # ======================================================

    ricerca = st.text_input(
        "🔍 Cerca sensore",
        placeholder=(
            "ADD, seriale, tipo, produttore..."
        ),
        key="mnt_ricerca"
    )

    risultato = df.copy()

    if ricerca.strip():

        query = ricerca.strip().lower()

        testo_ricerca = (
            risultato
            .astype(str)
            .agg(
                " ".join,
                axis=1
            )
            .str.lower()
        )

        risultato = risultato[
            testo_ricerca.str.contains(
                query,
                regex=False,
                na=False
            )
        ]

    st.markdown(
        f"### 📋 Sensori visualizzati: {len(risultato)}"
    )

    if risultato.empty:

        st.warning(
            "Nessun sensore trovato."
        )

        return

    # ======================================================
    # TABS
    # ======================================================

    tab1, tab2 = st.tabs(
        [
            "📈 Misurazioni",
            "📋 Dati MNT"
        ]
    )

    # ======================================================
    # GRAFICO
    # ======================================================

    with tab1:

        st.subheader(
            f"📈 STA / I_I — {cassa}"
        )

        fig = crea_grafico(
            risultato,
            cassa
        )

        st.pyplot(
            fig,
            clear_figure=True
        )

    # ======================================================
    # TABELLA
    # ======================================================

    with tab2:

        st.subheader(
            "📋 Dati letti direttamente dal file .MNT"
        )

        st.dataframe(
            risultato,
            use_container_width=True,
            hide_index=True,
            height=600
        )

        # --------------------------------------------------
        # ESPORTAZIONE FACOLTATIVA
        # --------------------------------------------------

        csv = risultato.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(
            "📥 Esporta risultato CSV",
            data=csv,
            file_name="misurazione_sensori.csv",
            mime="text/csv"
        )
