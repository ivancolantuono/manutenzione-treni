import streamlit as st
from pathlib import Path
import openpyxl
import base64
import html
import io

# ==========================================================
# CONFIGURAZIONE
# ==========================================================

st.set_page_config(
    page_title="Carrelli ETR1000",
    page_icon="🚆",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

FILE_EXCEL = BASE_DIR / "ATTIVITA' CARRELLO.xlsm"


# ==========================================================
# STILE
# ==========================================================

st.markdown("""
<style>

.carrelli-titolo {
    background: #b7d7f0;
    padding: 14px;
    border-radius: 8px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

.excel-container {
    width: 100%;
    overflow: auto;
    border: 1px solid #aaa;
    background: white;
    padding: 10px;
    border-radius: 8px;
}

.excel-table {
    border-collapse: collapse;
    table-layout: fixed;
    background: white;
}

.excel-table td {
    border: 1px solid #999;
    padding: 3px;
    vertical-align: middle;
    color: black;
    overflow: hidden;
}

.excel-table img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: auto;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# FUNZIONI
# ==========================================================

def colore_excel(colore):
    """
    Converte i colori Excel in CSS.
    """

    if colore is None:
        return None

    try:

        rgb = colore.rgb

        if rgb:

            rgb = str(rgb)

            # Excel può restituire AARRGGBB
            if len(rgb) == 8:
                rgb = rgb[2:]

            if len(rgb) == 6:
                return "#" + rgb

    except:
        pass

    return None


def bordo_css(border):
    """
    Converte i bordi Excel in CSS.
    """

    css = []

    lati = [
        ("top", border.top),
        ("bottom", border.bottom),
        ("left", border.left),
        ("right", border.right)
    ]

    for nome, lato in lati:

        if lato and lato.style:

            colore = colore_excel(lato.color)

            if not colore:
                colore = "#777"

            css.append(
                f"border-{nome}: 1px solid {colore};"
            )

    return "".join(css)


def allineamento_css(alignment):
    """
    Converte l'allineamento Excel.
    """

    css = ""

    if alignment:

        if alignment.horizontal:
            css += f"text-align:{alignment.horizontal};"

        if alignment.vertical:
            css += f"vertical-align:{alignment.vertical};"

        if alignment.wrap_text:
            css += "white-space:normal;"

        else:
            css += "white-space:nowrap;"

    return css


def font_css(font):
    """
    Converte font Excel.
    """

    css = ""

    if font:

        if font.bold:
            css += "font-weight:bold;"

        if font.italic:
            css += "font-style:italic;"

        if font.sz:
            css += f"font-size:{font.sz}pt;"

        colore = colore_excel(font.color)

        if colore:
            css += f"color:{colore};"

        if font.name:
            css += f"font-family:'{font.name}';"

    return css


def fill_css(fill):
    """
    Converte colore riempimento Excel.
    """

    if not fill:
        return ""

    try:

        if fill.fill_type:

            colore = colore_excel(
                fill.fgColor
            )

            if colore:
                return f"background-color:{colore};"

    except:
        pass

    return ""


def larghezza_colonna(ws, col):
    """
    Converte la larghezza Excel in pixel.
    """

    lettera = openpyxl.utils.get_column_letter(col)

    dimensione = ws.column_dimensions[lettera].width

    if dimensione is None:
        dimensione = 10

    # conversione approssimativa Excel -> pixel
    pixel = int(dimensione * 7)

    pixel = max(pixel, 35)

    return pixel


def altezza_riga(ws, row):
    """
    Converte altezza Excel in pixel.
    """

    altezza = ws.row_dimensions[row].height

    if altezza is None:
        altezza = 15

    pixel = int(altezza * 1.35)

    pixel = max(pixel, 22)

    return pixel


# ==========================================================
# IMMAGINI EXCEL
# ==========================================================

def estrai_immagini(ws):

    immagini = {}

    try:

        for img in ws._images:

            anchor = img.anchor

            # immagine ancorata alla cella
            if hasattr(anchor, "_from"):

                col = anchor._from.col + 1
                row = anchor._from.row + 1

            else:
                continue

            try:

                image_bytes = img._data()

            except:

                continue

            if not image_bytes:
                continue

            # determina formato
            estensione = "png"

            try:

                if hasattr(img, "format"):
                    if img.format:
                        estensione = img.format.lower()

            except:
                pass

            encoded = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            immagini[(row, col)] = {
                "data": encoded,
                "format": estensione
            }

    except Exception as e:

        st.warning(
            f"⚠️ Problema nella lettura delle immagini: {e}"
        )

    return immagini


# ==========================================================
# RENDER FOGLIO
# ==========================================================

def render_foglio(ws):

    immagini = estrai_immagini(ws)

    # ------------------------------------------------------
    # DIMENSIONI
    # ------------------------------------------------------

    max_row = ws.max_row
    max_col = ws.max_column

    # ------------------------------------------------------
    # MERGE CELLS
    # ------------------------------------------------------

    merged_map = {}

    for merged in ws.merged_cells.ranges:

        min_col = merged.min_col
        max_col_merge = merged.max_col

        min_row = merged.min_row
        max_row_merge = merged.max_row

        # cella principale
        merged_map[(min_row, min_col)] = (
            max_row_merge - min_row + 1,
            max_col_merge - min_col + 1
        )

        # celle secondarie
        for r in range(
            min_row,
            max_row_merge + 1
        ):

            for c in range(
                min_col,
                max_col_merge + 1
            ):

                if (
                    r != min_row
                    or c != min_col
                ):

                    merged_map[(r, c)] = "skip"

    # ------------------------------------------------------
    # TABELLA
    # ------------------------------------------------------

    risultato = []

    risultato.append(
        '<div class="excel-container">'
    )

    risultato.append(
        '<table class="excel-table">'
    )

    # ------------------------------------------------------
    # COLONNE
    # ------------------------------------------------------

    risultato.append("<colgroup>")

    for col in range(1, max_col + 1):

        width = larghezza_colonna(
            ws,
            col
        )

        risultato.append(
            f'<col style="width:{width}px;">'
        )

    risultato.append("</colgroup>")

    # ------------------------------------------------------
    # RIGHE
    # ------------------------------------------------------

    for row in range(1, max_row + 1):

        altezza = altezza_riga(
            ws,
            row
        )

        risultato.append(
            f'<tr style="height:{altezza}px;">'
        )

        for col in range(1, max_col + 1):

            # ----------------------------------------------
            # MERGE SECONDARIO
            # ----------------------------------------------

            if merged_map.get(
                (row, col)
            ) == "skip":

                continue

            cella = ws.cell(
                row=row,
                column=col
            )

            # ----------------------------------------------
            # STYLE
            # ----------------------------------------------

            stile = ""

            stile += fill_css(
                cella.fill
            )

            stile += font_css(
                cella.font
            )

            stile += allineamento_css(
                cella.alignment
            )

            stile += bordo_css(
                cella.border
            )

            # ----------------------------------------------
            # MERGE
            # ----------------------------------------------

            rowspan = 1
            colspan = 1

            merge_info = merged_map.get(
                (row, col)
            )

            if isinstance(
                merge_info,
                tuple
            ):

                rowspan = merge_info[0]
                colspan = merge_info[1]

            # ----------------------------------------------
            # CONTENUTO
            # ----------------------------------------------

            contenuto = ""

            valore = cella.value

            if valore is not None:

                testo = html.escape(
                    str(valore)
                )

                contenuto += testo

            # ----------------------------------------------
            # IMMAGINE
            # ----------------------------------------------

            img_info = immagini.get(
                (row, col)
            )

            if img_info:

                formato = img_info["format"]

                data = img_info["data"]

                contenuto += (
                    f'<br>'
                    f'<img '
                    f'src="data:image/{formato};base64,{data}" '
                    f'style="max-width:100%; max-height:250px;">'
                )

            # ----------------------------------------------
            # LINK
            # ----------------------------------------------

            if (
                isinstance(
                    valore,
                    str
                )
                and valore.startswith("http")
            ):

                url = html.escape(
                    valore,
                    quote=True
                )

                contenuto = (
                    f'<a href="{url}" '
                    f'target="_blank">'
                    f'{html.escape(valore)}'
                    f'</a>'
                )

            # ----------------------------------------------
            # TD
            # ----------------------------------------------

            td = (
                f'<td '
                f'style="{stile}"'
            )

            if rowspan > 1:

                td += (
                    f' rowspan="{rowspan}"'
                )

            if colspan > 1:

                td += (
                    f' colspan="{colspan}"'
                )

            td += ">"

            td += contenuto

            td += "</td>"

            risultato.append(td)

        risultato.append("</tr>")

    risultato.append("</table>")
    risultato.append("</div>")

    return "".join(risultato)


# ==========================================================
# PAGINA PRINCIPALE
# ==========================================================

def carrelli_page():

    st.markdown(
        """
        <div class="carrelli-titolo">
            🚆 CARRELLI ETR1000
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # FILE
    # ======================================================

    if not FILE_EXCEL.exists():

        st.error(
            "❌ File Excel non trovato."
        )

        st.write(
            "Percorso cercato:"
        )

        st.code(
            str(FILE_EXCEL)
        )

        st.info(
            "Metti il file "
            "'ATTIVITA' CARRELLO.xlsm' "
            "nella stessa cartella di carrelli.py."
        )

        return

    # ======================================================
    # CARICA EXCEL
    # ======================================================

    try:

        wb = openpyxl.load_workbook(
            FILE_EXCEL,
            read_only=False,
            data_only=False,
            keep_vba=True
        )

    except Exception as e:

        st.error(
            "❌ Errore apertura Excel."
        )

        st.code(str(e))

        return

    # ======================================================
    # FOGLI
    # ======================================================

    fogli = wb.sheetnames

    # ======================================================
    # SEZIONI
    # ======================================================

    sezioni = {

        "🛞 CARRELLI": [
            "DM1-CARR.1",
            "DM1-CARR.2",
            "M3-CARR.1",
            "M3-CARR.2",
            "M6-CARR.1",
            "M6-CARR.2",
            "DM8-CARR.1",
            "DM8-CARR.2"
        ],

        "📡 SENSORI": [
            "SENSORI SPM",
            "PT100 RIDUTTORI"
        ],

        "🔌 FUSE LOOP": [
            "FUSE LOOP CASSA MOTOR",
            "FUSE LOOP TRENO COMPLETO"
        ],

        "🔄 DNRA": [
            "LOOP DNRA",
            "OVERVIEW DNRA"
        ],

        "🚆 STATO TRENO": [
            "STATO TRENO"
        ]
    }

    # ======================================================
    # SEZIONE
    # ======================================================

    sezione = st.selectbox(
        "📂 Sezione",
        list(sezioni.keys())
    )

    # ======================================================
    # FOGLI DISPONIBILI
    # ======================================================

    fogli_sezione = [

        f
        for f in sezioni[sezione]
        if f in fogli

    ]

    if not fogli_sezione:

        st.warning(
            "Nessun foglio disponibile."
        )

        return

    # ======================================================
    # SELEZIONE FOGLIO
    # ======================================================

    foglio = st.selectbox(
        "📄 Foglio",
        fogli_sezione
    )

    st.divider()

    # ======================================================
    # VISUALIZZAZIONE
    # ======================================================

    ws = wb[foglio]

    st.markdown(
        f"### 📄 {foglio}"
    )

    try:

        contenuto = render_foglio(ws)

        st.markdown(
            contenuto,
            unsafe_allow_html=True
        )

    except Exception as e:

        st.error(
            "❌ Errore nella visualizzazione del foglio."
        )

        st.code(str(e))


# ==========================================================
# AVVIO
# ==========================================================

if __name__ == "__main__":

    carrelli_page()
