import streamlit as st
import pandas as pd
from datetime import date, datetime
from supabase import create_client
import urllib.parse

# =========================
# CONFIG
# =========================

st.set_page_config(layout="wide")

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
# LOGIN CENTRATO
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
# MENU PRINCIPALE
# =========================

menu = st.radio(
    "Seleziona sezione",
    ["📊 Storico", "🚄 Manutenzione", "📦 Magazzino"],
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
# 📊 STORICO
# =========================

if menu == "📊 Storico":

    st.title("📊 Storico Attività")

    df_storico = pd.DataFrame(rows)

    if not df_storico.empty:
        st.dataframe(df_storico, use_container_width=True)
    else:
        st.warning("Nessun dato presente")

# =========================
# 🚄 MANUTENZIONE
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
        st.session_state.mostra = True
        st.session_state.scadenza = scadenza

    # DASHBOARD
    aperte = sum(1 for r in rows if r["stato"] == "APERTO")
    chiuse = sum(1 for r in rows if r["stato"] == "CHIUSO")

    d1, d2 = st.columns(2)
    d1.metric("🔴 Aperte", aperte)
    d2.metric("🟢 Chiuse", chiuse)

    st.divider()

    if st.session_state.get("mostra"):

        risultati = df[df["Scadenza"] == st.session_state.scadenza]

        for i, r in risultati.iterrows():

            chiave = f"{r['Scheda']}_{r['Intervento']}_{treno}_{data_giorno}"

            record = next((x for x in rows if x["chiave"] == chiave), None)

            tecnico = record["tecnico"] if record else ""
            stato = record["stato"] if record else "APERTO"
            inizio = record["inizio"] if record else ""
            fine = record["fine"] if record else ""
            durata = record["durata"] if record else ""
            note = record["note"] if record else ""

            if ruolo == "OPERATORE" and tecnico != utente:
                continue

            colore = "🔴" if stato == "APERTO" else "🟢"

            with st.expander(f"{colore} {r['Componente']}"):

                st.write(r["Intervento"])

                if "Link" in r:
                    st.markdown(f"[Apri Scheda]({r['Link']})")

                st.write(f"Stato: {stato}")
                st.write(f"Inizio: {inizio}")
                st.write(f"Fine: {fine}")
                st.write(f"Durata: {durata}")

                note_input = st.text_area("Note", value=note, key=f"note_{i}")

                # CAPO
                if ruolo == "CAPOSQUADRA":

                    tecnico_input = st.text_input("Tecnico", value=tecnico, key=f"t_{i}")

                    if st.button(f"Assegna_{i}"):

                        supabase.table("interventi").upsert({
                            "chiave": chiave,
                            "treno": treno,
                            "data": str(data_giorno),
                            "tecnico": tecnico_input,
                            "stato": "APERTO",
                            "inizio": datetime.now().strftime("%H:%M"),
                            "note": note_input
                        }).execute()

                        # WHATSAPP
                        numero = NUMERI.get(tecnico_input.lower(), "")
                        if numero:
                            msg = f"Nuova attività 🚄\n{r['Intervento']}"
                            url = f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"
                            st.markdown(f"[📱 Avvisa operatore]({url})")

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

# =========================
# 📦 MAGAZZINO
# =========================

elif menu == "📦 Magazzino":

    st.title("📦 Ricerca Componenti")

    ricerca = st.text_input("Cerca componente")

    if ricerca:
        risultati = df[df["Componente"].str.contains(ricerca, case=False, na=False)]
        st.dataframe(risultati, use_container_width=True)