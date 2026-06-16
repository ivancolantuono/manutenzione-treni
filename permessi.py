import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

def pagina_permessi(supabase, utente, squadra):

    st.title("🏖️ Ferie e Permessi")

    # ==================================
    # NUOVA RICHIESTA
    # ==================================

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
        
        except Exception as e:
            st.error(str(e))
                st.success("✅ Richiesta inviata")
                st.rerun()

    st.divider()

    # ==================================
    # LE MIE RICHIESTE
    # ==================================

    st.subheader("📋 Le mie richieste")

    mie = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "utente",
        utente
    ).execute().data

    for r in mie:

        with st.expander(
            f"{r['tipo']} - {r['stato']}"
        ):

            st.write(
                f"📅 {r['data_inizio']} → {r['data_fine']}"
            )

            st.write(
                f"🕒 {r.get('ora_inizio','-')} → {r.get('ora_fine','-')}"
            )

            st.write(
                f"📝 {r.get('note','')}"
            )

    st.divider()

    # ==================================
    # APPROVAZIONI CAPOSQUADRA
    # ==================================

    st.subheader("👨‍✈️ Richieste squadra")

    richieste = supabase.table(
        "richieste_permessi"
    ).select("*").eq(
        "squadra",
        squadra
    ).eq(
        "stato",
        "IN ATTESA"
    ).execute().data

    if not richieste:
        st.info("Nessuna richiesta in attesa")

    for r in richieste:

        with st.expander(
            f"👤 {r['utente']} - {r['tipo']}"
        ):

            st.write(
                f"📅 {r['data_inizio']} → {r['data_fine']}"
            )

            st.write(
                f"🕒 {r.get('ora_inizio','-')} → {r.get('ora_fine','-')}"
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
                    key=f"no_{r['id']}"
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
