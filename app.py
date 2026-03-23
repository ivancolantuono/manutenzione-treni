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

    st.title("🚄 Gestione Manutenzione")

    # =========================
    # 👷 OPERATORE
    # =========================
    if ruolo == "OPERATORE":

        st.write(f"🚆 Treno: {record.get('treno','')}")
        st.write(f"📅 Data: {record.get('data','')}")
        st.write(f"⏱️ Scadenza: {record.get('scadenza','')}")

        if record.get("link"):
             st.markdown(f"[📄 Apri scheda tecnica]({record.get('link')})")

        note_input = st.text_area("Note", value=record.get("note",""), key=f"note_op_{i}")

        inizio = record.get("inizio","")

        st.text_input("Inizio", value=inizio, disabled=True)

        fine_input = st.time_input("Fine", key=f"fine_op_{i}")

        if st.button(f"Chiudi_{i}"):

            if not inizio:
                st.error("⚠️ Intervento non iniziato")
                st.stop()

            try:
                t1 = datetime.strptime(inizio, "%H:%M")
                t2 = datetime.strptime(str(fine_input), "%H:%M:%S")

                if t2 < t1:
                    st.error("⚠️ Orario non valido")
                    st.stop()
    
                durata_calc = str(t2 - t1)

            except:
                durata_calc = ""

            # ✅ QUI È LA CHIAVE GIUSTA
            supabase.table("interventi").update({
                "stato": "CHIUSO",
                "fine": str(fine_input),
                "durata": durata_calc,
                "note": note_input
            }).eq("chiave", record["chiave"]).execute()

            st.success("✅ Intervento chiuso")
            st.rerun()

    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================

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

            res = supabase.table("interventi").select("*").eq("chiave", chiave).execute()
            record = res.data[0] if res.data else None

            colore = "🔴" if not record else ("🟡" if record["stato"] == "APERTO" else "🟢")

            tecnico = record["tecnico"] if record else ""
            note = record["note"] if record else ""

            with st.expander(f"{colore} {r['Componente']}"):

                st.write(r["Intervento"])

                link = r.get("Link", "")
                if link:
                    st.markdown(f"[📄 Apri scheda tecnica]({link})")

                note_input = st.text_area("Note", value=note, key=f"note_{i}")

                operatori = [u for u, info in UTENTI.items() if info["ruolo"] == "OPERATORE"]

                tecnico_input = st.selectbox(
                    "Tecnico",
                    operatori,
                    index=operatori.index(tecnico) if tecnico in operatori else 0,
                    key=f"t_{i}"
                )

                col1, col2, col3, col4 = st.columns(4)

                # ✅ ASSEGNA
                if col1.button(f"Assegna_{i}"):

                    supabase.table("interventi").upsert({
                        "chiave": chiave,
                        "treno": treno,
                        "data": str(data_giorno),
                        "scadenza": scadenza,
                        "componente": r["Componente"],
                        "intervento": r["Intervento"],
                        "link": r.get("Link", ""),
                        "tecnico": tecnico_input,
                        "stato": "APERTO",
                        "inizio": ora_italia(),
                        "note": note_input
                    }).execute()

                    st.success("Assegnato")
                    st.rerun()

                # ❌ CANCELLA
                if col3.button(f"Cancella_{i}"):

                    supabase.table("interventi").delete().eq("chiave", chiave).execute()
                    st.warning("Cancellato")
                    st.rerun()

                # 📲 WHATSAPP
                if col4.button(f"Invia_{i}"):

                    numero = NUMERI.get(tecnico_input, "")

                    messaggio = f"""Treno: {treno}
Attività: {r['Intervento']}
Componente: {r['Componente']}
Data: {data_giorno}
Scadenza: {scadenza}
Scheda: {link}"""

                    url = f"https://wa.me/{numero}?text={urllib.parse.quote(messaggio)}"

                    st.markdown(f"[📲 Apri WhatsApp]({url})")

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