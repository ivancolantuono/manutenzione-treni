import streamlit as st
from pathlib import Path
import re


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

CARTELLA_IMMAGINI = BASE_DIR / "carrelli_img"


# ==========================================================
# CONFIGURAZIONE PAGINA
# ==========================================================

st.set_page_config(
    page_title="Carrelli ETR1000",
    page_icon="🚆",
    layout="wide"
)


# ==========================================================
# STILE
# ==========================================================

def configura_pagina():

    st.markdown(
        """
        <style>

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

        .carrelli-info {
            background: #f4f5f7;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 10px;
            margin-bottom: 20px;
            font-size: 16px;
        }

        .titolo-foglio {
            font-size: 24px;
            font-weight: 700;
            margin-top: 20px;
            margin-bottom: 15px;
        }

        .immagine-carrello {
            background: white;
            border-radius: 10px;
            padding: 10px;
            margin-top: 15px;
            margin-bottom: 20px;
        }

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

    "SENSORI SPM": [

        "DM1-CARR.1.",
        "DM1-CARR.2.",

        "M3-CARR.1.",
        "M3-CARR.2.",

        "M6-CARR.1.",
        "M6-CARR.2.",

        "DM8-CARR.1.",
        "DM8-CARR.2."
    ],

    "PT100 RIDUTTORI": [

        "PT100 RIDUTTORI"
    ],

    "TERMOFUSIBILI": [

        "TERMOFUSIBILI CASSA MOTOR"
    ],

    "IMS": [

        "LOOP IMS"
    ],

    "DNRA": [

        "DNRA"
    ],

    "FRENO PARCHEGGIO": [

        "PARCHEGGIO FRENATO",
        "PARCHEGGIO SFRENATO"
    ]
}


# ==========================================================
# NORMALIZZA NOMI
# ==========================================================

def normalizza_nome(nome):

    nome = str(nome)

    nome = Path(nome).stem

    nome = nome.lower()

    nome = nome.replace("_", " ")
    nome = nome.replace("-", " ")

    nome = re.sub(
        r"\s+",
        " ",
        nome
    )

    return nome.strip()


# ==========================================================
# TROVA IMMAGINI
# ==========================================================

def trova_immagini(nome_foglio):

    # ------------------------------------------------------
    # Controlla cartella
    # ------------------------------------------------------

    if not CARTELLA_IMMAGINI.exists():

        return []


    immagini = []


    # ------------------------------------------------------
    # Nome del foglio
    # ------------------------------------------------------

    nome_cercato = normalizza_nome(
        nome_foglio
    )


    # ------------------------------------------------------
    # Legge TUTTI i file della cartella
    # ------------------------------------------------------

    try:

        files = list(
            CARTELLA_IMMAGINI.iterdir()
        )

    except Exception:

        return []


    # ------------------------------------------------------
    # Estensioni consentite
    # ------------------------------------------------------

    estensioni = {

        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    }


    # ------------------------------------------------------
    # Analizza ogni file
    # ------------------------------------------------------

    for file in files:

        # deve essere un file
        if not file.is_file():
            continue


        # controlla estensione
        if file.suffix.lower() not in estensioni:
            continue


        nome_file = normalizza_nome(
            file.name
        )


        # ==================================================
        # IMMAGINE SINGOLA
        # ==================================================

        if nome_file == nome_cercato:

            immagini.append(file)

            continue


        # ==================================================
        # LOOP IMS
        #
        # Accetta:
        #
        # LOOP IMS 1.jpeg
        # LOOP IMS 2.jpeg
        # LOOP IMS 3.jpeg
        #
        # ma anche:
        #
        # LOOP IMS_1.jpeg
        # LOOP IMS-1.jpeg
        # ==================================================

        if nome_cercato == "loop ims":

            if nome_file.startswith("loop ims"):

                immagini.append(file)


    # ======================================================
    # ELIMINA DUPLICATI
    # ======================================================

    immagini = list(
        dict.fromkeys(immagini)
    )


    # ======================================================
    # ORDINE NUMERICO
    # ======================================================

    def ordine(file):

        numeri = re.findall(
            r"\d+",
            file.stem
        )

        if numeri:

            return int(
                numeri[-1]
            )

        return 0


    immagini.sort(
        key=ordine
    )


    return immagini


# ==========================================================
# MOSTRA IMMAGINI
# ==========================================================

def mostra_immagine(nome_foglio):

    st.markdown(
        f"""
        <div class="titolo-foglio">
            📄 {nome_foglio}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ------------------------------------------------------
    # Cerca immagini
    # ------------------------------------------------------

    immagini = trova_immagini(
        nome_foglio
    )


    # ------------------------------------------------------
    # Nessuna immagine
    # ------------------------------------------------------

    if not immagini:

        st.error(
            f"❌ Nessuna immagine trovata per: {nome_foglio}"
        )

        st.info(
            f"Cartella cercata: {CARTELLA_IMMAGINI}"
        )

        return


   
    # ======================================================
    # MOSTRA TUTTE LE IMMAGINI
    # ======================================================

    for numero, immagine in enumerate(
        immagini,
        start=1
    ):

        if len(immagini) > 1:

            st.markdown(
                f"### Immagine {numero} di {len(immagini)}"
            )


        st.image(
            str(immagine),
            use_container_width=True
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
    # ATTIVITÀ CARRELLO
    # ------------------------------------------------------

    st.markdown(
        "### 🛠️ ATTIVITA' CARRELLO"
    )


    # ======================================================
    # CONTROLLO CARTELLA
    # ======================================================

    if not CARTELLA_IMMAGINI.exists():

        st.error(
            "❌ Cartella 'carrelli_img' non trovata."
        )

        st.info(
            "La cartella deve essere nella stessa posizione di carrelli.py."
        )

        st.code(
            str(CARTELLA_IMMAGINI)
        )

        return


    # ======================================================
    # SEZIONE
    # ======================================================

    sezione = st.selectbox(
        "Sezione",
        list(SEZIONI.keys()),
        label_visibility="collapsed"
    )


    # ======================================================
    # FOGLIO
    # ======================================================

    st.markdown(
        "### CASSA E CARRELLO"
    )


    foglio = st.selectbox(
        "Foglio",
        SEZIONI[sezione],
        label_visibility="collapsed"
    )


    # ======================================================
    # SEPARATORE
    # ======================================================

    st.divider()


    # ======================================================
    # MOSTRA IMMAGINI
    # ======================================================

    mostra_immagine(
        foglio
    )


# ==========================================================
# AVVIO
# ==========================================================

if __name__ == "__main__":

    carrelli_page()
