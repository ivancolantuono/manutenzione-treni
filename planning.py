import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

# =========================
# UTILS
# =========================
def ora_italia_iso():
    return datetime.now(ZoneInfo("Europe/Rome")).isoformat()

@st.cache_data(ttl=30)
def get_planning():
    res = supabase.table("planning").select("*").execute()
    return res.data or []

def check_overlap(matricola, inizio, fine):
    res = supabase.table("planning")\
        .select("*")\
        .eq("operatore", matricola)\
        .execute()

    rows = res.data or []

    for r in rows:
        try:
            start = datetime.fromisoformat(r["inizio"])
            end = datetime.fromisoformat(r["fine"])
        except:
            continue

        if inizio < end and fine > start:
            return True

    return False


# =========================
# PAGINA
# =========================
def planning_page():

    st.title("📅 Planning Operatori")

    operatori_db = get_operatori()
    planning = get_planning()

    # =========================
    # INPUT ATTIVITÀ
    # =========================
    st.subheader("➕ Nuova attività")

    col1, col2 = st.columns(2)

    attivita = col1.text_input("🔧 Attività")

    inizio = col2.datetime_input("⏱️ Inizio", value=datetime.now())

    fine = st.datetime_input("🏁 Fine", value=datetime.now())

    # =========================
    # MODALITÀ
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
        # OCCUPATI ORA
        # =========================
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
    # ASSEGNA
    # =========================
    if st.button("🚀 Assegna"):

        if not attivita:
            st.error("Inserisci attività")
            st.stop()

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
                "fine": fine.isoformat(),
                "created_at": ora_italia_iso()
            }).execute()

        get_planning.clear()

        st.success("✅ Attività assegnata")
        st.rerun()

    st.divider()

    # =========================
    # VISUALIZZAZIONE
    # =========================
    st.subheader("📊 Planning attuale")

    if not planning:
        st.info("Nessuna attività")
        return

    df = pd.DataFrame(planning)

    if not df.empty:

        df["inizio"] = pd.to_datetime(df["inizio"], errors="coerce")
        df["fine"] = pd.to_datetime(df["fine"], errors="coerce")

        df = df.sort_values("inizio")

        for _, r in df.iterrows():

            st.markdown(f"""
🧑‍🔧 **{r.get("operatore_nome","")}**  
🔧 {r.get("attivita","")}  
⏱️ {r.get("inizio")} → {r.get("fine")}
""")

            st.divider()
