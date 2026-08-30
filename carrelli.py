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

    "SENSORI SPM": [

        "DM1-CARR.1",
        "DM1-CARR.2",

        "M3-CARR.1",
        "M3-CARR.2",

        "M6-CARR.1",
        "M6-CARR.2",

        "DM8-CARR.1",
        "DM8-CARR.2"
    ],


    "PT100 RIDUTTORI": [

        "PT100 RIDUTTORI"
    ],


    "TERMOFUSIBILI": [

        "TERMOFUSIBILI CASSA MOTOR"
       
    ],


    "IMS": [

        "LOOP IMS"
    
    ]

}


# ==========================================================
# CERCA IMMAGINE
# ==========================================================

def trova_immagini(nome_foglio):

    if not CARTELLA_IMMAGINI.exists():
        return []

    immagini = []

    estensioni = [
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.webp"
    ]

    nome_cercato = normalizza_nome(nome_foglio)

    for estensione in estensioni:

        for file in CARTELLA_IMMAGINI.glob(estensione):

            nome_file = normalizza_nome(file.name)

            # ----------------------------------------------
            # IMMAGINE SINGOLA
            # ----------------------------------------------

            if nome_file == nome_cercato:

                immagini.append(file)

            # ----------------------------------------------
            # LOOP IMS CON PIÙ IMMAGINI
            #
            # LOOP IMS 1
            # LOOP IMS 2
            # LOOP IMS 3
            # ----------------------------------------------

            elif nome_cercato == "loop ims":

                if nome_file.startswith("loop ims"):

                    immagini.append(file)

    # elimina duplicati
    immagini = list(dict.fromkeys(immagini))

    # ordine numerico
    def ordine(file):

        numeri = re.findall(
            r"\d+",
            file.stem
        )

        if numeri:
            return int(numeri[-1])

        return 0

    immagini.sort(key=ordine)

    return immagini

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

    immagini = trova_immagini(nome_foglio)

    if not immagini:

        st.error(
            f"❌ Nessuna immagine trovata per: {nome_foglio}"
        )

        return

    # Mostra tutte le immagini
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
    # SEZIONE
    # ------------------------------------------------------

    st.markdown(
        "### 🛠️ ATTIVITA' CARRELLO"
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
        "### CASSA E CARRELLO"
    )


    foglio = st.selectbox(
        "Foglio",
        SEZIONI[sezione],
        label_visibility="collapsed"
    )


   
    # ------------------------------------------------------
    # MOSTRA IMMAGINE
    # ------------------------------------------------------

    mostra_immagine(foglio)


  
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
