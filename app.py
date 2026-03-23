elif menu == "🚄 Manutenzione":

    from streamlit_autorefresh import st_autorefresh

    # =========================
    # 👷 OPERATORE
    # =========================
    if ruolo == "OPERATORE":

        st_autorefresh(interval=10000, key="refresh_operatore")

        st.title("📋 Attività assegnate")

        res = supabase.table("interventi").select("*").execute()
        rows = res.data if res.data else []

        risultati = [
            r for r in rows
            if r.get("tecnico") == utente and r.get("stato") != "CHIUSO"
        ]

        if not risultati:
            st.info("Nessuna attività assegnata")
            st.stop()

        for i, record in enumerate(risultati):

            colore = "🟡" if record["stato"] == "APERTO" else "🟢"

            with st.expander(f"{colore} {record.get('componente','')}"):

                st.write(record.get("intervento", ""))
                st.write(f"🚆 Treno: {record.get('treno','')}")
                st.write(f"📅 Data: {record.get('data','')}")

                note_input = st.text_area(
                    "Note",
                    value=record.get("note",""),
                    key=f"note_op_{i}"
                )

                st.text_input("Inizio", value=record.get("inizio",""), disabled=True)

                fine_input = st.time_input("Fine", key=f"fine_{i}")

                if st.button(f"Chiudi_{i}"):

                    supabase.table("interventi").update({
                        "stato": "CHIUSO",
                        "fine": str(fine_input),
                        "note": note_input
                    }).eq("chiave", record["chiave"]).execute()

                    st.success("Intervento chiuso")
                    st.rerun()

        st.stop()

    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    else:

        st_autorefresh(interval=10000, key="refresh_capo")

        st.title("🚄 Gestione Manutenzione")

        c1, c2, c3 = st.columns(3)

        with c1:
            treno = st.text_input("Treno")

        with c2:
            scadenza = st.selectbox("Scadenza", df["Scadenza"].unique())

        with c3:
            data_giorno = st.date_input("Data", value=date.today())

        if st.button("Genera"):

            if not treno:
                st.warning("⚠️ Inserisci il treno")
            else:
                st.session_state.mostra = True
                st.session_state.treno = treno
                st.session_state.scadenza = scadenza

        if st.session_state.get("mostra"):

            treno = st.session_state.treno
            risultati = df[df["Scadenza"] == st.session_state.scadenza]

            for i, r in risultati.iterrows():

                chiave = f"{r['Scheda']}_{r['Intervento']}_{treno}_{data_giorno}"

                res = supabase.table("interventi").select("*").eq("chiave", chiave).execute()
                record = res.data[0] if res.data else None

                if not record:
                    colore = "🔴"
                elif record["stato"] == "APERTO":
                    colore = "🟡"
                else:
                    colore = "🟢"

                tecnico = record["tecnico"] if record else ""
                note = record["note"] if record else ""

                with st.expander(f"{colore} {r['Componente']}"):

                    st.write(r["Intervento"])

                    note_input = st.text_area("Note", value=note, key=f"note_{i}")

                    operatori = [
                        u for u, info in UTENTI.items()
                        if info["ruolo"] == "OPERATORE"
                    ]

                    index_default = operatori.index(tecnico) if tecnico in operatori else 0

                    tecnico_input = st.selectbox(
                        "Tecnico",
                        operatori,
                        index=index_default,
                        key=f"t_{i}"
                    )

                    col1, col2, col3 = st.columns(3)

                    # 🔴 ASSEGNA
                    if col1.button(f"Assegna_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "componente": r["Componente"],
                            "intervento": r["Intervento"],
                            "tecnico": tecnico_input,
                            "stato": "APERTO",
                            "inizio": ora_italia(),
                            "note": note_input
                        }).execute()

                        st.success("Assegnato")
                        st.rerun()

                    # 🟢 WHATSAPP
                    numero = NUMERI.get(tecnico_input, "")

                    if numero:
                        messaggio = f"Ti è stata assegnata attività:\n{r['Componente']} - {r['Intervento']}\nTreno {treno}"
                        link = f"https://wa.me/{numero}?text={urllib.parse.quote(messaggio)}"
                        st.markdown(f"[📲 Invia su WhatsApp]({link})")

                    # ❌ CANCELLA
                    if col3.button(f"Cancella_{i}"):

                        supabase.table("interventi").delete().eq("chiave", chiave).execute()

                        st.warning("Cancellato")
                        st.rerun()