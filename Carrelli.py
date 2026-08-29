import streamlit as st
from pathlib import Path
import tempfile
import os

# ==========================================================
# CONFIGURAZIONE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

FILE_EXCEL = BASE_DIR / "ATTIVITA' CARRELLO.xlsm"


# ==========================================================
# PAGINA
# ==========================================================

def carrelli_page():

    # ======================================================
    # STILE
    # ======================================================

    st.markdown(
        """
        <style>

        .titolo-carrelli {
            background-color: #b7d7f0;
            padding: 12px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .sezione-carrelli {
            border: 2px solid #777;
            border-radius: 8px;
            padding: 10px;
            background-color: #fafafa;
            margin-bottom: 15px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # TITOLO
    # ======================================================

    st.markdown(
        """
        <div class="titolo-carrelli">
            🚆 CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # CONTROLLO FILE
    # ======================================================

    if not FILE_EXCEL.exists():

        st.error(
            "❌ File Excel non trovato."
        )

        st.info(
            "Il file deve chiamarsi:\n\n"
            "ATTIVITA' CARRELLO.xlsm\n\n"
            "e deve essere nella stessa cartella "
            "di Carrelli.py."
        )

        return


    # ======================================================
    # IMPORT OPENPYXL
    # ======================================================

    try:

        import openpyxl

    except ImportError:

        st.error(
            "❌ Manca il modulo openpyxl."
        )

        st.code(
            "pip install openpyxl"
        )

        return


    # ======================================================
    # IMPORT LIBREOFFICE
    # ======================================================

    # LibreOffice serve per trasformare il foglio Excel
    # in PDF mantenendo la parte grafica.
    #
    # Cerchiamo automaticamente il programma.

    possibili_libreoffice = [

        r"C:\Program Files\LibreOffice\program\soffice.exe",

        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",

        "soffice",

    ]

    soffice = None

    for programma in possibili_libreoffice:

        if programma == "soffice":

            soffice = programma
            break

        if Path(programma).exists():

            soffice = programma
            break


    # ======================================================
    # CARICA FOGLI
    # ======================================================

    @st.cache_data
    def carica_fogli(percorso):

        wb = openpyxl.load_workbook(
            percorso,
            read_only=True,
            keep_vba=True,
            data_only=False
        )

        return wb.sheetnames


    try:

        fogli = carica_fogli(
            str(FILE_EXCEL)
        )

    except Exception as e:

        st.error(
            "❌ Impossibile leggere il file Excel."
        )

        st.code(str(e))

        return


    # ======================================================
    # SEZIONI
    # ======================================================

    sezioni = {

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


    # ======================================================
    # SEZIONE
    # ======================================================

    sezione = st.selectbox(
        "📂 Seleziona sezione",
        list(sezioni.keys()),
        key="carrelli_sezione"
    )


    # ======================================================
    # FOGLI PRESENTI
    # ======================================================

    fogli_disponibili = [

        f
        for f in sezioni[sezione]
        if f in fogli

    ]


    if not fogli_disponibili:

        st.warning(
            "Nessun foglio disponibile "
            "per questa sezione."
        )

        return


    # ======================================================
    # FOGLIO
    # ======================================================

    foglio = st.selectbox(
        "🚆 Seleziona",
        fogli_disponibili,
        key="carrelli_foglio"
    )


    st.divider()


    # ======================================================
    # TITOLO FOGLIO
    # ======================================================

    st.markdown(
        f"""
        <div class="sezione-carrelli">

        <h3 style="margin:0;">
        📄 {foglio}
        </h3>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # RENDER EXCEL
    # ======================================================

    if soffice is None:

        st.warning(
            "⚠️ LibreOffice non è installato."
        )

        st.info(
            "Per visualizzare il foglio esattamente "
            "come Excel, installa LibreOffice sul PC."
        )

        st.markdown(
            """
            In alternativa posso preparare una
            versione che usa direttamente Excel
            tramite Windows.
            """
        )

        return


    # ======================================================
    # FUNZIONE CONVERSIONE
    # ======================================================

    def excel_to_pdf():

        cartella_temp = Path(
            tempfile.mkdtemp(
                prefix="carrelli_"
            )
        )

        # Copia Excel nella cartella temporanea
        copia_excel = (
            cartella_temp /
            FILE_EXCEL.name
        )

        copia_excel.write_bytes(
            FILE_EXCEL.read_bytes()
        )


        # --------------------------------------------------
        # COMANDO LIBREOFFICE
        # --------------------------------------------------

        import subprocess

        comando = [

            soffice,

            "--headless",

            "--convert-to",
            "pdf",

            "--outdir",
            str(cartella_temp),

            str(copia_excel)

        ]


        risultato = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=120
        )


        pdf = (
            cartella_temp /
            f"{FILE_EXCEL.stem}.pdf"
        )


        if not pdf.exists():

            raise Exception(
                "LibreOffice non ha generato il PDF.\n\n"
                + risultato.stdout
                + "\n"
                + risultato.stderr
            )


        return pdf


    # ======================================================
    # CONVERSIONE
    # ======================================================

    try:

        with st.spinner(
            "🔄 Preparazione visualizzazione Excel..."
        ):

            pdf_file = excel_to_pdf()


    except Exception as e:

        st.error(
            "❌ Errore nella conversione Excel → PDF."
        )

        st.code(str(e))

        return


    # ======================================================
    # PDF VIEWER
    # ======================================================

    try:

        from streamlit_pdf_viewer import pdf_viewer

        # --------------------------------------------------
        # Visualizza il PDF
        # --------------------------------------------------

        pdf_bytes = pdf_file.read_bytes()

        pdf_viewer(
            pdf_bytes,
            width="100%"
        )

    except ImportError:

        st.error(
            "❌ Manca streamlit-pdf-viewer."
        )

        st.code(
            "pip install streamlit-pdf-viewer"
        )

    except Exception as e:

        st.error(
            "❌ Errore visualizzazione PDF."
        )

        st.code(str(e))


    # ======================================================
    # INFORMAZIONE
    # ======================================================

    st.caption(
        "Visualizzazione renderizzata del foglio Excel "
        "originale, comprensiva della formattazione "
        "grafica e delle immagini incorporate."
    )
