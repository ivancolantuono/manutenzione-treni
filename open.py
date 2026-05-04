import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.express as px
from db import supabase, get_operatori
from streamlit_autorefresh import st_autorefresh


def openitem_page():
    st_autorefresh(interval=10000, key="auto_refresh_openitem")
    from zoneinfo import ZoneInfo

    utente_loggato = st.session_state.get("utente", "Sconosciuto")

    # ============================
    # FUNZIONI
    # ============================

    def ora_italia_iso():
        return datetime.now(ZoneInfo("Europe/Rome")).isoformat()

    def formatta_data(data_str):
        if not data_str:
            return "-"
        try:
            return datetime.fromisoformat(data_str).strftime("%d/%m/%Y %H:%M")
        except:
            return data_str

    @st.cache_data(ttl=5)
    def get_open_item_fast():
        return supabase.table("open_item")\
            .select("id,treno,cassa,impianto,descrizione,stato,utente,data_creazione,avanzamento,lavorazioni,data_chiusura,utente_chiusura,allegati")\
            .order("data_creazione", desc=True)\
            .execute().data

    def salva_log(item_id, azione, utente, vecchio="", nuovo="", campo=""):
        supabase.table("open_item_log").insert({
            "item_id": item_id,
            "azione": azione,
            "utente": utente,
            "valore_precedente": str(vecchio),
            "valore_nuovo": str(nuovo),
            "campo": campo,
            "data": ora_italia_iso()
        }).execute()

    def mostra_cronologia(item_id):
        log = supabase.table("open_item_log")\
            .select("*")\
            .eq("item_id", item_id)\
            .order("data", desc=False)\
            .execute().data

        if not log:
            st.info("Nessuna modifica")
            return

        st.markdown("### 📜 Cronologia")
        for l in log:
            st.write(f"{formatta_data(l['data'])} - {l['utente']} → {l['azione']}")
            if l.get("campo"):
                st.caption(f"{l['campo']}: {l.get('valore_nuovo','')}")

    def carica_allegati(files):
        urls = []
    
        if files:
            for file in files:
                file_path = f"open_item/{datetime.now().timestamp()}_{file.name}"
    
                supabase.storage.from_("allegati").upload(
                    file_path,
                    file.getvalue(),
                    {"content-type": file.type}
                )
    
                url = supabase.storage.from_("allegati").get_public_url(file_path)
                urls.append(url)
    
        return urls

    # ============================
    # UI
    # ============================

    st.title("📌 Open Item")
    if "edit_item_id" not in st.session_state:
        st.session_state.edit_item_id = None

    # ✅ INIT
    if "oi_form_id" not in st.session_state:
        st.session_state.oi_form_id = 0
    
    with st.expander("➕ Nuova attività"):
    
        form_id = st.session_state.oi_form_id
    
        col1, col2, col3 = st.columns(3)
    
        treno = col1.text_input("🚆 Treno", key=f"oi_treno_{form_id}")

        allegati = st.file_uploader(
            "📎 Allegati",
            type=["pdf","jpg","png","xlsx","txt"],
            accept_multiple_files=True,
            key=f"oi_file_{form_id}"
        )
    
        cassa = col2.multiselect(
            "☑️ Cassa",
            ["DM1","TT2","M3","T4","T5","M6","TT7","DM8"],
            key=f"oi_cassa_{form_id}"
        )
    
        impianto = col3.selectbox(
            "⚙️ Impianto",
            ["","Porte Interne","Freno","Antincendio","Pis","Arredo","Trazione",
             "Climatizzazione","Tcms","Porte Esterne","Toilette","Bar-Bistrot","Pantografo","Alta Tensione"],
            key=f"oi_impianto_{form_id}"
        )
    
        descrizione = st.text_area("📝 Descrizione", key=f"oi_descrizione_{form_id}")
    
        if st.button("➕ Inserisci"):

            if not treno or not descrizione:
                st.error("Compila i campi obbligatori")
                st.stop()
        
            file_urls = []

            if allegati:
                for file in allegati:
            
                    file_path = f"open_item/{datetime.now().timestamp()}_{file.name}"
            
                    supabase.storage.from_("allegati").upload(
                        file_path,
                        file.getvalue(),
                        {"content-type": file.type}
                    )
            
                    url = supabase.storage.from_("allegati").get_public_url(file_path)
            
                    file_urls.append(url)
        
            supabase.table("open_item").insert({
                "treno": treno,
                "cassa": ", ".join(cassa),
                "impianto": impianto,
                "descrizione": descrizione,
                "allegati": file_urls,   # 👈 nuova colonna
                "stato": "APERTO",
                "utente": utente_loggato,
                "data_creazione": ora_italia_iso()
            }).execute()
    
            st.success("✅ OPEN ITEM INSERITO")
    
            get_open_item_fast.clear()
            
            st.session_state.oi_form_id += 1
    
            import time
            st.rerun()
    
    st.divider()
    # ============================
    # DATI
    # ============================

    dati = get_open_item_fast()
    # ============================
    # 🔍 FILTRI
    # ============================
    
    st.subheader("🔍 Filtri")
    
    col1, col2, col3 = st.columns(3)
    
    lista_treni = sorted(set(d.get("treno","") for d in dati if d.get("treno")))
    lista_casse = sorted(set(d.get("cassa","") for d in dati if d.get("cassa")))
    lista_impianti = sorted(set(d.get("impianto","") for d in dati if d.get("impianto")))
    
    filtro_treno = col1.multiselect("🚆 Treno", lista_treni)
    filtro_cassa = col2.multiselect("☑️ Cassa", lista_casse)
    filtro_impianto = col3.multiselect("⚙️ Impianto", lista_impianti)
    
    
    def applica_filtri(d):
    
        if filtro_treno and d.get("treno") not in filtro_treno:
            return False
    
        if filtro_cassa and d.get("cassa") not in filtro_cassa:
            return False
    
        if filtro_impianto and d.get("impianto") not in filtro_impianto:
            return False
    
        return True
    
    
    dati = [d for d in dati if applica_filtri(d)]

    aperti = [d for d in dati if d["stato"] == "APERTO"]
    valutazione = [d for d in dati if d["stato"] == "VALUTAZIONE"]
    chiusi = [d for d in dati if d["stato"] == "CHIUSO"]

    # ============================
    # 🔴 APERTI
    # ============================

    with st.expander("**🔴 ATTIVITA' APERTE 🔴**", expanded=True):

        for item in valutazione:
        
            id = item["id"]
    
            with st.expander(
                f"🔴 [{item['treno']}] {item['impianto']} → {item['descrizione']}",
                expanded=False
            ):            
               
                in_modifica = st.session_state.edit_item_id == id
    
                cassa_edit = st.text_input(
                    "☑️ Cassa",
                    value=item.get("cassa",""),
                    disabled=not in_modifica,
                    key=f"cassa_{id}"
                )
                
                impianto_edit = st.text_input(
                    "⚙️ Impianto",
                    value=item.get("impianto",""),
                    disabled=not in_modifica,
                    key=f"imp_{id}"
                )
    
                descrizione_edit = st.text_area(
                    "📝 Descrizione",
                    value=item.get("descrizione",""),
                    disabled=not in_modifica,
                    key=f"desc_{id}"
                )
                st.write(f"👤 {item.get('utente','-')}")
                st.write(f"📅 {formatta_data(item.get('data_creazione'))}")
                allegati = item.get("allegati")
    
                # 🔧 se arriva come stringa (capita con Supabase)
                if isinstance(allegati, str):
                    import json
                    try:
                        allegati = json.loads(allegati)
                    except:
                        allegati = []
                
                if allegati:
                    for i, url in enumerate(allegati):
                        st.link_button(f"📎 Allegato {i+1}", url)
                
                           
                lavori = st.text_area("🔧 Lavorazioni", key=f"lav_{id}")
                avanzamento = st.text_area(
                    "📈 Avanzamento / Monitoraggio",
                    value=item.get("avanzamento","") or "",
                    key=f"av_{id}"
                )
                nuovi_allegati = st.file_uploader(
                    "📎 Aggiungi allegati",
                    type=["pdf","jpg","png","xlsx","txt"],
                    accept_multiple_files=True,
                    key=f"file_update_{id}"
                )
    
                col1, col2, col3, col4, col5 = st.columns(5)
    
                # 🟡 MONITORAGGIO (SALVA + VALUTAZIONE)
                if col1.button("🟡 Monitoraggio", key=f"monitor_{id}"):
    
                    if not avanzamento.strip():
                        st.error("Inserisci avanzamento")
                        st.stop()
                
                    # 📎 allegati esistenti
                    allegati_attuali = item.get("allegati") or []
                
                    if isinstance(allegati_attuali, str):
                        import json
                        try:
                            allegati_attuali = json.loads(allegati_attuali)
                        except:
                            allegati_attuali = []
                
                    # 📤 nuovi file
                    nuovi_url = carica_allegati(nuovi_allegati)
                
                    # 🔗 merge
                    allegati_finali = allegati_attuali + nuovi_url
                
                    # 💾 update
                    supabase.table("open_item").update({
                        "avanzamento": avanzamento.strip(),
                        "stato": "VALUTAZIONE",
                        "allegati": allegati_finali
                    }).eq("id", id).execute()
                
                    salva_log(
                        id,
                        "MONITORAGGIO",
                        utente_loggato,
                        item.get("avanzamento",""),
                        avanzamento,
                        "avanzamento"
                    )
                
                    get_open_item_fast.clear()
                    st.rerun()
                    
                # ✅ CHIUDI
                if col2.button("✅ Chiudi", key=f"close_{id}"):
    
                    if not lavori.strip():
                        st.error("Inserisci lavorazioni")
                        st.stop()
                
                    # 📎 allegati esistenti
                    allegati_attuali = item.get("allegati") or []
                
                    if isinstance(allegati_attuali, str):
                        import json
                        try:
                            allegati_attuali = json.loads(allegati_attuali)
                        except:
                            allegati_attuali = []
                
                    # 📤 nuovi file
                    nuovi_url = carica_allegati(nuovi_allegati)
                
                    # 🔗 merge
                    allegati_finali = allegati_attuali + nuovi_url
                
                    # 💾 update
                    supabase.table("open_item").update({
                        "stato": "CHIUSO",
                        "lavorazioni": lavori.strip(),
                        "data_chiusura": ora_italia_iso(),
                        "utente_chiusura": utente_loggato,
                        "allegati": allegati_finali
                    }).eq("id", id).execute()
                
                    salva_log(id,"CHIUSURA",utente_loggato,"","CHIUSO","stato")
                
                    get_open_item_fast.clear()
                    st.rerun()
                    
                # 🗑️ elimina file + record
                if col3.button("🗑️ Elimina", key=f"del_{id}"):
                
                    file_urls = item.get("allegati") or []
                
                    import ast
                
                    # 🔁 sicurezza (stringa → lista)
                    if isinstance(file_urls, str):
                        try:
                            file_urls = ast.literal_eval(file_urls)
                        except:
                            file_urls = [file_urls]
                
                    # =========================
                    # 🗑️ DELETE STORAGE
                    # =========================
                    for url in file_urls:
                        try:
                            if url:
                                file_path = url.split("allegati/")[-1]
                                supabase.storage.from_("allegati").remove([file_path])
                        except Exception as e:
                            st.error(f"Errore file: {e}")
                
                    # =========================
                    # 🗑️ DELETE DB
                    # =========================
                    supabase.table("open_item").delete().eq("id", id).execute()
                
                    get_open_item_fast.clear()
                    st.success("Eliminato")
                    st.rerun()
                    
                # 📜 LOG
                if col4.button("📜 Log", key=f"log_{id}"):
                    mostra_cronologia(id)
    
                if col5.button("✏️ Modifica", key=f"edit_{id}"):
                    if st.session_state.edit_item_id == id:
                        st.session_state.edit_item_id = None
                    else:
                        st.session_state.edit_item_id = id
                    st.rerun()
                # =========================
                # ✏️ MODIFICA ATTIVA
                # =========================
                if in_modifica:
                
                    st.divider()
                
                    colA, colB = st.columns(2)
                
                    if colA.button("💾 Salva", key=f"save_{id}"):
                
                        supabase.table("open_item").update({
                            "cassa": cassa_edit,
                            "impianto": impianto_edit,
                            "descrizione": descrizione_edit
                        }).eq("id", id).execute()
                
                        salva_log(id, "MODIFICA", utente_loggato, "", descrizione_edit, "descrizione")
                
                        st.session_state.edit_item_id = None
                        get_open_item_fast.clear()
                        st.success("Modificato")
                        st.rerun()
                
                    if colB.button("❌ Annulla", key=f"cancel_{id}"):
                        st.session_state.edit_item_id = None
                        st.rerun()

    # ============================
    # 🟡 VALUTAZIONE
    # ============================

    with st.expander("**🟡 MONITORAGGIO 🟡**", expanded=True):

        for item in valutazione:
    
            id = item["id"]
    
            with st.expander(
                f"🟡 [{item['treno']}] {item['impianto']} → {item['descrizione']}",
                expanded=True
            ):

                st.write(f"☑️ {item.get('cassa','-')}")
                st.write(f"⚙️ {item.get('impianto','-')}")
                st.write(f"👤 {item.get('utente','-')}")
                st.write(f"📅 {formatta_data(item.get('data_creazione'))}")
    
                lavori = st.text_area("🔧 Lavorazioni", key=f"lav_val_{id}")
                avanzamento = st.text_area(
                    "📈 Avanzamento",
                    value=item.get("avanzamento","") or "",
                    key=f"av_val_{id}"
                )
                nuovi_allegati_val = st.file_uploader(
                    "📎 Aggiungi allegati",
                    type=["pdf","jpg","png","xlsx","txt"],
                    accept_multiple_files=True,
                    key=f"file_val_{id}"
                )
    
                col1, col2, col3, col4 = st.columns(4)
    
                if col1.button("🔴 Riporta aperto", key=f"back_{id}"):
    
                    supabase.table("open_item").update({
                        "stato": "APERTO"
                    }).eq("id", id).execute()
    
                    salva_log(id,"STATO",utente_loggato,"VALUTAZIONE","APERTO","stato")
    
                    get_open_item_fast.clear()
                    st.rerun()
    
                if col2.button("✅ Chiudi", key=f"close_val_{id}"):
    
                    if not lavori.strip():
                        st.error("Inserisci lavorazioni")
                        st.stop()
                
                    allegati_attuali = item.get("allegati") or []
                
                    if isinstance(allegati_attuali, str):
                        import json
                        try:
                            allegati_attuali = json.loads(allegati_attuali)
                        except:
                            allegati_attuali = []
                
                    nuovi_url = carica_allegati(nuovi_allegati_val)
                    allegati_finali = allegati_attuali + nuovi_url
                
                    supabase.table("open_item").update({
                        "stato": "CHIUSO",
                        "lavorazioni": lavori.strip(),
                        "data_chiusura": ora_italia_iso(),
                        "utente_chiusura": utente_loggato,
                        "allegati": allegati_finali
                    }).eq("id", id).execute()
                
                    salva_log(id,"CHIUSURA",utente_loggato,"","CHIUSO","stato")
                
                    get_open_item_fast.clear()
                    st.rerun()
    
                if col3.button("💾 Aggiorna", key=f"update_av_{id}"):
    
                    if not avanzamento.strip():
                        st.error("Inserisci avanzamento")
                        st.stop()
        
                    supabase.table("open_item").update({
                        "avanzamento": avanzamento.strip()
                    }).eq("id", id).execute()
        
                    salva_log(
                        id,
                        "MODIFICA",
                        utente_loggato,
                        item.get("avanzamento",""),
                        avanzamento,
                        "avanzamento"
                    )
        
                    get_open_item_fast.clear()
                    st.rerun()
    
                if col4.button("📜 Log", key=f"log_val_{id}"):
                    mostra_cronologia(id)

    # ============================
    # 🟢 CHIUSI
    # ============================

    with st.expander("**🟢 ATTIVITA' CHIUSE 🟢**", expanded=True):

        for item in valutazione:
        
            id = item["id"]
    
            with st.expander(
                f"🟢 [{item['treno']}] {item['impianto']} → {item['descrizione']}",
                expanded=False
            ):
                st.write(f"☑️ {item.get('cassa','-')}")
                st.write(f"⚙️ {item.get('impianto','-')}")
                st.write(f"👤 {item.get('utente','-')}")
                st.write(f"📅 {formatta_data(item.get('data_creazione'))}")
    
                allegati = item.get("allegati")
    
                # 🔧 sicurezza (stringa → lista)
                if isinstance(allegati, str):
                    import json
                    try:
                        allegati = json.loads(allegati)
                    except:
                        allegati = []
                
                if allegati:
                    st.markdown("### 🖇️ Allegati")
                
                    for i, url in enumerate(allegati):
                
                        # 👁️ visualizza
                        if url.endswith((".jpg",".png",".jpeg")):
                            st.image(url, width=200)
                        else:
                            st.link_button(f"📎 Allegato {i+1}", url)
                
                        # ⬇️ download
                        st.markdown(
                            f'<a href="{url}" download target="_blank">⬇️</a>',
                            unsafe_allow_html=True
                        )
    
                st.text_area(
                    "🔒 Lavorazioni",
                    value=item.get("lavorazioni",""),
                    disabled=True,
                    key=f"view_{id}"
                )
    
                col1, col2 = st.columns(2)
    
                if col1.button("🔓 Riapri", key=f"riapri_{id}"):
    
                    supabase.table("open_item").update({
                        "stato": "APERTO"
                    }).eq("id", id).execute()
    
                    salva_log(id,"RIAPERTURA",utente_loggato,"CHIUSO","APERTO","stato")
    
                    get_open_item_fast.clear()
                    st.rerun()
    
                if col2.button("📜 Log", key=f"log_ch_{id}"):
                    mostra_cronologia(id)
    
        
