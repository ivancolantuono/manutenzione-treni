import streamlit as st
import pandas as pd
import numpy as np
import io

# ==========================================================
# MISURAZIONE SENSORI
# Conversione del file Excel "Misurazione sensori.xlsm"
# ==========================================================

def _carica_excel(uploaded_file):
    """Legge i due fogli del file Excel senza dipendere da macro/VBA."""
    return (
        pd.read_excel(uploaded_file, sheet_name="DATI_GRAFICO"),
        pd.read_excel(uploaded_file, sheet_name="Foglio1"),
    )


def _normalizza_colonne(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _prepara_dati(df_grafico, df_sensori):
    df_grafico = _normalizza_colonne(df_grafico)
    df_sensori = _normalizza_colonne(df_sensori)

    # Il foglio DATI_GRAFICO contiene già l'ordinamento usato
    # dal grafico originale Excel.
    if "ORDINE" in df_grafico.columns:
        df_grafico = df_grafico.sort_values("ORDINE").reset_index(drop=True)

    # Conversione numerica delle misure
    for col in ["I", "I_I", "ADD", "ORDINE"]:
        if col in df_grafico.columns:
            df_grafico[col] = pd.to_numeric(
                df_grafico[col], errors="coerce"
            )

    for col in ["I", "I_I", "ADD"]:
        if col in df_sensori.columns:
            df_sensori[col] = pd.to_numeric(
                df_sensori[col], errors="coerce"
            )

    return df_grafico, df_sensori


def _grafico_linee(df):
    """Ricrea il grafico del foglio DATI_GRAFICO con linee."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 5))

    x = df["ADD"].astype(str)

    ax.plot(
        x,
        df["I"],
        marker="o",
        linewidth=2,
        label="I",
    )

    ax.plot(
        x,
        df["I_I"],
        marker="o",
        linewidth=2,
        label="I_I",
    )

    ax.set_title("ORDINATO DA DM1")
    ax.set_xlabel("ADD")
    ax.set_ylabel("Valore")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()

    return fig


def misurazione_sensori_page():

    st.title("🔬 Misurazione Sensori")
    st.caption(
        "Analisi delle misure I e I_I dei sensori "
        "ordinati secondo il file DATI_GRAFICO."
    )

    # ======================================================
    # UPLOAD
    # ======================================================

    uploaded_file = st.file_uploader(
        "📥 Carica Misurazione sensori.xlsm",
        type=["xlsm", "xlsx"],
        key="misurazione_sensori_file",
    )

    if uploaded_file is None:
        st.info("Carica il file Excel per iniziare.")
        return

    # ======================================================
    # LETTURA
    # ======================================================

    try:
        with st.spinner("🔄 Lettura misurazioni..."):
            df_grafico, df_sensori = _carica_excel(uploaded_file)
            df_grafico, df_sensori = _prepara_dati(
                df_grafico,
                df_sensori,
            )

    except Exception as e:
        st.error("❌ Errore durante la lettura del file.")
        st.exception(e)
        return

    if df_grafico.empty:
        st.warning("⚠️ Il foglio DATI_GRAFICO è vuoto.")
        return

    # ======================================================
    # METRICHE
    # ======================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Sensori",
        len(df_grafico),
    )

    if "I" in df_grafico:
        c2.metric(
            "Media I",
            f"{df_grafico['I'].mean():.2f}",
        )

    if "I_I" in df_grafico:
        c3.metric(
            "Media I_I",
            f"{df_grafico['I_I'].mean():.2f}",
        )

    if "ADD" in df_grafico:
        c4.metric(
            "ADD",
            int(df_grafico["ADD"].nunique()),
        )

    st.divider()

    # ======================================================
    # FILTRI
    # ======================================================

    st.subheader("🔎 Filtri")

    col1, col2 = st.columns(2)

    with col1:
        add_disponibili = (
            df_grafico["ADD"]
            .dropna()
            .tolist()
            if "ADD" in df_grafico.columns
            else []
        )

        add_selezionati = st.multiselect(
            "📍 ADD",
            options=add_disponibili,
            default=[],
            key="misurazione_add",
        )

    with col2:
        ricerca = st.text_input(
            "🔍 Cerca sensore / seriale",
            placeholder="ADD, seriale, tipo, modello...",
            key="misurazione_ricerca",
        )

    df_view = df_grafico.copy()

    if add_selezionati:
        df_view = df_view[
            df_view["ADD"].isin(add_selezionati)
        ]

    # Se possibile arricchiamo la ricerca con Foglio1
    if ricerca and not df_sensori.empty:
        testo = (
            df_sensori.astype(str)
            .fillna("")
            .agg(" ".join, axis=1)
            .str.lower()
        )

        mask = testo.str.contains(
            ricerca.lower().strip(),
            regex=False,
            na=False,
        )

        if "ADD" in df_sensori.columns:
            add_trovati = df_sensori.loc[mask, "ADD"].tolist()
            df_view = df_view[
                df_view["ADD"].isin(add_trovati)
            ]

    # ======================================================
    # TABS
    # ======================================================

    tab_grafico, tab_misure, tab_anagrafica = st.tabs(
        [
            "📈 Grafico",
            "📊 Misurazioni",
            "🔧 Anagrafica sensori",
        ]
    )

    # ======================================================
    # GRAFICO
    # ======================================================

    with tab_grafico:

        st.subheader("📈 Misurazione")

        if df_view.empty:
            st.warning("Nessun sensore corrisponde ai filtri.")
        else:
            fig = _grafico_linee(df_view)
            st.pyplot(fig, use_container_width=True)

    # ======================================================
    # TABELLA MISURAZIONI
    # ======================================================

    with tab_misure:

        st.subheader("📊 DATI_GRAFICO")

        colonne = [
            c for c in
            ["ADD", "I", "I_I", "ORDINE"]
            if c in df_view.columns
        ]

        st.dataframe(
            df_view[colonne],
            use_container_width=True,
            hide_index=True,
        )

        # CSV
        csv = df_view[colonne].to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 Scarica CSV",
            data=csv,
            file_name="misurazione_sensori.csv",
            mime="text/csv",
        )

    # ======================================================
    # ANAGRAFICA
    # ======================================================

    with tab_anagrafica:

        st.subheader("🔧 Anagrafica sensori")

        if df_sensori.empty:
            st.warning("Il foglio Foglio1 è vuoto.")
        else:

            # Selezione colonne leggibile
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
                "ISO",
            ]

            colonne = [
                c for c in colonne_preferite
                if c in df_sensori.columns
            ]

            st.dataframe(
                df_sensori[colonne],
                use_container_width=True,
                hide_index=True,
                height=600,
            )
