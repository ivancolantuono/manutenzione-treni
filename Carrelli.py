import streamlit as st
from pathlib import Path
import subprocess
import tempfile
import shutil
import os
import hashlib

from streamlit_pdf_viewer import pdf_viewer


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

FILE_EXCEL = BASE_DIR / "ATTIVITA' CARRELLO.xlsm"


# ==========================================================
# STILE
# ==========================================================

st.markdown("""
<style>

.carrelli-header {
    background: linear-gradient(90deg, #d40000, #ed1c24);
    color: white;
    padding: 18px 25px;
    border-radius: 12px;
    margin-bottom: 20px;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
}

.sezione-box {
    background: #f5f5f5;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 15px;
}

.pdf-box {
    background: white;
    border-radius: 10px;
    padding: 5px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# STRUTTURA SEZIONI
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


# ==========================================================
# VERIFICA LIBREOFFICE
# ==========================================================

def trova_libreoffice():

    possibili = [
        "libreoffice",
        "soffice",
        "/usr/bin/libreoffice",
        "/usr/bin/soffice",
    ]

    for programma in possibili:

        if shutil.which(programma):

            return programma

        if Path(programma).exists():

            return programma

    return None


# ==========================================================
# CONVERSIONE EXCEL → PDF
# ==========================================================

@st.cache_data(show_spinner=False)
def converti_excel_pdf(percorso_excel, file_hash):

    libreoffice = trova_libreoffice()

    if not libreoffice:

        raise RuntimeError(
            "LibreOffice non è installato sul server."
        )

    # ------------------------------------------------------
    # CARTELLA TEMPORANEA
    # ------------------------------------------------------

    cartella = Path(
        tempfile.mkdtemp(
            prefix="carrelli_"
        )
    )

    try:

        file_excel = Path(percorso_excel)

        # --------------------------------------------------
        # COPIA FILE
        # --------------------------------------------------

        file_locale = cartella / file_excel.name

        shutil.copy2(
            file_excel,
            file_locale
        )

        # --------------------------------------------------
        # CONVERSIONE
        # --------------------------------------------------

        comando = [

            libreoffice,

            "--headless",

            "--convert-to",
            "pdf",

            "--outdir",
            str(cartella),

            str(file_locale)

        ]

        risultato = subprocess.run(

            comando,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            text=True,

            timeout=180

        )

        pdf = cartella / (
            file_excel.stem + ".pdf"
        )

        # --------------------------------------------------
        # CONTROLLO
        # --------------------------------------------------

        if risultato.returncode != 0:

            raise RuntimeError(
                risultato.stderr
                or risultato.stdout
                or "Errore sconosciuto durante la conversione."
            )

        if not pdf.exists():

            raise RuntimeError(
                "LibreOffice non ha generato il PDF."
            )

        # --------------------------------------------------
        # LEGGE PDF IN MEMORIA
        # --------------------------------------------------

        with open(
            pdf,
            "rb"
        ) as f:

            contenuto = f.read()

        return contenuto

    finally:

        shutil.rmtree(
            cartella,
            ignore_errors=True
        )


# ==========================================================
# FUNZIONE PRINCIPALE
# ==========================================================

def carrelli_page():

    # ======================================================
    # TITOLO
    # ======================================================

    st.markdown(
        """
        <div class="carrelli-header">
            🚆 CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # VERIFICA FILE
    # ======================================================

    if not FILE_EXCEL.exists():

        st.error(
            "❌ File Excel non trovato."
        )

        st.write(
            "Percorso cercato:"
        )

        st.code(
            str(FILE_EXCEL)
        )

        st.info(
            """
            Il file deve essere presente nella stessa
            cartella di Carrelli.py:

            ATTIVITA' CARRELLO.xlsm
            """
        )

        return


    # ======================================================
    # CARICAMENTO FOGLI CON OPENPYXL
    # ======================================================

    try:

        import openpyxl

        wb = openpyxl.load_workbook(
            FILE_EXCEL,
            read_only=True,
            data_only=False,
            keep_vba=True
        )

        fogli_disponibili = wb.sheetnames

        wb.close()

    except Exception as e:

        st.error(
            "❌ Impossibile leggere il file Excel."
        )

        st.code(
            str(e)
        )

        return


    # ======================================================
    # COSTRUZIONE MENU
    # ======================================================

    sezioni_disponibili = {}

    for nome_sezione, fogli in SEZIONI.items():

        presenti = [

            foglio

            for foglio in fogli

            if foglio in fogli_disponibili

        ]

        if presenti:

            sezioni_disponibili[
                nome_sezione
            ] = presenti


    # ======================================================
    # SEZIONE
    # ======================================================

    st.markdown(
        "### 📂 Sezione"
    )

    sezione = st.selectbox(

        "Seleziona sezione",

        list(
            sezioni_disponibili.keys()
        ),

        label_visibility="collapsed"

    )


    # ======================================================
    # FOGLI
    # ======================================================

    fogli = sezioni_disponibili[
        sezione
    ]

    st.markdown(
        "### 📄 Foglio"
    )

    foglio = st.selectbox(

        "Seleziona foglio",

        fogli,

        label_visibility="collapsed"

    )


    st.divider()


    # ======================================================
    # INFORMAZIONI
    # ======================================================

    st.markdown(
        f"""
        <div style="
            background:#f1f1f1;
            padding:12px;
            border-radius:8px;
            margin-bottom:15px;
        ">

        <b>📂 Sezione:</b> {sezione}<br>
        <b>📄 Foglio:</b> {foglio}

        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # HASH FILE
    # ======================================================

    try:

        with open(
            FILE_EXCEL,
            "rb"
        ) as f:

            file_bytes = f.read()

        file_hash = hashlib.md5(
            file_bytes
        ).hexdigest()

    except Exception as e:

        st.error(
            "Errore nella lettura del file."
        )

        st.code(
            str(e)
        )

        return


    # ======================================================
    # CONVERSIONE
    # ======================================================

    with st.spinner(
        "🔄 Preparazione documento..."
    ):

        try:

            pdf_bytes = converti_excel_pdf(

                str(FILE_EXCEL),

                file_hash

            )

        except Exception as e:

            st.error(
                "❌ Errore nella conversione Excel → PDF."
            )

            st.code(
                str(e)
            )

            st.info(
                """
                Il server Streamlit deve avere
                LibreOffice installato.
                """
            )

            return


    # ======================================================
    # VISUALIZZAZIONE
    # ======================================================

    st.markdown(
        f"### 📄 {foglio}"
    )

    st.markdown(
        """
        <div class="pdf-box">
        """,
        unsafe_allow_html=True
    )

    try:

        pdf_viewer(
            pdf_bytes,
            width="100%"
        )

    except Exception as e:

        st.error(
            "❌ Errore nella visualizzazione del PDF."
        )

        st.code(
            str(e)
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ==========================================================
# AVVIO
# ==========================================================

if __name__ == "__main__":

    carrelli_page()
