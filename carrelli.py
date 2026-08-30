# ==========================================================
# TROVA IMMAGINI
# ==========================================================

def trova_immagini(nome_foglio):

    if not CARTELLA_IMMAGINI.exists():
        return []

    immagini = []

    estensioni = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp"
    }

    # ------------------------------------------------------
    # Normalizzazione normale
    # ------------------------------------------------------

    nome_cercato = normalizza_nome(nome_foglio)

    # ------------------------------------------------------
    # Normalizzazione ancora più aggressiva
    #
    # DM1-CARR.1
    # DM1_CARR.1
    # DM1 CARR 1
    # DM1-CARR-1
    #
    # diventano tutti:
    #
    # dm1carr1
    # ------------------------------------------------------

    nome_cercato_sicuro = re.sub(
        r"[^a-z0-9]",
        "",
        nome_cercato
    )

    # ------------------------------------------------------
    # Legge anche eventuali sottocartelle
    # ------------------------------------------------------

    try:

        files = list(
            CARTELLA_IMMAGINI.rglob("*")
        )

    except Exception:

        return []

    # ------------------------------------------------------
    # Analizza i file
    # ------------------------------------------------------

    for file in files:

        if not file.is_file():
            continue

        if file.suffix.lower() not in estensioni:
            continue

        nome_file = normalizza_nome(
            file.name
        )

        nome_file_sicuro = re.sub(
            r"[^a-z0-9]",
            "",
            nome_file
        )

        # ==================================================
        # IMMAGINE SINGOLA
        # ==================================================

        if nome_file_sicuro == nome_cercato_sicuro:

            immagini.append(file)

            continue

        # ==================================================
        # LOOP IMS
        # ==================================================

        if nome_cercato_sicuro == "loopims":

            if nome_file_sicuro.startswith("loopims"):

                immagini.append(file)

    # ------------------------------------------------------
    # ELIMINA DUPLICATI
    # ------------------------------------------------------

    immagini = list(
        dict.fromkeys(immagini)
    )

    # ------------------------------------------------------
    # ORDINE NUMERICO
    # ------------------------------------------------------

    def ordine(file):

        numeri = re.findall(
            r"\d+",
            file.stem
        )

        if numeri:
            return int(numeri[-1])

        return 0

    immagini.sort(
        key=ordine
    )

    return immagini
