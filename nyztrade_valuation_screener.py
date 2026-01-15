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
    page_title="NYZTrade Sector Screener", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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
                <p style="color: #94a3b8;">Complete Stock Analysis Platform</p>
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
# DATABASE MANAGEMENT
# ============================================================================
@st.cache_data
def load_stocks_database(uploaded_file=None):
    """Load stocks database from uploaded CSV or default file"""
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['Ticker', 'Name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Try common column variations
                column_mapping = {
                    'Symbol': 'Ticker',
                    'SYMBOL': 'Ticker',
                    'Ticker Symbol': 'Ticker',
                    'Company Name': 'Name',
                    'Company': 'Name',
                    'COMPANY NAME': 'Name'
                }
                
                # Attempt to map columns
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns and new_col not in df.columns:
                        df[new_col] = df[old_col]
                
                # Check again
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ CSV file missing required columns: {missing_columns}")
                    return None
        else:
            # Try to load from the categorized file in outputs
            try:
                df = pd.read_csv('/mnt/user-data/outputs/stocks_universe_categorized_enhanced.csv')
            except:
                st.error("❌ Default database not found. Please upload a CSV file.")
                return None
        
        # Clean and prepare data
        df = df.dropna(subset=['Ticker', 'Name'])
        df['Ticker'] = df['Ticker'].astype(str).str.strip().str.upper()
        df['Name'] = df['Name'].astype(str).str.strip()
        
        # Add Category Name if missing
        if 'Category Name' not in df.columns:
            df['Category Name'] = 'Miscellaneous'
        else:
            df['Category Name'] = df['Category Name'].fillna('Miscellaneous')
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        if len(df) == 0:
            st.warning("⚠️ No valid data found in file")
            return None
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading database: {str(e)}")
        return None

# ============================================================================
# SECTOR MAPPING & BENCHMARKS
# ============================================================================
def get_sector_mapping():
    """Map categories to broader sectors"""
    return {
        'Financial Services': [
            'Money Center Banks', 'Financial Services', 'Credit Services',
            'Investment Brokerage - National', 'Mortgage Investment', 'Asset Management'
        ],
        'Technology': [
            'Business Software & Services', 'Information Technology Services',
            'Financial Technology', 'Communication Technology'
        ],
        'Healthcare & Pharma': [
            'Drugs - Generic', 'Drug Manufacturers - Major', 'Medical Services',
            'Biotechnology', 'Medical Diagnostics'
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
        'Textiles': [
            'Textile Industrial', 'Textile - Apparel Clothing'
        ]
    }

# Industry benchmarks for fair value calculations
INDUSTRY_BENCHMARKS = {
    'Financial Services': {'pe': 18, 'ev_ebitda': 12},
    'Technology': {'pe': 25, 'ev_ebitda': 15},
    'Healthcare & Pharma': {'pe': 28, 'ev_ebitda': 14},
    'Industrial & Manufacturing': {'pe': 22, 'ev_ebitda': 12},
    'Energy & Utilities': {'pe': 15, 'ev_ebitda': 8},
    'Consumer & Retail': {'pe': 30, 'ev_ebitda': 14},
    'Materials & Chemicals': {'pe': 18, 'ev_ebitda': 10},
    'Real Estate & Construction': {'pe': 25, 'ev_ebitda': 18},
    'Transportation': {'pe': 20, 'ev_ebitda': 12},
    'Textiles': {'pe': 20, 'ev_ebitda': 12},
    'Other': {'pe': 20, 'ev_ebitda': 12}
}

def create_sector_analysis(df):
    """Create sector-wise analysis of the stock universe"""
    sector_mapping = get_sector_mapping()
    
    # Create reverse mapping
    category_to_sector = {}
    for sector, categories in sector_mapping.items():
        for category in categories:
            category_to_sector[category] = sector
    
    # Add sector column to dataframe
    df['Sector'] = df['Category Name'].map(category_to_sector).fillna('Other')
    
    # Create sector summary
    sector_summary = df.groupby('Sector').agg({
        'Ticker': 'count',
        'Category Name': 'nunique'
    }).reset_index()
    
    sector_summary.columns = ['Sector', 'Stock Count', 'Sub-Categories']
    sector_summary = sector_summary.sort_values('Stock Count', ascending=False)
    
    return df, sector_summary

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
        time.sleep(0.05)  # Minimal rate limiting
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
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Other'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        fair_values = []
        
        # PE-based fair value
        if trailing_pe and trailing_pe > 0 and trailing_eps and price:
            # Use conservative approach: blend industry PE with historical PE
            historical_pe = trailing_pe * 0.9  # 10% discount to current PE
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
            if 0 < current_ev_ebitda < 100:  # Reasonable EV/EBITDA range
                # Use conservative approach
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
# INDIVIDUAL STOCK ANALYSIS
# ============================================================================
def analyze_individual_stock(ticker, sector):
    """Detailed analysis of individual stock"""
    info, error = fetch_stock_data(ticker)
    
    if error or not info:
        return None, error
    
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
# ENHANCED SECTOR SCREENING
# ============================================================================
def run_sector_screening(df, selected_sectors):
    """Run comprehensive sector-wise screening with ALL stocks"""
    
    sector_results = {}
    overall_progress = st.progress(0)
    status_text = st.empty()
    
    total_sectors = len(selected_sectors)
    
    for sector_idx, sector in enumerate(selected_sectors):
        status_text.text(f"Processing {sector}...")
        
        # Get sector mapping
        sector_mapping = get_sector_mapping()
        categories = sector_mapping.get(sector, [])
        
        # Filter stocks for this sector - ENSURE ALL ARE INCLUDED
        sector_stocks = df[df['Category Name'].isin(categories)].copy()
        
        st.info(f"Found {len(sector_stocks)} stocks in {sector} sector")
        
        if len(sector_stocks) == 0:
            continue
        
        sector_data = []
        total_stocks = len(sector_stocks)
        processed_count = 0
        
        for stock_idx, (_, row) in enumerate(sector_stocks.iterrows()):
            # Update progress more frequently
            if stock_idx % 10 == 0:  # Update every 10 stocks
                stock_progress = stock_idx / total_stocks
                overall_sector_progress = (sector_idx + stock_progress) / total_sectors
                overall_progress.progress(min(overall_sector_progress, 1.0))
                status_text.text(f"Processing {sector}: {stock_idx+1}/{total_stocks} - {row['Ticker']}")
            
            # Fetch stock data - NO SKIPPING
            info, error = fetch_stock_data(row['Ticker'])
            processed_count += 1
            
            # Process even if there's an error - record what we can
            try:
                if not error and info:
                    price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
                    market_cap = info.get('marketCap', 0)
                    pe_ratio = info.get('trailingPE', 0)
                    pb_ratio = info.get('priceToBook', 0)
                    dividend_yield = info.get('dividendYield', 0)
                    beta = info.get('beta', 0)
                    
                    # 52-week data
                    high_52w = info.get('fiftyTwoWeekHigh', 0)
                    low_52w = info.get('fiftyTwoWeekLow', 0)
                    
                    pct_from_high = None
                    pct_from_low = None
                    
                    if price and high_52w and low_52w and high_52w > low_52w:
                        pct_from_high = ((high_52w - price) / high_52w * 100)
                        pct_from_low = ((price - low_52w) / low_52w * 100)
                    
                    # Calculate fair value and upside
                    valuation_data = calculate_fair_value_and_upside(info, sector)
                    
                    sector_data.append({
                        'Ticker': row['Ticker'],
                        'Name': row['Name'],
                        'Category': row['Category Name'],
                        'Price': price,
                        'Market Cap': market_cap,
                        'Cap Type': categorize_market_cap(market_cap),
                        'PE Ratio': pe_ratio,
                        'PB Ratio': pb_ratio,
                        'Fair Value': valuation_data['avg_fair_value'],
                        'Upside %': valuation_data['avg_upside'],
                        'Dividend Yield': dividend_yield * 100 if dividend_yield else 0,
                        'Beta': beta,
                        '52W High': high_52w,
                        '52W Low': low_52w,
                        'From 52W High %': -pct_from_high if pct_from_high else None,
                        'From 52W Low %': pct_from_low if pct_from_low else None,
                        'Status': 'Success'
                    })
                else:
                    # Still record the stock even if data fetch failed
                    sector_data.append({
                        'Ticker': row['Ticker'],
                        'Name': row['Name'],
                        'Category': row['Category Name'],
                        'Price': None,
                        'Market Cap': None,
                        'Cap Type': 'Unknown',
                        'PE Ratio': None,
                        'PB Ratio': None,
                        'Fair Value': None,
                        'Upside %': None,
                        'Dividend Yield': None,
                        'Beta': None,
                        '52W High': None,
                        '52W Low': None,
                        'From 52W High %': None,
                        'From 52W Low %': None,
                        'Status': f'Error: {error}' if error else 'No Data'
                    })
            except Exception as e:
                # Record failed stocks too
                sector_data.append({
                    'Ticker': row['Ticker'],
                    'Name': row['Name'],
                    'Category': row['Category Name'],
                    'Price': None,
                    'Market Cap': None,
                    'Cap Type': 'Unknown',
                    'PE Ratio': None,
                    'PB Ratio': None,
                    'Fair Value': None,
                    'Upside %': None,
                    'Dividend Yield': None,
                    'Beta': None,
                    '52W High': None,
                    '52W Low': None,
                    'From 52W High %': None,
                    'From 52W Low %': None,
                    'Status': f'Exception: {str(e)[:50]}'
                })
        
        if sector_data:
            sector_results[sector] = pd.DataFrame(sector_data)
            st.success(f"✅ {sector}: Processed {len(sector_data)}/{total_stocks} stocks")
        
        # Update overall progress for completed sector
        overall_progress.progress(min((sector_idx + 1) / total_sectors, 1.0))
    
    overall_progress.empty()
    status_text.empty()
    
    return sector_results

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.markdown('''
<div class="main-header">
    NYZTRADE COMPLETE STOCK ANALYZER
</div>
<div class="sub-header">
    🎯 Complete Sector Analysis | Individual Stock Valuation | Fair Value Calculations
</div>
''', unsafe_allow_html=True)

# ============================================================================
# DATABASE LOADING
# ============================================================================
st.markdown('<div class="section-header">📂 Database Management</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📤 Upload Your Stock Database (CSV)", 
    type=['csv'],
    help="Upload a CSV file with columns: Ticker, Name, Category Name"
)

# Load database
if uploaded_file is not None:
    df = load_stocks_database(uploaded_file)
    if df is not None:
        st.session_state.stocks_df = df
        st.markdown('<div class="success-message">✅ Database uploaded successfully!</div>', unsafe_allow_html=True)
elif 'stocks_df' not in st.session_state:
    df = load_stocks_database()
    if df is not None:
        st.session_state.stocks_df = df
        st.markdown('<div class="success-message">✅ Default database loaded!</div>', unsafe_allow_html=True)
    else:
        st.error("❌ No database available. Please upload a CSV file.")
        st.stop()
else:
    df = st.session_state.stocks_df

# Create sector analysis
df, sector_summary = create_sector_analysis(df)

# Database statistics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{len(df):,}</div>
        <div style="color: #94a3b8;">📊 Total Stocks</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    sectors = len(sector_summary)
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{sectors}</div>
        <div style="color: #94a3b8;">🏢 Sectors</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    categories = df['Category Name'].nunique()
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{categories}</div>
        <div style="color: #94a3b8;">🏷️ Categories</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    nse_count = len(df[df['Ticker'].str.contains('.NS', na=False)])
    st.markdown(f'''
    <div class="metric-card">
        <div style="font-size: 2rem; font-weight: bold; color: #a78bfa;">{nse_count:,}</div>
        <div style="color: #94a3b8;">📈 NSE Stocks</div>
    </div>
    ''', unsafe_allow_html=True)

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
        ["🏢 Sector Analysis", "📈 Individual Stock"],
        help="Choose your analysis mode"
    )
    
    if mode == "🏢 Sector Analysis":
        st.markdown("### 🎯 Sector Selection")
        
        available_sectors = sector_summary['Sector'].tolist()
        available_sectors = [s for s in available_sectors if s != 'Other']
        
        # Show sector stock counts
        st.markdown("**Available Sectors:**")
        for _, row in sector_summary.head(10).iterrows():
            if row['Sector'] != 'Other':
                st.text(f"• {row['Sector']}: {row['Stock Count']:,} stocks")
        
        selected_sectors = st.multiselect(
            "🏢 Choose Sectors to Analyze",
            available_sectors,
            default=[],
            help="Select sectors for complete analysis"
        )
        
        if selected_sectors:
            total_stocks = 0
            for sector in selected_sectors:
                sector_count = sector_summary[sector_summary['Sector'] == sector]['Stock Count'].iloc[0]
                total_stocks += sector_count
            st.info(f"Will analyze {total_stocks:,} stocks across {len(selected_sectors)} sectors")
        
        st.markdown("---")
        
        sort_by = st.selectbox(
            "Sort Results By",
            ["Upside % (Desc)", "Price (Asc)", "PE Ratio (Asc)", "Market Cap (Desc)"],
            help="Choose how to sort the results within each sector"
        )
        
        run_analysis = st.button("🚀 ANALYZE ALL SECTORS", use_container_width=True, type="primary")
    
    else:  # Individual Stock Analysis
        st.markdown("### 📈 Individual Stock Analysis")
        
        # Stock selection
        search = st.text_input(
            "🔍 Search Stock",
            placeholder="Company name or ticker...",
            help="Search by company name or ticker symbol"
        )
        
        if search:
            search_upper = search.upper()
            filtered_df = df[
                df['Ticker'].str.upper().str.contains(search_upper, na=False) |
                df['Name'].str.upper().str.contains(search_upper, na=False)
            ].head(50)  # Limit to first 50 results
        else:
            filtered_df = df.head(50)  # Show first 50 stocks
        
        if len(filtered_df) > 0:
            stock_options = [f"{row['Name']} ({row['Ticker']})" for _, row in filtered_df.iterrows()]
            selected_stock = st.selectbox("🎯 Select Stock", [""] + stock_options)
            
            if selected_stock:
                ticker = selected_stock.split("(")[1].strip(")")
                stock_row = df[df['Ticker'] == ticker]
                if not stock_row.empty:
                    category = stock_row['Category Name'].iloc[0]
                    sector_mapping = get_sector_mapping()
                    
                    # Find sector for this stock
                    stock_sector = 'Other'
                    for sector, categories in sector_mapping.items():
                        if category in categories:
                            stock_sector = sector
                            break
                    
                    st.session_state.selected_stock = {
                        'ticker': ticker,
                        'name': stock_row['Name'].iloc[0],
                        'sector': stock_sector
                    }
        
        # Manual ticker input
        st.markdown("---")
        manual_ticker = st.text_input(
            "✏️ Manual Ticker Entry",
            placeholder="e.g., RELIANCE.NS",
            help="Enter any ticker manually"
        )
        
        if manual_ticker:
            st.session_state.selected_stock = {
                'ticker': manual_ticker.upper(),
                'name': manual_ticker.upper(),
                'sector': 'Other'
            }
        
        analyze_stock = st.button("📊 ANALYZE STOCK", use_container_width=True, type="primary")

# ============================================================================
# MAIN CONTENT
# ============================================================================

if mode == "🏢 Sector Analysis":
    # Sector Overview
    st.markdown('<div class="section-header">🏢 Sector Overview</div>', unsafe_allow_html=True)
    
    # Display sector distribution
    st.markdown("**Sector Distribution:**")
    for _, row in sector_summary.head(10).iterrows():
        st.markdown(f"**{row['Sector']}**: {row['Stock Count']:,} stocks ({row['Sub-Categories']} categories)")
    
    if run_analysis and selected_sectors:
        st.markdown(f'''
        <div class="highlight-box">
            <h3>🔍 Comprehensive Sector Analysis</h3>
            <p>Processing <strong>ALL</strong> stocks in {len(selected_sectors)} selected sectors...</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Run complete sector screening
        sector_results = run_sector_screening(df, selected_sectors)
        
        if sector_results:
            total_analyzed = sum(len(sector_df) for sector_df in sector_results.values())
            successful_analyses = sum(len(sector_df[sector_df['Status'] == 'Success']) for sector_df in sector_results.values())
            
            st.markdown(f'''
            <div class="success-message">
                ✅ Complete analysis finished!<br>
                📊 Total stocks processed: <strong>{total_analyzed:,}</strong><br>
                💰 Successful analyses: <strong>{successful_analyses:,}</strong><br>
                🎯 Coverage: <strong>{(successful_analyses/total_analyzed*100):.1f}%</strong>
            </div>
            ''', unsafe_allow_html=True)
            
            # Display sector-wise results
            st.markdown('<div class="section-header">🎯 Complete Sector Analysis Results</div>', unsafe_allow_html=True)
            
            for sector, sector_df in sector_results.items():
                with st.expander(f"🏢 {sector} ({len(sector_df):,} stocks processed)", expanded=True):
                    
                    # Filter successful analyses for metrics
                    success_df = sector_df[sector_df['Status'] == 'Success'].copy()
                    
                    if len(success_df) > 0:
                        # Sector summary stats
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            avg_pe = success_df['PE Ratio'].replace([np.inf, -np.inf], np.nan).mean()
                            st.metric("Avg PE Ratio", f"{avg_pe:.2f}" if pd.notna(avg_pe) else "N/A")
                        
                        with col2:
                            avg_pb = success_df['PB Ratio'].replace([np.inf, -np.inf], np.nan).mean()
                            st.metric("Avg PB Ratio", f"{avg_pb:.2f}" if pd.notna(avg_pb) else "N/A")
                        
                        with col3:
                            avg_upside = success_df['Upside %'].replace([np.inf, -np.inf], np.nan).mean()
                            st.metric("Avg Upside %", f"{avg_upside:+.1f}%" if pd.notna(avg_upside) else "N/A")
                        
                        with col4:
                            avg_from_high = success_df['From 52W High %'].mean()
                            st.metric("Avg from 52W High", f"{avg_from_high:+.1f}%" if pd.notna(avg_from_high) else "N/A")
                        
                        with col5:
                            undervalued_count = len(success_df[(success_df['Upside %'] > 0) & (success_df['Upside %'].notna())])
                            st.metric("Undervalued Stocks", f"{undervalued_count}")
                        
                        # Sort and display results
                        display_df = success_df.copy()
                        
                        if sort_by == "Upside % (Desc)":
                            display_df = display_df.sort_values('Upside %', ascending=False, na_position='last')
                        elif sort_by == "Price (Asc)":
                            display_df = display_df.sort_values('Price', ascending=True, na_position='last')
                        elif sort_by == "PE Ratio (Asc)":
                            display_df = display_df.sort_values('PE Ratio', ascending=True, na_position='last')
                        elif sort_by == "Market Cap (Desc)":
                            display_df = display_df.sort_values('Market Cap', ascending=False, na_position='last')
                        
                        # Format display columns
                        display_cols = ['Ticker', 'Name', 'Price', 'Fair Value', 'Upside %', 'PE Ratio', 'From 52W High %', 'Cap Type']
                        formatted_df = display_df[display_cols].copy()
                        
                        # Format numerical columns
                        formatted_df['Price'] = formatted_df['Price'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) and x > 0 else "N/A")
                        formatted_df['Fair Value'] = formatted_df['Fair Value'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) and x > 0 else "N/A")
                        formatted_df['Upside %'] = formatted_df['Upside %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
                        formatted_df['PE Ratio'] = formatted_df['PE Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x > 0 else "N/A")
                        formatted_df['From 52W High %'] = formatted_df['From 52W High %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
                        
                        st.markdown(f"**📈 Results (sorted by {sort_by}):**")
                        
                        st.dataframe(
                            formatted_df,
                            use_container_width=True,
                            hide_index=True,
                            height=400
                        )
                    else:
                        st.warning("No successful data retrieval for this sector")
            
            # Download option
            st.markdown("---")
            
            # Combine all sector data for download
            all_data = []
            for sector, sector_df in sector_results.items():
                sector_df_copy = sector_df.copy()
                sector_df_copy['Sector'] = sector
                all_data.append(sector_df_copy)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                csv = combined_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Complete Analysis (CSV)",
                    data=csv,
                    file_name=f"NYZTrade_Complete_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        else:
            st.warning("❌ No sector results generated")
    
    elif run_analysis and not selected_sectors:
        st.warning("⚠️ Please select at least one sector to analyze.")

else:  # Individual Stock Analysis Mode
    if analyze_stock and 'selected_stock' in st.session_state:
        stock_info = st.session_state.selected_stock
        
        with st.spinner(f"🔄 Analyzing {stock_info['ticker']}..."):
            analysis, error = analyze_individual_stock(stock_info['ticker'], stock_info['sector'])
        
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
            
            # Key metrics
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            metrics = [
                (col1, "💰", f"₹{analysis['price']:,.2f}", "Current Price"),
                (col2, "📈", f"{analysis['trailing_pe']:.2f}" if analysis['trailing_pe'] else "N/A", "PE Ratio"),
                (col3, "📚", f"{analysis['pb_ratio']:.2f}" if analysis['pb_ratio'] else "N/A", "P/B Ratio"),
                (col4, "🏦", f"₹{analysis['market_cap']/10000000:,.0f}Cr" if analysis['market_cap'] else "N/A", "Market Cap"),
                (col5, "💵", f"{analysis['dividend_yield']*100:.2f}%" if analysis['dividend_yield'] else "N/A", "Dividend Yield"),
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
                st.markdown('<div class="section-header">📊 Valuation Analysis</div>', unsafe_allow_html=True)
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
            st.error(f"❌ Error analyzing {stock_info['ticker']}: {error}")
    
    elif analyze_stock:
        st.warning("⚠️ Please select a stock first")

# Footer
st.markdown('''
<div style="margin-top: 50px; padding: 30px; background: rgba(30, 41, 59, 0.4); border-radius: 15px; text-align: center;">
    <h4 style="color: #a78bfa; margin-bottom: 15px;">NYZTrade Pro | Complete Stock Analysis Platform</h4>
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This platform is designed for educational and informational purposes only. 
        Fair value calculations are based on industry benchmarks and should not be considered as investment advice. 
        Always conduct your own research and consult with qualified financial professionals before making any investment decisions.
    </div>
    <div style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
        © 2024 NYZTrade | Complete Analysis Platform | Market data provided by Yahoo Finance
    </div>
</div>
''', unsafe_allow_html=True)
