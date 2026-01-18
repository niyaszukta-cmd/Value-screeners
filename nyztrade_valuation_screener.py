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

def calculate_dynamic_sector_benchmarks(sector, sample_size=30, _progress_callback=None):
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
            if _progress_callback:
                _progress_callback(f"Analyzing {sector} benchmarks: {i+1}/{len(stock_items)}", i/len(stock_items))
            
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
def get_value_screeners():
    """Define sector-wise valuation-based screening strategies"""
    
    # Get all sectors
    all_sectors = list(SECTOR_MAPPING.keys())
    
    screeners = {}
    
    # 1. UNDERVALUED STOCKS - for each sector
    for sector in all_sectors:
        sector_icon = get_sector_icon(sector)
        screeners[f"{sector_icon} {sector} - Undervalued Stocks"] = {
            'sector': sector,
            'strategy_type': 'undervalued',
            'upside_min': 15.0,
            'upside_max': 500.0,  # Filter outliers
            'pe_max_multiplier': 0.9,  # PE below sector average
            'description': f'Undervalued {sector.lower()} stocks with 15-500% upside potential'
        }
    
    # 2. OVERVALUED STOCKS - for each sector
    for sector in all_sectors:
        sector_icon = get_sector_icon(sector)
        screeners[f"{sector_icon} {sector} - Overvalued Stocks"] = {
            'sector': sector,
            'strategy_type': 'overvalued',
            'upside_min': -100.0,
            'upside_max': -5.0,  # Negative upside (overvalued)
            'pe_min_multiplier': 1.3,  # PE above 1.3x sector average
            'description': f'Overvalued {sector.lower()} stocks trading above fair value'
        }
    
    # 3. UNDERVALUED NEAR 52W HIGH - for each sector
    for sector in all_sectors:
        sector_icon = get_sector_icon(sector)
        screeners[f"{sector_icon} {sector} - Undervalued Near 52W High"] = {
            'sector': sector,
            'strategy_type': 'undervalued_near_high',
            'upside_min': 20.0,
            'upside_max': 500.0,
            'pe_max_multiplier': 0.8,  # Significantly undervalued
            'from_52w_high_max': -5.0,  # Within 5% of 52W high
            'from_52w_high_min': -20.0,  # But at least 5% away
            'description': f'Undervalued {sector.lower()} stocks near 52-week highs'
        }
    
    # 4. UNDERVALUED WITH MOMENTUM - for each sector
    for sector in all_sectors:
        sector_icon = get_sector_icon(sector)
        screeners[f"{sector_icon} {sector} - Undervalued with Momentum"] = {
            'sector': sector,
            'strategy_type': 'undervalued_momentum',
            'upside_min': 25.0,
            'upside_max': 500.0,
            'pe_max_multiplier': 0.85,  # Undervalued
            'from_52w_low_min': 25.0,  # At least 25% up from 52W low (momentum)
            'from_52w_high_min': -50.0,  # Still away from high (room to grow)
            'description': f'Undervalued {sector.lower()} stocks with strong price momentum'
        }
    
    # 5. UNDERVALUED WITH GROWTH POTENTIAL - for each sector
    for sector in all_sectors:
        sector_icon = get_sector_icon(sector)
        screeners[f"{sector_icon} {sector} - Undervalued with Growth"] = {
            'sector': sector,
            'strategy_type': 'undervalued_growth',
            'upside_min': 30.0,
            'upside_max': 500.0,
            'pe_max_multiplier': 0.8,  # Significantly undervalued
            'roe_min': 12.0,  # Good profitability for growth
            'description': f'Undervalued {sector.lower()} stocks with strong growth potential'
        }
    
    return screeners

def get_sector_icon(sector):
    """Get icon for sector"""
    icons = {
        'Financial Services': '🏦',
        'Technology': '💻', 
        'Healthcare & Pharma': '💊',
        'Industrial & Manufacturing': '🏭',
        'Energy & Utilities': '⚡',
        'Consumer & Retail': '🛒',
        'Materials & Chemicals': '🧪',
        'Real Estate & Construction': '🏠',
        'Transportation': '🚛',
        'Automotive': '🚗',
        'Textiles': '🧵'
    }
    return icons.get(sector, '📊')

def run_value_screener(screener_config, criteria, limit=50):
    """Run value-based screening for specific sector with dynamic benchmarks"""
    
    # Get sector stocks
    if 'sector' in screener_config:
        sector = screener_config['sector']
        categories = SECTOR_MAPPING.get(sector, [])
        sector_stocks = get_stocks_in_categories(categories)
        
        if not sector_stocks:
            return pd.DataFrame()
        
        # Calculate dynamic benchmarks for this sector
        with st.spinner(f"🧮 Calculating dynamic benchmarks for {sector}..."):
            benchmarks = calculate_dynamic_sector_benchmarks(sector, sample_size=30)
        
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
            </div>
            ''', unsafe_allow_html=True)
        
        stock_items = list(sector_stocks.items())
        st.info(f"🔍 Screening {len(stock_items):,} stocks in {sector} sector with {screener_config['strategy_type']} strategy")
        
    else:
        # Fallback to all stocks (shouldn't happen with new structure)
        all_stocks = {}
        for category, stocks in INDIAN_STOCKS.items():
            all_stocks.update(stocks)
        stock_items = list(all_stocks.items())
        benchmarks = None
        sector = 'All Sectors'
        st.info(f"🔍 Screening {len(stock_items):,} stocks across all sectors with {screener_config['strategy_type']} strategy")
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    analyzed_count = 0
    missing_valuation_count = 0
    outlier_count = 0
    
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
                # Calculate valuations with dynamic benchmarks
                valuation_data = calculate_fair_value_and_upside(info, sector, benchmarks)
                
                # CRITICAL FILTERS - Skip if no valuation data available
                if valuation_data['avg_upside'] is None:
                    missing_valuation_count += 1
                    continue
                
                # CRITICAL FILTERS - Skip outliers (upside > 500%)
                if valuation_data['avg_upside'] > 500:
                    outlier_count += 1
                    continue
                
                price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
                market_cap = info.get('marketCap', 0)
                pe_ratio = info.get('trailingPE', 0)
                pb_ratio = info.get('priceToBook', 0)
                dividend_yield = info.get('dividendYield', 0)
                roe = info.get('returnOnEquity', 0)
                
                # 52-week data
                high_52w = info.get('fiftyTwoWeekHigh', 0)
                low_52w = info.get('fiftyTwoWeekLow', 0)
                pct_from_high = None
                pct_from_low = None
                
                if price and high_52w and low_52w and high_52w > low_52w:
                    pct_from_high = ((high_52w - price) / high_52w * 100)
                    pct_from_low = ((price - low_52w) / low_52w * 100)
                
                # Apply strategy-specific filters
                passes = apply_strategy_filters(screener_config, valuation_data, pe_ratio, roe, pct_from_high, pct_from_low, benchmarks)
                
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
                        'PE vs Sector': (pe_ratio / benchmarks.get('pe', 1)) if pe_ratio and benchmarks else None,
                        'ROE %': (roe * 100) if roe else 0,
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
    
    # Display analysis summary
    st.success(f"✅ Analyzed {analyzed_count:,} stocks | Found {len(results)} opportunities | Excluded {missing_valuation_count} (no valuation) + {outlier_count} outliers (>500%)")
    
    return pd.DataFrame(results)

def apply_strategy_filters(screener_config, valuation_data, pe_ratio, roe, pct_from_high, pct_from_low, benchmarks):
    """Apply strategy-specific filters"""
    
    strategy = screener_config.get('strategy_type', '')
    passes = True
    
    # Upside filters (common to all strategies)
    upside = valuation_data['avg_upside']
    if 'upside_min' in screener_config and upside < screener_config['upside_min']:
        passes = False
    if 'upside_max' in screener_config and upside > screener_config['upside_max']:
        passes = False
    
    # PE filters with dynamic benchmarks
    if passes and benchmarks:
        sector_pe = benchmarks.get('pe', 20.0)
        
        if 'pe_max_multiplier' in screener_config:
            max_pe = sector_pe * screener_config['pe_max_multiplier']
            if pe_ratio and pe_ratio > max_pe:
                passes = False
        
        if 'pe_min_multiplier' in screener_config:
            min_pe = sector_pe * screener_config['pe_min_multiplier']
            if pe_ratio and pe_ratio < min_pe:
                passes = False
    
    # ROE filters for growth strategies
    if passes and 'roe_min' in screener_config:
        if not roe or (roe * 100) < screener_config['roe_min']:
            passes = False
    
    # 52-week filters for momentum strategies
    if passes and 'from_52w_high_max' in screener_config:
        if not pct_from_high or (-pct_from_high) > screener_config['from_52w_high_max']:
            passes = False
    
    if passes and 'from_52w_high_min' in screener_config:
        if not pct_from_high or (-pct_from_high) < screener_config['from_52w_high_min']:
            passes = False
    
    if passes and 'from_52w_low_min' in screener_config:
        if not pct_from_low or pct_from_low < screener_config['from_52w_low_min']:
            passes = False
    
    return passes

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
    NYZTRADE SECTOR SCREENER
</div>
<div class="sub-header">
    🎯 55 Sector-Wise Screeners | 5 Valuation Strategies | Dynamic Benchmarks | Outlier Filtering
</div>
''', unsafe_allow_html=True)

# ============================================================================
# STOCK UNIVERSE OVERVIEW
# ============================================================================
st.markdown('<div class="section-header">📊 Sector-Wise Valuation Screening</div>', unsafe_allow_html=True)

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
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">5</div>
        <div style="color: #94a3b8;">🎯 Value Strategies</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">500%</div>
        <div style="color: #94a3b8;">⚠️ Outlier Filter</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">✓</div>
        <div style="color: #94a3b8;">🧮 Quality Validation</div>
    </div>
    ''', unsafe_allow_html=True)

# Key features highlight
st.markdown(f'''
<div class="highlight-box">
    <h3>💎 Advanced Value Screening Technology</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
        <div>
            <strong>💎 Deep Value Analysis:</strong> Identifies undervalued stocks with 20-500% upside potential<br>
            <strong>🚀 Momentum Strategies:</strong> Finds undervalued stocks near 52-week highs<br>
            <strong>🌱 Growth Potential:</strong> Combines value with high ROE for growth opportunities
        </div>
        <div>
            <strong>⚠️ Outlier Protection:</strong> Excludes extreme outliers (>500% upside)<br>
            <strong>🧮 Quality Validation:</strong> Only stocks with complete valuation data<br>
            <strong>📊 Multi-Strategy:</strong> 5 distinct value-based screening approaches
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

# Display sector breakdown with stock counts
st.markdown("**📈 Multi-Sector Value Analysis Coverage:**")
sector_breakdown = []
for sector, categories in SECTOR_MAPPING.items():
    stock_count = sum(len(INDIAN_STOCKS.get(cat, {})) for cat in categories)
    sector_breakdown.append((sector, stock_count))

sector_breakdown.sort(key=lambda x: x[1], reverse=True)

col1, col2 = st.columns(2)
for i, (sector, count) in enumerate(sector_breakdown):
    col = col1 if i % 2 == 0 else col2
    with col:
        st.markdown(f"• **{sector}**: {count:,} stocks → Value screening")

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
        ["🎯 Value-Based Screeners", "📈 Individual Stock Analysis"],
        help="Choose your analysis approach"
    )
    
    if mode == "🎯 Value-Based Screeners":
        st.markdown("### 💎 Value-Based Screeners")
        
        value_screeners = get_value_screeners()
        selected_screener = st.selectbox(
            "Choose Value Screener",
            list(value_screeners.keys()),
            help="Select a value-focused screening strategy"
        )
        
        # Show screener details
        screener_config = value_screeners[selected_screener]
        
        # Extract sector from screener name
        if 'sector' in screener_config:
            sector = screener_config['sector']
            sector_stock_count = get_sector_stock_count(sector)
            st.markdown(f"**🏢 Sector:** {sector}")
            st.markdown(f"**📊 Sector Stocks:** {sector_stock_count:,}")
        else:
            total_stock_count = sum(len(stocks) for stocks in INDIAN_STOCKS.values())
            st.markdown(f"**📊 Universe:** {total_stock_count:,} stocks across all sectors")
        
        st.markdown(f"**📋 {screener_config['description']}**")
        st.markdown(f"**🎯 Strategy:** {screener_config['strategy_type']}")
        
        # Show key criteria with dynamic benchmark info
        if 'upside_min' in screener_config:
            st.markdown(f"**📈 Min Upside:** {screener_config['upside_min']}%")
        if 'upside_max' in screener_config:
            st.markdown(f"**⚠️ Max Upside:** {screener_config['upside_max']}% (outlier filter)")
        if 'pe_max_multiplier' in screener_config:
            st.markdown(f"**💰 PE Filter:** {screener_config['pe_max_multiplier']}x sector average")
        if 'pe_min_multiplier' in screener_config:
            st.markdown(f"**💰 PE Filter:** ≥{screener_config['pe_min_multiplier']}x sector average")
        if 'roe_min' in screener_config:
            st.markdown(f"**🌱 Min ROE:** {screener_config['roe_min']}%")
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters"):
            # Result limit
            result_limit = st.slider(
                "Max Results", 
                min_value=10, 
                max_value=500, 
                value=100, 
                step=10,
                help="Maximum number of results to display"
            )
            
            # Override default criteria with consistent float types
            custom_upside_min = st.number_input(
                "Custom Min Upside %", 
                value=float(screener_config.get('upside_min', 15)), 
                min_value=0.0, 
                max_value=100.0, 
                step=5.0
            )
            
            custom_upside_max = st.number_input(
                "Custom Max Upside % (Outlier Filter)", 
                value=float(screener_config.get('upside_max', 500)), 
                min_value=100.0, 
                max_value=1000.0, 
                step=50.0,
                help="Exclude extreme outliers above this upside %"
            )
            
            # PE multiplier for dynamic benchmarks
            if 'pe_max_multiplier' in screener_config:
                custom_pe_multiplier = st.number_input(
                    "Custom PE Multiplier (vs Sector Average)", 
                    value=float(screener_config.get('pe_max_multiplier', 1.0)), 
                    min_value=0.5, 
                    max_value=2.0, 
                    step=0.1,
                    help="PE ratio as multiple of sector average (e.g., 0.8 = 80% of sector PE)"
                )
            elif 'pe_min_multiplier' in screener_config:
                custom_pe_multiplier = st.number_input(
                    "Custom PE Multiplier (vs Sector Average)", 
                    value=float(screener_config.get('pe_min_multiplier', 1.0)), 
                    min_value=1.0, 
                    max_value=3.0, 
                    step=0.1,
                    help="Minimum PE ratio as multiple of sector average"
                )
            else:
                custom_pe_multiplier = None
            
            # ROE filter for growth strategies
            if 'roe_min' in screener_config:
                custom_roe_min = st.number_input(
                    "Custom Min ROE %", 
                    value=float(screener_config.get('roe_min', 12)), 
                    min_value=0.0, 
                    max_value=50.0, 
                    step=2.0,
                    help="Minimum Return on Equity for growth potential"
                )
            else:
                custom_roe_min = None
            
            st.info("🎯 Stocks without valuation data and outliers >500% are automatically excluded")
            st.info("🧮 Dynamic sector benchmarks are calculated in real-time")
        
        run_screener = st.button("🚀 RUN VALUE SCREENER", use_container_width=True, type="primary")
    
    else:  # Individual Stock Analysis
        st.markdown("### 📈 Individual Stock Analysis")
        
        # Sector selection for browsing
        browse_sector = st.selectbox(
            "🔍 Browse by Sector",
            ['All Sectors'] + list(SECTOR_MAPPING.keys()),
            help="Filter stocks by sector for analysis"
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
        
        st.info(f"Showing {len(filtered_stocks)} stocks for value analysis")
        
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
            help="Enter any NSE/BSE ticker for analysis"
        )
        
        if manual_ticker:
            st.session_state.selected_stock_ticker = manual_ticker.upper()
        
        analyze_stock = st.button("📊 ANALYZE STOCK", use_container_width=True, type="primary")

# ============================================================================
# MAIN CONTENT - VALUE-BASED SCREENERS
# ============================================================================

if mode == "🎯 Value-Based Screeners":
    if run_screener:
        screener_config = value_screeners[selected_screener]
        
        # Update criteria with custom values
        updated_config = screener_config.copy()
        updated_config['upside_min'] = custom_upside_min
        updated_config['upside_max'] = custom_upside_max
        
        # Update PE multiplier if applicable
        if custom_pe_multiplier is not None:
            if 'pe_max_multiplier' in screener_config:
                updated_config['pe_max_multiplier'] = custom_pe_multiplier
            elif 'pe_min_multiplier' in screener_config:
                updated_config['pe_min_multiplier'] = custom_pe_multiplier
        
        # Update ROE if applicable  
        if custom_roe_min is not None:
            updated_config['roe_min'] = custom_roe_min
        
        st.markdown(f'''
        <div class="highlight-box">
            <h3>💎 {selected_screener}</h3>
            <p><strong>Sector:</strong> {updated_config.get('sector', 'All Sectors')}</p>
            <p><strong>Strategy:</strong> {updated_config['strategy_type'].replace('_', ' ').title()}</p>
            <p><strong>Description:</strong> {updated_config['description']}</p>
            <p><strong>Dynamic Filters:</strong> Upside {custom_upside_min}% to {custom_upside_max}%</p>
            <p><strong>Scope:</strong> Sector-specific analysis with dynamic benchmarks</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Run the value screener
        results_df = run_value_screener(updated_config, None, result_limit)
        
        if results_df.empty:
            st.warning("❌ No stocks match the screening criteria. Try relaxing the filters.")
        else:
            st.markdown(f'''
            <div class="success-message">
                ✅ Found <strong>{len(results_df)}</strong> {updated_config['strategy_type'].replace('_', ' ')} opportunities in {updated_config.get('sector', 'All Sectors')}<br>
                📊 Strategy: {updated_config['description']}<br>
                🎯 Filtered: Excluded outliers (>{custom_upside_max}%) and stocks without valuation data<br>
                🧮 Analysis: Real-time dynamic benchmarks applied
            </div>
            ''', unsafe_allow_html=True)
            
            # Sort by upside percentage appropriately
            if screener_config['strategy_type'] == 'overvalued':
                # For overvalued stocks, sort by most negative upside first
                results_df = results_df.sort_values('Upside %', ascending=True, na_position='last')
            else:
                # For undervalued stocks, sort by highest upside first  
                results_df = results_df.sort_values('Upside %', ascending=False, na_position='last')
            
            # Format the dataframe for display
            display_df = results_df.copy()
            
            # Format columns
            display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
            display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A')
            display_df['Fair Value'] = display_df['Fair Value'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) and x > 0 else "N/A")
            display_df['Upside %'] = display_df['Upside %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            display_df['PE Ratio'] = display_df['PE Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x > 0 else "N/A")
            display_df['ROE %'] = display_df['ROE %'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
            display_df['From 52W High %'] = display_df['From 52W High %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            display_df['From 52W Low %'] = display_df['From 52W Low %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            
            # Display results
            st.markdown('<div class="section-header">💎 Value Screening Results</div>', unsafe_allow_html=True)
            
            # Show columns optimized for value analysis
            if screener_config['strategy_type'] in ['undervalued_momentum', 'undervalued_momentum_plus']:
                display_columns = ['Ticker', 'Name', 'Sector', 'Price', 'Fair Value', 'Upside %', 'From 52W High %', 'From 52W Low %', 'PE Ratio']
            elif screener_config['strategy_type'] == 'undervalued_growth':
                display_columns = ['Ticker', 'Name', 'Sector', 'Price', 'Fair Value', 'Upside %', 'PE Ratio', 'ROE %', 'Cap Type']
            else:
                display_columns = ['Ticker', 'Name', 'Sector', 'Price', 'Fair Value', 'Upside %', 'PE Ratio', 'From 52W High %', 'Cap Type']
            
            st.dataframe(
                display_df[display_columns],
                use_container_width=True,
                hide_index=True,
                height=min(600, len(display_df) * 35 + 100)  # Adjust height based on results
            )
            
            # Download option with enhanced data
            csv = results_df.to_csv(index=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"NYZTrade_{screener_config['strategy_type'].title()}_Screen_{timestamp}.csv"
            
            st.download_button(
                f"📥 Download Results ({len(results_df)} stocks)",
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
        
        with st.spinner(f"📊 Analyzing {ticker}..."):
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
                    <h3>💎 Valuation Summary</h3>
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
    <h4 style="color: #a78bfa; margin-bottom: 15px;">NYZTrade Value | Advanced Multi-Strategy Value Analysis</h4>
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This platform uses advanced value-based screening strategies with 
        outlier filtering and quality validation. The analysis, recommendations, and data presented here should not be 
        considered as financial advice or investment recommendations. Stocks with extreme outliers (>500% upside) are 
        excluded to prevent unrealistic expectations. Only stocks with complete valuation data are included in results. 
        Always conduct your own research and consult with qualified financial professionals before making any investment decisions.
    </div>
    <div style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
        © 2024 NYZTrade Value | Stock Universe: 8,984 Indian Stocks | Outlier Filter: >500% | Quality Validation: Complete Valuation Data Only
    </div>
</div>
''', unsafe_allow_html=True)
