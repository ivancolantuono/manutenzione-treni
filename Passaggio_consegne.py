import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
from db import supabase
import html

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

    def carica_consegne():

        try:

            res = (
                supabase
                .table("passaggio_consegne")
                .select("*")
                .order("created_at", desc=False)
                .execute()
            )

            return res.data or []

        except Exception as e:

            st.error("❌ Errore lettura passaggio_consegne")
            st.code(str(e))

            return []

    # ----------------------------------------------------------
    # FORMAT DATA
    # ----------------------------------------------------------

    def formatta_data(data_val):

        if not data_val:
            return "-"

        try:
            return datetime.fromisoformat(
                str(data_val)
            ).strftime("%d/%m/%Y %H:%M")

        except:

            return str(data_val)

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

    st.divider()

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

        # ------------------------------------------------------
        # CAMPI
        # ------------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            treno = st.text_input(
                "🚆 Treno",
                placeholder="Es. 1000/27"
            )

            manutenzione = st.text_input(
                "🔧 Manutenzione",
                placeholder="Es. MC"
            )

        with col2:

            servizio = st.text_input(
                "🚉 Servizio",
                placeholder="Es. 89705"
            )

            binario = st.text_input(
                "🛤️ Binario",
                placeholder="Es. MAV 9"
            )

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

            # --------------------------------------------------
            # CONTROLLI
            # --------------------------------------------------

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
            # RECORD
            # --------------------------------------------------

            nuovo = {

                "data_consegna":
                    str(data_consegna),

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
            # SALVATAGGIO
            # --------------------------------------------------

            try:

                supabase \
                    .table("passaggio_consegne") \
                    .insert(nuovo) \
                    .execute()

                st.success(
                    "✅ Treno aggiunto al passaggio consegne."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "❌ Errore durante l'inserimento."
                )

                st.code(str(e))

    # ==========================================================
    # CARICAMENTO DATI
    # ==========================================================

    dati = carica_consegne()

    # ==========================================================
    # FILTRO DATA
    # ==========================================================

    data_selezionata = str(data_consegna)

    dati_giorno = [

        d for d in dati

        if str(
            d.get("data_consegna", "")
        ) == data_selezionata

    ]

    # ==========================================================
    # INFORMAZIONI GIORNATA
    # ==========================================================

    st.markdown(
        f"""
        <div style="
            background:#e8f1f8;
            border:1px solid #b7c9d6;
            border-radius:6px;
            padding:10px 14px;
            margin-top:10px;
            margin-bottom:15px;
        ">

            <b>📅 Data:</b>
            {data_selezionata}

            &nbsp;&nbsp;&nbsp;

            <b>🕐 Turno:</b>
            {turno}

            &nbsp;&nbsp;&nbsp;

            <b>👤 Responsabile:</b>
            {responsabile or "-"}

        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # SE NON CI SONO DATI
    # ==========================================================

    if not dati_giorno:

        st.info(
            "ℹ️ Nessun passaggio di consegne "
            "presente per questa data."
        )

        return

    # ==========================================================
    # CSS TABELLE
    # ==========================================================

    st.markdown(
        """
        <style>

        .consegne-table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            margin-top: 8px;
            margin-bottom: 25px;
            font-size: 14px;
        }

        .consegne-table th {
            background-color: #d9eaf7;
            color: #1f1f1f;
            border: 1px solid #888888;
            padding: 8px 6px;
            text-align: center;
            font-weight: bold;
            vertical-align: middle;
        }

        .consegne-table td {
            border: 1px solid #999999;
            padding: 8px 6px;
            text-align: center;
            vertical-align: middle;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        .consegne-table td.note {
            text-align: left;
        }

        .sezione-consegne {
            background-color: #b7d7f0;
            border: 1px solid #8caec7;
            padding: 9px;
            text-align: center;
            font-weight: bold;
            border-radius: 4px;
            margin-top: 20px;
        }

        .pallino-verde {
            color: #16a34a;
            font-size: 22px;
            line-height: 1;
        }

        .pallino-rosso {
            color: #dc2626;
            font-size: 22px;
            line-height: 1;
        }

        .pallino-vuoto {
            color: #cfcfcf;
            font-size: 18px;
            line-height: 1;
        }

        .odl {
            color: #16704a;
            font-weight: bold;
            text-decoration: underline;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # TRENI IN USCITA
    # ==========================================================

    treni_uscita = [

        d for d in dati_giorno

        if d.get("tipo")
        == "TRENO IN USCITA"

    ]

    st.markdown(
        """
        <div class="sezione-consegne">
            🚆 TRENI IN USCITA
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------
    # NESSUN TRENO
    # ----------------------------------------------------------

    if not treni_uscita:

        st.info(
            "Nessun treno in uscita."
        )

    else:

        # ------------------------------------------------------
        # TABELLA
        # ------------------------------------------------------

        html = """

        <table class="consegne-table">

            <colgroup>

                <col style="width:10%">
                <col style="width:15%">
                <col style="width:11%">
                <col style="width:12%">
                <col style="width:7%">
                <col style="width:7%">
                <col style="width:25%">
                <col style="width:13%">

            </colgroup>

            <thead>

                <tr>

                    <th>TRENO</th>
                    <th>MANUTENZIONE</th>
                    <th>SERVIZIO</th>
                    <th>BINARIO</th>
                    <th>DISP</th>
                    <th>OUT</th>
                    <th>LAVORAZIONI / NOTE</th>
                    <th>N° ODL PADRE</th>

                </tr>

            </thead>

            <tbody>
        """

        for item in treni_uscita:

            treno_val = (
                item.get("treno") or "-"
            )

            manutenzione_val = (
                item.get("manutenzione") or "-"
            )

            servizio_val = (
                item.get("servizio") or "-"
            )

            binario_val = (
                item.get("binario") or "-"
            )

            lavorazioni_val = (
                item.get("lavorazioni") or "-"
            )

            odl_val = (
                item.get("odl") or "-"
            )

            # --------------------------------------------------
            # DISP
            # --------------------------------------------------

            if item.get("disp"):

                disp_html = (
                    '<span class="pallino-verde">●</span>'
                )

            else:

                disp_html = (
                    '<span class="pallino-vuoto">●</span>'
                )

            # --------------------------------------------------
            # OUT
            # --------------------------------------------------

            if item.get("out"):

                out_html = (
                    '<span class="pallino-rosso">●</span>'
                )

            else:

                out_html = (
                    '<span class="pallino-vuoto">●</span>'
                )

            # --------------------------------------------------
            # ODL
            # --------------------------------------------------

            if item.get("odl"):

                odl_html = (
                    f'<span class="odl">{odl_val}</span>'
                )

            else:

                odl_html = "-"

            html += f"""

                <tr>

                    <td>{treno_val}</td>

                    <td>{manutenzione_val}</td>

                    <td>{servizio_val}</td>

                    <td>{binario_val}</td>

                    <td>{disp_html}</td>

                    <td>{out_html}</td>

                    <td class="note">
                        {lavorazioni_val}
                    </td>

                    <td>{odl_html}</td>

                </tr>

            """

        html += """

            </tbody>

        </table>

        """

        st.markdown(
            html,
            unsafe_allow_html=True
        )

    # ==========================================================
    # MANUTENZIONE / LAVORAZIONI APERTE
    # ==========================================================

    manutenzioni = [

        d for d in dati_giorno

        if d.get("tipo")
        == "MANUTENZIONE / LAVORAZIONE APERTA"

    ]

    st.markdown(
        """
        <div class="sezione-consegne">
            🛠️ MANUTENZIONE / LAVORAZIONI APERTE
        </div>
        """,
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------
    # NESSUNA MANUTENZIONE
    # ----------------------------------------------------------

    if not manutenzioni:

        st.info(
            "Nessuna manutenzione o lavorazione aperta."
        )

    else:

        # ------------------------------------------------------
        # TABELLA
        # ------------------------------------------------------

        html = """

        <table class="consegne-table">

            <colgroup>

                <col style="width:12%">
                <col style="width:20%">
                <col style="width:15%">
                <col style="width:8%">
                <col style="width:8%">
                <col style="width:24%">
                <col style="width:13%">

            </colgroup>

            <thead>

                <tr>

                    <th>TRENO</th>
                    <th>MANUTENZIONE</th>
                    <th>BINARIO</th>
                    <th>DISP</th>
                    <th>OUT</th>
                    <th>LAVORAZIONI APERTE / NOTE</th>
                    <th>N° ODL PADRE</th>

                </tr>

            </thead>

            <tbody>
        """

        for item in manutenzioni:

            treno_val = (
                item.get("treno") or "-"
            )

            manutenzione_val = (
                item.get("manutenzione") or "-"
            )

            binario_val = (
                item.get("binario") or "-"
            )

            lavorazioni_val = (
                item.get("lavorazioni") or "-"
            )

            odl_val = (
                item.get("odl") or "-"
            )

            # --------------------------------------------------
            # DISP
            # --------------------------------------------------

            if item.get("disp"):

                disp_html = (
                    '<span class="pallino-verde">●</span>'
                )

            else:

                disp_html = (
                    '<span class="pallino-vuoto">●</span>'
                )

            # --------------------------------------------------
            # OUT
            # --------------------------------------------------

            if item.get("out"):

                out_html = (
                    '<span class="pallino-rosso">●</span>'
                )

            else:

                out_html = (
                    '<span class="pallino-vuoto">●</span>'
                )

            # --------------------------------------------------
            # ODL
            # --------------------------------------------------

            if item.get("odl"):

                odl_html = (
                    f'<span class="odl">{odl_val}</span>'
                )

            else:

                odl_html = "-"

            # --------------------------------------------------
            # RIGA
            # --------------------------------------------------

            html += f"""

                <tr>

                    <td>{treno_val}</td>

                    <td>{manutenzione_val}</td>

                    <td>{binario_val}</td>

                    <td>{disp_html}</td>

                    <td>{out_html}</td>

                    <td class="note">
                        {lavorazioni_val}
                    </td>

                    <td>{odl_html}</td>

                </tr>

            """

        html += """

            </tbody>

        </table>

        """

        st.markdown(
            html,
            unsafe_allow_html=True
        )

    # ==========================================================
    # RIEPILOGO TURNO
    # ==========================================================

    turni_presenti = sorted(
        set(
            str(d.get("turno"))
            for d in dati_giorno
            if d.get("turno")
        )
    )

    if turni_presenti:

        st.caption(
            "🕐 Turni presenti: "
            + ", ".join(turni_presenti)
        )
