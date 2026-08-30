import streamlit as st
from pathlib import Path


# ==========================================================
# PERCORSO IMMAGINI
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "carrelli_img"


# ==========================================================
# FUNZIONE PER CERCARE L'IMMAGINE
# ==========================================================

def trova_immagine(nome):

    estensioni = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]

    for estensione in estensioni:

        file = IMG_DIR / f"{nome}{estensione}"

        if file.exists():
            return file

    return None


# ==========================================================
# PAGINA CARRELLI
# ==========================================================

def carrelli_page():

    # ------------------------------------------------------
    # CONFIGURAZIONE GRAFICA
    # ------------------------------------------------------

    st.markdown("""
    <style>

    .carrelli-titolo {
        background: #e30613;
        color: white;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 25px;
    }

    .info-box {
        background: #f3f4f6;
        padding: 12px 16px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    </style>
    """, unsafe_allow_html=True)


    # ------------------------------------------------------
    # TITOLO
    # ------------------------------------------------------

    st.markdown(
        '<div class="carrelli-titolo">🚆 CARRELLI ETR1000</div>',
        unsafe_allow_html=True
    )


    # ------------------------------------------------------
    # SEZIONI
    # ------------------------------------------------------

    sezioni = {

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


    # ------------------------------------------------------
    # SEZIONE
    # ------------------------------------------------------

    st.markdown("### 📂 Sezione")

    sezione = st.selectbox(
        "Sezione",
        list(sezioni.keys()),
        label_visibility="collapsed"
    )


    # ------------------------------------------------------
    # FOGLIO
    # ------------------------------------------------------

    st.markdown("### 📄 Foglio")

    foglio = st.selectbox(
        "Foglio",
        sezioni[sezione],
        label_visibility="collapsed"
    )


    st.divider()


    # ------------------------------------------------------
    # INFORMAZIONI
    # ------------------------------------------------------

    st.markdown(
        f"""
        <div class="info-box">
            📂 <b>Sezione:</b> {sezione}<br>
            📄 <b>Foglio:</b> {foglio}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ------------------------------------------------------
    # CERCA IMMAGINE
    # ------------------------------------------------------

    immagine = trova_immagine(foglio)


    # ------------------------------------------------------
    # MOSTRA IMMAGINE
    # ------------------------------------------------------

    if immagine:

        st.markdown(
            f"### 📄 {foglio}"
        )

        st.image(
            str(immagine),
            use_container_width=True
        )


    else:

        st.warning(
            f"⚠️ Immagine non ancora disponibile per: {foglio}"
        )

        st.info(
            "Carica l'immagine nella cartella carrelli_img "
            "con il nome del foglio."
        )

        st.code(
            f"{foglio}.png\n"
            f"{foglio}.jpg\n"
            f"{foglio}.jpeg"
        )


    # ------------------------------------------------------
    # CONTROLLO CARTELLA
    # ------------------------------------------------------

    with st.expander("🔧 Controllo immagini"):

        st.write("Percorso cartella:")

        st.code(str(IMG_DIR))

        if IMG_DIR.exists():

            immagini = [
                f.name
                for f in IMG_DIR.iterdir()
                if f.is_file()
            ]

            if immagini:

                st.write("File presenti:")

                for file in sorted(immagini):
                    st.write(f"• {file}")

            else:

                st.warning(
                    "La cartella carrelli_img è vuota."
                )

        else:

            st.error(
                "La cartella carrelli_img non esiste."
            )
