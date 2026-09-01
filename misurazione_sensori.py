import streamlit as st
import pandas as pd
import re


# ==========================================================
# LETTURA FILE MNT
# ==========================================================

def leggi_mnt(file_mnt):

    contenuto = file_mnt.getvalue()

    testo = contenuto.decode(
        "latin-1",
        errors="ignore"
    )

    righe = testo.splitlines()

    dati = []

    software = ""
    database = ""

    # ======================================================
    # TESTATA
    # ======================================================

    for riga in righe[:10]:

        match = re.search(
            r"Software Version:\s*(.*?)\s+Database Version:\s*(.*)",
            riga,
            re.IGNORECASE
        )

        if match:

            software = match.group(1).strip()
            database = match.group(2).strip()

            break

    # ======================================================
    # DATI SENSORI
    # ======================================================

    for riga in righe:

        riga = riga.strip()

        if not riga:
            continue

        # Una riga sensore inizia con ADD numerico
        if not re.match(
            r"^\d+",
            riga
        ):
            continue

        parti = riga.split()

        # Servono almeno i campi principali
        if len(parti) < 10:
            continue

        try:

            record = {}

            record["Add"] = parti[0]

            if len(parti) > 1:
                record["M/S"] = parti[1]

            if len(parti) > 2:
                record["Type"] = parti[2]

            if len(parti) > 3:
                record["Man"] = parti[3]

            if len(parti) > 4:
                record["Serial"] = parti[4]

            if len(parti) > 5:
                record["YY/WW"] = parti[5]

            if len(parti) > 6:
                record["PW1"] = parti[6]

            if len(parti) > 7:
                record["PW2"] = parti[7]

            if len(parti) > 8:
                record["PW3"] = parti[8]

            if len(parti) > 9:
                record["PW4"] = parti[9]

            if len(parti) > 10:
                record["PW5"] = parti[10]

            if len(parti) > 11:
                record["I"] = parti[11]

            if len(parti) > 12:
                record["I_I"] = parti[12]

            if len(parti) > 13:
                record["STA"] = parti[13]

            if len(parti) > 14:
                record["ISO"] = parti[14]

            dati.append(record)

        except Exception:
            continue

    df = pd.DataFrame(dati)

    if df.empty:
        return df, software, database

    # ======================================================
    # CONVERSIONI
    # ======================================================

    for colonna in [
        "Add",
        "I",
        "I_I",
        "STA"
    ]:

        if colonna in df.columns:

            df[colonna] = pd.to_numeric(
                df[colonna],
                errors="coerce"
            )

    return df, software, database


# ==========================================================
# PAGINA STREAMLIT
# ==========================================================

def misurazione_sensori_page():

    st.title(
        "🔬 Misurazione Sensori"
    )

    st.caption(
        "Analisi diretta dei file MNT"
    )

    st.divider()

    # ======================================================
    # FILE MNT
    # ======================================================

    file_mnt = st.file_uploader(

        "📥 Carica file MNT",

        type=["mnt"],

        key="file_misurazione_mnt"

    )

    # ======================================================
    # NESSUN FILE
    # ======================================================

    if file_mnt is None:

        st.info(
            "Carica un file .MNT per iniziare."
        )

        return

    # ======================================================
    # ANALISI
    # ======================================================

    with st.spinner(
        "🔄 Analisi file MNT..."
    ):

        try:

            df, software, database = leggi_mnt(
                file_mnt
            )

        except Exception as e:

            st.error(
                "❌ Errore nella lettura del file MNT"
            )

            st.exception(e)

            return

    # ======================================================
    # CONTROLLO
    # ======================================================

    if df.empty:

        st.error(
            "❌ Nessun dato sensore trovato nel file MNT."
        )

        return

    # ======================================================
    # INFORMAZIONI
    # ======================================================

    st.success(
        f"✅ File {file_mnt.name} analizzato"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Sensori",
            len(df)
        )

    with col2:

        st.metric(
            "Software",
            software or "-"
        )

    with col3:

        st.metric(
            "Database",
            database or "-"
        )

    st.divider()

    # ======================================================
    # FILTRO
    # ======================================================

    ricerca = st.text_input(

        "🔍 Cerca sensore",

        placeholder=(
            "ADD, seriale, tipo, produttore..."
        ),

        key="ricerca_mnt"

    )

    risultato = df.copy()

    if ricerca:

        ricerca = ricerca.strip().lower()

        testo = (
            risultato
            .astype(str)
            .agg(
                " ".join,
                axis=1
            )
            .str.lower()
        )

        risultato = risultato[
            testo.str.contains(
                ricerca,
                regex=False,
                na=False
            )
        ]

    st.markdown(
        f"### 📋 Sensori trovati: {len(risultato)}"
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
            "📋 Dati sensori"
        ]
    )

    # ======================================================
    # GRAFICO
    # ======================================================

    with tab1:

        st.subheader(
            "📈 Misurazioni STA / I_I"
        )
        
        grafico = risultato.copy()
        
        grafico = grafico.sort_values(
            "Add"
        )
        
        colonne_grafico = []
        
        if "STA" in grafico.columns:
            colonne_grafico.append("STA")
        
        if "I_I" in grafico.columns:
            colonne_grafico.append("I_I")
        
        if colonne_grafico:
        
            st.line_chart(
                grafico.set_index("Add")[colonne_grafico],
                height=500
            )
        
        else:
        
            st.warning(
                "Nel file non sono presenti le colonne STA / I_I."
            )

        else:

            st.warning(
                "Nel file non sono presenti "
                "le colonne I / I_I."
            )

    # ======================================================
    # TABELLA
    # ======================================================

    with tab2:

        st.subheader(
            "📋 Dati sensori"
        )

        st.dataframe(

            risultato,

            use_container_width=True,

            hide_index=True,

            height=600

        )

        csv = risultato.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        )

        st.download_button(

            "📥 Scarica CSV",

            data=csv,

            file_name="misurazione_sensori.csv",

            mime="text/csv"

        )
