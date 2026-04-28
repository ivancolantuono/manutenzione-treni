# =========================
# SELEZIONE MODALITÀ
# =========================
modo = st.radio(
    "Modalità assegnazione",
    ["Operatore singolo", "Squadra"],
    horizontal=True
)

operatori_selezionati = []

# =========================
# OPERATORE SINGOLO
# =========================
if modo == "Operatore singolo":

    nomi = [o.get("Nominativo") for o in operatori_db if o.get("Nominativo")]

    selezionato = st.selectbox("Operatore", nomi)

    operatori_selezionati = [selezionato]


# =========================
# SQUADRA
# =========================
else:

    squadre = sorted(list(set(
        o.get("Squadra") for o in operatori_db if o.get("Squadra")
    )))

    squadra_sel = st.selectbox("Squadra", squadre)

    membri = [
        o for o in operatori_db
        if o.get("Squadra") == squadra_sel
    ]

    nomi_membri = [m.get("Nominativo") for m in membri]

    st.write("👥 Seleziona operatori della squadra")

    operatori_selezionati = st.multiselect(
        "Operatori",
        nomi_membri,
        default=nomi_membri
    )

    # =========================
    # CHECK OCCUPATI ORA
    # =========================
    planning = get_planning()
    now = datetime.now()

    occupati = []

    for p in planning:
        try:
            start = datetime.fromisoformat(p["inizio"])
            end = datetime.fromisoformat(p["fine"])
        except:
            continue

        if start <= now <= end:
            occupati.append(p["operatore"])

    occupati_nomi = [
        o.get("Nominativo")
        for o in operatori_db
        if str(o.get("Matricola","")).strip().lower() in occupati
    ]

    if occupati_nomi:
        st.warning("🔴 Occupati ora: " + ", ".join(occupati_nomi))


# =========================
# BOTTONE ASSEGNA
# =========================
if st.button("🚀 Assegna"):

    if not operatori_selezionati:
        st.error("Seleziona almeno un operatore")
        st.stop()

    matricole = []

    for nome in operatori_selezionati:

        op = next(
            (o for o in operatori_db if o.get("Nominativo") == nome),
            None
        )

        if op:
            m = str(op.get("Matricola","")).strip().lower()
            if m:
                matricole.append(m)

    # =========================
    # CHECK OVERLAP
    # =========================
    for m in matricole:
        if check_overlap(m, inizio, fine):
            st.error(f"⛔ Operatore occupato: {m}")
            st.stop()

    # =========================
    # INSERT
    # =========================
    for nome, m in zip(operatori_selezionati, matricole):

        supabase.table("planning").insert({
            "operatore": m,
            "operatore_nome": nome,
            "attivita": attivita,
            "inizio": inizio.isoformat(),
            "fine": fine.isoformat()
        }).execute()

    get_planning.clear()

    st.success("✅ Attività assegnata")
    st.rerun()
