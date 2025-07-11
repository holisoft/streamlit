import streamlit as st
import requests
import pandas as pd
from PIL import Image

# Configura la pagina
st.set_page_config(page_title="HoliSoft PDF Processor", layout="wide")

# Carica il logo 
try:
    logo = Image.open("holisoft_logo.png")
    st.image(logo, width=150)
except FileNotFoundError:
    st.write("Logo non trovato. Assicurati di avere 'holisoft_logo.png' nella cartella del progetto.")

# Hero section: titolo e descrizione
st.title("Dì addio al data entry manuale dei DDT")
st.subheader("L'AI di HoliSoft trasforma i tuoi PDF non strutturati in dati importabili nel gestionale in pochi secondi.")

# Features in tre colonne
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.markdown("### 🚀 Velocità - Estrai dati da PDF in meno di un minuto.")
col2.markdown("### 🎯 Precisione - Riduci errori di digitazione e incongruenze.")
col3.markdown("### 🔄 Integrazione - Importa i dati da un JSON pronti per il tuo gestionale.")

st.markdown("---")

# Invito all'azione
st.markdown("## Prova il servizio ora")
st.markdown("Carica un PDF di DDT e guarda l'AI all'opera:")

# Campi opzionali per Partita IVA
st.markdown("### Inserisci opzionalmente le Partite IVA:")
partita_iva_cliente = st.text_input("Partita IVA Cliente (opzionale)")
partita_iva_fornitore = st.text_input("Partita IVA Fornitore (opzionale)")

# Funzioni di autenticazione e processing
def get_token():
    url = st.secrets["api"]["auth_url"]
    payload = {
        "username": st.secrets["api"]["username"],
        "password": st.secrets["api"]["password"],
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data.get("access_token") or data.get("token")

def process_pdf(token: str, pdf_bytes: bytes, partita_iva_cliente=None, partita_iva_fornitore=None):
    url = st.secrets["api"]["process_url"]
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("document.pdf", pdf_bytes, "application/pdf")}
    
    data = {
	    "test": "true"
    }   
    if partita_iva_cliente:
        data["customer"] = partita_iva_cliente
    if partita_iva_fornitore:
        data["supplier"] = partita_iva_fornitore

    resp = requests.post(url, headers=headers, files=files, data=data)
    resp.raise_for_status()
    return resp.json()

# Applicazione principale
uploaded_file = st.file_uploader("Carica il tuo PDF", type="pdf")
if uploaded_file:
    with st.spinner("Ottenendo token…"):
        try:
            token = get_token()
        except Exception as e:
            st.error(f"Errore autenticazione: {e}")
            st.stop()

    with st.spinner("Elaborando il PDF…"):
        try:
            pdf_bytes = uploaded_file.read()
            result = process_pdf(token, pdf_bytes, partita_iva_cliente, partita_iva_fornitore)
        except Exception as e:
            st.error(f"Errore durante l'elaborazione: {e}")
            st.stop()

    st.success("Elaborazione completata!")

    # Dati di testata
    testata = result["data"]["TestataDocumento"]
    doc   = testata["Documento"]
    forn  = testata["Fornitore"]
    cli   = testata["Cliente"]

    header_md = f"""
**Documento**  
- Numero: {doc['Numero']}  
- Tipo: {doc['Tipo']}  
- Data: {doc['Data']}  

**Fornitore**  
- Ragione Sociale: {forn['RagioneSociale']}  
- P.IVA: {forn['PartitaIva']}  

**Cliente**  
- Ragione Sociale: {cli['RagioneSociale']}  
- P.IVA: {cli['PartitaIva']}  
"""
    st.info(header_md)

    # Tabella articoli
    articoli = result["data"]["Articoli"]
    df = pd.DataFrame(articoli)
    st.markdown("### 📋 Lista Articoli")
    st.dataframe(df, use_container_width=True)
