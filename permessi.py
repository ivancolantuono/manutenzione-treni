import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


def pagina_permessi():

    st.title("🏖️ Ferie e Permessi")

    tipo = st.selectbox(
        "Tipo richiesta",
        ["Ferie", "ROL", "Permesso", "Recupero"]
    )

    data_inizio = st.date_input("Data inizio")
    data_fine = st.date_input("Data fine")

    note = st.text_area("Note")

    if st.button("📨 Invia richiesta"):

        supabase.table("richieste_permessi").insert({
            "utente": utente,
            "squadra": squadra,
            "tipo": tipo,
            "data_inizio": str(data_inizio),
            "data_fine": str(data_fine),
            "note": note,
            "stato": "IN ATTESA",
            "data_richiesta": datetime.now(
                ZoneInfo("Europe/Rome")
            ).isoformat()
        }).execute()

        st.success("Richiesta inviata")
        st.rerun()

    st.divider()

    st.subheader("📋 Le mie richieste")

    richieste = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "utente",
        utente
    ).execute().data

    for r in richieste:

        stato = r.get("stato", "")

        if stato == "IN ATTESA":
            icona = "🟡"
        elif stato == "APPROVATA":
            icona = "🟢"
        else:
            icona = "🔴"

        with st.expander(
            f"{icona} {r['tipo']} - {r['data_inizio']}"
        ):

            st.write(f"📅 Dal: {r['data_inizio']}")
            st.write(f"📅 Al: {r['data_fine']}")
            st.write(f"📝 Note: {r.get('note','')}")
            st.write(f"📌 Stato: {stato}")
