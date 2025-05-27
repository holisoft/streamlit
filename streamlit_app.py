import streamlit as st
import requests
import pandas as pd

# Configura la pagina
st.set_page_config(page_title="HoliSoft PDF Processor", layout="wide")

# Titolo e breve descrizione del servizio
st.title("📄 HoliSoft PDF Processor")
st.markdown(
    "Benvenuto in **HoliSoft PDF Processor**, il servizio di HoliSoft che ti permette di elaborare PDF non strutturati "
    "e trasformarli in dati strutturati, pronti per essere importati nel tuo gestionale."
)
st.markdown("---")
st.markdown("### Prova il servizio")

# 1) Funzione per ottenere il token
@st.cache_data
def get_token():
    url = st.secrets["api"]["auth_url"]
    payload = {
        "username": st.secrets["api"]["username"],
        "password": st.secrets["api"]["password"],
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    # Restituisce il campo "access_token" o "token" a seconda dell’API
    return data.get("access_token") or data.get("token")

# 2) Funzione per inviare il PDF all’API di processing
def process_pdf(token: str, pdf_bytes: bytes):
    url = st.secrets["api"]["process_url"]
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("document.pdf", pdf_bytes, "application/pdf")}
    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()

def main():
    st.title("📄 PDF → API Processor")

    # Upload del file PDF
    uploaded_file = st.file_uploader("Carica qui il tuo PDF", type="pdf")
    if not uploaded_file:
        return

    # 3) Ottieni token
    with st.spinner("Ottenendo token…"):
        try:
            token = get_token()
        except Exception as e:
            st.error(f"Errore autenticazione: {e}")
            return

    # 4) Processa il PDF
    with st.spinner("Elaborando il PDF…"):
        try:
            result = process_pdf(token, uploaded_file.read())
        except Exception as e:
            st.error(f"Errore durante l’elaborazione: {e}")
            return

    st.success("Elaborazione completata!")

    # ------------------------------------------------
    # 5) Mostra i dati di testata in un riquadro (st.info)
    # ------------------------------------------------
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

    # ------------------------------------------------
    # 6) Mostra la lista degli articoli in tabella
    # ------------------------------------------------
    articoli = result["data"]["Articoli"]
    df = pd.DataFrame(articoli)

    st.markdown("### 📋 Lista Articoli")
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
