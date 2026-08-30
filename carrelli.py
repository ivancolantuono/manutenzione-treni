import streamlit as st
from pathlib import Path
import re


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

st.set_page_config(
    page_title="Carrelli ETR1000",
    page_icon="🚆",
    layout="wide"
)


# ==========================================================
# CARTELLA IMMAGINI
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

CARTELLA_IMMAGINI = BASE_DIR / "carrelli_img"


# ==========================================================
# STILE
# ==========================================================

st.markdown(
    """
    <style>

    /* Titolo */
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

    /* Titolo foglio */
    .titolo-foglio {
        background: #f1f3f5;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* Contenitore immagine */
    .immagine-container {
        background: white;
        border-radius: 10px;
        padding: 10px;
        margin-top: 10px;
    }

    </style>
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
# NORMALIZZAZIONE NOMI
# ==========================================================

def normalizza_nome(nome):

    nome = str(nome).lower()

    # togli estensione
    nome = re.sub(
        r"\.(png|jpg|jpeg|webp)$",
        "",
        nome
    )

    # uniforma separatori
    nome = nome.replace("_", " ")
    nome = nome.replace("-", " ")

    # elimina spazi multipli
    nome = re.sub(
        r"\s+",
        " ",
        nome
    )

    return nome.strip()


# ==========================================================
# CERCA IMMAGINE
# ==========================================================

def trova_immagine(nome_foglio):

    if not CARTELLA_IMMAGINI.exists():
        return None

    nome_cercato = normalizza_nome(
        nome_foglio
    )

    estensioni = [
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.webp"
    ]

    for estensione in estensioni:

        for file in CARTELLA_IMMAGINI.glob(estensione):

            nome_file = normalizza_nome(
                file.name
            )

            if nome_file == nome_cercato:

                return file

    return None


# ==========================================================
# MOSTRA IMMAGINE
# ==========================================================

def mostra_foglio(nome_foglio):

    st.markdown(
        f"""
        <div class="titolo-foglio">
            📄 {nome_foglio}
        </div>
        """,
        unsafe_allow_html=True
    )

    immagine = trova_immagine(
        nome_foglio
    )

    # ------------------------------------------------------
    # IMMAGINE NON TROVATA
    # ------------------------------------------------------

    if immagine is None:

        st.error(
            f"❌ Immagine non trovata per: {nome_foglio}"
        )

        st.info(
            "Carica nella cartella "
            "`carrelli_img` un'immagine chiamata:"
        )

        st.code(
            f"{nome_foglio}.png"
        )

        return

    # ------------------------------------------------------
    # IMMAGINE TROVATA
    # ------------------------------------------------------

    st.image(
        str(immagine),
        use_container_width=True
    )


# ==========================================================
# PAGINA CARRELLI
# ==========================================================

def carrelli_page():

    # ======================================================
    # TITOLO
    # ======================================================

    st.markdown(
        """
        <div class="carrelli-titolo">
            🚆 CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # CONTROLLO CARTELLA
    # ======================================================

    if not CARTELLA_IMMAGINI.exists():

        st.error(
            "❌ Cartella `carrelli_img` non trovata."
        )

        st.info(
            "Crea la cartella `carrelli_img` "
            "nella stessa posizione di `carrelli.py` "
            "e inserisci le immagini."
        )

        return

    # ======================================================
    # SEZIONE
    # ======================================================

    sezione = st.selectbox(
        "📂 Sezione",
        list(SEZIONI.keys()),
        key="carrelli_sezione"
    )

    # ======================================================
    # FOGLI DELLA SEZIONE
    # ======================================================

    fogli = SEZIONI[sezione]

    # ======================================================
    # SELEZIONE FOGLIO
    # ======================================================

    foglio = st.selectbox(
        "📄 Foglio",
        fogli,
        key="carrelli_foglio"
    )

    st.divider()

    # ======================================================
    # INFORMAZIONI
    # ======================================================

    st.caption(
        f"📂 Sezione: {sezione}"
    )

    st.caption(
        f"📄 Foglio: {foglio}"
    )

    # ======================================================
    # VISUALIZZAZIONE
    # ======================================================

    mostra_foglio(
        foglio
    )


# ==========================================================
# AVVIO
# ==========================================================

if __name__ == "__main__":

    carrelli_page()
