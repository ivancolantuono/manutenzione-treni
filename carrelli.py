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

BASE_DIR = Path(__file__).resolve().parent
IMMAGINI_DIR = BASE_DIR / "carrelli_img"


# ==========================================================
# STILE
# ==========================================================

st.markdown(
    """
    <style>

    .carrelli-titolo {
        background-color: #e30613;
        color: white;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 25px;
    }

    .titolo-foglio {
        background-color: #f1f3f5;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .titolo-immagine {
        font-size: 17px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 8px;
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
    ],

    "🔧 IMS": [
        "LOOP IMS"
    ]
}


# ==========================================================
# NORMALIZZAZIONE
# ==========================================================

def normalizza_nome(nome):

    nome = str(nome).lower()

    # togli estensione
    nome = re.sub(
        r"\.(png|jpg|jpeg|webp)$",
        "",
        nome
    )

    # uniforma trattini e underscore
    nome = nome.replace("_", " ")
    nome = nome.replace("-", " ")

    # elimina spazi doppi
    nome = re.sub(
        r"\s+",
        " ",
        nome
    )

    return nome.strip()


# ==========================================================
# NUMERO IMMAGINE
# ==========================================================

def numero_immagine(file):

    numeri = re.findall(
        r"\d+",
        file.stem
    )

    if numeri:
        return int(numeri[-1])

    return 0


# ==========================================================
# CERCA IMMAGINI
# ==========================================================

def trova_immagini(nome_foglio):

    cartella = Path(__file__).resolve().parent / "carrelli_img"

    if not cartella.exists():
        return []

    immagini = []

    estensioni = [
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.webp"
    ]

    nome_cercato = normalizza_nome(
        nome_foglio
    )

    # ------------------------------------------------------
    # SCANSIONE CARTELLA
    # ------------------------------------------------------

    for estensione in estensioni:

        for file in cartella.glob(estensione):

            nome_file = normalizza_nome(
                file.name
            )

            # ==================================================
            # CASO 1
            # NOME IDENTICO
            #
            # PT100 RIDUTTORI.jpeg
            # ==================================================

            if nome_file == nome_cercato:

                immagini.append(file)

                continue

            # ==================================================
            # CASO 2
            # PIÙ IMMAGINI LOOP IMS
            #
            # LOOP IMS 1.jpeg
            # LOOP IMS 2.jpeg
            # LOOP IMS 3.jpeg
            # ==================================================

            if nome_cercato == "loop ims":

                if nome_file.startswith("loop ims "):

                    immagini.append(file)

    # ------------------------------------------------------
    # ELIMINA DUPLICATI
    # ------------------------------------------------------

    immagini = list(
        dict.fromkeys(immagini)
    )

    # ------------------------------------------------------
    # ORDINE
    # ------------------------------------------------------

    immagini.sort(
        key=numero_immagine
    )

    return immagini


# ==========================================================
# MOSTRA FOGLIO
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

    immagini = trova_immagini(
        nome_foglio
    )

    # ------------------------------------------------------
    # NESSUNA IMMAGINE
    # ------------------------------------------------------

    if not immagini:

        st.error(
            f"❌ Nessuna immagine trovata per '{nome_foglio}'."
        )

        st.info(
            "Controlla che l'immagine sia presente "
            "nella cartella carrelli_img su GitHub."
        )

        st.code(
            f"carrelli_img/{nome_foglio}.png"
        )

        return

    # ------------------------------------------------------
    # UNA SOLA IMMAGINE
    # ------------------------------------------------------

    if len(immagini) == 1:

        st.image(
            str(immagini[0]),
            use_container_width=True
        )

        return

    # ------------------------------------------------------
    # PIÙ IMMAGINI
    # ------------------------------------------------------

    st.success(
        f"✅ Trovate {len(immagini)} immagini"
    )

    for indice, immagine in enumerate(
        immagini,
        start=1
    ):

        st.markdown(
            f"""
            <div class="titolo-immagine">
                Immagine {indice} di {len(immagini)}
            </div>
            """,
            unsafe_allow_html=True
        )

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
    # CARTELLA IMMAGINI
    # ======================================================

    if not IMMAGINI_DIR.exists():

        st.error(
            "❌ Cartella 'carrelli_img' non trovata."
        )

        st.info(
            "La cartella deve essere nella stessa "
            "posizione di carrelli.py."
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
    # FOGLI
    # ======================================================

    fogli = SEZIONI[sezione]

    foglio = st.selectbox(
        "📄 Foglio",
        fogli,
        key="carrelli_foglio"
    )

    st.divider()

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
