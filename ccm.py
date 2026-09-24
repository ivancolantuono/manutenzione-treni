    if selected_summary:

        descrizione = selected_summary[-1]

        if descrizione:

            st.info(
                f"Evento: {descrizione}"
            )

    # -----------------------------------------------------
    # LL
    # -----------------------------------------------------

    ll = ll_blocks.get(
        selected_rec,
        []
    )

    if not ll:

        st.warning(
            f"Nessuna LL per REC {selected_rec}"
        )

        return

    # -----------------------------------------------------
    # TIMELINE
    # -----------------------------------------------------

    st.subheader("⏱️ Timeline")

    idx = st.slider(
        "Campione",
        min_value=0,
        max_value=len(ll) - 1,
        value=0,
        key=f"ccm_slider_{selected_rec}"
    )

    row = ll[idx]

    states = decode_rec(row)

    st.caption(
        f"Campione: {idx + 1} / {len(ll)}"
    )

    st.caption(
        f"N: {row.get('N', '-')}"
    )

    # -----------------------------------------------------
    # SEGNALI DIGITALI
    # -----------------------------------------------------

    st.divider()

    st.subheader("🔌 Segnali digitali")

    # 4 colonne ravvicinate
    cols = st.columns(
        4,
        gap="small"
    )

    for i, word in enumerate(DIGITAL_WORDS):

        with cols[i % 4]:

            render_word(
                word,
                states
            )

    # -----------------------------------------------------
    # ANALOGICI
    # -----------------------------------------------------

    st.divider()

    st.subheader("📈 Segnali analogici")

    analog_cols = st.columns(
        len(ANALOG_SIGNALS),
        gap="small"
    )

    for col, signal in zip(
        analog_cols,
        ANALOG_SIGNALS
    ):

        value = row.get(
            signal,
            "—"
        )

        with col:

            analog_html = (
                '<div class="ccm-analog">'
                f'<div class="ccm-analog-name">{html.escape(signal)}</div>'
                f'<div class="ccm-analog-value">{html.escape(str(value))}</div>'
                '</div>'
            )

            st.markdown(
                analog_html,
                unsafe_allow_html=True
            )
