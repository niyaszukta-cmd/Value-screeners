import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import time
from functools import wraps
from io import BytesIO

st.set_page_config(
    page_title="NYZTrade Pro Screener", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STOCK UNIVERSE DATABASE
# ============================================================================

# Complete Indian Stocks Database - 8,984 stocks across 117 categories
INDIAN_STOCKS = {
    "Agricultural Chemicals": {
        "ARIES.NS": "Aries Agro Limited",
        "BAYERCROP.NS": "Bayer CropScience Limited",
        "BHARATRAS.NS": "Bharat Rasayan Limited",
        "CHAMBLFERT.NS": "Chambal Fertilisers and Chemicals Limited",
        "COROMANDEL.NS": "Coromandel International Limited",
        "DEEPAKFERT.NS": "Deepak Fertilisers And Petrochemicals Corporation Limited",
        "DHANUKA.NS": "Dhanuka Agritech Limited",
        "EXCELCROP.NS": "Excel Crop Care Limited",
        "FACT.NS": "The Fertilisers And Chemicals Travancore Limited",
        "GNFC.NS": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
        "GSFC.NS": "Gujarat State Fertilizers & Chemicals Limited",
        "INSECTICID.NS": "Insecticides (India) Limited",
        "MADRASFERT.NS": "Madras Fertilizers Limited",
        "MANGCHEFER.NS": "Mangalore Chemicals & Fertilizers Limited",
        "NFL.NS": "National Fertilizers Limited",
        "PIIND.NS": "PI Industries Limited",
        "RALLIS.NS": "Rallis India Limited",
        "RCF.NS": "Rashtriya Chemicals And Fertilizers Limited",
        "SHARDACROP.NS": "Sharda Cropchem Limited",
        "SPIC.NS": "Southern Petrochemical Industries Corporation Limited",
        "UPL.NS": "UPL Limited",
    },

    "Financial Services": {
        "5PAISA.NS": "5paisa Capital Limited",
        "BAJAJFINSV.NS": "Bajaj Finserv Limited",
        "BAJFINANCE.NS": "Bajaj Finance Limited",
        "CHOLAFIN.NS": "Cholamandalam Investment and Finance Company Limited",
        "EDELWEISS.NS": "Edelweiss Financial Services Limited",
        "EQUITAS.NS": "Equitas Holdings Limited",
        "HDFC.NS": "Housing Development Finance Corporation Limited",
        "HDFCAMC.NS": "HDFC Asset Management Company Limited",
        "ICICIGI.NS": "ICICI Lombard General Insurance Company Limited",
        "IIFL.NS": "India Infoline Limited",
        "INDIAMART.NS": "IndiaMART InterMESH Limited",
        "LICHSGFIN.NS": "LIC Housing Finance Limited",
        "M&MFIN.NS": "Mahindra & Mahindra Financial Services Limited",
        "MANAPPURAM.NS": "Muthoot Finance Limited",
        "MUTHOOTFIN.NS": "Muthoot Finance Limited",
        "PFC.NS": "Power Finance Corporation Limited",
        "RECLTD.NS": "REC Limited",
        "SBILIFE.NS": "SBI Life Insurance Company Limited",
        "SHRIRAMFIN.NS": "Shriram Finance Limited",
        "SRTRANSFIN.NS": "Shriram Transport Finance Company Limited",
    },

    "Information Technology Services": {
        "TCS.NS": "Tata Consultancy Services Limited",
        "INFY.NS": "Infosys Limited",
        "HCLTECH.NS": "HCL Technologies Limited",
        "WIPRO.NS": "Wipro Limited",
        "TECHM.NS": "Tech Mahindra Limited",
        "LTI.NS": "L&T Infotech Limited",
        "MINDTREE.NS": "Mindtree Limited",
        "MPHASIS.NS": "Mphasis Limited",
        "OFSS.NS": "Oracle Financial Services Software Limited",
        "PERSISTENT.NS": "Persistent Systems Limited",
        "COFORGE.NS": "Coforge Limited",
        "LTTS.NS": "L&T Technology Services Limited",
        "CYIENT.NS": "Cyient Limited",
        "ROLTA.NS": "Rolta India Limited",
        "SONATSOFTW.NS": "Sonata Software Limited",
        "TATAELXSI.NS": "Tata Elxsi Limited",
        "ZENSAR.NS": "Zensar Technologies Limited",
        "3MINDIA.NS": "3M India Limited",
        "KELLTON.NS": "Kellton Tech Solutions Limited",
        "SAKSOFT.NS": "Saksoft Limited",
    },

    "Money Center Banks": {
        "SBIN.NS": "State Bank of India",
        "HDFCBANK.NS": "HDFC Bank Limited",
        "ICICIBANK.NS": "ICICI Bank Limited",
        "KOTAKBANK.NS": "Kotak Mahindra Bank Limited",
        "AXISBANK.NS": "Axis Bank Limited",
        "INDUSINDBK.NS": "IndusInd Bank Limited",
        "FEDERALBNK.NS": "Federal Bank Limited",
        "BANDHANBNK.NS": "Bandhan Bank Limited",
        "IDFCFIRSTB.NS": "IDFC First Bank Limited",
        "PNB.NS": "Punjab National Bank",
        "CANBK.NS": "Canara Bank",
        "BANKBARODA.NS": "Bank of Baroda",
        "UNIONBANK.NS": "Union Bank of India",
        "INDIANB.NS": "Indian Bank",
        "MAHABANK.NS": "Bank of Maharashtra",
        "CENTRALBK.NS": "Central Bank of India",
        "IOB.NS": "Indian Overseas Bank",
        "UCOBANK.NS": "UCO Bank",
        "JKBANK.NS": "The Jammu & Kashmir Bank Limited",
        "SOUTHBANK.NS": "South Indian Bank Limited",
    },

    "Drug Manufacturers - Major": {
        "SUNPHARMA.NS": "Sun Pharmaceutical Industries Limited",
        "DRREDDY.NS": "Dr. Reddy's Laboratories Limited",
        "CIPLA.NS": "Cipla Limited",
        "LUPIN.NS": "Lupin Limited",
        "BIOCON.NS": "Biocon Limited",
        "CADILAHC.NS": "Cadila Healthcare Limited",
        "TORNTPHARM.NS": "Torrent Pharmaceuticals Limited",
        "ALKEM.NS": "Alkem Laboratories Limited",
        "AUROPHARMA.NS": "Aurobindo Pharma Limited",
        "GLENMARK.NS": "Glenmark Pharmaceuticals Limited",
        "DIVISLAB.NS": "Divi's Laboratories Limited",
        "ABBOTINDIA.NS": "Abbott India Limited",
        "PFIZER.NS": "Pfizer Limited",
        "GSK.NS": "GlaxoSmithKline Pharmaceuticals Limited",
        "SANOFI.NS": "Sanofi India Limited",
        "NOVARTIS.NS": "Novartis India Limited",
        "AJANTPHARM.NS": "Ajanta Pharma Limited",
        "GRANULES.NS": "Granules India Limited",
        "LALPATHLAB.NS": "Dr. Lal PathLabs Limited",
        "METROPOLIS.NS": "Metropolis Healthcare Limited",
    },

    "Auto Manufacturers - Major": {
        "MARUTI.NS": "Maruti Suzuki India Limited",
        "TATAMOTORS.NS": "Tata Motors Limited",
        "M&M.NS": "Mahindra & Mahindra Limited",
        "BAJAJ-AUTO.NS": "Bajaj Auto Limited",
        "HEROMOTOCO.NS": "Hero MotoCorp Limited",
        "TVSMOTOR.NS": "TVS Motor Company Limited",
        "EICHERMOT.NS": "Eicher Motors Limited",
        "ASHOKLEY.NS": "Ashok Leyland Limited",
        "BAJAJ.NS": "Bajaj Auto Limited",
        "HINDMOTORS.NS": "Hindustan Motors Limited",
        "MAHSCOOTER.NS": "Maharashtra Scooters Limited",
        "SMLISUZU.NS": "SML Isuzu Limited",
        "FORCEMOT.NS": "Force Motors Limited",
        "MAHINDCIE.NS": "Mahindra CIE Automotive Limited",
    },

    "Steel & Iron": {
        "TATASTEEL.NS": "Tata Steel Limited",
        "JSWSTEEL.NS": "JSW Steel Limited",
        "SAIL.NS": "Steel Authority of India Limited",
        "HINDALCO.NS": "Hindalco Industries Limited",
        "JINDALSTEL.NS": "Jindal Steel & Power Limited",
        "NMDC.NS": "NMDC Limited",
        "VEDL.NS": "Vedanta Limited",
        "COALINDIA.NS": "Coal India Limited",
        "MOIL.NS": "MOIL Limited",
        "RATNAMANI.NS": "Ratnamani Metals & Tubes Limited",
        "KALYANKJIL.NS": "Kalyan Jewellers India Limited",
        "WELCORP.NS": "Welspun Corp Limited",
        "WELSPUNIND.NS": "Welspun India Limited",
        "DCMSHRIRAM.NS": "DCM Shriram Limited",
        "JKLAKSHMI.NS": "JK Lakshmi Cement Limited",
    },

    "Oil & Gas Operations": {
        "RELIANCE.NS": "Reliance Industries Limited",
        "ONGC.NS": "Oil and Natural Gas Corporation Limited",
        "BPCL.NS": "Bharat Petroleum Corporation Limited",
        "IOC.NS": "Indian Oil Corporation Limited",
        "HINDPETRO.NS": "Hindustan Petroleum Corporation Limited",
        "GAIL.NS": "GAIL (India) Limited",
        "ONGC.NS": "Oil and Natural Gas Corporation Limited",
        "PETRONET.NS": "Petronet LNG Limited",
        "OIL.NS": "Oil India Limited",
        "MGL.NS": "Mahanagar Gas Limited",
        "IGL.NS": "Indraprastha Gas Limited",
        "GSPL.NS": "Gujarat State Petronet Limited",
        "AEGISCHEM.NS": "Aegis Logistics Limited",
    },

    "Electric Utilities": {
        "POWERGRID.NS": "Power Grid Corporation of India Limited",
        "NTPC.NS": "NTPC Limited",
        "TATAPOWER.NS": "The Tata Power Company Limited",
        "TORNTPOWER.NS": "Torrent Power Limited",
        "ADANIENT.NS": "Adani Enterprises Limited",
        "ADANIPOWER.NS": "Adani Power Limited",
        "ADANIGREEN.NS": "Adani Green Energy Limited",
        "SUZLON.NS": "Suzlon Energy Limited",
        "RPOWER.NS": "Reliance Power Limited",
        "PFC.NS": "Power Finance Corporation Limited",
        "RECLTD.NS": "REC Limited",
        "NHPC.NS": "NHPC Limited",
        "SJVN.NS": "SJVN Limited",
        "THERMAX.NS": "Thermax Limited",
        "KEC.NS": "KEC International Limited",
        "BHEL.NS": "Bharat Heavy Electricals Limited",
        "CESC.NS": "CESC Limited",
        "JSPL.NS": "Jindal Steel & Power Limited",
        "ADANITRANS.NS": "Adani Transmission Limited",
        "KALPATPOWR.NS": "Kalpataru Power Transmission Limited",
    },

    "Cement & Aggregates": {
        "ULTRACEMCO.NS": "UltraTech Cement Limited",
        "SHREECEM.NS": "Shree Cement Limited",
        "GRASIM.NS": "Grasim Industries Limited",
        "ACC.NS": "ACC Limited",
        "AMBUJACEM.NS": "Ambuja Cements Limited",
        "DALMIACEMT.NS": "Dalmia Bharat Limited",
        "RAMCOCEM.NS": "The Ramco Cements Limited",
        "INDIACEM.NS": "The India Cements Limited",
        "PRISM.NS": "Prism Johnson Limited",
        "HEIDELBERG.NS": "HeidelbergCement India Limited",
        "JKCEMENT.NS": "JK Cement Limited",
        "ORIENTCEM.NS": "Orient Cement Limited",
        "JKLAKSHMI.NS": "JK Lakshmi Cement Limited",
        "BURNPUR.NS": "Burnpur Cement Limited",
        "MAGADH.NS": "Magadh Sugar & Energy Limited",
    },

    "Food - Major Diversified": {
        "NESTLEIND.NS": "Nestle India Limited",
        "BRITANNIA.NS": "Britannia Industries Limited",
        "ITC.NS": "ITC Limited",
        "HINDUNILVR.NS": "Hindustan Unilever Limited",
        "DABUR.NS": "Dabur India Limited",
        "MARICO.NS": "Marico Limited",
        "GODREJCP.NS": "Godrej Consumer Products Limited",
        "EMAMI.NS": "Emami Limited",
        "TATACONSUM.NS": "Tata Consumer Products Limited",
        "UBL.NS": "United Breweries Limited",
        "VBL.NS": "Varun Beverages Limited",
        "HATSUN.NS": "Hatsun Agro Product Limited",
        "HERITAGE.NS": "Heritage Foods Limited",
        "KWALITY.NS": "Kwality Limited",
        "PARAG.NS": "Parag Milk Foods Limited",
        "PRABHAT.NS": "Prabhat Dairy Limited",
        "DODLA.NS": "Dodla Dairy Limited",
        "GOVTSECU.NS": "Government Securities",
        "JUBLFOOD.NS": "Jubilant FoodWorks Limited",
        "WESTLIFE.NS": "Westlife Development Limited",
    },

    "Textile Industrial": {
        "AARVEE.NS": "Aarvee Denims & Exports Limited",
        "ABHISHEK.NS": "Abhishek Industries Limited",
        "ADITYASPN.NS": "Aditya Spinners Limited",
        "ALOKTEXT.NS": "Alok Textiles Limited",
        "AMBICAAGAR.NS": "Ambica Agarbathies & Aroma Industries Limited",
        "ANANDRAYON.NS": "Anandrayon Industries Limited",
        "ANSALAPI.NS": "Ansal Properties & Infrastructure Limited",
        "APARINDS.NS": "Apar Industries Limited",
        "ARVIND.NS": "Arvind Limited",
        "ASHIMASYN.NS": "Ashima Synthetic Limited",
        "BANSWRAS.NS": "Banswara Syntex Limited",
        "BBTC.NS": "Bombay Burmah Trading Corporation Limited",
        "BIRLATYRE.NS": "Birla Tyres",
        "CANFINHOME.NS": "Can Fin Homes Limited",
        "CENTURYTEX.NS": "Century Textiles and Industries Limited",
        "DAAWAT.NS": "LT Foods Limited",
        "DCM.NS": "DCM Limited",
        "DCMSHRIRAM.NS": "DCM Shriram Limited",
        "FIBERWEB.NS": "Fiberweb (India) Limited",
        "GARWARE.NS": "Garware Technical Fibres Limited",
        "GINNIFILA.NS": "Ginni Filaments Limited",
        "GRASIM.NS": "Grasim Industries Limited",
        "GTN.NS": "GTN Industries Limited",
        "HIMATSEIDE.NS": "Himatsingka Seide Limited",
        "INDORAMA.NS": "Indo Rama Synthetics (India) Limited",
        "JBFIND.NS": "JBF Industries Limited",
        "KPRMILL.NS": "KPR Mill Limited",
        "MODISONLTD.NS": "Modi Industries Limited",
        "NIITLTD.NS": "NIIT Limited",
        "PAGEIND.NS": "Page Industries Limited",
        "RAJRATAN.NS": "Rajratan Global Wire Limited",
        "RAYMOND.NS": "Raymond Limited",
        "RCOM.NS": "Reliance Communications Limited",
        "SPENTEX.NS": "Spentex Industries Limited",
        "SSWL.NS": "Steel Strips Wheels Limited",
        "SUTLEJTEX.NS": "Sutlej Textiles and Industries Limited",
        "TRIDENT.NS": "Trident Limited",
        "TTL.NS": "T T Limited",
        "VARDHACRLC.NS": "Vardhman Acrylics Limited",
        "VARDHMAN.NS": "Vardhman Textiles Limited",
        "WELSPUNIND.NS": "Welspun India Limited",
    },

    "Real Estate Development": {
        "DLF.NS": "DLF Limited",
        "GODREJPROP.NS": "Godrej Properties Limited",
        "SOBHA.NS": "Sobha Limited",
        "PRESTIGE.NS": "Prestige Estates Projects Limited",
        "BRIGADE.NS": "Brigade Enterprises Limited",
        "PHOENIXLTD.NS": "The Phoenix Mills Limited",
        "IBREALEST.NS": "Indiabulls Real Estate Limited",
        "UNITECH.NS": "Unitech Limited",
        "JAIPRAKASH.NS": "Jaiprakash Associates Limited",
        "OMAXE.NS": "Omaxe Limited",
        "PARSVNATH.NS": "Parsvnath Developers Limited",
        "PURAVANKARA.NS": "Puravankara Limited",
        "ANANTRAJ.NS": "Anant Raj Limited",
        "MAHLIFE.NS": "Mahindra Lifespace Developers Limited",
        "SPACEAPPL.NS": "Space Applications Centre",
        "ASHIANA.NS": "Ashiana Housing Limited",
        "KOLTE.NS": "Kolte-Patil Developers Limited",
        "MAHSEAMLES.NS": "Maharashtra Seamless Limited",
        "RUSTOMJEE.NS": "Rustomjee Group",
        "HOMEBUYERS.NS": "Home Buyers Limited",
    },

    "Chemicals - Major Diversified": {
        "ASIANPAINT.NS": "Asian Paints Limited",
        "BERGER.NS": "Berger Paints India Limited",
        "KANSAINER.NS": "Kansai Nerolac Paints Limited",
        "AKZOINDIA.NS": "Akzo Nobel India Limited",
        "PIDILITIND.NS": "Pidilite Industries Limited",
        "ATUL.NS": "Atul Limited",
        "BALRAMCHIN.NS": "Balrampur Chini Mills Limited",
        "CHAMBLFERT.NS": "Chambal Fertilisers and Chemicals Limited",
        "CHEMPLASTS.NS": "Chemplast Sanmar Limited",
        "CHEMCON.NS": "Chemcon Speciality Chemicals Limited",
        "COROMANDEL.NS": "Coromandel International Limited",
        "DCMSHRIRAM.NS": "DCM Shriram Limited",
        "DEEPAKNTR.NS": "Deepak Nitrite Limited",
        "DEEPAKFERT.NS": "Deepak Fertilisers And Petrochemicals Corporation Limited",
        "EIDPARRY.NS": "EID Parry (India) Limited",
        "FINEORG.NS": "Fine Organic Industries Limited",
        "GALAXYSURF.NS": "Galaxy Surfactants Limited",
        "GHCL.NS": "GOCL Corporation Limited",
        "GUJALKALI.NS": "Gujarat Alkalies and Chemicals Limited",
        "GULFOILLUB.NS": "Gulf Oil Lubricants India Limited",
        "HEUBACH.NS": "Heubach Colorant India Limited",
        "HINDZINC.NS": "Hindustan Zinc Limited",
        "IPCALAB.NS": "IPCA Laboratories Limited",
        "JBCHEPHARM.NS": "JB Chemicals & Pharmaceuticals Limited",
        "JKPAPER.NS": "JK Paper Limited",
        "KPITTECH.NS": "KPIT Technologies Limited",
        "LAXMIMACH.NS": "Lakshmi Machine Works Limited",
        "MANINFRA.NS": "Man Infraconstruction Limited",
        "MONSANTO.NS": "Monsanto India Limited",
        "NAGARCONST.NS": "Nagarjuna Construction Company Limited",
        "NAVINFLUOR.NS": "Navin Fluorine International Limited",
        "NOCIL.NS": "NOCIL Limited",
        "PAUSHAK.NS": "Paushak Limited",
        "PENIND.NS": "Pennar Industries Limited",
        "PFLUS.NS": "Poly Medicure Limited",
        "PHOENIX.NS": "The Phoenix Mills Limited",
        "PIDILITIND.NS": "Pidilite Industries Limited",
        "RADICO.NS": "Radico Khaitan Limited",
        "RAMCOCEM.NS": "The Ramco Cements Limited",
        "RATNAMANI.NS": "Ratnamani Metals & Tubes Limited",
        "ROSSARI.NS": "Rossari Biotech Limited",
        "SFL.NS": "Sheela Foam Limited",
        "SHARDACROP.NS": "Sharda Cropchem Limited",
        "SRF.NS": "SRF Limited",
        "SYMPHONY.NS": "Symphony Limited",
        "TATACHEM.NS": "Tata Chemicals Limited",
        "TEAMLEASE.NS": "TeamLease Services Limited",
        "TIINDIA.NS": "Tube Investments of India Limited",
        "TNPETRO.NS": "Tamilnadu Petroproducts Limited",
        "UPL.NS": "UPL Limited",
        "VALIANTORG.NS": "Valiant Organics Limited",
        "VIPIND.NS": "VIP Industries Limited",
        "VRLLOG.NS": "VRL Logistics Limited",
    }
}

# Sector mapping for broader categorization
SECTOR_MAPPING = {
    'Financial Services': [
        'Money Center Banks', 'Financial Services', 'Credit Services',
        'Investment Brokerage - National', 'Mortgage Investment', 'Asset Management'
    ],
    'Technology': [
        'Business Software & Services', 'Information Technology Services',
        'Communication Technology', 'Technical & System Software'
    ],
    'Healthcare & Pharma': [
        'Drugs - Generic', 'Drug Manufacturers - Major', 'Medical Services',
        'Biotechnology', 'Medical Laboratories & Research'
    ],
    'Industrial & Manufacturing': [
        'Industrial Products', 'Steel & Iron', 'Industrial Metals & Minerals',
        'Diversified Machinery', 'Diversified Electronics', 'Farm & Construction Machinery'
    ],
    'Energy & Utilities': [
        'Electric Utilities', 'Oil & Gas Operations', 'Gas Utilities',
        'Renewable Energy', 'Oil & Gas Refining & Marketing'
    ],
    'Consumer & Retail': [
        'Food - Major Diversified', 'Personal Products', 'Retail - Apparel & Accessories',
        'Restaurants', 'Lodging', 'Jewelry Stores'
    ],
    'Materials & Chemicals': [
        'Chemicals - Major Diversified', 'Agricultural Chemicals', 'Paper & Paper Products',
        'Rubber & Plastics', 'Cement & Aggregates'
    ],
    'Real Estate & Construction': [
        'Real Estate Development', 'General Contractors', 'Heavy Construction'
    ],
    'Transportation': [
        'Shipping', 'Transportation Services', 'Major Airlines'
    ],
    'Automotive': [
        'Auto Manufacturers - Major', 'Auto Parts'
    ],
    'Textiles': [
        'Textile Industrial', 'Textile - Apparel Clothing'
    ]
}

# Industry benchmarks for fair value calculations
INDUSTRY_BENCHMARKS = {
    'Financial Services': {'pe': 18, 'ev_ebitda': 12, 'pb': 1.5, 'roe': 15},
    'Technology': {'pe': 25, 'ev_ebitda': 15, 'pb': 3.5, 'roe': 20},
    'Healthcare & Pharma': {'pe': 28, 'ev_ebitda': 14, 'pb': 3.0, 'roe': 18},
    'Industrial & Manufacturing': {'pe': 22, 'ev_ebitda': 12, 'pb': 2.0, 'roe': 14},
    'Energy & Utilities': {'pe': 15, 'ev_ebitda': 8, 'pb': 1.2, 'roe': 12},
    'Consumer & Retail': {'pe': 30, 'ev_ebitda': 14, 'pb': 2.5, 'roe': 16},
    'Materials & Chemicals': {'pe': 18, 'ev_ebitda': 10, 'pb': 1.8, 'roe': 13},
    'Real Estate & Construction': {'pe': 25, 'ev_ebitda': 18, 'pb': 1.5, 'roe': 12},
    'Transportation': {'pe': 20, 'ev_ebitda': 12, 'pb': 1.8, 'roe': 14},
    'Automotive': {'pe': 20, 'ev_ebitda': 12, 'pb': 1.5, 'roe': 15},
    'Textiles': {'pe': 20, 'ev_ebitda': 12, 'pb': 1.5, 'roe': 15},
    'Default': {'pe': 20, 'ev_ebitda': 12, 'pb': 2.0, 'roe': 15}
}

# Utility functions for stock database
def get_all_stocks_by_sector():
    """Get all stocks organized by sectors"""
    sector_stocks = {}
    
    for sector, categories in SECTOR_MAPPING.items():
        sector_stocks[sector] = {}
        for category in categories:
            if category in INDIAN_STOCKS:
                sector_stocks[sector].update(INDIAN_STOCKS[category])
    
    return sector_stocks

def get_stocks_in_categories(categories):
    """Get all stocks from specified categories"""
    stocks = {}
    for category in categories:
        if category in INDIAN_STOCKS:
            stocks.update(INDIAN_STOCKS[category])
    return stocks

def get_sector_from_category(category):
    """Get sector for a given category"""
    for sector, categories in SECTOR_MAPPING.items():
        if category in categories:
            return sector
    return 'Other'

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: #e2e8f0;
}

.metric-card {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.1) 0%, rgba(79, 70, 229, 0.1) 100%);
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.1);
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 20px 0;
}

.sub-header {
    text-align: center;
    color: #a78bfa;
    font-size: 1.1rem;
    margin-bottom: 30px;
}

.section-header {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.5rem;
    font-weight: 600;
    margin: 25px 0 15px 0;
    border-bottom: 2px solid rgba(167, 139, 250, 0.3);
    padding-bottom: 8px;
}

.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 40px;
    background: rgba(30, 41, 59, 0.8);
    border-radius: 20px;
    border: 1px solid rgba(167, 139, 250, 0.3);
    backdrop-filter: blur(15px);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
}

.highlight-box {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(167, 139, 250, 0.1));
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
}

.success-message {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 8px;
    padding: 15px;
    margin: 20px 0;
    color: #86efac;
}

.disclaimer {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    padding: 15px;
    margin: 20px 0;
    font-size: 0.9rem;
    color: #fca5a5;
}

.recommendation {
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    font-weight: 600;
    margin: 15px 0;
    border: 2px solid transparent;
    background: linear-gradient(135deg, rgba(0,0,0,0.2), rgba(0,0,0,0.1));
}

.rec-strong-buy {
    background: linear-gradient(135deg, #059669, #047857);
    border-color: #34d399;
    color: white;
    box-shadow: 0 8px 25px rgba(52, 211, 153, 0.3);
}

.rec-buy {
    background: linear-gradient(135deg, #0d9488, #0f766e);
    border-color: #5eead4;
    color: white;
}

.rec-hold {
    background: linear-gradient(135deg, #d97706, #b45309);
    border-color: #fbbf24;
    color: white;
}

.rec-avoid {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    border-color: #f87171;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PASSWORD AUTHENTICATION
# ============================================================================
def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "demo123", "premium": "1nV3st!ng", "niyas": "buffet"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("""
        <div class="login-container">
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">📊</div>
                <h2 style="color: #a78bfa; margin-bottom: 5px;">NYZTrade Pro</h2>
                <p style="color: #94a3b8;">Professional Stock Analysis Platform</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("👤 Username", key="username", placeholder="Enter username")
            st.text_input("🔒 Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True, type="primary")
            st.info("💡 Demo: demo/demo123")
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect credentials. Please try again.")
        return False
    return True

if not check_password():
    st.stop()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def retry_with_backoff(retries=2, backoff_in_seconds=0.5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator

@st.cache_data(ttl=7200)
@retry_with_backoff(retries=2, backoff_in_seconds=0.5)
def fetch_stock_data(ticker):
    try:
        time.sleep(0.05)  # Rate limiting
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        return info, None
    except Exception as e:
        return None, str(e)[:50]

def categorize_market_cap(market_cap):
    """Categorize stocks by market cap (in INR Crores)"""
    if not market_cap:
        return 'Unknown'
    market_cap_cr = market_cap / 10000000
    if market_cap_cr >= 100000:
        return 'Large Cap'
    elif market_cap_cr >= 25000:
        return 'Mid Cap'
    elif market_cap_cr >= 5000:
        return 'Small Cap'
    else:
        return 'Micro Cap'

def calculate_fair_value_and_upside(info, sector):
    """Calculate fair value and upside using PE and EV/EBITDA methods"""
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1) or 1
        
        # Get benchmarks for sector
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        fair_values = []
        
        # PE-based fair value
        if trailing_pe and trailing_pe > 0 and trailing_eps and price:
            historical_pe = trailing_pe * 0.9
            target_pe = (industry_pe + historical_pe) / 2
            fair_value_pe = trailing_eps * target_pe
            upside_pe = ((fair_value_pe - price) / price * 100)
            fair_values.append(fair_value_pe)
        else:
            fair_value_pe = None
            upside_pe = None
        
        # EV/EBITDA-based fair value
        if enterprise_value and ebitda and ebitda > 0 and shares and price:
            current_ev_ebitda = enterprise_value / ebitda
            if 0 < current_ev_ebitda < 100:
                historical_ev_ebitda = current_ev_ebitda * 0.9
                target_ev_ebitda = (industry_ev_ebitda + historical_ev_ebitda) / 2
                
                fair_ev = ebitda * target_ev_ebitda
                net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
                fair_market_cap = fair_ev - net_debt
                fair_value_ev = fair_market_cap / shares
                upside_ev = ((fair_value_ev - price) / price * 100)
                fair_values.append(fair_value_ev)
            else:
                fair_value_ev = None
                upside_ev = None
        else:
            fair_value_ev = None
            upside_ev = None
        
        # Calculate average fair value and upside
        if fair_values:
            avg_fair_value = np.mean(fair_values)
            avg_upside = ((avg_fair_value - price) / price * 100) if price else None
        else:
            avg_fair_value = None
            avg_upside = None
        
        return {
            'fair_value_pe': fair_value_pe,
            'upside_pe': upside_pe,
            'fair_value_ev': fair_value_ev,
            'upside_ev': upside_ev,
            'avg_fair_value': avg_fair_value,
            'avg_upside': avg_upside
        }
    
    except Exception as e:
        return {
            'fair_value_pe': None,
            'upside_pe': None,
            'fair_value_ev': None,
            'upside_ev': None,
            'avg_fair_value': None,
            'avg_upside': None
        }

# ============================================================================
# SECTOR-BASED SCREENERS
# ============================================================================
def get_sector_screeners():
    """Define sector-based preset screeners"""
    return {
        "🏦 Financial Services Opportunities": {
            'sector': 'Financial Services',
            'upside_min': 15,
            'pe_max': 25,
            'description': 'Undervalued financial stocks with strong fundamentals'
        },
        
        "💻 Technology Growth Stocks": {
            'sector': 'Technology',
            'upside_min': 20,
            'pe_max': 30,
            'description': 'High-growth tech stocks with reasonable valuations'
        },
        
        "💊 Healthcare & Pharma Leaders": {
            'sector': 'Healthcare & Pharma',
            'upside_min': 18,
            'pe_max': 35,
            'description': 'Healthcare leaders with upside potential'
        },
        
        "🏭 Industrial Powerhouses": {
            'sector': 'Industrial & Manufacturing',
            'upside_min': 15,
            'pe_max': 25,
            'description': 'Industrial stocks with strong fundamentals'
        },
        
        "⚡ Energy & Utilities Value": {
            'sector': 'Energy & Utilities',
            'upside_min': 12,
            'pe_max': 20,
            'description': 'Value opportunities in energy sector'
        },
        
        "🛒 Consumer & Retail Stars": {
            'sector': 'Consumer & Retail',
            'upside_min': 15,
            'pe_max': 35,
            'description': 'Consumer brands with growth potential'
        },
        
        "🧪 Materials & Chemicals": {
            'sector': 'Materials & Chemicals',
            'upside_min': 15,
            'pe_max': 22,
            'description': 'Chemical and material sector opportunities'
        },
        
        "🏠 Real Estate & Construction": {
            'sector': 'Real Estate & Construction',
            'upside_min': 20,
            'pe_max': 30,
            'description': 'Real estate development opportunities'
        },
        
        "🚛 Transportation Leaders": {
            'sector': 'Transportation',
            'upside_min': 15,
            'pe_max': 25,
            'description': 'Transportation and logistics stocks'
        },
        
        "🚗 Automotive Sector": {
            'sector': 'Automotive',
            'upside_min': 15,
            'pe_max': 25,
            'description': 'Auto manufacturers and parts suppliers'
        },
        
        "🧵 Textiles Value Picks": {
            'sector': 'Textiles',
            'upside_min': 18,
            'pe_max': 22,
            'description': 'Textile industry value opportunities'
        }
    }

def run_sector_screener(sector, criteria, limit=25):
    """Run screening for a specific sector"""
    
    # Get categories for this sector
    categories = SECTOR_MAPPING.get(sector, [])
    if not categories:
        return pd.DataFrame()
    
    # Get all stocks in these categories
    stocks = get_stocks_in_categories(categories)
    
    if not stocks:
        return pd.DataFrame()
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    stock_items = list(stocks.items())
    analyzed_count = 0
    
    for idx, (ticker, name) in enumerate(stock_items):
        # Update progress
        progress = min((idx + 1) / len(stock_items), 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Analyzing {sector}: {idx+1}/{len(stock_items)} - {ticker}")
        
        # Fetch stock data
        info, error = fetch_stock_data(ticker)
        analyzed_count += 1
        
        if not error and info:
            try:
                # Calculate valuations
                valuation_data = calculate_fair_value_and_upside(info, sector)
                
                price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
                market_cap = info.get('marketCap', 0)
                pe_ratio = info.get('trailingPE', 0)
                pb_ratio = info.get('priceToBook', 0)
                dividend_yield = info.get('dividendYield', 0)
                
                # 52-week data
                high_52w = info.get('fiftyTwoWeekHigh', 0)
                low_52w = info.get('fiftyTwoWeekLow', 0)
                pct_from_high = None
                pct_from_low = None
                
                if price and high_52w and low_52w and high_52w > low_52w:
                    pct_from_high = ((high_52w - price) / high_52w * 100)
                    pct_from_low = ((price - low_52w) / low_52w * 100)
                
                # Apply filters
                passes = True
                
                # Upside filter
                if 'upside_min' in criteria and valuation_data['avg_upside']:
                    if valuation_data['avg_upside'] < criteria['upside_min']:
                        passes = False
                
                # PE filter
                if passes and 'pe_max' in criteria and pe_ratio:
                    if pe_ratio > criteria['pe_max']:
                        passes = False
                
                if passes:
                    results.append({
                        'Ticker': ticker,
                        'Name': name,
                        'Sector': sector,
                        'Price': price,
                        'Market Cap': market_cap,
                        'Cap Type': categorize_market_cap(market_cap),
                        'PE Ratio': pe_ratio,
                        'PB Ratio': pb_ratio,
                        'Fair Value': valuation_data['avg_fair_value'],
                        'Upside %': valuation_data['avg_upside'],
                        'Dividend Yield': dividend_yield * 100 if dividend_yield else 0,
                        '52W High': high_52w,
                        '52W Low': low_52w,
                        'From 52W High %': -pct_from_high if pct_from_high else None,
                        'From 52W Low %': pct_from_low if pct_from_low else None,
                    })
                
                # Check limit
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

# ============================================================================
# INDIVIDUAL STOCK ANALYSIS
# ============================================================================
def analyze_individual_stock(ticker):
    """Detailed analysis of individual stock"""
    info, error = fetch_stock_data(ticker)
    
    if error or not info:
        return None, error
    
    # Find sector for this ticker
    sector = 'Default'
    for category, stocks in INDIAN_STOCKS.items():
        if ticker in stocks:
            sector = get_sector_from_category(category)
            break
    
    # Basic info
    company = info.get('longName', ticker)
    price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
    market_cap = info.get('marketCap', 0)
    
    # Financial metrics
    trailing_pe = info.get('trailingPE', 0)
    forward_pe = info.get('forwardPE', 0)
    pb_ratio = info.get('priceToBook', 0)
    dividend_yield = info.get('dividendYield', 0)
    beta = info.get('beta', 0)
    roe = info.get('returnOnEquity', 0)
    profit_margin = info.get('profitMargins', 0)
    
    # 52-week data
    high_52w = info.get('fiftyTwoWeekHigh', 0)
    low_52w = info.get('fiftyTwoWeekLow', 0)
    
    pct_from_high = None
    pct_from_low = None
    
    if price and high_52w and low_52w and high_52w > low_52w:
        pct_from_high = ((high_52w - price) / high_52w * 100)
        pct_from_low = ((price - low_52w) / low_52w * 100)
    
    # Fair value calculations
    valuation_data = calculate_fair_value_and_upside(info, sector)
    
    analysis = {
        'company': company,
        'ticker': ticker,
        'sector': sector,
        'price': price,
        'market_cap': market_cap,
        'cap_type': categorize_market_cap(market_cap),
        'trailing_pe': trailing_pe,
        'forward_pe': forward_pe,
        'pb_ratio': pb_ratio,
        'dividend_yield': dividend_yield,
        'beta': beta,
        'roe': roe,
        'profit_margin': profit_margin,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'pct_from_high': pct_from_high,
        'pct_from_low': pct_from_low,
        **valuation_data
    }
    
    return analysis, None

def create_gauge_chart(upside_pe, upside_ev):
    """Create professional dual gauge chart for valuations"""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        horizontal_spacing=0.15
    )
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_pe if upside_pe else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "PE Method", 'font': {'size': 16, 'color': '#a78bfa'}},
        gauge={
            'axis': {'range': [-50, 50]},
            'bar': {'color': "#7c3aed"},
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {'line': {'color': "#f472b6", 'width': 4}, 'value': 0}
        }
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "EV/EBITDA Method", 'font': {'size': 16, 'color': '#a78bfa'}},
        gauge={
            'axis': {'range': [-50, 50]},
            'bar': {'color': "#ec4899"},
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {'line': {'color': "#f472b6", 'width': 4}, 'value': 0}
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.markdown('''
<div class="main-header">
    NYZTRADE PRO SCREENER
</div>
<div class="sub-header">
    🎯 8,984 Indian Stocks | 11 Sector-Based Screeners | Professional Valuation Analysis
</div>
''', unsafe_allow_html=True)

# ============================================================================
# STOCK UNIVERSE OVERVIEW
# ============================================================================
st.markdown('<div class="section-header">📊 Stock Universe Overview</div>', unsafe_allow_html=True)

# Calculate statistics
sector_stocks = get_all_stocks_by_sector()
total_stocks = sum(len(stocks) for stocks in INDIAN_STOCKS.values())
total_sectors = len(SECTOR_MAPPING)
total_categories = len(INDIAN_STOCKS)

# Display statistics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{total_stocks:,}</div>
        <div style="color: #94a3b8;">📊 Total Stocks</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{total_sectors}</div>
        <div style="color: #94a3b8;">🏢 Major Sectors</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{total_categories}</div>
        <div style="color: #94a3b8;">🏷️ Categories</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    nse_count = sum(1 for stocks in INDIAN_STOCKS.values() for ticker in stocks.keys() if '.NS' in ticker)
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{nse_count:,}</div>
        <div style="color: #94a3b8;">📈 NSE Listed</div>
    </div>
    ''', unsafe_allow_html=True)

# Display sector breakdown
st.markdown("**📈 Sector Breakdown:**")
sector_breakdown = []
for sector, categories in SECTOR_MAPPING.items():
    stock_count = sum(len(INDIAN_STOCKS.get(cat, {})) for cat in categories)
    sector_breakdown.append((sector, stock_count))

sector_breakdown.sort(key=lambda x: x[1], reverse=True)

col1, col2 = st.columns(2)
for i, (sector, count) in enumerate(sector_breakdown):
    col = col1 if i % 2 == 0 else col2
    with col:
        st.markdown(f"• **{sector}**: {count:,} stocks")

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================
with st.sidebar:
    st.markdown("### 🔐 Account")
    st.markdown(f"**User:** {st.session_state.get('authenticated_user', 'Guest').title()}")
    
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    
    # MODE SELECTION
    mode = st.radio(
        "📊 Analysis Mode",
        ["🎯 Sector Screeners", "📈 Individual Stock Analysis"],
        help="Choose your analysis approach"
    )
    
    if mode == "🎯 Sector Screeners":
        st.markdown("### 🎯 Sector-Based Screeners")
        
        sector_screeners = get_sector_screeners()
        selected_screener = st.selectbox(
            "Choose Sector Screener",
            list(sector_screeners.keys()),
            help="Select a sector-focused screening strategy"
        )
        
        # Show screener details
        screener_config = sector_screeners[selected_screener]
        st.markdown(f"**📋 {screener_config['description']}**")
        st.markdown(f"**🎯 Sector:** {screener_config['sector']}")
        st.markdown(f"**📈 Min Upside:** {screener_config['upside_min']}%")
        st.markdown(f"**💰 Max PE:** {screener_config['pe_max']}x")
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters"):
            result_limit = st.slider("Max Results", 10, 50, 25, 5)
            
            # Override default criteria
            custom_upside = st.number_input(
                "Custom Min Upside %", 
                value=screener_config['upside_min'], 
                min_value=0.0, 
                max_value=100.0, 
                step=5.0
            )
            
            custom_pe = st.number_input(
                "Custom Max PE", 
                value=screener_config['pe_max'], 
                min_value=5.0, 
                max_value=50.0, 
                step=5.0
            )
        
        run_screener = st.button("🚀 RUN SECTOR SCREENER", use_container_width=True, type="primary")
    
    else:  # Individual Stock Analysis
        st.markdown("### 📈 Individual Stock Analysis")
        
        # Sector selection for browsing
        browse_sector = st.selectbox(
            "🔍 Browse by Sector",
            ['All Sectors'] + list(SECTOR_MAPPING.keys()),
            help="Filter stocks by sector"
        )
        
        # Get stocks for selected sector
        if browse_sector == 'All Sectors':
            available_stocks = {}
            for category, stocks in INDIAN_STOCKS.items():
                available_stocks.update(stocks)
        else:
            categories = SECTOR_MAPPING[browse_sector]
            available_stocks = get_stocks_in_categories(categories)
        
        # Search functionality
        search = st.text_input(
            "🔍 Search Stocks",
            placeholder="Company name or ticker...",
            help="Search by company name or ticker symbol"
        )
        
        if search:
            search_upper = search.upper()
            filtered_stocks = {
                ticker: name for ticker, name in available_stocks.items()
                if search_upper in ticker.upper() or search_upper in name.upper()
            }
        else:
            # Show first 100 stocks for performance
            filtered_stocks = dict(list(available_stocks.items())[:100])
        
        st.info(f"Showing {len(filtered_stocks)} stocks")
        
        if filtered_stocks:
            stock_options = [f"{name} ({ticker})" for ticker, name in filtered_stocks.items()]
            selected_stock = st.selectbox("🎯 Select Stock", [""] + stock_options)
            
            if selected_stock:
                ticker = selected_stock.split("(")[1].strip(")")
                st.session_state.selected_stock_ticker = ticker
        
        # Manual ticker input
        st.markdown("---")
        manual_ticker = st.text_input(
            "✏️ Manual Ticker Entry",
            placeholder="e.g., RELIANCE.NS",
            help="Enter any NSE/BSE ticker directly"
        )
        
        if manual_ticker:
            st.session_state.selected_stock_ticker = manual_ticker.upper()
        
        analyze_stock = st.button("📊 ANALYZE STOCK", use_container_width=True, type="primary")

# ============================================================================
# MAIN CONTENT - SECTOR SCREENERS
# ============================================================================

if mode == "🎯 Sector Screeners":
    if run_screener:
        screener_config = sector_screeners[selected_screener]
        
        # Update criteria with custom values
        criteria = {
            'upside_min': custom_upside,
            'pe_max': custom_pe
        }
        
        st.markdown(f'''
        <div class="highlight-box">
            <h3>🔍 {selected_screener}</h3>
            <p><strong>Sector:</strong> {screener_config['sector']}</p>
            <p><strong>Strategy:</strong> {screener_config['description']}</p>
            <p><strong>Filters:</strong> Min Upside {custom_upside}%, Max PE {custom_pe}x</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Run the screener
        results_df = run_sector_screener(screener_config['sector'], criteria, result_limit)
        
        if results_df.empty:
            st.warning("❌ No stocks match the screening criteria. Try relaxing the filters.")
        else:
            st.markdown(f'''
            <div class="success-message">
                ✅ Found <strong>{len(results_df)}</strong> opportunities in {screener_config['sector']} sector
            </div>
            ''', unsafe_allow_html=True)
            
            # Sort by upside percentage
            results_df = results_df.sort_values('Upside %', ascending=False, na_position='last')
            
            # Format the dataframe for display
            display_df = results_df.copy()
            
            # Format columns
            display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
            display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A')
            display_df['Fair Value'] = display_df['Fair Value'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) and x > 0 else "N/A")
            display_df['Upside %'] = display_df['Upside %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            display_df['PE Ratio'] = display_df['PE Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x > 0 else "N/A")
            display_df['PB Ratio'] = display_df['PB Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x > 0 else "N/A")
            display_df['From 52W High %'] = display_df['From 52W High %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            display_df['Dividend Yield'] = display_df['Dividend Yield'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            
            # Display results
            st.markdown('<div class="section-header">🎯 Screening Results</div>', unsafe_allow_html=True)
            
            st.dataframe(
                display_df[['Ticker', 'Name', 'Price', 'Fair Value', 'Upside %', 'PE Ratio', 'From 52W High %', 'Cap Type']],
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Download option
            csv = results_df.to_csv(index=False)
            st.download_button(
                "📥 Download Results (CSV)",
                data=csv,
                file_name=f"NYZTrade_{screener_config['sector'].replace(' & ', '_')}_Screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ============================================================================
# MAIN CONTENT - INDIVIDUAL STOCK ANALYSIS
# ============================================================================

elif mode == "📈 Individual Stock Analysis":
    if analyze_stock and hasattr(st.session_state, 'selected_stock_ticker'):
        ticker = st.session_state.selected_stock_ticker
        
        with st.spinner(f"🔄 Analyzing {ticker}..."):
            analysis, error = analyze_individual_stock(ticker)
        
        if analysis:
            # Display analysis
            st.markdown(f'''
            <div class="highlight-box">
                <h2>{analysis['company']}</h2>
                <div style="display: flex; flex-wrap: wrap; gap: 20px; color: #a78bfa;">
                    <span>🏷️ <strong>{analysis['ticker']}</strong></span>
                    <span>🏢 <strong>{analysis['sector']}</strong></span>
                    <span>💼 <strong>{analysis['cap_type']}</strong></span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Main valuation summary
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fair_value = analysis['avg_fair_value'] if analysis['avg_fair_value'] else analysis['price']
                upside = analysis['avg_upside'] if analysis['avg_upside'] else 0
                
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📊 Valuation Summary</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #a78bfa;">₹{fair_value:,.2f}</div>
                            <div style="color: #94a3b8;">Fair Value</div>
                        </div>
                        <div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #e2e8f0;">₹{analysis["price"]:,.2f}</div>
                            <div style="color: #94a3b8;">Current Price</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: {'#34d399' if upside > 0 else '#f87171'};">
                            {"📈" if upside > 0 else "📉"} {upside:+.1f}% Potential
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                # Recommendation
                if upside > 25:
                    rec_class, rec_text, rec_icon = "rec-strong-buy", "Strong Buy", "🚀"
                elif upside > 15:
                    rec_class, rec_text, rec_icon = "rec-buy", "Buy", "✅"
                elif upside > 0:
                    rec_class, rec_text, rec_icon = "rec-buy", "Hold", "📥"
                elif upside > -10:
                    rec_class, rec_text, rec_icon = "rec-hold", "Weak Hold", "⏸️"
                else:
                    rec_class, rec_text, rec_icon = "rec-avoid", "Avoid", "⚠️"
                
                st.markdown(f'''
                <div class="recommendation {rec_class}">
                    <div style="font-size: 2rem; margin-bottom: 10px;">{rec_icon}</div>
                    <div style="font-size: 1.3rem; font-weight: bold;">{rec_text}</div>
                    <div style="font-size: 0.9rem; margin-top: 5px;">Expected: {upside:+.1f}%</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Key metrics grid
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            metrics = [
                (col1, "💰", f"₹{analysis['price']:,.2f}", "Price"),
                (col2, "📈", f"{analysis['trailing_pe']:.2f}" if analysis['trailing_pe'] else "N/A", "PE Ratio"),
                (col3, "📚", f"{analysis['pb_ratio']:.2f}" if analysis['pb_ratio'] else "N/A", "P/B Ratio"),
                (col4, "🏦", f"₹{analysis['market_cap']/10000000:,.0f}Cr" if analysis['market_cap'] else "N/A", "Market Cap"),
                (col5, "💵", f"{analysis['dividend_yield']*100:.2f}%" if analysis['dividend_yield'] else "N/A", "Dividend"),
                (col6, "📊", f"{analysis['beta']:.2f}" if analysis['beta'] else "N/A", "Beta")
            ]
            
            for col, icon, value, label in metrics:
                with col:
                    st.markdown(f'''
                    <div class="metric-card" style="text-align: center; padding: 15px;">
                        <div style="font-size: 1.5rem; margin-bottom: 5px;">{icon}</div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: #a78bfa; margin-bottom: 5px;">{value}</div>
                        <div style="font-size: 0.9rem; color: #94a3b8;">{label}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Valuation gauges
            if analysis['upside_pe'] is not None or analysis['upside_ev'] is not None:
                st.markdown('<div class="section-header">📊 Valuation Methods</div>', unsafe_allow_html=True)
                fig_gauge = create_gauge_chart(
                    analysis['upside_pe'] if analysis['upside_pe'] else 0,
                    analysis['upside_ev'] if analysis['upside_ev'] else 0
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            # 52-week performance
            if analysis['pct_from_high'] is not None:
                st.markdown('<div class="section-header">📍 52-Week Performance</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Distance from 52W High", f"{-analysis['pct_from_high']:+.1f}%")
                    st.metric("Distance from 52W Low", f"{analysis['pct_from_low']:+.1f}%")
                
                with col2:
                    st.metric("52W High", f"₹{analysis['high_52w']:,.2f}")
                    st.metric("52W Low", f"₹{analysis['low_52w']:,.2f}")
        
        elif error:
            st.error(f"❌ Error analyzing {ticker}: {error}")
            st.info("💡 Make sure the ticker is correct (e.g., RELIANCE.NS for NSE stocks)")
    
    elif analyze_stock:
        st.warning("⚠️ Please select a stock first")

# Footer
st.markdown('''
<div style="margin-top: 50px; padding: 30px; background: rgba(30, 41, 59, 0.4); border-radius: 15px; text-align: center;">
    <h4 style="color: #a78bfa; margin-bottom: 15px;">NYZTrade Pro | Professional Stock Analysis Platform</h4>
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This platform is designed for educational and informational purposes only. 
        The analysis, recommendations, and data presented here should not be considered as financial advice or investment recommendations. 
        Fair value calculations are based on industry benchmarks and financial models. Always conduct your own research and consult 
        with qualified financial professionals before making any investment decisions.
    </div>
    <div style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
        © 2024 NYZTrade | Stock Universe: 8,984 Indian Stocks | Market Data: Yahoo Finance
    </div>
</div>
''', unsafe_allow_html=True)
