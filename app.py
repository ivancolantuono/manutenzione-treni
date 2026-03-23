import streamlit as st
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import date, datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
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
}
</style>
""", unsafe_allow_html=True)
# =========================
# ORAIO
# =========================
def ora_italia():
    return datetime.now(ZoneInfo("Europe/Rome")).strftime("%H:%M")

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
    "Massaro": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "Colantuono": {"password": "1111", "ruolo": "OPERATORE"},
    "Lucariello": {"password": "1111", "ruolo": "OPERATORE"},
    "Santorelli": {"password": "1111", "ruolo": "OPERATORE"},
    "Dubbioso": {"password": "1111", "ruolo": "OPERATORE"},
}

NUMERI = {
    "Colantuono": "393477618059"
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
    st.markdown(f"""
    <div style='margin-top:20px; font-size:24px; font-weight:bold;'>
    👤 {utente} ({ruolo})
    </div>
    """, unsafe_allow_html=True)

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
    
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="refresh_storico")
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

                st.write(f"🔧 {record.get('componente','')}")
                st.write(f"📋 {record.get('intervento','')}")

                link = record.get("link", "")

                if link:
                   st.markdown(f"[📄 Apri scheda tecnica]({link})")
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

                        data_insert = {
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "componente": str(r.get("componente","")),
                            "intervento": str(r.get("intervento","")),
                            "link": r.get("Link",""),                            
                            "tecnico": tecnico_input,
                            "stato": "APERTO",
                            "inizio": ora_italia(),
                            "note": note_input
                        }
                        st.write("DEBUG:", data_insert)
                        
                        supabase.table("interventi").upsert(data_insert).execute()

                        st.success("Assegnato")
                        st.rerun()

                    # 🟢 WHATSAPP
                    numero = NUMERI.get(tecnico_input, "")

                    if numero:
                        messaggio = f"Ti è stata assegnata una nuova attività:\n{r['Componente']} - {r['Intervento']}\nTreno {treno} - {r['Scheda']}_{r['Intervento']}"
                        link = f"https://wa.me/{numero}?text={urllib.parse.quote(messaggio)}"
                        st.markdown(f"[📲 Invia su WhatsApp]({link})")

                    # ❌ CANCELLA
                    if col3.button(f"Cancella_{i}"):

                        supabase.table("interventi").delete().eq("chiave", chiave).execute()

                        st.warning("Cancellato")
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