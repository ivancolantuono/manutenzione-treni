import streamlit as st
from pathlib import Path


# ==========================================================
# CONFIGURAZIONE
# ==========================================================

st.set_page_config(
    page_title="Carrelli ETR1000",
    page_icon="🚆",
    layout="wide"
)


# ==========================================================
# PERCORSI
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "carrelli_img"


# ==========================================================
# STILE
# ==========================================================

st.markdown("""
<style>

.carrelli-titolo {
    background: #e30613;
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 25px;
}

.info-box {
    background: #f3f4f6;
    padding: 12px 16px;
    border-radius: 8px;
    margin-top: 10px;
    margin-bottom: 20px;
}

.immagine-titolo {
    background: #f1f1f1;
    padding: 10px 15px;
    border-radius: 6px;
    font-size: 20px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# TITOLO
# ==========================================================

st.markdown(
    '<div class="carrelli-titolo">🚆 CARRELLI ETR1000</div>',
    unsafe_allow_html=True
)


# ==========================================================
# STRUTTURA SEZIONI
# ==========================================================

sezioni = {

    "🛞 CARRELLI": [
        "DM1-CARR.1",
        "DM1-CARR.2",
        "M3-CARR.1",
        "M3-CARR.2",
        "M6-CARR.1",
        "M6-CARR.2",
        "DM8-CARR.1",
        "DM8-CARR.2",
    ],

    "📡 SENSORI": [
        "SENSORI SPM",
        "PT100 RIDUTTORI",
    ],

    "🔌 FUSE LOOP": [
        "FUSE LOOP CASSA MOTOR",
        "FUSE LOOP TRENO COMPLETO",
    ],

    "🔄 DNRA": [
        "LOOP DNRA",
        "OVERVIEW DNRA",
    ],

    "🚆 STATO TRENO": [
        "STATO TRENO",
    ],
}


# ==========================================================
# FUNZIONE CERCA IMMAGINE
# ==========================================================

def trova_immagine(nome):

    # Possibili estensioni
    estensioni = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    ]

    for estensione in estensioni:

        percorso = IMG_DIR / f"{nome}{estensione}"

        if percorso.exists():
            return percorso

    return None


# ==========================================================
# SELEZIONE SEZIONE
# ==========================================================

st.markdown("### 📂 Sezione")

sezione = st.selectbox(
    "Seleziona la sezione",
    list(sezioni.keys()),
    label_visibility="collapsed"
)


# ==========================================================
# SELEZIONE FOGLIO
# ==========================================================

st.markdown("### 📄 Foglio")

fogli = sezioni[sezione]

foglio = st.selectbox(
    "Seleziona il foglio",
    fogli,
    label_visibility="collapsed"
)


# ==========================================================
# SEPARATORE
# ==========================================================

st.divider()


# ==========================================================
# INFORMAZIONI
# ==========================================================

st.markdown(
    f"""
    <div class="info-box">
        📂 <b>Sezione:</b> {sezione}<br>
        📄 <b>Foglio:</b> {foglio}
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# CERCA IMMAGINE
# ==========================================================

immagine = trova_immagine(foglio)


# ==========================================================
# VISUALIZZAZIONE
# ==========================================================

if immagine:

    st.markdown(
        f'<div class="immagine-titolo">📄 {foglio}</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # MOSTRA IMMAGINE
    # ------------------------------------------------------

    st.image(
        str(immagine),
        use_container_width=True
    )

else:

    st.warning(
        f"⚠️ L'immagine per **{foglio}** non è ancora presente."
    )

    st.markdown(
        "Carica nella cartella:"
    )

    st.code("carrelli_img")

    st.markdown(
        "un file con uno di questi nomi:"
    )

    st.code(
        f"{foglio}.png\n"
        f"{foglio}.jpg\n"
        f"{foglio}.jpeg\n"
        f"{foglio}.webp"
    )


# ==========================================================
# DEBUG CARTELLA
# ==========================================================

with st.expander("🔧 Controllo immagini", expanded=False):

    st.write("Cartella immagini:")

    st.code(str(IMG_DIR))

    if IMG_DIR.exists():

        files = sorted(
            [
                f.name
                for f in IMG_DIR.iterdir()
                if f.is_file()
            ]
        )

        if files:

            st.write("Immagini presenti:")

            for file in files:
                st.write(f"• {file}")

        else:

            st.warning(
                "La cartella esiste ma è vuota."
            )

    else:

        st.error(
            "La cartella carrelli_img non esiste."
        )
