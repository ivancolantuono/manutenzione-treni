import streamlit as st
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import date, datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
import urllib.parse

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Nasconde menu hamburger + GitHub + toolbar */
[data-testid="stToolbar"] {
    display: none;
}

/* Nasconde menu in alto a destra */
[data-testid="stDecoration"] {
    display: none;
}

/* Nasconde header */
header {
    visibility: hidden;
}

/* Sidebar completamente nascosta */
section[data-testid="stSidebar"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)

# =========================
# STILE
# =========================
st.markdown("""
<style>

/* SFONDO GENERALE */
.stApp {
    background-color: #FFFFFF;
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

@st.cache_data(ttl=5)
def get_interventi():
    res = supabase.table("interventi").select("*").execute()
    return res.data or []

@st.cache_data(ttl=10)
def get_open_item():
    res = supabase.table("open_item").select("*").execute()
    return res.data or []


# =========================
# ORAIO
# =========================
def ora_italia():
    return datetime.now(ZoneInfo("Europe/Rome")).strftime("%H:%M")

# =========================
# SUPABASE
# =========================

import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

@st.cache_data(ttl=60)
def get_utenti():

    res = supabase.table("operatori").select("*").execute()
    return res.data or[]
    
utenti = get_utenti()
# ============================
# LOG OPEN ITEM
# ============================
def salva_log(item_id, azione, utente, vecchio, nuovo):
    try:
        supabase.table("open_item_log").insert({
            "item_id": item_id,
            "azione": azione,
            "utente": utente,
            "data": datetime.now(ZoneInfo("Europe/Rome")).isoformat(),
            "valore_precedente": vecchio,
            "valore_nuovo": nuovo
        }).execute()
    except Exception as e:
        print("Errore log:", e)

# =========================
# 🔐 LOGIN + REGISTRAZIONE
# =========================
import hashlib
import time
from datetime import datetime

# =========================
# UTILS
# =========================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def format_nome(txt):
    return str(txt or "").strip().capitalize()

def norm(x):
    return str(x or "").strip().lower()   # 🔥 TUTTO MINUSCOLO

# =========================
# SESSION INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "pagina_login" not in st.session_state:
    st.session_state.pagina_login = "🔐 Login"

if "redirect_to_login" not in st.session_state:
    st.session_state.redirect_to_login = False

# 🔥 redirect PRIMA del widget
if st.session_state.redirect_to_login:
    st.session_state.pagina_login = "🔐 Login"
    st.session_state.redirect_to_login = False

# =========================
# BLOCCO LOGIN
# =========================
if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.image("frecciarossa.jpg", width=1000)

        pagina = st.radio(
            "",
            ["🔐 Login", "🆕 Registrazione", "🔑 Reset Password"],
            horizontal=True,
            key="pagina_login"
        )

        # =========================
        # 🔐 LOGIN
        # =========================
        if pagina == "🔐 Login":

            st.markdown("## 🔐 Login")

            matricola = norm(st.text_input("Matricola"))
            password = st.text_input("Password", type="password")

            if st.button("Accedi"):

                res = supabase.table("login").select("*").execute()
                utenti = res.data or []

                user = next(
                    (
                        x for x in utenti
                        if norm(x.get("matricola")) == matricola
                        and x.get("password") == hash_password(password)
                    ),
                    None
                )

                if user:

                    op = supabase.table("operatori")\
                        .select("*")\
                        .eq("Matricola", matricola)\
                        .execute()

                    if op.data:
                        nome = op.data[0].get("Nominativo")
                    else:
                        nome = user.get("nome")

                    st.session_state.logged_in = True
                    st.session_state.login_time = datetime.now()

                    # 🔥 QUESTA È LA RIGA CHE TI SALVA LA VITA
                    st.session_state.matricola = matricola.strip().lower()

                    st.session_state.utente = nome
                    st.session_state.ruolo = user.get("ruolo") or "OPERATORE"

                    st.success("✅ Accesso riuscito")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Credenziali errate")

        # =========================
        # 🆕 REGISTRAZIONE
        # =========================
        elif pagina == "🆕 Registrazione":

            st.markdown("## 🆕 Registrazione")

            nome = st.text_input("Nome")
            cognome = st.text_input("Cognome")
            email = st.text_input("Email")
            matricola = norm(st.text_input("Matricola"))

            ruolo = st.selectbox("Ruolo", ["OPERATORE", "CAPOSQUADRA"])
            password = st.text_input("Password", type="password")

            if st.button("Registrati"):

                if not nome or not cognome or not email or not matricola or not password:
                    st.error("Compila tutti i campi")
                    st.stop()

                try:
                    # 🔍 controllo login
                    esiste = supabase.table("login")\
                        .select("matricola")\
                        .eq("matricola", matricola)\
                        .execute()

                    if esiste.data:
                        st.error("Matricola già registrata")
                        st.stop()

                    # 🔥 INSERT LOGIN
                    supabase.table("login").insert({
                        "nome": format_nome(nome),
                        "cognome": format_nome(cognome),
                        "email": email,
                        "matricola": matricola,
                        "password": hash_password(password),
                        "ruolo": ruolo
                    }).execute()

                    # 🔍 controllo operatori (NO DUPLICATI)
                    op = supabase.table("operatori")\
                        .select("Matricola")\
                        .eq("Matricola", matricola)\
                        .execute()

                    if not op.data:
                        supabase.table("operatori").insert({
                            "Matricola": matricola,
                            "Nominativo": f"{format_nome(cognome)} {format_nome(nome)}",
                            "Telefono": ""
                        }).execute()

                    st.success("✅ Registrazione completata!")

                    time.sleep(1)

                    st.session_state.redirect_to_login = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Errore: {e}")

        # =========================
        # 🔑 RESET PASSWORD
        # =========================
        elif pagina == "🔑 Reset Password":

            st.markdown("## 🔑 Reset Password")

            matricola = norm(st.text_input("Matricola"))
            nuova_password = st.text_input("Nuova Password", type="password")

            if st.button("Reimposta Password"):

                if not matricola or not nuova_password:
                    st.error("Inserisci tutti i campi")
                    st.stop()

                try:
                    res = supabase.table("login")\
                        .select("*")\
                        .eq("matricola", matricola)\
                        .execute()

                    if not res.data:
                        st.error("Matricola non trovata")
                        st.stop()

                    supabase.table("login").update({
                        "password": hash_password(nuova_password)
                    }).eq("matricola", matricola).execute()

                    st.success("✅ Password aggiornata!")

                    time.sleep(1)

                    st.session_state.redirect_to_login = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Errore: {e}")

    st.stop()

# =========================
# DOPO LOGIN
# =========================
utente = st.session_state.get("utente", "")
ruolo = str(st.session_state.get("ruolo", "")).upper()
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
    if st.button("🔓 LOGOUT"):
        st.session_state.clear()
        st.rerun()

# =========================
# MENU ORIZZONTALE
# =========================
if ruolo == "CAPOSQUADRA":
    menu = st.radio(
        "",
        [
            "🚄 MANUTENZIONE",
            "📊 DASHBOARD",
            "📊 STORICO",
            "📚 SCHEDE SR",
            "📚 SCHEDE SR VZI6",
            "📦 CERCA COMPONENTE",
            "📌 OPEN ITEM"
        ],
        horizontal=True
    )
else:
    menu = st.radio(
        "",
        [
            "🚄 MANUTENZIONE",
            "📚 SCHEDE SR",
            "📚 SCHEDE SR VZI6",
            "📌 OPEN ITEM",
            "📦 CERCA COMPONENTE"
        ],
        horizontal=True
    )

# =========================
# 📥 CARICA DATABASE (SUPABASE)
# =========================
@st.cache_data(ttl=60)
def get_database_manutenzione():
    res = supabase.table("database_manutenzione").select("*").execute()
    return res.data or []

# 👉 converte in DataFrame
rows_db = get_database_manutenzione()
df = pd.DataFrame(rows_db)

# 👉 sicurezza colonne
if not df.empty:
    df.columns = df.columns.str.strip()
rows = get_interventi()

# =========================
# 👷 OPERATORI DA SUPABASE
# =========================
@st.cache_data(ttl=60)
def get_operatori():
    res = supabase.table("operatori").select("*").execute()
    return res.data or []

operatori_db = get_operatori()

operatori = [
    o.get("Nominativo")
    for o in operatori_db
    if o.get("Nominativo")
]

if "mostra" not in st.session_state:
    st.session_state["mostra"] = False

if menu == "📊 STORICO":

    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=8000, key="refresh_storico")

    st.title("📊 Storico Attività")

    # 🔥 RICARICA DATI SEMPRE
    rows = get_interventi()

    df = pd.DataFrame(rows)

    if df.empty:
        st.warning("Nessun dato presente")
        st.stop()

    # 🔥 CONVERSIONE SICURA
    for col in df.columns:
        df[col] = df[col].astype(str)

    # =========================
    # FILTRI
    # =========================

    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_treno = st.text_input("🚆 Treno")

    with col2:
        filtro_odl = st.text_input("🧾 ODL")

    with col3:
        filtro_tecnico = st.text_input("👷 Tecnico")

    stato = st.selectbox("📌 Stato", ["Tutti", "APERTO", "CHIUSO"])

    # =========================
    # FILTRAGGIO
    # =========================

    if filtro_treno:
        df = df[df["treno"].str.contains(filtro_treno, case=False)]

    if filtro_odl:
        df = df[df["odl"].str.contains(filtro_odl, case=False)]

    if filtro_tecnico:
        df = df[df["tecnico"].str.contains(filtro_tecnico, case=False)]

    if stato != "Tutti":
        df = df[df["stato"] == stato]

    # =========================
    # ORDINAMENTO
    # =========================
    if "data" in df.columns:
        df = df.sort_values(by="data", ascending=False)

    # =========================
    # METRICHE
    # =========================
    colA, colB, colC = st.columns(3)

    colA.metric("Totale", len(df))
    colB.metric("🔓 Aperti", len(df[df["stato"] == "APERTO"]))
    colC.metric("🔒 Chiusi", len(df[df["stato"] == "CHIUSO"]))

    # =========================
    # VISUALIZZAZIONE
    # =========================
    st.dataframe(df, use_container_width=True)

    # =========================
    # DOWNLOAD EXCEL
    # =========================
    import io
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)

    st.download_button(
        label="📥 Scarica Excel",
        data=buffer.getvalue(),
        file_name="storico.xlsx",
        mime="application/vnd.ms-excel"
    )

# =========================
# 🚄 MANUTENZIONE
# =========================
elif menu == "🚄 MANUTENZIONE":
    
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=8000, key="refresh_manutenzione")

    st.markdown("""
    <h1 style='margin-bottom:0;'>🚄 Gestione Manutenzione</h1>
    <p style='color:gray; margin-top:0;'>Pianificazione e controllo attività</p>
    """, unsafe_allow_html=True)
    
    import ast
    import urllib.parse

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

    if "mostra" not in st.session_state:
        st.session_state.mostra = False


    # =========================
    # DATI
    # =========================
    rows = get_interventi()

    utenti = get_utenti()
    operatori = [u.get("Nominativo") for u in utenti if u.get("Nominativo")]
    
    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    if ruolo == "CAPOSQUADRA":

             # 🔧 BOX PARAMETRI
        with st.container():
    
            st.markdown("### 🔧 DATI")
    
            col1, col2, col3 = st.columns(3)
    
            with col1:
                st.session_state.treno = st.text_input(
                    "🚄 Treno",
                    value=st.session_state.treno
                )
    
            with col2:
                st.session_state.odl = st.text_input(
                    "📝 ODL Padre",
                    value=st.session_state.odl
                )
    
            with col3:
                scelte = list(df["Scadenza"].unique())
    
                if st.session_state.scadenza not in scelte:
                    st.session_state.scadenza = scelte[0]
    
                st.session_state.scadenza = st.selectbox(
                    "📋 Scadenza",
                    scelte,
                    index=scelte.index(st.session_state.scadenza)
                )
    
            st.session_state.data = st.date_input(
                "📅 Data",
                value=st.session_state.data
            )
    
            st.markdown("<br>", unsafe_allow_html=True)
    
            # 🚀 BOTTONE GRANDE
            if st.button("🚀 Genera", use_container_width=True):
    
                if not st.session_state.treno or not st.session_state.odl:
                    st.error("⚠️ Inserisci Treno e ODL")
                else:
                    st.session_state.mostra = True
    
        if st.session_state.mostra:
    
            risultati = df[df["Scadenza"] == st.session_state.scadenza]
    
            # ✅ PRENDE I DATI DAL DB
            interventi_db = rows
    
            for i, r in risultati.iterrows():
    
                treno = st.session_state.treno
                odl = st.session_state.odl
                data_giorno = st.session_state.data
    
                # ✅ CHIAVE UNICA
                chiave = f"{r['Scheda']}{r['Intervento']}{treno}{odl}{data_giorno}"
    
                # ✅ CERCA RECORD CORRETTO
                record = next(
                    (x for x in interventi_db if str(x.get("chiave")) == str(chiave)),
                    None
                )
    
                # ✅ STATO
                if not record:
                    colore = "🔴"
                    tecnici = []
                else:
                    colore = "🟡" if record.get("stato") == "APERTO" else "🟢"
    
                    tecnici = record.get("tecnico", [])
                    if isinstance(tecnici, str):
                        try:
                            tecnici = ast.literal_eval(tecnici)
                        except:
                            tecnici = [tecnici]
    
                ods = r.get("ODS")
                
                titolo = f"{colore} **{r['Componente']}**"
                
                if ods and str(ods).lower() != "nan":
                    titolo += f"   ||      **{ods}**"
                
                with st.expander(titolo):

                    st.write(r["Intervento"])

                    # =========================
                    # 🔗 LINK
                    # =========================
                    link_raw = r.get("Link", "")
                    links = str(link_raw).split("|") if link_raw else []

                    for link in links:
                        link = link.strip()
                        if link:
                            st.markdown(f"[📄 Apri scheda tecnica]({link})")

                    # =========================
                    # 📝 NOTE
                    # =========================
                    note = record.get("note", "") if record else ""
                    st.write(note if note else "—")

                    # =========================
                    # 👷 TECNICI FIX
                    # =========================
                    tecnici_raw = record.get("tecnico", []) if record else []

                    if isinstance(tecnici_raw, str):
                        try:
                            tecnici_list = ast.literal_eval(tecnici_raw)
                        except:
                            tecnici_list = [tecnici_raw]
                    else:
                        tecnici_list = tecnici_raw

                    # 🔁 matricole → nomi
                    tecnici_default = []

                    for m in tecnici_list:
                        op = next(
                            (o for o in operatori_db if str(o.get("Matricola","")).strip().lower() == str(m).strip().lower()),
                            None
                        )
                        if op:
                            tecnici_default.append(op.get("Nominativo"))

                    tecnici_input = st.multiselect(
                        "Tecnici",
                        operatori,
                        default=tecnici_default,
                        key=f"tec_{i}"
                    )

                    # =========================
                    # BOTTONI
                    # =========================
                    colA, colB, colC = st.columns(3)

                    # 🔧 ASSEGNA
                    if colA.button("🔧 Assegna", key=f"assegna_{i}"):

                        if not tecnici_input:
                            st.error("Seleziona almeno un tecnico")
                            st.stop()

                        matricole = []
                        numeri = []

                        for t in tecnici_input:
                            op = next(
                                (o for o in operatori_db if o.get("Nominativo") == t),
                                None
                            )

                            if op:
                                matricola = str(op.get("Matricola","")).strip().lower()
                                telefono = str(op.get("Telefono","")).replace(".0","").strip()

                                if matricola:
                                    matricole.append(matricola)

                                if telefono.isdigit():
                                    numeri.append(telefono)

                        note_vecchie = record.get("note", "") if record else ""

                        supabase.table("interventi").upsert({
                            "chiave": str(chiave),
                            "treno": str(treno),
                            "odl": str(odl),
                            "scadenza": str(st.session_state.scadenza),
                            "data": str(data_giorno),
                            "componente": str(r["Componente"]),
                            "intervento": str(r["Intervento"]),
                            "link": str(link_raw),
                            "tecnico": str(matricole),
                            "caposquadra": str(utente),
                            "stato": "APERTO",
                            "inizio": str(ora_italia()),
                            "note": note_vecchie
                        }).execute()

                        st.cache_data.clear()
                        st.success("Assegnato")

                        # 📲 WHATSAPP
                        if numeri:

                            msg = f"""🚄 NUOVA ATTIVITÀ

                🚆 Treno: {treno}
                🧾 ODL: {odl}
                📅 Data: {data_giorno}
                ⏱️ Scadenza: {st.session_state.scadenza}

                👷 Caposquadra: {utente}

                🔧 {r['Intervento']}
                🔧 {r['Componente']}
                """

                            for num in numeri:
                                url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                                st.link_button(f"📲 Invia a {num}", url)

                        st.rerun()

                    # 🗑️ CANCELLA
                    if colB.button("🗑️ Cancella", key=f"cancella_{i}"):
                        supabase.table("interventi").delete().eq("chiave", chiave).execute()
                        st.cache_data.clear()
                        st.warning("Cancellato")
                        st.rerun()

                    # 🔒 CHIUDI
                    if record and record.get("stato") != "CHIUSO":
                        if colC.button("🔒 Chiudi", key=f"chiudi_{i}"):

                            note_vecchie = record.get("note","")

                            supabase.table("interventi").update({
                                "stato": "CHIUSO",
                                "fine": ora_italia(),
                                "note": note_vecchie + f"\n---\nCHIUSO DA {utente}"
                            }).eq("chiave", chiave).execute()

                            st.cache_data.clear()
                            st.success("Chiusa")
                            st.rerun()
    # =========================
    # 👷 OPERATORE
    # =========================
    else:

        st.subheader("📋 Attività assegnate")

        risultati = []

        matricola_utente = str(st.session_state.get("matricola","")).strip().lower()

        # 🔥 DEBUG (puoi togliere dopo)
        st.write("👤 Matricola utente:", matricola_utente)

        for r in rows:

            if r.get("stato") == "CHIUSO":
                continue

            tecnici_raw = r.get("tecnico", [])

            # 🔁 CONVERSIONE SICURA
            if isinstance(tecnici_raw, str):
                try:
                    tecnici_list = ast.literal_eval(tecnici_raw)
                except:
                    tecnici_list = [tecnici_raw]
            else:
                tecnici_list = tecnici_raw

            # 🔥 NORMALIZZAZIONE FORTE
            tecnici_norm = [
                str(t).replace("[","").replace("]","").replace("'","")
                .strip().lower()
                for t in tecnici_list
            ]

            # 🔥 DEBUG
            # st.write("DB:", tecnici_norm)

            if matricola_utente in tecnici_norm:
                risultati.append(r)

        # =========================
        # OUTPUT
        # =========================
        if not risultati:
            st.warning("❌ Nessuna attività trovata")
            st.stop()

        for i, record in enumerate(risultati):

            with st.expander(f"🟡 {record.get('componente','')}"):

                st.write(record.get("intervento",""))

                st.write(f"🚆 Treno: {record.get('treno','')}")
                st.write(f"🧾 ODL: {record.get('odl','')}")
                st.write(f"📅 Data: {record.get('data','')}")
                st.write(f"⏱️ Scadenza: {record.get('scadenza','')}")
                st.write(f"👷 Caposquadra: {record.get('caposquadra','')}")
                st.write(f"🕒 Inizio: {record.get('inizio','')}")

                # LINK
                link_raw = record.get("link", "")
                links = str(link_raw).split("|") if link_raw else []

                for link in links:
                    link = link.strip()
                    if link:
                        st.markdown(f"[📄 Apri scheda tecnica]({link})")

                # NOTE
                st.write(f"📝 Storico:\n{record.get('note','')}")

                note_input = st.text_area("Nota", key=f"note_{record['chiave']}_{i}")
                fine_input = st.time_input("Fine", key=f"fine_{record['chiave']}_{i}")

                # CHIUDI
                if st.button("✅ Chiudi", key=f"chiudi_{i}"):

                    note_vecchie = record.get("note") or ""

                    if note_input.strip():
                        nuove_note = f"{note_vecchie}\n---\n{utente}: {note_input.strip()}"
                    else:
                        nuove_note = note_vecchie

                    supabase.table("interventi").update({
                        "stato": "CHIUSO",
                        "fine": str(fine_input),
                        "note": nuove_note
                    }).eq("chiave", record["chiave"]).execute()

                    st.cache_data.clear()
                    st.success("Attività chiusa")
                    st.rerun()
    
elif menu == "📊 DASHBOARD":

    from streamlit_autorefresh import st_autorefresh
    import ast

    st_autorefresh(interval=8000, key="refresh_dashboard")

    st.title("📊 Dashboard Caposquadra")

    # =========================
    # DATI
    # =========================
    rows = get_interventi()
    df = pd.DataFrame(rows)

    if df.empty:
        st.warning("Nessuna attività")
        st.stop()

    # =========================
    # 🔁 MAPPA MATRICOLA → NOME
    # =========================
    operatori_db = get_operatori()

    mappa_operatori = {
        str(o.get("Matricola","")).strip().lower(): o.get("Nominativo","")
        for o in operatori_db
    }

    # =========================
    # PULIZIA
    # =========================
    for col in df.columns:
        df[col] = df[col].astype(str)

    # =========================
    # FILTRI
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        filtro_treno = st.text_input("🚆 Filtra Treno")

    with col2:
        filtro_stato = st.selectbox("📌 Stato", ["Tutti", "APERTO", "CHIUSO"])

    if filtro_treno:
        df = df[df["treno"].str.contains(filtro_treno, case=False)]

    if filtro_stato != "Tutti":
        df = df[df["stato"] == filtro_stato]

    # =========================
    # METRICHE
    # =========================
    colA, colB, colC = st.columns(3)

    colA.metric("Totale", len(df))
    colB.metric("Aperti", len(df[df["stato"] == "APERTO"]))
    colC.metric("Chiusi", len(df[df["stato"] == "CHIUSO"]))

    st.divider()

    # =========================
    # RAGGRUPPA PER TRENO
    # =========================
    treni = df["treno"].unique()

    for treno in treni:

        df_treno = df[df["treno"] == treno]

        with st.expander(f"🚆 Treno {treno} ({len(df_treno)} attività)"):

            for i, r in df_treno.iterrows():

                stato = r.get("stato","")

                colore = "🟡" if stato == "APERTO" else "🟢"

                # =========================
                # 🔁 TECNICI (MATRICOLE → NOMI)
                # =========================
                tecnici_raw = r.get("tecnico", "")

                if isinstance(tecnici_raw, str):
                    try:
                        tecnici_list = ast.literal_eval(tecnici_raw)
                    except:
                        tecnici_list = [tecnici_raw]
                else:
                    tecnici_list = tecnici_raw

                tecnici_nomi = []

                for m in tecnici_list:
                    m = str(m).strip().lower()
                    nome = mappa_operatori.get(m, m)
                    tecnici_nomi.append(nome)

                tecnici = ", ".join(tecnici_nomi)

                # =========================
                # OUTPUT
                # =========================
                st.markdown(f"""
{colore} **{r.get("componente","")}**  
🔧 {r.get("intervento","")}  
👷 TECNICO: {tecnici}  
👨‍✈️ CAPOSQUADRA: {r.get("caposquadra","")}  
📅 {r.get("data","")} | ⏱️ {r.get("scadenza","")}  
🧾 ODL: {r.get('odl','')}  
🕒 Inizio: {r.get('inizio','')}  
🏁 Fine: {r.get("fine","")}
""")

                st.divider()
# =========================
# 📦 CATALOGO COMPONENTI (SUPABASE + FAST SEARCH)
# =========================
elif menu == "📦 CERCA COMPONENTE":

    import pandas as pd
    import re

    st.title("📦 Cerca componente")

    # =========================
    # 📥 CARICAMENTO COMPLETO + COLONNA SEARCH
    # =========================
    @st.cache_data(ttl=300)
    def carica_magazzino():

        dati = []
        step = 1000
        start = 0

        while True:
            res = supabase.table("magazzino").select("*").range(start, start + step - 1).execute()

            if not res.data:
                break

            dati.extend(res.data)

            if len(res.data) < step:
                break

            start += step

        df = pd.DataFrame(dati)

        # 🔥 NORMALIZZA
        df.columns = df.columns.str.lower().str.strip()
        df = df.fillna("")

        for col in df.columns:
            df[col] = df[col].astype(str)

        # 🔥 COLONNA UNICA PER RICERCA (SUPER VELOCE)
        def normalizza(testo):
            testo = str(testo).lower()
            testo = testo.replace("_", " ").replace("-", " ")
            testo = re.sub(r"[^a-z0-9]", " ", testo)
            return testo

        df["search"] = df.apply(
            lambda x: normalizza(" ".join(x.values.astype(str))),
            axis=1
        )

        return df

    if "magazzino" not in st.session_state:

        with st.spinner("🔄 LOADING"):
            st.session_state.magazzino = carica_magazzino()

    df_mag = st.session_state.magazzino
    
    if df_mag.empty:
        st.warning("Catalogo vuoto")
        st.stop()

    # DEBUG (puoi toglierlo dopo)
    st.write("Righe:", len(df_mag))

    # =========================
    # INPUT
    # =========================
    col1, col2 = st.columns([3,1])

    with col1:
        ricerca = st.text_input(
            "🔍 Cerca componente o codice",
            placeholder="es. cilindro, compressore, 100360165"
        )

    with col2:
        limite = st.selectbox("Mostra", [50, 100, 200], index=0)

    risultati = df_mag.copy()

    # =========================
    # 🔍 RICERCA VELOCE
    # =========================
    if ricerca:

        ricerca_norm = ricerca.lower().strip()
        ricerca_norm = ricerca_norm.replace("_", " ").replace("-", " ")

        risultati = risultati[
            risultati["search"].str.contains(ricerca_norm, na=False)
        ]

    totale = len(risultati)

    # =========================
    # LIMITA RISULTATI
    # =========================
    risultati = risultati.head(limite)

    st.markdown(f"🔎 Trovati: {totale} | Mostrati: {len(risultati)}")

    if risultati.empty:
        st.warning("Nessun risultato trovato")
        st.stop()

    # =========================
    # 📄 TABELLA
    # =========================
    st.dataframe(
        risultati.drop(columns=["search"]),  # nasconde colonna tecnica
        use_container_width=True,
        height=500,
        hide_index=True
    )

    st.caption("🔍 Ricerca veloce su tutto il catalogo")

# =========================
# 📚 SCHEDE SR (SUPABASE)
# =========================
elif menu == "📚 SCHEDE SR":

    import pandas as pd
    import re

    st.title("📚 Ricerca Schede SR")

    # =========================
    # 📥 CARICAMENTO
    # =========================
    @st.cache_data(ttl=10)
    def carica_schede():

        dati = []
        step = 1000
        start = 0

        while True:
            res = supabase.table("schede_sr").select("*").range(start, start + step - 1).execute()

            if not res.data:
                break

            dati.extend(res.data)

            if len(res.data) < step:
                break

            start += step

        df = pd.DataFrame(dati)

        if df.empty:
            return df

        # 🔥 NORMALIZZA
        df.columns = df.columns.str.lower().str.strip()
        df = df.fillna("")

        for col in df.columns:
            df[col] = df[col].apply(lambda x: str(x))

        return df

    # =========================
    # CACHE
    # =========================
    if "schede_sr" not in st.session_state:
        with st.spinner("🔄 Caricamento schede SR..."):
            st.session_state.schede_sr = carica_schede()

    df_sr = st.session_state.schede_sr

    if df_sr.empty:
        st.warning("Nessuna scheda trovata")
        st.stop()

    # =========================
    # COLONNE
    # =========================
    col_manuale = "manuale"
    col_pagina = "pagina"
    col_titolo = "titolo"
    col_testo = "testo"
    col_link = "link1"
    col_sottogruppo = "sottogruppo"

    # =========================
    # PULIZIA
    # =========================
    def pulisci(testo):
        testo = str(testo).lower()
        testo = re.sub(r"[^a-z0-9]", " ", testo)
        return testo

    # =========================
    # 🔥 COLONNA UNICA RICERCA
    # =========================
    df_sr["__search__"] = (
        df_sr[col_testo] + " " +
        df_sr[col_titolo] + " " +
        df_sr[col_manuale] + " " +
        df_sr[col_sottogruppo]
    ).apply(pulisci)

    # =========================
    # INPUT
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        ricerca = st.text_input("🔍 Cerca")

    # =========================
    # 📂 SOTTOGRUPPI DINAMICI (CORRETTO)
    # =========================
    with col2:

        df_tmp = df_sr.copy()

        if ricerca:
            parole = [pulisci(p) for p in ricerca.split()]

            for parola in parole:
                df_tmp = df_tmp[
                    df_tmp["__search__"].apply(lambda x: parola in x)
                ]

        gruppi = sorted(
            df_tmp[col_sottogruppo]
            .fillna("")
            .astype(str)
            .unique()
        )

        gruppo_sel = st.selectbox(
            "📂 Sottogruppo",
            ["Tutti"] + gruppi
        )

    # =========================
    # 🔎 FILTRO PRINCIPALE
    # =========================
    df_filtrato = df_sr.copy()

    if ricerca:
        parole = [pulisci(p) for p in ricerca.split()]

        for parola in parole:
            df_filtrato = df_filtrato[
                df_filtrato["__search__"].apply(lambda x: parola in x)
            ]

    # =========================
    # 📂 FILTRO SOTTOGRUPPO
    # =========================
    if gruppo_sel != "Tutti":

        gruppo = gruppo_sel.lower()

        df_filtrato = df_filtrato[
            df_filtrato[col_sottogruppo]
            .apply(lambda x: gruppo in str(x).lower())
        ]

    risultati = df_filtrato

    # =========================
    # OUTPUT
    # =========================
    st.markdown(f"🔎 Risultati: {len(risultati)}")

    if risultati.empty:
        st.warning("Nessun risultato trovato")
        st.stop()

    gruppi = risultati.groupby([col_titolo, col_manuale])

    for (Titolo, Manuale), gruppo in gruppi:

        sottogruppo = gruppo[col_sottogruppo].iloc[0] if col_sottogruppo in gruppo.columns else ""
        
        link = ""
        if col_link in gruppo.columns:
            val = gruppo[col_link].astype(str).str.strip()
            val = val[val != ""]
            if not val.empty:
                link = val.iloc[0]

        pagine = gruppo[col_pagina].unique().tolist() if col_pagina in gruppo.columns else []

        with st.expander(f"🔧 {Titolo}"):

            # ✅ MOSTRA SEMPRE IL MANUALE
            if Manuale and str(Manuale).strip() != "":
                
                if link:
                    if not link.startswith("http"):
                        link = "https://" + link
                    st.markdown(f"📘 [{Manuale}]({link})")
                else:
                    st.markdown(f"📘 **{Manuale}**")
            else:
                st.caption("⚠️ Manuale non disponibile")

            st.caption(f"📂 {sottogruppo}")
            st.caption(f"📄 Pagine: {', '.join(map(str, pagine))}")
            
elif menu == "📌 OPEN ITEM":

    from datetime import datetime
    from zoneinfo import ZoneInfo

    utente_loggato = st.session_state.get("utente", "Sconosciuto")

    # ============================
    # FUNZIONI
    # ============================

    def ora_italia_iso():
        return datetime.now(ZoneInfo("Europe/Rome")).isoformat()

    def formatta_data(data_str):
        if not data_str:
            return "-"
        try:
            return datetime.fromisoformat(data_str).strftime("%d/%m/%Y %H:%M")
        except:
            return data_str

    @st.cache_data(ttl=10)
    def get_open_item_fast():
        return supabase.table("open_item")\
            .select("id,treno,cassa,impianto,descrizione,stato,utente,data_creazione,avanzamento,lavorazioni,data_chiusura,utente_chiusura")\
            .order("data_creazione", desc=True)\
            .execute().data

    def salva_log(item_id, azione, utente, vecchio="", nuovo="", campo=""):
        supabase.table("open_item_log").insert({
            "item_id": item_id,
            "azione": azione,
            "utente": utente,
            "valore_precedente": str(vecchio),
            "valore_nuovo": str(nuovo),
            "campo": campo,
            "data": ora_italia_iso()
        }).execute()

    def mostra_cronologia(item_id):
        log = supabase.table("open_item_log")\
            .select("*")\
            .eq("item_id", item_id)\
            .order("data", desc=False)\
            .execute().data

        if not log:
            st.info("Nessuna modifica")
            return

        st.markdown("### 📜 Cronologia")
        for l in log:
            st.write(f"{formatta_data(l['data'])} - {l['utente']} → {l['azione']}")
            if l.get("campo"):
                st.caption(f"{l['campo']}: {l.get('valore_precedente','')} → {l.get('valore_nuovo','')}")

    # ============================
    # UI
    # ============================

    st.title("📌 Open Item")

    # ============================
    # INSERIMENTO
    # ============================

    with st.expander("➕ Nuova attività"):

        col1, col2, col3 = st.columns(3)

        treno = col1.text_input("🚆 Treno")
        cassa = col2.multiselect("☑️ Cassa", ["DM1","TT2","M3","T4","T5","M6","TT7","DM8"])
        impianto = col3.selectbox("⚙️ Impianto",
            ["","Porte Interne","Freno","Antincendio","Pis","Arredo",
             "Climatizzazione","Tcms","Porte Esterne","Toilette","Bar-Bistrot","Pantografo","Alta Tensione"]
        )

        descrizione = st.text_area("📝 Descrizione")

        if st.button("➕ Inserisci"):
            if not treno or not descrizione:
                st.error("Compila i campi obbligatori")
            else:
                supabase.table("open_item").insert({
                    "treno": treno,
                    "cassa": ", ".join(cassa),
                    "impianto": impianto,
                    "descrizione": descrizione,
                    "stato": "APERTO",
                    "utente": utente_loggato,
                    "data_creazione": ora_italia_iso()
                }).execute()

                st.cache_data.clear()
                st.rerun()

    st.divider()

    # ============================
    # DATI
    # ============================

    dati = get_open_item_fast()
    # ============================
    # 🔍 FILTRI
    # ============================
    
    st.subheader("🔍 Filtri")
    
    col1, col2, col3 = st.columns(3)
    
    lista_treni = sorted(set(d.get("treno","") for d in dati if d.get("treno")))
    lista_casse = sorted(set(d.get("cassa","") for d in dati if d.get("cassa")))
    lista_impianti = sorted(set(d.get("impianto","") for d in dati if d.get("impianto")))
    
    filtro_treno = col1.multiselect("🚆 Treno", lista_treni)
    filtro_cassa = col2.multiselect("☑️ Cassa", lista_casse)
    filtro_impianto = col3.multiselect("⚙️ Impianto", lista_impianti)
    
    
    def applica_filtri(d):
    
        if filtro_treno and d.get("treno") not in filtro_treno:
            return False
    
        if filtro_cassa and d.get("cassa") not in filtro_cassa:
            return False
    
        if filtro_impianto and d.get("impianto") not in filtro_impianto:
            return False
    
        return True
    
    
    dati = [d for d in dati if applica_filtri(d)]

    aperti = [d for d in dati if d["stato"] == "APERTO"]
    valutazione = [d for d in dati if d["stato"] == "VALUTAZIONE"]
    chiusi = [d for d in dati if d["stato"] == "CHIUSO"]

    # ============================
    # 🔴 APERTI
    # ============================

    st.subheader("🔴 Attività Aperte")

    for item in aperti:

        id = item["id"]

        with st.expander(f"🔴 {item['treno']} - {item['descrizione']}"):

            st.write(f"☑️ {item.get('cassa','-')}")
            st.write(f"⚙️ {item.get('impianto','-')}")
            st.write(f"👤 {item.get('utente','-')}")
            st.write(f"📅 {formatta_data(item.get('data_creazione'))}")

            lavori = st.text_area("🔧 Lavorazioni", key=f"lav_{id}")

            avanzamento = st.text_area(
                "📈 Avanzamento / Monitoraggio",
                value=item.get("avanzamento","") or "",
                key=f"av_{id}"
            )

            col1, col2, col3, col4 = st.columns(4)

            # 🟡 MONITORAGGIO (SALVA + VALUTAZIONE)
            if col1.button("🟡 Monitoraggio", key=f"monitor_{id}"):
            
                if not avanzamento.strip():
                    st.error("Inserisci avanzamento")
                    st.stop()
            
                supabase.table("open_item").update({
                    "avanzamento": avanzamento.strip(),
                    "stato": "VALUTAZIONE"
                }).eq("id", id).execute()
            
                salva_log(
                    id,
                    "MONITORAGGIO",
                    utente_loggato,
                    item.get("avanzamento",""),
                    avanzamento,
                    "avanzamento"
                )
            
                st.cache_data.clear()
                st.rerun()
                
            # ✅ CHIUDI
            if col2.button("✅ Chiudi", key=f"close_{id}"):

                if not lavori.strip():
                    st.error("Inserisci lavorazioni")
                    st.stop()

                supabase.table("open_item").update({
                    "stato": "CHIUSO",
                    "lavorazioni": lavori.strip(),
                    "data_chiusura": ora_italia_iso(),
                    "utente_chiusura": utente_loggato
                }).eq("id", id).execute()

                salva_log(id,"CHIUSURA",utente_loggato,"","CHIUSO","stato")

                st.cache_data.clear()
                st.rerun()

            # 🗑️ ELIMINA
            if col3.button("🗑️ Elimina", key=f"del_{id}"):

                supabase.table("open_item").delete().eq("id", id).execute()

                salva_log(id,"ELIMINAZIONE",utente_loggato,"","")

                st.cache_data.clear()
                st.rerun()

            # 📜 LOG
            if col4.button("📜 Log", key=f"log_{id}"):
                mostra_cronologia(id)

    # ============================
    # 🟡 VALUTAZIONE
    # ============================

    st.subheader("🟡 Monitoraggio")

    for item in valutazione:

        id = item["id"]

        with st.expander(f"🟡 {item['treno']} - {item['descrizione']}"):

            st.write(f"☑️ {item.get('cassa','-')}")
            st.write(f"⚙️ {item.get('impianto','-')}")
            st.write(f"👤 {item.get('utente','-')}")
            st.write(f"📅 {formatta_data(item.get('data_creazione'))}")

            lavori = st.text_area("🔧 Lavorazioni", key=f"lav_val_{id}")

            avanzamento = st.text_area(
                "📈 Avanzamento",
                value=item.get("avanzamento","") or "",
                key=f"av_val_{id}"
            )

            col1, col2, col3, col4 = st.columns(4)

            if col1.button("🔴 Riporta aperto", key=f"back_{id}"):

                supabase.table("open_item").update({
                    "stato": "APERTO"
                }).eq("id", id).execute()

                salva_log(id,"STATO",utente_loggato,"VALUTAZIONE","APERTO","stato")

                st.cache_data.clear()
                st.rerun()

            if col2.button("✅ Chiudi", key=f"close_val_{id}"):

                if not lavori.strip():
                    st.error("Inserisci lavorazioni")
                    st.stop()

                supabase.table("open_item").update({
                    "stato": "CHIUSO",
                    "lavorazioni": lavori.strip(),
                    "data_chiusura": ora_italia_iso(),
                    "utente_chiusura": utente_loggato
                }).eq("id", id).execute()

                salva_log(id,"CHIUSURA",utente_loggato,"","CHIUSO","stato")

                st.cache_data.clear()
                st.rerun()

            if col3.button("💾 Aggiorna", key=f"update_av_{id}"):

                if not avanzamento.strip():
                    st.error("Inserisci avanzamento")
                    st.stop()
    
                supabase.table("open_item").update({
                    "avanzamento": avanzamento.strip()
                }).eq("id", id).execute()
    
                salva_log(
                    id,
                    "MODIFICA",
                    utente_loggato,
                    item.get("avanzamento",""),
                    avanzamento,
                    "avanzamento"
                )
    
                st.cache_data.clear()
                st.rerun()

            if col4.button("📜 Log", key=f"log_val_{id}"):
                mostra_cronologia(id)

    # ============================
    # 🟢 CHIUSI
    # ============================

    st.subheader("🟢 Attività Chiuse")

    for item in chiusi:

        id = item["id"]

        with st.expander(f"🟢 {item['treno']} - {item['descrizione']}"):

            st.write(f"☑️ {item.get('cassa','-')}")
            st.write(f"⚙️ {item.get('impianto','-')}")
            st.write(f"👤 {item.get('utente','-')}")
            st.write(f"📅 {formatta_data(item.get('data_creazione'))}")

            st.text_area(
                "🔒 Lavorazioni",
                value=item.get("lavorazioni",""),
                disabled=True,
                key=f"view_{id}"
            )

            col1, col2 = st.columns(2)

            if col1.button("🔓 Riapri", key=f"riapri_{id}"):

                supabase.table("open_item").update({
                    "stato": "APERTO"
                }).eq("id", id).execute()

                salva_log(id,"RIAPERTURA",utente_loggato,"CHIUSO","APERTO","stato")

                st.cache_data.clear()
                st.rerun()

            if col2.button("📜 Log", key=f"log_ch_{id}"):
                mostra_cronologia(id)
                
# =========================
# 📚 SCHEDE SR VZI6 (SUPABASE)
# =========================
elif menu == "📚 SCHEDE SR VZI6":

    import pandas as pd
    import re

    st.title("📚 Ricerca Schede SR VZI6")

    # =========================
    # 📥 CARICAMENTO
    # =========================
    @st.cache_data(ttl=10)
    def carica_schede():

        dati = []
        step = 1000
        start = 0

        while True:
            res = supabase.table("schede_sr_vzi6").select("*").range(start, start + step - 1).execute()

            if not res.data:
                break

            dati.extend(res.data)

            if len(res.data) < step:
                break

            start += step

        df = pd.DataFrame(dati)

        if df.empty:
            return df

        # 🔥 NORMALIZZA
        df.columns = df.columns.str.lower().str.strip()
        df = df.fillna("")

        for col in df.columns:
            df[col] = df[col].apply(lambda x: str(x))

        return df

    # =========================
    # CACHE
    # =========================
    if "schede_sr_vzi6" not in st.session_state:
        with st.spinner("🔄 Caricamento schede SR..."):
            st.session_state.schede_sr_vzi6 = carica_schede()

    df_sr = st.session_state.schede_sr_vzi6

    if df_sr.empty:
        st.warning("Nessuna scheda trovata")
        st.stop()

    # =========================
    # COLONNE
    # =========================
    col_manuale = "manuale"
    col_pagina = "pagina"
    col_titolo = "titolo"
    col_testo = "testo"
    col_link = "link"
    col_sottogruppo = "sottogruppo"

    # =========================
    # PULIZIA
    # =========================
    def pulisci(testo):
        testo = str(testo).lower()
        testo = re.sub(r"[^a-z0-9]", " ", testo)
        return testo

    # =========================
    # 🔥 COLONNA UNICA RICERCA
    # =========================
    df_sr["__search__"] = (
        df_sr[col_testo] + " " +
        df_sr[col_titolo] + " " +
        df_sr[col_manuale] + " " +
        df_sr[col_sottogruppo]
    ).apply(pulisci)

    # =========================
    # INPUT
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        ricerca = st.text_input("🔍 Cerca")

    # =========================
    # 📂 SOTTOGRUPPI DINAMICI (CORRETTO)
    # =========================
    with col2:

        df_tmp = df_sr.copy()

        if ricerca:
            parole = [pulisci(p) for p in ricerca.split()]

            for parola in parole:
                df_tmp = df_tmp[
                    df_tmp["__search__"].apply(lambda x: parola in x)
                ]

        gruppi = sorted(
            df_tmp[col_sottogruppo]
            .fillna("")
            .astype(str)
            .unique()
        )

        gruppo_sel = st.selectbox(
            "📂 Sottogruppo",
            ["Tutti"] + gruppi
        )

    # =========================
    # 🔎 FILTRO PRINCIPALE
    # =========================
    df_filtrato = df_sr.copy()

    if ricerca:
        parole = [pulisci(p) for p in ricerca.split()]

        for parola in parole:
            df_filtrato = df_filtrato[
                df_filtrato["__search__"].apply(lambda x: parola in x)
            ]

    # =========================
    # 📂 FILTRO SOTTOGRUPPO
    # =========================
    if gruppo_sel != "Tutti":

        gruppo = gruppo_sel.lower()

        df_filtrato = df_filtrato[
            df_filtrato[col_sottogruppo]
            .apply(lambda x: gruppo in str(x).lower())
        ]

    risultati = df_filtrato

    # =========================
    # OUTPUT
    # =========================
    st.markdown(f"🔎 Risultati: {len(risultati)}")

    if risultati.empty:
        st.warning("Nessun risultato trovato")
        st.stop()

    gruppi = risultati.groupby([col_titolo, col_manuale])

    for (titolo, manuale), gruppo in gruppi:

        sottogruppo = gruppo[col_sottogruppo].iloc[0] if col_sottogruppo in gruppo.columns else ""
        
        link = ""
        if col_link in gruppo.columns:
            val = gruppo[col_link].astype(str).str.strip()
            val = val[val != ""]
            if not val.empty:
                link = val.iloc[0]

        pagine = gruppo[col_pagina].unique().tolist() if col_pagina in gruppo.columns else []

        with st.expander(f"🔧 {titolo}"):

            # ✅ MOSTRA SEMPRE IL MANUALE
            if manuale and str(manuale).strip() != "":
                
                if link:
                    if not link.startswith("http"):
                        link = "https://" + link
                    st.markdown(f"📘 [{manuale}]({link})")
                else:
                    st.markdown(f"📘 **{manuale}**")
            else:
                st.caption("⚠️ Manuale non disponibile")

            st.caption(f"📂 {sottogruppo}")
            st.caption(f"📄 Pagine: {', '.join(map(str, pagine))}")
