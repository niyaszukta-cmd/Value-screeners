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

# ============================================================================
# COMPREHENSIVE INDIAN STOCKS DATABASE - STREAMLIT CLOUD READY
# ============================================================================

INDIAN_STOCKS = {
    "Agricultural Chemicals": {
        "UPL.NS": "UPL Limited",
        "RALLIS.NS": "Rallis India Limited",
        "PIIND.NS": "PI Industries Limited",
        "COROMANDEL.NS": "Coromandel International Limited",
        "CHAMBLFERT.NS": "Chambal Fertilisers and Chemicals Limited",
        "DEEPAKFERT.NS": "Deepak Fertilisers And Petrochemicals Corporation Limited",
        "GNFC.NS": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
        "GSFC.NS": "Gujarat State Fertilizers & Chemicals Limited",
        "RCF.NS": "Rashtriya Chemicals And Fertilizers Limited",
        "NFL.NS": "National Fertilizers Limited",
        "FACT.NS": "The Fertilisers And Chemicals Travancore Limited",
        "INSECTICID.NS": "Insecticides (India) Limited",
        "SHARDACROP.NS": "Sharda Cropchem Limited"
    },

    "Auto Manufacturers - Major": {
        "MARUTI.NS": "Maruti Suzuki India Limited",
        "TATAMOTORS.NS": "Tata Motors Limited",
        "M&M.NS": "Mahindra & Mahindra Limited",
        "BAJAJ-AUTO.NS": "Bajaj Auto Limited",
        "HEROMOTOCO.NS": "Hero MotoCorp Limited",
        "TVSMOTOR.NS": "TVS Motor Company Limited",
        "EICHERMOT.NS": "Eicher Motors Limited",
        "ASHOKLEY.NS": "Ashok Leyland Limited"
    },

    "Auto Parts": {
        "BOSCHLTD.NS": "Bosch Limited",
        "MOTHERSUMI.NS": "Motherson Sumi Systems Limited",
        "BHARATFORG.NS": "Bharat Forge Limited",
        "BALKRISIND.NS": "Balkrishna Industries Limited",
        "APOLLOTYRE.NS": "Apollo Tyres Limited",
        "MRF.NS": "MRF Limited",
        "CEATLTD.NS": "CEAT Limited",
        "JK-TYRE.NS": "JK Tyre & Industries Limited"
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
        "JKCEMENT.NS": "JK Cement Limited"
    },

    "Chemicals - Major Diversified": {
        "ASIANPAINT.NS": "Asian Paints Limited",
        "BERGER.NS": "Berger Paints India Limited",
        "KANSAINER.NS": "Kansai Nerolac Paints Limited",
        "PIDILITIND.NS": "Pidilite Industries Limited",
        "ATUL.NS": "Atul Limited",
        "DEEPAKNTR.NS": "Deepak Nitrite Limited",
        "SRF.NS": "SRF Limited",
        "TATACHEM.NS": "Tata Chemicals Limited",
        "NAVINFLUOR.NS": "Navin Fluorine International Limited",
        "NOCIL.NS": "NOCIL Limited",
        "ROSSARI.NS": "Rossari Biotech Limited"
    },

    "Credit Services": {
        "BAJFINANCE.NS": "Bajaj Finance Limited",
        "CHOLAFIN.NS": "Cholamandalam Investment and Finance Company Limited",
        "M&MFIN.NS": "Mahindra & Mahindra Financial Services Limited",
        "MANAPPURAM.NS": "Manappuram Finance Limited",
        "MUTHOOTFIN.NS": "Muthoot Finance Limited",
        "SHRIRAMFIN.NS": "Shriram Finance Limited"
    },

    "Drug Manufacturers - Major": {
        "SUNPHARMA.NS": "Sun Pharmaceutical Industries Limited",
        "DRREDDY.NS": "Dr. Reddy's Laboratories Limited",
        "CIPLA.NS": "Cipla Limited",
        "LUPIN.NS": "Lupin Limited",
        "DIVISLAB.NS": "Divi's Laboratories Limited",
        "TORNTPHARM.NS": "Torrent Pharmaceuticals Limited",
        "ALKEM.NS": "Alkem Laboratories Limited",
        "AUROPHARMA.NS": "Aurobindo Pharma Limited",
        "GLENMARK.NS": "Glenmark Pharmaceuticals Limited",
        "CADILAHC.NS": "Cadila Healthcare Limited",
        "AJANTPHARM.NS": "Ajanta Pharma Limited"
    },

    "Drug Manufacturers - Other": {
        "ABBOTINDIA.NS": "Abbott India Limited",
        "PFIZER.NS": "Pfizer Limited",
        "GSK.NS": "GlaxoSmithKline Pharmaceuticals Limited",
        "SANOFI.NS": "Sanofi India Limited"
    },

    "Drugs - Generic": {
        "IPCALAB.NS": "IPCA Laboratories Limited",
        "JBCHEPHARM.NS": "JB Chemicals & Pharmaceuticals Limited"
    },

    "Diversified Electronics": {
        "ABB.NS": "ABB India Limited",
        "SIEMENS.NS": "Siemens Limited",
        "CUMMINSIND.NS": "Cummins India Limited",
        "SCHNEIDER.NS": "Schneider Electric Infrastructure Limited"
    },

    "Diversified Machinery": {
        "LT.NS": "Larsen & Toubro Limited",
        "BHEL.NS": "Bharat Heavy Electricals Limited",
        "THERMAX.NS": "Thermax Limited",
        "KEC.NS": "KEC International Limited"
    },

    "Electric Utilities": {
        "NTPC.NS": "NTPC Limited",
        "POWERGRID.NS": "Power Grid Corporation of India Limited",
        "TATAPOWER.NS": "The Tata Power Company Limited",
        "ADANIPOWER.NS": "Adani Power Limited",
        "TORNTPOWER.NS": "Torrent Power Limited",
        "JSWENERGY.NS": "JSW Energy Limited",
        "NHPC.NS": "NHPC Limited"
    },

    "Financial Services": {
        "BAJAJFINSV.NS": "Bajaj Finserv Limited",
        "HDFCAMC.NS": "HDFC Asset Management Company Limited",
        "IIFL.NS": "India Infoline Limited",
        "LICHSGFIN.NS": "LIC Housing Finance Limited"
    },

    "Food - Major Diversified": {
        "NESTLEIND.NS": "Nestle India Limited",
        "BRITANNIA.NS": "Britannia Industries Limited",
        "ITC.NS": "ITC Limited",
        "HINDUNILVR.NS": "Hindustan Unilever Limited",
        "DABUR.NS": "Dabur India Limited",
        "MARICO.NS": "Marico Limited",
        "GODREJCP.NS": "Godrej Consumer Products Limited",
        "TATACONSUM.NS": "Tata Consumer Products Limited",
        "UBL.NS": "United Breweries Limited",
        "VBL.NS": "Varun Beverages Limited",
        "JUBLFOOD.NS": "Jubilant FoodWorks Limited"
    },

    "Gas Utilities": {
        "GAIL.NS": "GAIL (India) Limited",
        "PETRONET.NS": "Petronet LNG Limited",
        "GSPL.NS": "Gujarat State Petronet Limited"
    },

    "Information Technology Services": {
        "TCS.NS": "Tata Consultancy Services Limited",
        "INFY.NS": "Infosys Limited",
        "HCLTECH.NS": "HCL Technologies Limited",
        "WIPRO.NS": "Wipro Limited",
        "TECHM.NS": "Tech Mahindra Limited",
        "LTIM.NS": "LTIMindtree Limited",
        "MPHASIS.NS": "Mphasis Limited",
        "PERSISTENT.NS": "Persistent Systems Limited",
        "LTTS.NS": "L&T Technology Services Limited",
        "CYIENT.NS": "Cyient Limited",
        "TATAELXSI.NS": "Tata Elxsi Limited"
    },

    "Insurance - Life": {
        "SBILIFE.NS": "SBI Life Insurance Company Limited",
        "HDFCLIFE.NS": "HDFC Life Insurance Company Limited",
        "ICICIPRULI.NS": "ICICI Prudential Life Insurance Company Limited"
    },

    "Insurance - Property & Casualty": {
        "ICICIGI.NS": "ICICI Lombard General Insurance Company Limited",
        "SBICARD.NS": "SBI Cards and Payment Services Limited"
    },

    "Jewelry Stores": {
        "TITAN.NS": "Titan Company Limited",
        "KALYANKJIL.NS": "Kalyan Jewellers India Limited"
    },

    "Medical Services": {
        "APOLLOHOSP.NS": "Apollo Hospitals Enterprise Limited",
        "FORTIS.NS": "Fortis Healthcare Limited"
    },

    "Money Center Banks": {
        "SBIN.NS": "State Bank of India",
        "HDFCBANK.NS": "HDFC Bank Limited",
        "ICICIBANK.NS": "ICICI Bank Limited",
        "KOTAKBANK.NS": "Kotak Mahindra Bank Limited",
        "AXISBANK.NS": "Axis Bank Limited",
        "INDUSINDBK.NS": "IndusInd Bank Limited",
        "PNB.NS": "Punjab National Bank",
        "CANBK.NS": "Canara Bank",
        "BANKBARODA.NS": "Bank of Baroda"
    },

    "Oil & Gas Operations": {
        "RELIANCE.NS": "Reliance Industries Limited",
        "ONGC.NS": "Oil and Natural Gas Corporation Limited",
        "OIL.NS": "Oil India Limited"
    },

    "Oil & Gas Refining & Marketing": {
        "BPCL.NS": "Bharat Petroleum Corporation Limited",
        "IOC.NS": "Indian Oil Corporation Limited",
        "HINDPETRO.NS": "Hindustan Petroleum Corporation Limited"
    },

    "Real Estate Development": {
        "DLF.NS": "DLF Limited",
        "GODREJPROP.NS": "Godrej Properties Limited",
        "SOBHA.NS": "Sobha Limited",
        "PRESTIGE.NS": "Prestige Estates Projects Limited",
        "BRIGADE.NS": "Brigade Enterprises Limited"
    },

    "Renewable Energy": {
        "ADANIGREEN.NS": "Adani Green Energy Limited",
        "SUZLON.NS": "Suzlon Energy Limited"
    },

    "Retail - Apparel & Accessories": {
        "ADITBIRL.NS": "Aditya Birla Fashion & Retail Limited",
        "RAYMOND.NS": "Raymond Limited",
        "PAGEIND.NS": "Page Industries Limited"
    },

    "Steel & Iron": {
        "TATASTEEL.NS": "Tata Steel Limited",
        "JSWSTEEL.NS": "JSW Steel Limited",
        "SAIL.NS": "Steel Authority of India Limited",
        "JINDALSTEL.NS": "Jindal Steel & Power Limited",
        "NMDC.NS": "NMDC Limited",
        "VEDL.NS": "Vedanta Limited",
        "COALINDIA.NS": "Coal India Limited"
    },

    "Textile Industrial": {
        "ARVIND.NS": "Arvind Limited",
        "TRIDENT.NS": "Trident Limited",
        "VTL.NS": "Vardhman Textiles Limited",
        "WELSPUNIND.NS": "Welspun India Limited",
        "SUTLEJTEX.NS": "Sutlej Textiles and Industries Limited"
    },

    "Wireless Communications": {
        "BHARTIARTL.NS": "Bharti Airtel Limited",
        "IDEA.NS": "Idea Cellular Limited",
        "RCOM.NS": "Reliance Communications Limited",
        "TATACOMM.NS": "Tata Communications Limited"
    }
}

# Database utility functions
def get_all_tickers():
    """Get list of all ticker symbols"""
    tickers = []
    for category_stocks in INDIAN_STOCKS.values():
        tickers.extend(category_stocks.keys())
    return tickers

def get_stocks_by_category(category):
    """Get stocks in a specific category"""
    return INDIAN_STOCKS.get(category, {})

def get_all_categories():
    """Get list of all categories"""
    return list(INDIAN_STOCKS.keys())

def search_stock(query):
    """Search for stocks by ticker or name"""
    results = {}
    query_upper = query.upper()
    
    for category, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query_upper in ticker.upper() or query_upper in name.upper():
                if category not in results:
                    results[category] = {}
                results[category][ticker] = name
    
    return results

def get_stock_info(ticker):
    """Get stock information by ticker"""
    for category, stocks in INDIAN_STOCKS.items():
        if ticker in stocks:
            return {
                "ticker": ticker,
                "name": stocks[ticker],
                "category": category
            }
    return None

# Statistics  
TOTAL_STOCKS = sum(len(stocks) for stocks in INDIAN_STOCKS.values())
TOTAL_CATEGORIES = len(INDIAN_STOCKS)

# ============================================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="NYZTrade - Industry Stock Screener", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with mobile responsiveness
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .stats-container {
        display: flex; 
        justify-content: space-around; 
        flex-wrap: wrap; 
        margin: 1rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        min-width: 150px;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .highlight-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1));
        border: 2px solid rgba(34, 197, 94, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .success-message {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.15));
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #059669;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header { padding: 1rem; }
        .stats-container { flex-direction: column; align-items: center; }
        .stat-card { min-width: 200px; margin: 0.25rem 0; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SECTOR GROUPING AND BENCHMARKS
# ============================================================================

INDUSTRY_TO_SECTOR = {
    # Financial Services
    "Credit Services": "Financial Services", 
    "Financial Services": "Financial Services",
    "Insurance - Life": "Financial Services",
    "Insurance - Property & Casualty": "Financial Services",
    "Money Center Banks": "Financial Services",
    
    # Technology
    "Information Technology Services": "Technology",
    "Wireless Communications": "Technology",
    
    # Healthcare & Pharma
    "Drug Manufacturers - Major": "Healthcare & Pharma",
    "Drug Manufacturers - Other": "Healthcare & Pharma",
    "Drugs - Generic": "Healthcare & Pharma",
    "Medical Services": "Healthcare & Pharma",
    
    # Industrial & Manufacturing
    "Diversified Electronics": "Industrial & Manufacturing",
    "Diversified Machinery": "Industrial & Manufacturing",
    "Steel & Iron": "Industrial & Manufacturing",
    
    # Energy & Utilities
    "Electric Utilities": "Energy & Utilities",
    "Gas Utilities": "Energy & Utilities",
    "Oil & Gas Operations": "Energy & Utilities",
    "Oil & Gas Refining & Marketing": "Energy & Utilities",
    "Renewable Energy": "Energy & Utilities",
    
    # Consumer & Retail
    "Auto Manufacturers - Major": "Consumer & Retail",
    "Auto Parts": "Consumer & Retail",
    "Food - Major Diversified": "Consumer & Retail",
    "Jewelry Stores": "Consumer & Retail",
    "Retail - Apparel & Accessories": "Consumer & Retail",
    
    # Materials & Chemicals
    "Agricultural Chemicals": "Materials & Chemicals",
    "Cement & Aggregates": "Materials & Chemicals",
    "Chemicals - Major Diversified": "Materials & Chemicals",
    
    # Real Estate & Construction
    "Real Estate Development": "Real Estate & Construction",
    
    # Textiles
    "Textile Industrial": "Textiles"
}

def get_sector_for_industry(industry):
    """Get broad sector for a given industry"""
    return INDUSTRY_TO_SECTOR.get(industry, "Other")

# Default benchmarks by sector
SECTOR_BENCHMARKS = {
    'Financial Services': {'pe': 18.0, 'pb': 1.5, 'roe': 15.0},
    'Technology': {'pe': 25.0, 'pb': 3.5, 'roe': 20.0},
    'Healthcare & Pharma': {'pe': 28.0, 'pb': 3.0, 'roe': 18.0},
    'Industrial & Manufacturing': {'pe': 22.0, 'pb': 2.0, 'roe': 14.0},
    'Energy & Utilities': {'pe': 15.0, 'pb': 1.2, 'roe': 12.0},
    'Consumer & Retail': {'pe': 30.0, 'pb': 2.5, 'roe': 16.0},
    'Materials & Chemicals': {'pe': 18.0, 'pb': 1.8, 'roe': 13.0},
    'Real Estate & Construction': {'pe': 25.0, 'pb': 1.5, 'roe': 12.0},
    'Textiles': {'pe': 20.0, 'pb': 1.5, 'roe': 15.0},
    'Other': {'pe': 20.0, 'pb': 2.0, 'roe': 15.0}
}

# ============================================================================
# STOCK DATA FETCHING AND CACHING
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(ticker, max_retries=2):
    """Fetch stock data with caching and retry mechanism"""
    for attempt in range(max_retries + 1):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info:
                continue
                
            return info, None
            
        except Exception as e:
            if attempt == max_retries:
                return None, str(e)
            time.sleep(0.5)  # Brief pause before retry
    
    return None, "Failed after retries"

def get_stock_fundamentals(ticker):
    """Get key fundamental metrics for a stock"""
    info, error = fetch_stock_data(ticker)
    
    if error or not info:
        return None
    
    try:
        # Extract key metrics
        fundamentals = {
            'ticker': ticker,
            'name': info.get('longName', info.get('shortName', 'Unknown')),
            'price': info.get('currentPrice', info.get('regularMarketPrice')),
            'market_cap': info.get('marketCap'),
            'trailing_pe': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'roe': info.get('returnOnEquity'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'profit_margin': info.get('profitMargins'),
            'debt_to_equity': info.get('debtToEquity'),
            '52w_high': info.get('fiftyTwoWeekHigh'),
            '52w_low': info.get('fiftyTwoWeekLow'),
            'volume': info.get('volume')
        }
        
        # Calculate additional metrics
        if fundamentals['price'] and fundamentals['52w_high']:
            fundamentals['pct_from_high'] = ((fundamentals['price'] - fundamentals['52w_high']) / fundamentals['52w_high']) * 100
        
        if fundamentals['price'] and fundamentals['52w_low']:
            fundamentals['pct_from_low'] = ((fundamentals['price'] - fundamentals['52w_low']) / fundamentals['52w_low']) * 100
        
        # Determine market cap category
        if fundamentals['market_cap']:
            if fundamentals['market_cap'] >= 200000000000:  # 20,000 Cr
                fundamentals['cap_type'] = 'Large'
            elif fundamentals['market_cap'] >= 50000000000:  # 5,000 Cr
                fundamentals['cap_type'] = 'Mid'
            else:
                fundamentals['cap_type'] = 'Small'
        else:
            fundamentals['cap_type'] = 'Unknown'
        
        return fundamentals
        
    except Exception as e:
        return None

# ============================================================================
# VALUATION AND SCREENING LOGIC
# ============================================================================

def calculate_fair_value(fundamentals, benchmarks):
    """Simple fair value calculation using industry PE"""
    if not fundamentals or not benchmarks or not fundamentals.get('trailing_pe'):
        return None
    
    try:
        # Simple PE-based valuation
        current_pe = fundamentals['trailing_pe']
        sector_pe = benchmarks['pe']
        
        if current_pe > 0:
            # Calculate fair value based on sector PE
            fair_value = fundamentals['price'] * (sector_pe / current_pe)
            return fair_value if fair_value > 0 else None
    except:
        return None
    
    return None

def run_industry_screener(industry, strategy_type="undervalued", max_results=50):
    """Run screening for a specific industry"""
    
    stocks = get_stocks_by_category(industry)
    if not stocks:
        return pd.DataFrame()
    
    # Get sector benchmarks for industry
    sector = get_sector_for_industry(industry)
    benchmarks = SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other'])
    
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_stocks = len(stocks)
    
    for i, (ticker, name) in enumerate(stocks.items()):
        # Update progress
        progress = (i + 1) / total_stocks
        progress_bar.progress(progress)
        status_text.text(f"Processing {ticker} ({i + 1}/{total_stocks})")
        
        # Get fundamentals
        fundamentals = get_stock_fundamentals(ticker)
        if not fundamentals or not fundamentals['price']:
            continue
        
        # Calculate fair value
        fair_value = calculate_fair_value(fundamentals, benchmarks)
        if not fair_value or fair_value <= 0:
            continue
        
        # Calculate upside
        upside = ((fair_value - fundamentals['price']) / fundamentals['price']) * 100
        
        # Apply strategy filters
        passes_filter = False
        
        if strategy_type == "undervalued":
            if upside >= 15:  # At least 15% upside
                passes_filter = True
        
        elif strategy_type == "undervalued_supertrend":
            if upside >= 15:
                # Use 52-week position as proxy for technical strength
                if fundamentals.get('pct_from_high') and fundamentals['pct_from_high'] >= -25:
                    passes_filter = True
        
        elif strategy_type == "undervalued_rsi_macd":
            if upside >= 15:
                # Use 52-week position as proxy for not overbought
                if fundamentals.get('pct_from_high') and fundamentals['pct_from_high'] >= -30:
                    passes_filter = True
        
        elif strategy_type == "momentum":
            # Momentum: stocks near 52W high
            if (fundamentals.get('pct_from_high') and fundamentals['pct_from_high'] >= -10 and
                fundamentals.get('trailing_pe') and fundamentals['trailing_pe'] <= benchmarks['pe'] * 1.5):
                passes_filter = True
        
        elif strategy_type == "quality":
            # Quality: good ROE, reasonable PE, positive upside
            if (fundamentals.get('roe') and fundamentals['roe'] > benchmarks['roe'] / 100 and
                fundamentals.get('trailing_pe') and fundamentals['trailing_pe'] <= benchmarks['pe'] * 1.2 and
                upside >= 5):
                passes_filter = True
        
        if not passes_filter:
            continue
        
        # Add to results
        result = {
            'Ticker': ticker,
            'Name': name,
            'Industry': industry,
            'Price': fundamentals['price'],
            'Fair Value': fair_value,
            'Upside %': upside,
            'PE Ratio': fundamentals['trailing_pe'],
            'PB Ratio': fundamentals['pb_ratio'],
            'ROE %': fundamentals['roe'] * 100 if fundamentals['roe'] else None,
            'Market Cap': fundamentals['market_cap'],
            'Cap Type': fundamentals['cap_type'],
            'From 52W High %': fundamentals['pct_from_high'],
            'From 52W Low %': fundamentals['pct_from_low'],
            'Beta': fundamentals['beta'],
            'Dividend Yield %': fundamentals['dividend_yield'] * 100 if fundamentals['dividend_yield'] else None
        }
        results.append(result)
        
        if len(results) >= max_results:
            break
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def search_stocks_by_name(query, max_results=50):
    """Search stocks by company name across all industries"""
    results = []
    query_lower = query.lower()
    
    for industry, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query_lower in name.lower() or query_lower in ticker.lower():
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'industry': industry
                })
                if len(results) >= max_results:
                    break
        if len(results) >= max_results:
            break
    
    return results

# ============================================================================
# INDIVIDUAL STOCK ANALYSIS
# ============================================================================

def analyze_individual_stock(ticker):
    """Analyze individual stock with industry benchmarks"""
    
    # Get stock info
    stock_info = get_stock_info(ticker)
    if not stock_info:
        return None, "Stock not found in database"
    
    # Get fundamentals
    fundamentals = get_stock_fundamentals(ticker)
    if not fundamentals:
        return None, "Unable to fetch stock data"
    
    # Get sector benchmarks
    industry = stock_info['category']
    sector = get_sector_for_industry(industry)
    benchmarks = SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other'])
    
    # Calculate fair value
    fair_value = calculate_fair_value(fundamentals, benchmarks)
    upside = ((fair_value - fundamentals['price']) / fundamentals['price']) * 100 if fair_value else 0
    
    analysis = {
        'ticker': ticker,
        'company': fundamentals['name'],
        'industry': industry,
        'sector': sector,
        'price': fundamentals['price'],
        'fair_value': fair_value,
        'upside': upside,
        'fundamentals': fundamentals,
        'benchmarks': benchmarks
    }
    
    return analysis, None

# ============================================================================
# MAIN STREAMLIT APPLICATION
# ============================================================================

def main():
    
    # Header
    st.markdown(f'''
    <div class="main-header">
        <h1>🎯 NYZTrade - Industry Stock Screener</h1>
        <h3>Professional Stock Screening Across {TOTAL_CATEGORIES} Indian Industries</h3>
        <p>Real Industry Benchmarks • {TOTAL_STOCKS:,} Stock Universe</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Stats row
    st.markdown(f'''
    <div class="stats-container">
        <div class="stat-card">
            <h3>{TOTAL_CATEGORIES}</h3>
            <p>Industries</p>
        </div>
        <div class="stat-card">
            <h3>{TOTAL_STOCKS:,}</h3>
            <p>Stocks</p>
        </div>
        <div class="stat-card">
            <h3>5</h3>
            <p>Strategies</p>
        </div>
        <div class="stat-card">
            <h3>Live</h3>
            <p>Data</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🔧 Analysis Controls")
    
    # Mode selection
    mode = st.sidebar.selectbox(
        "Choose Mode",
        ["🎯 Stock Screener", "📈 Individual Analysis", "📊 Industry Explorer"]
    )
    
    if mode == "🎯 Stock Screener":
        
        st.markdown("### 🎯 Industry-Based Stock Screener")
        
        # Industry selection
        industries = sorted(get_all_categories())
        selected_industry = st.sidebar.selectbox("Select Industry", industries)
        
        # Strategy selection  
        strategy_options = [
            ("undervalued", "🎯 Undervalued Stocks (15%+ upside)"),
            ("undervalued_supertrend", "📈 Undervalued + Strong Position"),
            ("undervalued_rsi_macd", "🔍 Undervalued + Momentum"),
            ("momentum", "🚀 Momentum Stocks"),
            ("quality", "💎 Quality Stocks")
        ]
        
        strategy_choice = st.sidebar.selectbox(
            "Screening Strategy",
            strategy_options,
            format_func=lambda x: x[1]
        )
        
        strategy_type = strategy_choice[0]
        strategy_name = strategy_choice[1]
        
        # Parameters
        max_results = st.sidebar.slider("Max Results", 10, 100, 30)
        
        # Run screener
        if st.sidebar.button("🚀 Run Screener", type="primary"):
            
            # Show industry info
            industry_stocks = get_stocks_by_category(selected_industry)
            sector = get_sector_for_industry(selected_industry)
            
            st.markdown(f'''
            <div class="highlight-box">
                <h3>📊 {strategy_name}</h3>
                <p><strong>Industry:</strong> {selected_industry}</p>
                <p><strong>Sector:</strong> {sector}</p>
                <p><strong>Universe:</strong> {len(industry_stocks):,} stocks</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Run screener
            with st.spinner(f"🔍 Screening {len(industry_stocks):,} stocks..."):
                results_df = run_industry_screener(selected_industry, strategy_type, max_results)
            
            if results_df.empty:
                st.warning(f"❌ No stocks found matching {strategy_name} criteria in {selected_industry}")
            else:
                # Display results
                st.markdown(f'''
                <div class="success-message">
                    ✅ Found <strong>{len(results_df)}</strong> opportunities in {selected_industry}<br>
                    🎯 Strategy: {strategy_name}
                </div>
                ''', unsafe_allow_html=True)
                
                # Sort results by upside
                results_df = results_df.sort_values('Upside %', ascending=False)
                
                # Format display
                display_df = results_df.copy()
                
                # Format currency columns
                for col in ['Price', 'Fair Value']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                # Format percentage columns
                for col in ['Upside %', 'ROE %', 'From 52W High %', 'From 52W Low %', 'Dividend Yield %']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else 'N/A')
                
                # Format ratio columns
                for col in ['PE Ratio', 'PB Ratio', 'Beta']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
                
                # Format market cap
                if 'Market Cap' in display_df.columns:
                    display_df['Market Cap'] = display_df['Market Cap'].apply(
                        lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A'
                    )
                
                # Select key columns for display
                display_columns = ['Ticker', 'Name', 'Price', 'Fair Value', 'Upside %', 'PE Ratio', 'From 52W High %', 'Cap Type']
                
                # Display table
                st.dataframe(
                    display_df[display_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=min(600, len(display_df) * 35 + 100)
                )
                
                # Download CSV
                csv = results_df.to_csv(index=False)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"NYZTrade_{selected_industry.replace(' ', '_')}_{strategy_type}_{timestamp}.csv"
                
                st.download_button(
                    f"📥 Download Results ({len(results_df)} stocks)",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
    
    elif mode == "📈 Individual Analysis":
        
        st.markdown("### 📈 Individual Stock Analysis")
        
        # Stock selection methods
        st.sidebar.subheader("Stock Selection")
        
        input_method = st.sidebar.radio(
            "Input Method",
            ["🔍 Search by Name", "✏️ Direct Ticker", "📋 Browse by Industry"]
        )
        
        selected_ticker = None
        
        if input_method == "🔍 Search by Name":
            search_query = st.sidebar.text_input("Search Company", placeholder="e.g., Reliance, TCS, HDFC")
            
            if search_query and len(search_query) >= 2:
                search_results = search_stocks_by_name(search_query, 15)
                if search_results:
                    options = [f"{r['ticker']} - {r['name']}" for r in search_results]
                    selected = st.sidebar.selectbox("Select Stock", [""] + options)
                    if selected:
                        selected_ticker = selected.split(" - ")[0]
                else:
                    st.sidebar.info("No stocks found")
        
        elif input_method == "✏️ Direct Ticker":
            selected_ticker = st.sidebar.text_input("Enter Ticker", placeholder="e.g., RELIANCE.NS").upper()
        
        elif input_method == "📋 Browse by Industry":
            browse_industry = st.sidebar.selectbox("Select Industry", [""] + sorted(get_all_categories()))
            if browse_industry:
                industry_stocks = get_stocks_by_category(browse_industry)
                stock_options = [f"{ticker} - {name}" for ticker, name in industry_stocks.items()]
                selected_stock = st.sidebar.selectbox("Select Stock", [""] + sorted(stock_options))
                if selected_stock:
                    selected_ticker = selected_stock.split(" - ")[0]
        
        # Analyze button
        if selected_ticker and st.sidebar.button("🚀 Analyze", type="primary"):
            
            with st.spinner(f"Analyzing {selected_ticker}..."):
                analysis, error = analyze_individual_stock(selected_ticker)
            
            if error:
                st.error(f"❌ {error}")
            elif analysis:
                # Display analysis
                st.markdown(f"# {analysis['company']}")
                st.markdown(f"**{analysis['ticker']} • {analysis['industry']} • {analysis['sector']}**")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"₹{analysis['price']:,.2f}")
                
                with col2:
                    if analysis['fair_value']:
                        upside_delta = f"{analysis['upside']:+.1f}%"
                        delta_color = "normal" if analysis['upside'] > 0 else "inverse"
                        st.metric(
                            "Fair Value",
                            f"₹{analysis['fair_value']:,.2f}",
                            delta=upside_delta,
                            delta_color=delta_color
                        )
                    else:
                        st.metric("Fair Value", "N/A")
                
                with col3:
                    # Recommendation based on upside
                    if analysis['upside'] > 25:
                        rec = "🚀 Strong Buy"
                    elif analysis['upside'] > 15:
                        rec = "✅ Buy"
                    elif analysis['upside'] > 0:
                        rec = "📊 Hold"
                    else:
                        rec = "⚠️ Avoid"
                    st.metric("Recommendation", rec)
                
                with col4:
                    # 52-week position
                    if analysis['fundamentals']['pct_from_high'] is not None:
                        range_pos = 100 + analysis['fundamentals']['pct_from_high']
                        pos_emoji = "🟢" if range_pos > 80 else "🟡" if range_pos > 60 else "🟠" if range_pos > 40 else "🔴"
                        st.metric("52W Position", f"{pos_emoji} {range_pos:.0f}%")
                    else:
                        st.metric("52W Position", "N/A")
                
                st.markdown("---")
                
                # Detailed metrics in tabs
                tab1, tab2, tab3 = st.tabs(["📊 Fundamentals", "📈 Performance", "💼 Details"])
                
                with tab1:
                    col1, col2, col3 = st.columns(3)
                    
                    fund = analysis['fundamentals']
                    bench = analysis['benchmarks']
                    
                    with col1:
                        pe = fund['trailing_pe']
                        if pe:
                            pe_vs_sector = pe - bench['pe']
                            st.metric(
                                "PE Ratio",
                                f"{pe:.2f}x",
                                delta=f"{pe_vs_sector:+.1f}x vs sector",
                                delta_color="inverse" if pe_vs_sector > 0 else "normal"
                            )
                        else:
                            st.metric("PE Ratio", "N/A")
                    
                    with col2:
                        pb = fund['pb_ratio']
                        if pb:
                            pb_vs_sector = pb - bench['pb']
                            st.metric(
                                "PB Ratio",
                                f"{pb:.2f}x",
                                delta=f"{pb_vs_sector:+.1f}x vs sector",
                                delta_color="inverse" if pb_vs_sector > 0 else "normal"
                            )
                        else:
                            st.metric("PB Ratio", "N/A")
                    
                    with col3:
                        roe = fund['roe']
                        if roe:
                            roe_pct = roe * 100
                            roe_vs_sector = roe_pct - bench['roe']
                            st.metric(
                                "ROE",
                                f"{roe_pct:.1f}%",
                                delta=f"{roe_vs_sector:+.1f}pp vs sector",
                                delta_color="normal" if roe_vs_sector > 0 else "inverse"
                            )
                        else:
                            st.metric("ROE", "N/A")
                
                with tab2:
                    fund = analysis['fundamentals']
                    if fund['pct_from_high'] is not None:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("From 52W High", f"{fund['pct_from_high']:+.1f}%")
                            st.metric("From 52W Low", f"{fund['pct_from_low']:+.1f}%")
                        
                        with col2:
                            # Visual 52-week position
                            current_position = ((fund['price'] - fund['52w_low']) / (fund['52w_high'] - fund['52w_low'])) * 100
                            st.markdown("**52-Week Position**")
                            st.progress(current_position / 100)
                            st.caption(f"{current_position:.1f}% of range")
                            
                            if current_position > 80:
                                st.success("🟢 Very Strong")
                            elif current_position > 60:
                                st.info("🟡 Strong")
                            elif current_position > 40:
                                st.warning("🟠 Moderate")
                            else:
                                st.error("🔴 Weak")
                    else:
                        st.info("52-week data not available")
                
                with tab3:
                    fund = analysis['fundamentals']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Market Cap", f"₹{fund['market_cap']/10000000:,.0f} Cr" if fund['market_cap'] else "N/A")
                        st.metric("Beta", f"{fund['beta']:.2f}" if fund['beta'] else "N/A")
                        st.metric("Dividend Yield", f"{fund['dividend_yield']*100:.2f}%" if fund['dividend_yield'] else "N/A")
                    
                    with col2:
                        st.metric("Profit Margin", f"{fund['profit_margin']*100:.1f}%" if fund['profit_margin'] else "N/A")
                        st.metric("Debt/Equity", f"{fund['debt_to_equity']:.2f}" if fund['debt_to_equity'] else "N/A")
                        st.metric("Volume", f"{fund['volume']:,}" if fund['volume'] else "N/A")
    
    elif mode == "📊 Industry Explorer":
        
        st.markdown("### 📊 Industry Explorer")
        
        # Show industry statistics
        industry_counts = {industry: len(stocks) for industry, stocks in INDIAN_STOCKS.items()}
        top_industries = dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:12])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Top Industries by Stock Count")
            
            # Create bar chart
            industries_df = pd.DataFrame(list(top_industries.items()), columns=['Industry', 'Stock Count'])
            fig = px.bar(
                industries_df, 
                x='Stock Count', 
                y='Industry',
                orientation='h',
                height=450,
                color='Stock Count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Database Statistics")
            
            st.metric("Total Industries", f"{TOTAL_CATEGORIES}")
            st.metric("Total Stocks", f"{TOTAL_STOCKS:,}")
            st.metric("Avg per Industry", f"{TOTAL_STOCKS // TOTAL_CATEGORIES}")
            
            # Sector distribution
            st.markdown("#### Sector Breakdown")
            sectors_count = {}
            for industry in get_all_categories():
                sector = get_sector_for_industry(industry)
                sectors_count[sector] = sectors_count.get(sector, 0) + 1
            
            for sector, count in sorted(sectors_count.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{sector}: {count}")
        
        # Specific industry exploration
        st.markdown("---")
        st.markdown("#### 🔍 Explore Industry Details")
        
        explore_industry = st.selectbox("Select Industry", sorted(get_all_categories()))
        
        if explore_industry:
            industry_stocks = get_stocks_by_category(explore_industry)
            sector = get_sector_for_industry(explore_industry)
            
            st.info(f"**{explore_industry}** • Sector: {sector} • {len(industry_stocks)} stocks")
            
            # Show stocks in expandable section
            if st.expander(f"View all {len(industry_stocks)} stocks"):
                stocks_df = pd.DataFrame(list(industry_stocks.items()), columns=['Ticker', 'Company'])
                st.dataframe(stocks_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
