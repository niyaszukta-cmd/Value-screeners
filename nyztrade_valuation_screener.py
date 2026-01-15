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

.sector-card {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(79, 70, 229, 0.1) 100%);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 15px;
    padding: 25px;
    margin: 15px 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 40px rgba(124, 58, 237, 0.2);
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
                <p style="color: #94a3b8;">Sector-Focused Stock Screening Platform</p>
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
# SECTOR MAPPING
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
def retry_with_backoff(retries=3, backoff_in_seconds=1):
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
@retry_with_backoff(retries=2, backoff_in_seconds=1)
def fetch_stock_data(ticker):
    try:
        time.sleep(0.1)  # Minimal delay
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

# ============================================================================
# SECTOR-WISE SCREENING FUNCTIONS
# ============================================================================
def run_sector_screening(df, selected_sectors, sample_size_per_sector=10):
    """Run sector-wise screening with sample stocks from each sector"""
    
    sector_results = {}
    overall_progress = st.progress(0)
    status_text = st.empty()
    
    total_sectors = len(selected_sectors)
    
    for sector_idx, sector in enumerate(selected_sectors):
        status_text.text(f"Analyzing sector: {sector}")
        
        # Get sector mapping
        sector_mapping = get_sector_mapping()
        categories = sector_mapping.get(sector, [])
        
        # Filter stocks for this sector
        sector_stocks = df[df['Category Name'].isin(categories)]
        
        if len(sector_stocks) == 0:
            continue
        
        # Sample stocks from this sector
        sample_stocks = sector_stocks.head(sample_size_per_sector)
        
        sector_data = []
        stock_progress = st.progress(0)
        
        for stock_idx, row in sample_stocks.iterrows():
            # Update progress for individual stocks
            progress_pct = min((stock_idx + 1) / len(sample_stocks), 1.0)
            stock_progress.progress(progress_pct)
            
            # Fetch stock data
            info, error = fetch_stock_data(row['Ticker'])
            
            if not error and info:
                try:
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
                    
                    sector_data.append({
                        'Ticker': row['Ticker'],
                        'Name': row['Name'],
                        'Category': row['Category Name'],
                        'Price': price,
                        'Market Cap': market_cap,
                        'Cap Type': categorize_market_cap(market_cap),
                        'PE Ratio': pe_ratio,
                        'PB Ratio': pb_ratio,
                        'Dividend Yield': dividend_yield * 100 if dividend_yield else 0,
                        'Beta': beta,
                        '52W High': high_52w,
                        '52W Low': low_52w,
                        'From 52W High %': -pct_from_high if pct_from_high else None,
                        'From 52W Low %': pct_from_low if pct_from_low else None,
                    })
                except Exception as e:
                    continue
        
        stock_progress.empty()
        
        if sector_data:
            sector_results[sector] = pd.DataFrame(sector_data)
        
        # Update overall progress
        overall_progress.progress(min((sector_idx + 1) / total_sectors, 1.0))
    
    overall_progress.empty()
    status_text.empty()
    
    return sector_results

def create_sector_summary_chart(sector_summary):
    """Create interactive sector distribution chart"""
    fig = px.bar(
        sector_summary,
        x='Stock Count',
        y='Sector',
        orientation='h',
        title='Stock Distribution by Sector',
        color='Stock Count',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        title=dict(x=0.5, font=dict(size=18, color='#a78bfa')),
        xaxis=dict(showgrid=True, gridcolor='rgba(167, 139, 250, 0.2)'),
        yaxis=dict(showgrid=False)
    )
    
    return fig

def create_sector_performance_chart(sector_results):
    """Create sector performance comparison"""
    sector_stats = []
    
    for sector, df in sector_results.items():
        if len(df) > 0:
            avg_pe = df['PE Ratio'].replace([np.inf, -np.inf], np.nan).mean()
            avg_pb = df['PB Ratio'].replace([np.inf, -np.inf], np.nan).mean()
            avg_div_yield = df['Dividend Yield'].mean()
            avg_from_high = df['From 52W High %'].mean()
            
            sector_stats.append({
                'Sector': sector,
                'Avg PE': avg_pe if pd.notna(avg_pe) else 0,
                'Avg PB': avg_pb if pd.notna(avg_pb) else 0,
                'Avg Dividend Yield': avg_div_yield,
                'Avg Distance from 52W High': avg_from_high if pd.notna(avg_from_high) else 0,
                'Stock Count': len(df)
            })
    
    if not sector_stats:
        return None
    
    stats_df = pd.DataFrame(sector_stats)
    
    # Create subplot with multiple metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Average PE Ratio', 'Average PB Ratio', 
                       'Average Dividend Yield (%)', 'Distance from 52W High (%)'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # PE Ratio
    fig.add_trace(
        go.Bar(x=stats_df['Sector'], y=stats_df['Avg PE'], name='PE Ratio',
               marker_color='#7c3aed'),
        row=1, col=1
    )
    
    # PB Ratio  
    fig.add_trace(
        go.Bar(x=stats_df['Sector'], y=stats_df['Avg PB'], name='PB Ratio',
               marker_color='#ec4899'),
        row=1, col=2
    )
    
    # Dividend Yield
    fig.add_trace(
        go.Bar(x=stats_df['Sector'], y=stats_df['Avg Dividend Yield'], 
               name='Dividend Yield', marker_color='#34d399'),
        row=2, col=1
    )
    
    # Distance from High
    fig.add_trace(
        go.Bar(x=stats_df['Sector'], y=stats_df['Avg Distance from 52W High'], 
               name='Distance from High', marker_color='#f59e0b'),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        title=dict(text='Sector Performance Metrics', x=0.5, 
                  font=dict(size=18, color='#a78bfa'))
    )
    
    # Update all xaxis to rotate labels
    for i in range(1, 5):
        fig.update_xaxes(tickangle=45, row=(i-1)//2 + 1, col=(i-1)%2 + 1)
    
    return fig

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.markdown('''
<div class="main-header">
    NYZTRADE SECTOR SCREENER PRO
</div>
<div class="sub-header">
    🎯 Sector-Focused Analysis | Market Insights | Performance Comparison
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
    
    # SECTOR SELECTION
    st.markdown("### 🎯 Sector Selection")
    
    available_sectors = sector_summary['Sector'].tolist()
    available_sectors = [s for s in available_sectors if s != 'Other']
    
    selected_sectors = st.multiselect(
        "🏢 Choose Sectors to Analyze",
        available_sectors,
        default=available_sectors[:3],  # Select first 3 by default
        help="Select sectors for detailed analysis"
    )
    
    st.markdown("---")
    
    # ANALYSIS PARAMETERS
    st.markdown("### ⚙️ Analysis Parameters")
    
    sample_size = st.slider(
        "Stocks per Sector",
        min_value=5,
        max_value=20,
        value=10,
        help="Number of stocks to analyze from each sector"
    )
    
    analysis_type = st.selectbox(
        "Analysis Focus",
        ["Overview", "Performance", "Valuation", "Risk Analysis"],
        help="Choose the type of analysis to perform"
    )
    
    st.markdown("---")
    
    run_analysis = st.button("🚀 RUN SECTOR ANALYSIS", use_container_width=True, type="primary")

# ============================================================================
# SECTOR OVERVIEW
# ============================================================================
st.markdown('<div class="section-header">🏢 Sector Overview</div>', unsafe_allow_html=True)

# Display sector distribution
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Sector Distribution:**")
    for _, row in sector_summary.head(10).iterrows():
        st.markdown(f"**{row['Sector']}**: {row['Stock Count']:,} stocks ({row['Sub-Categories']} categories)")

with col2:
    # Sector distribution chart
    fig_dist = create_sector_summary_chart(sector_summary)
    st.plotly_chart(fig_dist, use_container_width=True)

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

if run_analysis and selected_sectors:
    st.markdown(f'''
    <div class="highlight-box">
        <h3>🔍 Analyzing {len(selected_sectors)} Sectors</h3>
        <p>Running sector-wise analysis with {sample_size} stocks per sector...</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Run sector screening
    sector_results = run_sector_screening(df, selected_sectors, sample_size)
    
    if sector_results:
        st.markdown(f'''
        <div class="success-message">
            ✅ Analysis completed for <strong>{len(sector_results)}</strong> sectors
        </div>
        ''', unsafe_allow_html=True)
        
        # Create performance comparison chart
        fig_perf = create_sector_performance_chart(sector_results)
        if fig_perf:
            st.markdown('<div class="section-header">📊 Sector Performance Comparison</div>', unsafe_allow_html=True)
            st.plotly_chart(fig_perf, use_container_width=True)
        
        # Display sector-wise results
        st.markdown('<div class="section-header">🎯 Detailed Sector Analysis</div>', unsafe_allow_html=True)
        
        for sector, sector_df in sector_results.items():
            with st.expander(f"🏢 {sector} ({len(sector_df)} stocks analyzed)", expanded=True):
                
                # Sector summary stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_pe = sector_df['PE Ratio'].replace([np.inf, -np.inf], np.nan).mean()
                    st.metric("Avg PE Ratio", f"{avg_pe:.2f}" if pd.notna(avg_pe) else "N/A")
                
                with col2:
                    avg_pb = sector_df['PB Ratio'].replace([np.inf, -np.inf], np.nan).mean()
                    st.metric("Avg PB Ratio", f"{avg_pb:.2f}" if pd.notna(avg_pb) else "N/A")
                
                with col3:
                    avg_div = sector_df['Dividend Yield'].mean()
                    st.metric("Avg Dividend Yield", f"{avg_div:.2f}%" if pd.notna(avg_div) else "N/A")
                
                with col4:
                    avg_from_high = sector_df['From 52W High %'].mean()
                    st.metric("Avg from 52W High", f"{avg_from_high:+.1f}%" if pd.notna(avg_from_high) else "N/A")
                
                # Top performers in sector
                st.markdown("**📈 Top Performers:**")
                
                # Sort by distance from 52W high (closest to high = best performers)
                top_performers = sector_df.copy()
                top_performers = top_performers[top_performers['From 52W High %'].notna()]
                top_performers = top_performers.sort_values('From 52W High %', ascending=True).head(5)
                
                if len(top_performers) > 0:
                    # Format display
                    display_cols = ['Ticker', 'Name', 'Price', 'PE Ratio', 'From 52W High %', 'From 52W Low %']
                    display_df = top_performers[display_cols].copy()
                    
                    display_df['Price'] = display_df['Price'].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) and x > 0 else "N/A")
                    display_df['PE Ratio'] = display_df['PE Ratio'].apply(lambda x: f"{x:.2f}" if pd.notna(x) and x > 0 else "N/A")
                    display_df['From 52W High %'] = display_df['From 52W High %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
                    display_df['From 52W Low %'] = display_df['From 52W Low %'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No performance data available for this sector")
        
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
                "📥 Download Complete Sector Analysis (CSV)",
                data=csv,
                file_name=f"NYZTrade_Sector_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    else:
        st.warning("❌ No data retrieved for the selected sectors. Please try different sectors or check your internet connection.")

elif run_analysis and not selected_sectors:
    st.warning("⚠️ Please select at least one sector to analyze.")

# Footer
st.markdown('''
<div style="margin-top: 50px; padding: 30px; background: rgba(30, 41, 59, 0.4); border-radius: 15px; text-align: center;">
    <h4 style="color: #a78bfa; margin-bottom: 15px;">NYZTrade Pro | Sector-Focused Stock Analysis</h4>
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer:</strong> This platform is designed for educational and informational purposes only. 
        The analysis, recommendations, and data presented here should not be considered as financial advice or investment recommendations. 
        Always conduct your own research and consult with qualified financial professionals before making any investment decisions.
    </div>
    <div style="margin-top: 15px; color: #64748b; font-size: 0.9rem;">
        © 2024 NYZTrade | Sector Analysis Platform | Market data provided by Yahoo Finance
    </div>
</div>
''', unsafe_allow_html=True)
