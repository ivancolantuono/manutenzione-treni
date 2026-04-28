import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

from db import supabase, get_planning, get_operatori


# =========================
# 🔒 CHECK SOVRAPPOSIZIONE
# =========================
def check_overlap(matricola, start, end):

    res = supabase.table("planning")\
        .select("*")\
        .eq("matricola", matricola)\
        .eq("stato", "ATTIVO")\
        .execute()

    for r in res.data:

        existing_start = datetime.fromisoformat(r["inizio"])
        existing_end = datetime.fromisoformat(r["fine"])

        if start < existing_end and end > existing_start:
            return True

    return False


# =========================
# 🧠 UI PLANNING COMPLETA
# =========================
def planning_page():

    st.title("🧠 Pianificazione Operatori")

    # =========================
    # AUTO REFRESH
    # =========================
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="planning_refresh")

    # =========================
    # DATI
    # =========================
    operatori_db = get_operatori()
    planning = get_planning()

    # =========================
    # MAPPE
    # =========================
    mappa_nome_to_op = {
        o.get("Nominativo"): o
        for o in operatori_db
    }

    nomi_operatori = list(mappa_nome_to_op.keys())

    # =========================
    # ➕ INSERIMENTO
    # =========================
    with st.expander("➕ Nuova attività"):

        col1, col2 = st.columns(2)

        with col1:
            operatore = st.selectbox("Operatore", nomi_operatori)
            attivita = st.text_input("Attività")

        with col2:
            inizio = st.datetime_input("Inizio", value=datetime.now())
            durata = st.number_input("Durata (min)", min_value=5, step=5)

        fine = inizio + timedelta(minutes=int(durata))

        st.write(f"⏱️ Fine prevista: {fine.strftime('%H:%M')}")

        if st.button("🚀 Assegna"):

            if not attivita.strip():
                st.error("Inserisci attività")
                st.stop()

            op = mappa_nome_to_op.get(operatore)
            matricola = str(op.get("Matricola")).strip().lower()

            if check_overlap(matricola, inizio, fine):
                st.error("⚠️ Operatore già occupato in questo orario")
                st.stop()

            supabase.table("planning").insert({
                "matricola": matricola,
                "nome": operatore,
                "attivita": attivita,
                "inizio": inizio.isoformat(),
                "fine": fine.isoformat(),
                "stato": "ATTIVO"
            }).execute()

            get_planning.clear()
            st.success("✅ Attività assegnata")
            st.rerun()

    st.divider()

    # =========================
    # 📊 DATAFRAME
    # =========================
    df = pd.DataFrame(planning)

    if df.empty:
        st.warning("Nessuna attività pianificata")
        return

    df["inizio"] = pd.to_datetime(df["inizio"])
    df["fine"] = pd.to_datetime(df["fine"])

    # =========================
    # 🟢🔴 STATO LIVE
    # =========================
    now = datetime.now()

    df["occupato"] = df.apply(
        lambda x: x["inizio"] <= now <= x["fine"],
        axis=1
    )

    occupati = df[df["occupato"]]["nome"].unique()
    liberi = [o for o in nomi_operatori if o not in occupati]

    colA, colB = st.columns(2)

    with colA:
        st.subheader("🔴 Occupati")
        for o in occupati:
            st.write(o)

    with colB:
        st.subheader("🟢 Liberi")
        for o in liberi:
            st.write(o)

    st.divider()

    # =========================
    # 📊 TIMELINE GANTT
    # =========================
    st.subheader("📊 Timeline Operatori")

    fig = px.timeline(
        df,
        x_start="inizio",
        x_end="fine",
        y="nome",
        color="attivita"
    )

    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🔒 CHIUSURA ATTIVITÀ
    # =========================
    st.subheader("🔒 Chiudi attività")

    for i, r in df.iterrows():

        if r["stato"] == "ATTIVO":

            with st.expander(f"🔧 {r['nome']} - {r['attivita']}"):

                st.write(f"🕒 {r['inizio']} → {r['fine']}")

                if st.button("✅ Chiudi", key=f"close_{i}"):

                    supabase.table("planning").update({
                        "stato": "CHIUSO"
                    }).eq("id", r["id"]).execute()

                    get_planning.clear()
                    st.success("Attività chiusa")
                    st.rerun()