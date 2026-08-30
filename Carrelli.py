import streamlit as st
from pathlib import Path
import base64


# ============================================================
# CONFIGURAZIONE
# ============================================================

st.set_page_config(
    page_title="Carrelli ETR1000",
    page_icon="🚆",
    layout="wide"
)


BASE_DIR = Path(__file__).resolve().parent

IMMAGINI_DIR = BASE_DIR / "carrelli_img"


# ============================================================
# FOGLI
# ============================================================

SEZIONI = {

    "🛞 CARRELLI": [
        "DM1-CARR.1",
        "DM1-CARR.2",
        "M3-CARR.1",
        "M3-CARR.2",
        "M6-CARR.1",
        "M6-CARR.2",
        "DM8-CARR.1",
        "DM8-CARR.2",
    ],

    "📡 SENSORI": [
        "SENSORI SPM",
        "PT100 RIDUTTORI",
    ],

    "🔌 FUSE LOOP": [
        "FUSE LOOP CASSA MOTOR",
        "FUSE LOOP TRENO COMPLETO",
    ],

    "🔄 DNRA": [
        "LOOP DNRA",
        "OVERVIEW DNRA",
    ],

    "🚆 STATO TRENO": [
        "STATO TRENO",
    ],
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       TITOLO
       ====================================================== */

    .carrelli-title {
        background: linear-gradient(
            90deg,
            #e30613,
            #f21b2d
        );

        color: white;

        padding: 16px 22px;

        border-radius: 10px;

        text-align: center;

        font-size: 26px;

        font-weight: 700;

        margin-bottom: 25px;
    }


    /* ======================================================
       CONTENITORE IMMAGINE
       ====================================================== */

    .foglio-container {

        width: 100%;

        background: white;

        border-radius: 10px;

        padding: 10px;

        margin-top: 15px;

        overflow: auto;

        box-shadow:
            0 2px 10px rgba(0,0,0,0.08);

    }


    .foglio-container img {

        display: block;

        width: 100%;

        height: auto;

        border-radius: 4px;

    }


    /* ======================================================
       INFO
       ====================================================== */

    .info-foglio {

        background: #f4f6f8;

        padding: 10px 15px;

        border-radius: 8px;

        margin-top: 10px;

        margin-bottom: 10px;

        color: #333;

        font-size: 14px;

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNZIONE - IMMAGINE
# ============================================================

def trova_immagine(nome_foglio):

    # Prima prova PNG
    png = IMMAGINI_DIR / f"{nome_foglio}.png"

    if png.exists():
        return png


    # Prova JPG
    jpg = IMMAGINI_DIR / f"{nome_foglio}.jpg"

    if jpg.exists():
        return jpg


    # Prova JPEG
    jpeg = IMMAGINI_DIR / f"{nome_foglio}.jpeg"

    if jpeg.exists():
        return jpeg


    return None


# ============================================================
# VISUALIZZA IMMAGINE
# ============================================================

def visualizza_foglio(nome_foglio):

    immagine = trova_immagine(nome_foglio)


    # --------------------------------------------------------
    # IMMAGINE NON TROVATA
    # --------------------------------------------------------

    if immagine is None:

        st.error(
            f"❌ Immagine non trovata per il foglio: "
            f"{nome_foglio}"
        )

        st.info(
            f"Devi inserire nella cartella "
            f"`carrelli_img` il file:"
        )

        st.code(
            f"{nome_foglio}.png"
        )

        return


    # --------------------------------------------------------
    # INFORMAZIONI
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="info-foglio">
            📂 Sezione: <b>{st.session_state.sezione}</b><br>
            📄 Foglio: <b>{nome_foglio}</b>
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # IMMAGINE
    # --------------------------------------------------------

    with open(immagine, "rb") as f:

        dati = f.read()


    encoded = base64.b64encode(dati).decode()


    # --------------------------------------------------------
    # MOSTRA IMMAGINE
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="foglio-container">

            <img
                src="data:image/png;base64,{encoded}"
            >

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGINA CARRELLI
# ============================================================

def carrelli_page():

    # --------------------------------------------------------
    # TITOLO
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="carrelli-title">
            🚆 CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CONTROLLO CARTELLA
    # --------------------------------------------------------

    if not IMMAGINI_DIR.exists():

        st.error(
            "❌ Cartella `carrelli_img` non trovata."
        )

        st.info(
            "Crea una cartella chiamata "
            "`carrelli_img` nella stessa cartella "
            "di carrelli.py."
        )

        return


    # --------------------------------------------------------
    # SEZIONE
    # --------------------------------------------------------

    sezione = st.selectbox(
        "📂 Sezione",
        list(SEZIONI.keys())
    )

    st.session_state.sezione = sezione


    # --------------------------------------------------------
    # FOGLI DISPONIBILI
    # --------------------------------------------------------

    fogli_disponibili = []

    for foglio in SEZIONI[sezione]:

        if trova_immagine(foglio) is not None:

            fogli_disponibili.append(foglio)


    # --------------------------------------------------------
    # NESSUN FOGLIO
    # --------------------------------------------------------

    if not fogli_disponibili:

        st.warning(
            "⚠️ Nessun foglio disponibile "
            "per questa sezione."
        )

        st.write(
            "Controlla che le immagini siano "
            "presenti nella cartella:"
        )

        st.code(
            str(IMMAGINI_DIR)
        )

        return


    # --------------------------------------------------------
    # FOGLIO
    # --------------------------------------------------------

    foglio = st.selectbox(
        "📄 Foglio",
        fogli_disponibili
    )


    st.divider()


    # --------------------------------------------------------
    # TITOLO FOGLIO
    # --------------------------------------------------------

    st.markdown(
        f"## 📄 {foglio}"
    )


    # --------------------------------------------------------
    # VISUALIZZAZIONE
    # --------------------------------------------------------

    visualizza_foglio(foglio)


# ============================================================
# AVVIO
# ============================================================

if __name__ == "__main__":

    carrelli_page()
