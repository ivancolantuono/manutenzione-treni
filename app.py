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
    color: black;
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
    "Morello": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "Cacace": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "Dentice": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "Basco": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "Colantuono": {"password": "1111", "ruolo": "OPERATORE"},
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

df_operatori = pd.read_excel("operatori.xlsx")
df_operatori.columns = df_operatori.columns.str.strip()

if "mostra" not in st.session_state:
    st.session_state["mostra"] = False

# =========================
# STORICO
# =========================

if menu == "📊 Storico":
    
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=15000, key="refresh_storico")
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

    import ast
    import urllib.parse

    st.title("🚄 Gestione Manutenzione")

    # =========================
    # SESSION STATE
    # =========================
    if "treno" not in st.session_state:
        st.session_state.treno = ""

    if "odl" not in st.session_state:
        st.session_state.odl = ""

    if "scadenza" not in st.session_state:
        st.session_state.scadenza = None

    if "data" not in st.session_state:
        st.session_state.data = date.today()

    # trigger aggiornamento
    if "refresh_key" not in st.session_state:
        st.session_state.refresh_key = 0

    # =========================
    # DATI (sempre freschi)
    # =========================
    def carica_interventi():
        return supabase.table("interventi").select("*").execute().data

    rows = carica_interventi()

    df_operatori = pd.read_excel("operatori.xlsx")
    df_operatori.columns = df_operatori.columns.str.strip()
    operatori = df_operatori["Nominativo"].dropna().tolist()

    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    if ruolo == "CAPOSQUADRA":

        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state.treno = st.text_input("Treno", value=st.session_state.treno)

        with col2:
            st.session_state.odl = st.text_input("ODL Padre", value=st.session_state.odl)

        with col3:
            scadenze = df["Scadenza"].unique().tolist()

            if st.session_state.scadenza not in scadenze:
                st.session_state.scadenza = scadenze[0]

            st.session_state.scadenza = st.selectbox(
                "Scadenza",
                scadenze,
                index=scadenze.index(st.session_state.scadenza)
            )

        st.session_state.data = st.date_input("Data", value=st.session_state.data)

        if st.button("Genera"):
            st.session_state.mostra = True

        if st.session_state.get("mostra"):

            risultati = df[df["Scadenza"] == st.session_state.scadenza]

            for i, r in risultati.iterrows():

                chiave = f"{r['Scheda']}{r['Intervento']}{st.session_state.treno}{st.session_state.odl}{st.session_state.data}"

                rec = next((x for x in rows if x["chiave"] == chiave), None)

                colore = "🔴" if not rec else ("🟡" if rec["stato"] == "APERTO" else "🟢")

                tecnici = []
                if rec:
                    tecnici = rec.get("tecnico", [])
                    if isinstance(tecnici, str):
                        tecnici = ast.literal_eval(tecnici)

                with st.expander(f"{colore} {r['Componente']}"):

                    st.write(f"🔧 {r['Intervento']}")

                    # LINK DOPPIO
                    if r.get("Link"):
                        st.markdown(f"[📄 Scheda 1]({r['Link']})")
                    if r.get("Link2"):
                        st.markdown(f"[📄 Scheda 2]({r['Link2']})")

                    note = rec.get("note","") if rec else ""
                    note_input = st.text_area("Note", value=note, key=f"note_{i}")

                    tecnici_input = st.multiselect(
                        "Tecnici",
                        operatori,
                        default=tecnici,
                        key=f"tec_{i}"
                    )

                    colA, colB = st.columns(2)

                    # ASSEGNA
                    if colA.button(f"Assegna_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": st.session_state.treno,
                            "odl": st.session_state.odl,
                            "scadenza": st.session_state.scadenza,
                            "data": str(st.session_state.data),
                            "componente": r["Componente"],
                            "intervento": r["Intervento"],
                            "link": r.get("Link",""),
                            "link2": r.get("Link2",""),
                            "tecnico": tecnici_input,
                            "caposquadra": utente,
                            "stato": "APERTO",
                            "inizio": ora_italia(),
                            "note": note_input
                        }).execute()

                        st.session_state.refresh_key += 1
                        st.success("Assegnato")

                    # WHATSAPP
                    numeri = []

                    for t in tecnici_input:
                        row = df_operatori[df_operatori["Nominativo"] == t]
                        if not row.empty and "Telefono" in df_operatori.columns:
                            num = str(row["Telefono"].values[0]).replace(".0","")
                            numeri.append(num)

                    if numeri:
                        msg = f"""🚄 NUOVA ATTIVITÀ

🚆 Treno: {treno}
🧾 ODL: {odl}
📅 Data: {data_giorno}
⏱️ Scadenza: {scadenza}

🔧 {r['Intervento']}
🔧 {r['Componente']}
"""

                        for num in numeri:
                            link = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                            st.markdown(f"[📲 WhatsApp {num}]({link})")

    # =========================
    # 👷 OPERATORE
    # =========================
    else:

        st.subheader("📋 Attività assegnate")

        risultati = []

        for r in rows:

            if r.get("stato") == "CHIUSO":
                continue

            tecnici = r.get("tecnico", [])
            if isinstance(tecnici, str):
                tecnici = ast.literal_eval(tecnici)

            if utente in tecnici:
                risultati.append(r)

        if not risultati:
            st.info("Nessuna attività")
            st.stop()

        for i, record in enumerate(risultati):

            with st.expander(f"🟡 {record.get('componente','')}"):

                st.write(record.get("intervento",""))
                st.write(f"🚆 {record.get('treno','')} | 🧾 {record.get('odl','')}")
                st.write(f"👷 {record.get('caposquadra','')}")

                # LINK DOPPIO
                if record.get("link"):
                    st.markdown(f"[📄 Scheda 1]({record.get('link')})")
                if record.get("link2"):
                    st.markdown(f"[📄 Scheda 2]({record.get('link2')})")

                note_input = st.text_area("Note", key=f"note_op_{i}")
                fine_input = st.time_input("Fine", key=f"fine_{i}")

                if st.button(f"Chiudi_{i}"):

                    nuove_note = f"{record.get('note','')}\n{utente}: {note_input}"

                    supabase.table("interventi").update({
                        "stato": "CHIUSO",
                        "fine": str(fine_input),
                        "note": nuove_note
                    }).eq("chiave", record["chiave"]).execute()

                    st.session_state.refresh_key += 1
                    st.success("Chiuso")
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