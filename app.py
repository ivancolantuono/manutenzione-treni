import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

st.set_page_config(layout="wide")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("manutenzione.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS interventi (
    chiave TEXT PRIMARY KEY,
    treno TEXT,
    data TEXT,
    tecnico TEXT,
    stato TEXT,
    inizio TEXT,
    fine TEXT,
    durata TEXT,
    note TEXT
)
""")
conn.commit()

# =========================
# UTENTI
# =========================

UTENTI = {
    "IVAN COLANTUONO": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "DANIELE MORELLO": {"password": "1111", "ruolo": "CAPOSQUADRA"},
    "RICCARDO CACACE": {"password": "2222", "ruolo": "CAPOSQUADRA"}
    "CARMINE SANTORELLI": {"password": "3333", "ruolo": "OPERATORE"}
}

# =========================
# LOGIN
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login")

    u = st.text_input("Utente")
    p = st.text_input("Password", type="password")

    if st.button("Accedi"):
        if u in UTENTI and UTENTI[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.utente = u
            st.session_state.ruolo = UTENTI[u]["ruolo"]
            st.rerun()
        else:
            st.error("Errore login")

    st.stop()

# =========================
# LOGOUT
# =========================

if st.button("🔓 Disconnetti"):
    st.session_state.clear()
    st.rerun()

utente = st.session_state.utente
ruolo = st.session_state.ruolo

st.success(f"{utente} - {ruolo}")

# =========================
# CARICA CHECKLIST
# =========================

df = pd.read_excel("database_manutenzione.xlsx")
df.columns = df.columns.str.strip()

# =========================
# INPUT
# =========================

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

# =========================
# LOGICA
# =========================

if st.session_state.get("mostra"):

    risultati = df[df["Scadenza"] == st.session_state.scadenza]

    for i, r in risultati.iterrows():

        chiave = f"{r['Scheda']}_{r['Intervento']}_{treno}_{data_giorno}"

        cursor.execute("SELECT * FROM interventi WHERE chiave=?", (chiave,))
        row = cursor.fetchone()

        tecnico, stato, inizio, fine, durata, note = "", "APERTO", "", "", "", ""

        if row:
            _, _, _, tecnico, stato, inizio, fine, durata, note = row

        if ruolo == "OPERATORE" and tecnico != utente:
            continue

        colore = "🔴" if stato == "APERTO" else "🟢"

        with st.expander(f"{colore} {r['Componente']}"):

            st.write(r["Intervento"])

            if "Link" in r and pd.notna(r["Link"]):
                st.markdown(f"[Apri Scheda]({r['Link']})")

            st.write(f"Stato: {stato}")
            st.write(f"Inizio: {inizio}")
            st.write(f"Fine: {fine}")
            st.write(f"Durata: {durata}")

            note_input = st.text_area("Note", value=note, key=f"note_{i}")

            # ======================
            # CAPO
            # ======================
            if ruolo == "CAPOSQUADRA":

                tecnico_input = st.text_input("Tecnico", value=tecnico, key=f"t_{i}")

                col1, col2, col3 = st.columns(3)

                if col1.button(f"Assegna_{i}"):

                    inizio_now = datetime.now().strftime("%H:%M")

                    cursor.execute("""
                    INSERT OR REPLACE INTO interventi VALUES (?,?,?,?,?,?,?,?,?)
                    """, (chiave, treno, str(data_giorno), tecnico_input,
                          "APERTO", inizio_now, "", "", note_input))

                    conn.commit()
                    st.success("Assegnato")

                if col2.button(f"Modifica_{i}"):

                    cursor.execute("""
                    INSERT OR REPLACE INTO interventi VALUES (?,?,?,?,?,?,?,?,?)
                    """, (chiave, treno, str(data_giorno), tecnico_input,
                          stato, inizio, fine, durata, note_input))

                    conn.commit()
                    st.success("Modificato")

                if col3.button(f"Cancella_{i}"):

                    cursor.execute("DELETE FROM interventi WHERE chiave=?", (chiave,))
                    conn.commit()
                    st.warning("Cancellato")

            # ======================
            # OPERATORE
            # ======================
            if ruolo == "OPERATORE":

                st.write(f"Tecnico: {tecnico}")

                st.text_input("Inizio attività", value=inizio, disabled=True)

                fine_input = st.time_input("Fine", key=f"f_{i}")

                if st.button(f"Chiudi_{i}"):

                    try:
                        t1 = datetime.strptime(inizio, "%H:%M")
                        t2 = datetime.strptime(str(fine_input), "%H:%M:%S")
                        durata_calc = str(t2 - t1)
                    except:
                        durata_calc = ""

                    cursor.execute("""
                    INSERT OR REPLACE INTO interventi VALUES (?,?,?,?,?,?,?,?,?)
                    """, (chiave, treno, str(data_giorno), utente,
                          "CHIUSO", inizio, str(fine_input), durata_calc, note_input))

                    conn.commit()
                    st.success("Chiuso")