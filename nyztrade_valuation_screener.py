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
        "MRF.NS": "MRF Limited"
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
        "NAVINFLUOR.NS": "Navin Fluorine International Limited"
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
    page_title="NYZTrade - Industry-Based Stock Screener", 
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
    
    .industry-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(129, 140, 248, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
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
# INDUSTRY CATEGORIZATION AND MAPPING
# ============================================================================

def get_industry_stock_count():
    """Get count of stocks in each industry"""
    return {industry: len(stocks) for industry, stocks in INDIAN_STOCKS.items()}

def get_top_industries(top_n=20):
    """Get top N industries by stock count"""
    counts = get_industry_stock_count()
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n])

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

# Sector grouping for broader analysis
INDUSTRY_TO_SECTOR = {
    # Financial Services
    "Asset Management": "Financial Services",
    "Banks - Regional": "Financial Services",
    "Credit Services": "Financial Services", 
    "Financial Services": "Financial Services",
    "Insurance - Life": "Financial Services",
    "Insurance - Property & Casualty": "Financial Services",
    "Investment Brokerage - National": "Financial Services",
    "Money Center Banks": "Financial Services",
    "Mortgage Investment": "Financial Services",
    
    # Technology
    "Business Software & Services": "Technology",
    "Communication Technology": "Technology",
    "Computer Processing Hardware": "Technology",
    "Information Technology Services": "Technology",
    "Technical & System Software": "Technology",
    "Wireless Communications": "Technology",
    
    # Healthcare & Pharma
    "Biotechnology": "Healthcare & Pharma",
    "Drug Manufacturers - Major": "Healthcare & Pharma",
    "Drug Manufacturers - Other": "Healthcare & Pharma", 
    "Drugs - Generic": "Healthcare & Pharma",
    "Medical Services": "Healthcare & Pharma",
    "Medical Laboratories & Research": "Healthcare & Pharma",
    
    # Industrial & Manufacturing
    "Aerospace/Defense - Major Diversified": "Industrial & Manufacturing",
    "Aluminum": "Industrial & Manufacturing",
    "Diversified Electronics": "Industrial & Manufacturing",
    "Diversified Machinery": "Industrial & Manufacturing",
    "Farm & Construction Machinery": "Industrial & Manufacturing",
    "Heavy Construction": "Industrial & Manufacturing",
    "Industrial Products": "Industrial & Manufacturing",
    "Steel & Iron": "Industrial & Manufacturing",
    "Tools & Hardware": "Industrial & Manufacturing",
    
    # Energy & Utilities
    "Electric Utilities": "Energy & Utilities",
    "Gas Utilities": "Energy & Utilities",
    "Oil & Gas Operations": "Energy & Utilities",
    "Oil & Gas Refining & Marketing": "Energy & Utilities",
    "Renewable Energy": "Energy & Utilities",
    
    # Consumer & Retail
    "Apparel Stores": "Consumer & Retail",
    "Auto Manufacturers - Major": "Consumer & Retail",
    "Auto Parts": "Consumer & Retail", 
    "Food - Major Diversified": "Consumer & Retail",
    "Jewelry Stores": "Consumer & Retail",
    "Lodging": "Consumer & Retail",
    "Personal Products": "Consumer & Retail",
    "Restaurants": "Consumer & Retail",
    "Retail - Apparel & Accessories": "Consumer & Retail",
    "Tobacco Products, Other": "Consumer & Retail",
    
    # Materials & Chemicals
    "Agricultural Chemicals": "Materials & Chemicals",
    "Cement & Aggregates": "Materials & Chemicals",
    "Chemicals - Major Diversified": "Materials & Chemicals",
    "Paper & Paper Products": "Materials & Chemicals",
    "Rubber & Plastics": "Materials & Chemicals",
    
    # Transportation
    "Air Delivery & Freight Services": "Transportation",
    "Air Services, Other": "Transportation",
    "Major Airlines": "Transportation",
    "Shipping": "Transportation",
    "Transportation Services": "Transportation",
    "Trucking": "Transportation",
    
    # Real Estate & Construction
    "General Contractors": "Real Estate & Construction",
    "Real Estate Development": "Real Estate & Construction",
    
    # Textiles
    "Textile Industrial": "Textiles",
    "Textile - Apparel Clothing": "Textiles"
}

def get_sector_for_industry(industry):
    """Get broad sector for a given industry"""
    return INDUSTRY_TO_SECTOR.get(industry, "Other")

def get_industries_by_sector():
    """Group industries by sector"""
    sectors = {}
    for industry in get_all_categories():
        sector = get_sector_for_industry(industry)
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(industry)
    return sectors

# Default benchmarks by sector
SECTOR_BENCHMARKS = {
    'Financial Services': {'pe': 18.0, 'ev_ebitda': 12.0, 'pb': 1.5, 'roe': 15.0},
    'Technology': {'pe': 25.0, 'ev_ebitda': 15.0, 'pb': 3.5, 'roe': 20.0},
    'Healthcare & Pharma': {'pe': 28.0, 'ev_ebitda': 14.0, 'pb': 3.0, 'roe': 18.0},
    'Industrial & Manufacturing': {'pe': 22.0, 'ev_ebitda': 12.0, 'pb': 2.0, 'roe': 14.0},
    'Energy & Utilities': {'pe': 15.0, 'ev_ebitda': 8.0, 'pb': 1.2, 'roe': 12.0},
    'Consumer & Retail': {'pe': 30.0, 'ev_ebitda': 14.0, 'pb': 2.5, 'roe': 16.0},
    'Materials & Chemicals': {'pe': 18.0, 'ev_ebitda': 10.0, 'pb': 1.8, 'roe': 13.0},
    'Real Estate & Construction': {'pe': 25.0, 'ev_ebitda': 18.0, 'pb': 1.5, 'roe': 12.0},
    'Transportation': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 1.8, 'roe': 14.0},
    'Textiles': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 1.5, 'roe': 15.0},
    'Other': {'pe': 20.0, 'ev_ebitda': 12.0, 'pb': 2.0, 'roe': 15.0}
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
            hist = stock.history(period="1y")
            
            if not info or hist.empty:
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
            'forward_pe': info.get('forwardPE'),
            'pb_ratio': info.get('priceToBook'),
            'ps_ratio': info.get('priceToSalesTrailing12Months'),
            'ev_ebitda': info.get('enterpriseToEbitda'),
            'roe': info.get('returnOnEquity'),
            'roa': info.get('returnOnAssets'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'profit_margin': info.get('profitMargins'),
            'book_value': info.get('bookValue'),
            'debt_to_equity': info.get('debtToEquity'),
            '52w_high': info.get('fiftyTwoWeekHigh'),
            '52w_low': info.get('fiftyTwoWeekLow'),
            'volume': info.get('volume'),
            'avg_volume': info.get('averageVolume'),
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
# SIMPLE VALUATION LOGIC
# ============================================================================

def calculate_simple_fair_value(fundamentals, sector_benchmarks):
    """Calculate a simple fair value estimate"""
    if not fundamentals or not fundamentals.get('trailing_pe'):
        return None
    
    # Simple PE-based fair value
    sector_pe = sector_benchmarks.get('pe', 20)
    current_pe = fundamentals['trailing_pe']
    
    if current_pe and current_pe > 0:
        # If PE is reasonable, calculate fair value
        fair_pe_ratio = sector_pe / current_pe
        fair_value = fundamentals['price'] * fair_pe_ratio
        return fair_value
    
    return None

# ============================================================================
# MAIN STREAMLIT APPLICATION
# ============================================================================

def main():
    
    # Header
    st.markdown(f'''
    <div class="main-header">
        <h1>🎯 NYZTrade - Industry Stock Screener</h1>
        <h3>Professional Stock Analysis Across {TOTAL_CATEGORIES} Indian Industries</h3>
        <p>Industry-Specific Analysis • {TOTAL_STOCKS:,} Stock Universe</p>
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
            <h3>Live</h3>
            <p>Data</p>
        </div>
        <div class="stat-card">
            <h3>Real-Time</h3>
            <p>Analysis</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🔧 Analysis Controls")
    
    # Mode selection
    mode = st.sidebar.selectbox(
        "Analysis Mode",
        ["🎯 Industry Explorer", "📈 Stock Analysis", "📊 Quick Search"]
    )
    
    if mode == "🎯 Industry Explorer":
        
        st.markdown("### 🔍 Industry Explorer")
        
        # Show top industries by stock count
        top_industries = get_top_industries(15)
        
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
                title="Stock Count by Industry",
                height=500,
                color='Stock Count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Industry Statistics")
            
            # Show stats
            st.metric("Total Industries", f"{TOTAL_CATEGORIES}")
            st.metric("Total Stocks", f"{TOTAL_STOCKS:,}")
            st.metric("Avg Stocks/Industry", f"{TOTAL_STOCKS // TOTAL_CATEGORIES}")
            
            # Show sector distribution
            sectors_count = {}
            for industry in get_all_categories():
                sector = get_sector_for_industry(industry)
                sectors_count[sector] = sectors_count.get(sector, 0) + 1
            
            st.markdown("#### Sector Distribution")
            for sector, count in sorted(sectors_count.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{sector}: {count} industries")
        
        # Industry details
        st.markdown("---")
        st.markdown("#### 🔍 Explore Specific Industry")
        
        selected_explore_industry = st.selectbox("Select Industry to Explore", sorted(get_all_categories()))
        
        if selected_explore_industry:
            industry_stocks = get_stocks_by_category(selected_explore_industry)
            sector = get_sector_for_industry(selected_explore_industry)
            
            st.markdown(f'''
            <div class="industry-card">
                <h4>📊 {selected_explore_industry}</h4>
                <p><strong>Sector:</strong> {sector}</p>
                <p><strong>Total Stocks:</strong> {len(industry_stocks):,}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Show all stocks in the industry
            if st.expander(f"📋 All {len(industry_stocks)} Stocks in {selected_explore_industry}"):
                stocks_df = pd.DataFrame(list(industry_stocks.items()), columns=['Ticker', 'Company Name'])
                st.dataframe(stocks_df, use_container_width=True, hide_index=True)
    
    elif mode == "📈 Stock Analysis":
        
        # Stock selection
        st.sidebar.subheader("📍 Stock Selection")
        
        input_method = st.sidebar.radio(
            "Input Method",
            ["🔍 Search by Name", "✏️ Direct Ticker", "📋 Browse by Industry"]
        )
        
        selected_ticker = None
        
        if input_method == "🔍 Search by Name":
            search_query = st.sidebar.text_input("Search Company Name", placeholder="e.g., Reliance, TCS, HDFC")
            
            if search_query and len(search_query) >= 2:
                search_results = search_stocks_by_name(search_query, 20)
                if search_results:
                    options = [f"{r['ticker']} - {r['name']}" for r in search_results]
                    selected = st.sidebar.selectbox("Select Stock", [""] + options)
                    if selected:
                        selected_ticker = selected.split(" - ")[0]
                else:
                    st.sidebar.info("No stocks found")
        
        elif input_method == "✏️ Direct Ticker":
            selected_ticker = st.sidebar.text_input("Enter Ticker", placeholder="e.g., RELIANCE.NS, TCS.NS").upper()
        
        elif input_method == "📋 Browse by Industry":
            browse_industry = st.sidebar.selectbox("Select Industry", [""] + sorted(get_all_categories()))
            if browse_industry:
                industry_stocks = get_stocks_by_category(browse_industry)
                stock_options = [f"{ticker} - {name}" for ticker, name in industry_stocks.items()]
                selected_stock = st.sidebar.selectbox("Select Stock", [""] + sorted(stock_options))
                if selected_stock:
                    selected_ticker = selected_stock.split(" - ")[0]
        
        # Analyze button
        if selected_ticker and st.sidebar.button("🚀 Analyze Stock", type="primary"):
            
            with st.spinner(f"📊 Analyzing {selected_ticker}..."):
                
                # Get stock info and fundamentals
                stock_info = get_stock_info(selected_ticker)
                if not stock_info:
                    st.error("❌ Stock not found in database")
                    return
                
                fundamentals = get_stock_fundamentals(selected_ticker)
                if not fundamentals:
                    st.error("❌ Unable to fetch stock data")
                    return
                
                # Get sector benchmarks
                industry = stock_info['category']
                sector = get_sector_for_industry(industry)
                sector_benchmarks = SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other'])
                
                # Calculate fair value
                fair_value = calculate_simple_fair_value(fundamentals, sector_benchmarks)
                upside = ((fair_value - fundamentals['price']) / fundamentals['price']) * 100 if fair_value else 0
            
            # Display analysis
            st.markdown(f"# {fundamentals['name']}")
            st.markdown(f"**{selected_ticker} • {industry} • {sector} • {fundamentals['cap_type']} Cap**")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", f"₹{fundamentals['price']:,.2f}")
            
            with col2:
                if fair_value:
                    delta_color = "normal" if upside > 0 else "inverse"
                    st.metric(
                        "Est. Fair Value",
                        f"₹{fair_value:,.2f}",
                        delta=f"{upside:+.1f}% potential",
                        delta_color=delta_color
                    )
                else:
                    st.metric("Est. Fair Value", "N/A")
            
            with col3:
                # Simple recommendation
                if upside > 20:
                    rec = "🚀 Strong Buy"
                elif upside > 10:
                    rec = "✅ Buy"
                elif upside > 0:
                    rec = "📊 Hold"
                else:
                    rec = "⚠️ Caution"
                st.metric("Recommendation", rec)
            
            with col4:
                # Position in 52-week range
                if fundamentals['pct_from_high'] is not None:
                    range_pos = 100 + fundamentals['pct_from_high']
                    pos_emoji = "🟢" if range_pos > 75 else "🟡" if range_pos > 50 else "🟠" if range_pos > 25 else "🔴"
                    st.metric("52W Position", f"{pos_emoji} {range_pos:.0f}%")
                else:
                    st.metric("52W Position", "N/A")
            
            st.markdown("---")
            
            # Detailed metrics in tabs
            tab1, tab2, tab3 = st.tabs(["📊 Fundamentals", "📈 Performance", "💼 Details"])
            
            with tab1:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("PE Ratio", f"{fundamentals['trailing_pe']:.2f}x" if fundamentals['trailing_pe'] else "N/A")
                    st.caption(f"Sector Avg: {sector_benchmarks['pe']:.1f}x")
                
                with col2:
                    st.metric("PB Ratio", f"{fundamentals['pb_ratio']:.2f}x" if fundamentals['pb_ratio'] else "N/A")
                    st.caption(f"Sector Avg: {sector_benchmarks['pb']:.1f}x")
                
                with col3:
                    if fundamentals['roe']:
                        roe_pct = fundamentals['roe'] * 100
                        st.metric("ROE", f"{roe_pct:.1f}%")
                        st.caption(f"Sector Avg: {sector_benchmarks['roe']:.1f}%")
                    else:
                        st.metric("ROE", "N/A")
            
            with tab2:
                if fundamentals['pct_from_high'] is not None:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("From 52W High", f"{fundamentals['pct_from_high']:+.1f}%")
                        st.metric("From 52W Low", f"{fundamentals['pct_from_low']:+.1f}%")
                    
                    with col2:
                        # Progress bar for 52W position
                        current_position = ((fundamentals['price'] - fundamentals['52w_low']) / (fundamentals['52w_high'] - fundamentals['52w_low'])) * 100
                        st.markdown("**52-Week Range Position**")
                        st.progress(current_position / 100)
                        st.caption(f"Position: {current_position:.1f}%")
                        
                        if current_position > 80:
                            st.success("🟢 Near High")
                        elif current_position > 60:
                            st.info("🟡 Upper Range")
                        elif current_position > 40:
                            st.info("🟡 Mid Range")
                        else:
                            st.warning("🟠 Lower Range")
                else:
                    st.info("52-week data not available")
            
            with tab3:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Market Cap", f"₹{fundamentals['market_cap']/10000000:,.0f} Cr" if fundamentals['market_cap'] else "N/A")
                    st.metric("Beta", f"{fundamentals['beta']:.2f}" if fundamentals['beta'] else "N/A")
                
                with col2:
                    st.metric("Dividend Yield", f"{fundamentals['dividend_yield']*100:.2f}%" if fundamentals['dividend_yield'] else "N/A")
                    st.metric("Profit Margin", f"{fundamentals['profit_margin']*100:.1f}%" if fundamentals['profit_margin'] else "N/A")
    
    elif mode == "📊 Quick Search":
        
        st.markdown("### 🔍 Quick Stock Search")
        
        search_query = st.text_input("Search for stocks by name or ticker", placeholder="e.g., Reliance, TCS, HDFC, INFY")
        
        if search_query and len(search_query) >= 2:
            results = search_stocks_by_name(search_query, 30)
            
            if results:
                st.markdown(f"**Found {len(results)} stocks matching '{search_query}'**")
                
                # Create DataFrame
                results_df = pd.DataFrame(results)
                results_df['Sector'] = results_df['industry'].apply(get_sector_for_industry)
                
                # Display results
                st.dataframe(
                    results_df[['ticker', 'name', 'industry', 'Sector']].rename(columns={
                        'ticker': 'Ticker',
                        'name': 'Company Name',
                        'industry': 'Industry'
                    }),
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Show sector distribution
                sector_counts = results_df['Sector'].value_counts()
                if len(sector_counts) > 1:
                    st.markdown("#### Sector Distribution in Results")
                    
                    fig = px.pie(
                        values=sector_counts.values,
                        names=sector_counts.index,
                        title=f"Sector Distribution for '{search_query}'"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
            else:
                st.info(f"No stocks found matching '{search_query}'. Try a different search term.")

if __name__ == "__main__":
    main()
