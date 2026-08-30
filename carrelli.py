import streamlit as st
from pathlib import Path


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "carrelli_img"


# ==========================================================
# CONFIGURAZIONE PAGINA
# ==========================================================

def configura_pagina():

    st.markdown(
        """
        <style>

        /* ================================================
           TITOLO
           ================================================ */

        .carrelli-titolo {
            background: #e30613;
            color: white;
            padding: 16px 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 25px;
        }


        /* ================================================
           BOX INFORMAZIONI
           ================================================ */

        .carrelli-info {
            background: #f4f5f7;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 10px;
            margin-bottom: 20px;
            font-size: 16px;
        }


        /* ================================================
           IMMAGINE
           ================================================ */

        .immagine-carrello {
            background: white;
            border-radius: 10px;
            padding: 10px;
            margin-top: 15px;
        }


        /* ================================================
           NASCONDE IL TESTO DEL FILE UPLOADER ECC.
           ================================================ */

        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# TITOLO
# ==========================================================

def mostra_titolo():

    st.markdown(
        """
        <div class="carrelli-titolo">
            🚆 CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# SEZIONI
# ==========================================================

SEZIONI = {

    "🛞 CARRELLI": [

        "DM1-CARR.1",
        "DM1-CARR.2",

        "M3-CARR.1",
        "M3-CARR.2",

        "M6-CARR.1",
        "M6-CARR.2",

        "DM8-CARR.1",
        "DM8-CARR.2"
    ],


    "📡 SENSORI": [

        "SENSORI SPM",
        "PT100 RIDUTTORI"
    ],


    "🔌 FUSE LOOP": [

        "FUSE LOOP CASSA MOTOR",
        "FUSE LOOP TRENO COMPLETO"
    ],


    "🔄 DNRA": [

        "LOOP DNRA",
        "OVERVIEW DNRA"
    ],


    "🚆 STATO TRENO": [

        "STATO TRENO"
    ]
}


# ==========================================================
# CERCA IMMAGINE
# ==========================================================

def trova_immagine(nome):

    if not IMG_DIR.exists():
        return None


    # ------------------------------------------------------
    # Prima prova con il nome esatto
    # ------------------------------------------------------

    estensioni = [

        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]


    for estensione in estensioni:

        percorso = IMG_DIR / f"{nome}{estensione}"

        if percorso.exists():

            return percorso


    # ------------------------------------------------------
    # Seconda ricerca:
    # confronto senza distinzione tra maiuscole/minuscole
    # ------------------------------------------------------

    nome_lower = nome.lower().strip()


    try:

        for file in IMG_DIR.iterdir():

            if not file.is_file():
                continue

            if file.suffix.lower() not in estensioni:
                continue

            nome_file = file.stem.lower().strip()

            if nome_file == nome_lower:

                return file

    except Exception:

        return None


    return None


# ==========================================================
# MOSTRA IMMAGINE
# ==========================================================

def mostra_immagine(foglio):

    immagine = trova_immagine(foglio)


    # ------------------------------------------------------
    # IMMAGINE TROVATA
    # ------------------------------------------------------

    if immagine is not None:

        st.markdown(
            f"### 📄 {foglio}"
        )


        st.markdown(
            '<div class="immagine-carrello">',
            unsafe_allow_html=True
        )


        st.image(
            str(immagine),
            use_container_width=True
        )


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        return


    # ------------------------------------------------------
    # IMMAGINE NON TROVATA
    # ------------------------------------------------------

    st.warning(
        f"⚠️ Immagine non disponibile per: {foglio}"
    )


    st.info(
        "Carica l'immagine nella cartella "
        "`carrelli_img` del repository GitHub."
    )


    st.code(
        f"{foglio}.jpeg"
    )


# ==========================================================
# CONTROLLO CARTELLA
# ==========================================================

def controllo_cartella():

    with st.expander("🔧 Controllo immagini"):

        st.write(
            "Cartella utilizzata:"
        )

        st.code(
            str(IMG_DIR)
        )


        # --------------------------------------------------
        # CARTELLA NON ESISTE
        # --------------------------------------------------

        if not IMG_DIR.exists():

            st.error(
                "❌ La cartella carrelli_img non esiste."
            )

            return


        # --------------------------------------------------
        # LEGGI FILE
        # --------------------------------------------------

        try:

            files = [

                file

                for file in IMG_DIR.iterdir()

                if file.is_file()

            ]

        except Exception as e:

            st.error(
                "Errore nella lettura della cartella."
            )

            st.code(
                str(e)
            )

            return


        # --------------------------------------------------
        # CARTELLA VUOTA
        # --------------------------------------------------

        if not files:

            st.warning(
                "⚠️ La cartella carrelli_img è vuota."
            )

            return


        # --------------------------------------------------
        # FILE PRESENTI
        # --------------------------------------------------

        st.write(
            f"Immagini/file presenti: {len(files)}"
        )


        for file in sorted(files):

            st.write(
                f"• {file.name}"
            )


# ==========================================================
# PAGINA CARRELLI
# ==========================================================

def carrelli_page():

    # ------------------------------------------------------
    # STILE
    # ------------------------------------------------------

    configura_pagina()


    # ------------------------------------------------------
    # TITOLO
    # ------------------------------------------------------

    mostra_titolo()


    # ------------------------------------------------------
    # SEZIONE
    # ------------------------------------------------------

    st.markdown(
        "### 📂 Sezione"
    )


    sezione = st.selectbox(
        "Sezione",
        list(SEZIONI.keys()),
        label_visibility="collapsed"
    )


    # ------------------------------------------------------
    # FOGLIO
    # ------------------------------------------------------

    st.markdown(
        "### 📄 Foglio"
    )


    foglio = st.selectbox(
        "Foglio",
        SEZIONI[sezione],
        label_visibility="collapsed"
    )


    # ------------------------------------------------------
    # SEPARATORE
    # ------------------------------------------------------

    st.divider()


    # ------------------------------------------------------
    # INFORMAZIONI
    # ------------------------------------------------------

    st.markdown(
        f"""
        <div class="carrelli-info">
            📂 <b>Sezione:</b> {sezione}<br>
            📄 <b>Foglio:</b> {foglio}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ------------------------------------------------------
    # MOSTRA IMMAGINE
    # ------------------------------------------------------

    mostra_immagine(foglio)


    # ------------------------------------------------------
    # DEBUG
    # ------------------------------------------------------

    controllo_cartella()


# ==========================================================
# AVVIO DIRETTO
# ==========================================================

if __name__ == "__main__":

    st.set_page_config(
        page_title="Carrelli ETR1000",
        page_icon="🚆",
        layout="wide"
    )

    carrelli_page()
