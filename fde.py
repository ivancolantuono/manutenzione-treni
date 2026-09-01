import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime
import re

# ==================================================
# DATASET PRESENTI NEL LOG
# ==================================================
DATASETS = [
    "iFDE1Status1",
    "iFDEStatus2",
    "iFDE1Diag1",
    "iFDEDiag2",
    "iFDECount",
    "iFDECtrlOp",
    "iFDEIdent2",
    "SCU-MAIN VERSION.RELEASE",
    "SCU-DIAG VERSION.RELEASE",
]

# ==================================================
# DECODIFICHE SEGNALI (DATA -> TESTO)
# ==================================================
DECODIFICHE = {
    "ISMOKESENSSTATE": {
        "0": "NESSUN ALLARME",
        "1": "ALLARME TERMICO",
        "2": "ALLARME FUMO",
        "3": "ALLARME FUMO E TERMICO",
        "4": "FAULT",
        "5": "SENSORE DISABILITATO",
    },
    "IHVACCMDSTATE": {
        "0": "STANDBY",
        "1": "HVAC SPENTO PER INCENDIO A BORDO",
        "2": "FAIL",
    },
    "IGWAYDOORCMDSTATE": {
        "0": "STANDBY",
        "1": "CHIUSURA PORTA ATTIVA",
        "2": "FAIL",
    },
    "IPGRAREAMODE": {
        "1": "START",
        "2": "STANDBY",
        "3": "PRE-ALLARME",
        "4": "PRE-ATTIVAZIONE SPRINKLERS",
        "5": "ATTIVAZIONE SPRINKLERS",
        "6": "SCARICO DISABILITATO",
        "7": "TEST/MANUTENZIONE",
    },
    "FIOCARDS": {
        "0": "OK",
        "1": "110V NON PRESENTE",
        "2": "FAULT",
        "3": "SCHEDA NON PRESENTE",
    },
     "IFIREGENERALALARM": {
        "0": "NESSUN ALLARME",
        "1": "ALLARME INCENDIO",
    }, 
      "IELECTROVALVEDMX": {
        "0": "STANDBY",
        "1": "ELETTROVALVOLA MAU ATTIVA",
        "2": "FAIL",
    },
      "FSCUCOM": {
        "0": "COMUNICAZIONE TRA CENTRALINE OK",
        "1": "COMUNICAZIONE TRA CENTRALINE FALLITA",      
    },
      "FCCUCOM": {
        "0": "COMUNICAZIONE CON CCU OK",
        "1": "COMUNICAZIONE CON CCU FALLITA",      
    },
      "FSMOKESENS": {
        "0": "OK",
        "1": "MANUTENZIONE RICHIESTA SU SENSORE",
        "2": "SENSORE SPORCO",
        "3": "FAULT",
        "4": "SENSORE NON PRESENTE",
    },
     "FAEROSOL": {
        "0": "OK",
        "1": "CIRCUITO APERTO AEROSOL",
        "2": "VALORE INSTABILE AEROSOL",
        "3": "CANALE INSTABILE AEROSOL",
        "4": "COMANDO AEROSOL ATTIVO",
        "5": "24V NON PRESENTE",
    },
       "IAEROCARTRIDGESTATE": {
        "0": "OK",
        "1": "CARTUCCIA ATTIVA",
        "2": "CARTUCCIA SPARATA",
        "3": "FAULT",
        "4": "NESSUNA CARTUCCIA",
     },   
        "ICARFIREALARM": {
        "0": "NESSUN ALLARME",
        "1": "PRE-ALLARME AREA PASSEGGERI",
        "2": "ALLARME AREA PASSEGGERI",
        "3": "ALLARME AREA TECNICA",
        "4": "PRE-ALLARME AREA PASSEGGERI E ALLARME AREA TECNICA",
        "5": "ALLARME AREA TECNICA E PASSEGGERI",
    },
        "FELECTROVALVES": {
        "0": "ELETTROVALVOLA OK",
        "1": "CIRCUITO APERTO",
        "2": "VALORE INSTABILE",
        "3": "CANALE INSTABILE",
        "4": "24V NON PRESENTE",
     },   
        "ITECHAREAMODE": {
        "1": "STARTING",
        "2": "STANDBY",
        "3": "ALLARME",
        "4": "SPEGNIMENTO FUOCO AREA TECNICA",
        "5": "TEST/MANUTENZIONE",
     },
        "FFIREONBOARDTX": {
        "0": "NESSUN FUOCO A BORDO TRASMESSO",
        "1": "FUOCO A BORDO TRASMESSO",
     },
        "IFIREONBOARDTX": {
        "0": "ALLARME TRASMESSO IN ACCOPPIATA",
        "1": "NESSUN ALLARME TRASMESSO IN ACCOPPIATA",
     },  
        "FSMOKESENSLOOP": {
        "0": "LOOP OK",
        "1": "LOOP INTERROTTO IN DM1",
        "2": "LOOP INTERROTTO IN TT2",
        "3": "LOOP INTERROTTO IN M3",
        "4": "LOOP INTERROTTO IN T4",
        "5": "LOOP INTERROTTO IN T5",
        "6": "LOOP INTERROTTO IN M6",
        "7": "LOOP INTERROTTO IN TT7",
        "8": "LOOP INTERROTTO IN DM8",
      },
        "IGENSYSTEMMODE": {
        "0": "NON ALIMENTATO",
        "1": "SISTEMA IN SERVIZIO",
        "2": "SISTEMA DEGRADATO",
        "3": "SISTEMA FUORI SERVIZIO",
        "4": "INIZIALIZZAZIONE",
        "10": "MODALITA' TEST",
        "11": "MODALITA' CARICAMENTO SW",
      },
        "ISPECSYSTOKMODE": {
        "0": "MASTER",
        "1": "SLAVE",
        },
        "IMAUINPUTSTATE": {
        "0": "NON ATTIVO",
        "1": "ATTIVO",
    },
 

}

# ==================================================
# DECODIFICA CASSA
# ==================================================
def decodifica_cassa(val):
    MAPPA_CASSA = {
        "1": "DM1",
        "2": "TT2",
        "3": "M3",
        "4": "T4",
        "5": "T5",
        "6": "M6",
        "7": "TT7",
        "8": "DM8",
    }
    return MAPPA_CASSA.get(val, val)

# ==================================================
# UTILITY
# ==================================================
def normalizza_segnale(segnale: str) -> str:
    return re.split(r"[\[_]", segnale)[0].strip()

def parse_dato(valore: str):
    coach = "-"
    number = "-"
    data = "-"

    m = re.search(r"COACH\s*N\s*:\s*(\d+)", valore, re.IGNORECASE)
    if m:
        coach = decodifica_cassa(m.group(1))

    m = re.search(r"NUMBER\s*:\s*(\d+)", valore, re.IGNORECASE)
    if m:
        number = m.group(1)

    m = re.search(r"DATA\s*:\s*(\d+)", valore, re.IGNORECASE)
    if m:
        data = m.group(1)

    return coach, number, data

def decodifica_data_segnale(segnale_norm, data_val):
    seg = segnale_norm.upper()
    for key, mapping in DECODIFICHE.items():
        if seg.startswith(key):
            return mapping.get(data_val, data_val)
    return data_val

# ==================================================
# TIMESTAMP
# ==================================================
def parse_timestamp(ts_raw):
    try:
        return datetime.strptime(
            " ".join(ts_raw.split()),
            "%a %b %d %H:%M:%S %Y"
        )
    except:
        return None

# ==================================================
# PARSER LOG
# ==================================================
def importa_log(percorso):
    dati = []
    timestamp = None
    dataset = None
    segnale = None

    with open(percorso, encoding="utf-8", errors="ignore") as f:
        for riga in f:
            r = riga.strip()

            if r.startswith("------->"):
                timestamp = parse_timestamp(r.replace("------->", "").strip())
                dataset = None
                segnale = None
                continue

            if not timestamp:
                continue

            if segnale and r and "/" not in r:
                dati.append([
                    timestamp,
                    dataset,
                    segnale,
                    r.replace("\x00", "").strip()
                ])
                segnale = None
                dataset = None
                continue

            for ds in DATASETS:
                if ds + "/" in r:
                    segnale = r.split(ds + "/", 1)[1].split(":", 1)[0].strip()
                    dataset = ds
                    break

    return pd.DataFrame(
        dati,
        columns=["timestamp", "dataset", "segnale", "valore"]
    )



# ==========================================================
# STREAMLIT + PLOTLY
# ==========================================================
def prepara_eventi(df, origine):
    if df is None or df.empty:
        return pd.DataFrame()
    df=df.copy(); df['origine']=origine
    casse=[]; numbers=[]; date_valori=[]; descrizioni=[]; tags=[]
    for _,r in df.iterrows():
        cassa,number,data_val=parse_dato(r['valore'])
        data_dec=decodifica_data_segnale(r['segnale_norm'],data_val)
        segnale=str(r['segnale_norm']).upper()
        if segnale.startswith('ISMOKESENSSTATE'):
            number=DECODIFICA_NUMBER_SMOKE.get(str(number),number)
        elif segnale.startswith('FSMOKESENS'):
            number=DECODIFICA_NUMBER_SMOKE.get(str(number),number)
        elif segnale.startswith('IMAUINPUTSTATE'):
            data_dec=DECODIFICHE['IMAUINPUTSTATE'].get(str(data_val),data_val)
            number=DECODIFICA_NUMBER_MAU.get(str(number),data_dec)
        tag='NORMALE'
        if segnale.startswith('ISMOKESENSSTATE') or segnale.startswith('FSMOKESENS'):
            if data_dec in ('ALLARME FUMO','ALLARME FUMO E TERMICO'): tag='FUMO'
            elif data_dec=='ALLARME TERMICO': tag='TERMICO'
            elif data_dec=='FAULT': tag='FAULT_SMOKE'
        else:
            if data_dec=='SISTEMA FUORI SERVIZIO': tag='FUORI SERVIZIO'
            elif data_dec=='ALLARME INCENDIO': tag='ALLARME INCENDIO'
            elif number=='BASSA PRESSIONE': tag='BASSA PRESSIONE'
            elif number=='CONDOTTA ACQUA PRESSURIZZATA': tag='CONDOTTA ACQUA PRESSURIZZATA'
        casse.append(cassa); numbers.append(number); date_valori.append(data_val); descrizioni.append(data_dec); tags.append(tag)
    df['cassa']=casse; df['number']=numbers; df['data_val']=date_valori; df['descrizione']=descrizioni; df['evento']=tags
    return df

COLORI_EVENTO={'FUMO':'#ff7f50','TERMICO':'#ff7f50','FAULT_SMOKE':'#9e9e9e','ALLARME INCENDIO':'#ff4d4d','FUORI SERVIZIO':'#ff4d4d','BASSA PRESSIONE':'#008f39','CONDOTTA ACQUA PRESSURIZZATA':'#008f39','NORMALE':'#808080'}

def importa_log_streamlit(uploaded_file):
    dati=[]; timestamp=None; dataset=None; segnale=None
    testo=uploaded_file.getvalue().decode('utf-8',errors='ignore')
    for riga in testo.splitlines():
        r=riga.strip()
        if r.startswith('------->'):
            timestamp=parse_timestamp(r.replace('------->','').strip()); dataset=None; segnale=None; continue
        if not timestamp: continue
        if segnale and r and '/' not in r:
            dati.append([timestamp,dataset,segnale,r.replace('\\x00','').strip()]); segnale=None; dataset=None; continue
        for ds in DATASETS:
            if ds+'/' in r:
                segnale=r.split(ds+'/',1)[1].split(':',1)[0].strip(); dataset=ds; break
    df=pd.DataFrame(dati,columns=['timestamp','dataset','segnale','valore'])
    if not df.empty: df['segnale_norm']=df['segnale'].apply(normalizza_segnale)
    return df

def fde_page():
    import plotly.express as px
    st.title('📊 Analizzatore Log FDE')
    st.caption('Analisi interattiva dei log FDE DM1 + DM8')
    c1,c2=st.columns(2)
    with c1: file_dm1=st.file_uploader('📥 Carica Log DM1',type=None,key='fde_dm1')
    with c2: file_dm8=st.file_uploader('📥 Carica Log DM8',type=None,key='fde_dm8')
    if file_dm1 is None and file_dm8 is None:
        st.info('Carica almeno un Log DM1 o DM8 per iniziare.'); return
    frames=[]
    for f,origine in ((file_dm1,'DM1'),(file_dm8,'DM8')):
        if f is not None:
            d=importa_log_streamlit(f)
            if d.empty: st.warning(f'Il Log {origine} non contiene eventi riconosciuti.')
            else: frames.append(prepara_eventi(d,origine))
    if not frames: st.error('Nessun evento riconosciuto nei file caricati.'); return
    df=pd.concat(frames,ignore_index=True).sort_values('timestamp').reset_index(drop=True)
    dmin=df.timestamp.min().date(); dmax=df.timestamp.max().date()
    st.divider()
    c1,c2,c3,c4=st.columns(4)
    with c1: data_da=st.date_input('📅 Da',dmin,min_value=dmin,max_value=dmax,key='fde_da')
    with c2: data_a=st.date_input('📅 A',dmax,min_value=dmin,max_value=dmax,key='fde_a')
    with c3: orig=st.multiselect('💻 Origine',['DM1','DM8'],default=['DM1','DM8'],key='fde_orig')
    with c4: evsel=st.multiselect('🚨 Tipo evento',sorted(df.evento.unique()),key='fde_ev')
    ricerca=st.text_input('🔍 Cerca',placeholder='Segnale, dataset, valore, cassa, sensore, descrizione...')
    da=datetime.combine(data_da,datetime.min.time()); a=datetime.combine(data_a,datetime.max.time())
    out=df[(df.timestamp>=da)&(df.timestamp<=a)].copy()
    if orig: out=out[out.origine.isin(orig)]
    if evsel: out=out[out.evento.isin(evsel)]
    if ricerca.strip():
        q=ricerca.strip().lower(); mask=pd.Series(False,index=out.index)
        for col in ['origine','dataset','segnale_norm','valore','cassa','number','descrizione','evento']:
            mask |= out[col].astype(str).str.lower().str.contains(q,na=False,regex=False)
        out=out[mask]
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Eventi',len(out)); c2.metric('DM1',int((out.origine=='DM1').sum())); c3.metric('DM8',int((out.origine=='DM8').sum())); c4.metric('Allarmi / Fault',int((out.evento!='NORMALE').sum()))
    if out.empty: st.warning('Nessun evento trovato con i filtri selezionati.'); return
    st.subheader('📈 Timeline FDE')
    plot=out.copy(); plot['asse_y']=plot.segnale_norm.astype(str)
    fig=px.scatter(plot,x='timestamp',y='asse_y',color='evento',symbol='origine',color_discrete_map=COLORI_EVENTO,hover_data={'timestamp':'|%d-%m-%Y %H:%M:%S','origine':True,'dataset':True,'segnale_norm':True,'cassa':True,'number':True,'data_val':True,'descrizione':True,'valore':True,'asse_y':False},labels={'timestamp':'Data / Ora','asse_y':'Segnale','evento':'Evento','origine':'Origine'})
    fig.update_traces(marker=dict(size=10,line=dict(width=.5)))
    fig.update_layout(height=max(550,min(1100,350+plot.segnale_norm.nunique()*22)),hovermode='closest',margin=dict(l=10,r=10,t=30,b=10),legend_title_text='Tipo evento',xaxis=dict(rangeslider=dict(visible=True),type='date'))
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'scrollZoom':True,'responsive':True})
    st.subheader(f'📋 Eventi ({len(out)})')
    tab=out.copy(); tab['Time']=tab.timestamp.dt.strftime('%d-%m-%Y // %H:%M:%S')
    tab=tab[['Time','origine','dataset','segnale_norm','cassa','number','data_val','descrizione','evento','valore']].rename(columns={'origine':'Origine','dataset':'Dataset','segnale_norm':'Segnale','cassa':'Cassa','number':'Number','data_val':'Data','descrizione':'Descrizione','evento':'Evento','valore':'Valore grezzo'})
    st.dataframe(tab,use_container_width=True,hide_index=True,height=600)
    st.download_button('📥 Scarica risultati CSV',tab.to_csv(index=False).encode('utf-8-sig'),'analisi_fde.csv','text/csv')
