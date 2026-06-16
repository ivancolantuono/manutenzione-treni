import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


def pagina_permessi(supabase, utente, squadra):

    st.title("🏖️ Ferie e Permessi")

    # =========================
    # NUOVA RICHIESTA
    # =========================

    st.subheader("➕ Nuova richiesta")

    tipo = st.selectbox(
        "Tipo richiesta",
        ["Ferie", "ROL", "Permesso", "Recupero"]
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
                "data_richiesta": datetime.now(
                    ZoneInfo("Europe/Rome")
                ).isoformat()
            }).execute()

            st.success("✅ Richiesta inviata")
            st.rerun()

        except Exception as e:
            st.error(f"Errore Supabase: {e}")

    st.divider()

    # =========================
    # LE MIE RICHIESTE
    # =========================

    st.subheader("📋 Le mie richieste")

    mie_richieste = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "utente",
        utente
    ).order(
        "id",
        desc=True
    ).execute().data

    if not mie_richieste:
        st.info("Nessuna richiesta presente")

    for r in mie_richieste:

        with st.expander(
            f"{r['tipo']} - {r['stato']}"
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
                    f"👤 Gestita da: {r['approvato_da']}"
                )

    st.divider()

    # =========================
    # APPROVAZIONE CAPOSQUADRA
    # =========================

    st.subheader("👨‍✈️ Richieste della squadra")

    richieste = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "squadra",
        squadra
    ).eq(
        "stato",
        "IN ATTESA"
    ).order(
        "id",
        desc=True
    ).execute().data

    if not richieste:
        st.info("Nessuna richiesta da approvare")

    for r in richieste:

        if r["utente"] == utente:
            continue

        with st.expander(
            f"👤 {r['utente']} - {r['tipo']}"
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
                        "data_approvazione": datetime.now(
                            ZoneInfo("Europe/Rome")
                        ).isoformat()
                    }).eq(
                        "id",
                        r["id"]
                    ).execute()

                    st.success("Richiesta approvata")
                    st.rerun()

            with col2:

                motivo = st.text_input(
                    "Motivo rifiuto",
                    key=f"motivo_{r['id']}"
                )

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
                        "data_approvazione": datetime.now(
                            ZoneInfo("Europe/Rome")
                        ).isoformat()
                    }).eq(
                        "id",
                        r["id"]
                    ).execute()

                    st.warning("Richiesta rifiutata")
                    st.rerun()
