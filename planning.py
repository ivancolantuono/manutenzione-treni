import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
from db import supabase, get_operatori
from streamlit_autorefresh import st_autorefresh

# =========================
# 🔄 GET PLANNING
# =========================
@st.cache_data(ttl=10)
def get_planning():
    res = supabase.table("planning").select("*").execute()
    return res.data or []


# =========================
# 🧠 PAGINA PRINCIPALE
# =========================
def planning_page():

    st.title("🧠 Pianificazione Operatori")
    st_autorefresh(interval=8000, key="refresh_planning")
    get_planning.clear()

    # =========================
    # 📥 DATI
    # =========================
    operatori_db = get_operatori()
    dati = get_planning()

    df = pd.DataFrame(dati)

    if not df.empty:
        df["inizio"] = pd.to_datetime(df["inizio"])
        df["fine"] = pd.to_datetime(df["fine"])
        df["inizio"] = df["inizio"].dt.tz_localize(None)
        df["fine"] = df["fine"].dt.tz_localize(None)

    now = datetime.now()

    # =========================
    # 🔍 CHECK OVERLAP (VELOCE)
    # =========================
    def check_overlap_local(matricola, inizio, fine):

    if df.empty:
        return False

    now = datetime.now()

    records = df[df["operatore"] == matricola]

    for _, r in records.iterrows():

        # 🔥 IGNORA ATTIVITÀ GIÀ FINITE
        if r["fine"] <= now:
            continue

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

        now = datetime.now(ZoneInfo("Europe/Rome"))
        inizio = col3.datetime_input("Inizio", value=now)
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

    st.subheader("📊 Pianificazione")

    with st.expander("Mostra pianificazione", expanded=False):
    
        if df.empty:
            st.info("Nessuna attività pianificata")
    
        else:
            # mapping
            mappa_nome = {
                str(o.get("Matricola")).strip().lower(): o.get("Nominativo")
                for o in operatori_db
            }
    
            df["operatore_nome"] = df["operatore"].apply(
                lambda x: mappa_nome.get(str(x).strip().lower(), x)
            )
    
            df["inizio"] = pd.to_datetime(df["inizio"])
            df["fine"] = pd.to_datetime(df["fine"])
    
            df_display = df.copy()
    
            df_display["Operatore"] = df_display["operatore_nome"]
            df_display["Attività"] = df_display["attivita"]
            df_display["Inizio"] = df_display["inizio"].dt.strftime("%H:%M")
            df_display["Fine"] = df_display["fine"].dt.strftime("%H:%M")
    
            st.dataframe(
                df_display[["Operatore", "Attività", "Inizio", "Fine"]],
                use_container_width=True,
                hide_index=True
            )
        
        # =========================
        # LOOP RIGHE (PRO)
        # =========================
        for i, r in df.iterrows():
        
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2,2,2,2,2])
        
                col1.write(r["operatore_nome"])
                col2.write(r["attivita"])
                col3.write(r["inizio"].strftime("%H:%M"))
                col4.write(r["fine"].strftime("%H:%M"))
        
                # =========================
                # ✏️ MODIFICA
                # =========================
                if col5.button("✏️", key=f"edit_{r['id']}"):
                    st.session_state["edit_id"] = r["id"]
        
                # =========================
                # 🗑️ CANCELLA
                # =========================
                if col5.button("🗑️", key=f"delete_{r['id']}"):
                    supabase.table("planning").delete().eq("id", r["id"]).execute()
                    get_planning.clear()
                    st.rerun()

    # =========================
    # ✏️ MODIFICA ATTIVITÀ
    # =========================
    if "edit_id" in st.session_state:
    
        st.subheader("✏️ Modifica attività")
    
        record = next(
            (x for x in df.to_dict("records") if x["id"] == st.session_state["edit_id"]),
            None
        )
    
        if record:
    
            nuova_attivita = st.text_input("Attività", value=record["attivita"])
    
            nuovo_inizio = st.datetime_input(
                "Inizio",
                value=record["inizio"]
            )
    
            nuova_fine = st.datetime_input(
                "Fine",
                value=record["fine"]
            )
    
            if st.button("💾 Salva modifica"):
    
                try:
                    supabase.table("planning").update({
                        "attivita": nuova_attivita,
                        "inizio": nuovo_inizio.isoformat(),
                        "fine": nuova_fine.isoformat()
                    }).eq("id", record["id"]).execute()
    
                    get_planning.clear()
                    del st.session_state["edit_id"]
    
                    st.success("Modificato!")
                    st.rerun()
    
                except Exception as e:
                    st.error(e)
    
            if st.button("❌ Annulla"):
                del st.session_state["edit_id"]
                st.rerun()
    # =========================
    # 📊 TIMELINE
    # =========================
    st.subheader("📊 Timeline Operatori")
    
    # mapping squadra
    mappa_squadra = {
        str(o.get("Matricola")).strip().lower(): o.get("Squadra")
        for o in operatori_db
    }
    
    df["squadra"] = df["operatore"].apply(
        lambda x: mappa_squadra.get(str(x).strip().lower(), "N/A")
    )
    
    # sicurezza datetime
    df["inizio"] = pd.to_datetime(df["inizio"], errors="coerce")
    df["fine"] = pd.to_datetime(df["fine"], errors="coerce")
    df = df.dropna(subset=["inizio", "fine"])
    
    if not df.empty:
    
        fig = px.timeline(
            df,
            x_start="inizio",
            x_end="fine",
            y="operatore_nome",
            text="attivita",
            color="squadra"
        )
        fig.update_traces(textposition="inside")
    
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(yaxis_title=None)
    
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("Nessun dato per la timeline")
