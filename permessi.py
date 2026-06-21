import streamlit as st
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
from db import supabase, get_operatori
from streamlit_autorefresh import st_autorefresh

def formatta_data(data_str):
    try:
        return datetime.strptime(
            str(data_str),
            "%Y-%m-%d"
        ).strftime("%d/%m/%Y")
    except:
        return data_str
        
def pagina_permessi(supabase, utente):

    st_autorefresh(interval=10000, key="auto_refresh_permessi")

    # DATI DAL LOGIN
    ruolo = st.session_state.get("ruolo", "")
    squadra = st.session_state.get("squadra", "")
    
    st.write("UTENTE:", utente)
    st.write("RUOLO:", ruolo)
    st.write("SQUADRA LOGIN:", squadra)

    st.title("🏖️ FERIE E PERMESSI")
    
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
    
            st.write(f"📅 Dal: {formatta_data(r['data_inizio'])}")
            st.write(f"📅 Al: {formatta_data(r['data_fine'])}")
    
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
    
        richieste = [
            r for r in richieste
            if str(r.get("squadra","")).strip().upper()
            == str(squadra).strip().upper()
        ]
    
        if not richieste:
            st.info("Nessuna richiesta in attesa")
    
        for r in richieste:
    
            with st.expander(
                f"{r['utente']} - {r['tipo']}"
            ):
    
                st.write("👥 Squadra:", r["squadra"])
                st.write(f"📅 Dal: {formatta_data(r['data_inizio'])}")
                st.write(f"📅 Al: {formatta_data(r['data_fine'])}")
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
    
                        st.success("Richiesta approvata")
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
    
                        st.warning("Richiesta rifiutata")
                        st.rerun()                        
    # =====================
    # APPROVATE
    # =====================
    
    if ruolo.strip().upper() == "CAPOSQUADRA":
    
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
    
        approvate = [
            r for r in approvate
            if str(r.get("squadra", "")).strip().upper()
            == str(squadra).strip().upper()
        ]
    
        if not approvate:
            st.info("Nessuna richiesta approvata")
    
        for r in approvate:
    
            with st.expander(
                f"🟢 {r['utente']} - {r['tipo']}"
            ):
    
                st.write(f"👥 Squadra: {r.get('squadra','-')}")
                st.write(f"📅 Dal: {r.get('data_inizio','-')}")
                st.write(f"📅 Al: {r.get('data_fine','-')}")
                st.write(f"🕒 Dalle: {r.get('ora_inizio','-')}")
                st.write(f"🕒 Alle: {r.get('ora_fine','-')}")
    
                st.write(
                    f"👤 Approvato da: {r.get('approvato_da','-')}"
                )
    
                st.write(
                    f"📅 Data approvazione: {r.get('data_approvazione','-')}"
                )
    
    
    # =====================
    # RIFIUTATE
    # =====================
    
    if ruolo.strip().upper() == "CAPOSQUADRA":
    
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
    
        rifiutate = [
            r for r in rifiutate
            if str(r.get("squadra", "")).strip().upper()
            == str(squadra).strip().upper()
        ]
    
        if not rifiutate:
            st.info("Nessuna richiesta rifiutata")
    
        for r in rifiutate:
    
            with st.expander(
                f"🔴 {r['utente']} - {r['tipo']}"
            ):
    
                st.write(f"👥 Squadra: {r.get('squadra','-')}")
                st.write(f"📅 Dal: {formatta_data(r['data_inizio'])}")
                st.write(f"📅 Al: {formatta_data(r['data_fine'])}")
                st.write(f"🕒 Dalle: {r.get('ora_inizio','-')}")
                st.write(f"🕒 Alle: {r.get('ora_fine','-')}")
    
                st.write(
                    f"👤 Gestita da: {r.get('approvato_da','-')}"
                )
    
                st.write(
                    f"📅 Data gestione: {r.get('data_approvazione','-')}"
                )
    
                st.error(
                    f"❌ Motivo: {r.get('motivo_rifiuto','Non specificato')}"
                )
