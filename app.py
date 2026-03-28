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
# LOGIN EXCEL FIX DEFINITIVO
# =========================

import pandas as pd

df_utenti = pd.read_excel("operatori.xlsx")
df_utenti.columns = df_utenti.columns.str.strip()

# pulizia
for col in df_utenti.columns:
    df_utenti[col] = df_utenti[col].astype(str).str.strip()

# fix password Excel
df_utenti["Password"] = df_utenti["Password"].str.replace(".0","")

# =========================
# SESSION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image("frecciarossa.jpg", use_container_width=True)
        st.markdown("## 🔐 Accesso Sistema")

        u = st.text_input("Utente").strip().lower()
        p = st.text_input("Password", type="password").strip()

        if st.button("Accedi"):

            user = df_utenti[
                (df_utenti["Nominativo"].str.lower() == u) &
                (df_utenti["Password"] == p)
            ]

            if not user.empty:

                st.session_state.logged_in = True
                st.session_state.utente = user.iloc[0]["Nominativo"]
                st.session_state.ruolo = user.iloc[0]["Ruolo"]
                st.session_state.squadra = user.iloc[0]["Squadra"]
                st.session_state.telefono = user.iloc[0]["Telefono"]

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
    if st.button("🔓 Disconnetti"):
        st.session_state.clear()
        st.rerun()

# =========================
# MENU
# =========================
if ruolo == "CAPOSQUADRA":
    menu = st.radio(
        "",
        ["📊 Storico", "🚄 Manutenzione", "📦 Cerca Componente", "📚 Schede SR"],
        horizontal=True
)
else:
    menu = st.radio(
         "",
         ["🚄 Manutenzione", "📊 Storico", "📦 Cerca Componente"],
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

if menu == "📊 Storico":

    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="refresh_storico")

    st.title("📊 Storico Attività")

    # 🔥 RICARICA DATI SEMPRE
    res = supabase.table("interventi").select("*").execute()
    rows = res.data if res.data else []

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
    # REFRESH
    # =========================
    if ruolo == "CAPOSQUADRA":
        st_autorefresh(interval=8000, key="refresh_capo")
    else:
        st_autorefresh(interval=8000, key="refresh_operatore")

    # =========================
    # DATI
    # =========================
    res = supabase.table("interventi").select("*").execute()
    rows = res.data if res.data else []

    df_operatori = pd.read_excel("operatori.xlsx")
    df_operatori.columns = df_operatori.columns.str.strip()

    df.columns = df.columns.str.strip()

    operatori = df_operatori["Nominativo"].dropna().tolist()

    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    if ruolo == "CAPOSQUADRA":

             # 🔧 BOX PARAMETRI
        with st.container():
    
            st.markdown("### 🔧 Parametri")
    
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
            interventi_db = supabase.table("interventi").select("*").execute().data
    
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
    
                with st.expander(f"{colore} {r['Componente']}"):
    
                    st.write(r["Intervento"])
    
                    # 🔗 LINK
                    link_raw = r.get("Link", "")
                    links = str(link_raw).split("|") if link_raw else []
    
                    for idx, link in enumerate(links):
                        link = link.strip()
                        if link:
                            st.markdown(f"[📄 Scheda {idx+1}]({link})")
    
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
                    if colA.button(f"Assegna_{i}"):

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
                    
                        st.success("Assegnato")
                        st.rerun()

                    # WHATSAPP
                    numeri = []

                    for t in tecnici_input:
                        row = df_operatori[df_operatori["Nominativo"] == t]
                        if not row.empty and "Telefono" in df_operatori.columns:
                            num = str(row["Telefono"].values[0]).replace(".0","").strip()
                            if num.isdigit():
                                numeri.append(num)

                    if numeri:

                        msg = f"""🚄 NUOVA ATTIVITÀ

🚆 Treno: {treno}
🧾 ODL: {odl}
📅 Data: {data_giorno}
⏱️ Scadenza: {st.session_state.scadenza}

👷‍♂️ Caposquadra: {utente}

🔧 {r['Intervento']}
🔧 {r['Componente']}
"""

                        for link in links:
                            if link.strip():
                                msg += f"\n📄 {link.strip()}"

                        for num in numeri:
                            url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                            st.markdown(f"[📲 Invia WhatsApp a {num}]({url})")

                    # CANCELLA
                    if colC.button(f"Cancella_{i}"):

                        supabase.table("interventi").delete().eq("chiave", chiave).execute()
                        st.warning("Cancellato")
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
                    if link.strip():
                        st.markdown(f"[📄 Scheda {idx+1}]({link.strip()})")

                # STORICO NOTE
                st.write(f"📝 Storico:\n{record.get('note','')}")
                
                # INPUT
                note_input = st.text_area("Nota", key=f"note_{record['chiave']}_{i}")
                fine_input = st.time_input("Fine", key=f"fine_{record['chiave']}_{i}")
                
                # =========================
                # =========================
                # CHIUSURA ATTIVITÀ
 
                if st.button(f"Chiudi_{i}"):

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
                
                    st.success("Attività chiusa")
                    st.rerun()
    
elif menu == "📊 Dashboard":

    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=8000, key="refresh_dashboard")

    st.title("📊 Dashboard Caposquadra")

    # =========================
    # DATI
    # =========================
    res = supabase.table("interventi").select("*").execute()
    rows = res.data if res.data else []

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

# =========================
# 📚 SCHEDE SR (EXCEL)
# =========================
elif menu == "📚 Schede SR":

    st.title("📚 Ricerca Schede SR")

    import pandas as pd

    df_sr = pd.read_excel("schede_sr.xlsx")

    # pulizia colonne
    df_sr.columns = df_sr.columns.astype(str)
    df_sr.columns = df_sr.columns.str.strip().str.lower()

    ricerca = st.text_input("🔍 Cerca componente")

    # colonne
    col_manuale = "manuale"
    col_pagina = "pagina"
    col_titolo = "titolo"
    col_testo = "testo"

    # filtro
    if ricerca:
        risultati = df_sr[
            df_sr[col_testo].astype(str).str.contains(ricerca, case=False, na=False)
        ]
    else:
        risultati = df_sr

    st.write(f"🔎 Risultati trovati: {len(risultati)}")

    # 📄 RISULTATI
    for i, r in risultati.iterrows():

        manuale = str(r.get(col_manuale, "—"))
        pagina = str(r.get(col_pagina, "—"))
        titolo = str(r.get(col_titolo, "—"))

        st.markdown(f"""
        🔧 *{titolo}*  
        📘 {manuale} — Pag. {pagina}
        """)