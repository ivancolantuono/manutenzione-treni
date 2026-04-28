import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from db import supabase, get_operatori

# =========================
# 🔄 GET PLANNING
# =========================
@st.cache_data(ttl=10)
def get_planning():
    res = supabase.table("planning").select("*").execute()
    return res.data or []

# =========================
# 🔍 CHECK OVERLAP
# =========================
def check_overlap(matricola, inizio, fine):

    res = supabase.table("planning")\
        .select("*")\
        .eq("operatore", matricola)\
        .execute()

    records = res.data or []

    for r in records:
        try:
            start_db = datetime.fromisoformat(r["inizio"])
            end_db = datetime.fromisoformat(r["fine"])
        except:
            continue

        if not (fine <= start_db or inizio >= end_db):
            return True

    return False

# =========================
# 🧠 PAGINA PRINCIPALE
# =========================
def planning_page():

    st.title("🧠 Pianificazione Operatori")

    operatori_db = get_operatori()

    operatori = [
        o.get("Nominativo")
        for o in operatori_db
        if o.get("Nominativo")
    ]

    squadre = sorted(
        list({
            o.get("Squadra")
            for o in operatori_db
            if o.get("Squadra")
        })
    )

    # =========================
    # ➕ NUOVA ATTIVITÀ
    # =========================
    with st.expander("➕ Nuova attività", expanded=True):

        col1, col2 = st.columns(2)

        modo = col1.radio("Assegna a:", ["Operatore", "Squadra"], horizontal=True)

        operatori_scelti = []

        # =========================
        # OPERATORE SINGOLO
        # =========================
        if modo == "Operatore":

            selezione = col1.selectbox("Operatore", operatori)
            operatori_scelti = [selezione]

        # =========================
        # SQUADRA → SCELTA OPERATORI
        # =========================
        else:

            squadra_sel = col1.selectbox("Squadra", squadre)

            membri = [
                o.get("Nominativo")
                for o in operatori_db
                if o.get("Squadra") == squadra_sel
            ]

            st.info("👥 " + ", ".join(membri))

            operatori_scelti = st.multiselect(
                "Seleziona operatori della squadra",
                membri,
                default=membri
            )

        attivita = col2.text_input("Attività")

        col3, col4 = st.columns(2)

        inizio = col3.datetime_input("Inizio", value=datetime.now())
        durata = col4.number_input("Durata (min)", min_value=5, step=5, value=60)

        fine = inizio + timedelta(minutes=durata)

        st.write(f"⏱️ Fine prevista: {fine.strftime('%H:%M')}")

        # =========================
        # 🚀 ASSEGNA
        # =========================
        if st.button("🚀 Assegna"):

            if not operatori_scelti:
                st.error("Seleziona almeno un operatore")
                st.stop()

            if not attivita:
                st.error("Inserisci attività")
                st.stop()

            matricole = []

            for nome in operatori_scelti:

                op = next(
                    (o for o in operatori_db if o.get("Nominativo") == nome),
                    None
                )

                if op:
                    m = str(op.get("Matricola", "")).strip().lower()
                    if m:
                        matricole.append(m)

            # =========================
            # 🔍 OVERLAP
            # =========================
            for m in matricole:
                if check_overlap(m, inizio, fine):
                    st.error(f"⚠️ Operatore occupato: {m}")
                    st.stop()

            # =========================
            # 💾 INSERT
            # =========================
            try:
                for nome, m in zip(operatori_scelti, matricole):

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

            except Exception as e:
                st.error(f"Errore insert: {e}")

    # =========================
    # 📊 DATI
    # =========================
    st.subheader("📊 Pianificazione")

    dati = get_planning()

    if not dati:
        st.info("Nessuna attività pianificata")
        return

    df = pd.DataFrame(dati)

    # =========================
    # 🔁 MATRICOLA → NOME
    # =========================
    mappa_nome = {
        str(o.get("Matricola")).strip().lower(): o.get("Nominativo")
        for o in operatori_db
    }

    mappa_squadra = {
        str(o.get("Matricola")).strip().lower(): o.get("Squadra")
        for o in operatori_db
    }

    df["operatore_nome"] = df["operatore"].apply(
        lambda x: mappa_nome.get(str(x).strip().lower(), x)
    )

    df["squadra"] = df["operatore"].apply(
        lambda x: mappa_squadra.get(str(x).strip().lower(), "")
    )

    df["inizio"] = pd.to_datetime(df["inizio"])
    df["fine"] = pd.to_datetime(df["fine"])

    df = df.sort_values("inizio")

    # =========================
    # 📄 TABELLA
    # =========================
    st.dataframe(
        df[["operatore_nome", "squadra", "attivita", "inizio", "fine"]],
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 📊 TIMELINE
    # =========================
    st.subheader("📊 Timeline Operatori")

    fig = px.timeline(
        df,
        x_start="inizio",
        x_end="fine",
        y="operatore_nome",
        color="squadra"
    )

    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🟢 DISPONIBILI ORA
    # =========================
    st.subheader("🟢 Operatori disponibili ora")

    now = datetime.now()

    occupati = set()

    for _, r in df.iterrows():
        if r["inizio"] <= now <= r["fine"]:
            occupati.add(r["operatore_nome"])

    liberi = [o for o in operatori if o not in occupati]

    if liberi:
        st.success(", ".join(liberi))
    else:
        st.warning("Nessun operatore disponibile")
