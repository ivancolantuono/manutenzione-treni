import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


def pagina_permessi(supabase, utente, squadra):

    ruolo = st.session_state.get("ruolo", "").upper()

    st.title("🏖️ Ferie e Permessi")
    
    # ==================================
    # NUOVA RICHIESTA
    # ==================================
    
    st.subheader("➕ Nuova richiesta")
    
    tipo = st.selectbox(
        "Tipo richiesta",
        [
            "FERIE",
            "ROL",
            "PERMESSO",
            "RECUPERO"
        ]
    )
    
    data_inizio = st.date_input("📅 Data inizio")
    data_fine = st.date_input("📅 Data fine")
    
    ora_inizio = st.time_input("🕒 Ora inizio")
    ora_fine = st.time_input("🕒 Ora fine")
    
    note = st.text_area("📝 Note")
    
    if st.button("📨 Invia richiesta"):
    
        try:
    
            supabase.table("richieste_permessi").insert({
    
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
            st.rerun()
    
        except Exception as e:
    
            st.error(str(e))
    
    # ==================================
    # LE MIE RICHIESTE
    # ==================================
    
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
    
        stato = r.get("stato", "")
    
        if stato == "APPROVATO":
            colore = "🟢"
        elif stato == "RIFIUTATO":
            colore = "🔴"
        else:
            colore = "🟡"
    
        with st.expander(
            f"{colore} {r['tipo']} - {stato}"
        ):
    
            st.write(
                f"📅 Dal {r['data_inizio']} al {r['data_fine']}"
            )
    
            st.write(
                f"🕒 {r.get('ora_inizio','')} - {r.get('ora_fine','')}"
            )
    
            st.write(
                f"📝 {r.get('note','')}"
            )
    
            if r.get("approvato_da"):
                st.write(
                    f"👤 Approvato da: {r['approvato_da']}"
                )
    
            if r.get("motivo_rifiuto"):
                st.write(
                    f"❌ Motivo rifiuto: {r['motivo_rifiuto']}"
                )
    
    # ==================================
    # APPROVAZIONI
    # ==================================
    
    if ruolo in ["CAPOSQUADRA", "INGEGNERIA"]:
    
        st.divider()
    
        st.subheader("✅ Richieste da approvare")
    
        if ruolo == "CAPOSQUADRA":
    
            richieste = supabase.table(
                "richieste_permessi"
            ).select("*").eq(
                "squadra",
                squadra
            ).eq(
                "stato",
                "IN ATTESA"
            ).execute().data
    
        else:
    
            richieste = supabase.table(
                "richieste_permessi"
            ).select("*").eq(
                "stato",
                "IN ATTESA"
            ).execute().data
    
        if not richieste:
            st.info("Nessuna richiesta da approvare")
    
        for r in richieste:
    
            if r["utente"] == utente:
                continue
    
            with st.expander(
                f"👤 {r['utente']} | {r['tipo']}"
            ):
    
                st.write(f"👥 Squadra: {r['squadra']}")
    
                st.write(
                    f"📅 Dal {r['data_inizio']} al {r['data_fine']}"
                )
    
                st.write(
                    f"🕒 {r.get('ora_inizio','')} - {r.get('ora_fine','')}"
                )
    
                st.write(
                    f"📝 {r.get('note','')}"
                )
    
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
