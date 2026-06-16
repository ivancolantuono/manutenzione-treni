import streamlit as st
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
from db import supabase, get_operatori
from streamlit_autorefresh import st_autorefresh


def pagina_permessi(supabase, utente):
    st_autorefresh(interval=10000, key="auto_refresh_permessi")

    # LETTURA OPERATORE
    operatore = supabase.table(
        "operatori"
    ).select("*").eq(
        "Nominativo",
        utente
    ).execute()

    squadra = ""
    ruolo = ""

    if operatore.data:
        squadra = operatore.data[0].get("Squadra", "")
        ruolo = operatore.data[0].get("ruolo", "")

    st.title("🏖️ Ferie e Permessi")

    # =====================
    # NUOVA RICHIESTA
    # =====================

    st.subheader("📝 Nuova richiesta")

    tipo = st.selectbox(
        "Tipo richiesta",
        ["Ferie", "ROL", "Permesso", "Recupero"]
    )

    data_inizio = st.date_input("📅 Data inizio")
    data_fine = st.date_input("📅 Data fine")

    ora_inizio = st.time_input("🕒 Ora inizio")
    ora_fine = st.time_input("🕒 Ora fine")

    note = st.text_area(
        "📌 Note",
        key="note_permesso"
    )

    if st.button("📨 Invia richiesta"):

        supabase.table(
            "richieste_permessi"
        ).insert({

            "utente": utente,
            "squadra": squadra,
            "tipo": tipo,

            "data_inizio": str(data_inizio),
            "data_fine": str(data_fine),

            "ora_inizio": str(ora_inizio),
            "ora_fine": str(ora_fine),

            "note": note,

            "stato": "IN ATTESA",

            "data_richiesta":
            datetime.now(
                ZoneInfo("Europe/Rome")
            ).isoformat()

        }).execute()

        st.success("✅ Richiesta inviata")

        st.session_state.pop("note_permesso", None)

        st.rerun()
        
    st.divider()

    # =====================
    # LE MIE RICHIESTE
    # =====================
    
    st.divider()
    
    st.subheader("📋 Le mie richieste")
    
    mie = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "utente",
        utente
    ).order(
        "id",
        desc=True
    ).execute().data
    
    if not mie:
        st.info("Nessuna richiesta presente")
    
    for r in mie:
    
        stato = r.get("stato", "IN ATTESA")
    
        icona = "🟡"
    
        if stato == "APPROVATO":
            icona = "🟢"
    
        elif stato == "RIFIUTATO":
            icona = "🔴"
    
        with st.expander(
            f"{icona} {r['tipo']} - {stato}"
        ):
    
            st.write(f"📅 Dal: {r['data_inizio']}")
            st.write(f"📅 Al: {r['data_fine']}")
    
            st.write(f"🕒 Dalle: {r['ora_inizio']}")
            st.write(f"🕒 Alle: {r['ora_fine']}")
    
            st.write(f"📝 Note: {r.get('note','')}")
    
            if r.get("approvato_da"):
                st.write(
                    f"👤 Gestita da: {r['approvato_da']}"
                )
    
            if r.get("data_approvazione"):
                st.write(
                    f"📅 Data approvazione: {r['data_approvazione']}"
                )
    
            if stato == "RIFIUTATO":
    
                st.error(
                    f"❌ Motivo rifiuto: "
                    f"{r.get('motivo_rifiuto','Non specificato')}"
                )
    # =====================
    # APPROVAZIONI
    # =====================

    if ruolo.upper() in [
        "CAPOSQUADRA",
        "Ingegneria"
    ]:

        st.divider()
        st.subheader("✅ Richieste da approvare")

        richieste = supabase.table(
            "richieste_permessi"
        ).select("*").eq(
            "stato",
            "IN ATTESA"
        ).execute().data

        if ruolo.upper() == "Ingegneria":

            richieste = [
                r for r in richieste
                if str(r.get("squadra")) == str(squadra)
            ]
        
        elif ruolo.upper() == "CAPOSQUADRA":
        
            richieste = richieste
            
        for r in richieste:

            with st.expander(
                f"{r['utente']} - {r['tipo']}"
            ):

                st.write("👥 Squadra:", r["squadra"])
                st.write("📅 Dal:", r["data_inizio"])
                st.write("📅 Al:", r["data_fine"])
                st.write("🕒 Dalle:", r["ora_inizio"])
                st.write("🕒 Alle:", r["ora_fine"])
                st.write("📌 Note:", r["note"])

                motivo = st.text_input(
                    "Motivo rifiuto",
                    key=f"motivo_{r['id']}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approva",
                        key=f"ok_{r['id']}"
                    ):

                        supabase.table(
                            "richieste_permessi"
                        ).update({

                            "stato": "APPROVATO",
                            "approvato_da": utente,
                            "data_approvazione":
                            datetime.now(
                                ZoneInfo("Europe/Rome")
                            ).isoformat()

                        }).eq(
                            "id",
                            r["id"]
                        ).execute()

                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Rifiuta",
                        key=f"ko_{r['id']}"
                    ):

                        supabase.table(
                            "richieste_permessi"
                        ).update({

                            "stato": "RIFIUTATO",
                            "approvato_da": utente,
                            "motivo_rifiuto": motivo,
                            "data_approvazione":
                            datetime.now(
                                ZoneInfo("Europe/Rome")
                            ).isoformat()

                        }).eq(
                            "id",
                            r["id"]
                        ).execute()

                        st.rerun()
                        
    # =====================
    # APPROVATE
    # =====================
    
    st.divider()
    st.subheader("🟢 Richieste approvate")
    
    approvate = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "stato",
        "APPROVATO"
    ).order(
        "id",
        desc=True
    ).execute().data
    
    if ruolo.upper() == "CAPOSQUADRA":
    
        approvate = [
            r for r in approvate
            if str(r.get("squadra")) == str(squadra)
        ]
    
    for r in approvate:
    
        with st.expander(
            f"🟢 {r['utente']} - {r['tipo']}"
        ):
    
            st.write(f"👥 Squadra: {r['squadra']}")
            st.write(f"📅 Dal: {r['data_inizio']}")
            st.write(f"📅 Al: {r['data_fine']}")
            st.write(f"👤 Approvato da: {r.get('approvato_da','-')}")
    
    # =====================
    # RIFIUTATE
    # =====================
    
    st.divider()
    st.subheader("🔴 Richieste rifiutate")
    
    rifiutate = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "stato",
        "RIFIUTATO"
    ).order(
        "id",
        desc=True
    ).execute().data
    
    if ruolo.upper() == "CAPOSQUADRA":
    
        rifiutate = [
            r for r in rifiutate
            if str(r.get("squadra")) == str(squadra)
        ]
    
    for r in rifiutate:
    
        with st.expander(
            f"🔴 {r['utente']} - {r['tipo']}"
        ):
    
            st.write(f"👥 Squadra: {r['squadra']}")
            st.write(f"📅 Dal: {r['data_inizio']}")
            st.write(f"📅 Al: {r['data_fine']}")
            st.write(
                f"👤 Gestita da: {r.get('approvato_da','-')}"
            )
    
            st.error(
                f"Motivo: "
                f"{r.get('motivo_rifiuto','Non specificato')}"
            )
                            
        