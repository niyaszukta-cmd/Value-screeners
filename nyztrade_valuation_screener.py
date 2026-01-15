import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

st.set_page_config(
    page_title="NYZTrade Pro Valuation & Screener", 
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

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.stat-item {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 10px;
    padding: 15px;
    text-align: center;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #a78bfa;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 0.9rem;
    color: #cbd5e1;
}

.highlight-box {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(167, 139, 250, 0.1));
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
}

.upload-section {
    background: rgba(30, 41, 59, 0.4);
    border: 2px dashed rgba(167, 139, 250, 0.4);
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
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

.success-message {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 8px;
    padding: 15px;
    margin: 20px 0;
    color: #86efac;
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
                <p style="color: #94a3b8;">Professional Stock Valuation & Screening Platform</p>
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
    """Load stocks database from uploaded CSV or default"""
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        else:
            # Try to load from the categorized file in outputs
            df = pd.read_csv('/mnt/user-data/outputs/stocks_universe_categorized_enhanced.csv')
        
        # Clean and prepare data
        df = df.dropna(subset=['Ticker', 'Name'])
        df['Ticker'] = df['Ticker'].str.strip().str.upper()
        df['Name'] = df['Name'].str.strip()
        df['Category Name'] = df['Category Name'].fillna('Miscellaneous')
        
        return df
    except Exception as e:
        st.error(f"Error loading database: {str(e)}")
        return None

def get_sector_mapping():
    """Map categories to broader sectors for efficient screening"""
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

# ============================================================================
# INDUSTRY BENCHMARKS (Enhanced with more sectors)
# ============================================================================
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
    'Textiles': {'pe': 20, 'ev_ebitda': 12, 'pb': 1.5, 'roe': 15},
    'Default': {'pe': 20, 'ev_ebitda': 12, 'pb': 2.0, 'roe': 15}
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def retry_with_backoff(retries=3, backoff_in_seconds=2):
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

@st.cache_data(ttl=3600)
@retry_with_backoff(retries=3, backoff_in_seconds=2)
def fetch_stock_data(ticker):
    try:
        time.sleep(0.3)  # Rate limiting
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        return info, None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate" in error_msg.lower():
            return None, "Rate limit reached"
        return None, str(e)[:100]

def categorize_market_cap(market_cap):
    """Categorize stocks by market cap (in INR Crores)"""
    if market_cap >= 100000:  # >= 1 Lakh Crore
        return 'Large Cap'
    elif market_cap >= 25000:  # >= 25,000 Crore
        return 'Mid Cap'
    elif market_cap >= 5000:   # >= 5,000 Crore
        return 'Small Cap'
    else:
        return 'Micro Cap'

def get_sector_from_category(category, sector_mapping):
    """Get broader sector from specific category"""
    for sector, categories in sector_mapping.items():
        if category in categories:
            return sector
    return 'Other'

def calculate_valuations(info, sector='Default'):
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        book_value = info.get('bookValue', 0)
        revenue = info.get('totalRevenue', 0)
        
        # Get benchmarks for sector
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        industry_pb = benchmark['pb']
        
        # Determine cap type
        cap_type = categorize_market_cap(market_cap / 10000000) if market_cap else 'Large Cap'
        
        # PE-based valuation
        historical_pe = trailing_pe * 0.9 if trailing_pe and trailing_pe > 0 else industry_pe
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # EV/EBITDA-based valuation
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2 if current_ev_ebitda and 0 < current_ev_ebitda < 50 else industry_ev_ebitda
        
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        
        # Calculate average upside
        ups = [v for v in [upside_pe, upside_ev] if v is not None]
        avg_upside = np.mean(ups) if ups else None
        
        # Additional metrics
        pb_ratio = price / book_value if book_value and book_value > 0 else None
        ps_ratio = market_cap / revenue if revenue and revenue > 0 else None
        
        # 52-week position
        high_52w = info.get('fiftyTwoWeekHigh', 0)
        low_52w = info.get('fiftyTwoWeekLow', 0)
        if high_52w and low_52w and high_52w > low_52w:
            pct_from_high = ((high_52w - price) / high_52w * 100) if price else None
            pct_from_low = ((price - low_52w) / low_52w * 100) if price else None
        else:
            pct_from_high = None
            pct_from_low = None
        
        return {
            'price': price,
            'trailing_pe': trailing_pe,
            'forward_pe': forward_pe,
            'trailing_eps': trailing_eps,
            'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe,
            'upside_pe': upside_pe,
            'enterprise_value': enterprise_value,
            'ebitda': ebitda,
            'market_cap': market_cap,
            'cap_type': cap_type,
            'current_ev_ebitda': current_ev_ebitda,
            'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev,
            'upside_ev': upside_ev,
            'avg_upside': avg_upside,
            'pb_ratio': pb_ratio,
            'ps_ratio': ps_ratio,
            'book_value': book_value,
            'revenue': revenue,
            'net_debt': (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'roe': info.get('returnOnEquity', 0),
            'profit_margin': info.get('profitMargins', 0),
            '52w_high': high_52w,
            '52w_low': low_52w,
            'pct_from_high': pct_from_high,
            'pct_from_low': pct_from_low,
            'sector': sector,
        }
    except:
        return None

# ============================================================================
# ENHANCED SCREENER LOGIC
# ============================================================================
def run_targeted_screener(df, criteria):
    """
    Run targeted stock screener based on sectors and criteria
    """
    sector_mapping = get_sector_mapping()
    
    # Filter by sector first if specified
    if 'sectors' in criteria and criteria['sectors']:
        # Get all categories for selected sectors
        selected_categories = []
        for sector in criteria['sectors']:
            selected_categories.extend(sector_mapping.get(sector, []))
        
        if selected_categories:
            df = df[df['Category Name'].isin(selected_categories)]
    
    # Further filter by specific categories if specified
    if 'categories' in criteria and criteria['categories']:
        df = df[df['Category Name'].isin(criteria['categories'])]
    
    # Market cap filter
    if 'cap_types' in criteria and criteria['cap_types']:
        # We'll apply this filter during screening since we need market cap data
        pass
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Limit the number of stocks to screen for efficiency
    limit = criteria.get('stock_limit', 200)
    df_sample = df.head(limit) if len(df) > limit else df
    
    total = len(df_sample)
    
    for idx, row in df_sample.iterrows():
        # Update progress
        progress = (idx + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Screening {idx + 1}/{total}: {row['Ticker']}")
        
        # Fetch data
        info, error = fetch_stock_data(row['Ticker'])
        if error or not info:
            continue
        
        # Get sector for this stock
        sector = get_sector_from_category(row['Category Name'], sector_mapping)
        
        vals = calculate_valuations(info, sector)
        if not vals:
            continue
        
        # Apply filters
        passes = True
        
        # Market cap filter
        if 'cap_types' in criteria and criteria['cap_types']:
            if vals['cap_type'] not in criteria['cap_types']:
                passes = False
        
        # Valuation filter
        if passes and 'valuation' in criteria:
            if criteria['valuation'] == 'undervalued' and (not vals['avg_upside'] or vals['avg_upside'] <= 0):
                passes = False
            elif criteria['valuation'] == 'overvalued' and (not vals['avg_upside'] or vals['avg_upside'] >= 0):
                passes = False
        
        # Upside range
        if passes and 'upside_min' in criteria and vals['avg_upside']:
            if vals['avg_upside'] < criteria['upside_min']:
                passes = False
        
        if passes and 'upside_max' in criteria and vals['avg_upside']:
            if vals['avg_upside'] > criteria['upside_max']:
                passes = False
        
        # Price range
        if passes and 'price_min' in criteria and vals['price']:
            if vals['price'] < criteria['price_min']:
                passes = False
        
        if passes and 'price_max' in criteria and vals['price']:
            if vals['price'] > criteria['price_max']:
                passes = False
        
        # PE ratio filter
        if passes and 'pe_max' in criteria and vals['trailing_pe']:
            if vals['trailing_pe'] > criteria['pe_max']:
                passes = False
        
        # 52-week position filters
        if passes and criteria.get('near_52w_high') and vals['pct_from_high']:
            if vals['pct_from_high'] > 10:  # More than 10% below high
                passes = False
        
        if passes and criteria.get('near_52w_low') and vals['pct_from_low']:
            if vals['pct_from_low'] > 50:  # More than 50% above low
                passes = False
        
        # ROE filter
        if passes and 'roe_min' in criteria and vals['roe']:
            if vals['roe'] * 100 < criteria['roe_min']:
                passes = False
        
        # Debt filter (based on net debt to market cap ratio)
        if passes and criteria.get('low_debt') and vals['market_cap'] and vals['net_debt']:
            debt_ratio = abs(vals['net_debt']) / vals['market_cap'] * 100
            if debt_ratio > 30:  # More than 30% debt to market cap
                passes = False
        
        # If passed all filters, add to results
        if passes:
            results.append({
                'Ticker': row['Ticker'],
                'Name': row['Name'],
                'Category': row['Category Name'],
                'Sector': sector,
                'Price': vals['price'],
                'Market Cap': vals['market_cap'] / 10000000,  # in Cr
                'Cap Type': vals['cap_type'],
                'PE': vals['trailing_pe'],
                'Upside %': vals['avg_upside'],
                'From 52W High %': -vals['pct_from_high'] if vals['pct_from_high'] else None,
                'From 52W Low %': vals['pct_from_low'] if vals['pct_from_low'] else None,
                'P/B': vals['pb_ratio'],
                'ROE %': vals['roe'] * 100 if vals['roe'] else None,
                'Profit Margin %': vals['profit_margin'] * 100 if vals['profit_margin'] else None,
            })
            
            # Check result limit
            if 'result_limit' in criteria and len(results) >= criteria['result_limit']:
                break
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

# ============================================================================
# ENHANCED PRESET SCREENERS
# ============================================================================
def get_preset_screeners(df):
    """Get targeted preset screeners based on available data"""
    
    # Get top categories by stock count for focused screening
    category_counts = df['Category Name'].value_counts()
    top_categories = category_counts.head(15).index.tolist()
    
    # Remove miscellaneous categories for focused screening
    focused_categories = [cat for cat in top_categories if 'Miscellaneous' not in cat][:10]
    
    presets = {
        "🚀 Top Undervalued Large Caps": {
            'cap_types': ['Large Cap'],
            'valuation': 'undervalued',
            'upside_min': 20,
            'pe_max': 25,
            'stock_limit': 100,
            'result_limit': 25
        },
        
        "💎 High-Growth Mid Caps": {
            'cap_types': ['Mid Cap'],
            'valuation': 'undervalued',
            'upside_min': 25,
            'roe_min': 15,
            'stock_limit': 150,
            'result_limit': 25
        },
        
        "⭐ Small Cap Gems": {
            'cap_types': ['Small Cap'],
            'valuation': 'undervalued',
            'upside_min': 30,
            'pe_max': 20,
            'stock_limit': 200,
            'result_limit': 25
        },
        
        "🎯 Undervalued Near 52W High": {
            'valuation': 'undervalued',
            'upside_min': 15,
            'near_52w_high': True,
            'stock_limit': 200,
            'result_limit': 25
        },
        
        "💰 Value Picks Near 52W Low": {
            'valuation': 'undervalued',
            'upside_min': 25,
            'near_52w_low': True,
            'stock_limit': 200,
            'result_limit': 25
        },
        
        "⚠️ Overvalued Large Caps": {
            'cap_types': ['Large Cap'],
            'valuation': 'overvalued',
            'upside_max': -15,
            'stock_limit': 100,
            'result_limit': 25
        },
        
        "🏦 Financial Sector Screening": {
            'sectors': ['Financial Services'],
            'valuation': 'undervalued',
            'upside_min': 15,
            'pb_ratio_max': 2.0,
            'stock_limit': 100,
            'result_limit': 25
        },
        
        "💻 Technology Screening": {
            'sectors': ['Technology'],
            'valuation': 'undervalued',
            'upside_min': 20,
            'pe_max': 30,
            'stock_limit': 100,
            'result_limit': 25
        },
        
        "💊 Healthcare & Pharma": {
            'sectors': ['Healthcare & Pharma'],
            'valuation': 'undervalued',
            'upside_min': 20,
            'stock_limit': 100,
            'result_limit': 25
        },
        
        "🏭 Industrial Screening": {
            'sectors': ['Industrial & Manufacturing'],
            'valuation': 'undervalued',
            'upside_min': 18,
            'pe_max': 25,
            'stock_limit': 100,
            'result_limit': 25
        },
        
        "🔍 Quality Stocks (High ROE)": {
            'valuation': 'undervalued',
            'upside_min': 15,
            'roe_min': 20,
            'low_debt': True,
            'stock_limit': 200,
            'result_limit': 25
        },
        
        "📈 Growth at Reasonable Price": {
            'upside_min': 15,
            'upside_max': 50,
            'pe_max': 25,
            'roe_min': 15,
            'stock_limit': 200,
            'result_limit': 25
        }
    }
    
    return presets

# ============================================================================
# CHART FUNCTIONS (Same as original but optimized)
# ============================================================================
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
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "PE Multiple", 'font': {'size': 16, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#7c3aed", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "EV/EBITDA", 'font': {'size': 16, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#ec4899", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': '#e2e8f0'}
    )
    return fig

# ============================================================================
# PDF REPORT GENERATION (Same as original)
# ============================================================================
def create_pdf_report(company, ticker, sector, vals):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'], 
        fontSize=28, 
        textColor=colors.HexColor('#7c3aed'), 
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    story = []
    story.append(Paragraph("NYZTrade Pro", title_style))
    story.append(Paragraph("Professional Valuation Report", subtitle_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"{company}", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    fair_data = [
        ['Metric', 'Value'],
        ['Fair Value', f"₹ {avg_fair:,.2f}"],
        ['Current Price', f"₹ {vals['price']:,.2f}"],
        ['Potential Upside', f"{avg_up:+.2f}%"]
    ]
    fair_table = Table(fair_data, colWidths=[3*inch, 2.5*inch])
    fair_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(fair_table)
    story.append(Spacer(1, 25))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.markdown('''
<div class="main-header">
    NYZTRADE STOCK SCREENER PRO
</div>
<div class="sub-header">
    📊 Enhanced Database | Sector-Focused Screening | Advanced Analytics | Real-Time Data
</div>
''', unsafe_allow_html=True)

# ============================================================================
# DATABASE LOADING SECTION
# ============================================================================
st.markdown('<div class="section-header">📂 Database Management</div>', unsafe_allow_html=True)

# File upload option
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
    # Try to load default database
    df = load_stocks_database()
    if df is not None:
        st.session_state.stocks_df = df
        st.markdown('<div class="success-message">✅ Default database loaded successfully!</div>', unsafe_allow_html=True)
    else:
        st.error("❌ No database available. Please upload a CSV file.")
        st.stop()
else:
    df = st.session_state.stocks_df

# Database statistics
if df is not None:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="stat-value">{len(df):,}</div>
            <div class="stat-label">📊 Total Stocks</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        categories = df['Category Name'].nunique()
        st.markdown(f'''
        <div class="metric-card">
            <div class="stat-value">{categories}</div>
            <div class="stat-label">🏷️ Categories</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        sector_mapping = get_sector_mapping()
        sectors = len(sector_mapping)
        st.markdown(f'''
        <div class="metric-card">
            <div class="stat-value">{sectors}</div>
            <div class="stat-label">🏢 Sectors</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        # Count NSE vs BSE
        nse_count = len(df[df['Ticker'].str.contains('.NS', na=False)])
        st.markdown(f'''
        <div class="metric-card">
            <div class="stat-value">{nse_count:,}</div>
            <div class="stat-label">📈 NSE Stocks</div>
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
        ["🔍 Smart Screener", "📈 Individual Analysis"],
        help="Choose your analysis mode"
    )
    
    if mode == "🔍 Smart Screener":
        st.markdown("### 🎯 Screening Options")
        
        screener_type = st.radio(
            "Screener Type",
            ["🚀 Preset Screeners", "🎛️ Custom Filters"],
            help="Choose between optimized presets or custom criteria"
        )
        
        if screener_type == "🚀 Preset Screeners":
            preset_screeners = get_preset_screeners(df)
            selected_preset = st.selectbox(
                "📋 Choose Preset",
                list(preset_screeners.keys()),
                help="Optimized screeners for different investment strategies"
            )
            
            # Show preset details
            preset_details = preset_screeners[selected_preset]
            st.markdown("**Screening Criteria:**")
            for key, value in preset_details.items():
                if key not in ['stock_limit', 'result_limit']:
                    st.text(f"• {key}: {value}")
            
            run_screen = st.button("🚀 RUN SCREENER", use_container_width=True, type="primary")
            
        else:  # Custom Filters
            st.markdown("### 🎛️ Custom Criteria")
            
            # Sector Selection
            sector_mapping = get_sector_mapping()
            selected_sectors = st.multiselect(
                "🏢 Sectors",
                list(sector_mapping.keys()),
                help="Select sectors to focus screening"
            )
            
            # Market Cap Filter
            cap_types = st.multiselect(
                "💼 Market Cap",
                ['Large Cap', 'Mid Cap', 'Small Cap', 'Micro Cap'],
                default=['Large Cap', 'Mid Cap']
            )
            
            # Valuation Filter
            valuation_type = st.selectbox(
                "📊 Valuation",
                ["All", "Undervalued", "Overvalued"]
            )
            
            # Advanced Filters
            with st.expander("🔧 Advanced Filters"):
                col1, col2 = st.columns(2)
                
                with col1:
                    upside_min = st.number_input("Min Upside %", value=10.0, step=5.0)
                    price_min = st.number_input("Min Price ₹", value=0.0, step=10.0)
                    pe_max = st.number_input("Max PE", value=30.0, step=5.0)
                
                with col2:
                    upside_max = st.number_input("Max Upside %", value=100.0, step=10.0)
                    price_max = st.number_input("Max Price ₹", value=5000.0, step=100.0)
                    roe_min = st.number_input("Min ROE %", value=10.0, step=2.0)
                
                # Position Filters
                near_52w_high = st.checkbox("Near 52W High", help="Within 10% of 52-week high")
                near_52w_low = st.checkbox("Near 52W Low", help="Good rebound candidates")
                low_debt = st.checkbox("Low Debt Companies", help="Debt-to-market-cap < 30%")
            
            # Screening Limits
            col1, col2 = st.columns(2)
            with col1:
                stock_limit = st.number_input("Stocks to Screen", value=200, min_value=50, max_value=500, step=50)
            with col2:
                result_limit = st.number_input("Max Results", value=25, min_value=10, max_value=50, step=5)
            
            run_screen = st.button("🔍 RUN CUSTOM SCREENER", use_container_width=True, type="primary")
    
    else:  # Individual Analysis
        st.markdown("### 📈 Stock Selection")
        
        # Category filter
        categories = ['All Categories'] + sorted(df['Category Name'].unique().tolist())
        selected_category = st.selectbox("🏷️ Filter by Category", categories)
        
        # Filter stocks based on category
        if selected_category == 'All Categories':
            filtered_df = df
        else:
            filtered_df = df[df['Category Name'] == selected_category]
        
        # Search functionality
        search = st.text_input(
            "🔍 Search Stocks",
            placeholder="Company name or ticker...",
            help="Search by company name or ticker symbol"
        )
        
        if search:
            search_upper = search.upper()
            filtered_df = filtered_df[
                filtered_df['Ticker'].str.upper().str.contains(search_upper, na=False) |
                filtered_df['Name'].str.upper().str.contains(search_upper, na=False)
            ]
        
        st.markdown(f"**{len(filtered_df):,} stocks available**")
        
        if len(filtered_df) > 0:
            # Stock selection
            stock_options = [f"{row['Name']} ({row['Ticker']})" for _, row in filtered_df.head(100).iterrows()]
            selected = st.selectbox("🎯 Select Stock", [""] + stock_options)
            
            if selected:
                ticker = selected.split("(")[1].strip(")")
                st.session_state.selected_ticker = ticker
        
        # Manual ticker input
        st.markdown("---")
        custom_ticker = st.text_input(
            "✏️ Manual Entry",
            placeholder="e.g., RELIANCE.NS",
            help="Enter any NSE/BSE ticker manually"
        )
        
        analyze_clicked = st.button("📊 ANALYZE STOCK", use_container_width=True, type="primary")

# ============================================================================
# MAIN CONTENT - SCREENER RESULTS
# ============================================================================

if mode == "🔍 Smart Screener":
    if 'run_screen' in locals() and run_screen:
        # Build criteria
        if screener_type == "🚀 Preset Screeners":
            criteria = preset_screeners[selected_preset].copy()
            st.markdown(f'''
            <div class="highlight-box">
                <h3>🔍 {selected_preset}</h3>
                <p>Running optimized screening with {criteria.get('stock_limit', 200)} stocks...</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            criteria = {}
            if selected_sectors:
                criteria['sectors'] = selected_sectors
            if cap_types:
                criteria['cap_types'] = cap_types
            if valuation_type == "Undervalued":
                criteria['valuation'] = 'undervalued'
            elif valuation_type == "Overvalued":
                criteria['valuation'] = 'overvalued'
            if upside_min > 0:
                criteria['upside_min'] = upside_min
            if upside_max < 100:
                criteria['upside_max'] = upside_max
            if price_min > 0:
                criteria['price_min'] = price_min
            if price_max < 5000:
                criteria['price_max'] = price_max
            if pe_max < 30:
                criteria['pe_max'] = pe_max
            if roe_min > 10:
                criteria['roe_min'] = roe_min
            if near_52w_high:
                criteria['near_52w_high'] = True
            if near_52w_low:
                criteria['near_52w_low'] = True
            if low_debt:
                criteria['low_debt'] = True
            
            criteria['stock_limit'] = stock_limit
            criteria['result_limit'] = result_limit
            
            st.markdown('''
            <div class="highlight-box">
                <h3>🔍 Custom Screener Results</h3>
                <p>Running custom screening criteria...</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Run screener
        try:
            results_df = run_targeted_screener(df, criteria)
            
            if results_df.empty:
                st.warning("❌ No stocks match your criteria. Try relaxing your filters.")
            else:
                st.markdown(f'''
                <div class="success-message">
                    ✅ Found <strong>{len(results_df)}</strong> stocks matching your criteria
                </div>
                ''', unsafe_allow_html=True)
                
                # Sort by upside percentage
                results_df = results_df.sort_values('Upside %', ascending=False, na_position='last')
                
                # Format the dataframe for display
                display_df = results_df.copy()
                
                # Format columns
                for col in ['Price', 'Market Cap']:
                    display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                display_df['Market Cap'] = display_df['Market Cap'].str.replace('₹', '₹') + 'Cr'
                
                for col in ['PE', 'P/B']:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                
                for col in ['Upside %', 'From 52W High %', 'From 52W Low %', 'ROE %', 'Profit Margin %']:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else 'N/A')
                
                # Display results table
                st.markdown('<div class="section-header">📊 Screening Results</div>', unsafe_allow_html=True)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Name": st.column_config.TextColumn("Company", width="medium"),
                        "Category": st.column_config.TextColumn("Category", width="medium"),
                        "Sector": st.column_config.TextColumn("Sector", width="small"),
                        "Price": st.column_config.TextColumn("Price", width="small"),
                        "Market Cap": st.column_config.TextColumn("MCap", width="small"),
                        "Cap Type": st.column_config.TextColumn("Type", width="small"),
                        "PE": st.column_config.TextColumn("PE", width="small"),
                        "Upside %": st.column_config.TextColumn("Upside", width="small"),
                        "P/B": st.column_config.TextColumn("P/B", width="small"),
                        "ROE %": st.column_config.TextColumn("ROE", width="small"),
                    }
                )
                
                # Download and analysis options
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download button
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Results (CSV)",
                        data=csv,
                        file_name=f"NYZTrade_Screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Analyze individual stock
                    if len(results_df) > 0:
                        selected_for_analysis = st.selectbox(
                            "📊 Analyze Stock from Results",
                            ["Select a stock..."] + results_df['Ticker'].tolist(),
                            format_func=lambda x: f"{results_df[results_df['Ticker']==x]['Name'].iloc[0]} ({x})" if x != "Select a stock..." else x
                        )
                        
                        if selected_for_analysis != "Select a stock..." and st.button("📈 Analyze", use_container_width=True, type="primary"):
                            st.session_state.analyze_ticker = selected_for_analysis
        
        except Exception as e:
            st.error(f"❌ Screening failed: {str(e)}")

# ============================================================================
# MAIN CONTENT - INDIVIDUAL ANALYSIS
# ============================================================================

if mode == "📈 Individual Analysis" and analyze_clicked:
    if custom_ticker:
        st.session_state.analyze_ticker = custom_ticker.upper()
    elif hasattr(st.session_state, 'selected_ticker'):
        st.session_state.analyze_ticker = st.session_state.selected_ticker

# Individual Stock Analysis
if hasattr(st.session_state, 'analyze_ticker') and st.session_state.analyze_ticker:
    ticker = st.session_state.analyze_ticker
    
    with st.spinner(f"🔄 Analyzing {ticker}..."):
        info, error = fetch_stock_data(ticker)
    
    if error or not info:
        st.error(f"❌ Error fetching data for {ticker}: {error if error else 'Unknown error'}")
        
        if error == "Rate limit reached":
            st.info("⏳ Please wait a moment and try again.")
        else:
            st.markdown('''
            <div class="highlight-box">
                <h4>💡 Troubleshooting Tips:</h4>
                <ul>
                    <li>Verify ticker format (e.g., RELIANCE.NS for NSE, RELIANCE.BO for BSE)</li>
                    <li>Check if the stock is actively trading</li>
                    <li>Try again in a few moments</li>
                </ul>
            </div>
            ''', unsafe_allow_html=True)
        
        # Clear the ticker from session state
        if 'analyze_ticker' in st.session_state:
            del st.session_state.analyze_ticker
        
        st.stop()
    
    # Get stock sector
    stock_row = df[df['Ticker'] == ticker]
    if not stock_row.empty:
        category = stock_row['Category Name'].iloc[0]
        sector_mapping = get_sector_mapping()
        sector = get_sector_from_category(category, sector_mapping)
    else:
        sector = info.get('sector', 'Default')
    
    vals = calculate_valuations(info, sector)
    if not vals:
        st.error("❌ Unable to calculate valuations for this stock")
        if 'analyze_ticker' in st.session_state:
            del st.session_state.analyze_ticker
        st.stop()
    
    company = info.get('longName', ticker)
    industry = info.get('industry', 'N/A')
    
    # Company Header
    st.markdown(f'''
    <div class="highlight-box">
        <h2 style="margin-bottom: 10px;">{company}</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 20px; color: #a78bfa;">
            <span>🏷️ <strong>{ticker}</strong></span>
            <span>🏢 <strong>{sector}</strong></span>
            <span>🏭 <strong>{industry}</strong></span>
            <span>💼 <strong>{vals['cap_type']}</strong></span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Calculate summary metrics
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Main valuation summary
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📊 Valuation Summary</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                <div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: #a78bfa;">₹{avg_fair:,.2f}</div>
                    <div style="color: #94a3b8;">Fair Value</div>
                </div>
                <div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: #e2e8f0;">₹{vals["price"]:,.2f}</div>
                    <div style="color: #94a3b8;">Current Price</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px;">
                <span style="font-size: 1.5rem; font-weight: bold; color: {'#34d399' if avg_up > 0 else '#f87171'};">
                    {"📈" if avg_up > 0 else "📉"} {avg_up:+.1f}% Potential
                </span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Recommendation
        if avg_up > 25:
            rec_class, rec_text, rec_icon = "rec-strong-buy", "Strong Buy", "🚀"
        elif avg_up > 15:
            rec_class, rec_text, rec_icon = "rec-buy", "Buy", "✅"
        elif avg_up > 0:
            rec_class, rec_text, rec_icon = "rec-buy", "Hold", "📥"
        elif avg_up > -10:
            rec_class, rec_text, rec_icon = "rec-hold", "Weak Hold", "⏸️"
        else:
            rec_class, rec_text, rec_icon = "rec-avoid", "Avoid", "⚠️"
        
        st.markdown(f'''
        <div class="recommendation {rec_class}">
            <div style="font-size: 2rem; margin-bottom: 10px;">{rec_icon}</div>
            <div style="font-size: 1.3rem; font-weight: bold;">{rec_text}</div>
            <div style="font-size: 0.9rem; margin-top: 5px;">Expected: {avg_up:+.1f}%</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # PDF Report
        pdf = create_pdf_report(company, ticker, sector, vals)
        st.download_button(
            "📥 Download Report",
            data=pdf,
            file_name=f"NYZTrade_{ticker}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Key metrics grid
    st.markdown('<div class="section-header">📊 Key Financial Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    metrics_data = [
        (col1, "💰", f"₹{vals['price']:,.2f}", "Current Price"),
        (col2, "📈", f"{vals['trailing_pe']:.1f}x" if vals['trailing_pe'] else "N/A", "PE Ratio"),
        (col3, "💵", f"₹{vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A", "EPS (TTM)"),
        (col4, "🏦", f"₹{vals['market_cap']/10000000:,.0f}Cr", "Market Cap"),
        (col5, "📊", f"{vals['current_ev_ebitda']:.1f}x" if vals['current_ev_ebitda'] else "N/A", "EV/EBITDA"),
        (col6, "📚", f"{vals['pb_ratio']:.1f}x" if vals['pb_ratio'] else "N/A", "P/B Ratio"),
    ]
    
    for col, icon, value, label in metrics_data:
        with col:
            st.markdown(f'''
            <div class="metric-card" style="text-align: center; padding: 15px;">
                <div style="font-size: 1.5rem; margin-bottom: 5px;">{icon}</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #a78bfa; margin-bottom: 5px;">{value}</div>
                <div style="font-size: 0.9rem; color: #94a3b8;">{label}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Charts section
    st.markdown('<div class="section-header">📊 Valuation Analysis</div>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        if vals['upside_pe'] is not None or vals['upside_ev'] is not None:
            fig_gauge = create_gauge_chart(
                vals['upside_pe'] if vals['upside_pe'] else 0,
                vals['upside_ev'] if vals['upside_ev'] else 0
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("Insufficient data for valuation gauges")
    
    with chart_col2:
        # 52-week performance
        if vals['pct_from_high'] is not None:
            st.markdown(f'''
            <div class="metric-card">
                <h4>📍 52-Week Position</h4>
                <div style="margin: 15px 0;">
                    <div style="margin-bottom: 10px;">
                        <span style="color: #94a3b8;">From 52W High:</span>
                        <span style="color: {'#f87171' if vals['pct_from_high'] > 20 else '#34d399'}; font-weight: bold;">
                            {-vals['pct_from_high']:+.1f}%
                        </span>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <span style="color: #94a3b8;">From 52W Low:</span>
                        <span style="color: {'#34d399' if vals['pct_from_low'] > 20 else '#f87171'}; font-weight: bold;">
                            {vals['pct_from_low']:+.1f}%
                        </span>
                    </div>
                    <div style="font-size: 0.9rem; color: #64748b; margin-top: 15px;">
                        Range: ₹{vals['52w_low']:,.1f} - ₹{vals['52w_high']:,.1f}
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("52-week data not available")
    
    # Detailed financial data
    st.markdown('<div class="section-header">📋 Detailed Financial Data</div>', unsafe_allow_html=True)
    
    # Create comprehensive financial table
    financial_metrics = {
        'Valuation Metrics': {
            'Current Price': f"₹{vals['price']:,.2f}",
            'Fair Value (PE)': f"₹{vals['fair_value_pe']:,.2f}" if vals['fair_value_pe'] else 'N/A',
            'Fair Value (EV)': f"₹{vals['fair_value_ev']:,.2f}" if vals['fair_value_ev'] else 'N/A',
            'Market Cap': f"₹{vals['market_cap']/10000000:,.0f} Cr",
            'Enterprise Value': f"₹{vals['enterprise_value']/10000000:,.0f} Cr" if vals['enterprise_value'] else 'N/A',
        },
        'Ratio Analysis': {
            'PE Ratio (TTM)': f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A',
            'Forward PE': f"{vals['forward_pe']:.2f}x" if vals['forward_pe'] else 'N/A',
            'EV/EBITDA': f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A',
            'P/B Ratio': f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else 'N/A',
            'P/S Ratio': f"{vals['ps_ratio']:.2f}x" if vals['ps_ratio'] else 'N/A',
        },
        'Performance Metrics': {
            'ROE': f"{vals['roe']*100:.1f}%" if vals['roe'] else 'N/A',
            'Profit Margin': f"{vals['profit_margin']*100:.1f}%" if vals['profit_margin'] else 'N/A',
            'Beta': f"{vals['beta']:.2f}" if vals['beta'] else 'N/A',
            'Dividend Yield': f"{vals['dividend_yield']*100:.2f}%" if vals['dividend_yield'] else 'N/A',
        },
        '52-Week Performance': {
            '52W High': f"₹{vals['52w_high']:,.2f}" if vals['52w_high'] else 'N/A',
            '52W Low': f"₹{vals['52w_low']:,.2f}" if vals['52w_low'] else 'N/A',
            'From High': f"{-vals['pct_from_high']:+.1f}%" if vals['pct_from_high'] else 'N/A',
            'From Low': f"{vals['pct_from_low']:+.1f}%" if vals['pct_from_low'] else 'N/A',
        }
    }
    
    # Display financial data in organized sections
    for section_name, metrics in financial_metrics.items():
        with st.expander(f"📊 {section_name}", expanded=True):
            cols = st.columns(len(metrics))
            for i, (metric, value) in enumerate(metrics.items()):
                with cols[i]:
                    st.metric(metric, value)
    
    # Clear analyze ticker from session state after analysis
    if 'analyze_ticker' in st.session_state:
        del st.session_state.analyze_ticker

# Footer
st.markdown('''
<div style="margin-top: 50px; padding: 30px; background: rgba(30, 41, 59, 0.4); border-radius: 15px; text-align: center;">
    <h4 style="color: #a78bfa; margin-bottom: 15px;">NYZTrade Pro | Advanced Stock Analysis Platform</h4>
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This platform is designed for educational and informational purposes only. 
        The analysis, recommendations, and data presented here should not be considered as financial advice or investment recommendations. 
        Always conduct your own research and consult with qualified financial professionals before making any investment decisions. 
        Past performance does not guarantee future results.
    </div>
    <div style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
        © 2024 NYZTrade | Developed for Educational Purposes | Market data provided by Yahoo Finance
    </div>
</div>
''', unsafe_allow_html=True)
