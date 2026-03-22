import streamlit as st
import pandas as pd
from datetime import date, datetime
from supabase import create_client
import urllib.parse

st.set_page_config(layout="wide")

# =========================
# STILE
# =========================

st.markdown("""
<style>

/* SFONDO GENERALE */
.stApp {
    background-color: #808080;
}

/* BOTTONI ROSSI */
.stButton>button {
    background-color: #e10600;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}

/* INPUT */
.stTextInput>div>div>input {
    background-color: white;
    border: 2px solid #ccc;
    border-radius: 6px;
}

/* TEXT AREA (NOTE) */
.stTextArea textarea {
    background-color: white !important;
    border: 2px solid #999 !important;
    border-radius: 8px !important;
    color: black !important;
}

/* LABEL NOTE */
label {
    font-weight: bold;
    color: #333;
}

/* EXPANDER */
.streamlit-expanderHeader {
    font-weight: bold;
}

/* BOX INTERVENTO */
.block-container {
    padding-top: 2rem;
}
/* SELECTBOX */
.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    border: 2px solid #999 !important;
    border-radius: 6px;
}

/* DATE INPUT */
.stDateInput input {
    background-color: white !important;
    border: 2px solid #999 !important;
    border-radius: 6px;
    color: black !important;
}

/* LABEL */
label {
    color: #000 !important;
    font-weight: bold;

</style>
""", unsafe_allow_html=True)
# =========================
# SUPABASE
# =========================

url = "https://nlsezrwjvhxvsbycxlxd.supabase.co"
key = "sb_publishable_fpaQCHaVxVoHU_x7hhuLkg_zdhiHlUl"
supabase = create_client(url, key)

# =========================
# UTENTI
# =========================

UTENTI = {
    "ivan": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "marco": {"password": "1111", "ruolo": "OPERATORE"},
}

NUMERI = {
    "marco": "393123456789"
}

# =========================
# LOGIN
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image("frecciarossa.jpg", use_container_width=True)
        st.markdown("## 🔐 Accesso Sistema")

        u = st.text_input("Utente")
        p = st.text_input("Password", type="password")

        if st.button("Accedi"):
            if u in UTENTI and UTENTI[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.utente = u
                st.session_state.ruolo = UTENTI[u]["ruolo"]
                st.rerun()
            else:
                st.error("Credenziali errate")

    st.stop()

utente = st.session_state.utente
ruolo = st.session_state.ruolo

# =========================
# HEADER
# =========================
colA, colB = st.columns([6,2])

with colA:
    st.markdown(f"### 👤 {utente} ({ruolo})")

with colB:
    st.markdown("<br><br>", unsafe_allow_html=True)  # 👈 sposta in basso
    if st.button("🔓 Disconnetti"):
        st.session_state.clear()
        st.rerun()

# =========================
# MENU
# =========================

menu = st.radio(
    "",
    ["📊 Storico", "🚄 Manutenzione", "📦 Cerca Componente"],
    horizontal=True
)

# =========================
# DATI
# =========================

df = pd.read_excel("database_manutenzione.xlsx")
df.columns = df.columns.str.strip()

res = supabase.table("interventi").select("*").execute()
rows = res.data if res.data else []

# =========================
# STORICO
# =========================

if menu == "📊 Storico":

    st.title("📊 Storico Attività")

    df_storico = pd.DataFrame(rows)

    if not df_storico.empty:
        st.dataframe(df_storico, use_container_width=True)
    else:
        st.warning("Nessun dato presente")

# =========================
# MANUTENZIONE
# =========================

elif menu == "🚄 Manutenzione":

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
            st.error("⚠️ Inserisci il treno")
        else:
            st.session_state.mostra = True
            st.session_state.scadenza = scadenza

    if st.session_state.get("mostra") and treno:

        risultati = df[df["Scadenza"] == st.session_state.scadenza]

        for i, r in risultati.iterrows():

            chiave = f"{r['Scheda']}_{r['Intervento']}_{treno}_{data_giorno}"

            record = next((x for x in rows if x["chiave"] == chiave), None)

            if not record:
                colore = "🔴"
            elif record["stato"] == "APERTO":
                colore = "🟡"
            else:
                colore = "🟢"

            tecnico = record["tecnico"] if record else ""
            stato = record["stato"] if record else "APERTO"
            inizio = record["inizio"] if record else ""
            fine = record["fine"] if record else ""
            durata = record["durata"] if record else ""
            note = record["note"] if record else ""

            if ruolo == "OPERATORE" and tecnico != utente:
                continue

            with st.expander(f"{colore} {r['Componente']}"):

                st.write(r["Intervento"])
                if "Link" in r:
                    st.markdown(f"[Apri Scheda]({r['Link']})")

                note_input = st.text_area("Note", value=note, key=f"note_{i}")

                # CAPO
                if ruolo == "CAPOSQUADRA":

                    tecnico_input = st.text_input("Tecnico", value=tecnico, key=f"t_{i}")

                    col1, col2, col3 = st.columns(3)

                    if col1.button(f"Assegna_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "tecnico": tecnico_input,
                            "stato": "APERTO",
                            "inizio": datetime.now().strftime("%H:%M"),
                            "note": note_input
                        }).execute()

                        st.success("Assegnato")
                        st.rerun()

                    if col2.button(f"Modifica_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "tecnico": tecnico_input,
                            "stato": stato,
                            "inizio": inizio,
                            "fine": fine,
                            "durata": durata,
                            "note": note_input
                        }).execute()

                        st.success("Modificato")
                        st.rerun()

                    if col3.button(f"Cancella_{i}"):

                        supabase.table("interventi").delete().eq("chiave", chiave).execute()

                        st.warning("Cancellato")
                        st.rerun()

                # OPERATORE
                if ruolo == "OPERATORE":

                    st.text_input("Inizio", value=inizio, disabled=True)

                    fine_input = st.time_input("Fine", key=f"f_{i}")

                    if st.button(f"Chiudi_{i}"):

                        try:
                            t1 = datetime.strptime(inizio, "%H:%M")
                            t2 = datetime.strptime(str(fine_input), "%H:%M:%S")
                            durata_calc = str(t2 - t1)
                        except:
                            durata_calc = ""

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "tecnico": utente,
                            "stato": "CHIUSO",
                            "inizio": inizio,
                            "fine": str(fine_input),
                            "durata": durata_calc,
                            "note": note_input
                        }).execute()

                        st.success("Chiuso")
                        st.rerun()

# =========================
# MAGAZZINO
# =========================

elif menu == "📦 Cerca Componente":

    st.title("📦 Cerca componente")

    ricerca = st.text_input("🔍 Cerca")

    df_mag = pd.read_excel("magazzino.xlsx")
    df_mag.columns = df_mag.columns.str.strip()

    for col in df_mag.columns:
        df_mag[col] = df_mag[col].astype(str).fillna("")

    if ricerca:
        df_mag = df_mag[
            df_mag["COMPONENTE"].str.contains(ricerca, case=False) |
            df_mag["ASSIEME"].str.contains(ricerca, case=False)
        ]

    st.dataframe(df_mag, use_container_width=True)