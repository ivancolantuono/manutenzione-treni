import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# ORDINE SENSORI DM1
# ==========================================================

ORDER_DM1 = [
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
# ORDINE SENSORI DM8
# ==========================================================

ORDER_DM8 = [
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
# LETTURA EXCEL
# ==========================================================

def _carica_excel(uploaded_file):

    df_grafico = pd.read_excel(
        uploaded_file,
        sheet_name="DATI_GRAFICO"
    )

    df_sensori = pd.read_excel(
        uploaded_file,
        sheet_name="Foglio1"
    )

    return df_grafico, df_sensori


# ==========================================================
# NORMALIZZA COLONNE
# ==========================================================

def _normalizza_colonne(df):

    df = df.copy()

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    return df


# ==========================================================
# PREPARAZIONE DATI
# ==========================================================

def _prepara_dati(
    df_grafico,
    df_sensori
):

    df_grafico = _normalizza_colonne(
        df_grafico
    )

    df_sensori = _normalizza_colonne(
        df_sensori
    )

    # ------------------------------------------------------
    # ADD
    # ------------------------------------------------------

    if "ADD" in df_grafico.columns:

        df_grafico["ADD"] = (
            pd.to_numeric(
                df_grafico["ADD"],
                errors="coerce"
            )
            .astype("Int64")
            .astype(str)
            .str.zfill(3)
        )

    # ------------------------------------------------------
    # I / I_I
    # ------------------------------------------------------

    for col in ["I", "I_I", "STA"]:

        if col in df_grafico.columns:

            df_grafico[col] = pd.to_numeric(
                df_grafico[col],
                errors="coerce"
            )

    # ------------------------------------------------------
    # ORDINE
    # ------------------------------------------------------

    if "ORDINE" in df_grafico.columns:

        df_grafico["ORDINE"] = pd.to_numeric(
            df_grafico["ORDINE"],
            errors="coerce"
        )

    # ------------------------------------------------------
    # FOGLIO1
    # ------------------------------------------------------

    if "ADD" in df_sensori.columns:

        df_sensori["ADD"] = (
            pd.to_numeric(
                df_sensori["ADD"],
                errors="coerce"
            )
            .astype("Int64")
            .astype(str)
            .str.zfill(3)
        )

    for col in ["I", "I_I", "STA"]:

        if col in df_sensori.columns:

            df_sensori[col] = pd.to_numeric(
                df_sensori[col],
                errors="coerce"
            )

    return (
        df_grafico,
        df_sensori
    )


# ==========================================================
# APPLICA ORDINE DM1 / DM8
# ==========================================================

def _applica_ordine(
    df,
    tipo_dm
):

    df = df.copy()

    if "ADD" not in df.columns:

        return df, []

    # ------------------------------------------------------
    # Scegli ordine
    # ------------------------------------------------------

    if tipo_dm == "DM1":

        order_list = ORDER_DM1

    else:

        order_list = ORDER_DM8

    # ------------------------------------------------------
    # Normalizza ADD
    # ------------------------------------------------------

    df["ADD"] = (
        df["ADD"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .fillna("")
        .str.zfill(3)
    )

    # ------------------------------------------------------
    # Crea posizione
    # ------------------------------------------------------

    posizione = {
        add: i
        for i, add in enumerate(order_list)
    }

    df["POSIZIONE"] = (
        df["ADD"]
        .map(posizione)
    )

    # ------------------------------------------------------
    # Teniamo solo gli ADD presenti nell'ordine
    # ------------------------------------------------------

    df = df[
        df["POSIZIONE"].notna()
    ].copy()

    # ------------------------------------------------------
    # Ordina secondo orderList
    # ------------------------------------------------------

    df = df.sort_values(
        "POSIZIONE"
    ).reset_index(
        drop=True
    )

    # ------------------------------------------------------
    # ADD realmente presenti
    # ------------------------------------------------------

    add_presenti = df[
        "ADD"
    ].drop_duplicates().tolist()

    return (
        df,
        add_presenti
    )


# ==========================================================
# GRAFICO
# ==========================================================

def _grafico_linee(
    df,
    tipo_dm
):

    df = df.copy()

    # ------------------------------------------------------
    # ORDINE
    # ------------------------------------------------------

    df, add_presenti = _applica_ordine(
        df,
        tipo_dm
    )

    if df.empty:

        return None

    # ------------------------------------------------------
    # POSIZIONE X
    # ------------------------------------------------------

    x = list(
        range(
            len(df)
        )
    )

    fig, ax = plt.subplots(
        figsize=(16, 6)
    )

    # ------------------------------------------------------
    # LINEA I
    # ------------------------------------------------------

    if "I" in df.columns:

        ax.plot(
            x,
            df["I"],
            linewidth=2,
            marker="o",
            label="I"
        )

    # ------------------------------------------------------
    # LINEA I_I
    # ------------------------------------------------------

    if "I_I" in df.columns:

        ax.plot(
            x,
            df["I_I"],
            linewidth=2,
            marker="o",
            label="I_I"
        )

    # ------------------------------------------------------
    # ASSE X
    # ------------------------------------------------------

    ax.set_xticks(x)

    ax.set_xticklabels(
        add_presenti,
        rotation=90
    )

    # ------------------------------------------------------
    # TITOLO
    # ------------------------------------------------------

    ax.set_title(
        f"Misurazione sensori - ORDINATO {tipo_dm}"
    )

    ax.set_xlabel(
        "ADD"
    )

    ax.set_ylabel(
        "Valore"
    )

    # ------------------------------------------------------
    # GRIGLIA
    # ------------------------------------------------------

    ax.grid(
        True,
        alpha=0.25
    )

    # ------------------------------------------------------
    # LEGENDA
    # ------------------------------------------------------

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
        "Analisi delle misure I e I_I "
        "con ordinamento sensori DM1 / DM8."
    )

    st.divider()

    # ======================================================
    # SELEZIONE DM
    # ======================================================

    tipo_dm = st.radio(
        "🚆 Ordine sensori",
        [
            "DM1",
            "DM8"
        ],
        horizontal=True,
        key="misurazione_tipo_dm"
    )

    st.divider()

    # ======================================================
    # UPLOAD
    # ======================================================

    uploaded_file = st.file_uploader(
        "📥 Carica Misurazione sensori.xlsm",
        type=[
            "xlsm",
            "xlsx"
        ],
        key="misurazione_sensori_file"
    )

    if uploaded_file is None:

        st.info(
            "Carica il file Excel per iniziare."
        )

        return

    # ======================================================
    # LETTURA
    # ======================================================

    try:

        with st.spinner(
            "🔄 Lettura misurazioni..."
        ):

            (
                df_grafico,
                df_sensori
            ) = _carica_excel(
                uploaded_file
            )

            (
                df_grafico,
                df_sensori
            ) = _prepara_dati(
                df_grafico,
                df_sensori
            )

    except Exception as e:

        st.error(
            "❌ Errore durante la lettura del file."
        )

        st.exception(e)

        return

    # ======================================================
    # CONTROLLO
    # ======================================================

    if df_grafico.empty:

        st.warning(
            "⚠️ Il foglio DATI_GRAFICO è vuoto."
        )

        return

    if "ADD" not in df_grafico.columns:

        st.error(
            "❌ Nel foglio DATI_GRAFICO "
            "non è presente la colonna ADD."
        )

        return

    # ======================================================
    # APPLICA ORDINE
    # ======================================================

    (
        df_ordinato,
        add_presenti
    ) = _applica_ordine(
        df_grafico,
        tipo_dm
    )

    # ======================================================
    # METRICHE
    # ======================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Sensori trovati",
        len(df_ordinato)
    )

    if "I" in df_ordinato.columns:

        c2.metric(
            "Media I",
            f"{df_ordinato['I'].mean():.2f}"
        )

    if "I_I" in df_ordinato.columns:

        c3.metric(
            "Media I_I",
            f"{df_ordinato['I_I'].mean():.2f}"
        )

    c4.metric(
        "Ordine",
        tipo_dm
    )

    st.divider()

    # ======================================================
    # MOSTRA ORDINE
    # ======================================================

    st.subheader(
        f"📋 Ordine utilizzato: {tipo_dm}"
    )

    st.write(
        " → ".join(add_presenti)
    )

    st.divider()

    # ======================================================
    # FILTRI ADD
    # ======================================================

    add_selezionati = st.multiselect(
        "📍 Seleziona ADD",
        options=add_presenti,
        default=[],
        key="misurazione_add"
    )

    df_view = df_ordinato.copy()

    if add_selezionati:

        df_view = df_view[
            df_view["ADD"].isin(
                add_selezionati
            )
        ].copy()

        # Mantiene SEMPRE l'ordine DM1/DM8
        df_view["POSIZIONE"] = (
            df_view["ADD"].map(
                {
                    add: i
                    for i, add in enumerate(
                        ORDER_DM1
                        if tipo_dm == "DM1"
                        else ORDER_DM8
                    )
                }
            )
        )

        df_view = df_view.sort_values(
            "POSIZIONE"
        )

    # ======================================================
    # TABS
    # ======================================================

    tab_grafico, tab_misure, tab_anagrafica = st.tabs(
        [
            "📈 Grafico",
            "📊 Misurazioni",
            "🔧 Anagrafica sensori"
        ]
    )

    # ======================================================
    # GRAFICO
    # ======================================================

    with tab_grafico:

        st.subheader(
            f"📈 Misurazione sensori - {tipo_dm}"
        )

        if df_view.empty:

            st.warning(
                "Nessun sensore corrisponde ai filtri."
            )

        else:

            fig = _grafico_linee(
                df_view,
                tipo_dm
            )

            if fig is not None:

                st.pyplot(
                    fig,
                    use_container_width=True
                )

    # ======================================================
    # TABELLA
    # ======================================================

    with tab_misure:

        st.subheader(
            "📊 DATI_GRAFICO"
        )

        colonne = [
            c
            for c in [
                "ADD",
                "I",
                "I_I",
                "STA",
                "ORDINE",
                "POSIZIONE"
            ]
            if c in df_view.columns
        ]

        st.dataframe(
            df_view[colonne],
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------
        # CSV
        # --------------------------------------------------

        csv = (
            df_view[colonne]
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )

        st.download_button(
            "📥 Scarica CSV",
            data=csv,
            file_name=(
                f"misurazione_sensori_{tipo_dm}.csv"
            ),
            mime="text/csv"
        )

    # ======================================================
    # ANAGRAFICA
    # ======================================================

    with tab_anagrafica:

        st.subheader(
            "🔧 Anagrafica sensori"
        )

        if df_sensori.empty:

            st.warning(
                "Il foglio Foglio1 è vuoto."
            )

        else:

            colonne_preferite = [
                "Add",
                "M/S",
                "Type",
                "Man",
                "Serial",
                "N",
                "YY/WW",
                "PW1",
                "PW2",
                "PW3",
                "PW4",
                "PW5",
                "I",
                "I_I",
                "STA",
                "ISO"
            ]

            colonne = [
                c
                for c in colonne_preferite
                if c in df_sensori.columns
            ]

            st.dataframe(
                df_sensori[colonne],
                use_container_width=True,
                hide_index=True,
                height=600
            )
