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

            st.error(
                "❌ Errore lettura tabella "
                "passaggio_consegne"
            )

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

        Gestisce anche:

        1000/04
        1000/27
        """

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
    # MODIFICA
    # ==========================================================

    def modifica_consegna(
        id_record,
        dati_modificati
    ):

        try:

            (
                supabase
                .table("passaggio_consegne")
                .update(dati_modificati)
                .eq("id", id_record)
                .execute()
            )

            carica_consegne.clear()

            return True

        except Exception as e:

            st.error(
                "❌ Errore durante la modifica."
            )

            st.code(str(e))

            return False


    # ==========================================================
    # ELIMINA
    # ==========================================================

    def elimina_consegna(id_record):

        try:

            (
                supabase
                .table("passaggio_consegne")
                .delete()
                .eq("id", id_record)
                .execute()
            )

            carica_consegne.clear()

            return True

        except Exception as e:

            st.error(
                "❌ Errore durante l'eliminazione."
            )

            st.code(str(e))

            return False


    # ==========================================================
    # TITOLO
    # ==========================================================

    st.title(
        "🔄 Passaggio Consegne"
    )


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

    data_selezionata = str(
        data_consegna
    )


    # ==========================================================
    # FILTRA DATA + TURNO
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
        expanded=True
    ):

        with st.form(
            "form_passaggio_consegne",
            clear_on_submit=True
        ):

            st.markdown(
                "### Tipo"
            )


            # --------------------------------------------------
            # TIPO
            # --------------------------------------------------

            tipo = st.radio(
                "",
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

                stato = st.radio(
                    "Stato treno",
                    [
                        "🟢 DISP",
                        "🔴 OUT"
                    ],
                    horizontal=True,
                    index=0
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
                use_container_width=True
            )


        # ======================================================
        # ELABORAZIONE INSERIMENTO
        # ======================================================

        if inserisci:

            errore = False


            # --------------------------------------------------
            # CONTROLLO TRENO
            # --------------------------------------------------

            if not treno.strip():

                st.error(
                    "⚠️ Inserisci il numero del treno."
                )

                errore = True


            # --------------------------------------------------
            # CONTROLLO SERVIZIO
            # --------------------------------------------------

            if (
                not errore
                and tipo.startswith("🚆")
                and not servizio.strip()
            ):

                st.error(
                    "⚠️ Per un treno in uscita "
                    "inserisci il servizio."
                )

                errore = True


            # --------------------------------------------------
            # SALVATAGGIO
            # --------------------------------------------------

            if not errore:

                disp = (
                    stato == "🟢 DISP"
                )

                out = (
                    stato == "🔴 OUT"
                )


                if tipo.startswith("🚆"):

                    tipo_db = (
                        "TRENO IN USCITA"
                    )

                else:

                    tipo_db = (
                        "MANUTENZIONE / "
                        "LAVORAZIONE APERTA"
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


                try:

                    (
                        supabase
                        .table(
                            "passaggio_consegne"
                        )
                        .insert(nuovo)
                        .execute()
                    )


                    # ------------------------------------------
                    # SVUOTA CACHE
                    # ------------------------------------------

                    carica_consegne.clear()


                    st.success(
                        "✅ Treno aggiunto "
                        "al passaggio consegne."
                    )


                    # ------------------------------------------
                    # RICARICA
                    # ------------------------------------------

                    st.rerun()


                except Exception as e:

                    st.error(
                        "❌ Errore durante "
                        "l'inserimento."
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
                d

                for d in dati_consegna

                if d.get("id")
                == modifica_id
            ),
            None
        )


        if record_modifica:

            st.markdown(
                """
                <div style="
                    background-color:#fff3cd;
                    padding:12px;
                    border-radius:6px;
                    font-weight:bold;
                    margin-top:15px;
                    margin-bottom:15px;
                ">
                ✏️ MODIFICA PASSAGGIO CONSEGNE
                </div>
                """,
                unsafe_allow_html=True
            )


            with st.form(
                f"form_modifica_{modifica_id}"
            ):

                tipo_originale = (
                    record_modifica.get(
                        "tipo",
                        ""
                    )
                )


                tipo_modifica = st.radio(
                    "Tipo",
                    [
                        "🚆 TRENO IN USCITA",
                        "🛠️ MANUTENZIONE / "
                        "LAVORAZIONE APERTA"
                    ],
                    index=(
                        0

                        if tipo_originale
                        == "TRENO IN USCITA"

                        else 1
                    ),
                    horizontal=True
                )


                col1, col2, col3 = st.columns(3)


                # ------------------------------------------
                # TRENO
                # ------------------------------------------

                with col1:

                    treno_mod = st.text_input(
                        "🚆 Treno",
                        value=(
                            record_modifica.get(
                                "treno"
                            )
                            or ""
                        )
                    )


                    manutenzione_mod = st.text_input(
                        "🔧 Manutenzione",
                        value=(
                            record_modifica.get(
                                "manutenzione"
                            )
                            or ""
                        )
                    )


                # ------------------------------------------
                # SERVIZIO / BINARIO
                # ------------------------------------------

                with col2:

                    servizio_mod = st.text_input(
                        "🚉 Servizio",
                        value=(
                            record_modifica.get(
                                "servizio"
                            )
                            or ""
                        )
                    )


                    binario_mod = st.text_input(
                        "🛤️ Binario",
                        value=(
                            record_modifica.get(
                                "binario"
                            )
                            or ""
                        )
                    )


                # ------------------------------------------
                # ODL / STATO
                # ------------------------------------------

                with col3:

                    odl_mod = st.text_input(
                        "📋 N° ODL PADRE",
                        value=(
                            record_modifica.get(
                                "odl"
                            )
                            or ""
                        )
                    )


                    stato_mod = st.radio(
                        "Stato treno",
                        [
                            "🟢 DISP",
                            "🔴 OUT"
                        ],
                        index=(
                            0

                            if record_modifica.get(
                                "disp"
                            )

                            else 1
                        ),
                        horizontal=True
                    )


                # ------------------------------------------
                # LAVORAZIONI
                # ------------------------------------------

                lavorazioni_mod = st.text_area(
                    "📝 Lavorazioni aperte / Note",
                    value=(
                        record_modifica.get(
                            "lavorazioni"
                        )
                        or ""
                    )
                )


                # ------------------------------------------
                # PULSANTI
                # ------------------------------------------

                col_salva, col_annulla = st.columns(2)


                with col_salva:

                    salva_modifica = (
                        st.form_submit_button(
                            "💾 Salva modifiche",
                            use_container_width=True
                        )
                    )


                with col_annulla:

                    annulla_modifica = (
                        st.form_submit_button(
                            "❌ Annulla",
                            use_container_width=True
                        )
                    )


            # ==================================================
            # ANNULLA MODIFICA
            # ==================================================

            if annulla_modifica:

                del st.session_state[
                    "modifica_id"
                ]

                st.rerun()


            # ==================================================
            # SALVA MODIFICA
            # ==================================================

            if salva_modifica:

                errore_modifica = False


                if not treno_mod.strip():

                    st.error(
                        "⚠️ Inserisci il numero del treno."
                    )

                    errore_modifica = True


                if (
                    not errore_modifica
                    and tipo_modifica.startswith("🚆")
                    and not servizio_mod.strip()
                ):

                    st.error(
                        "⚠️ Per un treno in uscita "
                        "inserisci il servizio."
                    )

                    errore_modifica = True


                if not errore_modifica:

                    nuovo_tipo = (

                        "TRENO IN USCITA"

                        if tipo_modifica.startswith("🚆")

                        else

                        "MANUTENZIONE / "
                        "LAVORAZIONE APERTA"
                    )


                    nuovo_disp = (
                        stato_mod
                        == "🟢 DISP"
                    )


                    nuovo_out = (
                        stato_mod
                        == "🔴 OUT"
                    )


                    dati_modificati = {

                        "tipo":
                            nuovo_tipo,

                        "treno":
                            treno_mod.strip(),

                        "manutenzione":
                            manutenzione_mod.strip(),

                        "servizio":
                            servizio_mod.strip(),

                        "binario":
                            binario_mod.strip(),

                        "disp":
                            nuovo_disp,

                        "out":
                            nuovo_out,

                        "lavorazioni":
                            lavorazioni_mod.strip(),

                        "odl":
                            odl_mod.strip()
                    }


                    if modifica_consegna(
                        modifica_id,
                        dati_modificati
                    ):

                        del st.session_state[
                            "modifica_id"
                        ]


                        st.success(
                            "✅ Passaggio modificato."
                        )


                        st.rerun()


        else:

            # Il record non appartiene più alla
            # data/turno visualizzato

            del st.session_state[
                "modifica_id"
            ]


    # ==========================================================
    # CONFERMA ELIMINAZIONE
    # ==========================================================

    elimina_id = st.session_state.get(
        "elimina_id"
    )


    if elimina_id:

        record_elimina = next(
            (
                d

                for d in dati_consegna

                if d.get("id")
                == elimina_id
            ),
            None
        )


        if record_elimina:

            st.warning(
                f"⚠️ Vuoi eliminare il passaggio "
                f"del treno "
                f"**{record_elimina.get('treno', '-')}**?"
            )


            e1, e2 = st.columns(2)


            with e1:

                conferma_elimina = st.button(
                    "🗑️ Sì, elimina",
                    type="primary",
                    use_container_width=True
                )


            with e2:

                annulla_elimina = st.button(
                    "❌ Annulla",
                    use_container_width=True
                )


            if annulla_elimina:

                del st.session_state[
                    "elimina_id"
                ]

                st.rerun()


            if conferma_elimina:

                if elimina_consegna(
                    elimina_id
                ):

                    del st.session_state[
                        "elimina_id"
                    ]

                    st.success(
                        "✅ Passaggio eliminato."
                    )

                    st.rerun()


        else:

            del st.session_state[
                "elimina_id"
            ]


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
                1.4
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
                    1.4
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
                )
                or "-"
            )


            c8.write(
                item.get("odl")
                or "-"
            )


            # --------------------------------------------------
            # AZIONI
            # --------------------------------------------------

            az1, az2 = c9.columns(2)


            if az1.button(
                "✏️",
                key=f"modifica_uscita_{item['id']}",
                help="Modifica"
            ):

                st.session_state[
                    "modifica_id"
                ] = item["id"]

                st.rerun()


            if az2.button(
                "🗑️",
                key=f"elimina_uscita_{item['id']}",
                help="Elimina"
            ):

                st.session_state[
                    "elimina_id"
                ] = item["id"]

                st.rerun()


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
            "Nessuna manutenzione "
            "o lavorazione aperta."
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
                1.4
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
                    1.4
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
                )
                or "-"
            )


            c7.write(
                item.get("odl")
                or "-"
            )


            # --------------------------------------------------
            # AZIONI
            # --------------------------------------------------

            az1, az2 = c8.columns(2)


            if az1.button(
                "✏️",
                key=f"modifica_manutenzione_{item['id']}",
                help="Modifica"
            ):

                st.session_state[
                    "modifica_id"
                ] = item["id"]

                st.rerun()


            if az2.button(
                "🗑️",
                key=f"elimina_manutenzione_{item['id']}",
                help="Elimina"
            ):

                st.session_state[
                    "elimina_id"
                ] = item["id"]

                st.rerun()


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
