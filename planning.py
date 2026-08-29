import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
from db import supabase, get_operatori
from streamlit_autorefresh import st_autorefresh

st.markdown("""
<style>

/* =========================
   POPover AZIONI PLANNING
   ========================= */

/* Riduce il pulsante del popover */
div[data-testid="stPopover"] > button {
    width: 55px !important;
    min-width: 55px !important;
    height: 38px !important;
    padding: 0 !important;
    margin: 0 auto !important;
    border-radius: 6px !important;
}

/* Riduce il contenitore del popover */
div[data-testid="stPopoverBody"] {
    width: 150px !important;
    min-width: 150px !important;
    padding: 8px !important;
}

/* Bottoni Modifica / Cancella */
div[data-testid="stPopoverBody"] .stButton > button {
    width: 100% !important;
    min-height: 38px !important;
    margin-bottom: 6px !important;
}

</style>
""", unsafe_allow_html=True)

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

    st.title("🗓️ Pianificazione Operatori")
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
    with st.expander("**➕ Nuova attività**", expanded=True):

        col1, col2 = st.columns(2)

        modo = col1.radio(
            "**Assegna a:**",
            ["Operatore", "Squadra"],
            horizontal=True
        )

        attivita = col2.text_input("**Attività**")

        col3, col4 = st.columns(2)

        now = datetime.now(ZoneInfo("Europe/Rome"))
        inizio = col3.datetime_input("**Inizio**", value=now)
        durata = col4.number_input("**Durata (min)**", min_value=5, step=5, value=60)

        fine = inizio + timedelta(minutes=durata)

        st.write(f"**⏱️ Fine prevista: {fine.strftime('%H:%M')}**")

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
            selezionati = st.multiselect("Seleziona operatori", nomi_membri)
            for nome in nomi_membri:
                if nome in occupati:
                    st.markdown(f"🔴 {nome} (occupato)")
                else:
                    st.markdown(f"🟢 {nome}")

            

        # =========================
        # 🚀 ASSEGNA
        # =========================
        if st.button("**🚀 Assegna**"):

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

    with st.expander("Mostra pianificazione", expanded=True):

        if df.empty:
            st.info("Nessuna attività pianificata")

        else:

            # =========================
            # MAPPA MATRICOLA → NOME
            # =========================
            mappa_nome = {
                str(o.get("Matricola", "")).strip().lower():
                o.get("Nominativo", "")
                for o in operatori_db
            }

            df["operatore_nome"] = df["operatore"].apply(
                lambda x: mappa_nome.get(
                    str(x).strip().lower(),
                    x
                )
            )

            df["inizio"] = pd.to_datetime(df["inizio"])
            df["fine"] = pd.to_datetime(df["fine"])

            # =========================
            # INTESTAZIONE
            # =========================
            col1, col2, col3, col4, col5 = st.columns(
                [2, 3, 1.5, 1.5, 1]
            )

            col1.markdown("**Operatore**")
            col2.markdown("**Attività**")
            col3.markdown("**Inizio**")
            col4.markdown("**Fine**")
            col5.markdown("**Azioni**")

            st.divider()

            # =========================
            # RIGHE
            # =========================
            for i, r in df.iterrows():

                col1, col2, col3, col4, col5 = st.columns(
                    [2, 3, 1.5, 1.5, 1]
                )

                col1.write(r["operatore_nome"])
                col2.write(r["attivita"])
                col3.write(r["inizio"].strftime("%H:%M"))
                col4.write(r["fine"].strftime("%H:%M"))

                # =========================
                # ⋮ MENU AZIONI
                # =========================
                with col5:
                
                    with st.popover("⋮", use_container_width=True):
                
                        # =========================
                        # ✏️ MODIFICA
                        # =========================
                        if st.button(
                            "✏️ Modifica",
                            key=f"edit_{r['id']}",
                            use_container_width=True
                        ):
                            st.session_state["edit_id"] = r["id"]
                            st.rerun()
                
                        # =========================
                        # 🗑️ CANCELLA
                        # =========================
                        if st.button(
                            "🗑️ Cancella",
                            key=f"delete_{r['id']}",
                            use_container_width=True
                        ):
                
                            try:
                
                                supabase.table("planning") \
                                    .delete() \
                                    .eq("id", r["id"]) \
                                    .execute()
                
                                get_planning.clear()
                
                                st.success("✅ Attività eliminata")
                                st.rerun()
                
                            except Exception as e:
                
                                st.error(
                                    f"Errore eliminazione: {e}"
                                )

    # =========================
    # ✏️ MODIFICA ATTIVITÀ
    # =========================
    if "edit_id" in st.session_state:

        st.subheader("✏️ Modifica attività")

        record = next(
            (
                x for x in df.to_dict("records")
                if x["id"] == st.session_state["edit_id"]
            ),
            None
        )

        if record:

            nuova_attivita = st.text_input(
                "Attività",
                value=record["attivita"]
            )

            nuovo_inizio = st.datetime_input(
                "Inizio",
                value=record["inizio"]
            )

            nuova_fine = st.datetime_input(
                "Fine",
                value=record["fine"]
            )

            col1, col2 = st.columns(2)

            # =========================
            # 💾 SALVA
            # =========================
            with col1:

                if st.button(
                    "💾 Salva modifica",
                    use_container_width=True
                ):

                    try:

                        supabase.table("planning").update({

                            "attivita": nuova_attivita,

                            "inizio":
                                nuovo_inizio.isoformat(),

                            "fine":
                                nuova_fine.isoformat()

                        }).eq(
                            "id",
                            record["id"]
                        ).execute()

                        get_planning.clear()

                        del st.session_state["edit_id"]

                        st.success(
                            "✅ Attività modificata"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Errore modifica: {e}"
                        )

            # =========================
            # ❌ ANNULLA
            # =========================
            with col2:

                if st.button(
                    "❌ Annulla",
                    use_container_width=True
                ):

                    del st.session_state["edit_id"]

                    st.rerun()

    
    st.subheader("📊 Timeline Operatori")

    # 👉 PRIMA controlli se è vuoto
    if df.empty:
        st.info("Nessuna attività da visualizzare")
    
    else:
        # mapping squadra
        mappa_squadra = {
            str(o.get("Matricola")).strip().lower(): o.get("Squadra")
            for o in operatori_db
        }
    
        df["squadra"] = df["operatore"].apply(
            lambda x: mappa_squadra.get(str(x).strip().lower(), "N/A")
        )
    
        df = df.dropna(subset=["inizio", "fine"])
    
        if df.empty:
            st.warning("Nessun dato valido per la timeline")
        else:
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
