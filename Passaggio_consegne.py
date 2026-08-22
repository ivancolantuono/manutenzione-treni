import streamlit as st

from datetime import date, datetime
from zoneinfo import ZoneInfo

from db import supabase


# ==============================================================
# PAGINA PASSAGGIO CONSEGNE
# ==============================================================

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
            key="pc_data"
        )

    with col2:

        turno = st.selectbox(
            "🕐 Turno",
            [
                "Mattina",
                "Pomeriggio",
                "Notte"
            ],
            key="pc_turno"
        )

    with col3:

        responsabile = st.text_input(
            "👤 Responsabile",
            value=st.session_state.get(
                "utente",
                ""
            ),
            key="pc_responsabile"
        )

    # ==========================================================
    # CARICA DATI
    # ==========================================================

    dati = carica_consegne()

    data_selezionata = str(
        data_consegna
    )

    # ==========================================================
    # DATI DEL GIORNO / TURNO
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
                dati_consegna[0]
                .get("responsabile")
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
    # MODIFICA RECORD
    # ==========================================================

    modifica_id = st.session_state.get(
        "modifica_id"
    )

    if modifica_id is not None:

        record_modifica = next(
            (
                d for d in dati
                if str(d.get("id"))
                == str(modifica_id)
            ),
            None
        )

        if record_modifica:

            st.divider()

            st.markdown(
                "### ✏️ Modifica consegna"
            )

            # --------------------------------------------------
            # TIPO
            # --------------------------------------------------

            tipo_attuale = record_modifica.get(
                "tipo",
                "TRENO IN USCITA"
            )

            if tipo_attuale == "TRENO IN USCITA":

                indice_tipo = 0

            else:

                indice_tipo = 1

            tipo_modifica = st.radio(
                "Tipo",
                [
                    "🚆 TRENO IN USCITA",
                    "🛠️ MANUTENZIONE / LAVORAZIONE APERTA"
                ],
                index=indice_tipo,
                horizontal=True,
                key="edit_tipo"
            )

            # --------------------------------------------------
            # CAMPI
            # --------------------------------------------------

            e1, e2, e3 = st.columns(3)

            with e1:

                edit_treno = st.text_input(
                    "🚆 Treno",
                    value=record_modifica.get(
                        "treno"
                    ) or "",
                    key="edit_treno"
                )

                edit_manutenzione = st.text_input(
                    "🔧 Manutenzione",
                    value=record_modifica.get(
                        "manutenzione"
                    ) or "",
                    key="edit_manutenzione"
                )

            with e2:

                edit_servizio = st.text_input(
                    "🚉 Servizio",
                    value=record_modifica.get(
                        "servizio"
                    ) or "",
                    key="edit_servizio"
                )

                edit_binario = st.text_input(
                    "🛤️ Binario",
                    value=record_modifica.get(
                        "binario"
                    ) or "",
                    key="edit_binario"
                )

            with e3:

                edit_odl = st.text_input(
                    "📋 N° ODL PADRE",
                    value=record_modifica.get(
                        "odl"
                    ) or "",
                    key="edit_odl"
                )

                # ----------------------------------------------
                # STATO
                # ----------------------------------------------

                if record_modifica.get("disp"):

                    stato_default = 0

                elif record_modifica.get("out"):

                    stato_default = 1

                else:

                    stato_default = 0

                edit_stato = st.radio(
                    "Stato",
                    [
                        "🟢 DISP",
                        "🔴 OUT"
                    ],
                    index=stato_default,
                    horizontal=True,
                    key="edit_stato"
                )

            edit_lavorazioni = st.text_area(
                "📝 Lavorazioni aperte / Note",
                value=record_modifica.get(
                    "lavorazioni"
                ) or "",
                key="edit_lavorazioni"
            )

            # --------------------------------------------------
            # PULSANTI
            # --------------------------------------------------

            b1, b2 = st.columns(2)

            with b1:

                salva_modifica = st.button(
                    "💾 Salva modifica",
                    type="primary",
                    use_container_width=True,
                    key="salva_modifica"
                )

            with b2:

                annulla_modifica = st.button(
                    "❌ Annulla",
                    use_container_width=True,
                    key="annulla_modifica"
                )

            # --------------------------------------------------
            # ANNULLA
            # --------------------------------------------------

            if annulla_modifica:

                st.session_state.pop(
                    "modifica_id",
                    None
                )

                st.rerun()

            # --------------------------------------------------
            # SALVA
            # --------------------------------------------------

            if salva_modifica:

                if not edit_treno.strip():

                    st.error(
                        "⚠️ Inserisci il numero del treno."
                    )

                    st.stop()

                if (
                    tipo_modifica.startswith("🚆")
                    and not edit_servizio.strip()
                ):

                    st.error(
                        "⚠️ Per un treno in uscita "
                        "inserisci il servizio."
                    )

                    st.stop()

                if tipo_modifica.startswith("🚆"):

                    tipo_db_modifica = (
                        "TRENO IN USCITA"
                    )

                else:

                    tipo_db_modifica = (
                        "MANUTENZIONE / "
                        "LAVORAZIONE APERTA"
                    )

                edit_disp = (
                    edit_stato
                    == "🟢 DISP"
                )

                edit_out = (
                    edit_stato
                    == "🔴 OUT"
                )

                dati_modificati = {

                    "tipo":
                        tipo_db_modifica,

                    "treno":
                        edit_treno.strip(),

                    "manutenzione":
                        edit_manutenzione.strip(),

                    "servizio":
                        edit_servizio.strip(),

                    "binario":
                        edit_binario.strip(),

                    "disp":
                        edit_disp,

                    "out":
                        edit_out,

                    "lavorazioni":
                        edit_lavorazioni.strip(),

                    "odl":
                        edit_odl.strip()
                }

                try:

                    (
                        supabase
                        .table(
                            "passaggio_consegne"
                        )
                        .update(
                            dati_modificati
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
                        "✅ Consegna modificata."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ Errore durante la modifica."
                    )

                    st.code(str(e))

            st.divider()

    # ==========================================================
    # CONFERMA ELIMINAZIONE
    # ==========================================================

    elimina_id = st.session_state.get(
        "elimina_id"
    )

    if elimina_id is not None:

        record_elimina = next(
            (
                d for d in dati
                if str(d.get("id"))
                == str(elimina_id)
            ),
            None
        )

        if record_elimina:

            st.warning(
                "⚠️ Sei sicuro di voler eliminare "
                f"il treno **{record_elimina.get('treno', '-') }**?"
            )

            e1, e2 = st.columns(2)

            with e1:

                conferma_elimina = st.button(
                    "🗑️ Sì, elimina",
                    type="primary",
                    use_container_width=True,
                    key="conferma_elimina"
                )

            with e2:

                annulla_elimina = st.button(
                    "❌ Annulla",
                    use_container_width=True,
                    key="annulla_elimina"
                )

            if annulla_elimina:

                st.session_state.pop(
                    "elimina_id",
                    None
                )

                st.rerun()

            if conferma_elimina:

                try:

                    (
                        supabase
                        .table(
                            "passaggio_consegne"
                        )
                        .delete()
                        .eq(
                            "id",
                            elimina_id
                        )
                        .execute()
                    )

                    carica_consegne.clear()

                    st.session_state.pop(
                        "elimina_id",
                        None
                    )

                    st.success(
                        "🗑️ Consegna eliminata."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ Errore durante l'eliminazione."
                    )

                    st.code(str(e))

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
            "",
            [
                "🚆 TRENO IN USCITA",
                "🛠️ MANUTENZIONE / LAVORAZIONE APERTA"
            ],
            horizontal=True,
            key="pc_tipo"
        )

        c1, c2, c3 = st.columns(3)

        # ------------------------------------------------------
        # COLONNA 1
        # ------------------------------------------------------

        with c1:

            treno = st.text_input(
                "🚆 Treno",
                placeholder="Es. 1000/27",
                key="pc_treno"
            )

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="Es. MC",
                key="pc_manutenzione"
            )

        # ------------------------------------------------------
        # COLONNA 2
        # ------------------------------------------------------

        with c2:

            servizio = st.text_input(
                "🚉 Servizio",
                placeholder="Es. 89705",
                key="pc_servizio"
            )

            binario = st.text_input(
                "🛤️ Binario",
                placeholder="Es. MAV 9",
                key="pc_binario"
            )

        # ------------------------------------------------------
        # COLONNA 3
        # ------------------------------------------------------

        with c3:

            odl = st.text_input(
                "📋 N° ODL PADRE",
                placeholder="Es. 100014925813",
                key="pc_odl"
            )

            stato = st.radio(
                "Stato treno",
                [
                    "🟢 DISP",
                    "🔴 OUT"
                ],
                horizontal=True,
                key="pc_stato"
            )

        # ------------------------------------------------------
        # STATO
        # ------------------------------------------------------

        disp = (
            stato
            == "🟢 DISP"
        )

        out = (
            stato
            == "🔴 OUT"
        )

        # ------------------------------------------------------
        # LAVORAZIONI
        # ------------------------------------------------------

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

            if not treno.strip():

                st.error(
                    "⚠️ Inserisci il numero del treno."
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

            # --------------------------------------------------
            # INSERT SUPABASE
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

                # --------------------------------------------------
                # SVUOTA CAMPI
                # --------------------------------------------------

                st.session_state[
                    "pc_treno"
                ] = ""

                st.session_state[
                    "pc_manutenzione"
                ] = ""

                st.session_state[
                    "pc_servizio"
                ] = ""

                st.session_state[
                    "pc_binario"
                ] = ""

                st.session_state[
                    "pc_odl"
                ] = ""

                st.session_state[
                    "pc_lavorazioni"
                ] = ""

                st.session_state[
                    "pc_stato"
                ] = "🟢 DISP"

                # --------------------------------------------------
                # CACHE
                # --------------------------------------------------

                carica_consegne.clear()

                st.success(
                    "✅ Treno aggiunto al passaggio consegne."
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
    # DIVISORE
    # ==========================================================

    st.divider()

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
    # TITOLO TRENI IN USCITA
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
                0.7
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
        h9.markdown("")

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
                    0.7
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

            # --------------------------------------------------
            # STATO
            # --------------------------------------------------

            if (
                item.get("disp")
                and not item.get("out")
            ):

                c5.markdown("🟢")

                c6.markdown("⚪")

            elif (
                item.get("out")
                and not item.get("disp")
            ):

                c5.markdown("⚪")

                c6.markdown("🔴")

            elif (
                item.get("disp")
                and item.get("out")
            ):

                c5.markdown("⚠️")
                c6.markdown("⚠️")

            else:

                c5.markdown("⚪")
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
            # MENU AZIONI
            # --------------------------------------------------

            with c9:

                with st.popover(
                    "⋮"
                ):

                    if st.button(
                        "✏️ Modifica",
                        key=(
                            f"mod_uscita_"
                            f"{item['id']}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state[
                            "modifica_id"
                        ] = item["id"]

                        st.rerun()

                    if st.button(
                        "🗑️ Elimina",
                        key=(
                            f"del_uscita_"
                            f"{item['id']}"
                        ),
                        use_container_width=True
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

    # ==========================================================
    # TITOLO
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
                0.7
            ]
        )

        h1.markdown("**TRENO**")
        h2.markdown("**MANUTENZIONE**")
        h3.markdown("**BINARIO**")
        h4.markdown("**DISP**")
        h5.markdown("**OUT**")
        h6.markdown("**LAVORAZIONI APERTE / NOTE**")
        h7.markdown("**N° ODL PADRE**")
        h8.markdown("")

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
                    0.7
                ]
            )

            c1.write(
                item.get("treno") or "-"
            )

            c2.write(
                item.get(
                    "manutenzione"
                ) or "-"
            )

            c3.write(
                item.get(
                    "binario"
                ) or "-"
            )

            # --------------------------------------------------
            # STATO
            # --------------------------------------------------

            if (
                item.get("disp")
                and not item.get("out")
            ):

                c4.markdown("🟢")

                c5.markdown("⚪")

            elif (
                item.get("out")
                and not item.get("disp")
            ):

                c4.markdown("⚪")

                c5.markdown("🔴")

            elif (
                item.get("disp")
                and item.get("out")
            ):

                c4.markdown("⚠️")

                c5.markdown("⚠️")

            else:

                c4.markdown("⚪")
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
            # MENU AZIONI
            # --------------------------------------------------

            with c8:

                with st.popover(
                    "⋮"
                ):

                    if st.button(
                        "✏️ Modifica",
                        key=(
                            f"mod_manutenzione_"
                            f"{item['id']}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state[
                            "modifica_id"
                        ] = item["id"]

                        st.rerun()

                    if st.button(
                        "🗑️ Elimina",
                        key=(
                            f"del_manutenzione_"
                            f"{item['id']}"
                        ),
                        use_container_width=True
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
