import streamlit as st
import pandas as pd
from datetime import date, datetime
from zoneinfo import ZoneInfo
from db import supabase
import html

def Passaggio_consegne_page():

    import html
    from datetime import date, datetime
    from zoneinfo import ZoneInfo

    # ==========================================================
    # FUNZIONI
    # ==========================================================

    def ora_italia():
        return datetime.now(
            ZoneInfo("Europe/Rome")
        ).isoformat()

    # ----------------------------------------------------------
    # CARICA DATI
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
    # ORDINA TRENI
    # ----------------------------------------------------------

    def chiave_treno(item):

        valore = str(
            item.get("treno", "")
        ).strip()

        # Esempi:
        # 1000/01
        # 1000/27
        # 1000/100

        parti = (
            valore
            .replace("-", "/")
            .split("/")
        )

        risultato = []

        for parte in parti:

            try:

                risultato.append(
                    int(parte)
                )

            except:

                risultato.append(
                    999999
                )

        return tuple(risultato)


    # ----------------------------------------------------------
    # ESCAPE HTML
    # ----------------------------------------------------------

    def safe(value):

        if value is None:
            return "-"

        valore = str(value).strip()

        if not valore:
            return "-"

        return html.escape(valore)


    # ==========================================================
    # TABELLA STILE EXCEL
    # ==========================================================

    def crea_tabella_excel(
        titolo,
        dati_tabella,
        tipo_tabella
    ):

        # ------------------------------------------------------
        # COLONNE
        # ------------------------------------------------------

        if tipo_tabella == "uscita":

            colonne = [

                ("TRENO", "12%"),

                ("MANUTENZIONE", "15%"),

                ("SERVIZIO", "13%"),

                ("BINARIO", "13%"),

                ("DISP", "7%"),

                ("OUT", "7%"),

                ("LAVORAZIONI / NOTE", "21%"),

                ("N° ODL PADRE", "12%")

            ]

        else:

            colonne = [

                ("TRENO", "12%"),

                ("MANUTENZIONE", "17%"),

                ("BINARIO", "14%"),

                ("DISP", "7%"),

                ("OUT", "7%"),

                ("LAVORAZIONI APERTE / NOTE", "31%"),

                ("N° ODL PADRE", "12%")

            ]


        # ------------------------------------------------------
        # TITOLO
        # ------------------------------------------------------

        st.markdown(
            f"""
            <div style="
                width:100%;
                box-sizing:border-box;
                background:#b7d7f0;
                border:2px solid #4f81a5;
                padding:11px;
                text-align:center;
                font-weight:bold;
                font-size:15px;
                margin-top:22px;
                margin-bottom:0px;
                color:#111;
            ">
                {titolo}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ------------------------------------------------------
        # NESSUN DATO
        # ------------------------------------------------------

        if not dati_tabella:

            st.markdown(
                """
                <div style="
                    border-left:2px solid #555;
                    border-right:2px solid #555;
                    border-bottom:2px solid #555;
                    padding:14px;
                    color:#666;
                    background:#fafafa;
                ">
                    Nessun dato presente.
                </div>
                """,
                unsafe_allow_html=True
            )

            return


        # ------------------------------------------------------
        # ORDINA
        # ------------------------------------------------------

        dati_tabella = sorted(
            dati_tabella,
            key=chiave_treno
        )


        # ------------------------------------------------------
        # INIZIO TABELLA
        # ------------------------------------------------------

        html_tabella = f"""
        <div style="
            width:100%;
            overflow-x:auto;
            margin:0;
            padding:0;
        ">

        <table style="
            width:100%;
            min-width:850px;
            border-collapse:collapse;
            border-spacing:0;
            table-layout:fixed;
            font-family:Arial,sans-serif;
            font-size:14px;
            background:#ffffff;
            color:#111111;
        ">

        <thead>

        <tr>
        """


        # ------------------------------------------------------
        # INTESTAZIONE
        # ------------------------------------------------------

        for nome, larghezza in colonne:

            html_tabella += f"""
            <th style="
                width:{larghezza};
                box-sizing:border-box;
                border:2px solid #555555;
                background:#e5edf4;
                color:#111111;
                padding:10px 5px;
                text-align:center;
                font-weight:bold;
                vertical-align:middle;
                height:42px;
            ">
                {nome}
            </th>
            """


        html_tabella += """
        </tr>

        </thead>

        <tbody>
        """


        # ------------------------------------------------------
        # RIGHE
        # ------------------------------------------------------

        for item in dati_tabella:

            html_tabella += """
            <tr>
            """


            # ==================================================
            # TRENO
            # ==================================================

            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 6px;
                text-align:center;
                font-weight:bold;
                background:#ffffff;
                color:#111111;
                vertical-align:middle;
                height:48px;
            ">
                {safe(item.get("treno"))}
            </td>
            """


            # ==================================================
            # MANUTENZIONE
            # ==================================================

            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 6px;
                text-align:center;
                background:#ffffff;
                color:#111111;
                vertical-align:middle;
            ">
                {safe(item.get("manutenzione"))}
            </td>
            """


            # ==================================================
            # SERVIZIO
            # ==================================================

            if tipo_tabella == "uscita":

                html_tabella += f"""
                <td style="
                    border:2px solid #555555;
                    padding:12px 6px;
                    text-align:center;
                    background:#ffffff;
                    color:#111111;
                    vertical-align:middle;
                ">
                    {safe(item.get("servizio"))}
                </td>
                """


            # ==================================================
            # BINARIO
            # ==================================================

            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 6px;
                text-align:center;
                background:#ffffff;
                color:#111111;
                vertical-align:middle;
            ">
                {safe(item.get("binario"))}
            </td>
            """


            # ==================================================
            # DISP
            # ==================================================

            if item.get("disp"):

                disp_html = """
                <span style="
                    display:inline-block;
                    width:16px;
                    height:16px;
                    background:#20b957;
                    border:2px solid #147a38;
                    border-radius:50%;
                    box-sizing:border-box;
                "></span>
                """

            else:

                disp_html = """
                <span style="
                    display:inline-block;
                    width:16px;
                    height:16px;
                    background:#e5e5e5;
                    border:2px solid #999999;
                    border-radius:50%;
                    box-sizing:border-box;
                "></span>
                """


            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 6px;
                text-align:center;
                background:#ffffff;
                vertical-align:middle;
            ">
                {disp_html}
            </td>
            """


            # ==================================================
            # OUT
            # ==================================================

            if item.get("out"):

                out_html = """
                <span style="
                    display:inline-block;
                    width:16px;
                    height:16px;
                    background:#e53935;
                    border:2px solid #a51e1b;
                    border-radius:50%;
                    box-sizing:border-box;
                "></span>
                """

            else:

                out_html = """
                <span style="
                    display:inline-block;
                    width:16px;
                    height:16px;
                    background:#e5e5e5;
                    border:2px solid #999999;
                    border-radius:50%;
                    box-sizing:border-box;
                "></span>
                """


            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 6px;
                text-align:center;
                background:#ffffff;
                vertical-align:middle;
            ">
                {out_html}
            </td>
            """


            # ==================================================
            # LAVORAZIONI
            # ==================================================

            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 8px;
                text-align:left;
                background:#ffffff;
                color:#111111;
                vertical-align:middle;
                white-space:normal;
                overflow-wrap:anywhere;
                line-height:1.4;
            ">
                {safe(item.get("lavorazioni"))}
            </td>
            """


            # ==================================================
            # ODL
            # ==================================================

            odl = item.get("odl")

            if odl:

                odl_html = f"""
                <span style="
                    color:#167a55;
                    text-decoration:underline;
                    font-weight:bold;
                ">
                    {safe(odl)}
                </span>
                """

            else:

                odl_html = "-"


            html_tabella += f"""
            <td style="
                border:2px solid #555555;
                padding:12px 6px;
                text-align:center;
                background:#ffffff;
                color:#111111;
                vertical-align:middle;
                overflow-wrap:anywhere;
            ">
                {odl_html}
            </td>
            """


            html_tabella += """
            </tr>
            """


        # ------------------------------------------------------
        # FINE TABELLA
        # ------------------------------------------------------

        html_tabella += """
        </tbody>

        </table>

        </div>
        """


        st.markdown(
            html_tabella,
            unsafe_allow_html=True
        )


    # ==========================================================
    # TITOLO PAGINA
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
        # INSERISCI
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
            # INSERT SUPABASE
            # --------------------------------------------------

            try:

                (
                    supabase
                    .table("passaggio_consegne")
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
                    "❌ Errore durante l'inserimento."
                )

                st.code(str(e))


    st.divider()


    # ==========================================================
    # STORICO
    # ==========================================================

    st.subheader(
        "📚 Storico Passaggi Consegne"
    )


    dati = carica_consegne()


    if not dati:

        st.info(
            "Nessun passaggio di consegne presente."
        )

        return


    # ==========================================================
    # DATE DISPONIBILI
    # ==========================================================

    date_disponibili = sorted(
        list(
            set(
                d.get("data_consegna")
                for d in dati
                if d.get("data_consegna")
            )
        ),
        reverse=True
    )


    if not date_disponibili:

        st.info(
            "Nessuna data disponibile."
        )

        return


    # ==========================================================
    # SELEZIONE DATA
    # ==========================================================

    data_storico = st.selectbox(
        "📅 Visualizza data",
        date_disponibili,
        index=0
    )


    # ==========================================================
    # SELEZIONE TURNO
    # ==========================================================

    turni_disponibili = sorted(
        list(
            set(
                d.get("turno")
                for d in dati
                if (
                    d.get("data_consegna")
                    == data_storico
                    and d.get("turno")
                )
            )
        )
    )


    filtro_turno = st.selectbox(
        "🕐 Visualizza turno",
        ["Tutti i turni"] + turni_disponibili
    )


    # ==========================================================
    # FILTRO DATA
    # ==========================================================

    dati_giorno = [

        d for d in dati

        if d.get("data_consegna")
        == data_storico

    ]


    # ==========================================================
    # FILTRO TURNO
    # ==========================================================

    if filtro_turno != "Tutti i turni":

        dati_giorno = [

            d for d in dati_giorno

            if d.get("turno")
            == filtro_turno

        ]


    if not dati_giorno:

        st.info(
            "Nessun dato per questa giornata/turno."
        )

        return


    # ==========================================================
    # RESPONSABILI
    # ==========================================================

    responsabili = sorted(
        set(
            d.get("responsabile")
            for d in dati_giorno
            if d.get("responsabile")
        )
    )


    st.caption(
        f"📅 Data: **{data_storico}**"
        f"   |   "
        f"🕐 Turno: **{filtro_turno}**"
        f"   |   "
        f"👤 Responsabile: "
        f"**{', '.join(responsabili) if responsabili else '-'}**"
    )


    # ==========================================================
    # TRENI IN USCITA
    # ==========================================================

    treni_uscita = [

        d for d in dati_giorno

        if d.get("tipo")
        == "TRENO IN USCITA"

    ]


    crea_tabella_excel(
        "🚆 TRENI IN USCITA",
        treni_uscita,
        "uscita"
    )


    # ==========================================================
    # MANUTENZIONI
    # ==========================================================

    manutenzioni = [

        d for d in dati_giorno

        if d.get("tipo")
        == "MANUTENZIONE / LAVORAZIONE APERTA"

    ]


    crea_tabella_excel(
        "🛠️ MANUTENZIONE / LAVORAZIONI APERTE",
        manutenzioni,
        "manutenzione"
    )


    # ==========================================================
    # RIEPILOGO
    # ==========================================================

    st.divider()


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "🚆 Treni in uscita",
            len(treni_uscita)
        )


    with col2:

        st.metric(
            "🛠️ Lavorazioni aperte",
            len(manutenzioni)
        )


    with col3:

        st.metric(
            "📋 Totale",
            len(dati_giorno)
        )


    # ==========================================================
    # INFORMAZIONI TURNO
    # ==========================================================

    turni_presenti = sorted(
        set(
            d.get("turno")
            for d in dati_giorno
            if d.get("turno")
        )
    )


    st.caption(
        "🕐 Turni presenti: "
        + (
            ", ".join(turni_presenti)
            if turni_presenti
            else "-"
        )
    )
