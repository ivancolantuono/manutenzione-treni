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

    # =========================
    # 📥 DATI
    # =========================
    operatori_db = get_operatori()
    dati = get_planning()

    df = pd.DataFrame(dati)

    if not df.empty:
        df["inizio"] = pd.to_datetime(df["inizio"])
        df["fine"] = pd.to_datetime(df["fine"])

    # =========================
    # 🔍 CHECK OVERLAP (VELOCE)
    # =========================
    def check_overlap_local(matricola, inizio, fine):

        if df.empty:
            return False

        records = df[df["operatore"] == matricola]

        for _, r in records.iterrows():
            if not (fine <= r["inizio"] or inizio >= r["fine"]):
                return True

        return False

    # =========================
    # 👷 LISTE
    # =========================
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

        modo = col1.radio(
            "Assegna a:",
            ["Operatore", "Squadra"],
            horizontal=True
        )

        attivita = col2.text_input("Attività")

        col3, col4 = st.columns(2)

        inizio = col3.datetime_input("Inizio", value=datetime.now())
        durata = col4.number_input("Durata (min)", min_value=5, step=5, value=60)

        fine = inizio + timedelta(minutes=durata)

        st.write(f"⏱️ Fine prevista: {fine.strftime('%H:%M')}")

        # =========================
        # 👤 OPERATORE SINGOLO
        # =========================
        if modo == "Operatore":

            selezione = col1.selectbox("Operatore", operatori)

        # =========================
        # 👥 SQUADRA
        # =========================
        else:

            squadra = col1.selectbox("Squadra", squadre)

            membri = [
                o for o in operatori_db
                if o.get("Squadra") == squadra
            ]

            nomi_membri = []
            occupati = []

            for o in membri:
                nome = o.get("Nominativo")
                matricola = str(o.get("Matricola", "")).strip().lower()

                if not nome or not matricola:
                    continue

                nomi_membri.append(nome)

                if check_overlap_local(matricola, inizio, fine):
                    occupati.append(nome)

            # 👇 VISUALIZZAZIONE STATO
            st.write("👥 Membri squadra:")
            for nome in nomi_membri:
                if nome in occupati:
                    st.markdown(f"🔴 {nome} (occupato)")
                else:
                    st.markdown(f"🟢 {nome}")

            selezionati = st.multiselect("Seleziona operatori", nomi_membri)

        # =========================
        # 🚀 ASSEGNA
        # =========================
        if st.button("🚀 Assegna"):

            if not attivita:
                st.error("Inserisci attività")
                st.stop()

            matricole = []

            # -------------------------
            # OPERATORE
            # -------------------------
            if modo == "Operatore":

                op = next(
                    (o for o in operatori_db if o.get("Nominativo") == selezione),
                    None
                )

                if op:
                    m = str(op.get("Matricola", "")).strip().lower()

                    if check_overlap_local(m, inizio, fine):
                        st.error("⚠️ Operatore occupato")
                        st.stop()

                    matricole.append(m)

            # -------------------------
            # SQUADRA
            # -------------------------
            else:

                if not selezionati:
                    st.error("Seleziona almeno un operatore")
                    st.stop()

                for nome in selezionati:

                    if nome in occupati:
                        continue  # 👉 BLOCCO OCCUPATI

                    op = next(
                        (o for o in membri if o.get("Nominativo") == nome),
                        None
                    )

                    if op:
                        m = str(op.get("Matricola", "")).strip().lower()
                        matricole.append(m)

                if not matricole:
                    st.error("Tutti gli operatori selezionati sono occupati")
                    st.stop()

            # =========================
            # 💾 INSERT
            # =========================
            try:
                for m in matricole:
                    supabase.table("planning").insert({
                        "operatore": m,
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
    # 📊 TABELLA
    # =========================
    st.subheader("📊 Pianificazione")

    if df.empty:
        st.info("Nessuna attività pianificata")
        return

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
