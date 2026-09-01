import streamlit as st
import pandas as pd
import requests
from streamlit_pdf_viewer import pdf_viewer
import os
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from zoneinfo import ZoneInfo
from permessi import pagina_permessi
from datetime import date, datetime
from db import supabase
from planning import planning_page
from open import openitem_page
from Passaggio_consegne import Passaggio_consegne_page
from db import get_utenti
from db import get_operatori
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from misurazione_sensori import misurazione_sensori_page
from carrelli import carrelli_page
from analizza import analizza_page
import urllib.parse

st.set_page_config(
    page_title="Manager ETR1000",
    page_icon="🚅",
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

/* Nasconde decorazione rossa */
[data-testid="stDecoration"] {
    display:none;
}

/* Nasconde footer */
footer {
    visibility:hidden;
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

cell_renderer = JsCode("""
class UrlCellRenderer {
    init(params) {

        if (params.value == null || params.value == "") {
            this.eGui = document.createElement('span');
            this.eGui.innerText = "";
            return;
        }

        this.eGui = document.createElement('a');

        this.eGui.innerText = params.value;

        this.eGui.href = params.data.link;

        this.eGui.target = "_blank";

        this.eGui.style.color = "#0066cc";
        this.eGui.style.fontWeight = "bold";
        this.eGui.style.textDecoration = "none";
    }

    getGui() {
        return this.eGui;
    }
}
""")

URL_PIS = "https://nlsezrwjvhxvsbycxlxd.supabase.co/storage/v1/object/public/software/Versioni%20PIS.xlsx"

@st.cache_data(ttl=5)
def carica_pis():
    df = pd.read_excel(URL_PIS)
    # Elimina eventuali spazi nelle intestazioni
    df.columns = df.columns.astype(str).str.strip()
    return df

@st.cache_data(ttl=5)
def get_interventi():
    res = supabase.table("interventi").select("*").execute()
    return res.data or []

# =========================
# ORAIO
# =========================
def ora_italia():
    return datetime.now(ZoneInfo("Europe/Rome")).strftime("%H:%M")
# =========================
# 🔐 LOGIN + REGISTRAZIONE
# =========================

import hashlib
import secrets
import extra_streamlit_components as stx

# ==========================================================
# COOKIE
# ==========================================================

cookie_manager = stx.CookieManager(
    key="manager_etr1000_cookie_manager"
)
COOKIE_LOGIN = "manager_etr1000_matricola"
# ==========================================================
# UTILS
# ==========================================================

def hash_password(pwd):
    return hashlib.sha256(
        pwd.encode()
    ).hexdigest()

def format_nome(txt):
    return str(txt or "").strip().capitalize()

def norm(x):
    return str(x or "").strip().lower()

# ==========================================================
# SESSION STATE
# ==========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "utente" not in st.session_state:
    st.session_state.utente = ""

if "matricola" not in st.session_state:
    st.session_state.matricola = ""

if "ruolo" not in st.session_state:
    st.session_state.ruolo = ""

if "squadra" not in st.session_state:
    st.session_state.squadra = ""

# ==========================================================
# 🔄 RIPRISTINO LOGIN DAL COOKIE
# ==========================================================

if not st.session_state.logged_in:

    try:

        matricola_cookie = cookie_manager.get(
            COOKIE_LOGIN
        )

        if matricola_cookie:

            matricola = norm(
                matricola_cookie
            )

            # ==============================================
            # CERCA UTENTE
            # ==============================================

            res = (
                supabase
                .table("login")
                .select("*")
                .eq(
                    "matricola",
                    matricola
                )
                .limit(1)
                .execute()
            )

            utenti = res.data or []

            if utenti:

                user = utenti[0]

                # ==========================================
                # RECUPERA OPERATORE
                # ==========================================

                op = (
                    supabase
                    .table("operatori")
                    .select("*")
                    .eq(
                        "Matricola",
                        matricola
                    )
                    .limit(1)
                    .execute()
                )

                if op.data:

                    nome = op.data[0].get(
                        "Nominativo",
                        ""
                    )

                else:

                    nome = user.get(
                        "nome",
                        ""
                    )

                # ==========================================
                # RIPRISTINA SESSIONE
                # ==========================================

                st.session_state.logged_in = True

                st.session_state.matricola = matricola

                st.session_state.utente = nome

                st.session_state.ruolo = user.get(
                    "ruolo",
                    "OPERATORE"
                )

                st.session_state.squadra = user.get(
                    "squadra",
                    ""
                )

            else:

                # Cookie non valido
                try:

                    cookie_manager.delete(
                        COOKIE_LOGIN
                    )

                except:

                    pass

    except Exception:

        pass

# ==========================================================
# BLOCCO LOGIN
# ==========================================================

if not st.session_state.logged_in:

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        st.image(
            "frecciarossa.jpg",
            width=2000
        )
        # ==========================================================
        # 🔄 REDIRECT DOPO OPERAZIONE
        # ==========================================================
        
        if st.session_state.get("redirect_login", False):
            st.session_state.pagina_login = "🔐Login"
            st.session_state.redirect_login = False

        pagina = st.segmented_control(
            "",
            [
                "🔐Login",
                "🆕Registrazione",
                "🔑Reset Password"
            ],
            default="🔐Login",
            key="pagina_login"
        )

        # ==================================================
        # 🔐 LOGIN
        # ==================================================

        if pagina == "🔐Login":

            st.markdown(
                "## 🔐 Login"
            )

            matricola = norm(
                st.text_input(
                    "Matricola"
                )
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            if st.button(
                "**Accedi**",
                use_container_width=True
            ):

                if not matricola or not password:

                    st.error(
                        "❌ Inserisci matricola e password."
                    )

                    st.stop()

                try:

                    # --------------------------------------
                    # CERCA UTENTE
                    # --------------------------------------

                    res = (
                        supabase
                        .table("login")
                        .select("*")
                        .eq(
                            "matricola",
                            matricola
                        )
                        .execute()
                    )

                    utenti = res.data or []

                    user = next(
                        (
                            x
                            for x in utenti
                            if norm(
                                x.get("matricola")
                            ) == matricola
                            and x.get("password")
                            == hash_password(
                                password
                            )
                        ),
                        None
                    )

                    if not user:

                        st.error(
                            "❌ Credenziali errate"
                        )

                        st.stop()

                    # --------------------------------------
                    # RECUPERA OPERATORE
                    # --------------------------------------

                    op = (
                        supabase
                        .table("operatori")
                        .select("*")
                        .eq(
                            "Matricola",
                            matricola
                        )
                        .execute()
                    )

                    if op.data:

                        nome = op.data[0].get(
                            "Nominativo"
                        )

                    else:

                        nome = user.get(
                            "nome"
                        )

                    # ==================================================
                    # 🍪 SALVA MATRICOLA NEL COOKIE
                    # ==================================================
                    
                    cookie_manager.set(
                        COOKIE_LOGIN,
                        matricola,
                        expires_at=datetime(
                            2099,
                            12,
                            31
                        )
                    )
                    # --------------------------------------
                    # SESSION STATE
                    # --------------------------------------

                    st.session_state.logged_in = True

                    st.session_state.login_time = datetime.now()

                    st.session_state.matricola = matricola

                    st.session_state.utente = nome

                    st.session_state.ruolo = user.get(
                        "ruolo",
                        "OPERATORE"
                    )

                    st.session_state.squadra = user.get(
                        "squadra",
                        ""
                    )

                    st.success(
                        "✅ Accesso riuscito"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ Errore durante il login."
                    )

                    st.code(
                        str(e)
                    )

        # ==================================================
        # 🆕 REGISTRAZIONE
        # ==================================================

        elif pagina == "🆕Registrazione":

            st.markdown(
                "## 🆕 Registrazione"
            )

            nome = st.text_input(
                "Nome"
            )

            cognome = st.text_input(
                "Cognome"
            )

            email = st.text_input(
                "Email"
            )

            matricola = norm(
                st.text_input(
                    "Matricola"
                )
            )

            ruolo = st.selectbox(
                "Ruolo",
                [
                    "OPERATORE",
                    "CAPOSQUADRA"
                ]
            )

            squadra = st.selectbox(
                "Squadra",
                [
                    "1-COR-H24",
                    "2-COR-H24",
                    "3-COR-H24",
                    "4-COR-H24",
                    "5-COR-H24",
                    "1-PRO-H24",
                    "2-PRO-H24",
                    "3-PRO-H24",
                    "4-PRO-H24",
                    "5-PRO-H24",
                    "INGEGNERIA"
                ]
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            if st.button(
                "Registrati",
                use_container_width=True
            ):

                if not nome or not cognome or not email or not matricola or not password:

                    st.error(
                        "Compila tutti i campi"
                    )

                    st.stop()

                try:

                    esiste = (
                        supabase
                        .table("login")
                        .select("matricola")
                        .eq(
                            "matricola",
                            matricola
                        )
                        .execute()
                    )

                    if esiste.data:

                        st.error(
                            "Matricola già registrata"
                        )

                        st.stop()

                    supabase.table(
                        "login"
                    ).insert({

                        "nome":
                            format_nome(nome),

                        "cognome":
                            format_nome(cognome),

                        "email":
                            email,

                        "matricola":
                            matricola,

                        "password":
                            hash_password(
                                password
                            ),

                        "ruolo":
                            ruolo,

                        "squadra":
                            squadra,

                        "session_token":
                            None

                    }).execute()

                    op = (
                        supabase
                        .table("operatori")
                        .select("Matricola")
                        .eq(
                            "Matricola",
                            matricola
                        )
                        .execute()
                    )

                    if not op.data:

                        supabase.table(
                            "operatori"
                        ).insert({

                            "Matricola":
                                matricola,

                            "Nominativo":
                                f"{format_nome(cognome)} "
                                f"{format_nome(nome)}",

                            "Telefono":
                                ""

                        }).execute()

                    get_operatori.clear()

                    st.success(
                        "✅ Registrazione completata!"
                    )

                    st.session_state.redirect_login = True

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Errore: {e}"
                    )

        # ==================================================
        # 🔑 RESET PASSWORD
        # ==================================================

        elif pagina == "🔑Reset Password":

            st.markdown(
                "## 🔑 Reset Password"
            )

            matricola = norm(
                st.text_input(
                    "Matricola"
                )
            )

            nuova_password = st.text_input(
                "Nuova Password",
                type="password"
            )

            if st.button(
                "Reimposta Password",
                use_container_width=True
            ):

                if not matricola or not nuova_password:

                    st.error(
                        "Inserisci tutti i campi"
                    )

                    st.stop()

                try:

                    res = (
                        supabase
                        .table("login")
                        .select("*")
                        .eq(
                            "matricola",
                            matricola
                        )
                        .execute()
                    )

                    if not res.data:

                        st.error(
                            "Matricola non trovata"
                        )

                        st.stop()

                    (
                        supabase
                        .table("login")
                        .update({

                            "password":
                                hash_password(
                                    nuova_password
                                ),

                            # --------------------------------
                            # INVALIDA EVENTUALI SESSIONI
                            # --------------------------------
                            "session_token":
                                None

                        })
                        .eq(
                            "matricola",
                            matricola
                        )
                        .execute()
                    )

                    # --------------------------------------
                    # ELIMINA COOKIE
                    # --------------------------------------

                    try:

                        cookie_manager.delete(
                            "manager_etr1000_login"
                        )

                    except:
                        pass

                    st.success(
                        "✅ Password aggiornata!"
                    )

                    st.session_state.logged_in = False

                    st.session_state.redirect_login = True
                    
                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Errore: {e}"
                    )

    st.stop()
# =========================
# DOPO LOGIN
# =========================

utente = st.session_state.get("utente", "")
ruolo = str(st.session_state.get("ruolo", "")).upper()
modalita = st.session_state.get("modalita", ruolo)

# =========================
# 📌 MENU LATERALE
# =========================

with st.sidebar:

    st.markdown("## 🚄 MANAGER ETR1000")
    st.divider()

    st.markdown("### BENVENUTO")
    st.markdown(f"### 👤 {utente}")

    st.divider()

    # =====================================================
    # 👨‍✈️ CAPOSQUADRA
    # =====================================================

    if modalita == "CAPOSQUADRA":

        # -------------------------------------------------
        # MENU PRINCIPALE
        # -------------------------------------------------

        menu = option_menu(
            None,
            [
                "Open Item",
                "Cerca Componente",
                "Manutenzione",
                "Passaggio Consegne",
                "Schede SR",
                "Schede SR VZI6",
                "Planning",
                "Dashboard",
                "Storico",
                "Ferie e Permessi",
                "Scadenze Temporali",
                "Software",
                "Treno"
            ],

            icons=[
                "pin-angle-fill",
                "search",
                "tools",
                "database",
                "folder",
                "folder",
                "journal-text",
                "bar-chart",
                "clock-history",
                "calendar-heart",
                "alarm",
                "cpu",
                "train-front"
            ],

            menu_icon="list",
            default_index=0,

            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "#fafafa"
                },

                "icon": {
                    "color": "#000000",
                    "font-size": "18px"
                },

                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "2px",
                    "--hover-color": "#f3f3f3",
                },

                "nav-link-selected": {
                    "background-color": "#d40000",
                    "color": "white",
                },
            },
        )

        # =================================================
        # 🚆 SOTTOMENU TRENO
        # =================================================

         
        if menu == "Treno":

            st.markdown(
                """
                <div style="
                    margin-top:5px;
                    margin-bottom:5px;
                    padding-left:10px;
                    font-weight:bold;
                    font-size:15px;
                ">
                    🚆 SISTEMI TRENO
                </div>
                """,
                unsafe_allow_html=True
            )

            sistema_treno = st.radio(
                "",
                [
                    "Carrelli",
                    "HVAC",
                    "Misurazione Sensori",
                    "Analizza Log FDE"
                ],
                key="sistema_treno",
                label_visibility="collapsed"
            )

        else:

            sistema_treno = st.session_state.get(
                "sistema_treno",
                "Carrelli"
            )
    # =====================================================
    # 👀 SUPERVISORE
    # =====================================================

    elif modalita == "SUPERVISORE":

        menu = option_menu(
            None,
            [
                "Controllo Permessi"
            ],
            icons=[
                "clipboard-check"
            ],
            default_index=0,
        )

    # =====================================================
    # 👷 OPERATORE
    # =====================================================

    else:

        menu = option_menu(
            None,
            [
                "Open Item",
                "Schede SR",
                "Schede SR VZI6",
                "Manutenzione",
                "Cerca Componente",
                "Ferie e Permessi",
                "Scadenze Temporali",
                "Versioni Software",
                "Treno"
            ],

            icons=[
                "pin-angle-fill",
                "journal-text",
                "journal-code",
                "train-front",
                "search",
                "calendar-heart",
                "alarm",
                "cpu",
                "train-front"
            ],

            default_index=0,
        )

        # =================================================
        # 🚆 SOTTOMENU TRENO
        # =================================================

        if menu == "Treno":

            st.markdown(
                """
                <div style="
                    margin-top:5px;
                    margin-bottom:5px;
                    padding-left:10px;
                    font-weight:bold;
                    font-size:15px;
                ">
                    🚆 SISTEMI TRENO
                </div>
                """,
                unsafe_allow_html=True
            )

            sistema_treno = st.radio(
                "",
                [
                    "Carrelli",
                    "HVAC",
                    "Misurazione Sensori",
                    "Analizza Log FDE"
                ],
                key="sistema_treno",
                label_visibility="collapsed"
            )

        else:

            sistema_treno = st.session_state.get(
                "sistema_treno",
                "Carrelli"
            )

    # =====================================================
    # SEPARATORE
    # =====================================================

    st.divider()

    # =====================================================
    # 🔓 LOGOUT
    # =====================================================

    if st.button(
        "🔓 Logout",
        use_container_width=True
    ):

        try:

            matricola = st.session_state.get(
                "matricola"
            )

            if matricola:

                supabase.table(
                    "login"
                ).update({
                    "session_token": None
                }).eq(
                    "matricola",
                    matricola
                ).execute()

            cookie_manager.delete(
                "manager_etr1000_login"
            )

        except:
            pass

        st.session_state.clear()

        st.rerun()
# =========================
# 📥 CARICA DATABASE (SUPABASE)
# =========================
@st.cache_data(ttl=60)
def get_database_manutenzione():
    res = supabase.table("database_manutenzione").select("*").execute()
    return res.data or []

def load_database():
    return get_database_manutenzione()

def load_operatori():
    return get_operatori()

def load_interventi():
    return get_interventi()

# 👉 converte in DataFrame
rows_db = load_database()
df = pd.DataFrame(rows_db)

# 👉 sicurezza colonne
if not df.empty:
    df.columns = df.columns.str.strip()
rows = load_interventi()

# =========================
# 👷 OPERATORI DA SUPABASE
# =========================

operatori_db = load_operatori()

operatori = [
    o.get("Nominativo")
    for o in operatori_db
    if o.get("Nominativo")
]

if "mostra" not in st.session_state:
    st.session_state["mostra"] = False

if menu == "Storico":

    st.title("📊 Storico Attività")

    # 🔥 RICARICA DATI SEMPRE
    rows = load_interventi()

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
elif menu == "Manutenzione":
    
    st_autorefresh(interval=15000, key="refresh_manutenzione")

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
    
    operatori = [
        o.get("Nominativo")
        for o in operatori_db
        if o.get("Nominativo")
    ]
    
    # =========================
    # 👨‍🔧 CAPOSQUADRA
    # =========================
    if modalita == "CAPOSQUADRA":

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

            if "treno_old" not in st.session_state:
                st.session_state.treno_old = st.session_state.treno
            
            if "odl_old" not in st.session_state:
                st.session_state.odl_old = st.session_state.odl
            
            if (
                st.session_state.treno != st.session_state.treno_old
                or st.session_state.odl != st.session_state.odl_old
            ):
                st.session_state.mostra = False
            
            st.session_state.treno_old = st.session_state.treno
            st.session_state.odl_old = st.session_state.odl
    
            with col3:
                if "Scadenza" not in df.columns or df.empty:
                    st.error("Database manutenzione vuoto o colonna 'Scadenza' mancante")
                    st.stop()
                
                scelte = sorted(df["Scadenza"].dropna().unique())

                if not scelte:
                    st.warning("⚠️ Nessuna scadenza disponibile")
                    st.stop()
                
                # 🔥 indice safe
                try:
                    idx = scelte.index(st.session_state.scadenza)
                except:
                    idx = 0
                    st.session_state.scadenza = scelte[0]
                
                st.session_state.scadenza = st.selectbox(
                    "📋 Scadenza",
                    scelte,
                    index=idx
                )
                # 🔥 RESET AUTO REFRESH

                if "scadenza_old" not in st.session_state:
                    st.session_state.scadenza_old = st.session_state.scadenza
                if st.session_state.scadenza != st.session_state.scadenza_old:
                    st.session_state.mostra = False
                st.session_state.scadenza_old = st.session_state.scadenza
    
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
            interventi_db = supabase.table("interventi").select("*").execute().data or []
    
            for i, r in risultati.iterrows():
    
                treno = st.session_state.treno
                odl = st.session_state.odl
                data_giorno = st.session_state.data
    
                # ✅ CHIAVE UNICA
                chiave = f"{r['Scheda']}|{r['Intervento']}|{treno}|{odl}|{data_giorno}"
    
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

                    nome_scheda = r.get("Scheda", "Scheda")

                    for link in links:
                        link = link.strip()
                        if link:
                            st.markdown(f"[📄 {nome_scheda}]({link})")
                                        
                    # =========================
                    # 📝 NOTE
                    # =========================
                    note = record.get("note", "") if record else ""
                    st.write(note if note else "—")

                    # =========================
                    # 👷 TECNICI
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
                    # 📲 WHATSAPP (SUBITO VISIBILE)
                    # =========================
                    numeri = []

                    for t in tecnici_input:
                        op = next(
                            (o for o in operatori_db if o.get("Nominativo") == t),
                            None
                        )

                        if op:
                            telefono = str(op.get("Telefono","")).replace(".0","").strip()

                            # 🔥 pulizia numero
                            telefono = "".join(filter(str.isdigit, telefono))

                            # 🔥 prefisso Italia
                            if telefono and not telefono.startswith("39"):
                                telefono = "39" + telefono

                            if telefono:
                                numeri.append(telefono)

                    # 👉 MOSTRA SUBITO I BOTTONI
                    if numeri:

                        links = str(link_raw).split("|") if link_raw else []

                        nome_scheda = r.get("Scheda", "Scheda")

                        schede_txt = ""

                        for link in links:

                            link = link.strip()

                            if link:

                                schede_txt += f"{nome_scheda}\n{link}\n\n"

                        msg = f"""🚄 NUOVA ATTIVITÀ

🚆 Treno: {treno}
🧾 ODL: {odl}
📅 Data: {data_giorno}
⏱️ Scadenza: {st.session_state.scadenza}

👷 Caposquadra: {utente}

🔧 {r['Intervento']}
🔧 {r['Componente']}

📄 Scheda tecnica:

{schede_txt}

"""
                        for num in numeri:
                            url = f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"
                            st.link_button(f"📲 Invia a {num}", url)

                    # =========================
                    # BOTTONI AZIONE
                    # =========================
                    colA, colB, colC = st.columns(3)

                    # 🔧 ASSEGNA
                    if colA.button("🔧 Assegna", key=f"assegna_{i}"):

                        if not tecnici_input:
                            st.error("Seleziona almeno un tecnico")
                            st.stop()

                        matricole = []

                        for t in tecnici_input:
                            op = next(
                                (o for o in operatori_db if o.get("Nominativo") == t),
                                None
                            )

                            if op:
                                matricola = str(op.get("Matricola","")).strip().lower()
                                if matricola:
                                    matricole.append(matricola)

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
                            "tecnico": str(matricole),   # 🔥 matricole pulite
                            "caposquadra": str(utente),
                            "stato": "APERTO",
                            "inizio": str(ora_italia()),
                            "note": note_vecchie
                        }).execute()

                        get_interventi.clear()
                        st.success("Assegnato")
                        st.rerun()

                    # 🗑️ CANCELLA
                    if colB.button("🗑️ Cancella", key=f"cancella_{i}"):
                        supabase.table("interventi").delete().eq("chiave", chiave).execute()
                        get_interventi.clear()
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

                            get_interventi.clear()
                            st.success("Chiusa")
                            st.rerun()
    # =========================
    # 👷 OPERATORE
    # =========================
    else:

        st.subheader("📋 Attività assegnate")

        risultati = []

        matricola_utente = str(st.session_state.get("matricola","")).strip().lower()

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

                    get_interventi.clear()
                    st.success("Attività chiusa")
                    st.rerun()
    
elif menu == "Dashboard":

    import ast

    st.title("📊 Dashboard Caposquadra")
    
    df = pd.DataFrame(rows)

    if df.empty:
        st.warning("Nessuna attività")
        st.stop()

    # =========================
    # 🔁 MAPPA MATRICOLA → NOME
    # =========================
   
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
elif menu == "Cerca Componente":

    import pandas as pd
    import re

    st.title("⚙️ Cerca componente")

    if "admin_componenti" not in st.session_state:
        st.session_state.admin_componenti = False
    
    if not st.session_state.admin_componenti:
    
        with st.expander("**🔒 Area amministratore**"):
    
            pwd = st.text_input(
                "LA TUA PASSWORD",
                type="password"
            )
    
            if st.button("Accedi"):
    
                if pwd == "280188":
                    st.session_state.admin_componenti = True
                    st.rerun()
                else:
                    st.error("Password errata")

    # =========================
    # 📥 CARICAMENTO COMPLETO + COLONNA SEARCH
    # =========================
    @st.cache_data(ttl=5)
    def carica_magazzino():

        dati = []
        step = 1000
        start = 0

        while True:
            res = supabase.table("magazzino").select("*").order("id").range(start, start + step - 1).execute()

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
    
    # 👉 filtro unico
    assiemi = sorted(df_mag["assieme"].dropna().unique())
    filtro_assieme = st.multiselect("📦 Assieme", assiemi)
    
    risultati = df_mag.copy()
    
    # 🔍 ricerca
    if ricerca:
        ricerca_norm = ricerca.lower().strip()
        ricerca_norm = ricerca_norm.replace("_", " ").replace("-", " ")
    
        risultati = risultati[
            risultati["search"].str.contains(ricerca_norm, na=False)
        ]
    
    # 📦 filtro assieme
    if filtro_assieme:
        risultati = risultati[risultati["assieme"].isin(filtro_assieme)]
    
    # totale SEMPRE fuori
    totale = len(risultati)
    
    # =========================
    # LIMITA RISULTATI
    # =========================
    risultati = risultati.head(limite)
    
    st.markdown(f"🔎 Trovati: {totale} | Mostrati: {len(risultati)}")
    
    if risultati.empty:
        st.warning("Nessun risultato trovato")
        st.stop()

    if st.session_state.admin_componenti:
    
        st.divider()
    
        if st.button("➕ Nuovo componente"):
            st.session_state.nuovo = True

    if st.session_state.get("nuovo", False):

        st.subheader("➕ Nuovo componente")   
        elemento = st.text_input("Elemento")
        assieme = st.text_input("Assieme")
        componente = st.text_input("Componenete")
        part_number = st.text_input("Part Number")
        
    
        if st.button("💾 Salva componente"):
            supabase.table("magazzino").insert({
            "ELEMENTO": elemento,
            "ASSIEME": assieme,
            "COMPONENTE": componente,
            "Part_Number": part_number,
        }).execute()
            st.success("✅ Componente inserito")

            st.session_state.nuovo = False

            st.cache_data.clear()
            st.session_state.magazzino = carica_magazzino()

            st.rerun()
        
    # =========================
    # 📄 TABELLA
    # =========================
    evento = st.dataframe(
        risultati.drop(columns=["search", "id"]),
        use_container_width=True,
        height=500,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    st.caption("🔍 Ricerca veloce su tutto il catalogo")

    if st.session_state.admin_componenti:
    
        righe = evento.selection.rows
    
        if righe:
    
            indice = righe[0]
    
            r = risultati.iloc[indice]
    
            st.divider()
    
            st.subheader("✏️ Modifica componente")
            elemento = st.text_input(
                "Elemento",
                value=r["elemento"],
                key="mod_elemento"
            )
            
            assieme = st.text_input(
                "Assieme",
                value=r["assieme"],
                key="mod_assieme"
            )
            
            componente = st.text_input(
                "Componente",
                value=r["componente"],
                key="mod_componente"
            )
            
            part_number = st.text_input(
                "Part Number",
                value=r["part_number"],
                key="mod_part"
            )

            col1, col2 = st.columns(2)

            with col1:
            
                if st.button("💾 Salva modifiche", type="primary"):
                
                    supabase.table("magazzino").update({
                
                        "ELEMENTO": elemento,
                        "ASSIEME": assieme,
                        "COMPONENTE": componente,
                        "Part_Number": part_number
                
                    }).eq(
                        "id",
                        int(r["id"])
                    ).execute()
                    st.success("✅ Componente aggiornato")
                    st.cache_data.clear()
                    st.session_state.magazzino = carica_magazzino()
                    st.rerun()
    
            
            with col2:
               
                if st.button("🗑️ Elimina componente", type="secondary"):
                
                    supabase.table("magazzino")\
                        .delete()\
                        .eq("id", int(r["id"]))\
                        .execute()
                
                    st.success("🗑️ Componente eliminato")
                
                    st.cache_data.clear()
                    st.session_state.magazzino = carica_magazzino()
                    st.rerun()

# =========================
# 📚 SCHEDE SR (SUPABASE)
# =========================
elif menu == "Schede SR":

    import pandas as pd
    import re

    st.title("📇 Ricerca Schede SR")

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
            
elif menu == "Open Item":
    openitem_page()

                
# =========================
# 📚 SCHEDE SR VZI6 (SUPABASE)
# =========================
elif menu == "Schede SR VZI6":

    import pandas as pd
    import re

    st.title("📇 Ricerca Schede SR VZI6")

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
        with st.spinner("🔄 Caricamento schede SR VZI6..."):
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

elif menu == "Planning":
    planning_page()

elif menu == "Ferie e Permessi":

    pagina_permessi(
        supabase,
        utente        
    )
    
elif menu == "📊 CONTROLLO PERMESSI":

    st.title("📊 Controllo Permessi")

    col1, col2 = st.columns(2)

    with col1:
        data_da = st.date_input(
            "Da",
            key="sup_da"
        )

    with col2:
        data_a = st.date_input(
            "A",
            key="sup_a"
        )

    richieste = supabase.table(
        "richieste_permessi"
    ).select("*").execute().data

    richieste = [
        r for r in richieste
        if r.get("stato") in [
            "APPROVATO",
            "RIFIUTATO"
        ]
    ]

    filtrate = []

    for r in richieste:

        try:

            data_richiesta = datetime.fromisoformat(
                r["data_richiesta"]
            ).date()

            if data_da <= data_richiesta <= data_a:
                filtrate.append(r)

        except:
            pass

    df = pd.DataFrame(filtrate)

    st.dataframe(
        df,
        use_container_width=True
    )
    import io 
    if not df.empty:

        colonne = [
            "utente",
            "squadra",
            "tipo",
            "data_inizio",
            "data_fine",
            "stato",
            "approvato_da",
            "data_richiesta",
            "data_approvazione",
            "motivo_rifiuto"
        ]
    
        colonne_presenti = [
            c for c in colonne
            if c in df.columns
        ]
    
        df_export = df[colonne_presenti]
    
        buffer = io.BytesIO()
    
        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:
    
            df_export.to_excel(
                writer,
                index=False,
                sheet_name="Permessi"
            )
    
        st.download_button(
            "📥 Scarica Excel",
            data=buffer.getvalue(),
            file_name=f"permessi_{data_da}_{data_a}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
elif menu == "Scadenze Temporali":

    st.title("📚 SCADENZE")

    piani = {
        "F0": "https://nlsezrwjvhxvsbycxlxd.supabase.co/storage/v1/object/public/manuali/F0_PdM_rev.05.pdf",
        "F1": "https://nloezrwjvhxvsbycxlxd.supabase.co/storage/v1/object/public/manuali/F1.pdf",
        "F2": "https://nloezrwjvhxvsbycxlxd.supabase.co/storage/v1/object/public/manuali/F2.pdf",
        "F3": "https://nloezrwjvhxvsbycxlxd.supabase.co/storage/v1/object/public/manuali/F3.pdf",
        "F4": "https://nloezrwjvhxvsbycxlxd.supabase.co/storage/v1/object/public/manuali/F4.pdf",
    }

    cols = st.columns(4)

    for i, nome in enumerate(piani.keys()):

        with cols[i % 4]:

            if st.button(nome, use_container_width=True):

                st.session_state["pdf_piano"] = piani[nome]
                st.session_state["nome_piano"] = nome

    if "pdf_piano" in st.session_state:

        st.divider()

        st.subheader(f"📄 SCADENZA {st.session_state['nome_piano']}")

        st.link_button(
            "🔗 Apri in una nuova scheda",
            st.session_state["pdf_piano"]
        )

        try:

            response = requests.get(
                st.session_state["pdf_piano"]
            )

            if response.status_code == 200:

                pdf_viewer(
                    response.content,
                    width="100%"
                )

            else:

                st.error("Impossibile caricare il PDF.")

        except Exception as e:

            st.error(e)
            
elif menu == "Software":

    st.title("📺 Software")

    df = carica_pis()

    if df.empty:
        st.warning("Nessun dato trovato.")
        st.stop()

    treno = st.selectbox(
        "🚄 Seleziona il treno",
        sorted(df["Treno"].unique())
    )

    dati = df[df["Treno"] == treno].iloc[0]

    software = [
        ("📺 DOVE 6", dati["Versione DOVE 6"], dati["link dove 6"]),
        ("🖥️ ONM100", dati["Versione ONM 100"], dati["link onm 100"]),
        ("🎥 DVR", dati["Versione DVR"], dati["link DVR"]),
        ("💻 PC PANEL", dati["Versione PC Panel"], dati["link PC Panel"]),
        ("📡 CAB RADIO", dati["Versione CAB RADIO"], None),
        ("❄️ HVAC", dati["Versione HVAC"], dati["link HVAC"]),
        ("⏹️ BCU", dati["Versione BCU"], dati["link BCU"]),
    ]

    st.divider()

    for nome, versione, link in software:

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {nome}")
                st.write(f"**Versione:** {versione}")

            with col2:
                if pd.notna(link) and str(link).strip() != "":
                    st.link_button(
                        "**📄 Procedura**",
                        link,
                        use_container_width=True
                    )
                else:
                    st.info("Nessuna procedura")



elif menu == "Passaggio Consegne":
    Passaggio_consegne_page()

elif menu == "Passaggio Consegne":

    Passaggio_consegne_page()

elif menu == "Treno":

    sistema = st.session_state.get(
        "sistema_treno",
        "Carrelli"
    )

    if sistema == "Carrelli":

        carrelli_page()

    elif sistema == "HVAC":

        st.title("HVAC")
        st.info("Sezione HVAC in preparazione.")

    elif sistema == "Misurazione Sensori":

        misurazione_sensori_page()


    elif sistema == "Analizza Log FDE":
        analizza_page()
