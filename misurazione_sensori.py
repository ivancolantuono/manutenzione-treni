import streamlit as st
import pandas as pd
import re
import altair as alt


# ==========================================================
# ORDINE SENSORI DM1
# ==========================================================

ORDER_DM1 = [
    "007", "005", "006", "004", "003", "002", "001", "008", "009",
    "010", "011", "012", "013", "014", "015", "017", "016", "018",
    "027", "029", "030", "028", "026", "025", "023", "024", "022",
    "021", "020", "019", "031", "032", "033", "034", "035", "036",
    "038", "037", "039", "040", "041", "042", "043", "044", "045",
    "046", "047", "048", "049", "050", "051", "052", "053", "054",
    "055", "056", "057", "058", "059", "060", "061", "062", "063",
    "064", "065", "066", "067", "068", "074", "073", "072", "071",
    "070", "069"
]


# ==========================================================
# ORDINE SENSORI DM8
# ==========================================================

ORDER_DM8 = [
    "069", "070", "071", "072", "073", "074", "068", "067", "058",
    "059", "060", "061", "062", "063", "064", "065", "066", "049",
    "050", "051", "052", "053", "054", "055", "056", "057", "040",
    "041", "042", "043", "044", "045", "046", "047", "048", "039",
    "037", "038", "036", "035", "034", "033", "032", "031", "019",
    "020", "021", "022", "024", "023", "025", "026", "028", "030",
    "029", "027", "018", "016", "017", "015", "014", "013", "012",
    "011", "010", "009", "008", "001", "002", "003", "004", "006",
    "005", "007"
]


# ==========================================================
# OTTIENI ORDINE
# ==========================================================

def get_order(cassa):

    cassa = str(cassa).upper().strip()

    if cassa == "DM1":
        return ORDER_DM1

    if cassa == "DM8":
        return ORDER_DM8

    return []


# ==========================================================
# NORMALIZZA ADD
# ==========================================================

def normalize_add(value):

    if value is None:
        return ""

    value = str(value).strip()

    value = re.sub(
        r"\.0$",
        "",
        value
    )

    match = re.search(
        r"\d+",
        value
    )

    if not match:
        return ""

    return match.group(0).zfill(3)


# ==========================================================
# NORMALIZZA COLONNE
# ==========================================================

def normalize_column_name(value):

    value = str(value).strip()

    value = value.replace(
        "\ufeff",
        ""
    )

    upper = value.upper()

    if upper in [
        "ADD",
        "ADDRESS",
        "ADDR"
    ]:
        return "ADD"

    if upper in [
        "I",
        "I."
    ]:
        return "I"

    if upper in [
        "I_I",
        "I/I",
        "I-I",
        "II"
    ]:
        return "I_I"

    if upper == "STA":
        return "STA"

    return value


# ==========================================================
# RICONOSCIMENTO DM1 / DM8
# ==========================================================

def detect_cassa(
    nome_file,
    testo
):

    nome = str(
        nome_file
    ).upper()

    if "DM1" in nome:
        return "DM1"

    if "DM8" in nome:
        return "DM8"

    testo_upper = str(
        testo
    ).upper()

    if re.search(
        r"\bDM1\b",
        testo_upper
    ):
        return "DM1"

    if re.search(
        r"\bDM8\b",
        testo_upper
    ):
        return "DM8"

    return "SCONOSCIUTA"


# ==========================================================
# CERCA HEADER
# ==========================================================

def trova_header(righe):

    for indice, riga in enumerate(righe):

        testo = riga.strip()

        if not testo:
            continue

        upper = testo.upper()

        if "ADD" not in upper:
            continue

        if (
            "STA" not in upper
            and
            "I_I" not in upper
            and
            "I/I" not in upper
        ):
            continue

        return indice

    return None


# ==========================================================
# SEPARA HEADER
# ==========================================================

def split_header(riga):

    riga = riga.strip()

    if "\t" in riga:

        return [
            x.strip()
            for x in riga.split("\t")
        ]

    if ";" in riga:

        return [
            x.strip()
            for x in riga.split(";")
        ]

    if "," in riga:

        return [
            x.strip()
            for x in riga.split(",")
        ]

    return re.split(
        r"\s+",
        riga
    )


# ==========================================================
# SEPARA RIGA DATI
# ==========================================================

def split_data_line(riga):

    riga = riga.strip()

    if "\t" in riga:

        return [
            x.strip()
            for x in riga.split("\t")
        ]

    if ";" in riga:

        return [
            x.strip()
            for x in riga.split(";")
        ]

    if "," in riga:

        return [
            x.strip()
            for x in riga.split(",")
        ]

    return re.split(
        r"\s+",
        riga
    )


# ==========================================================
# TROVA COLONNA
# ==========================================================

def trova_colonna(
    header,
    possibili
):

    for indice, nome in enumerate(header):

        nome_normalizzato = normalize_column_name(
            nome
        )

        if nome_normalizzato in possibili:

            return indice

    return None


# ==========================================================
# IMPORTA FILE .MNT
# ==========================================================

def importa_mnt(
    uploaded_file
):

    contenuto = uploaded_file.getvalue()

    # ------------------------------------------------------
    # DECODIFICA
    # ------------------------------------------------------

    try:

        testo = contenuto.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        testo = contenuto.decode(
            "latin-1",
            errors="ignore"
        )

    righe = testo.splitlines()

    # ------------------------------------------------------
    # CASSA
    # ------------------------------------------------------

    cassa = detect_cassa(
        uploaded_file.name,
        testo
    )

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    indice_header = trova_header(
        righe
    )

    if indice_header is None:

        return importa_senza_header(
            righe,
            cassa
        )

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    header_raw = split_header(
        righe[indice_header]
    )

    header = [
        normalize_column_name(x)
        for x in header_raw
    ]

    # ------------------------------------------------------
    # COLONNE
    # ------------------------------------------------------

    indice_add = trova_colonna(
        header,
        {"ADD"}
    )

    indice_i = trova_colonna(
        header,
        {"I"}
    )

    indice_i_i = trova_colonna(
        header,
        {"I_I"}
    )

    indice_sta = trova_colonna(
        header,
        {"STA"}
    )

    if indice_add is None:

        return (
            pd.DataFrame(),
            cassa
        )

    records = []

    # ======================================================
    # DATI
    # ======================================================

    for riga in righe[
        indice_header + 1:
    ]:

        riga = riga.strip()

        if not riga:
            continue

        parti = split_data_line(
            riga
        )

        if indice_add >= len(parti):
            continue

        add = normalize_add(
            parti[indice_add]
        )

        if not add:
            continue

        record = {
            "ADD": add,
            "I": None,
            "I_I": None,
            "STA": None
        }

        # --------------------------------------------------
        # I
        # --------------------------------------------------

        if (
            indice_i is not None
            and
            indice_i < len(parti)
        ):

            record["I"] = parti[
                indice_i
            ]

        # --------------------------------------------------
        # I_I
        # --------------------------------------------------

        if (
            indice_i_i is not None
            and
            indice_i_i < len(parti)
        ):

            record["I_I"] = parti[
                indice_i_i
            ]

        # --------------------------------------------------
        # STA
        # --------------------------------------------------

        if (
            indice_sta is not None
            and
            indice_sta < len(parti)
        ):

            record["STA"] = parti[
                indice_sta
            ]

        records.append(
            record
        )

    df = pd.DataFrame(
        records
    )

    if df.empty:

        return (
            df,
            cassa
        )

    # ======================================================
    # CONVERSIONE NUMERICA
    # ======================================================

    for colonna in [
        "I",
        "I_I",
        "STA"
    ]:

        df[colonna] = pd.to_numeric(
            df[colonna],
            errors="coerce"
        )

    # ======================================================
    # UN RECORD PER SENSOR
    # ======================================================

    df = df.drop_duplicates(
        subset=["ADD"],
        keep="last"
    )

    # ======================================================
    # ORDINE
    # ======================================================

    df = applica_ordine(
        df,
        cassa
    )

    return (
        df,
        cassa
    )


# ==========================================================
# IMPORTAZIONE SENZA HEADER
# ==========================================================

def importa_senza_header(
    righe,
    cassa
):

    records = []

    for riga in righe:

        riga = riga.strip()

        if not riga:
            continue

        parti = split_data_line(
            riga
        )

        if len(parti) < 2:
            continue

        add = normalize_add(
            parti[0]
        )

        if not add:
            continue

        numeri = []

        for valore in parti[1:]:

            try:

                numero = float(
                    str(valore)
                    .replace(",", ".")
                )

                numeri.append(
                    numero
                )

            except Exception:

                pass

        if not numeri:
            continue

        record = {
            "ADD": add,
            "I": None,
            "I_I": None,
            "STA": None
        }

        if len(numeri) >= 1:
            record["I"] = numeri[-1]

        if len(numeri) >= 2:
            record["I_I"] = numeri[-2]

        if len(numeri) >= 3:
            record["STA"] = numeri[-3]

        records.append(
            record
        )

    df = pd.DataFrame(
        records
    )

    if df.empty:

        return (
            df,
            cassa
        )

    for colonna in [
        "I",
        "I_I",
        "STA"
    ]:

        df[colonna] = pd.to_numeric(
            df[colonna],
            errors="coerce"
        )

    df = df.drop_duplicates(
        subset=["ADD"],
        keep="last"
    )

    df = applica_ordine(
        df,
        cassa
    )

    return (
        df,
        cassa
    )


# ==========================================================
# APPLICA ORDINE FISICO
# ==========================================================

def applica_ordine(
    df,
    cassa
):

    df = df.copy()

    ordine = get_order(
        cassa
    )

    if not ordine:

        return df

    df["ADD"] = (
        df["ADD"]
        .apply(normalize_add)
    )

    mappa = {
        add: posizione
        for posizione, add
        in enumerate(ordine)
    }

    df["_POSIZIONE"] = (
        df["ADD"]
        .map(mappa)
    )

    df = df.sort_values(
        "_POSIZIONE",
        na_position="last"
    )

    df = df.reset_index(
        drop=True
    )

    return df


# ==========================================================
# PREPARA GRAFICO
# ==========================================================

def prepara_grafico(
    df,
    cassa
):

    df = applica_ordine(
        df,
        cassa
    )

    ordine = get_order(
        cassa
    )

    mappa = {
        add: posizione
        for posizione, add
        in enumerate(ordine)
    }

    df["POSIZIONE"] = (
        df["ADD"]
        .map(mappa)
    )

    # ------------------------------------------------------
    # Solo ADD presenti nell'ordine
    # ------------------------------------------------------

    df = df[
        df["POSIZIONE"].notna()
    ].copy()

    # ------------------------------------------------------
    # Ordinamento definitivo
    # ------------------------------------------------------

    df = df.sort_values(
        "POSIZIONE"
    )

    df = df.reset_index(
        drop=True
    )

    # ------------------------------------------------------
    # Nome visualizzato
    # ------------------------------------------------------

    df["SENSORE"] = (
        df["ADD"]
        .astype(str)
    )

    # ------------------------------------------------------
    # STA NUMERICA
    # ------------------------------------------------------

    if "STA" in df.columns:

        df["STA"] = pd.to_numeric(
            df["STA"],
            errors="coerce"
        )

    # ------------------------------------------------------
    # I_I NUMERICA
    # ------------------------------------------------------

    if "I_I" in df.columns:

        df["I_I"] = pd.to_numeric(
            df["I_I"],
            errors="coerce"
        )

    return df


# ==========================================================
# GRAFICO
# ==========================================================

def crea_grafico(
    df,
    cassa
):

    grafico = prepara_grafico(
        df,
        cassa
    )

    if grafico.empty:

        return None

    colonne = []

    if "STA" in grafico.columns:
        colonne.append("STA")

    if "I_I" in grafico.columns:
        colonne.append("I_I")

    if not colonne:

        return None

    # ======================================================
    # FORMATO LONG
    # ======================================================

    long_df = grafico[
        [
            "SENSORE",
            "POSIZIONE"
        ] + colonne
    ].melt(
        id_vars=[
            "SENSORE",
            "POSIZIONE"
        ],
        value_vars=colonne,
        var_name="Segnale",
        value_name="Valore"
    )

    # ======================================================
    # LINEE
    # ======================================================

    linee = (
        alt.Chart(
            long_df
        )
        .mark_line(
            point=False,
            strokeWidth=2
        )
        .encode(

            x=alt.X(
                "SENSORE:N",
                sort=alt.SortField(
                    field="POSIZIONE",
                    order="ascending"
                ),
                axis=alt.Axis(
                    title="Sensori",
                    labelAngle=-90,
                    labelOverlap=False
                )
            ),

            y=alt.Y(
                "Valore:Q",
                title="Valore"
            ),

            color=alt.Color(
                "Segnale:N",
                title="Segnale"
            ),

            tooltip=[
                alt.Tooltip(
                    "SENSORE:N",
                    title="Sensore"
                ),

                alt.Tooltip(
                    "Segnale:N",
                    title="Segnale"
                ),

                alt.Tooltip(
                    "Valore:Q",
                    title="Valore"
                )
            ]
        )
    )

    # ======================================================
    # SENSORI STA <= 45
    # ======================================================

    critici = grafico[
        pd.to_numeric(
            grafico["STA"],
            errors="coerce"
        ) <= 45
    ].copy()

    # ======================================================
    # PUNTI STA <= 45
    # ======================================================

    if not critici.empty:

        punti_critici = (
            alt.Chart(
                critici
            )
            .mark_point(
                filled=True,
                size=110
            )
            .encode(

                x=alt.X(
                    "SENSORE:N",
                    sort=alt.SortField(
                        field="POSIZIONE",
                        order="ascending"
                    )
                ),

                y=alt.Y(
                    "STA:Q"
                ),

                tooltip=[
                    alt.Tooltip(
                        "SENSORE:N",
                        title="⚠️ Sensore"
                    ),

                    alt.Tooltip(
                        "STA:Q",
                        title="STA"
                    )
                ]
            )
        )

        # --------------------------------------------------
        # SOGLIA 45
        # --------------------------------------------------

        soglia = pd.DataFrame(
            {
                "Soglia": [45]
            }
        )

        linea_soglia = (
            alt.Chart(
                soglia
            )
            .mark_rule(
                strokeDash=[6, 4]
            )
            .encode(
                y=alt.Y(
                    "Soglia:Q"
                )
            )
        )

        chart = (
            linee
            + linea_soglia
            + punti_critici
        )

    else:

        chart = linee

    # ======================================================
    # MASSIMO / MINIMO STA
    # ======================================================

    if "STA" in grafico.columns:

        sta_validi = grafico[
            grafico["STA"].notna()
        ].copy()

        if not sta_validi.empty:

            max_sta = sta_validi[
                "STA"
            ].max()

            min_sta = sta_validi[
                "STA"
            ].min()

            max_sta_df = sta_validi[
                sta_validi["STA"] == max_sta
            ].copy()

            min_sta_df = sta_validi[
                sta_validi["STA"] == min_sta
            ].copy()

            punti_max_sta = (
                alt.Chart(
                    max_sta_df
                )
                .mark_point(
                    filled=True,
                    size=180,
                    shape="triangle"
                )
                .encode(

                    x=alt.X(
                        "SENSORE:N",
                        sort=alt.SortField(
                            field="POSIZIONE",
                            order="ascending"
                        )
                    ),

                    y=alt.Y(
                        "STA:Q"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "SENSORE:N",
                            title="⬆️ STA massimo"
                        ),

                        alt.Tooltip(
                            "STA:Q",
                            title="STA"
                        )
                    ]
                )
            )

            punti_min_sta = (
                alt.Chart(
                    min_sta_df
                )
                .mark_point(
                    filled=True,
                    size=180,
                    shape="triangle-down"
                )
                .encode(

                    x=alt.X(
                        "SENSORE:N",
                        sort=alt.SortField(
                            field="POSIZIONE",
                            order="ascending"
                        )
                    ),

                    y=alt.Y(
                        "STA:Q"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "SENSORE:N",
                            title="⬇️ STA minimo"
                        ),

                        alt.Tooltip(
                            "STA:Q",
                            title="STA"
                        )
                    ]
                )
            )

            chart = (
                chart
                + punti_max_sta
                + punti_min_sta
            )

    # ======================================================
    # MASSIMO / MINIMO I_I
    # ======================================================

    if "I_I" in grafico.columns:

        ii_validi = grafico[
            grafico["I_I"].notna()
        ].copy()

        if not ii_validi.empty:

            max_ii = ii_validi[
                "I_I"
            ].max()

            min_ii = ii_validi[
                "I_I"
            ].min()

            max_ii_df = ii_validi[
                ii_validi["I_I"] == max_ii
            ].copy()

            min_ii_df = ii_validi[
                ii_validi["I_I"] == min_ii
            ].copy()

            punti_max_ii = (
                alt.Chart(
                    max_ii_df
                )
                .mark_point(
                    filled=True,
                    size=160,
                    shape="triangle"
                )
                .encode(

                    x=alt.X(
                        "SENSORE:N",
                        sort=alt.SortField(
                            field="POSIZIONE",
                            order="ascending"
                        )
                    ),

                    y=alt.Y(
                        "I_I:Q"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "SENSORE:N",
                            title="⬆️ I_I massimo"
                        ),

                        alt.Tooltip(
                            "I_I:Q",
                            title="I_I"
                        )
                    ]
                )
            )

            punti_min_ii = (
                alt.Chart(
                    min_ii_df
                )
                .mark_point(
                    filled=True,
                    size=160,
                    shape="triangle-down"
                )
                .encode(

                    x=alt.X(
                        "SENSORE:N",
                        sort=alt.SortField(
                            field="POSIZIONE",
                            order="ascending"
                        )
                    ),

                    y=alt.Y(
                        "I_I:Q"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "SENSORE:N",
                            title="⬇️ I_I minimo"
                        ),

                        alt.Tooltip(
                            "I_I:Q",
                            title="I_I"
                        )
                    ]
                )
            )

            chart = (
                chart
                + punti_max_ii
                + punti_min_ii
            )

    # ======================================================
    # DIMENSIONI
    # ======================================================

    chart = chart.properties(
        height=500
    )

    # ======================================================
    # INTERAZIONE
    # ======================================================

    chart = chart.interactive()

    return chart


# ==========================================================
# PAGINA STREAMLIT
# ==========================================================

def misurazione_sensori_page():

    st.title(
        "🔬 Misurazione Sensori"
    )

    st.caption(
        "Analisi dei sensori tramite file .MNT"
    )

    st.divider()

    # ======================================================
    # SELEZIONE CASSA
    # ======================================================

    cassa = st.radio(
        "🚆 Cassa",
        [
            "DM1",
            "DM8"
        ],
        horizontal=True,
        key="mnt_cassa"
    )

    st.divider()

    # ======================================================
    # CARICAMENTO .MNT
    # ======================================================

    uploaded_file = st.file_uploader(
        "📥 Carica file .MNT",
        type=["mnt"],
        key="mnt_file"
    )

    if uploaded_file is None:

        st.info(
            "Carica un file .MNT per iniziare."
        )

        return

    # ======================================================
    # CONTROLLO ESTENSIONE
    # ======================================================

    if not uploaded_file.name.lower().endswith(
        ".mnt"
    ):

        st.error(
            "❌ Il file deve avere estensione .MNT."
        )

        return

    # ======================================================
    # LETTURA
    # ======================================================

    try:

        with st.spinner(
            "🔄 Lettura del file .MNT..."
        ):

            (
                df,
                cassa_file
            ) = importa_mnt(
                uploaded_file
            )

    except Exception as errore:

        st.error(
            "❌ Errore durante la lettura del file .MNT."
        )

        st.exception(
            errore
        )

        return

    # ======================================================
    # CONTROLLO
    # ======================================================

    if df.empty:

        st.error(
            "❌ Nessun sensore riconosciuto "
            "nel file .MNT."
        )

        return

    # ======================================================
    # ORDINE
    # ======================================================

    df = applica_ordine(
        df,
        cassa
    )

    # ======================================================
    # PREPARAZIONE
    # ======================================================

    grafico_df = prepara_grafico(
        df,
        cassa
    )

    if grafico_df.empty:

        st.warning(
            "⚠️ Nessun sensore valido "
            "per l'ordine selezionato."
        )

        return

    # ======================================================
    # SENSORI CRITICI
    # ======================================================

    sta_numerica = pd.to_numeric(
        grafico_df["STA"],
        errors="coerce"
    )

    sensori_critici = grafico_df[
        sta_numerica <= 45
    ].copy()

    # ======================================================
    # MASSIMI / MINIMI
    # ======================================================

    sta_validi = grafico_df[
        grafico_df["STA"].notna()
    ]

    ii_validi = grafico_df[
        grafico_df["I_I"].notna()
    ]

    # ======================================================
    # INFORMAZIONI
    # ======================================================

    st.success(
        f"✅ File MNT caricato: "
        f"{uploaded_file.name}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Sensori",
            len(grafico_df)
        )

    with col2:

        st.metric(
            "Cassa",
            cassa
        )

    with col3:

        st.metric(
            "STA ≤ 45",
            len(sensori_critici)
        )

    with col4:

        st.metric(
            "Soglia",
            "45"
        )

    st.divider()

    # ======================================================
    # TABS
    # ======================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "📈 Misurazioni",
            "⚠️ Analisi valori",
            "📋 Dati MNT"
        ]
    )

    # ======================================================
    # TAB GRAFICO
    # ======================================================

    with tab1:

        st.subheader(
            f"📈 STA / I_I — {cassa}"
        )

        chart = crea_grafico(
            grafico_df,
            cassa
        )

        if chart is None:

            st.warning(
                "Nel file .MNT non sono presenti "
                "STA / I_I."
            )

        else:

            st.altair_chart(
                chart,
                use_container_width=True
            )

        st.caption(
            "⚠️ STA ≤ 45 = sotto soglia | "
            "▲ = massimo | "
            "▼ = minimo"
        )

    # ======================================================
    # TAB ANALISI
    # ======================================================

    with tab2:

        st.subheader(
            "📊 Analisi dei valori"
        )

        # ==================================================
        # STA
        # ==================================================

        st.markdown(
            "### STA"
        )

        if sta_validi.empty:

            st.info(
                "Nessun valore STA disponibile."
            )

        else:

            massimo_sta = sta_validi[
                "STA"
            ].max()

            minimo_sta = sta_validi[
                "STA"
            ].min()

            sensori_max_sta = sta_validi[
                sta_validi["STA"] == massimo_sta
            ]["ADD"].tolist()

            sensori_min_sta = sta_validi[
                sta_validi["STA"] == minimo_sta
            ]["ADD"].tolist()

            col1, col2 = st.columns(2)

            with col1:

                st.success(
                    f"⬆️ STA MASSIMO: "
                    f"{massimo_sta}"
                )

                st.write(
                    "Sensore/i: "
                    + ", ".join(
                        sensori_max_sta
                    )
                )

            with col2:

                st.error(
                    f"⬇️ STA MINIMO: "
                    f"{minimo_sta}"
                )

                st.write(
                    "Sensore/i: "
                    + ", ".join(
                        sensori_min_sta
                    )
                )

        st.divider()

        # ==================================================
        # I_I
        # ==================================================

        st.markdown(
            "### I_I"
        )

        if ii_validi.empty:

            st.info(
                "Nessun valore I_I disponibile."
            )

        else:

            massimo_ii = ii_validi[
                "I_I"
            ].max()

            minimo_ii = ii_validi[
                "I_I"
            ].min()

            sensori_max_ii = ii_validi[
                ii_validi["I_I"] == massimo_ii
            ]["ADD"].tolist()

            sensori_min_ii = ii_validi[
                ii_validi["I_I"] == minimo_ii
            ]["ADD"].tolist()

            col1, col2 = st.columns(2)

            with col1:

                st.success(
                    f"⬆️ I_I MASSIMO: "
                    f"{massimo_ii}"
                )

                st.write(
                    "Sensore/i: "
                    + ", ".join(
                        sensori_max_ii
                    )
                )

            with col2:

                st.error(
                    f"⬇️ I_I MINIMO: "
                    f"{minimo_ii}"
                )

                st.write(
                    "Sensore/i: "
                    + ", ".join(
                        sensori_min_ii
                    )
                )

        st.divider()

        # ==================================================
        # SENSORI STA <= 45
        # ==================================================

        st.markdown(
            "### ⚠️ Sensori con STA ≤ 45"
        )

        if sensori_critici.empty:

            st.success(
                "✅ Nessun sensore con STA ≤ 45."
            )

        else:

            st.warning(
                f"⚠️ {len(sensori_critici)} "
                "sensori con STA ≤ 45."
            )

            colonne_critici = [
                "ADD",
                "STA",
                "I",
                "I_I"
            ]

            colonne_critici = [
                col
                for col in colonne_critici
                if col in sensori_critici.columns
            ]

            tabella_critici = sensori_critici[
                colonne_critici
            ].copy()

            tabella_critici = tabella_critici.rename(
                columns={
                    "ADD": "Sensore"
                }
            )

            st.dataframe(
                tabella_critici,
                use_container_width=True,
                hide_index=True
            )

    # ======================================================
    # TAB DATI MNT
    # ======================================================

    with tab3:

        st.subheader(
            "📋 Dati estratti dal file .MNT"
        )

        colonne = [
            "ADD",
            "I",
            "I_I",
            "STA"
        ]

        colonne = [
            col
            for col in colonne
            if col in grafico_df.columns
        ]

        st.dataframe(
            grafico_df[
                colonne
            ],
            use_container_width=True,
            hide_index=True,
            height=600
        )

        # ==================================================
        # CSV
        # ==================================================

        csv = (
            grafico_df[
                colonne
            ]
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )

        st.download_button(
            "📥 Scarica CSV",
            data=csv,
            file_name=(
                f"misurazione_{cassa}.csv"
            ),
            mime="text/csv"
        )
