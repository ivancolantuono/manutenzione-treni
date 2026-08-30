import streamlit as st
from pathlib import Path
import tempfile
import os
import time




# ==========================================================
# CONFIGURAZIONE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

FILE_EXCEL = BASE_DIR / "ATTIVITA' CARRELLO.xlsm"


# ==========================================================
# CONFIGURAZIONE PAGINA
# ==========================================================

st.set_page_config(
    page_title="Carrelli ETR1000",
    page_icon="🚆",
    layout="wide"
)


# ==========================================================
# CSS
# ==========================================================

st.markdown("""
<style>

/* =========================================
   TITOLO
   ========================================= */

.carrelli-titolo {

    background-color: #b7d7f0;

    padding: 14px;

    border-radius: 8px;

    text-align: center;

    font-size: 24px;

    font-weight: bold;

    margin-bottom: 20px;
}


/* =========================================
   PDF
   ========================================= */

.pdf-box {

    width: 100%;

    background: white;

    border-radius: 10px;

    overflow: hidden;

}


/* =========================================
   BOTTONI
   ========================================= */

.stButton > button {

    border-radius: 8px;

}

</style>
""", unsafe_allow_html=True)


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
# CONTROLLO EXCEL
# ==========================================================

def controllo_excel():

    if not FILE_EXCEL.exists():

        st.error(
            "❌ File Excel non trovato."
        )

        st.code(
            str(FILE_EXCEL)
        )

        st.info(
            "Il file deve essere nella stessa "
            "cartella di Carrelli.py."
        )

        return False

    return True


# ==========================================================
# LETTURA FOGLI
# ==========================================================

def elenco_fogli():

    if win32com is None:

        return []

    excel = None
    wb = None

    try:

        excel = win32com.client.DispatchEx(
            "Excel.Application"
        )

        excel.Visible = False
        excel.DisplayAlerts = False

        wb = excel.Workbooks.Open(
            str(FILE_EXCEL),
            ReadOnly=True
        )

        fogli = []

        for ws in wb.Worksheets:

            fogli.append(
                ws.Name
            )

        return fogli

    except Exception:

        return []

    finally:

        try:

            if wb is not None:
                wb.Close(
                    SaveChanges=False
                )

        except:
            pass

        try:

            if excel is not None:
                excel.Quit()

        except:
            pass


# ==========================================================
# CONVERSIONE FOGLIO EXCEL → PDF
# ==========================================================

def esporta_foglio_pdf(nome_foglio):

    """
    Apre Excel tramite COM e converte
    solamente il foglio selezionato in PDF.

    Il rendering viene fatto direttamente
    da Microsoft Excel.

    In questo modo vengono mantenuti:

    - immagini
    - forme
    - frecce
    - linee
    - colori
    - testi
    - diagrammi
    - celle unite
    - grafica originale
    """

    if win32com is None:

        raise Exception(
            "Modulo pywin32 non installato."
        )


    if not FILE_EXCEL.exists():

        raise Exception(
            "File Excel non trovato."
        )


    # ------------------------------------------------------
    # FILE TEMPORANEO
    # ------------------------------------------------------

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="carrelli_"
        )
    )

    pdf_path = (
        temp_dir
        / f"{nome_foglio}.pdf"
    )


    excel = None
    wb = None
    ws = None


    try:

        # ==================================================
        # AVVIA EXCEL
        # ==================================================

        excel = win32com.client.DispatchEx(
            "Excel.Application"
        )

        excel.Visible = False

        excel.DisplayAlerts = False

        excel.ScreenUpdating = False


        # ==================================================
        # APERTURA FILE
        # ==================================================

        wb = excel.Workbooks.Open(

            str(FILE_EXCEL),

            UpdateLinks=0,

            ReadOnly=True,

            IgnoreReadOnlyRecommended=True

        )


        # ==================================================
        # CERCA FOGLIO
        # ==================================================

        ws = wb.Worksheets(
            nome_foglio
        )


        # ==================================================
        # DISATTIVA GRIGLIA
        # ==================================================

        try:

            ws.Activate()

            excel.ActiveWindow.DisplayGridlines = False

        except:

            pass


        # ==================================================
        # PAGINA
        # ==================================================

        page = ws.PageSetup


        # --------------------------------------------------
        # AREA DI STAMPA
        # --------------------------------------------------

        try:

            used = ws.UsedRange

            first_row = used.Row

            first_col = used.Column

            last_row = (
                used.Row
                + used.Rows.Count
                - 1
            )

            last_col = (
                used.Column
                + used.Columns.Count
                - 1
            )

            # Conversione numeri → lettere

            def numero_colonna(n):

                risultato = ""

                while n > 0:

                    n, resto = divmod(
                        n - 1,
                        26
                    )

                    risultato = (
                        chr(65 + resto)
                        + risultato
                    )

                return risultato


            prima_colonna = numero_colonna(
                first_col
            )

            ultima_colonna = numero_colonna(
                last_col
            )


            area = (
                f"${prima_colonna}${first_row}:"
                f"${ultima_colonna}${last_row}"
            )

            page.PrintArea = area

        except:

            # Se qualcosa va storto,
            # lascia quella già presente in Excel.

            pass


        # ==================================================
        # ORIENTAMENTO
        # ==================================================

        try:

            # 2 = Landscape
            page.Orientation = 2

        except:

            pass


        # ==================================================
        # MARGINI
        # ==================================================

        try:

            page.LeftMargin = (
                excel.CentimetersToPoints(0.3)
            )

            page.RightMargin = (
                excel.CentimetersToPoints(0.3)
            )

            page.TopMargin = (
                excel.CentimetersToPoints(0.3)
            )

            page.BottomMargin = (
                excel.CentimetersToPoints(0.3)
            )

        except:

            pass


        # ==================================================
        # SCALATURA
        # ==================================================

        try:

            page.Zoom = False

            page.FitToPagesWide = 1

            page.FitToPagesTall = False

        except:

            pass


        # ==================================================
        # CENTRA FOGLIO
        # ==================================================

        try:

            page.CenterHorizontally = True

            page.CenterVertically = False

        except:

            pass


        # ==================================================
        # QUALITÀ
        # ==================================================

        try:

            page.PrintQuality = 600

        except:

            pass


        # ==================================================
        # ESPORTA PDF
        # ==================================================

        ws.ExportAsFixedFormat(

            Type=0,

            Filename=str(pdf_path),

            Quality=0,

            IncludeDocProperties=True,

            IgnorePrintAreas=False,

            OpenAfterPublish=False

        )


        # ==================================================
        # ATTESA FILE
        # ==================================================

        for _ in range(50):

            if pdf_path.exists():

                if pdf_path.stat().st_size > 0:

                    break

            time.sleep(0.1)


        if not pdf_path.exists():

            raise Exception(
                "Excel non ha creato il PDF."
            )


        if pdf_path.stat().st_size == 0:

            raise Exception(
                "Il PDF generato è vuoto."
            )


        # ==================================================
        # LETTURA
        # ==================================================

        with open(
            pdf_path,
            "rb"
        ) as f:

            pdf_data = f.read()


        return pdf_data


    finally:

        # ==================================================
        # CHIUSURA EXCEL
        # ==================================================

        try:

            if wb is not None:

                wb.Close(
                    SaveChanges=False
                )

        except:

            pass


        try:

            if excel is not None:

                excel.Quit()

        except:

            pass


        # ==================================================
        # PULIZIA COM
        # ==================================================

        try:

            del ws

        except:

            pass

        try:

            del wb

        except:

            pass

        try:

            del excel

        except:

            pass


        # ==================================================
        # ELIMINA TEMP
        # ==================================================

        try:

            if pdf_path.exists():

                pdf_path.unlink()

            temp_dir.rmdir()

        except:

            pass


# ==========================================================
# VISUALIZZA PDF
# ==========================================================

def visualizza_pdf(pdf_data):

    try:

        from streamlit_pdf_viewer import pdf_viewer

        pdf_viewer(

            input=pdf_data,

            width=1200

        )

    except ImportError:

        st.error(
            "❌ Manca streamlit-pdf-viewer."
        )

        st.info(
            "Installa con:"
        )

        st.code(
            "pip install streamlit-pdf-viewer"
        )

    except Exception as e:

        st.error(
            "❌ Errore visualizzazione PDF."
        )

        st.code(
            str(e)
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
    # CONTROLLO
    # ======================================================

    if not controllo_excel():

        return


    # ======================================================
    # CONTROLLO PYWIN32
    # ======================================================

    if win32com is None:

        st.error(
            "❌ pywin32 non è installato."
        )

        st.code(
            "pip install pywin32"
        )

        return


    # ======================================================
    # VERIFICA EXCEL
    # ======================================================

    try:

        fogli_reali = elenco_fogli()

    except:

        fogli_reali = []


    # ======================================================
    # SEZIONE
    # ======================================================

    sezione = st.selectbox(

        "📂 Sezione",

        list(
            SEZIONI.keys()
        ),

        key="carrelli_sezione"

    )


    # ======================================================
    # FOGLI DISPONIBILI
    # ======================================================

    fogli_sezione = [

        foglio

        for foglio in SEZIONI[sezione]

        if foglio in fogli_reali

    ]


    if not fogli_sezione:

        st.warning(
            "⚠️ Nessun foglio disponibile "
            "in questa sezione."
        )

        if fogli_reali:

            st.caption(
                "Fogli presenti nel file:"
            )

            st.write(
                fogli_reali
            )

        return


    # ======================================================
    # SELEZIONE FOGLIO
    # ======================================================

    foglio = st.selectbox(

        "📄 Foglio",

        fogli_sezione,

        key="carrelli_foglio"

    )


    # ======================================================
    # PULSANTE VISUALIZZA
    # ======================================================

    col1, col2, col3 = st.columns(
        [1, 1, 4]
    )


    with col1:

        visualizza = st.button(

            "👁️ Visualizza",

            use_container_width=True,

            type="primary"

        )


    with col2:

        if st.button(

            "🔄 Aggiorna",

            use_container_width=True

        ):

            st.session_state.pop(
                "carrelli_pdf",
                None
            )

            st.rerun()


    # ======================================================
    # CONVERSIONE
    # ======================================================

    if visualizza:

        with st.spinner(
            f"📄 Apertura di Excel e "
            f"renderizzazione di {foglio}..."
        ):

            try:

                pdf_data = (
                    esporta_foglio_pdf(
                        foglio
                    )
                )

                st.session_state[
                    "carrelli_pdf"
                ] = pdf_data

                st.session_state[
                    "carrelli_pdf_nome"
                ] = foglio


            except Exception as e:

                st.error(
                    "❌ Errore durante la "
                    "conversione Excel → PDF."
                )

                st.code(
                    str(e)
                )


    # ======================================================
    # VISUALIZZAZIONE
    # ======================================================

    if (
        "carrelli_pdf"
        in st.session_state
    ):

        st.divider()

        nome = st.session_state.get(
            "carrelli_pdf_nome",
            foglio
        )

        st.markdown(
            f"### 📄 {nome}"
        )

        visualizza_pdf(
            st.session_state[
                "carrelli_pdf"
            ]
        )


# ==========================================================
# AVVIO
# ==========================================================

if __name__ == "__main__":

    carrelli_page()
