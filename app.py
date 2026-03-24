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

df_operatori = pd.read_excel("operatori.xlsx")
df_operatori.columns = df_operatori.columns.str.strip()

if "mostra" not in st.session_state:
    st.session_state["mostra"] = False

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
    # CARICA DATI
    # =========================
    res = supabase.table("interventi").select("*").execute()
    rows = res.data if res.data else []

    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    if ruolo == "CAPOSQUADRA":

        c1, c2, c3 = st.columns(3)

        with c1:
            treno = st.text_input("Treno", key="input_treno")

        with c2:
            scadenza = st.selectbox("Scadenza", df["Scadenza"].unique(), key="input_scadenza")

        with c3:
            data_giorno = st.date_input("Data", value=date.today(), key="input_data")

        # =========================
        # GENERA (SALVA STATO)
        # =========================
        if st.button("Genera"):
            if not treno:
                st.error("Inserisci treno")
            else:
                st.session_state["mostra"] = True
                st.session_state["treno"] = treno
                st.session_state["scadenza"] = scadenza
                st.session_state["data"] = data_giorno

        # =========================
        # MOSTRA LISTA (STABILE)
        # =========================
        if st.session_state.get("mostra"):

            treno = st.session_state["treno"]
            scadenza = st.session_state["scadenza"]
            data_giorno = st.session_state["data"]

            risultati = df[df["Scadenza"] == scadenza]

            for i, r in risultati.iterrows():

                # 🔑 CHIAVE STABILE
                chiave = f"{str(r['Scheda']).strip()}{str(treno).strip()}{str(data_giorno)}"

                record = next((x for x in rows if str(x.get("chiave")) == str(chiave)), None)

                colore = "🔴"
                if record:
                    colore = "🟡" if record.get("stato") == "APERTO" else "🟢"

                with st.expander(f"{colore} {r['Componente']}"):

                    st.write(r["Intervento"])

                    if "Link" in r and pd.notna(r["Link"]):
                        st.markdown(f"[📄 Apri scheda]({r['Link']})")

                    note = record.get("note", "") if record else ""
                    note_input = st.text_area("Note", value=note, key=f"note_{i}")

                    # =========================
                    # TECNICI DA EXCEL
                    # =========================
                    lista_tecnici = df_operatori.apply(
                        lambda x: f"{x['Nominativo']} (Squadra {x['Squadra']})", axis=1
                    )

                    scelta = st.selectbox("Tecnico", lista_tecnici, key=f"t_{i}")
                    tecnico_input = scelta.split(" (")[0]

                    numero_row = df_operatori[df_operatori["Nominativo"] == tecnico_input]
                    numero = numero_row["Codice"].values[0] if not numero_row.empty else None

                    col1, col2, col3 = st.columns(3)

                    # =========================
                    # ASSEGNA
                    # =========================
                    if col1.button(f"Assegna_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "scadenza": scadenza,
                            "componente": r["Componente"],
                            "intervento": r["Intervento"],
                            "link": r.get("Link",""),
                            "tecnico": tecnico_input,
                            "stato": "APERTO",
                            "inizio": ora_italia(),
                            "note": note_input
                        }).execute()

                        st.success("Assegnato")
                        st.rerun()

                    # =========================
                    # WHATSAPP (SEMPRE VISIBILE)
                    # =========================
                    if numero:

                        msg = f"""🚄 NUOVA ATTIVITÀ

👤 Tecnico: {tecnico_input}
🚆 Treno: {treno}
📅 Data: {data_giorno}
⏱️ Scadenza: {scadenza}

🔧 {r['Intervento']}
📦 {r['Componente']}
"""

                        if "Link" in r and pd.notna(r["Link"]):
                            msg += f"\n📄 {r['Link']}"

                        url = f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"

                        st.markdown(f"[📲 Invia WhatsApp]({url})")

                    # =========================
                    # MODIFICA
                    # =========================
                    if col2.button(f"Modifica_{i}") and record:

                        supabase.table("interventi").update({
                            "tecnico": tecnico_input,
                            "note": note_input
                        }).eq("chiave", chiave).execute()

                        st.success("Modificato")
                        st.rerun()

                    # =========================
                    # CANCELLA
                    # =========================
                    if col3.button(f"Cancella_{i}"):

                        supabase.table("interventi").delete().eq("chiave", chiave).execute()

                        st.warning("Cancellato")
                        st.rerun()

    # =========================
    # 👷 OPERATORE
    # =========================
    else:

        st.subheader("📋 Attività assegnate")

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

            colore = "🟡" if record.get("stato") == "APERTO" else "🟢"

            with st.expander(f"{colore} {record.get('componente','')}"):

                st.write(record.get("intervento",""))

                st.write(f"🚆 Treno: {record.get('treno','')}")
                st.write(f"📅 Data: {record.get('data','')}")
                st.write(f"⏱️ Scadenza: {record.get('scadenza','')}")

                if record.get("link"):
                    st.markdown(f"[📄 Apri scheda]({record.get('link')})")

                note_input = st.text_area("Note", value=record.get("note",""), key=f"note_op_{i}")

                inizio = record.get("inizio","")
                st.text_input("Inizio", value=inizio, disabled=True)

                fine_input = st.time_input("Fine", key=f"fine_{i}")

                if st.button(f"Chiudi_{i}"):

                    t1 = datetime.strptime(inizio, "%H:%M")
                    t2 = datetime.strptime(str(fine_input), "%H:%M:%S")

                    durata = str(t2 - t1) if t2 >= t1 else "Errore"

                    supabase.table("interventi").update({
                        "stato": "CHIUSO",
                        "fine": str(fine_input),
                        "durata": durata,
                        "note": note_input
                    }).eq("chiave", record["chiave"]).execute()

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