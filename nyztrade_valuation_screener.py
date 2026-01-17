import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import time
from functools import wraps
from io import BytesIO
import statistics

st.set_page_config(
    page_title="NYZTrade Dynamic Screener", 
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

# Default/Fallback benchmarks (used if dynamic calculation fails)
DEFAULT_BENCHMARKS = {
    'Financial Services': {'pe': 18.0, 'ev_ebitda': 12.0, 'pb': 1.5, 'roe': 15.0},
    'Technology': {'pe': 25.0, 'ev_ebitda': 15.0, 'pb': 3.5, 'roe': 20.0},
    'Healthcare & Pharma': {'pe': 28.0, 'ev_ebitda': 14.0, 'pb': 3.0, 'roe': 18.0},
    'Industrial & Manufacturing': {'pe': 22.0, 'ev_ebitda': 12.0, 'pb': 2.0, 'roe': 14.0},
    'Energy & Utilities': {'pe': 15.0, 'ev_ebitda': 8.0, 'pb': 1.2, 'roe': 12.0},
    'Consumer & Retail': {'pe': 30.0, 'ev_ebitda': 14.0, 'pb': 2.5, 'roe': 16.0},
    'Materials & Chemicals': {'pe': 18.0, 'ev_ebitda': 10.0, 'pb': 1.8, 'roe': 13.0},
    'Real Estate & Construction': {'pe': 25.0, 'ev_ebitda': 18.0, 'pb': 1.5, 'roe': 12.0},
    'Transportation': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 1.8, 'roe': 14.0},
    'Automotive': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 1.5, 'roe': 15.0},
    'Textiles': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 1.5, 'roe': 15.0},
    'Default': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 2.0, 'roe': 15.0}
}

# ============================================================================
# DYNAMIC BENCHMARK CALCULATION
# ============================================================================

@st.cache_data(ttl=21600)  # Cache for 6 hours
def calculate_dynamic_sector_benchmarks(sector, sample_size=30, progress_callback=None):
    """
    Calculate dynamic sector benchmarks by analyzing actual sector data
    Excludes outliers using IQR method for more accurate averages
    """
    
    try:
        # Get categories for this sector
        categories = SECTOR_MAPPING.get(sector, [])
        if not categories:
            return DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])
        
        # Get all stocks in these categories
        stocks = get_stocks_in_categories(categories)
        
        if not stocks:
            return DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])
        
        # Take a representative sample for benchmark calculation
        stock_items = list(stocks.items())
        if len(stock_items) > sample_size:
            # Take evenly distributed sample
            step = len(stock_items) // sample_size
            stock_items = stock_items[::step][:sample_size]
        
        # Collect metrics
        pe_ratios = []
        pb_ratios = []
        ev_ebitda_ratios = []
        roe_values = []
        
        for i, (ticker, name) in enumerate(stock_items):
            if progress_callback:
                progress_callback(f"Analyzing {sector} benchmarks: {i+1}/{len(stock_items)}", i/len(stock_items))
            
            # Fetch stock data
            info, error = fetch_stock_data(ticker)
            
            if not error and info:
                try:
                    # Collect PE ratios
                    pe = info.get('trailingPE', 0)
                    if pe and 0 < pe < 200:  # Reasonable PE range
                        pe_ratios.append(pe)
                    
                    # Collect PB ratios
                    pb = info.get('priceToBook', 0)
                    if pb and 0 < pb < 20:  # Reasonable PB range
                        pb_ratios.append(pb)
                    
                    # Collect EV/EBITDA ratios
                    enterprise_value = info.get('enterpriseValue', 0)
                    ebitda = info.get('ebitda', 0)
                    if enterprise_value and ebitda and ebitda > 0:
                        ev_ebitda = enterprise_value / ebitda
                        if 0 < ev_ebitda < 100:  # Reasonable EV/EBITDA range
                            ev_ebitda_ratios.append(ev_ebitda)
                    
                    # Collect ROE values
                    roe = info.get('returnOnEquity', 0)
                    if roe and -50 < roe < 100:  # Reasonable ROE range (-50% to 100%)
                        roe_values.append(roe * 100)  # Convert to percentage
                
                except:
                    continue
        
        # Calculate benchmarks excluding outliers
        benchmarks = {}
        
        # PE benchmark
        if len(pe_ratios) >= 5:
            pe_clean = remove_outliers(pe_ratios)
            benchmarks['pe'] = float(np.mean(pe_clean)) if pe_clean else DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['pe']
        else:
            benchmarks['pe'] = DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['pe']
        
        # PB benchmark
        if len(pb_ratios) >= 5:
            pb_clean = remove_outliers(pb_ratios)
            benchmarks['pb'] = float(np.mean(pb_clean)) if pb_clean else DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['pb']
        else:
            benchmarks['pb'] = DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['pb']
        
        # EV/EBITDA benchmark
        if len(ev_ebitda_ratios) >= 5:
            ev_ebitda_clean = remove_outliers(ev_ebitda_ratios)
            benchmarks['ev_ebitda'] = float(np.mean(ev_ebitda_clean)) if ev_ebitda_clean else DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['ev_ebitda']
        else:
            benchmarks['ev_ebitda'] = DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['ev_ebitda']
        
        # ROE benchmark
        if len(roe_values) >= 5:
            roe_clean = remove_outliers(roe_values)
            benchmarks['roe'] = float(np.mean(roe_clean)) if roe_clean else DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['roe']
        else:
            benchmarks['roe'] = DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])['roe']
        
        return benchmarks
        
    except Exception as e:
        # Fallback to default benchmarks on any error
        return DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])

def remove_outliers(data, method='iqr'):
    """
    Remove outliers from data using IQR method
    IQR method is more robust than z-score for financial data
    """
    if len(data) < 4:
        return data
    
    data = np.array(data)
    
    if method == 'iqr':
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Filter out outliers
        cleaned_data = data[(data >= lower_bound) & (data <= upper_bound)]
        
    elif method == 'zscore':
        # Z-score method (alternative)
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        cleaned_data = data[z_scores < 3]
    
    else:
        cleaned_data = data
    
    return cleaned_data.tolist() if len(cleaned_data) > 0 else data.tolist()

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

def get_sector_stock_count(sector):
    """Get total number of stocks in a sector"""
    categories = SECTOR_MAPPING.get(sector, [])
    total_stocks = 0
    for category in categories:
        if category in INDIAN_STOCKS:
            total_stocks += len(INDIAN_STOCKS[category])
    return total_stocks

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

.benchmark-box {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    color: #93c5fd;
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
                <h2 style="color: #a78bfa; margin-bottom: 5px;">NYZTrade Dynamic</h2>
                <p style="color: #94a3b8;">AI-Powered Dynamic Benchmark Analysis</p>
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

def calculate_fair_value_and_upside(info, sector, dynamic_benchmarks=None):
    """Calculate fair value and upside using dynamic or default benchmarks"""
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1) or 1
        
        # Get benchmarks (dynamic if available, else default)
        if dynamic_benchmarks:
            benchmark = dynamic_benchmarks
        else:
            benchmark = DEFAULT_BENCHMARKS.get(sector, DEFAULT_BENCHMARKS['Default'])
        
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        fair_values = []
        
        # PE-based fair value with dynamic benchmark
        if trailing_pe and trailing_pe > 0 and trailing_eps and price:
            # Use more sophisticated approach: blend industry average with historical performance
            historical_pe = trailing_pe * 0.85  # 15% discount to current PE for conservatism
            target_pe = (industry_pe * 0.7 + historical_pe * 0.3)  # Weight industry average more heavily
            fair_value_pe = trailing_eps * target_pe
            upside_pe = ((fair_value_pe - price) / price * 100)
            fair_values.append(fair_value_pe)
        else:
            fair_value_pe = None
            upside_pe = None
        
        # EV/EBITDA-based fair value with dynamic benchmark
        if enterprise_value and ebitda and ebitda > 0 and shares and price:
            current_ev_ebitda = enterprise_value / ebitda
            if 0 < current_ev_ebitda < 100:
                # Use dynamic approach
                historical_ev_ebitda = current_ev_ebitda * 0.85
                target_ev_ebitda = (industry_ev_ebitda * 0.7 + historical_ev_ebitda * 0.3)
                
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
            'avg_upside': avg_upside,
            'benchmark_pe': industry_pe,
            'benchmark_ev_ebitda': industry_ev_ebitda
        }
    
    except Exception as e:
        return {
            'fair_value_pe': None,
            'upside_pe': None,
            'fair_value_ev': None,
            'upside_ev': None,
            'avg_fair_value': None,
            'avg_upside': None,
            'benchmark_pe': None,
            'benchmark_ev_ebitda': None
        }

# ============================================================================
# SECTOR-BASED SCREENERS WITH DYNAMIC BENCHMARKS
# ============================================================================
def get_sector_screeners():
    """Define sector-based preset screeners with dynamic benchmark awareness"""
    return {
        "🏦 Financial Services Opportunities": {
            'sector': 'Financial Services',
            'upside_min': 15.0,
            'pe_max_multiplier': 1.3,  # 30% above sector average
            'description': 'Undervalued financial stocks with PE below 1.3x sector average'
        },
        
        "💻 Technology Growth Stocks": {
            'sector': 'Technology',
            'upside_min': 20.0,
            'pe_max_multiplier': 1.2,
            'description': 'High-growth tech stocks with PE below 1.2x sector average'
        },
        
        "💊 Healthcare & Pharma Leaders": {
            'sector': 'Healthcare & Pharma',
            'upside_min': 18.0,
            'pe_max_multiplier': 1.25,
            'description': 'Healthcare leaders with PE below 1.25x sector average'
        },
        
        "🏭 Industrial Powerhouses": {
            'sector': 'Industrial & Manufacturing',
            'upside_min': 15.0,
            'pe_max_multiplier': 1.2,
            'description': 'Industrial stocks with PE below 1.2x sector average'
        },
        
        "⚡ Energy & Utilities Value": {
            'sector': 'Energy & Utilities',
            'upside_min': 12.0,
            'pe_max_multiplier': 1.4,
            'description': 'Value opportunities with PE below 1.4x sector average'
        },
        
        "🛒 Consumer & Retail Stars": {
            'sector': 'Consumer & Retail',
            'upside_min': 15.0,
            'pe_max_multiplier': 1.1,
            'description': 'Consumer brands with PE below 1.1x sector average'
        },
        
        "🧪 Materials & Chemicals": {
            'sector': 'Materials & Chemicals',
            'upside_min': 15.0,
            'pe_max_multiplier': 1.3,
            'description': 'Chemical sector with PE below 1.3x sector average'
        },
        
        "🏠 Real Estate & Construction": {
            'sector': 'Real Estate & Construction',
            'upside_min': 20.0,
            'pe_max_multiplier': 1.2,
            'description': 'Real estate with PE below 1.2x sector average'
        },
        
        "🚛 Transportation Leaders": {
            'sector': 'Transportation',
            'upside_min': 15.0,
            'pe_max_multiplier': 1.3,
            'description': 'Transportation with PE below 1.3x sector average'
        },
        
        "🚗 Automotive Sector": {
            'sector': 'Automotive',
            'upside_min': 15.0,
            'pe_max_multiplier': 1.2,
            'description': 'Auto sector with PE below 1.2x sector average'
        },
        
        "🧵 Textiles Value Picks": {
            'sector': 'Textiles',
            'upside_min': 18.0,
            'pe_max_multiplier': 1.1,
            'description': 'Textile sector with PE below 1.1x sector average'
        }
    }

def run_dynamic_sector_screener(sector, criteria, limit=25, use_dynamic_benchmarks=True):
    """Run screening with dynamic benchmarks"""
    
    # Get categories for this sector
    categories = SECTOR_MAPPING.get(sector, [])
    if not categories:
        return pd.DataFrame(), None
    
    # Get all stocks in these categories
    stocks = get_stocks_in_categories(categories)
    
    if not stocks:
        return pd.DataFrame(), None
    
    # Calculate dynamic benchmarks if requested
    benchmarks = None
    if use_dynamic_benchmarks:
        benchmark_progress = st.progress(0)
        benchmark_status = st.empty()
        
        def benchmark_callback(message, progress):
            benchmark_status.text(message)
            benchmark_progress.progress(progress)
        
        benchmark_status.text(f"🧮 Calculating dynamic benchmarks for {sector}...")
        benchmarks = calculate_dynamic_sector_benchmarks(sector, sample_size=30, progress_callback=benchmark_callback)
        
        benchmark_progress.empty()
        benchmark_status.empty()
        
        # Display calculated benchmarks
        if benchmarks:
            st.markdown(f'''
            <div class="benchmark-box">
                <h4>📊 Dynamic Sector Benchmarks for {sector}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 15px; margin: 10px 0;">
                    <div><strong>Average PE:</strong> {benchmarks.get('pe', 0):.2f}x</div>
                    <div><strong>Average PB:</strong> {benchmarks.get('pb', 0):.2f}x</div>
                    <div><strong>Average EV/EBITDA:</strong> {benchmarks.get('ev_ebitda', 0):.2f}x</div>
                    <div><strong>Average ROE:</strong> {benchmarks.get('roe', 0):.1f}%</div>
                </div>
                <p style="font-size: 0.9rem; margin-top: 10px;">
                    ✨ These benchmarks are calculated from real sector data, excluding outliers
                </p>
            </div>
            ''', unsafe_allow_html=True)
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    stock_items = list(stocks.items())
    
    # Calculate dynamic PE limit if using multiplier
    pe_limit = None
    if 'pe_max_multiplier' in criteria and benchmarks:
        pe_limit = benchmarks['pe'] * criteria['pe_max_multiplier']
        st.info(f"📊 Dynamic PE filter: {pe_limit:.2f}x ({criteria['pe_max_multiplier']:.1f}x sector average of {benchmarks['pe']:.2f}x)")
    elif 'pe_max' in criteria:
        pe_limit = criteria['pe_max']
    
    for idx, (ticker, name) in enumerate(stock_items):
        # Update progress
        progress = min((idx + 1) / len(stock_items), 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Screening {sector}: {idx+1}/{len(stock_items)} - {ticker}")
        
        # Fetch stock data
        info, error = fetch_stock_data(ticker)
        
        if not error and info:
            try:
                # Calculate valuations with dynamic benchmarks
                valuation_data = calculate_fair_value_and_upside(info, sector, benchmarks)
                
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
                
                # PE filter (dynamic or static)
                if passes and pe_limit and pe_ratio:
                    if pe_ratio > pe_limit:
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
                        'Benchmark PE': valuation_data.get('benchmark_pe'),
                        'PE vs Sector': (pe_ratio / valuation_data.get('benchmark_pe', 1)) if pe_ratio and valuation_data.get('benchmark_pe') else None,
                        'Dividend Yield': dividend_yield * 100 if dividend_yield else 0,
                        '52W High': high_52w,
                        '52W Low': low_52w,
                        'From 52W High %': -pct_from_high if pct_from_high else None,
                        'From 52W Low %': pct_from_low if pct_from_low else None,
                    })
                
                # Check limit - if limit is -1, process all stocks
                if limit > 0 and len(results) >= limit:
                    break
                    
            except Exception as e:
                continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results), benchmarks

# ============================================================================
# INDIVIDUAL STOCK ANALYSIS WITH DYNAMIC BENCHMARKS
# ============================================================================
def analyze_individual_stock_dynamic(ticker):
    """Detailed analysis with dynamic sector benchmarks"""
    info, error = fetch_stock_data(ticker)
    
    if error or not info:
        return None, error
    
    # Find sector for this ticker
    sector = 'Default'
    for category, stocks in INDIAN_STOCKS.items():
        if ticker in stocks:
            sector = get_sector_from_category(category)
            break
    
    # Calculate dynamic benchmarks for this sector
    with st.spinner(f"🧮 Calculating dynamic benchmarks for {sector} sector..."):
        benchmarks = calculate_dynamic_sector_benchmarks(sector, sample_size=25)
    
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
    
    # Fair value calculations with dynamic benchmarks
    valuation_data = calculate_fair_value_and_upside(info, sector, benchmarks)
    
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
        'dynamic_benchmarks': benchmarks,
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
        title={'text': "PE Method (Dynamic)", 'font': {'size': 16, 'color': '#a78bfa'}},
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
        title={'text': "EV/EBITDA Method (Dynamic)", 'font': {'size': 16, 'color': '#a78bfa'}},
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
    NYZTRADE DYNAMIC SCREENER
</div>
<div class="sub-header">
    🧮 AI-Powered Dynamic Benchmarks | Real-Time Sector Analysis | Outlier-Free Calculations
</div>
''', unsafe_allow_html=True)

# ============================================================================
# STOCK UNIVERSE OVERVIEW
# ============================================================================
st.markdown('<div class="section-header">📊 Stock Universe & Dynamic Benchmarks</div>', unsafe_allow_html=True)

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
        <div style="color: #94a3b8;">🏢 Dynamic Sectors</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">IQR</div>
        <div style="color: #94a3b8;">🎯 Outlier Removal</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">6H</div>
        <div style="color: #94a3b8;">⚡ Benchmark Cache</div>
    </div>
    ''', unsafe_allow_html=True)

# Key features highlight
st.markdown(f'''
<div class="highlight-box">
    <h3>🚀 Dynamic Benchmark Technology</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
        <div>
            <strong>✨ Real-Time Calculation:</strong> PE/PB/EV ratios calculated from actual sector data<br>
            <strong>🎯 Outlier Exclusion:</strong> IQR method removes extreme values for accuracy<br>
            <strong>📊 Smart Caching:</strong> 6-hour cache for optimal performance
        </div>
        <div>
            <strong>⚡ Adaptive Screening:</strong> PE limits adjust to sector averages<br>
            <strong>🧮 Statistical Rigor:</strong> Minimum 5 stocks required for reliable averages<br>
            <strong>🔄 Auto-Fallback:</strong> Default benchmarks if calculation fails
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# Display sector breakdown with stock counts
st.markdown("**📈 Sector Coverage for Dynamic Analysis:**")
sector_breakdown = []
for sector, categories in SECTOR_MAPPING.items():
    stock_count = sum(len(INDIAN_STOCKS.get(cat, {})) for cat in categories)
    sector_breakdown.append((sector, stock_count))

sector_breakdown.sort(key=lambda x: x[1], reverse=True)

col1, col2 = st.columns(2)
for i, (sector, count) in enumerate(sector_breakdown):
    col = col1 if i % 2 == 0 else col2
    with col:
        st.markdown(f"• **{sector}**: {count:,} stocks → Dynamic benchmarks")

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
        ["🎯 Dynamic Sector Screeners", "📈 Individual Stock Analysis"],
        help="Choose your analysis approach"
    )
    
    if mode == "🎯 Dynamic Sector Screeners":
        st.markdown("### 🧮 Dynamic Sector Screeners")
        
        sector_screeners = get_sector_screeners()
        selected_screener = st.selectbox(
            "Choose Dynamic Screener",
            list(sector_screeners.keys()),
            help="Select a sector screener with dynamic benchmarks"
        )
        
        # Show screener details
        screener_config = sector_screeners[selected_screener]
        sector_stock_count = get_sector_stock_count(screener_config['sector'])
        
        st.markdown(f"**📋 {screener_config['description']}**")
        st.markdown(f"**🎯 Sector:** {screener_config['sector']}")
        st.markdown(f"**📊 Available Stocks:** {sector_stock_count:,}")
        st.markdown(f"**📈 Min Upside:** {screener_config['upside_min']}%")
        st.markdown(f"**💰 PE Multiplier:** {screener_config['pe_max_multiplier']}x sector avg")
        
        # Dynamic benchmark toggle
        use_dynamic = st.checkbox("🧮 Use Dynamic Benchmarks", value=True, 
                                  help="Calculate real-time sector averages (recommended)")
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters"):
            # Set maximum results to sector stock count
            result_limit = st.slider(
                "Max Results (0 = All Stocks)", 
                min_value=0, 
                max_value=sector_stock_count, 
                value=min(50, sector_stock_count), 
                step=10,
                help=f"0 means analyze ALL {sector_stock_count:,} stocks in this sector"
            )
            
            # Override default criteria with consistent float types
            custom_upside = st.number_input(
                "Custom Min Upside %", 
                value=float(screener_config['upside_min']), 
                min_value=0.0, 
                max_value=100.0, 
                step=5.0
            )
            
            custom_pe_multiplier = st.number_input(
                "Custom PE Multiplier", 
                value=float(screener_config['pe_max_multiplier']), 
                min_value=0.5, 
                max_value=3.0, 
                step=0.1,
                help="Multiplier of sector average PE"
            )
            
            if result_limit == 0:
                st.info(f"🎯 Will analyze ALL {sector_stock_count:,} stocks in {screener_config['sector']} sector")
        
        run_screener = st.button("🚀 RUN DYNAMIC SCREENER", use_container_width=True, type="primary")
    
    else:  # Individual Stock Analysis
        st.markdown("### 📈 Dynamic Individual Analysis")
        
        # Sector selection for browsing
        browse_sector = st.selectbox(
            "🔍 Browse by Sector",
            ['All Sectors'] + list(SECTOR_MAPPING.keys()),
            help="Filter stocks by sector for dynamic analysis"
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
        
        st.info(f"Showing {len(filtered_stocks)} stocks with dynamic benchmarks")
        
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
            help="Enter any NSE/BSE ticker for dynamic analysis"
        )
        
        if manual_ticker:
            st.session_state.selected_stock_ticker = manual_ticker.upper()
        
        analyze_stock = st.button("📊 DYNAMIC ANALYSIS", use_container_width=True, type="primary")

# ============================================================================
# MAIN CONTENT - DYNAMIC SECTOR SCREENERS
# ============================================================================

if mode == "🎯 Dynamic Sector Screeners":
    if run_screener:
        screener_config = sector_screeners[selected_screener]
        
        # Update criteria
        criteria = {
            'upside_min': custom_upside,
            'pe_max_multiplier': custom_pe_multiplier
        }
        
        # Set limit: 0 means all stocks, otherwise use the specified limit
        screen_limit = -1 if result_limit == 0 else result_limit
        
        st.markdown(f'''
        <div class="highlight-box">
            <h3>🧮 {selected_screener}</h3>
            <p><strong>Sector:</strong> {screener_config['sector']}</p>
            <p><strong>Total Stocks:</strong> {get_sector_stock_count(screener_config['sector']):,}</p>
            <p><strong>Analysis Scope:</strong> {"ALL stocks" if result_limit == 0 else f"Top {result_limit} results"}</p>
            <p><strong>Strategy:</strong> {screener_config['description']}</p>
            <p><strong>Dynamic Filters:</strong> Min Upside {custom_upside}%, PE ≤ {custom_pe_multiplier}x sector average</p>
            <p><strong>Method:</strong> {"🧮 Dynamic Benchmarks" if use_dynamic else "📊 Static Benchmarks"}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Run the dynamic screener
        results_df, calculated_benchmarks = run_dynamic_sector_screener(
            screener_config['sector'], 
            criteria, 
            limit=screen_limit, 
            use_dynamic_benchmarks=use_dynamic
        )
        
        if results_df.empty:
            st.warning("❌ No stocks match the dynamic screening criteria. Try relaxing the filters.")
        else:
            st.markdown(f'''
            <div class="success-message">
                ✅ Found <strong>{len(results_df)}</strong> dynamic opportunities in {screener_config['sector']} sector<br>
                🧮 Analysis Method: {"Dynamic sector benchmarks" if use_dynamic else "Static benchmarks"}<br>
                📊 Scope: {"Complete sector analysis" if result_limit == 0 else f"Top {result_limit} filtered results"}
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
            display_df['PE vs Sector'] = display_df['PE vs Sector'].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "N/A")
            display_df['From 52W High %'] = display_df['From 52W High %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            
            # Display results
            st.markdown('<div class="section-header">🎯 Dynamic Screening Results</div>', unsafe_allow_html=True)
            
            # Show columns optimized for dynamic analysis
            display_columns = ['Ticker', 'Name', 'Price', 'Fair Value', 'Upside %', 'PE Ratio', 'PE vs Sector', 'From 52W High %', 'Cap Type']
            
            st.dataframe(
                display_df[display_columns],
                use_container_width=True,
                hide_index=True,
                height=min(600, len(display_df) * 35 + 100)  # Adjust height based on results
            )
            
            # Download option with enhanced data
            csv = results_df.to_csv(index=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            scope = "Complete" if result_limit == 0 else f"Top{result_limit}"
            filename = f"NYZTrade_Dynamic_{screener_config['sector'].replace(' & ', '_')}_{scope}_Screen_{timestamp}.csv"
            
            st.download_button(
                f"📥 Download Dynamic Results ({len(results_df)} stocks)",
                data=csv,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )

# ============================================================================
# MAIN CONTENT - INDIVIDUAL STOCK ANALYSIS
# ============================================================================

elif mode == "📈 Individual Stock Analysis":
    if analyze_stock and hasattr(st.session_state, 'selected_stock_ticker'):
        ticker = st.session_state.selected_stock_ticker
        
        with st.spinner(f"🧮 Running dynamic analysis for {ticker}..."):
            analysis, error = analyze_individual_stock_dynamic(ticker)
        
        if analysis:
            # Display analysis with dynamic benchmarks
            st.markdown(f'''
            <div class="highlight-box">
                <h2>{analysis['company']}</h2>
                <div style="display: flex; flex-wrap: wrap; gap: 20px; color: #a78bfa;">
                    <span>🏷️ <strong>{analysis['ticker']}</strong></span>
                    <span>🏢 <strong>{analysis['sector']}</strong></span>
                    <span>💼 <strong>{analysis['cap_type']}</strong></span>
                    <span>🧮 <strong>Dynamic Benchmarks</strong></span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Show dynamic benchmarks
            benchmarks = analysis['dynamic_benchmarks']
            if benchmarks:
                st.markdown(f'''
                <div class="benchmark-box">
                    <h4>📊 Dynamic Sector Benchmarks vs Stock Metrics</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 15px 0;">
                        <div>
                            <strong>Sector Avg PE:</strong> {benchmarks.get('pe', 0):.2f}x<br>
                            <strong>Stock PE:</strong> {analysis['trailing_pe']:.2f}x<br>
                            <strong>Ratio:</strong> {(analysis['trailing_pe']/benchmarks.get('pe', 1)):.2f}x
                        </div>
                        <div>
                            <strong>Sector Avg PB:</strong> {benchmarks.get('pb', 0):.2f}x<br>
                            <strong>Stock PB:</strong> {analysis['pb_ratio']:.2f}x<br>
                            <strong>Ratio:</strong> {(analysis['pb_ratio']/benchmarks.get('pb', 1)):.2f}x
                        </div>
                        <div>
                            <strong>Sector Avg ROE:</strong> {benchmarks.get('roe', 0):.1f}%<br>
                            <strong>Stock ROE:</strong> {(analysis['roe']*100):.1f}%<br>
                            <strong>Difference:</strong> {((analysis['roe']*100) - benchmarks.get('roe', 0)):+.1f}pp
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Main valuation summary with dynamic fair value
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fair_value = analysis['avg_fair_value'] if analysis['avg_fair_value'] else analysis['price']
                upside = analysis['avg_upside'] if analysis['avg_upside'] else 0
                
                st.markdown(f'''
                <div class="metric-card">
                    <h3>🧮 Dynamic Valuation Summary</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #a78bfa;">₹{fair_value:,.2f}</div>
                            <div style="color: #94a3b8;">Dynamic Fair Value</div>
                        </div>
                        <div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #e2e8f0;">₹{analysis["price"]:,.2f}</div>
                            <div style="color: #94a3b8;">Current Price</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 15px;">
                        <span style="font-size: 1.5rem; font-weight: bold; color: {'#34d399' if upside > 0 else '#f87171'};">
                            {"📈" if upside > 0 else "📉"} {upside:+.1f}% Potential (Dynamic)
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                # Enhanced recommendation with dynamic context
                pe_ratio = analysis['trailing_pe'] / benchmarks.get('pe', 1) if analysis['trailing_pe'] and benchmarks else 1
                
                if upside > 25 and pe_ratio < 1.2:
                    rec_class, rec_text, rec_icon = "rec-strong-buy", "Strong Buy", "🚀"
                elif upside > 15 and pe_ratio < 1.3:
                    rec_class, rec_text, rec_icon = "rec-buy", "Buy", "✅"
                elif upside > 0 and pe_ratio < 1.5:
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
                    <div style="font-size: 0.8rem; margin-top: 3px;">PE: {pe_ratio:.2f}x sector avg</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Key metrics grid with sector comparison
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
            
            # Dynamic valuation gauges
            if analysis['upside_pe'] is not None or analysis['upside_ev'] is not None:
                st.markdown('<div class="section-header">🧮 Dynamic Valuation Methods</div>', unsafe_allow_html=True)
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
    <h4 style="color: #a78bfa; margin-bottom: 15px;">NYZTrade Dynamic | AI-Powered Real-Time Benchmark Analysis</h4>
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This platform uses dynamic benchmarks calculated from real market data, 
        excluding statistical outliers for accuracy. The analysis, recommendations, and data presented here should not be 
        considered as financial advice or investment recommendations. Dynamic benchmarks are recalculated regularly but may 
        not reflect the latest market conditions. Always conduct your own research and consult with qualified financial 
        professionals before making any investment decisions.
    </div>
    <div style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
        © 2024 NYZTrade Dynamic | Stock Universe: 8,984 Indian Stocks | Dynamic Benchmarks: IQR Outlier Removal | Cache: 6 Hours
    </div>
</div>
''', unsafe_allow_html=True)
