import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

def pagina_permessi(supabase, utente):

    ruolo = st.session_state.get("ruolo", "")
    squadra = st.session_state.get("squadra", "")

    st.title("🏖️ Ferie e Permessi")

    # ====================================
    # NUOVA RICHIESTA
    # ====================================

    st.subheader("📝 Nuova richiesta")

    tipo = st.selectbox(
        "Tipo richiesta",
        ["Ferie", "ROL", "Permesso", "Recupero"]
    )

    data_inizio = st.date_input("📅 Data inizio")
    data_fine = st.date_input("📅 Data fine")

    ora_inizio = st.time_input("🕒 Ora inizio")
    ora_fine = st.time_input("🕒 Ora fine")

    note = st.text_area("📌 Note")

    if st.button("📨 Invia richiesta"):

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
            "data_richiesta": datetime.now(
                ZoneInfo("Europe/Rome")
            ).isoformat()
        }).execute()

        st.success("✅ Richiesta inviata")
        st.rerun()

    st.divider()

    # ====================================
    # MIE RICHIESTE
    # ====================================

    st.subheader("📋 Le mie richieste")

    mie = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "utente",
        utente
    ).execute().data

    for r in mie:

        colore = {
            "IN ATTESA": "🟡",
            "APPROVATO": "🟢",
            "RIFIUTATO": "🔴"
        }.get(r["stato"], "⚪")

        with st.expander(
            f"{colore} {r['tipo']} - {r['stato']}"
        ):

            st.write(f"📅 Dal: {r['data_inizio']}")
            st.write(f"📅 Al: {r['data_fine']}")
            st.write(f"🕒 Dalle: {r['ora_inizio']}")
            st.write(f"🕒 Alle: {r['ora_fine']}")
            st.write(f"📌 Note: {r.get('note','')}")

            if r.get("approvato_da"):
                st.write(
                    f"👤 Approvato da: {r['approvato_da']}"
                )

    st.divider()

    # ====================================
    # APPROVAZIONI
    # ====================================

    if ruolo in ["Caposquadra", "Ingegneria"]:

        st.subheader("✅ Richieste da approvare")

        richieste = supabase.table(
            "richieste_permessi"
        ).select("*").eq(
            "stato",
            "IN ATTESA"
        ).execute().data

        if ruolo == "Caposquadra":

            richieste = [
                r for r in richieste
                if str(r.get("squadra")) == str(squadra)
            ]

        if not richieste:
            st.info("Nessuna richiesta da approvare")

        for r in richieste:

            with st.expander(
                f"👤 {r['utente']} - {r['tipo']}"
            ):

                st.write(f"👥 Squadra: {r['squadra']}")
                st.write(f"📅 Dal: {r['data_inizio']}")
                st.write(f"📅 Al: {r['data_fine']}")
                st.write(f"🕒 Dalle: {r['ora_inizio']}")
                st.write(f"🕒 Alle: {r['ora_fine']}")
                st.write(f"📌 Note: {r.get('note','')}")

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approva",
                        key=f"app_{r['id']}"
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
                        key=f"rif_{r['id']}"
                    ):

                        supabase.table(
                            "richieste_permessi"
                        ).update({
                            "stato": "RIFIUTATO",
                            "approvato_da": utente,
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
