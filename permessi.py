import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


def pagina_permessi(supabase, utente):

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

    note = st.text_area("📌 Note")

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
        st.rerun()

    st.divider()

    # =====================
    # LE MIE RICHIESTE
    # =====================

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

            st.write("📅 Dal:", r["data_inizio"])
            st.write("📅 Al:", r["data_fine"])
            st.write("🕒 Dalle:", r["ora_inizio"])
            st.write("🕒 Alle:", r["ora_fine"])
            st.write("📌 Note:", r.get("note", ""))

    # =====================
    # APPROVAZIONI
    # =====================

    if ruolo.upper() in [
        "CAPOSQUADRA",
        "INGEGNERIA"
    ]:

        st.divider()
        st.subheader("✅ Richieste da approvare")

        richieste = supabase.table(
            "richieste_permessi"
        ).select("*").eq(
            "stato",
            "IN ATTESA"
        ).execute().data

        if ruolo.upper() == "CAPOSQUADRA":

            richieste = [
                r for r in richieste
                if r.get("squadra") == squadra
            ]

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
