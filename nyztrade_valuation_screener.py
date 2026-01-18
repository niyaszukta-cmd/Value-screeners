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
# COMPREHENSIVE INDIAN STOCKS DATABASE (117 INDUSTRIES, 8,984 STOCKS)
# ============================================================================

# Load from uploaded database file
exec(open('/mnt/user-data/uploads/1768721158220_indian_stocks_database.py').read())

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
    "Food - Major Diversified": "Consumer & Retail",
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
# TECHNICAL INDICATOR CALCULATIONS
# ============================================================================

def calculate_rsi(prices, period=14):
    """Calculate RSI (Relative Strength Index)"""
    try:
        if len(prices) < period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None
    except:
        return None

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        if len(prices) < slow + signal:
            return None, None, None
        
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return (
            macd.iloc[-1] if not macd.empty else None,
            signal_line.iloc[-1] if not signal_line.empty else None,
            histogram.iloc[-1] if not histogram.empty else None
        )
    except:
        return None, None, None

def calculate_supertrend(high, low, close, period=10, multiplier=3.0):
    """Calculate Supertrend indicator"""
    try:
        if len(close) < period + 1:
            return None, None
        
        # Calculate True Range (TR)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Average True Range (ATR)
        atr = tr.rolling(window=period).mean()
        
        # Calculate basic upper and lower bands
        hl_avg = (high + low) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        # Initialize Supertrend
        supertrend = pd.Series(index=close.index, dtype=float)
        trend = pd.Series(index=close.index, dtype=int)
        
        for i in range(period, len(close)):
            if i == period:
                supertrend.iloc[i] = upper_band.iloc[i]
                trend.iloc[i] = 1
            else:
                # Upper band calculation
                if upper_band.iloc[i] < supertrend.iloc[i-1] or close.iloc[i-1] > supertrend.iloc[i-1]:
                    upper_band.iloc[i] = upper_band.iloc[i]
                else:
                    upper_band.iloc[i] = supertrend.iloc[i-1]
                
                # Lower band calculation
                if lower_band.iloc[i] > supertrend.iloc[i-1] or close.iloc[i-1] < supertrend.iloc[i-1]:
                    lower_band.iloc[i] = lower_band.iloc[i]
                else:
                    lower_band.iloc[i] = supertrend.iloc[i-1]
                
                # Final Supertrend calculation
                if close.iloc[i] <= lower_band.iloc[i]:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    trend.iloc[i] = -1
                elif close.iloc[i] >= upper_band.iloc[i]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    trend.iloc[i] = 1
                else:
                    supertrend.iloc[i] = supertrend.iloc[i-1]
                    trend.iloc[i] = trend.iloc[i-1]
        
        return supertrend.iloc[-1], trend.iloc[-1]
    except:
        return None, None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_technical_indicators(ticker, period_days=100):
    """Fetch historical data and calculate technical indicators with caching"""
    try:
        # Fetch historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date, progress=False)
        
        if hist.empty or len(hist) < 30:
            return None
        
        # Calculate indicators
        rsi = calculate_rsi(hist['Close'])
        macd, macd_signal, macd_histogram = calculate_macd(hist['Close'])
        supertrend_value, supertrend_trend = calculate_supertrend(
            hist['High'], hist['Low'], hist['Close']
        )
        
        # Determine signals
        rsi_signal = None
        if rsi is not None:
            if rsi < 30:
                rsi_signal = 'oversold'  # Potential buy
            elif rsi > 70:
                rsi_signal = 'overbought'  # Potential sell
            elif 40 <= rsi <= 60:
                rsi_signal = 'neutral'
            elif 30 <= rsi < 40:
                rsi_signal = 'bullish'  # Recovering from oversold
            elif 60 < rsi <= 70:
                rsi_signal = 'bearish'  # Approaching overbought
        
        macd_signal_trend = None
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                macd_signal_trend = 'bullish'
            else:
                macd_signal_trend = 'bearish'
        
        supertrend_signal = None
        if supertrend_trend is not None:
            if supertrend_trend == 1:
                supertrend_signal = 'bullish'
            else:
                supertrend_signal = 'bearish'
        
        return {
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram,
            'macd_trend': macd_signal_trend,
            'supertrend_value': supertrend_value,
            'supertrend_trend': supertrend_trend,
            'supertrend_signal': supertrend_signal,
            'current_price': hist['Close'].iloc[-1] if not hist.empty else None
        }
    
    except Exception as e:
        return None

def get_quick_technical_signals(ticker):
    """Quick technical signals for screening (lighter version)"""
    try:
        # Get only last 60 days for quicker processing
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date, progress=False)
        
        if hist.empty or len(hist) < 20:
            return None
        
        # Quick RSI
        rsi = calculate_rsi(hist['Close'], period=14)
        
        # Quick Supertrend
        supertrend_value, supertrend_trend = calculate_supertrend(
            hist['High'], hist['Low'], hist['Close'], period=7, multiplier=2.5
        )
        
        return {
            'rsi_bullish': rsi is not None and (rsi < 70 and rsi > 25),  # Not overbought, not extremely oversold
            'supertrend_bullish': supertrend_trend == 1,
            'rsi_value': rsi,
            'supertrend_signal': 'bullish' if supertrend_trend == 1 else 'bearish'
        }
    except:
        return None

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
# INDUSTRY BENCHMARK CALCULATIONS
# ============================================================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes  
def calculate_industry_benchmarks(industry, sample_size=20):
    """Calculate dynamic industry benchmarks"""
    try:
        stocks = get_stocks_by_category(industry)
        if not stocks:
            sector = get_sector_for_industry(industry)
            return SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other'])
        
        # Take a sample for efficiency
        stock_items = list(stocks.items())
        if len(stock_items) > sample_size:
            step = len(stock_items) // sample_size
            stock_items = stock_items[::step][:sample_size]
        
        # Collect metrics
        pe_ratios, pb_ratios, ev_ebitda_ratios, roe_values = [], [], [], []
        
        for ticker, name in stock_items:
            fundamentals = get_stock_fundamentals(ticker)
            if fundamentals:
                if fundamentals['trailing_pe'] and 5 <= fundamentals['trailing_pe'] <= 100:
                    pe_ratios.append(fundamentals['trailing_pe'])
                if fundamentals['pb_ratio'] and 0.1 <= fundamentals['pb_ratio'] <= 20:
                    pb_ratios.append(fundamentals['pb_ratio'])
                if fundamentals['ev_ebitda'] and 2 <= fundamentals['ev_ebitda'] <= 50:
                    ev_ebitda_ratios.append(fundamentals['ev_ebitda'])
                if fundamentals['roe'] and 0.01 <= fundamentals['roe'] <= 1:
                    roe_values.append(fundamentals['roe'] * 100)
        
        # Calculate benchmarks with outlier removal
        def remove_outliers_and_mean(data):
            if len(data) < 3:
                return np.mean(data) if data else None
            q1, q3 = np.percentile(data, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered = [x for x in data if lower_bound <= x <= upper_bound]
            return np.mean(filtered) if filtered else np.mean(data)
        
        sector = get_sector_for_industry(industry)
        default = SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other'])
        
        benchmarks = {
            'pe': remove_outliers_and_mean(pe_ratios) or default['pe'],
            'pb': remove_outliers_and_mean(pb_ratios) or default['pb'], 
            'ev_ebitda': remove_outliers_and_mean(ev_ebitda_ratios) or default['ev_ebitda'],
            'roe': remove_outliers_and_mean(roe_values) or default['roe']
        }
        
        return benchmarks
        
    except Exception as e:
        sector = get_sector_for_industry(industry)
        return SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other'])

# ============================================================================
# VALUATION CALCULATIONS  
# ============================================================================

def calculate_fair_value(fundamentals, benchmarks):
    """Calculate fair value using multiple methods"""
    if not fundamentals or not benchmarks:
        return None
    
    fair_values = []
    
    # PE-based valuation
    if fundamentals['trailing_pe'] and fundamentals['roe']:
        eps = fundamentals['book_value'] * fundamentals['roe'] if fundamentals['book_value'] else None
        if eps:
            pe_fair_value = eps * benchmarks['pe']
            fair_values.append(pe_fair_value)
    
    # PB-based valuation  
    if fundamentals['book_value']:
        pb_fair_value = fundamentals['book_value'] * benchmarks['pb']
        fair_values.append(pb_fair_value)
    
    # EV/EBITDA approach (simplified)
    if fundamentals['market_cap'] and fundamentals['ev_ebitda']:
        # Estimate EBITDA from current EV/EBITDA ratio
        current_ebitda = fundamentals['market_cap'] / fundamentals['ev_ebitda'] if fundamentals['ev_ebitda'] != 0 else None
        if current_ebitda:
            ev_fair_value = current_ebitda * benchmarks['ev_ebitda']
            # Convert back to price per share (approximation)
            shares_outstanding = fundamentals['market_cap'] / fundamentals['price'] if fundamentals['price'] else None
            if shares_outstanding:
                ev_price_fair = ev_fair_value / shares_outstanding
                fair_values.append(ev_price_fair)
    
    # Return average of methods
    if fair_values:
        # Remove outliers before averaging
        if len(fair_values) > 1:
            fair_values = [fv for fv in fair_values if fv > 0]  # Remove negative values
            if len(fair_values) > 2:
                # Remove extreme outliers
                q1, q3 = np.percentile(fair_values, [25, 75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                fair_values = [fv for fv in fair_values if lower_bound <= fv <= upper_bound]
        
        return np.mean(fair_values) if fair_values else None
    
    return None

# ============================================================================
# SCREENING LOGIC
# ============================================================================

def run_industry_screener(industry, strategy_type="undervalued", max_results=50):
    """Run screening for a specific industry"""
    
    stocks = get_stocks_by_category(industry)
    if not stocks:
        return pd.DataFrame()
    
    # Get industry benchmarks
    benchmarks = calculate_industry_benchmarks(industry)
    
    results = []
    
    with st.progress(0) as progress_bar:
        total_stocks = len(stocks)
        
        for i, (ticker, name) in enumerate(stocks.items()):
            # Update progress
            progress_bar.progress((i + 1) / total_stocks)
            
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
            if strategy_type == "undervalued" and upside < 10:
                continue
            elif strategy_type == "undervalued_supertrend":
                if upside < 10:
                    continue
                # Check technical signals
                technical = get_quick_technical_signals(ticker)
                if not technical or not technical.get('supertrend_bullish', False):
                    continue
            elif strategy_type == "undervalued_rsi_macd":
                if upside < 10:
                    continue
                # Check RSI is not overbought
                technical = get_quick_technical_signals(ticker)
                if not technical or not technical.get('rsi_bullish', False):
                    continue
            elif strategy_type == "overvalued" and upside > -10:
                continue
            elif strategy_type == "momentum" and (not fundamentals['pct_from_high'] or fundamentals['pct_from_high'] < -20):
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
    
    return pd.DataFrame(results)

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
    
    # Get industry benchmarks
    industry = stock_info['category']
    benchmarks = calculate_industry_benchmarks(industry)
    
    # Calculate fair value
    fair_value = calculate_fair_value(fundamentals, benchmarks)
    upside = ((fair_value - fundamentals['price']) / fundamentals['price']) * 100 if fair_value else 0
    
    # Get technical indicators
    technical_data = get_technical_indicators(ticker)
    
    analysis = {
        'ticker': ticker,
        'company': fundamentals['name'],
        'industry': industry,
        'sector': get_sector_for_industry(industry),
        'price': fundamentals['price'],
        'fair_value': fair_value,
        'upside': upside,
        'fundamentals': fundamentals,
        'benchmarks': benchmarks,
        'technical': technical_data
    }
    
    return analysis, None

# ============================================================================
# MAIN STREAMLIT APPLICATION
# ============================================================================

def main():
    
    # Header
    st.markdown(f'''
    <div class="main-header">
        <h1>🎯 NYZTrade - Comprehensive Industry Screener</h1>
        <h3>Professional Stock Analysis Across {TOTAL_CATEGORIES} Indian Industries</h3>
        <p>Powered by Real-Time Industry Benchmarks • {TOTAL_STOCKS:,} Stocks Universe</p>
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
            <h3>6</h3>
            <p>Strategies</p>
        </div>
        <div class="stat-card">
            <h3>Real-Time</h3>
            <p>Benchmarks</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🔧 Screening Controls")
    
    # Mode selection
    mode = st.sidebar.selectbox(
        "Analysis Mode",
        ["🎯 Industry Screener", "📈 Individual Stock Analysis", "📊 Industry Explorer"]
    )
    
    if mode == "🎯 Industry Screener":
        
        # Industry selection
        industries = sorted(get_all_categories())
        selected_industry = st.sidebar.selectbox("Select Industry", industries)
        
        # Strategy selection  
        strategy = st.sidebar.selectbox(
            "Screening Strategy",
            [
                ("undervalued", "🎯 Undervalued Stocks"),
                ("undervalued_supertrend", "📈 Undervalued + Supertrend Bullish"),
                ("undervalued_rsi_macd", "🔍 Undervalued + RSI/MACD Signals"),
                ("overvalued", "⚠️ Overvalued Stocks"),
                ("momentum", "🚀 Momentum Plays"),
                ("quality", "💎 Quality Stocks")
            ],
            format_func=lambda x: x[1]
        )
        
        strategy_type = strategy[0]
        strategy_name = strategy[1]
        
        # Parameters
        max_results = st.sidebar.slider("Max Results", 10, 100, 50)
        
        # Run button
        if st.sidebar.button("🚀 Run Screener", type="primary"):
            
            # Show industry info
            industry_stocks = get_stocks_by_category(selected_industry)
            sector = get_sector_for_industry(selected_industry)
            
            st.markdown(f'''
            <div class="highlight-box">
                <h3>📊 {strategy_name}</h3>
                <p><strong>Industry:</strong> {selected_industry}</p>
                <p><strong>Sector:</strong> {sector}</p>
                <p><strong>Stock Universe:</strong> {len(industry_stocks):,} stocks</p>
                <p><strong>Strategy:</strong> {strategy_type.replace('_', ' ').title()}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Run screener
            with st.spinner(f"🔍 Screening {len(industry_stocks):,} stocks in {selected_industry}..."):
                results_df = run_industry_screener(selected_industry, strategy_type, max_results)
            
            if results_df.empty:
                st.warning(f"❌ No stocks found matching {strategy_name} criteria in {selected_industry}")
            else:
                # Display results
                st.markdown(f'''
                <div class="success-message">
                    ✅ Found <strong>{len(results_df)}</strong> {strategy_name.lower()} opportunities<br>
                    📊 Industry: {selected_industry}<br>
                    🎯 Strategy: {strategy_type.replace('_', ' ').title()}
                </div>
                ''', unsafe_allow_html=True)
                
                # Sort results appropriately
                if strategy_type == "overvalued":
                    results_df = results_df.sort_values('Upside %', ascending=True)
                else:
                    results_df = results_df.sort_values('Upside %', ascending=False)
                
                # Format display
                display_df = results_df.copy()
                for col in ['Price', 'Fair Value']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                for col in ['Upside %', 'ROE %', 'From 52W High %', 'From 52W Low %', 'Dividend Yield %']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else 'N/A')
                
                if 'Market Cap' in display_df.columns:
                    display_df['Market Cap'] = display_df['Market Cap'].apply(lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A')
                
                # Display table
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=min(600, len(display_df) * 35 + 100)
                )
                
                # Download button
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
    
    elif mode == "📈 Individual Stock Analysis":
        
        # Stock input methods
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
                    options = [f"{r['ticker']} - {r['name']} ({r['industry']})" for r in search_results]
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
                analysis, error = analyze_individual_stock(selected_ticker)
            
            if error:
                st.error(f"❌ Error: {error}")
            elif analysis:
                # Display analysis
                st.markdown(f"# {analysis['company']}")
                st.markdown(f"**{analysis['ticker']} • {analysis['industry']} • {analysis['sector']}**")
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"₹{analysis['price']:,.2f}")
                
                with col2:
                    upside_delta = f"{analysis['upside']:+.1f}%" if analysis['fair_value'] else "N/A"
                    delta_color = "normal" if analysis['upside'] > 0 else "inverse"
                    st.metric(
                        "Fair Value",
                        f"₹{analysis['fair_value']:,.2f}" if analysis['fair_value'] else "N/A",
                        delta=upside_delta,
                        delta_color=delta_color
                    )
                
                with col3:
                    # Recommendation
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
                    # Position in 52-week range
                    if analysis['fundamentals']['pct_from_high'] is not None:
                        range_pos = 100 + analysis['fundamentals']['pct_from_high']  # Convert to position from low
                        if range_pos > 80:
                            pos_emoji = "🟢"
                        elif range_pos > 60:
                            pos_emoji = "🟡"
                        elif range_pos > 40:
                            pos_emoji = "🟠"
                        else:
                            pos_emoji = "🔴"
                        st.metric("52W Position", f"{pos_emoji} {range_pos:.0f}%")
                    else:
                        st.metric("52W Position", "N/A")
                
                st.markdown("---")
                
                # Tabbed analysis
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Industry Benchmarks", 
                    "📈 Technical Analysis", 
                    "📍 Performance", 
                    "💼 Fundamentals"
                ])
                
                with tab1:
                    st.markdown("#### Industry Benchmark Comparison")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        pe = analysis['fundamentals']['trailing_pe']
                        benchmark_pe = analysis['benchmarks']['pe']
                        if pe and benchmark_pe:
                            pe_delta = pe - benchmark_pe
                            st.metric(
                                "PE Ratio",
                                f"{pe:.2f}x",
                                delta=f"{pe_delta:+.2f}x vs industry",
                                delta_color="inverse" if pe_delta > 0 else "normal"
                            )
                            st.caption(f"Industry Avg: {benchmark_pe:.2f}x")
                        else:
                            st.metric("PE Ratio", "N/A")
                    
                    with col2:
                        pb = analysis['fundamentals']['pb_ratio']
                        benchmark_pb = analysis['benchmarks']['pb']
                        if pb and benchmark_pb:
                            pb_delta = pb - benchmark_pb
                            st.metric(
                                "PB Ratio",
                                f"{pb:.2f}x",
                                delta=f"{pb_delta:+.2f}x vs industry",
                                delta_color="inverse" if pb_delta > 0 else "normal"
                            )
                            st.caption(f"Industry Avg: {benchmark_pb:.2f}x")
                        else:
                            st.metric("PB Ratio", "N/A")
                    
                    with col3:
                        roe = analysis['fundamentals']['roe']
                        benchmark_roe = analysis['benchmarks']['roe']
                        if roe and benchmark_roe:
                            roe_pct = roe * 100
                            roe_delta = roe_pct - benchmark_roe
                            st.metric(
                                "ROE",
                                f"{roe_pct:.1f}%",
                                delta=f"{roe_delta:+.1f}pp vs industry",
                                delta_color="normal" if roe_delta > 0 else "inverse"
                            )
                            st.caption(f"Industry Avg: {benchmark_roe:.1f}%")
                        else:
                            st.metric("ROE", "N/A")
                
                with tab2:
                    st.markdown("#### Real-Time Technical Indicators")
                    
                    if analysis['technical']:
                        tech = analysis['technical']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            rsi = tech.get('rsi')
                            if rsi:
                                rsi_emoji = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡"
                                rsi_text = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                                st.metric("RSI (14)", f"{rsi:.1f}", delta=f"{rsi_emoji} {rsi_text}")
                            else:
                                st.metric("RSI (14)", "N/A")
                        
                        with col2:
                            macd_trend = tech.get('macd_trend')
                            macd = tech.get('macd')
                            if macd_trend and macd:
                                trend_emoji = "🟢" if macd_trend == "bullish" else "🔴"
                                st.metric(
                                    "MACD",
                                    f"{macd:.3f}",
                                    delta=f"{trend_emoji} {macd_trend.title()}",
                                    delta_color="normal" if macd_trend == "bullish" else "inverse"
                                )
                            else:
                                st.metric("MACD", "N/A")
                        
                        with col3:
                            supertrend_signal = tech.get('supertrend_signal')
                            supertrend_value = tech.get('supertrend_value')
                            if supertrend_signal and supertrend_value:
                                signal_emoji = "🟢" if supertrend_signal == "bullish" else "🔴"
                                distance = ((analysis['price'] - supertrend_value) / supertrend_value) * 100
                                st.metric(
                                    "Supertrend",
                                    f"₹{supertrend_value:.2f}",
                                    delta=f"{signal_emoji} {supertrend_signal.title()} ({distance:+.1f}%)",
                                    delta_color="normal" if supertrend_signal == "bullish" else "inverse"
                                )
                            else:
                                st.metric("Supertrend", "N/A")
                        
                        # Technical summary
                        st.markdown("---")
                        bullish_signals = sum([
                            1 for signal in [
                                tech.get('rsi_signal') in ['bullish', 'oversold'],
                                tech.get('macd_trend') == 'bullish',
                                tech.get('supertrend_signal') == 'bullish'
                            ] if signal
                        ])
                        
                        total_signals = sum([
                            1 for signal in [
                                tech.get('rsi_signal') is not None,
                                tech.get('macd_trend') is not None,
                                tech.get('supertrend_signal') is not None
                            ] if signal
                        ])
                        
                        if total_signals > 0:
                            signal_strength = bullish_signals / total_signals
                            if signal_strength >= 0.67:
                                st.success(f"🟢 Strong Bullish Signals ({bullish_signals}/{total_signals})")
                            elif signal_strength >= 0.34:
                                st.info(f"🟡 Mixed Signals ({bullish_signals}/{total_signals})")
                            else:
                                st.error(f"🔴 Bearish Signals ({bullish_signals}/{total_signals})")
                        
                    else:
                        st.warning("⚠️ Technical indicators not available")
                
                with tab3:
                    st.markdown("#### 52-Week Performance")
                    
                    fund = analysis['fundamentals']
                    if fund['pct_from_high'] is not None:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("From 52W High", f"{fund['pct_from_high']:+.1f}%",
                                     delta=f"High: ₹{fund['52w_high']:,.2f}")
                            st.metric("From 52W Low", f"{fund['pct_from_low']:+.1f}%",
                                     delta=f"Low: ₹{fund['52w_low']:,.2f}")
                        
                        with col2:
                            # Visual progress bar
                            current_position = ((fund['price'] - fund['52w_low']) / (fund['52w_high'] - fund['52w_low'])) * 100
                            st.markdown("**52-Week Range Position**")
                            st.progress(current_position / 100)
                            st.caption(f"**{current_position:.1f}%** of 52-week range")
                            
                            # Performance status
                            if current_position > 80:
                                st.success("🟢 Very Strong Position")
                            elif current_position > 60:
                                st.success("🟢 Strong Position")
                            elif current_position > 40:
                                st.info("🟡 Moderate Position")
                            elif current_position > 20:
                                st.warning("🟠 Weak Position")
                            else:
                                st.error("🔴 Very Weak Position")
                    else:
                        st.info("📊 52-week data not available")
                
                with tab4:
                    st.markdown("#### Key Financial Metrics")
                    
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
        
        st.markdown("### 🔍 Industry Explorer")
        
        # Show top industries by stock count
        top_industries = get_top_industries(20)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Top 20 Industries by Stock Count")
            
            # Create bar chart
            industries_df = pd.DataFrame(list(top_industries.items()), columns=['Industry', 'Stock Count'])
            fig = px.bar(
                industries_df, 
                x='Stock Count', 
                y='Industry',
                orientation='h',
                title="Stock Count by Industry",
                height=600
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Industry Statistics")
            
            # Show stats
            total_categories = len(get_all_categories())
            avg_stocks_per_industry = TOTAL_STOCKS // total_categories
            
            st.metric("Total Industries", f"{total_categories}")
            st.metric("Total Stocks", f"{TOTAL_STOCKS:,}")
            st.metric("Avg Stocks/Industry", f"{avg_stocks_per_industry}")
            
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
                <p><strong>Sample Companies:</strong> {', '.join(list(industry_stocks.values())[:5])}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Show all stocks in the industry
            if st.expander(f"📋 All {len(industry_stocks)} Stocks in {selected_explore_industry}"):
                stocks_df = pd.DataFrame(list(industry_stocks.items()), columns=['Ticker', 'Company Name'])
                st.dataframe(stocks_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
