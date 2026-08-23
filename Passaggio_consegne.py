import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
from db import supabase


def Passaggio_consegne_page():

    # ==========================================================
    # STILE CAMPI FORM
    # ==========================================================

    st.markdown(
        """
        <style>

        /* ================================================
           CAMPI INPUT
        ================================================ */

        div[data-baseweb="input"] {
            border: 2px solid #8a8a8a !important;
            border-radius: 7px !important;
            background-color: #fafafa !important;
        }

        div[data-baseweb="input"]:focus-within {
            border: 2px solid #e30613 !important;
            box-shadow: 0 0 0 1px #e30613 !important;
        }

        div[data-baseweb="input"] input {
            font-size: 17px !important;
            font-weight: 500 !important;
            color: #222222 !important;
        }

        /* ================================================
           TEXTAREA
        ================================================ */

        div[data-baseweb="textarea"] {
            border: 2px solid #8a8a8a !important;
            border-radius: 7px !important;
            background-color: #fafafa !important;
        }

        div[data-baseweb="textarea"]:focus-within {
            border: 2px solid #e30613 !important;
            box-shadow: 0 0 0 1px #e30613 !important;
        }

        div[data-baseweb="textarea"] textarea {
            font-size: 16px !important;
            color: #222222 !important;
        }

        /* ================================================
           LABEL DEI CAMPI
        ================================================ */

        div[data-testid="stTextInput"] label,
        div[data-testid="stTextArea"] label {
            font-size: 15px !important;
            font-weight: 700 !important;
            color: #222222 !important;
        }

        /* ================================================
           RADIO
        ================================================ */

        div[data-testid="stRadio"] label {
            font-weight: 600 !important;
        }

        /* ================================================
           EXPANDER
        ================================================ */

        div[data-testid="stExpander"] {
            border: 2px solid #b5b5b5 !important;
            border-radius: 10px !important;
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
                "❌ Errore lettura tabella "
                "passaggio_consegne"
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
    # ORDINAMENTO TRENO
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

    # ----------------------------------------------------------
    # DATA
    # ----------------------------------------------------------

    with col1:

        data_consegna = st.date_input(
            "📅 Data",
            value=date.today()
        )

    # ----------------------------------------------------------
    # TURNO
    # ----------------------------------------------------------

    with col2:

        turno = st.selectbox(
            "🕐 Turno",
            [
                "Mattina",
                "Pomeriggio",
                "Notte"
            ]
        )

    # ----------------------------------------------------------
    # RESPONSABILE
    # ----------------------------------------------------------

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

    data_selezionata = str(
        data_consegna
    )

    # ==========================================================
    # FILTRO DATA + TURNO
    # ==========================================================

    dati_consegna = [

        d

        for d in dati

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

        # ------------------------------------------------------
        # FORM
        # clear_on_submit = svuota automaticamente i campi
        # ------------------------------------------------------

        with st.form(
            "form_aggiungi_passaggio",
            clear_on_submit=True
        ):

            st.markdown("### Tipo")

            tipo = st.radio(
                "Tipo",
                [
                    "🚆 TRENO IN USCITA",
                    "🛠️ MANUTENZIONE / "
                    "LAVORAZIONE APERTA"
                ],
                horizontal=True
            )

            col1, col2, col3 = st.columns(3)

            # --------------------------------------------------
            # COLONNA 1
            # --------------------------------------------------

            with col1:

                treno = st.text_input(
                    "🚆 Treno",
                    placeholder="Es. 1000/27"
                )

                manutenzione = st.text_input(
                    "🔧 Manutenzione",
                    placeholder="Es. MC"
                )

            # --------------------------------------------------
            # COLONNA 2
            # --------------------------------------------------

            with col2:

                servizio = st.text_input(
                    "🚉 Servizio",
                    placeholder="Es. 89705"
                )

                binario = st.text_input(
                    "🛤️ Binario",
                    placeholder="Es. MAV 9"
                )

            # --------------------------------------------------
            # COLONNA 3
            # --------------------------------------------------

            with col3:

                odl = st.text_input(
                    "📋 N° ODL PADRE",
                    placeholder="Es. 100014925813"
                )

                st.write("")

                stato = st.radio(
                    "Stato treno",
                    [
                        "🟢 DISP",
                        "🔴 OUT"
                    ],
                    horizontal=True
                )

            # --------------------------------------------------
            # STATO
            # --------------------------------------------------

            disp = (
                stato == "🟢 DISP"
            )

            out = (
                stato == "🔴 OUT"
            )

            # --------------------------------------------------
            # LAVORAZIONI
            # --------------------------------------------------

            lavorazioni = st.text_area(
                "📝 Lavorazioni aperte / Note",
                placeholder=(
                    "Inserire lavorazioni, "
                    "anomalie, attività da monitorare..."
                )
            )

            # --------------------------------------------------
            # PULSANTE
            # --------------------------------------------------

            inserisci = st.form_submit_button(
                "➕ Inserisci",
                type="primary",
                use_container_width=True
            )

        # ======================================================
        # INSERIMENTO
        # ======================================================

        if inserisci:

            # --------------------------------------------------
            # CONTROLLO TRENO
            # --------------------------------------------------

            if not treno.strip():

                st.error(
                    "⚠️ Inserisci il numero del treno."
                )

            # --------------------------------------------------
            # CONTROLLO SERVIZIO
            # --------------------------------------------------

            elif (
                tipo.startswith("🚆")
                and not servizio.strip()
            ):

                st.error(
                    "⚠️ Per un treno in uscita "
                    "inserisci il servizio."
                )

            else:

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

                # --------------------------------------------------
                # INSERT
                # --------------------------------------------------

                try:

                    (
                        supabase
                        .table(
                            "passaggio_consegne"
                        )
                        .insert(nuovo)
                        .execute()
                    )

                    carica_consegne.clear()

                    st.success(
                        "✅ Treno aggiunto "
                        "al passaggio consegne."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ Errore durante "
                        "l'inserimento."
                    )

                    st.code(str(e))

    # ==========================================================
    # SEPARATORE
    # ==========================================================

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

        d

        for d in dati_consegna

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

    # ==========================================================
    # TRENI
    # ==========================================================

    if not treni_uscita:

        st.info(
            "Nessun treno in uscita."
        )

    else:

        # ------------------------------------------------------
        # INTESTAZIONE
        # ------------------------------------------------------

        h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns(
            [
                1.1,
                1.4,
                1.2,
                1.2,
                0.6,
                0.6,
                3,
                1.4,
                1.3
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

        # ------------------------------------------------------
        # RIGHE
        # ------------------------------------------------------

        for item in treni_uscita:

            item_id = item.get("id")

            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
                [
                    1.1,
                    1.4,
                    1.2,
                    1.2,
                    0.6,
                    0.6,
                    3,
                    1.4,
                    1.3
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
                item.get("lavorazioni") or "-"
            )

            c8.write(
                item.get("odl") or "-"
            )

            # --------------------------------------------------
            # AZIONI
            # --------------------------------------------------

            modifica = c9.button(
                "✏️",
                key=f"modifica_u_{item_id}",
                help="Modifica"
            )

            cancella = c9.button(
                "🗑️",
                key=f"cancella_u_{item_id}",
                help="Cancella"
            )

            # --------------------------------------------------
            # ATTIVA MODIFICA
            # --------------------------------------------------

            if modifica:

                st.session_state[
                    "modifica_id"
                ] = item_id

                st.rerun()

            # --------------------------------------------------
            # CANCELLA
            # --------------------------------------------------

            if cancella:

                st.session_state[
                    "cancella_id"
                ] = item_id

                st.rerun()

            # ==================================================
            # FORM MODIFICA
            # ==================================================

            if (
                st.session_state.get(
                    "modifica_id"
                )
                == item_id
            ):

                st.markdown(
                    "#### ✏️ Modifica treno"
                )

                with st.form(
                    f"form_modifica_u_{item_id}"
                ):

                    col_a, col_b, col_c = st.columns(3)

                    with col_a:

                        nuovo_treno = st.text_input(
                            "🚆 Treno",
                            value=item.get(
                                "treno"
                            ) or ""
                        )

                        nuova_manutenzione = st.text_input(
                            "🔧 Manutenzione",
                            value=item.get(
                                "manutenzione"
                            ) or ""
                        )

                    with col_b:

                        nuovo_servizio = st.text_input(
                            "🚉 Servizio",
                            value=item.get(
                                "servizio"
                            ) or ""
                        )

                        nuovo_binario = st.text_input(
                            "🛤️ Binario",
                            value=item.get(
                                "binario"
                            ) or ""
                        )

                    with col_c:

                        nuovo_odl = st.text_input(
                            "📋 N° ODL PADRE",
                            value=item.get(
                                "odl"
                            ) or ""
                        )

                        stato_modifica = st.radio(
                            "Stato",
                            [
                                "🟢 DISP",
                                "🔴 OUT"
                            ],
                            index=(
                                0
                                if item.get("disp")
                                else 1
                            ),
                            horizontal=True
                        )

                    nuova_lavorazione = st.text_area(
                        "📝 Lavorazioni / Note",
                        value=item.get(
                            "lavorazioni"
                        ) or ""
                    )

                    col_save, col_annulla = st.columns(2)

                    with col_save:

                        salva = st.form_submit_button(
                            "💾 Salva modifica",
                            type="primary",
                            use_container_width=True
                        )

                    with col_annulla:

                        annulla = st.form_submit_button(
                            "↩️ Annulla",
                            use_container_width=True
                        )

                if annulla:

                    st.session_state.pop(
                        "modifica_id",
                        None
                    )

                    st.rerun()

                if salva:

                    if not nuovo_treno.strip():

                        st.error(
                            "⚠️ Il numero del treno "
                            "non può essere vuoto."
                        )

                    elif (
                        not nuovo_servizio.strip()
                    ):

                        st.error(
                            "⚠️ Inserisci il servizio."
                        )

                    else:

                        nuovo_disp = (
                            stato_modifica
                            == "🟢 DISP"
                        )

                        nuovo_out = (
                            stato_modifica
                            == "🔴 OUT"
                        )

                        aggiornamento = {

                            "treno":
                                nuovo_treno.strip(),

                            "manutenzione":
                                nuova_manutenzione.strip(),

                            "servizio":
                                nuovo_servizio.strip(),

                            "binario":
                                nuovo_binario.strip(),

                            "disp":
                                nuovo_disp,

                            "out":
                                nuovo_out,

                            "lavorazioni":
                                nuova_lavorazione.strip(),

                            "odl":
                                nuovo_odl.strip()
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
                                    item_id
                                )
                                .execute()
                            )

                            st.session_state.pop(
                                "modifica_id",
                                None
                            )

                            carica_consegne.clear()

                            st.success(
                                "✅ Modifica salvata."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "❌ Errore durante "
                                "la modifica."
                            )

                            st.code(str(e))

            # ==================================================
            # CONFERMA CANCELLAZIONE
            # ==================================================

            if (
                st.session_state.get(
                    "cancella_id"
                )
                == item_id
            ):

                st.warning(
                    f"⚠️ Vuoi cancellare "
                    f"il treno {item.get('treno')}?"
                )

                col_conferma, col_annulla = st.columns(2)

                with col_conferma:

                    conferma_delete = st.button(
                        "🗑️ Sì, cancella",
                        key=f"conferma_u_{item_id}",
                        type="primary",
                        use_container_width=True
                    )

                with col_annulla:

                    annulla_delete = st.button(
                        "↩️ Annulla",
                        key=f"annulla_u_{item_id}",
                        use_container_width=True
                    )

                if annulla_delete:

                    st.session_state.pop(
                        "cancella_id",
                        None
                    )

                    st.rerun()

                if conferma_delete:

                    try:

                        (
                            supabase
                            .table(
                                "passaggio_consegne"
                            )
                            .delete()
                            .eq(
                                "id",
                                item_id
                            )
                            .execute()
                        )

                        st.session_state.pop(
                            "cancella_id",
                            None
                        )

                        carica_consegne.clear()

                        st.success(
                            "🗑️ Record cancellato."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "❌ Errore durante "
                            "la cancellazione."
                        )

                        st.code(str(e))

            st.divider()

    # ==========================================================
    # MANUTENZIONI / LAVORAZIONI APERTE
    # ==========================================================

    manutenzioni = [

        d

        for d in dati_consegna

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

    # ==========================================================
    # MANUTENZIONI
    # ==========================================================

    if not manutenzioni:

        st.info(
            "Nessuna manutenzione o "
            "lavorazione aperta."
        )

    else:

        # ------------------------------------------------------
        # INTESTAZIONE
        # ------------------------------------------------------

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
            [
                1.1,
                1.6,
                1.4,
                0.6,
                0.6,
                4,
                1.4,
                1.3
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

        # ------------------------------------------------------
        # RIGHE
        # ------------------------------------------------------

        for item in manutenzioni:

            item_id = item.get("id")

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                [
                    1.1,
                    1.6,
                    1.4,
                    0.6,
                    0.6,
                    4,
                    1.4,
                    1.3
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
                item.get("lavorazioni") or "-"
            )

            c7.write(
                item.get("odl") or "-"
            )

            # --------------------------------------------------
            # AZIONI
            # --------------------------------------------------

            modifica = c8.button(
                "✏️",
                key=f"modifica_m_{item_id}",
                help="Modifica"
            )

            cancella = c8.button(
                "🗑️",
                key=f"cancella_m_{item_id}",
                help="Cancella"
            )

            # --------------------------------------------------
            # ATTIVA MODIFICA
            # --------------------------------------------------

            if modifica:

                st.session_state[
                    "modifica_id"
                ] = item_id

                st.rerun()

            # --------------------------------------------------
            # ATTIVA CANCELLA
            # --------------------------------------------------

            if cancella:

                st.session_state[
                    "cancella_id"
                ] = item_id

                st.rerun()

            # ==================================================
            # FORM MODIFICA
            # ==================================================

            if (
                st.session_state.get(
                    "modifica_id"
                )
                == item_id
            ):

                st.markdown(
                    "#### ✏️ Modifica manutenzione"
                )

                with st.form(
                    f"form_modifica_m_{item_id}"
                ):

                    col_a, col_b, col_c = st.columns(3)

                    with col_a:

                        nuovo_treno = st.text_input(
                            "🚆 Treno",
                            value=item.get(
                                "treno"
                            ) or ""
                        )

                        nuova_manutenzione = st.text_input(
                            "🔧 Manutenzione",
                            value=item.get(
                                "manutenzione"
                            ) or ""
                        )

                    with col_b:

                        nuovo_binario = st.text_input(
                            "🛤️ Binario",
                            value=item.get(
                                "binario"
                            ) or ""
                        )

                        nuovo_odl = st.text_input(
                            "📋 N° ODL PADRE",
                            value=item.get(
                                "odl"
                            ) or ""
                        )

                    with col_c:

                        stato_modifica = st.radio(
                            "Stato",
                            [
                                "🟢 DISP",
                                "🔴 OUT"
                            ],
                            index=(
                                0
                                if item.get("disp")
                                else 1
                            ),
                            horizontal=True
                        )

                    nuova_lavorazione = st.text_area(
                        "📝 Lavorazioni / Note",
                        value=item.get(
                            "lavorazioni"
                        ) or ""
                    )

                    col_save, col_annulla = st.columns(2)

                    with col_save:

                        salva = st.form_submit_button(
                            "💾 Salva modifica",
                            type="primary",
                            use_container_width=True
                        )

                    with col_annulla:

                        annulla = st.form_submit_button(
                            "↩️ Annulla",
                            use_container_width=True
                        )

                if annulla:

                    st.session_state.pop(
                        "modifica_id",
                        None
                    )

                    st.rerun()

                if salva:

                    if not nuovo_treno.strip():

                        st.error(
                            "⚠️ Il numero del treno "
                            "non può essere vuoto."
                        )

                    else:

                        nuovo_disp = (
                            stato_modifica
                            == "🟢 DISP"
                        )

                        nuovo_out = (
                            stato_modifica
                            == "🔴 OUT"
                        )

                        aggiornamento = {

                            "treno":
                                nuovo_treno.strip(),

                            "manutenzione":
                                nuova_manutenzione.strip(),

                            "binario":
                                nuovo_binario.strip(),

                            "disp":
                                nuovo_disp,

                            "out":
                                nuovo_out,

                            "lavorazioni":
                                nuova_lavorazione.strip(),

                            "odl":
                                nuovo_odl.strip()
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
                                    item_id
                                )
                                .execute()
                            )

                            st.session_state.pop(
                                "modifica_id",
                                None
                            )

                            carica_consegne.clear()

                            st.success(
                                "✅ Modifica salvata."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "❌ Errore durante "
                                "la modifica."
                            )

                            st.code(str(e))

            # ==================================================
            # CANCELLAZIONE
            # ==================================================

            if (
                st.session_state.get(
                    "cancella_id"
                )
                == item_id
            ):

                st.warning(
                    f"⚠️ Vuoi cancellare "
                    f"il treno {item.get('treno')}?"
                )

                col_conferma, col_annulla = st.columns(2)

                with col_conferma:

                    conferma_delete = st.button(
                        "🗑️ Sì, cancella",
                        key=f"conferma_m_{item_id}",
                        type="primary",
                        use_container_width=True
                    )

                with col_annulla:

                    annulla_delete = st.button(
                        "↩️ Annulla",
                        key=f"annulla_m_{item_id}",
                        use_container_width=True
                    )

                if annulla_delete:

                    st.session_state.pop(
                        "cancella_id",
                        None
                    )

                    st.rerun()

                if conferma_delete:

                    try:

                        (
                            supabase
                            .table(
                                "passaggio_consegne"
                            )
                            .delete()
                            .eq(
                                "id",
                                item_id
                            )
                            .execute()
                        )

                        st.session_state.pop(
                            "cancella_id",
                            None
                        )

                        carica_consegne.clear()

                        st.success(
                            "🗑️ Record cancellato."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "❌ Errore durante "
                            "la cancellazione."
                        )

                        st.code(str(e))

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
