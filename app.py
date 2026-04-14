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

url = "https://nlsezrwjvhxvsbycxlxd.supabase.co"
key = "sb_publishable_fpaQCHaVxVoHU_x7hhuLkg_zdhiHlUl"
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
# SESSION
# =========================
if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image("frecciarossa.jpg")
        st.markdown("## 🔐 LOGIN")

        u = st.text_input("Utente").strip().lower()
        p = st.text_input("Password", type="password").strip()

        if st.button("Accedi"):

            user = next(
                (
                    x for x in utenti
                    if str(x.get("Nominativo","")).lower().strip() == u
                    and str(x.get("Password","")).replace(".0","").strip() == p
                ),
                None
            )

            if user:
                st.session_state.logged_in = True
                st.session_state.utente = user.get("Nominativo")
                st.session_state.ruolo = user.get("Ruolo")
                st.session_state.squadra = user.get("Squadra")
                st.session_state.telefono = user.get("Telefono")

                st.success("Accesso riuscito")
                st.rerun()

            else:
                st.error("Credenziali errate")

    st.stop()

utente = st.session_state.utente
ruolo = st.session_state.ruolo.upper()

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
            "🚄 Manutenzione",
            "📊 Dashboard",
            "📊 Storico",
            "📚 Schede SR",
            "📦 Cerca Componente",
            "📌 Open Item"
        ],
        horizontal=True
    )
else:
    menu = st.radio(
        "",
        [
            "🚄 Manutenzione",
            "📚 Schede SR",
            "📌 Open Item",
            "📦 Cerca Componente"
        ],
        horizontal=True
    )

# =========================
# DATI
# =========================

df = pd.read_excel("database_manutenzione.xlsx")
df.columns = df.columns.str.strip()

rows = get_interventi()

utenti = get_utenti()
operatori = [u["Nominativo"] for u in utenti]

if "mostra" not in st.session_state:
    st.session_state["mostra"] = False

if menu == "📊 Storico":

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
elif menu == "🚄 Manutenzione":
    
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
    
                    # 🔗 LINK
                    link_raw = r.get("Link", "")
                    links = str(link_raw).split("|") if link_raw else []
    
                    for idx, link in enumerate(links):
                        link = link.strip()
                        if link:
                    
                            nome = r.get("Scheda")
                    
                            if not nome:
                                nome = "Apri scheda tecnica"
                    
                            st.markdown(f"[📄 {nome}]({link})")
    
                    # 📝 NOTE (DAL DB!)
                    note = record.get("note", "") if record else ""
    
                    if note and "📎 Allegato:" in note:
                        note_pulite = note.split("📎 Allegato:")[0]
                    else:
                        note_pulite = note
    
                    st.markdown("<b><u>📝 Note operatore</u></b>", unsafe_allow_html=True)
                    st.write(note_pulite if note_pulite else "—")
    
                    # 👷 TECNICI
                    tecnici_input = st.multiselect(
                        "Tecnici",
                        operatori,
                        default=tecnici,
                        key=f"tec_{i}"
                    )
    
                    colA, colB, colC = st.columns(3)
                    # ASSEGNA
                    if colA.button("🔧 Assegna", key=f"assegna_{i}"):
                        # 🚫 BLOCCO SE NESSUN TECNICO
                        if not tecnici_input:
                            st.error("⚠️ Seleziona almeno un tecnico prima di assegnare")
                            st.stop()

                        # 🔁 recupera eventuali note già presenti
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
                            "tecnico": str(tecnici_input),
                            "caposquadra": str(utente),
                            "stato": "APERTO",
                            "inizio": str(ora_italia()),
                            "note": note_vecchie  # ✅ mantiene le note esistenti
                        }).execute()
                    
                        st.cache_data.clear()
                        st.success("Assegnato")
                        st.rerun()

                    # WHATSAPP
                    import urllib.parse

                    numeri = []

                    for t in tecnici_input:
                        for u in utenti:
                            nome = str(u.get("Nominativo","")).lower().strip()
                            telefono = str(u.get("Telefono","")).replace(".0","").strip()
                    
                            if str(t).lower().strip() == nome and telefono.isdigit():
                                numeri.append(telefono)

                        
                    if numeri:
                        
                        link = r.get("Link", "")

                        msg = f"""🚄 NUOVA ATTIVITÀ
                        
    🚆 Treno: {treno}
    🧾 ODL: {odl}
    📅 Data: {data_giorno}
    ⏱️ Scadenza: {st.session_state.scadenza}
                        
    👷 Caposquadra: {utente}
                        
    🔧 {r['Intervento']}
    🔧 {r['Componente']}
                        
    📄 Scheda tecnica:
    {link}
    """
                    
                        # 🔥 BOTTONI BELLI (NON LINK BRUTTI)
                        for num in numeri:
                            url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                            
                            st.link_button(f"📲 Invia a {num}", url)
                    # CANCELLA
                    if colB.button("🗑️ Cancella", key=f"cancella_{i}"):

                        supabase.table("interventi").delete().eq("chiave", chiave).execute()
                        st.cache_data.clear()
                        st.warning("Cancellato")
                        st.rerun()

                    # =========================
                    # 🔒 CHIUSURA FORZATA CAPOSQUADRA
                    # =========================
                    if record and record.get("stato") != "CHIUSO":
                    
                        if colC.button("🔒 Chiudi attività", key=f"chiudi_capo_{i}"):
                    
                            note_vecchie = record.get("note", "")
                    
                            nuove_note = f"{note_vecchie}\n---\nCHIUSO DA CAPOSQUADRA: {utente}"
                    
                            supabase.table("interventi").update({
                                "stato": "CHIUSO",
                                "fine": ora_italia(),
                                "note": nuove_note
                            }).eq("chiave", chiave).execute()
                    
                            st.cache_data.clear()
                            st.success("Attività chiusa dal caposquadra")
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

            tecnici = r.get("tecnico", [])

            if isinstance(tecnici, str):
                try:
                    tecnici = ast.literal_eval(tecnici)
                except:
                    tecnici = [tecnici]

            if utente in tecnici:
                risultati.append(r)

        if not risultati:
            st.info("Nessuna attività assegnata")
            st.stop()

        for i, record in enumerate(risultati):

            with st.expander(f"🟡 {record.get('componente','')}"):

                st.write(record.get("intervento",""))

                # INFO COMPLETE
                st.write(f"🚆 Treno: {record.get('treno','')}")
                st.write(f"🧾 ODL: {record.get('odl','')}")
                st.write(f"📅 Data: {record.get('data','')}")
                st.write(f"⏱️ Scadenza: {record.get('scadenza','')}")
                st.write(f"👷 Caposquadra: {record.get('caposquadra','NON DEFINITO')}")
                st.write(f"🕒 Inizio: {record.get('inizio','')}")

                # LINK MULTIPLI
                link_raw = record.get("link", "")
                links = str(link_raw).split("|") if link_raw else []

                for idx, link in enumerate(links):
                    link = link.strip()
                    if link:
                       st.markdown(f"[📄 Apri scheda tecnica]({link})")
                        
                # STORICO NOTE
                st.write(f"📝 Storico:\n{record.get('note','')}")
                
                # INPUT
                note_input = st.text_area("Nota", key=f"note_{record['chiave']}_{i}")
                fine_input = st.time_input("Fine", key=f"fine_{record['chiave']}_{i}")
                
                # =========================
                # =========================
                # CHIUSURA ATTIVIT
                if st.button("✅ Chiudi", key=f"chiudi_{i}"):

                    note_vecchie = record.get("note") or ""
                    note_input = note_input.strip()
                
                    if note_input:
                        nuove_note = f"{note_vecchie}\n---\n{utente}: {note_input}"
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
    
elif menu == "📊 Dashboard":

    from streamlit_autorefresh import st_autorefresh
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

    # pulizia
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

                if stato == "APERTO":
                    colore = "🟡"
                else:
                    colore = "🟢"

                # =========================
                # TECNICI
                # =========================
                tecnici = r.get("tecnico","")

                st.markdown(f"""
{colore} *{r.get("componente","")}*  
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
# MAGAZZINO
# =========================
elif menu == "📦 Cerca Componente":

    st.title("📦 Cerca componente")

    import re

    # =========================
    # CACHE (velocità)
    # =========================
    @st.cache_data
    def carica_magazzino():
        df = pd.read_excel("magazzino.xlsx")
        df.columns = df.columns.str.strip()

        for col in df.columns:
            df[col] = df[col].astype(str).fillna("")

        return df

    df_mag = carica_magazzino()

    # =========================
    # INPUT
    # =========================
    col1, col2 = st.columns([3,1])

    with col1:
        ricerca = st.text_input("🔍 Cerca componente o codice", placeholder="es. compressore o 100360165")

    with col2:
        limite = st.selectbox("Mostra", [50, 100, 200], index=0)

    risultati = df_mag.copy()

    # =========================
    # TROVA COLONNE PART NUMBER 🔥
    # =========================
    colonne_pn = []

    for col in df_mag.columns:
        nome = col.lower()
        if "pn" in nome or "part" in nome or "codice" in nome:
            colonne_pn.append(col)

    # =========================
    # RICERCA INTELLIGENTE
    # =========================
    if ricerca:

        parole = ricerca.lower().split()

        for parola in parole:

            mask = (
                risultati["COMPONENTE"].str.lower().str.contains(parola) |
                risultati["ASSIEME"].str.lower().str.contains(parola)
            )

            # 🔥 CERCA IN TUTTI I PART NUMBER
            for col in colonne_pn:
                mask = mask | risultati[col].str.lower().str.contains(parola)

            risultati = risultati[mask]

    totale = len(risultati)

    # =========================
    # LIMITA RISULTATI (ANTI BLOCCO)
    # =========================
    risultati = risultati.head(limite)

    st.markdown(f"🔎 Trovati: {totale} | Mostrati: {len(risultati)}")

    if risultati.empty:
        st.warning("Nessun risultato trovato")
        st.stop()

    # =========================
    # TABELLA
    # =========================
    st.dataframe(
        risultati,
        use_container_width=True,
        height=500,
        hide_index=True
    )

    # =========================
    # INFO DEBUG (utile)
    # =========================
    st.caption(f"🔍 Ricerca attiva su: COMPONENTE, ASSIEME + {', '.join(colonne_pn)}")

# =========================
# 📚 SCHEDE SR (EXCEL)
# =========================
elif menu == "📚 Schede SR":

    import pandas as pd
    import re

    st.title("📚 Ricerca Schede SR")

    # =========================
    # 📥 CARICA FILE
    # =========================
    df_sr = pd.read_excel("schede_sr.xlsx")

    # 🔥 pulizia generale (FONDAMENTALE)
    df_sr = df_sr.fillna("")

    df_sr.columns = df_sr.columns.astype(str)
    df_sr.columns = df_sr.columns.str.strip().str.lower()

    # =========================
    # 📌 COLONNE
    # =========================
    col_manuale = "manuale"
    col_pagina = "pagina"
    col_titolo = "titolo"
    col_testo = "testo"
    col_link = "link1"

    # 🔎 trova sottogruppo
    col_sottogruppo = None
    for col in df_sr.columns:
        if "sotto" in col:
            col_sottogruppo = col
            break

    # 🔥 normalizza sottogruppo
    if col_sottogruppo:
        df_sr[col_sottogruppo] = (
            df_sr[col_sottogruppo]
            .astype(str)
            .str.strip()
        )

    # =========================
    # 🔧 FUNZIONE PULIZIA
    # =========================
    def pulisci(testo):
        testo = str(testo).lower()
        testo = re.sub(r"[^a-z0-9]", " ", testo)
        return testo

    # =========================
    # 📱 INPUT
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        ricerca = st.text_input(
            "🔍 Cerca",
            placeholder="es. compressore aria"
        )

    # =========================
    # 📂 SOTTOGRUPPI DINAMICI
    # =========================
    with col2:

        if col_sottogruppo:

            df_tmp = df_sr.copy()

            if ricerca:

                parole = [pulisci(p) for p in ricerca.split()]

                df_tmp["__search__"] = (
                    df_tmp[col_testo].astype(str) + " " +
                    df_tmp[col_titolo].astype(str) + " " +
                    df_tmp[col_manuale].astype(str) + " " +
                    df_tmp[col_sottogruppo].astype(str)
                ).apply(pulisci)

                for parola in parole:
                    df_tmp = df_tmp[
                        df_tmp["__search__"].str.contains(parola, na=False)
                    ]

            gruppi = sorted(
                df_tmp[col_sottogruppo]
                .astype(str)
                .str.strip()
                .unique()
            )

            gruppo_sel = st.selectbox(
                "📂 Sottogruppo",
                ["Tutti"] + gruppi
            )

        else:
            gruppo_sel = "Tutti"

    # =========================
    # 🔎 FILTRO PRINCIPALE
    # =========================
    df_filtrato = df_sr.copy()

    if ricerca:

        parole = [pulisci(p) for p in ricerca.split()]

        df_filtrato["__search__"] = (
            df_filtrato[col_testo].astype(str) + " " +
            df_filtrato[col_titolo].astype(str) + " " +
            df_filtrato[col_manuale].astype(str)
        )

        if col_sottogruppo:
            df_filtrato["__search__"] += " " + df_filtrato[col_sottogruppo].astype(str)

        df_filtrato["__search__"] = df_filtrato["__search__"].apply(pulisci)

        for parola in parole:
            df_filtrato = df_filtrato[
                df_filtrato["__search__"].str.contains(parola, na=False)
            ]

    # =========================
    # 📂 FILTRO SOTTOGRUPPO (FIX PYARROW)
    # =========================
    if gruppo_sel != "Tutti" and col_sottogruppo:

        df_filtrato = df_filtrato[
            df_filtrato[col_sottogruppo]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .str.contains(
                gruppo_sel.strip().lower(),
                na=False,
                regex=False
            )
        ]

    risultati = df_filtrato.copy()

    # =========================
    # 📊 RISULTATI
    # =========================
    st.markdown(f"**🔎 Risultati trovati: {len(risultati)}**")

    if risultati.empty:
        st.info("Nessuna scheda trovata")
        st.stop()

    # =========================
    # 📄 OUTPUT
    # =========================
    gruppi = risultati.groupby([col_titolo, col_manuale])

    for (titolo, manuale), gruppo in gruppi:

        sottogruppo = gruppo[col_sottogruppo].iloc[0] if col_sottogruppo else ""

        # 🔗 LINK
        link = None
        if col_link in gruppo.columns:

            links = gruppo[col_link].astype(str)
            links = links[links.str.strip() != ""]
            links = links[links.str.lower() != "nan"]

            if not links.empty:
                link = links.iloc[0].strip()

        # 📄 PAGINE
        pagine = gruppo[col_pagina].astype(str).unique().tolist()

        with st.expander(f"🔧 {str(titolo)[:60]}"):

            if link:
                if not link.startswith("http"):
                    link = "https://" + link
                st.markdown(f"📘 [{manuale}]({link})")
            else:
                st.markdown(f"📘 **{manuale}**")

            if sottogruppo:
                st.caption(f"📂 {sottogruppo}")

            if pagine:
                st.caption(f"📄 Pagine: {', '.join(pagine)}")

elif menu == "📌 Open Item":

    from datetime import datetime
    from zoneinfo import ZoneInfo
    from streamlit_autorefresh import st_autorefresh

    utente_loggato = st.session_state.get("utente", "Sconosciuto")

    st_autorefresh(interval=30000, key="refresh_open_item")

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

    def mostra_cronologia(item_id):
        log = supabase.table("open_item_log")\
            .select("*")\
            .eq("item_id", item_id)\
            .order("data", desc=False)\
            .execute().data

        with st.modal("📜 Cronologia"):
            if not log:
                st.info("Nessuna modifica")
            for l in log:
                st.write(f"{formatta_data(l['data'])} - {l['utente']} → {l['azione']}")
                if l.get("campo"):
                    st.caption(f"{l['campo']}: {l.get('valore_precedente','')} → {l.get('valore_nuovo','')}")

    # ============================
    # INSERIMENTO
    # ============================

    st.title("📌 Open Item")
    st.subheader("➕ Nuova attività")

    col1, col2, col3 = st.columns(3)

    treno = col1.text_input("🚆 Treno")

    cassa = col2.multiselect("☑️ Cassa",
        ["DM1","TT2","M3","T4","T5","M6","TT7","DM8"]
    )

    impianto = col3.selectbox("⚙️ Impianto",
        ["","Porte Interne","Freno","Antincendio","Pis","Arredo",
         "Climatizzazione","Tcms","Porte Esterne","Toilette","Bar-Bistrot"]
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

            st.success("Inserito")
            st.rerun()

    st.divider()

    # ============================
    # DATI
    # ============================

    dati = get_open_item()

    # ============================
    # FILTRI
    # ============================

    st.subheader("🔍 Filtri")

    col1, col2 = st.columns(2)

    filtro_treno = col1.multiselect(
        "Treno", sorted(set(d["treno"] for d in dati if d.get("treno")))
    )

    filtro_cassa = col2.multiselect(
        "Cassa", sorted(set(d["cassa"] for d in dati if d.get("cassa")))
    )

    def filtra(d):
        if filtro_treno and d.get("treno") not in filtro_treno:
            return False
        if filtro_cassa and d.get("cassa") not in filtro_cassa:
            return False
        return True

    dati = [d for d in dati if filtra(d)]

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
                "📈 Avanzamento",
                value=item.get("avanzamento","") or "",
                key=f"av_{id}"
            )

            col1, col2, col3, col4 = st.columns(4)

            # 💾 SALVA + VALUTAZIONE
            if col1.button("💾 Salva / Valutazione", key=f"save_{id}"):

                if not avanzamento.strip():
                    st.error("Inserisci avanzamento")
                    st.stop()

                supabase.table("open_item").update({
                    "avanzamento": avanzamento.strip(),
                    "stato": "VALUTAZIONE"
                }).eq("id", id).execute()

                salva_log(id,"MODIFICA",utente_loggato,"",avanzamento,"avanzamento")
                salva_log(id,"STATO",utente_loggato,"APERTO","VALUTAZIONE","stato")

                st.rerun()

            # 🗑️ ELIMINA
            if col2.button("🗑️ Elimina", key=f"del_{id}"):
                supabase.table("open_item").delete().eq("id", id).execute()
                salva_log(id,"ELIMINAZIONE",utente_loggato,"","")
                st.rerun()

            # 📜 LOG
            if col3.button("📜 Log", key=f"log_{id}"):
                mostra_cronologia(id)

            # ✅ CHIUDI
            if col4.button("✅ Chiudi", key=f"close_{id}"):

                if not lavori.strip():
                    st.error("Inserisci lavorazioni")
                    st.stop()

                if not avanzamento.strip():
                    st.error("Inserisci avanzamento")
                    st.stop()

                supabase.table("open_item").update({
                    "stato": "CHIUSO",
                    "lavorazioni": lavori.strip(),
                    "avanzamento": avanzamento.strip(),
                    "data_chiusura": ora_italia_iso(),
                    "utente_chiusura": utente_loggato
                }).eq("id", id).execute()

                salva_log(id,"STATO",utente_loggato,"APERTO","CHIUSO","stato")
                salva_log(id,"MODIFICA",utente_loggato,"",lavori,"lavorazioni")

                st.rerun()

    # ============================
    # 🟡 VALUTAZIONE
    # ============================

    st.subheader("🟡 In Valutazione")

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

            col1, col2, col3 = st.columns(3)

            if col1.button("🔴 Apri", key=f"back_{id}"):

                supabase.table("open_item").update({
                    "stato":"APERTO"
                }).eq("id",id).execute()

                salva_log(id,"STATO",utente_loggato,"VALUTAZIONE","APERTO","stato")

                st.rerun()

            if col2.button("✅ Chiudi", key=f"close_val_{id}"):

                if not lavori.strip():
                    st.error("Inserisci lavorazioni")
                    st.stop()

                if not avanzamento.strip():
                    st.error("Inserisci avanzamento")
                    st.stop()

                supabase.table("open_item").update({
                    "stato":"CHIUSO",
                    "lavorazioni":lavori.strip(),
                    "avanzamento":avanzamento.strip(),
                    "data_chiusura":ora_italia_iso(),
                    "utente_chiusura":utente_loggato
                }).eq("id",id).execute()

                salva_log(id,"STATO",utente_loggato,"VALUTAZIONE","CHIUSO","stato")

                st.rerun()

            if col3.button("📜 Log", key=f"log_val_{id}"):
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
                    "stato":"APERTO"
                }).eq("id",id).execute()

                salva_log(id,"STATO",utente_loggato,"CHIUSO","APERTO","stato")

                st.rerun()

            if col2.button("📜 Log", key=f"log_ch_{id}"):
                mostra_cronologia(id)
