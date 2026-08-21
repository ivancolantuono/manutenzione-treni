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

    from datetime import datetime
    from zoneinfo import ZoneInfo

    # ==========================================
    # FUNZIONI
    # ==========================================

    def ora_italia():
        return datetime.now(
            ZoneInfo("Europe/Rome")
        ).isoformat()

    @st.cache_data(ttl=5)
    def carica_consegne():

        res = (
            supabase
            .table("passaggi_consegne")
            .select("*")
            .order("treno")
            .execute()
        )

        return res.data or []

    def salva_consegna(
        tipo,
        treno,
        manutenzione,
        servizio,
        binario,
        disp,
        out,
        lavorazioni,
        odl
    ):

        supabase.table("passaggi_consegne").insert({

            "tipo": tipo,
            "treno": treno,
            "manutenzione": manutenzione,
            "servizio": servizio,
            "binario": binario,
            "disp": disp,
            "out": out,
            "lavorazioni": lavorazioni,
            "odl_padre": odl,
            "utente": st.session_state.get(
                "utente",
                "Sconosciuto"
            ),
            "data_creazione": ora_italia()

        }).execute()

        carica_consegne.clear()

    # ==========================================
    # TITOLO
    # ==========================================

    st.title("🔄 Passaggio Consegne")

    st.caption(
        f"📅 {datetime.now(ZoneInfo('Europe/Rome')).strftime('%d/%m/%Y %H:%M')}"
    )

    # ==========================================
    # NUOVO PASSAGGIO
    # ==========================================

    with st.expander("➕ Aggiungi treno", expanded=False):

        tipo = st.radio(
            "Tipo",
            [
                "TRENO IN USCITA",
                "MANUTENZIONE / LAVORAZIONE APERTA"
            ],
            horizontal=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            treno = st.text_input(
                "🚆 Treno",
                placeholder="es. 1000/27"
            )

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="es. MC"
            )

        with col2:

            if tipo == "TRENO IN USCITA":

                servizio = st.text_input(
                    "🚉 Servizio",
                    placeholder="es. 89705"
                )

            else:

                servizio = ""

            binario = st.text_input(
                "🛤️ Binario",
                placeholder="es. MAV 9"
            )

        with col3:

            disp = st.checkbox(
                "DISP"
            )

            out = st.checkbox(
                "OUT"
            )

            odl = st.text_input(
                "🔢 N° ODL PADRE"
            )

        lavorazioni = st.text_area(
            "📝 Lavorazioni aperte / Note",
            placeholder=(
                "Inserire lavorazioni, anomalie, "
                "attività da monitorare..."
            )
        )

        if st.button(
            "💾 Inserisci",
            type="primary",
            use_container_width=True
        ):

            if not treno:

                st.error(
                    "Inserire il numero del treno."
                )

            else:

                salva_consegna(
                    "USCITA"
                    if tipo == "TRENO IN USCITA"
                    else "MANUTENZIONE",
                    treno,
                    manutenzione,
                    servizio,
                    binario,
                    disp,
                    out,
                    lavorazioni,
                    odl
                )

                st.success(
                    "✅ Passaggio inserito"
                )

                st.rerun()

    st.divider()

    # ==========================================
    # CARICAMENTO DATI
    # ==========================================

    dati = carica_consegne()

    # ==========================================
    # TRENI IN USCITA
    # ==========================================

    st.markdown(
        """
        <div style="
            background:#b7d3ec;
            padding:10px;
            text-align:center;
            font-size:20px;
            font-weight:bold;
            border-radius:6px;
        ">
        🚆 TRENI IN USCITA
        </div>
        """,
        unsafe_allow_html=True
    )

    uscita = [
        x for x in dati
        if x.get("tipo") == "USCITA"
    ]

    if uscita:

        uscita = sorted(
            uscita,
            key=lambda x: (
                str(x.get("treno", ""))
            )
        )

        for item in uscita:

            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(
                [1.1, 1.5, 1.2, 1.2, 0.6, 0.6, 3.5, 1.5]
            )

            col1.write(f"**{item.get('treno','')}**")
            col2.write(item.get("manutenzione", ""))
            col3.write(item.get("servizio", ""))
            col4.write(item.get("binario", ""))

            col5.write(
                "❌" if item.get("disp") else ""
            )

            col6.write(
                "❌" if item.get("out") else ""
            )

            col7.write(
                item.get("lavorazioni", "")
            )

            odl = item.get("odl_padre", "")

            if odl:

                col8.markdown(
                    f"**{odl}**"
                )

            else:

                col8.write("")

            st.divider()

    else:

        st.info(
            "Nessun treno in uscita."
        )

    # ==========================================
    # MANUTENZIONE
    # ==========================================

    st.markdown(
        """
        <div style="
            background:#b7d3ec;
            padding:10px;
            text-align:center;
            font-size:20px;
            font-weight:bold;
            border-radius:6px;
            margin-top:20px;
        ">
        🛠️ MANUTENZIONE / LAVORAZIONI APERTE
        </div>
        """,
        unsafe_allow_html=True
    )

    manutenzione = [
        x for x in dati
        if x.get("tipo") == "MANUTENZIONE"
    ]

    if manutenzione:

        manutenzione = sorted(
            manutenzione,
            key=lambda x: str(
                x.get("treno", "")
            )
        )

        for item in manutenzione:

            col1, col2, col3, col4, col5, col6 = st.columns(
                [1.1, 1.5, 1.2, 0.6, 4, 1.5]
            )

            col1.write(
                f"**{item.get('treno','')}**"
            )

            col2.write(
                item.get("manutenzione", "")
            )

            col3.write(
                item.get("binario", "")
            )

            col4.write(
                "❌" if item.get("disp") else ""
            )

            col5.write(
                item.get("lavorazioni", "")
            )

            odl = item.get("odl_padre", "")

            if odl:

                col6.markdown(
                    f"**{odl}**"
                )

            else:

                col6.write("")

            st.divider()

    else:

        st.info(
            "Nessuna lavorazione aperta."
        )
