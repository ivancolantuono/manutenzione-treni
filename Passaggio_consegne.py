import streamlit as st
import pandas as pd
import requests
from streamlit_pdf_viewer import pdf_viewer
import os
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from zoneinfo import ZoneInfo
from permessi import pagina_permessi
from datetime import date, datetime
from db import supabase
from planning import planning_page
from open import openitem_page
from db import get_utenti
from db import get_operatori
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
import urllib.parse

def passaggio_consegne_page():

    st.title("🔄 Passaggio Consegne")

    # ============================================================
    # DATA / TURNO
    # ============================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        data_consegna = st.date_input(
            "📅 Data",
            value=datetime.now().date()
        )

    with col2:
        turno = st.selectbox(
            "🕐 Turno",
            ["Mattina", "Pomeriggio", "Notte"]
        )

    with col3:
        responsabile = st.session_state.get(
            "utente",
            "Sconosciuto"
        )

        st.text_input(
            "👤 Responsabile",
            value=responsabile,
            disabled=True
        )

    st.divider()

    # ============================================================
    # AGGIUNGI TRENO
    # ============================================================

    with st.expander("➕ Aggiungi treno", expanded=True):

        tipo = st.radio(
            "Tipo",
            [
                "🚆 TRENO IN USCITA",
                "🔧 MANUTENZIONE / LAVORAZIONE APERTA"
            ],
            horizontal=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            treno = st.text_input(
                "🚆 Treno",
                placeholder="Es. 1000/27"
            )

        with col2:

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="Es. MC"
            )

        with col3:

            binario = st.text_input(
                "🛤️ Binario",
                placeholder="Es. MAV 9"
            )

        col1, col2, col3 = st.columns(3)

        with col1:

            disp = st.checkbox(
                "🟢 DISP"
            )

        with col2:

            out = st.checkbox(
                "🔴 OUT"
            )

        with col3:

            odl = st.text_input(
                "📄 N° ODL PADRE",
                placeholder="Es. 100014925813"
            )

        note = st.text_area(
            "📝 Lavorazioni aperte / Note",
            placeholder=(
                "Inserire lavorazioni, anomalie, "
                "attività da monitorare..."
            )
        )

        if st.button(
            "➕ Inserisci",
            type="primary",
            use_container_width=True
        ):

            if not treno:

                st.error(
                    "Inserisci il numero del treno."
                )

                st.stop()

            if "passaggio_consegne" not in st.session_state:

                st.session_state.passaggio_consegne = []

            st.session_state.passaggio_consegne.append({

                "tipo": tipo,

                "treno": treno,

                "manutenzione": manutenzione,

                "binario": binario,

                "disp": disp,

                "out": out,

                "odl": odl,

                "note": note

            })

            st.success(
                "✅ Treno inserito"
            )

            st.rerun()

    # ============================================================
    # INIZIALIZZAZIONE
    # ============================================================

    if "passaggio_consegne" not in st.session_state:

        st.session_state.passaggio_consegne = []

    dati = st.session_state.passaggio_consegne

    treni_uscita = [
        x for x in dati
        if x["tipo"] == "🚆 TRENO IN USCITA"
    ]

    manutenzioni = [
        x for x in dati
        if x["tipo"] == "🔧 MANUTENZIONE / LAVORAZIONE APERTA"
    ]

    # ============================================================
    # FUNZIONE PALLINO DISP
    # ============================================================

    def pallino_disp(disponibile):

        if disponibile:

            return """
            <div style="
                text-align:center;
                color:#20a446;
                font-size:24px;
                line-height:20px;
            ">●</div>
            """

        else:

            return """
            <div style="
                text-align:center;
                color:#d9534f;
                font-size:24px;
                line-height:20px;
            ">●</div>
            """

    # ============================================================
    # FUNZIONE PALLINO OUT
    # ============================================================

    def pallino_out(is_out):

        if is_out:

            return """
            <div style="
                text-align:center;
                color:#d9534f;
                font-size:24px;
                line-height:20px;
            ">●</div>
            """

        return ""

    # ============================================================
    # INTESTAZIONE TRENI IN USCITA
    # ============================================================

    def mostra_intestazione_uscita():

        cols = st.columns(
            [
                1.2,
                1.6,
                1.2,
                1.2,
                0.7,
                0.7,
                3.2,
                1.6
            ]
        )

        intestazioni = [

            "🚆 TRENO",

            "🔧 MANUTENZIONE",

            "📡 SERVIZIO",

            "🛤️ BINARIO",

            "DISP",

            "OUT",

            "📝 LAVORAZIONI APERTE / NOTE",

            "📄 N° ODL PADRE"

        ]

        for col, titolo in zip(
            cols,
            intestazioni
        ):

            with col:

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-weight:700;
                        font-size:13px;
                    ">
                    {titolo}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ============================================================
    # INTESTAZIONE MANUTENZIONE
    # ============================================================

    def mostra_intestazione_manutenzione():

        cols = st.columns(
            [
                1.2,
                1.8,
                1.3,
                0.8,
                3.8,
                1.6
            ]
        )

        intestazioni = [

            "🚆 TRENO",

            "🔧 MANUTENZIONE",

            "🛤️ BINARIO",

            "DISP",

            "📝 LAVORAZIONI APERTE / NOTE",

            "📄 N° ODL PADRE"

        ]

        for col, titolo in zip(
            cols,
            intestazioni
        ):

            with col:

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-weight:700;
                        font-size:13px;
                    ">
                    {titolo}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ============================================================
    # 🚆 TRENI IN USCITA
    # ============================================================

    st.markdown(
        """
        <div style="
            background:#b7d7f0;
            padding:10px;
            border-radius:5px;
            text-align:center;
            font-weight:700;
            font-size:18px;
            margin-top:15px;
        ">
        🚆 TRENI IN USCITA
        </div>
        """,
        unsafe_allow_html=True
    )

    if treni_uscita:

        # --------------------------------------------
        # INTESTAZIONE COLONNE
        # --------------------------------------------

        with st.container(border=True):

            mostra_intestazione_uscita()

        # --------------------------------------------
        # RIGHE
        # --------------------------------------------

        for i, item in enumerate(
            treni_uscita
        ):

            cols = st.columns(
                [
                    1.2,
                    1.6,
                    1.2,
                    1.2,
                    0.7,
                    0.7,
                    3.2,
                    1.6
                ]
            )

            # TRENO

            cols[0].write(
                f"**{item['treno']}**"
            )

            # MANUTENZIONE

            cols[1].write(
                item["manutenzione"]
                if item["manutenzione"]
                else "-"
            )

            # SERVIZIO

            cols[2].write(
                item.get(
                    "servizio",
                    "-"
                )
            )

            # BINARIO

            cols[3].write(
                item["binario"]
                if item["binario"]
                else "-"
            )

            # DISP

            cols[4].markdown(
                pallino_disp(
                    item["disp"]
                ),
                unsafe_allow_html=True
            )

            # OUT

            cols[5].markdown(
                pallino_out(
                    item["out"]
                ),
                unsafe_allow_html=True
            )

            # NOTE

            cols[6].write(
                item["note"]
                if item["note"]
                else "-"
            )

            # ODL

            if item["odl"]:

                cols[7].markdown(
                    f"[🔗 {item['odl']}](#)"
                )

            else:

                cols[7].write("-")

    else:

        st.info(
            "Nessun treno in uscita."
        )

    # ============================================================
    # 🔧 MANUTENZIONE / LAVORAZIONI APERTE
    # ============================================================

    st.markdown(
        """
        <div style="
            background:#b7d7f0;
            padding:10px;
            border-radius:5px;
            text-align:center;
            font-weight:700;
            font-size:18px;
            margin-top:20px;
        ">
        🔧 MANUTENZIONE / LAVORAZIONI APERTE
        </div>
        """,
        unsafe_allow_html=True
    )

    if manutenzioni:

        # --------------------------------------------
        # INTESTAZIONE COLONNE
        # --------------------------------------------

        with st.container(border=True):

            mostra_intestazione_manutenzione()

        # --------------------------------------------
        # RIGHE
        # --------------------------------------------

        for i, item in enumerate(
            manutenzioni
        ):

            cols = st.columns(
                [
                    1.2,
                    1.8,
                    1.3,
                    0.8,
                    3.8,
                    1.6
                ]
            )

            # TRENO

            cols[0].write(
                f"**{item['treno']}**"
            )

            # MANUTENZIONE

            cols[1].write(
                item["manutenzione"]
                if item["manutenzione"]
                else "-"
            )

            # BINARIO

            cols[2].write(
                item["binario"]
                if item["binario"]
                else "-"
            )

            # DISP

            cols[3].markdown(
                pallino_disp(
                    item["disp"]
                ),
                unsafe_allow_html=True
            )

            # NOTE

            cols[4].write(
                item["note"]
                if item["note"]
                else "-"
            )

            # ODL

            if item["odl"]:

                cols[5].markdown(
                    f"[🔗 {item['odl']}](#)"
                )

            else:

                cols[5].write("-")

    else:

        st.info(
            "Nessuna manutenzione o lavorazione aperta."
        )

    # ============================================================
    # RIEPILOGO
    # ============================================================

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            f"📅 **Data consegna:** "
            f"{data_consegna.strftime('%d/%m/%Y')}"
        )

    with col2:

        st.write(
            f"🕐 **Turno:** {turno}"
        )

    with col3:

        st.write(
            f"👤 **Responsabile:** {responsabile}"
        )
