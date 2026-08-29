import streamlit as st
import pandas as pd
from pathlib import Path
import zipfile
import shutil
import os


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

FILE_EXCEL = BASE_DIR / "ATTIVITA' CARRELLO.xlsm"

CARTELLA_IMMAGINI = BASE_DIR / "immagini_carrelli"


# ==========================================================
# PAGINA CARRELLI
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

        .box-carrelli {
            border: 2px solid #777;
            border-radius: 10px;
            padding: 15px;
            background-color: #fafafa;
            margin-bottom: 15px;
        }

        .immagine-box {
            border: 1px solid #aaa;
            border-radius: 8px;
            padding: 8px;
            background-color: white;
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
            🚆 DIAGNOSTICA CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # CONTROLLO FILE
    # ======================================================

    if not FILE_EXCEL.exists():

        st.error(
            f"❌ File Excel non trovato:\n\n"
            f"{FILE_EXCEL}"
        )

        st.info(
            "Metti ATTIVITA' CARRELLO.xlsm "
            "nella stessa cartella di Carrelli.py."
        )

        return


    # ======================================================
    # ESTRAZIONE IMMAGINI
    # ======================================================

    def estrai_immagini():

        CARTELLA_IMMAGINI.mkdir(
            parents=True,
            exist_ok=True
        )

        immagini_esistenti = list(
            CARTELLA_IMMAGINI.glob("*")
        )

        if immagini_esistenti:
            return immagini_esistenti


        immagini = []

        try:

            with zipfile.ZipFile(
                FILE_EXCEL,
                "r"
            ) as archivio:

                files_media = [
                    nome
                    for nome in archivio.namelist()
                    if nome.startswith("xl/media/")
                    and not nome.endswith("/")
                ]


                for indice, nome in enumerate(
                    files_media,
                    start=1
                ):

                    estensione = (
                        Path(nome)
                        .suffix
                        .lower()
                    )

                    if not estensione:
                        estensione = ".bin"


                    nome_file = (
                        f"immagine_{indice:03d}"
                        f"{estensione}"
                    )

                    destinazione = (
                        CARTELLA_IMMAGINI /
                        nome_file
                    )


                    with archivio.open(nome) as sorgente:

                        with open(
                            destinazione,
                            "wb"
                        ) as destinazione_file:

                            shutil.copyfileobj(
                                sorgente,
                                destinazione_file
                            )


                    immagini.append(
                        destinazione
                    )


        except Exception as e:

            st.error(
                "❌ Errore durante "
                "l'estrazione delle immagini."
            )

            st.code(str(e))

            return []


        return immagini


    immagini = estrai_immagini()


    # ======================================================
    # LETTURA FOGLI EXCEL
    # ======================================================

    @st.cache_data
    def carica_fogli():

        try:

            excel = pd.ExcelFile(
                FILE_EXCEL,
                engine="openpyxl"
            )

            return excel.sheet_names

        except Exception as e:

            return []


    fogli = carica_fogli()


    # ======================================================
    # INFORMAZIONI
    # ======================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📚 Fogli Excel",
            len(fogli)
        )

    with col2:

        st.metric(
            "🖼️ Immagini",
            len(immagini)
        )

    with col3:

        st.metric(
            "📁 File",
            "ATTIVITA' CARRELLO"
        )


    st.divider()


    # ======================================================
    # SELEZIONE FOGLIO
    # ======================================================

    if not fogli:

        st.error(
            "❌ Nessun foglio trovato nel file Excel."
        )

        return


    # ======================================================
    # CATEGORIE PRINCIPALI
    # ======================================================

    categorie = {

        "🛞 SENSORI SPM":
            [
                "SENSORI SPM"
            ],

        "🚆 CARRELLI":
            [
                "DM1-CARR.1",
                "DM1-CARR.2",
                "M3-CARR.1",
                "M3-CARR.2",
                "M6-CARR.1",
                "M6-CARR.2",
                "DM8-CARR.1",
                "DM8-CARR.2"
            ],

        "🌡️ PT100":
            [
                "PT100 RIDUTTORI"
            ],

        "🔌 FUSE LOOP":
            [
                "FUSE LOOP CASSA MOTOR",
                "FUSE LOOP TRENO COMPLETO"
            ],

        "🔄 DNRA":
            [
                "LOOP DNRA",
                "OVERVIEW DNRA"
            ],

        "🚄 STATO TRENO":
            [
                "STATO TRENO"
            ],

        "📋 DATI":
            [
                "DATA1",
                "DATA",
                "Italian"
            ]
    }


    # ======================================================
    # COSTRUZIONE LISTA
    # ======================================================

    categorie_presenti = {}

    for categoria, lista in categorie.items():

        presenti = [
            foglio
            for foglio in lista
            if foglio in fogli
        ]

        if presenti:

            categorie_presenti[
                categoria
            ] = presenti


    # ======================================================
    # SELEZIONE CATEGORIA
    # ======================================================

    categoria = st.selectbox(
        "🔧 Seleziona sezione",
        list(categorie_presenti.keys()),
        key="carrelli_categoria"
    )


    # ======================================================
    # SELEZIONE FOGLIO
    # ======================================================

    fogli_categoria = categorie_presenti[
        categoria
    ]


    foglio = st.selectbox(
        "📄 Seleziona elemento",
        fogli_categoria,
        key="carrelli_foglio"
    )


    st.divider()


    # ======================================================
    # MOSTRA FOGLIO
    # ======================================================

    st.markdown(
        f"""
        <div class="box-carrelli">
            <h3>📄 {foglio}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ======================================================
    # LETTURA DATI DEL FOGLIO
    # ======================================================

    try:

        df = pd.read_excel(
            FILE_EXCEL,
            sheet_name=foglio,
            engine="openpyxl",
            header=None
        )

        df = df.dropna(
            axis=0,
            how="all"
        )

        df = df.dropna(
            axis=1,
            how="all"
        )


    except Exception as e:

        st.error(
            "❌ Errore lettura foglio."
        )

        st.code(str(e))

        df = pd.DataFrame()


    # ======================================================
    # RICERCA
    # ======================================================

    if not df.empty:

        ricerca = st.text_input(
            "🔎 Cerca nel foglio",
            placeholder=(
                "Inserisci codice, sensore, "
                "descrizione..."
            ),
            key=f"ricerca_{foglio}"
        )


        if ricerca:

            testo = (
                df
                .astype(str)
                .apply(
                    lambda col:
                    col.str.contains(
                        ricerca,
                        case=False,
                        na=False
                    )
                )
                .any(axis=1)
            )

            df_visualizza = df[
                testo
            ]

        else:

            df_visualizza = df


        st.markdown(
            f"**Righe trovate: {len(df_visualizza)}**"
        )


        # ==================================================
        # TABELLA
        # ==================================================

        st.dataframe(
            df_visualizza,
            use_container_width=True,
            hide_index=True,
            height=400
        )


    else:

        st.info(
            "Questo foglio non contiene dati "
            "tabellari visualizzabili."
        )


    # ======================================================
    # IMMAGINI
    # ======================================================

    if immagini:

        st.divider()

        st.subheader(
            "🖼️ Immagini presenti nel file Excel"
        )

        st.caption(
            "Le immagini vengono mostrate "
            "direttamente dagli elementi incorporati "
            "nel file ATTIVITA' CARRELLO.xlsm."
        )


        # ==================================================
        # FILTRA IMMAGINI VISUALIZZABILI
        # ==================================================

        immagini_visualizzabili = [

            img

            for img in immagini

            if img.suffix.lower()
            in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".bmp",
                ".webp"
            ]
        ]


        if immagini_visualizzabili:

            # ==============================================
            # GRIGLIA
            # ==============================================

            colonne = st.columns(3)


            for indice, immagine in enumerate(
                immagini_visualizzabili
            ):

                colonna = colonne[
                    indice % 3
                ]


                with colonna:

                    with st.container(
                        border=True
                    ):

                        st.caption(
                            immagine.name
                        )

                        st.image(
                            str(immagine),
                            use_container_width=True
                        )


        else:

            st.warning(
                "Le immagini presenti sono in "
                "formato non direttamente visualizzabile "
                "da Streamlit."
            )

            st.write(
                [
                    img.name
                    for img in immagini
                ]
            )


    # ======================================================
    # DEBUG FOGLI
    # ======================================================

    with st.expander(
        "🔍 Visualizza tutti i fogli del file"
    ):

        for i, nome in enumerate(
            fogli,
            start=1
        ):

            st.write(
                f"{i}. {nome}"
            )