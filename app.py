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
[18:42, 25/03/2026] Ivan Colantuono:         st_autorefresh(interval=8…
[18:48, 25/03/2026] Ivan Colantuono: elif menu == "🚄 Manutenzione":

    st.title("🚄 Gestione Manutenzione")

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

    df.columns = df.columns.str.strip()  # 🔥 IMPORTANTE

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
            scelte = list(df["Scadenza"].unique())

            if st.session_state.scadenza not in scelte:
                st.session_state.scadenza = scelte[0]

            st.session_state.scadenza = st.selectbox(
                "Scadenza",
                scelte,
                index=scelte.index(st.session_state.scadenza)
            )

        st.session_state.data = st.date_input("Data", value=st.session_state.data)

        if st.button("Genera"):

            if not st.session_state.treno or not st.session_state.odl:
                st.error("⚠️ Inserisci Treno e ODL")
            else:
                st.session_state.mostra = True

        if st.session_state.mostra:

            risultati = df[df["Scadenza"] == st.session_state.scadenza]

            for i, r in risultati.iterrows():

                treno = st.session_state.treno
                odl = st.session_state.odl
                data_giorno = st.session_state.data

                chiave = f"{r['Scheda']}{r['Intervento']}{treno}{odl}{data_giorno}"

                rec = next((x for x in rows if x["chiave"] == chiave), None)

                if not rec:
                    colore = "🔴"
                    tecnici = []
                else:
                    colore = "🟡" if rec["stato"] == "APERTO" else "🟢"

                    tecnici = rec.get("tecnico", [])
                    if isinstance(tecnici, str):
                        try:
                            tecnici = ast.literal_eval(tecnici)
                        except:
                            tecnici = [tecnici]

                with st.expander(f"{colore} {r['Componente']}"):

                    st.write(r["Intervento"])

                    # =========================
                    # LINK DINAMICI (FUNZIONA SEMPRE)
                    # =========================
                    link1 = r.get("Link") or r.get("link")
                    link2 = r.get("Link2") or r.get("Link 2") or r.get("link2")

                    if link1:
                        st.markdown(f"[📄 Scheda 1]({link1})")

                    if link2:
                        st.markdown(f"[📄 Scheda 2]({link2})")

                    note = rec.get("note","") if rec else ""
                    note_input = st.text_area("Note", value=note, key=f"note_{i}")

                    tecnici_input = st.multiselect(
                        "Tecnici",
                        operatori,
                        default=tecnici,
                        key=f"tec_{i}"
                    )

                    colA, colB, colC = st.columns(3)

                    # =========================
                    # ASSEGNA (FIX BUG)
                    # =========================
                    if colA.button(f"Assegna_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "odl": odl,
                            "scadenza": st.session_state.scadenza,
                            "data": str(data_giorno),
                            "componente": r["Componente"],
                            "intervento": r["Intervento"],
                            "link": link1,
                            "link2": link2,
                            "tecnico": str(tecnici_input),  # 🔥 FIX
                            "caposquadra": utente,
                            "stato": "APERTO",
                            "inizio": ora_italia(),
                            "note": note_input
                        }).execute()

                        st.success("Assegnato")
                        st.rerun()

                    # =========================
                    # WHATSAPP (TUO + FIX)
                    # =========================
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

🔧 {r['Intervento']}
🔧 {r['Componente']}
"""

                        if link1:
                            msg += f"\n📄 {link1}"

                        if link2:
                            msg += f"\n📄 {link2}"

                        for num in numeri:
                            url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                            st.markdown(f"[📲 Invia WhatsApp a {num}]({url})")

                    # =========================
                    # CANCELLA
                    # =========================
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
                st.write(f"🚆 Treno: {record.get('treno','')}")
                st.write(f"🧾 ODL: {record.get('odl','')}")
                st.write(f"👷 {record.get('caposquadra','')}")

                if record.get("link"):
                    st.markdown(f"[📄 Scheda 1]({record.get('link')})")

                if record.get("link2"):
                    st.markdown(f"[📄 Scheda 2]({record.get('link2')})")

                note_input = st.text_area("Note", key=f"note_op_{i}")
                fine_input = st.time_input("Fine", key=f"fine_{i}")

                if st.button(f"Chiudi_{i}"):

                    nuove_note = f"{record.get('note','')}\n---\n{utente}: {note_input}"

                    supabase.table("interventi").update({
                        "stato": "CHIUSO",
                        "fine": str(fine_input),
                        "note": nuove_note
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