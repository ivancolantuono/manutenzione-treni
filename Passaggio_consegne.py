import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
from db import supabase


def Passaggio_consegne_page():

    # ==========================================================
    # CONFIGURAZIONE
    # ==========================================================

    TRIENI_DISPONIBILI = [
        f"1000/{i:02d}"
        for i in range(1, 111)
    ]

    BINARI_DISPONIBILI = [
        "MAV1/5",
        "MAV1/6",
        "MAV2/5",
        "MAV2/6",
        "MAV2/2",
        "MAV2/3",
        "MAV2/4",
    ]

    # ==========================================================
    # STILE
    # ==========================================================

    st.markdown(
        """
        <style>

        /* ==================================================
           FORM GENERALE
           ================================================== */

        div[data-testid="stExpander"] {
            border: 2px solid #707070 !important;
            border-radius: 10px !important;
            background-color: #fafafa !important;
            padding: 4px !important;
        }

        /* ==================================================
           LABEL
           ================================================== */

        div[data-testid="stTextInput"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stSelectbox"] label {

            font-size: 15px !important;
            font-weight: 800 !important;
            color: #222222 !important;

        }

        /* ==================================================
           INPUT TESTO
           ================================================== */

        div[data-testid="stTextInput"]
        div[data-baseweb="input"] {

            border: 2px solid #555555 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            min-height: 45px !important;

            box-shadow:
                0 1px 3px rgba(0,0,0,0.08) !important;

        }

        div[data-testid="stTextInput"] input {

            font-size: 16px !important;
            font-weight: 600 !important;
            color: #111111 !important;
            padding: 10px 12px !important;

        }

        /* ==================================================
           SELECTBOX
           ================================================== */

        div[data-testid="stSelectbox"]
        div[data-baseweb="select"] > div {

            border: 2px solid #555555 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            min-height: 45px !important;

        }

        div[data-testid="stSelectbox"] div {

            font-size: 16px !important;

        }

        /* ==================================================
           TEXTAREA
           ================================================== */

        div[data-testid="stTextArea"]
        div[data-baseweb="textarea"] {

            border: 2px solid #555555 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;

            box-shadow:
                0 1px 3px rgba(0,0,0,0.08) !important;

        }

        div[data-testid="stTextArea"] textarea {

            font-size: 16px !important;
            color: #111111 !important;

        }

        /* ==================================================
           RADIO
           ================================================== */

        div[data-testid="stRadio"] {

            border: 2px solid #777777 !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            background-color: #ffffff !important;

        }

        div[data-testid="stRadio"] label {

            font-weight: 700 !important;
            color: #222222 !important;

        }

        /* ==================================================
           PULSANTI
           ================================================== */

        div[data-testid="stButton"] button {

            border-radius: 7px !important;
            font-weight: 700 !important;

        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # FUNZIONI
    # ==========================================================

    def ora_italia():

        return datetime.now(
            ZoneInfo("Europe/Rome")
        ).isoformat()

    # ----------------------------------------------------------
    # CARICA CONSEGNE
    # ----------------------------------------------------------

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

            st.error(
                "❌ Errore lettura tabella passaggio_consegne"
            )

            st.code(str(e))

            return []

    # ----------------------------------------------------------
    # NORMALIZZA DATA
    # ----------------------------------------------------------

    def normalizza_data(valore):

        if not valore:

            return ""

        if isinstance(valore, date):

            return str(valore)

        return str(valore)[:10]

    # ----------------------------------------------------------
    # ORDINAMENTO TRENI
    # ----------------------------------------------------------

    def chiave_treno(item):

        valore = str(
            item.get("treno", "")
        ).strip()

        parti = (
            valore
            .replace("-", "/")
            .split("/")
        )

        numeri = []

        for parte in parti:

            try:

                numeri.append(
                    int(parte)
                )

            except:

                numeri.append(
                    999999
                )

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
            value=date.today(),
            format="DD/MM/YYYY"
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
    # CARICAMENTO DATI
    # ==========================================================

    dati = carica_consegne()

    data_selezionata = str(
        data_consegna
    )

    # ==========================================================
    # DATI DELLA CONSEGNA
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
            f"📅 **Data:** "
            f"{data_consegna.strftime('%d/%m/%Y')}"
        )

    with col_info2:

        st.markdown(
            f"🕐 **Turno:** {turno}"
        )

    with col_info3:

        if dati_consegna:

            responsabile_salvato = (
                dati_consegna[0].get(
                    "responsabile"
                )
                or "-"
            )

            st.markdown(
                f"👤 **Responsabile:** "
                f"{responsabile_salvato}"
            )

        else:

            st.markdown(
                f"👤 **Responsabile:** "
                f"{responsabile or '-'}"
            )

    # ==========================================================
    # AGGIUNGI TRENO
    # ==========================================================

    with st.expander(
        "➕ Aggiungi treno",
        expanded=False
    ):

        st.markdown(
            "### Tipo"
        )

        tipo = st.radio(
            "Tipo",
            [
                "🚆 TRENO IN USCITA",
                "🛠️ MANUTENZIONE / LAVORAZIONE APERTA"
            ],
            horizontal=True,
            key="pc_tipo"
        )

        # ======================================================
        # PRIMA RIGA
        # ======================================================

        col1, col2, col3 = st.columns(
            [1.2, 1.2, 0.8]
        )

        # ------------------------------------------------------
        # TRENO
        # ------------------------------------------------------

        with col1:

            treno = st.selectbox(
                "🚆 Treno",
                options=TRIENI_DISPONIBILI,
                index=None,
                placeholder="Seleziona il treno",
                key="pc_treno"
            )

        # ------------------------------------------------------
        # SERVIZIO
        # ------------------------------------------------------

        with col2:

            servizio = st.text_input(
                "🚉 Servizio",
                placeholder="Es. 89705",
                key="pc_servizio"
            )

        # ------------------------------------------------------
        # ODL
        # ------------------------------------------------------

        with col3:

            odl = st.text_input(
                "📋 N° ODL PADRE",
                placeholder="Es. 100014925813",
                key="pc_odl"
            )

        # ======================================================
        # SECONDA RIGA
        # ======================================================

        col1, col2, col3 = st.columns(
            [1.2, 1.2, 0.8]
        )

        # ------------------------------------------------------
        # MANUTENZIONE
        # ------------------------------------------------------

        with col1:

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="Es. MC",
                key="pc_manutenzione"
            )

        # ------------------------------------------------------
        # BINARIO
        # ------------------------------------------------------

        with col2:

            binario = st.selectbox(
                "🛤️ Binario",
                [
                    "Seleziona binario"
                ] + BINARI_DISPONIBILI,
                key="pc_binario"
            )

        # ------------------------------------------------------
        # STATO
        # ------------------------------------------------------

        with col3:

            stato = st.radio(
                "Stato treno",
                [
                    "🟢 DISP",
                    "🔴 OUT"
                ],
                horizontal=True,
                key="pc_stato"
            )

            disp = (
                stato == "🟢 DISP"
            )

            out = (
                stato == "🔴 OUT"
            )

        # ======================================================
        # LAVORAZIONI
        # ======================================================

        lavorazioni = st.text_area(
            "📝 Lavorazioni aperte / Note",
            placeholder=(
                "Inserire lavorazioni, anomalie, "
                "attività da monitorare..."
            ),
            key="pc_lavorazioni"
        )

        # ======================================================
        # INSERIMENTO
        # ======================================================

        if st.button(
            "➕ Inserisci",
            type="primary",
            use_container_width=True,
            key="pc_inserisci"
        ):

            # --------------------------------------------------
            # CONTROLLO TRENO
            # --------------------------------------------------

            if treno == "Seleziona treno":

                st.error(
                    "⚠️ Seleziona il numero del treno."
                )

                st.stop()

            # --------------------------------------------------
            # CONTROLLO SERVIZIO
            # --------------------------------------------------

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
            # CONTROLLO BINARIO
            # --------------------------------------------------

            if binario == "Seleziona binario":

                st.error(
                    "⚠️ Seleziona il binario."
                )

                st.stop()

            # --------------------------------------------------
            # TIPO DATABASE
            # --------------------------------------------------

            if tipo.startswith("🚆"):

                tipo_db = (
                    "TRENO IN USCITA"
                )

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

            # ==================================================
            # INSERIMENTO SUPABASE
            # ==================================================

            try:

                (
                    supabase
                    .table(
                        "passaggio_consegne"
                    )
                    .insert(nuovo)
                    .execute()
                )

                # ------------------------------------------------
                # IMPORTANTE:
                # NON MODIFICHIAMO st.session_state DEI WIDGET.
                #
                # Cambiamo la versione del form.
                # Al prossimo run i widget avranno nuove chiavi
                # e quindi partiranno vuoti.
                # ------------------------------------------------

                st.session_state[
                    "pc_form_version"
                ] = (
                    st.session_state.get(
                        "pc_form_version",
                        0
                    ) + 1
                )

                carica_consegne.clear()

                st.success(
                    "✅ Treno aggiunto "
                    "al passaggio consegne."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "❌ Errore durante l'inserimento."
                )

                st.code(
                    str(e)
                )

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
    # FUNZIONE MODIFICA
    # ==========================================================

    def modifica_record(item):

        st.session_state[
            "modifica_id"
        ] = item.get("id")

    # ==========================================================
    # FUNZIONE CANCELLA
    # ==========================================================

    def cancella_record(record_id):

        try:

            (
                supabase
                .table(
                    "passaggio_consegne"
                )
                .delete()
                .eq(
                    "id",
                    record_id
                )
                .execute()
            )

            carica_consegne.clear()

            st.success(
                "🗑️ Record cancellato."
            )

            st.rerun()

        except Exception as e:

            st.error(
                "❌ Errore durante la cancellazione."
            )

            st.code(
                str(e)
            )

    # ==========================================================
    # MODIFICA RECORD
    # ==========================================================

    modifica_id = st.session_state.get(
        "modifica_id"
    )

    if modifica_id:

        record_modifica = next(
            (
                d for d in dati_consegna
                if d.get("id") == modifica_id
            ),
            None
        )

        if record_modifica:

            st.markdown(
                "### ✏️ Modifica consegna"
            )

            with st.container(
                border=True
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    treno_mod = st.selectbox(
                        "🚆 Treno",
                        TRIENI_DISPONIBILI,
                        index=(
                            TRIENI_DISPONIBILI.index(
                                record_modifica.get(
                                    "treno"
                                )
                            )
                            if record_modifica.get(
                                "treno"
                            ) in TRIENI_DISPONIBILI
                            else 0
                        ),
                        key=f"mod_treno_{modifica_id}"
                    )

                with col2:

                    servizio_mod = st.text_input(
                        "🚉 Servizio",
                        value=(
                            record_modifica.get(
                                "servizio"
                            )
                            or ""
                        ),
                        key=f"mod_servizio_{modifica_id}"
                    )

                with col3:

                    odl_mod = st.text_input(
                        "📋 N° ODL PADRE",
                        value=(
                            record_modifica.get(
                                "odl"
                            )
                            or ""
                        ),
                        key=f"mod_odl_{modifica_id}"
                    )

                col1, col2, col3 = st.columns(3)

                with col1:

                    manutenzione_mod = st.text_input(
                        "🔧 Manutenzione",
                        value=(
                            record_modifica.get(
                                "manutenzione"
                            )
                            or ""
                        ),
                        key=f"mod_manutenzione_{modifica_id}"
                    )

                with col2:

                    binario_mod = st.selectbox(
                        "🛤️ Binario",
                        BINARI_DISPONIBILI,
                        index=(
                            BINARI_DISPONIBILI.index(
                                record_modifica.get(
                                    "binario"
                                )
                            )
                            if record_modifica.get(
                                "binario"
                            ) in BINARI_DISPONIBILI
                            else 0
                        ),
                        key=f"mod_binario_{modifica_id}"
                    )

                with col3:

                    stato_mod = st.radio(
                        "Stato treno",
                        [
                            "🟢 DISP",
                            "🔴 OUT"
                        ],
                        horizontal=True,
                        index=(
                            0
                            if record_modifica.get(
                                "disp"
                            )
                            else 1
                        ),
                        key=f"mod_stato_{modifica_id}"
                    )

                lavorazioni_mod = st.text_area(
                    "📝 Lavorazioni aperte / Note",
                    value=(
                        record_modifica.get(
                            "lavorazioni"
                        )
                        or ""
                    ),
                    key=f"mod_lavorazioni_{modifica_id}"
                )

                col_salva, col_annulla = st.columns(2)

                with col_salva:

                    if st.button(
                        "💾 Salva modifiche",
                        type="primary",
                        use_container_width=True,
                        key=f"salva_mod_{modifica_id}"
                    ):

                        nuovo_stato_disp = (
                            stato_mod == "🟢 DISP"
                        )

                        nuovo_stato_out = (
                            stato_mod == "🔴 OUT"
                        )

                        aggiornamento = {

                            "treno":
                                treno_mod,

                            "manutenzione":
                                manutenzione_mod.strip(),

                            "servizio":
                                servizio_mod.strip(),

                            "binario":
                                binario_mod,

                            "disp":
                                nuovo_stato_disp,

                            "out":
                                nuovo_stato_out,

                            "lavorazioni":
                                lavorazioni_mod.strip(),

                            "odl":
                                odl_mod.strip()
                        }

                        try:

                            (
                                supabase
                                .table(
                                    "passaggio_consegne"
                                )
                                .update(
                                    aggiornamento
                                )
                                .eq(
                                    "id",
                                    modifica_id
                                )
                                .execute()
                            )

                            carica_consegne.clear()

                            st.session_state.pop(
                                "modifica_id",
                                None
                            )

                            st.success(
                                "✅ Modifica salvata."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "❌ Errore durante la modifica."
                            )

                            st.code(
                                str(e)
                            )

                with col_annulla:

                    if st.button(
                        "↩️ Annulla",
                        use_container_width=True,
                        key=f"annulla_mod_{modifica_id}"
                    ):

                        st.session_state.pop(
                            "modifica_id",
                            None
                        )

                        st.rerun()

    # ==========================================================
    # TRENI IN USCITA
    # ==========================================================

    treni_uscita = [

        d for d in dati_consegna

        if d.get("tipo")
        == "TRENO IN USCITA"
    ]

    treni_uscita = sorted(
        treni_uscita,
        key=chiave_treno
    )

    # ==========================================================
    # TITOLO TRENI
    # ==========================================================

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

        h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns(
            [
                1.2,
                1.5,
                1.3,
                1.3,
                0.8,
                0.8,
                3,
                1.5,
                1.5
            ]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**SERVIZIO**")
        h4.markdown("**BINARIO**")
        h5.markdown("**DISP**")
        h6.markdown("**OUT**")
        h7.markdown("**LAVORAZIONI / NOTE**")
        h8.markdown("**N° ODL PADRE**")
        h9.markdown("**AZIONI**")

        st.divider()

        # ======================================================
        # RIGHE
        # ======================================================

        for item in treni_uscita:

            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
                [
                    1.2,
                    1.5,
                    1.3,
                    1.3,
                    0.8,
                    0.8,
                    3,
                    1.5,
                    1.5
                ]
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

            if item.get("disp"):

                c5.markdown("🟢")

            else:

                c5.markdown("⚪")

            if item.get("out"):

                c6.markdown("🔴")

            else:

                c6.markdown("⚪")

            c7.write(
                item.get(
                    "lavorazioni"
                ) or "-"
            )

            c8.write(
                item.get(
                    "odl"
                ) or "-"
            )

            # --------------------------------------------------
            # AZIONI
            # --------------------------------------------------

            with c9:

                with st.popover("**⋮**"):
            
                    if st.button(
                        "✏️ Modifica",
                        key=f"edit_{item.get('id')}",
                        use_container_width=True
                    ):
            
                        modifica_record(item)
                        st.rerun()
            
                    if st.button(
                        "🗑️ Cancella",
                        key=f"delete_{item.get('id')}",
                        use_container_width=True
                    ):
            
                        cancella_record(item.get("id"))
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

    # ==========================================================
    # TITOLO MANUTENZIONI
    # ==========================================================

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

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
            [
                1.2,
                1.8,
                1.5,
                0.8,
                0.8,
                4,
                1.5,
                1.5
            ]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**BINARIO**")
        h4.markdown("**DISP**")
        h5.markdown("**OUT**")
        h6.markdown("**LAVORAZIONI APERTE / NOTE**")
        h7.markdown("**N° ODL PADRE**")
        h8.markdown("**AZIONI**")

        st.divider()

        # ======================================================
        # RIGHE
        # ======================================================

        for item in manutenzioni:

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                [
                    1.2,
                    1.8,
                    1.5,
                    0.8,
                    0.8,
                    4,
                    1.5,
                    1.5
                ]
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

            if item.get("disp"):

                c4.markdown("🟢")

            else:

                c4.markdown("⚪")

            if item.get("out"):

                c5.markdown("🔴")

            else:

                c5.markdown("⚪")

            c6.write(
                item.get(
                    "lavorazioni"
                ) or "-"
            )

            c7.write(
                item.get(
                    "odl"
                ) or "-"
            )

            # --------------------------------------------------
            # AZIONI
            # --------------------------------------------------

            with c8:

                if st.button(
                    "✏️ Modifica",
                    key=f"edit_m_{item.get('id')}"
                ):

                    modifica_record(
                        item
                    )

                    st.rerun()

                if st.button(
                    "🗑️ Cancella",
                    key=f"delete_m_{item.get('id')}"
                ):

                    cancella_record(
                        item.get("id")
                    )

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
        f"🚆 Treni in uscita: "
        f"{len(treni_uscita)}"
        f"  |  "
        f"🛠️ Lavorazioni aperte: "
        f"{len(manutenzioni)}"
    )
