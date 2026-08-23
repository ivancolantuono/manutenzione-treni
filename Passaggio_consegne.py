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
                numeri.append(
                    int(parte)
                )

            except:

                numeri.append(
                    999999
                )

        return tuple(numeri)

    # ----------------------------------------------------------
    # TIPO DATABASE
    # ----------------------------------------------------------

    def tipo_database(tipo):

        if tipo.startswith("🚆"):

            return "TRENO IN USCITA"

        return (
            "MANUTENZIONE / "
            "LAVORAZIONE APERTA"
        )

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
    # CARICAMENTO DATI
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
    # INFORMAZIONI PASSAGGIO
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

        # ======================================================
        # FORM INSERIMENTO
        # ======================================================

        with st.form(
            "passaggio_consegne_form",
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
        # ELABORAZIONE INSERIMENTO
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

                tipo_db = tipo_database(
                    tipo
                )

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

                # ----------------------------------------------
                # INSERT SUPABASE
                # ----------------------------------------------

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
            margin-bottom:10px;
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

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns(
            [
                1.2,
                1.5,
                1.3,
                1.3,
                0.8,
                0.8,
                3,
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

        st.divider()

        # ------------------------------------------------------
        # RIGHE
        # ------------------------------------------------------

        for item in treni_uscita:

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(
                [
                    1.2,
                    1.5,
                    1.3,
                    1.3,
                    0.8,
                    0.8,
                    3,
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
                item.get("lavorazioni") or "-"
            )

            c8.write(
                item.get("odl") or "-"
            )

            # --------------------------------------------------
            # MODIFICA / CANCELLA
            # --------------------------------------------------

            with st.expander(
                f"✏️ Modifica / 🗑️ "
                f"{item.get('treno', '-')}"
            ):

                with st.form(
                    f"modifica_treno_{item.get('id')}"
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

                    col_save, col_cancel = st.columns(2)

                    with col_save:

                        salva_modifica = st.form_submit_button(
                            "💾 Salva modifica",
                            type="primary",
                            use_container_width=True
                        )

                    with col_cancel:

                        pass

                if salva_modifica:

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
                                    item.get("id")
                                )
                                .execute()
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

                # --------------------------------------------------
                # CANCELLAZIONE
                # --------------------------------------------------

                st.divider()

                conferma = st.checkbox(
                    "Confermo di voler cancellare questo record.",
                    key=f"conferma_delete_{item.get('id')}"
                )

                if st.button(
                    "🗑️ Cancella record",
                    key=f"delete_{item.get('id')}",
                    type="secondary",
                    disabled=not conferma,
                    use_container_width=True
                ):

                    try:

                        (
                            supabase
                            .table(
                                "passaggio_consegne"
                            )
                            .delete()
                            .eq(
                                "id",
                                item.get("id")
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
            margin-bottom:10px;
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

        h1, h2, h3, h4, h5, h6, h7 = st.columns(
            [
                1.2,
                1.8,
                1.5,
                0.8,
                0.8,
                4,
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

        st.divider()

        # ------------------------------------------------------
        # RIGHE
        # ------------------------------------------------------

        for item in manutenzioni:

            c1, c2, c3, c4, c5, c6, c7 = st.columns(
                [
                    1.2,
                    1.8,
                    1.5,
                    0.8,
                    0.8,
                    4,
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
                item.get("lavorazioni") or "-"
            )

            c7.write(
                item.get("odl") or "-"
            )

            # --------------------------------------------------
            # MODIFICA
            # --------------------------------------------------

            with st.expander(
                f"✏️ Modifica / 🗑️ "
                f"{item.get('treno', '-')}"
            ):

                with st.form(
                    f"modifica_manutenzione_{item.get('id')}"
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

                    salva_modifica = st.form_submit_button(
                        "💾 Salva modifica",
                        type="primary",
                        use_container_width=True
                    )

                if salva_modifica:

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
                                    item.get("id")
                                )
                                .execute()
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

                # --------------------------------------------------
                # CANCELLAZIONE
                # --------------------------------------------------

                st.divider()

                conferma = st.checkbox(
                    "Confermo di voler cancellare questo record.",
                    key=f"conferma_delete_m_{item.get('id')}"
                )

                if st.button(
                    "🗑️ Cancella record",
                    key=f"delete_m_{item.get('id')}",
                    type="secondary",
                    disabled=not conferma,
                    use_container_width=True
                ):

                    try:

                        (
                            supabase
                            .table(
                                "passaggio_consegne"
                            )
                            .delete()
                            .eq(
                                "id",
                                item.get("id")
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
