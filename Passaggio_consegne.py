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


    def pallino_colore(attivo, colore):

        if attivo:

            return f"""
                <span style="
                    display:inline-block;
                    width:13px;
                    height:13px;
                    background-color:{colore};
                    border-radius:50%;
                    border:1px solid rgba(0,0,0,0.25);
                "></span>
            """

        return """
            <span style="
                display:inline-block;
                width:13px;
                height:13px;
                background-color:#e0e0e0;
                border-radius:50%;
                border:1px solid #999;
            "></span>
        """


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
            f"""
            📅 **Data:** 
            {data_consegna.strftime("%d/%m/%Y")}
            """
        )


    with col_info2:

        st.markdown(
            f"""
            🕐 **Turno:** {turno}
            """
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
                f"""
                👤 **Responsabile:** 
                {responsabile_salvato}
                """
            )

        else:

            st.markdown(
                f"""
                👤 **Responsabile:** 
                {responsabile or "-"}
                """
            )


    # ==========================================================
    # AGGIUNGI TRENO
    # ==========================================================

    with st.expander(
        "➕ Aggiungi treno",
        expanded=True
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
            horizontal=True
        )


        # ======================================================
        # DATI TRENO
        # ======================================================

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


        # ======================================================
        # LAVORAZIONI
        # ======================================================

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
            # SALVATAGGIO SUPABASE
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

                st.code(
                    str(e)
                )


    # ==========================================================
    # NESSUN DATO PER DATA / TURNO
    # ==========================================================

    if not dati_consegna:

        st.divider()

        st.info(
            f"""
            📭 Nessuna consegna presente per

            **{data_consegna.strftime("%d/%m/%Y")}**

            turno **{turno}**.
            """
        )

        return


    # ==========================================================
    # ==========================================================
    # 🚆 TRENI IN USCITA
    # ==========================================================
    # ==========================================================

    treni_uscita = [

        d for d in dati_consegna

        if d.get("tipo")
        == "TRENO IN USCITA"

    ]


    # ORDINA I TRENI

    treni_uscita = sorted(
        treni_uscita,
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
            border:1px solid #8faec5;
            margin-top:20px;
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
        # COSTRUZIONE RIGHE
        # ======================================================

        righe_html = ""


        for item in treni_uscita:

            treno = (
                item.get("treno")
                or "-"
            )

            manutenzione = (
                item.get("manutenzione")
                or "-"
            )

            servizio = (
                item.get("servizio")
                or "-"
            )

            binario = (
                item.get("binario")
                or "-"
            )

            lavorazioni = (
                item.get("lavorazioni")
                or "-"
            )

            odl = (
                item.get("odl")
                or "-"
            )


            # DISP

            disp_html = pallino_colore(
                item.get("disp"),
                "#20a84b"
            )


            # OUT

            out_html = pallino_colore(
                item.get("out"),
                "#e53935"
            )


            righe_html += f"""

            <tr>

                <td class="cella treno">
                    {treno}
                </td>

                <td class="cella">
                    {manutenzione}
                </td>

                <td class="cella">
                    {servizio}
                </td>

                <td class="cella">
                    {binario}
                </td>

                <td class="cella centro">
                    {disp_html}
                </td>

                <td class="cella centro">
                    {out_html}
                </td>

                <td class="cella note">
                    {lavorazioni}
                </td>

                <td class="cella odl">
                    {odl}
                </td>

            </tr>

            """


        # ======================================================
        # TABELLA TRENI USCITA
        # ======================================================

        tabella_uscita = f"""

        <style>

            .tabella-consegne {{
                width:100%;
                border-collapse:collapse;
                table-layout:fixed;
                font-size:14px;
                background-color:white;
            }}


            .tabella-consegne th {{

                background-color:#e8eef3;

                color:#222;

                font-weight:bold;

                text-align:center;

                vertical-align:middle;

                border:1px solid #555;

                padding:10px 6px;

            }}


            .tabella-consegne td {{

                border:1px solid #777;

                padding:10px 7px;

                vertical-align:middle;

                color:#222;

                background-color:white;

                word-wrap:break-word;

                overflow-wrap:break-word;

            }}


            .tabella-consegne tbody tr:hover td {{

                background-color:#f4f8fb;

            }}


            .tabella-consegne .centro {{

                text-align:center;

            }}


            .tabella-consegne .treno {{

                text-align:center;

                font-weight:bold;

            }}


            .tabella-consegne .note {{

                text-align:left;

                white-space:normal;

            }}


            .tabella-consegne .odl {{

                text-align:center;

                word-break:break-all;

            }}

        </style>


        <div style="
            width:100%;
            overflow-x:auto;
        ">

            <table class="tabella-consegne">

                <colgroup>

                    <col style="width:12%;">
                    <col style="width:15%;">
                    <col style="width:13%;">
                    <col style="width:13%;">
                    <col style="width:7%;">
                    <col style="width:7%;">
                    <col style="width:21%;">
                    <col style="width:12%;">

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

                    {righe_html}

                </tbody>

            </table>

        </div>

        """


        st.markdown(
            tabella_uscita,
            unsafe_allow_html=True
        )


    # ==========================================================
    # ==========================================================
    # 🛠️ MANUTENZIONE / LAVORAZIONI APERTE
    # ==========================================================
    # ==========================================================

    manutenzioni = [

        d for d in dati_consegna

        if d.get("tipo")
        == "MANUTENZIONE / LAVORAZIONE APERTA"

    ]


    # ORDINA I TRENI

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
            border:1px solid #8faec5;
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
        # COSTRUZIONE RIGHE
        # ======================================================

        righe_html = ""


        for item in manutenzioni:

            treno = (
                item.get("treno")
                or "-"
            )

            manutenzione = (
                item.get("manutenzione")
                or "-"
            )

            binario = (
                item.get("binario")
                or "-"
            )

            lavorazioni = (
                item.get("lavorazioni")
                or "-"
            )

            odl = (
                item.get("odl")
                or "-"
            )


            # DISP

            disp_html = pallino_colore(
                item.get("disp"),
                "#20a84b"
            )


            # OUT

            out_html = pallino_colore(
                item.get("out"),
                "#e53935"
            )


            # --------------------------------------------------
            # RIGA
            # --------------------------------------------------

            righe_html += f"""

            <tr>

                <td class="cella treno">
                    {treno}
                </td>

                <td class="cella">
                    {manutenzione}
                </td>

                <td class="cella">
                    {binario}
                </td>

                <td class="cella centro">
                    {disp_html}
                </td>

                <td class="cella centro">
                    {out_html}
                </td>

                <td class="cella note">
                    {lavorazioni}
                </td>

                <td class="cella odl">
                    {odl}
                </td>

            </tr>

            """


        # ======================================================
        # TABELLA MANUTENZIONE
        # ======================================================

        tabella_manutenzione = f"""

        <style>

            .tabella-manutenzione {{

                width:100%;

                border-collapse:collapse;

                table-layout:fixed;

                font-size:14px;

                background-color:white;

            }}


            .tabella-manutenzione th {{

                background-color:#e8eef3;

                color:#222;

                font-weight:bold;

                text-align:center;

                vertical-align:middle;

                border:1px solid #555;

                padding:10px 6px;

            }}


            .tabella-manutenzione td {{

                border:1px solid #777;

                padding:10px 7px;

                vertical-align:middle;

                color:#222;

                background-color:white;

                word-wrap:break-word;

                overflow-wrap:break-word;

            }}


            .tabella-manutenzione tbody tr:hover td {{

                background-color:#f4f8fb;

            }}


            .tabella-manutenzione .centro {{

                text-align:center;

            }}


            .tabella-manutenzione .treno {{

                text-align:center;

                font-weight:bold;

            }}


            .tabella-manutenzione .note {{

                text-align:left;

                white-space:normal;

            }}


            .tabella-manutenzione .odl {{

                text-align:center;

                word-break:break-all;

            }}

        </style>


        <div style="
            width:100%;
            overflow-x:auto;
        ">

            <table class="tabella-manutenzione">

                <colgroup>

                    <col style="width:12%;">
                    <col style="width:17%;">
                    <col style="width:14%;">
                    <col style="width:7%;">
                    <col style="width:7%;">
                    <col style="width:31%;">
                    <col style="width:12%;">

                </colgroup>


                <thead>

                    <tr>

                        <th>
                            TRENO
                        </th>

                        <th>
                            MANUTENZIONE
                        </th>

                        <th>
                            BINARIO
                        </th>

                        <th>
                            DISP
                        </th>

                        <th>
                            OUT
                        </th>

                        <th>
                            LAVORAZIONI APERTE / NOTE
                        </th>

                        <th>
                            N° ODL PADRE
                        </th>

                    </tr>

                </thead>


                <tbody>

                    {righe_html}

                </tbody>

            </table>

        </div>

        """


        st.markdown(
            tabella_manutenzione,
            unsafe_allow_html=True
        )


    # ==========================================================
    # RIEPILOGO
    # ==========================================================

    st.divider()


    st.caption(
        f"""
        📅 Consegna del
        **{data_consegna.strftime("%d/%m/%Y")}**
        &nbsp;&nbsp;|&nbsp;&nbsp;

        🕐 Turno: **{turno}**
        &nbsp;&nbsp;|&nbsp;&nbsp;

        🚆 Treni in uscita:
        **{len(treni_uscita)}**
        &nbsp;&nbsp;|&nbsp;&nbsp;

        🛠️ Lavorazioni aperte:
        **{len(manutenzioni)}**
        """
    )
