import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

st.set_page_config(layout="wide")

# =========================
# UTENTI
# =========================

UTENTI = {
    "ivan": {"password": "1234", "ruolo": "CAPOSQUADRA"},
    "marco": {"password": "1111", "ruolo": "OPERATORE"},
    "luca": {"password": "2222", "ruolo": "OPERATORE"}
}

FILE_DB = "database_manutenzione.xlsx"
FILE_SAVE = "assegnazioni.xlsx"

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
# DATI
# =========================

df = pd.read_excel(FILE_DB)
df.columns = df.columns.str.strip()

if "df_save" not in st.session_state:
    if os.path.exists(FILE_SAVE):
        df_save = pd.read_excel(FILE_SAVE)
    else:
        df_save = pd.DataFrame()

    cols = ["Chiave","Treno","Data","Tecnico","Stato","Inizio","Fine","Durata","Note"]

    for c in cols:
        if c not in df_save.columns:
            df_save[c] = ""

    st.session_state.df_save = df_save

df_save = st.session_state.df_save

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
        salvato = df_save[df_save["Chiave"] == chiave]

        tecnico = ""
        stato = "APERTO"
        inizio = ""
        fine = ""
        durata = ""
        note = ""

        if not salvato.empty:
            tecnico = salvato.iloc[0]["Tecnico"]
            stato = salvato.iloc[0]["Stato"]
            inizio = salvato.iloc[0]["Inizio"]
            fine = salvato.iloc[0]["Fine"]
            durata = salvato.iloc[0]["Durata"]
            note = salvato.iloc[0]["Note"]

        if ruolo == "OPERATORE" and tecnico != utente:
            continue

        colore = "🔴" if stato == "APERTO" else "🟢"

        with st.expander(f"{colore} {r['Componente']}"):

            st.write(r["Intervento"])

            if "Link" in r and pd.notna(r["Link"]):
                st.markdown(f"[Apri Scheda]({r['Link']})")

            # STATO
            if stato == "APERTO":
                st.error(f"Stato: {stato}")
            else:
                st.success(f"Stato: {stato}")

            st.write(f"Data: {data_giorno}")
            st.write(f"Inizio: {inizio}")
            st.write(f"Fine: {fine}")
            st.write(f"⏱ Durata: {durata}")

            note_input = st.text_area("Note", value=note, key=f"note_{i}")

            # ======================
            # CAPOSQUADRA
            # ======================
            if ruolo == "CAPOSQUADRA":

                tecnico_input = st.text_input("Tecnico", value=tecnico, key=f"t_{i}")

                col1, col2, col3 = st.columns(3)

                # ASSEGNA
                if col1.button(f"Assegna_{i}"):

                    nuova = pd.DataFrame([{
                        "Chiave": chiave,
                        "Treno": treno,
                        "Data": data_giorno,
                        "Tecnico": tecnico_input,
                        "Stato": "APERTO",
                        "Inizio": datetime.now().strftime("%H:%M"),
                        "Fine": "",
                        "Durata": "",
                        "Note": note_input
                    }])

                    df_save = df_save[df_save["Chiave"] != chiave]
                    df_save = pd.concat([df_save, nuova], ignore_index=True)

                    st.session_state.df_save = df_save
                    df_save.to_excel(FILE_SAVE, index=False)

                    st.success("Assegnato")

                # MODIFICA
                if col2.button(f"Modifica_{i}"):

                    nuova = pd.DataFrame([{
                        "Chiave": chiave,
                        "Treno": treno,
                        "Data": data_giorno,
                        "Tecnico": tecnico_input,
                        "Stato": stato,
                        "Inizio": inizio,
                        "Fine": fine,
                        "Durata": durata,
                        "Note": note_input
                    }])

                    df_save = df_save[df_save["Chiave"] != chiave]
                    df_save = pd.concat([df_save, nuova], ignore_index=True)

                    st.session_state.df_save = df_save
                    df_save.to_excel(FILE_SAVE, index=False)

                    st.success("Modificato")

                # CANCELLA
                if col3.button(f"Cancella_{i}"):

                    df_save = df_save[df_save["Chiave"] != chiave]

                    st.session_state.df_save = df_save
                    df_save.to_excel(FILE_SAVE, index=False)

                    st.warning("Cancellato")

            # ======================
            # OPERATORE
            # ======================
            if ruolo == "OPERATORE":

                st.write(f"Tecnico: {tecnico}")

                st.text_input("Inizio attività", value=inizio, disabled=True)

                fine_input = st.time_input("Fine attività", key=f"f_{i}")

                if st.button(f"Chiudi_{i}"):

                    # CALCOLO DURATA
                    try:
                        t1 = datetime.strptime(inizio, "%H:%M")
                        t2 = datetime.strptime(str(fine_input), "%H:%M:%S")
                        durata_calc = str(t2 - t1)
                    except:
                        durata_calc = ""

                    nuova = pd.DataFrame([{
                        "Chiave": chiave,
                        "Treno": treno,
                        "Data": data_giorno,
                        "Tecnico": utente,
                        "Stato": "CHIUSO",
                        "Inizio": inizio,
                        "Fine": fine_input,
                        "Durata": durata_calc,
                        "Note": note_input
                    }])

                    df_save = df_save[df_save["Chiave"] != chiave]
                    df_save = pd.concat([df_save, nuova], ignore_index=True)

                    st.session_state.df_save = df_save
                    df_save.to_excel(FILE_SAVE, index=False)

                    st.success("Chiuso")