import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
from db import supabase


def Passaggio_consegne_page():

    # ==========================================================
    # FUNZIONI
    # ==========================================================

    def ora_italia():
        return datetime.now(
            ZoneInfo("Europe/Rome")
        ).isoformat()

    @st.cache_data(ttl=5)
    def carica_consegne():

        try:

            res = (
                supabase
                .table("passaggio_consegne")
                .select("*")
                .execute()
            )

            return res.data or []

        except Exception as e:

            st.error("❌ Errore lettura tabella passaggio_consegne")
            st.code(str(e))

            return []

    def normalizza_data(valore):

        if not valore:
            return ""

        if isinstance(valore, date):
            return str(valore)

        return str(valore)[:10]

    def chiave_treno(item):

        """
        Ordinamento numerico dei treni.

        Esempi:
        1
        2
        3
        10
        11
        27

        Gestisce anche valori tipo:
        1000/04
        1000/27
        """

        valore = str(item.get("treno", "")).strip()

        parti = valore.replace("-", "/").split("/")

        numeri = []

        for parte in parti:

            try:
                numeri.append(int(parte))
            except:
                numeri.append(999999)

        return tuple(numeri)

    # ==========================================================
    # TITOLO
    # ==========================================================

    st.title("🔄 Passaggio Consegne")

    # ==========================================================
    # DATA / TURNO / RESPONSABILE
    # ==========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        data_consegna = st.date_input(
            "📅 Data",
            value=date.today()
        )

    with col2:

        turno = st.selectbox(
            "🕐 Turno",
            [
                "Mattina",
                "Pomeriggio",
                "Notte"
            ]
        )

    with col3:

        responsabile = st.text_input(
            "👤 Responsabile",
            value=st.session_state.get(
                "utente",
                ""
            )
        )

    # ==========================================================
    # CARICA DATI
    # ==========================================================

    dati = carica_consegne()

    data_selezionata = str(data_consegna)

    # ==========================================================
    # DATI DELLA CONSEGNA SELEZIONATA
    # ==========================================================

    dati_consegna = [

        d for d in dati

        if normalizza_data(
            d.get("data_consegna")
        ) == data_selezionata

        and d.get("turno") == turno
    ]

    # ==========================================================
    # INFORMAZIONI CONSEGNA
    # ==========================================================

    st.divider()

    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:

        st.markdown(
            f"📅 **Data:** {data_consegna.strftime('%d/%m/%Y')}"
        )

    with col_info2:

        st.markdown(
            f"🕐 **Turno:** {turno}"
        )

    with col_info3:

        if dati_consegna:

            responsabile_salvato = (
                dati_consegna[0].get("responsabile")
                or "-"
            )

            st.markdown(
                f"👤 **Responsabile:** {responsabile_salvato}"
            )

        else:

            st.markdown(
                f"👤 **Responsabile:** {responsabile or '-'}"
            )

    # ==========================================================
    # AGGIUNGI TRENO
    # ==========================================================

    with st.expander(
        "➕ Aggiungi treno",
        expanded=True
    ):

        st.markdown("### Tipo")

        tipo = st.radio(
            "",
            [
                "🚆 TRENO IN USCITA",
                "🛠️ MANUTENZIONE / LAVORAZIONE APERTA"
            ],
            horizontal=True
        )

        col1, col2, col3 = st.columns(3)

        # ------------------------------------------------------
        # COLONNA 1
        # ------------------------------------------------------

        with col1:

            treno = st.text_input(
                "🚆 Treno",
                placeholder="Es. 1000/27"
            )

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="Es. MC"
            )

        # ------------------------------------------------------
        # COLONNA 2
        # ------------------------------------------------------

        with col2:

            servizio = st.text_input(
                "🚉 Servizio",
                placeholder="Es. 89705"
            )

            binario = st.text_input(
                "🛤️ Binario",
                placeholder="Es. MAV 9"
            )

        # ------------------------------------------------------
        # COLONNA 3
        # ------------------------------------------------------

        with col3:

            odl = st.text_input(
                "📋 N° ODL PADRE",
                placeholder="Es. 100014925813"
            )

            st.write("")

            disp = st.checkbox(
                "🟢 DISP"
            )

            out = st.checkbox(
                "🔴 OUT"
            )

        # ------------------------------------------------------
        # LAVORAZIONI
        # ------------------------------------------------------

        lavorazioni = st.text_area(
            "📝 Lavorazioni aperte / Note",
            placeholder=(
                "Inserire lavorazioni, anomalie, "
                "attività da monitorare..."
            )
        )

        # ======================================================
        # INSERIMENTO
        # ======================================================

        if st.button(
            "➕ Inserisci",
            type="primary",
            use_container_width=True
        ):

            if not treno.strip():

                st.error(
                    "⚠️ Inserisci il numero del treno."
                )

                st.stop()

            if (
                tipo.startswith("🚆")
                and not servizio.strip()
            ):

                st.error(
                    "⚠️ Per un treno in uscita "
                    "inserisci il servizio."
                )

                st.stop()

            # --------------------------------------------------
            # TIPO DATABASE
            # --------------------------------------------------

            if tipo.startswith("🚆"):

                tipo_db = "TRENO IN USCITA"

            else:

                tipo_db = (
                    "MANUTENZIONE / "
                    "LAVORAZIONE APERTA"
                )

            # --------------------------------------------------
            # NUOVO RECORD
            # --------------------------------------------------

            nuovo = {

                "data_consegna":
                    data_selezionata,

                "turno":
                    turno,

                "responsabile":
                    responsabile.strip(),

                "tipo":
                    tipo_db,

                "treno":
                    treno.strip(),

                "manutenzione":
                    manutenzione.strip(),

                "servizio":
                    servizio.strip(),

                "binario":
                    binario.strip(),

                "disp":
                    disp,

                "out":
                    out,

                "lavorazioni":
                    lavorazioni.strip(),

                "odl":
                    odl.strip(),

                "created_at":
                    ora_italia()
            }

            try:

                (
                    supabase
                    .table("passaggio_consegne")
                    .insert(nuovo)
                    .execute()
                )

                # Svuota cache
                carica_consegne.clear()

                st.success(
                    "✅ Treno aggiunto al passaggio consegne."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "❌ Errore durante l'inserimento."
                )

                st.code(str(e))

    st.divider()

    # ==========================================================
    # NESSUN DATO
    # ==========================================================

    if not dati_consegna:

        st.info(
            f"📭 Nessuna consegna presente per "
            f"{data_consegna.strftime('%d/%m/%Y')} "
            f"— turno {turno}."
        )

        return

    # ==========================================================
    # TRENI IN USCITA
    # ==========================================================

    treni_uscita = [

        d for d in dati_consegna

        if d.get("tipo") == "TRENO IN USCITA"
    ]

    # Ordinamento numerico
    treni_uscita = sorted(
        treni_uscita,
        key=chiave_treno
    )

    st.markdown(
        """
        <div style="
            background-color:#b7d7f0;
            padding:10px;
            text-align:center;
            font-weight:bold;
            border-radius:5px;
            margin-top:15px;
        ">
        🚆 TRENI IN USCITA
        </div>
        """,
        unsafe_allow_html=True
    )

    if not treni_uscita:

        st.info(
            "Nessun treno in uscita."
        )

    else:

        # ======================================================
        # INTESTAZIONE
        # ======================================================

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
            [1.2, 1.5, 1.3, 1.3, 0.8, 0.8, 3, 1.5]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**SERVIZIO**")
        h4.markdown("**BINARIO**")
        h5.markdown("**DISP**")
        h6.markdown("**OUT**")
        h7.markdown("**LAVORAZIONI / NOTE**")
        h8.markdown("**N° ODL PADRE**")

        st.divider()

        # ======================================================
        # RIGHE
        # ======================================================

        for item in treni_uscita:

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                [1.2, 1.5, 1.3, 1.3, 0.8, 0.8, 3, 1.5]
            )

            c1.write(
                item.get("treno") or "-"
            )

            c2.write(
                item.get("manutenzione") or "-"
            )

            c3.write(
                item.get("servizio") or "-"
            )

            c4.write(
                item.get("binario") or "-"
            )

            # DISP
            if item.get("disp"):

                c5.markdown("🟢")

            else:

                c5.markdown("⚪")

            # OUT
            if item.get("out"):

                c6.markdown("🔴")

            else:

                c6.markdown("⚪")

            c7.write(
                item.get("lavorazioni") or "-"
            )

            if item.get("odl"):

                c8.write(
                    item.get("odl")
                )

            else:

                c8.write("-")

            st.divider()

    # ==========================================================
    # MANUTENZIONI / LAVORAZIONI APERTE
    # ==========================================================

    manutenzioni = [

        d for d in dati_consegna

        if d.get("tipo")
        == "MANUTENZIONE / LAVORAZIONE APERTA"
    ]

    manutenzioni = sorted(
        manutenzioni,
        key=chiave_treno
    )

    st.markdown(
        """
        <div style="
            background-color:#b7d7f0;
            padding:10px;
            text-align:center;
            font-weight:bold;
            border-radius:5px;
            margin-top:25px;
        ">
        🛠️ MANUTENZIONE / LAVORAZIONI APERTE
        </div>
        """,
        unsafe_allow_html=True
    )

    if not manutenzioni:

        st.info(
            "Nessuna manutenzione o lavorazione aperta."
        )

    else:

        # ======================================================
        # INTESTAZIONE
        # ======================================================

        h1, h2, h3, h4, h5, h6, h7 = st.columns(
            [1.2, 1.8, 1.5, 0.8, 0.8, 4, 1.5]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**BINARIO**")
        h4.markdown("**DISP**")
        h5.markdown("**OUT**")
        h6.markdown("**LAVORAZIONI APERTE / NOTE**")
        h7.markdown("**N° ODL PADRE**")

        st.divider()

        # ======================================================
        # RIGHE
        # ======================================================

        for item in manutenzioni:

            c1, c2, c3, c4, c5, c6, c7 = st.columns(
                [1.2, 1.8, 1.5, 0.8, 0.8, 4, 1.5]
            )

            c1.write(
                item.get("treno") or "-"
            )

            c2.write(
                item.get("manutenzione") or "-"
            )

            c3.write(
                item.get("binario") or "-"
            )

            # DISP
            if item.get("disp"):

                c4.markdown("🟢")

            else:

                c4.markdown("⚪")

            # OUT
            if item.get("out"):

                c5.markdown("🔴")

            else:

                c5.markdown("⚪")

            c6.write(
                item.get("lavorazioni") or "-"
            )

            if item.get("odl"):

                c7.write(
                    item.get("odl")
                )

            else:

                c7.write("-")

            st.divider()

    # ==========================================================
    # RIEPILOGO
    # ==========================================================

    st.divider()

    st.caption(
        f"📅 Consegna del "
        f"{data_consegna.strftime('%d/%m/%Y')}"
        f"  |  "
        f"🕐 Turno: {turno}"
        f"  |  "
        f"🚆 Treni in uscita: {len(treni_uscita)}"
        f"  |  "
        f"🛠️ Lavorazioni aperte: {len(manutenzioni)}"
    )
