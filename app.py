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
if is_mobile:
    st.markdown("""
    <style>

    /* RIDUCE SPAZI */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }

    /* BOTTONI GRANDI */
    .stButton>button {
        width: 100%;
        height: 50px;
        font-size: 18px;
    }

    /* TEXT AREA GRANDE */
    textarea {
        font-size: 16px !important;
    }

    /* INPUT */
    input {
        font-size: 16px !important;
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        font-size: 18px !important;
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
is_mobile = st.session_state.get("mobile", False)

if st.sidebar.checkbox("📱 Modalità Mobile"):
    is_mobile = True
    st.session_state.mobile = True

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

    st.title("🚄 Gestione Manutenzione")

    import ast
    from datetime import datetime, date
    import urllib.parse

    # =========================
    # MODALITÀ MOBILE
    # =========================
    is_mobile = st.sidebar.checkbox("📱 Modalità Mobile", value=True)

    if is_mobile:
        st.markdown("""
        <style>
        .block-container {padding: 1rem;}
        .stButton>button {width:100%; height:50px; font-size:18px;}
        textarea, input {font-size:16px !important;}
        </style>
        """, unsafe_allow_html=True)

    # =========================
    # DATI
    # =========================
    res = supabase.table("interventi").select("*").execute()
    rows = res.data if res.data else []

    df_operatori = pd.read_excel("operatori.xlsx")
    df_operatori.columns = df_operatori.columns.str.strip()

    operatori = df_operatori["Nominativo"].dropna().tolist()

    # =========================
    # FIX TECNICI
    # =========================
    def fix_tecnici(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                return ast.literal_eval(val)
            except:
                return [val]
        return []

    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    if ruolo == "CAPOSQUADRA":

        st.subheader("📋 Assegnazione")

        if is_mobile:
            treno = st.text_input("🚆 Treno")
            odl = st.text_input("🧾 ODL")
            scadenza = st.selectbox("⏱️ Scadenza", df["Scadenza"].unique())
            data_giorno = st.date_input("📅 Data", value=date.today())
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                treno = st.text_input("Treno")
            with c2:
                odl = st.text_input("ODL")
            with c3:
                scadenza = st.selectbox("Scadenza", df["Scadenza"].unique())
            data_giorno = st.date_input("Data", value=date.today())

        if st.button("Genera"):

            if not treno or not odl:
                st.error("Inserisci Treno e ODL")
                st.stop()

            risultati = df[df["Scadenza"] == scadenza]

            for i, r in risultati.iterrows():

                chiave = f"{treno}{odl}{r['Intervento']}_{data_giorno}"

                rec = next((x for x in rows if str(x.get("chiave")) == str(chiave)), None)

                tecnici = fix_tecnici(rec.get("tecnico")) if rec else []

                stato = rec.get("stato") if rec else None
                colore = "🔴" if not rec else ("🟡" if stato == "APERTO" else "🟢")

                with st.expander(f"{colore} {r['Componente']}"):

                    st.write(f"🔧 {r['Intervento']}")

                    if r.get("Link"):
                        st.markdown(f"[📄 Scheda tecnica]({r['Link']})")

                    tecnici_input = st.multiselect(
                        "Tecnici",
                        operatori,
                        default=tecnici,
                        key=f"tec_{i}"
                    )

                    note_input = st.text_area(
                        "Note",
                        value=rec.get("note","") if rec else "",
                        key=f"note_{i}"
                    )

                    # =========================
                    # ASSEGNA
                    # =========================
                    if st.button(f"✅ Assegna", key=f"ass_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "odl": odl,
                            "scadenza": scadenza,
                            "data": str(data_giorno),
                            "componente": r["Componente"],
                            "intervento": r["Intervento"],
                            "link": r.get("Link",""),
                            "tecnico": list(tecnici_input),
                            "caposquadra": utente,
                            "stato": "APERTO",
                            "inizio": datetime.now().strftime("%H:%M"),
                            "note": note_input
                        }).execute()

                        st.success("Assegnato")
                        st.rerun()

                    # =========================
                    # WHATSAPP
                    # =========================
                    numeri = []

                    for t in tecnici_input:
                        row = df_operatori[df_operatori["Nominativo"] == t]
                        if not row.empty:
                            num = str(row["Telefono"].values[0]).replace(".0","").strip()
                            if num.isdigit():
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
                            url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                            st.markdown(f"[📲 WhatsApp {num}]({url})")

                    # =========================
                    # MODIFICA + CHIUSURA
                    # =========================
                    if rec:

                        st.write(f"👨‍✈️ {rec.get('caposquadra','')}")
                        st.write(f"🕒 Inizio: {rec.get('inizio','')}")

                        fine = st.time_input("Fine", key=f"fine_{i}")

                        if st.button("🔴 Chiudi", key=f"chiudi_{i}"):

                            supabase.table("interventi").update({
                                "stato": "CHIUSO",
                                "fine": str(fine),
                                "note": f"{rec.get('note','')}\n---\nCHIUSO DA CAPO"
                            }).eq("chiave", chiave).execute()

                            st.rerun()

    # =========================
    # 👷 OPERATORE
    # =========================
    else:

        st.subheader("📋 Attività assegnate")

        risultati = []

        for r in rows:

            if r.get("stato") == "CHIUSO":
                continue

            tecnici = fix_tecnici(r.get("tecnico"))

            if utente in tecnici:
                risultati.append(r)

        if not risultati:
            st.info("Nessuna attività")
            st.stop()

        for i, record in enumerate(risultati):

            with st.container():

                st.markdown(f"""
                ### 🔧 {record.get('componente','')}
                👨‍✈️ {record.get('caposquadra','')}
                🚆 {record.get('treno','')}
                🧾 {record.get('odl','')}
                ⏱️ {record.get('scadenza','')}
                """)

                if record.get("link"):
                    st.markdown(f"[📄 Scheda tecnica]({record.get('link')})")

                st.write(f"🕒 Inizio: {record.get('inizio','')}")

                note_input = st.text_area("Note", key=f"note_op_{i}")
                fine_input = st.time_input("Fine", key=f"fine_op_{i}")

                if st.button("✅ CHIUDI", key=f"close_{i}"):

                    supabase.table("interventi").update({
                        "stato": "CHIUSO",
                        "fine": str(fine_input),
                        "note": f"{record.get('note','')}\n---\n{utente}: {note_input}"
                    }).eq("chiave", record["chiave"]).execute()

                    st.success("Chiuso")
                    st.rerun()

                st.divider()
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