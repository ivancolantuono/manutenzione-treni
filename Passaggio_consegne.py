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

def Passaggio_consegne_page():

    from datetime import date
    from zoneinfo import ZoneInfo

    # ==========================================================
    # FUNZIONI
    # ==========================================================

    def ora_italia():
        return datetime.now(
            ZoneInfo("Europe/Rome")
        ).isoformat()

    @st.cache_data(ttl=5)
    def carica_consegne():
    
        try:
    
            res = (
                supabase
                .table("passaggio_consegne")
                .select("*")
                .execute()
            )
    
            return res.data or []
    
        except Exception as e:
    
            st.error("❌ Errore lettura tabella passaggio_consegne")
            st.code(str(e))
    
            return []

    # ==========================================================
    # TITOLO
    # ==========================================================

    st.title("🔄 Passaggio Consegne")

    # ==========================================================
    # DATA / TURNO / RESPONSABILE
    # ==========================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        data_consegna = st.date_input(
            "📅 Data",
            value=date.today()
        )

    with col2:
        turno = st.selectbox(
            "🕐 Turno",
            [
                "Mattina",
                "Pomeriggio",
                "Notte"
            ]
        )

    with col3:
        responsabile = st.text_input(
            "👤 Responsabile",
            value=st.session_state.get(
                "utente",
                ""
            )
        )

    st.divider()

    # ==========================================================
    # AGGIUNGI TRENO
    # ==========================================================

    with st.expander("➕ Aggiungi treno", expanded=True):

        st.markdown("### Tipo")

        tipo = st.radio(
            "",
            [
                "🚆 TRENO IN USCITA",
                "🛠️ MANUTENZIONE / LAVORAZIONE APERTA"
            ],
            horizontal=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            treno = st.text_input(
                "🚆 Treno",
                placeholder="Es. 1000/27"
            )

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="Es. MC"
            )

        with col2:

            servizio = st.text_input(
                "🚉 Servizio",
                placeholder="Es. 89705"
            )

            binario = st.text_input(
                "🛤️ Binario",
                placeholder="Es. MAV 9"
            )

        with col3:

            odl = st.text_input(
                "📋 N° ODL PADRE",
                placeholder="Es. 100014925813"
            )

            st.write("")

            disp = st.checkbox(
                "🟢 DISP"
            )

            out = st.checkbox(
                "🔴 OUT"
            )

        lavorazioni = st.text_area(
            "📝 Lavorazioni aperte / Note",
            placeholder=(
                "Inserire lavorazioni, anomalie, "
                "attività da monitorare..."
            )
        )

        # ======================================================
        # INSERIMENTO
        # ======================================================

        if st.button(
            "➕ Inserisci",
            type="primary",
            use_container_width=True
        ):

            if not treno.strip():

                st.error(
                    "⚠️ Inserisci il numero del treno."
                )

            elif tipo.startswith("🚆") and not servizio.strip():

                st.error(
                    "⚠️ Per un treno in uscita inserisci il servizio."
                )

            else:

                if tipo.startswith("🚆"):
                    tipo_db = "TRENO IN USCITA"
                else:
                    tipo_db = "MANUTENZIONE / LAVORAZIONE APERTA"

                nuovo = {

                    "data_consegna":
                        str(data_consegna),

                    "turno":
                        turno,

                    "responsabile":
                        responsabile,

                    "tipo":
                        tipo_db,

                    "treno":
                        treno.strip(),

                    "manutenzione":
                        manutenzione.strip(),

                    "servizio":
                        servizio.strip(),

                    "binario":
                        binario.strip(),

                    "disp":
                        disp,

                    "out":
                        out,

                    "lavorazioni":
                        lavorazioni.strip(),

                    "odl":
                        odl.strip(),

                    "created_at":
                        ora_italia()
                }

                supabase \
                    .table("passaggio_consegne") \
                    .insert(nuovo) \
                    .execute()

                carica_consegne.clear()

                st.success(
                    "✅ Treno aggiunto al passaggio consegne."
                )

                st.rerun()

    st.divider()

    # ==========================================================
    # SELEZIONE STORICO
    # ==========================================================

    st.subheader("📚 Storico Passaggi Consegne")

    dati = carica_consegne()

    if not dati:

        st.info(
            "Nessun passaggio di consegne presente."
        )

        return

    # date disponibili
    date_disponibili = sorted(
        list(
            set(
                d["data_consegna"]
                for d in dati
                if d.get("data_consegna")
            )
        ),
        reverse=True
    )

    # ==========================================================
    # SELETTORE DATA
    # ==========================================================

    data_storico = st.selectbox(
        "📅 Visualizza data",
        date_disponibili,
        index=0
    )

    # ==========================================================
    # FILTRA DATA
    # ==========================================================

    dati_giorno = [
        d for d in dati
        if d.get("data_consegna") == data_storico
    ]

    if not dati_giorno:

        st.info(
            "Nessun dato per questa giornata."
        )

        return

    # ==========================================================
    # INFORMAZIONI CONSEGNA
    # ==========================================================

    primo = dati_giorno[0]

    st.caption(
        f"📅 {data_storico}   |   "
        f"👤 Responsabile: {primo.get('responsabile', '-')}"
    )

    # ==========================================================
    # TRENI IN USCITA
    # ==========================================================

    treni_uscita = [
        d for d in dati_giorno
        if d.get("tipo") == "TRENO IN USCITA"
    ]

    st.markdown(
        """
        <div style="
            background-color:#b7d7f0;
            padding:10px;
            text-align:center;
            font-weight:bold;
            border-radius:5px;
            margin-top:15px;
        ">
        🚆 TRENI IN USCITA
        </div>
        """,
        unsafe_allow_html=True
    )

    if not treni_uscita:

        st.info("Nessun treno in uscita.")

    else:

        # intestazione
        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
            [1.2, 1.5, 1.3, 1.3, 0.8, 0.8, 3, 1.5]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**SERVIZIO**")
        h4.markdown("**BINARIO**")
        h5.markdown("**DISP**")
        h6.markdown("**OUT**")
        h7.markdown("**LAVORAZIONI / NOTE**")
        h8.markdown("**N° ODL PADRE**")

        st.divider()

        for item in treni_uscita:

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                [1.2, 1.5, 1.3, 1.3, 0.8, 0.8, 3, 1.5]
            )

            c1.write(
                item.get("treno") or "-"
            )

            c2.write(
                item.get("manutenzione") or "-"
            )

            c3.write(
                item.get("servizio") or "-"
            )

            c4.write(
                item.get("binario") or "-"
            )

            if item.get("disp"):
                c5.markdown("🟢")
            else:
                c5.markdown("⚪")

            if item.get("out"):
                c6.markdown("🔴")
            else:
                c6.markdown("⚪")

            c7.write(
                item.get("lavorazioni") or "-"
            )

            if item.get("odl"):

                c8.markdown(
                    f"[{item['odl']}]"
                )

            else:

                c8.write("-")

    # ==========================================================
    # MANUTENZIONI / LAVORAZIONI APERTE
    # ==========================================================

    manutenzioni = [
        d for d in dati_giorno
        if d.get("tipo")
        == "MANUTENZIONE / LAVORAZIONE APERTA"
    ]

    st.markdown(
        """
        <div style="
            background-color:#b7d7f0;
            padding:10px;
            text-align:center;
            font-weight:bold;
            border-radius:5px;
            margin-top:25px;
        ">
        🛠️ MANUTENZIONE / LAVORAZIONI APERTE
        </div>
        """,
        unsafe_allow_html=True
    )

    if not manutenzioni:

        st.info(
            "Nessuna manutenzione o lavorazione aperta."
        )

    else:

        # ==================================================
        # INTESTAZIONE
        # ==================================================

        h1, h2, h3, h4, h5, h6, h7 = st.columns(
            [1.2, 1.8, 1.5, 0.8, 0.8, 4, 1.5]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**BINARIO**")
        h4.markdown("**DISP**")
        h5.markdown("**OUT**")
        h6.markdown("**LAVORAZIONI APERTE / NOTE**")
        h7.markdown("**N° ODL PADRE**")

        st.divider()

        # ==================================================
        # RIGHE
        # ==================================================

        for item in manutenzioni:

            c1, c2, c3, c4, c5, c6, c7 = st.columns(
                [1.2, 1.8, 1.5, 0.8, 0.8, 4, 1.5]
            )

            c1.write(
                item.get("treno") or "-"
            )

            c2.write(
                item.get("manutenzione") or "-"
            )

            c3.write(
                item.get("binario") or "-"
            )

            # DISP
            if item.get("disp"):

                c4.markdown(
                    "🟢"
                )

            else:

                c4.markdown(
                    "⚪"
                )

            # OUT
            if item.get("out"):

                c5.markdown(
                    "🔴"
                )

            else:

                c5.markdown(
                    "⚪"
                )

            c6.write(
                item.get("lavorazioni") or "-"
            )

            if item.get("odl"):

                c7.markdown(
                    f"[{item['odl']}]"
                )

            else:

                c7.write("-")

            st.divider()

    # ==========================================================
    # TURNO
    # ==========================================================

    turni = sorted(
        set(
            d.get("turno")
            for d in dati_giorno
            if d.get("turno")
        )
    )

    st.caption(
        "🕐 Turni presenti: "
        + ", ".join(turni)
    )
