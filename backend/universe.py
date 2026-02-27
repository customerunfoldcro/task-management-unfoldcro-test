"""Universe loader: NIFTY 50 + NIFTY Next 50 symbols."""

# Hard-coded universe for reliability. In production, pull from NSE index constituents.
# Yahoo Finance uses .NS suffix for NSE-listed stocks.

NIFTY_50 = [
    {"symbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "industry": "Oil & Gas Refining"},
    {"symbol": "TCS", "name": "Tata Consultancy Services", "sector": "Technology", "industry": "IT Services"},
    {"symbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "INFY", "name": "Infosys", "sector": "Technology", "industry": "IT Services"},
    {"symbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "Consumer Staples", "industry": "FMCG"},
    {"symbol": "ITC", "name": "ITC", "sector": "Consumer Staples", "industry": "FMCG"},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Financials", "industry": "Banks"},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Telecom", "industry": "Telecom Services"},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "LT", "name": "Larsen & Toubro", "sector": "Industrials", "industry": "Construction"},
    {"symbol": "AXISBANK", "name": "Axis Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Financials", "industry": "NBFC"},
    {"symbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Materials", "industry": "Paints"},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Consumer Discretionary", "industry": "Automobiles"},
    {"symbol": "TITAN", "name": "Titan Company", "sector": "Consumer Discretionary", "industry": "Jewellery"},
    {"symbol": "SUNPHARMA", "name": "Sun Pharma", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Consumer Discretionary", "industry": "Automobiles"},
    {"symbol": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Materials", "industry": "Cement"},
    {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "Financials", "industry": "Financial Services"},
    {"symbol": "WIPRO", "name": "Wipro", "sector": "Technology", "industry": "IT Services"},
    {"symbol": "ONGC", "name": "Oil & Natural Gas Corp", "sector": "Energy", "industry": "Oil & Gas"},
    {"symbol": "NTPC", "name": "NTPC", "sector": "Utilities", "industry": "Power Generation"},
    {"symbol": "POWERGRID", "name": "Power Grid Corp", "sector": "Utilities", "industry": "Power Transmission"},
    {"symbol": "M&M", "name": "Mahindra & Mahindra", "sector": "Consumer Discretionary", "industry": "Automobiles"},
    {"symbol": "TATASTEEL", "name": "Tata Steel", "sector": "Materials", "industry": "Steel"},
    {"symbol": "HCLTECH", "name": "HCL Technologies", "sector": "Technology", "industry": "IT Services"},
    {"symbol": "ADANIENT", "name": "Adani Enterprises", "sector": "Industrials", "industry": "Conglomerate"},
    {"symbol": "ADANIPORTS", "name": "Adani Ports", "sector": "Industrials", "industry": "Ports"},
    {"symbol": "COALINDIA", "name": "Coal India", "sector": "Energy", "industry": "Mining"},
    {"symbol": "JSWSTEEL", "name": "JSW Steel", "sector": "Materials", "industry": "Steel"},
    {"symbol": "TECHM", "name": "Tech Mahindra", "sector": "Technology", "industry": "IT Services"},
    {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance", "sector": "Financials", "industry": "Insurance"},
    {"symbol": "SBILIFE", "name": "SBI Life Insurance", "sector": "Financials", "industry": "Insurance"},
    {"symbol": "BRITANNIA", "name": "Britannia Industries", "sector": "Consumer Staples", "industry": "Food Products"},
    {"symbol": "GRASIM", "name": "Grasim Industries", "sector": "Materials", "industry": "Cement & Textiles"},
    {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "DIVISLAB", "name": "Divi's Laboratories", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "NESTLEIND", "name": "Nestle India", "sector": "Consumer Staples", "industry": "Food Products"},
    {"symbol": "CIPLA", "name": "Cipla", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "DRREDDY", "name": "Dr Reddy's Labs", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "EICHERMOT", "name": "Eicher Motors", "sector": "Consumer Discretionary", "industry": "Automobiles"},
    {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals", "sector": "Healthcare", "industry": "Hospitals"},
    {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp", "sector": "Consumer Discretionary", "industry": "Automobiles"},
    {"symbol": "BPCL", "name": "Bharat Petroleum", "sector": "Energy", "industry": "Oil & Gas"},
    {"symbol": "TATACONSUM", "name": "Tata Consumer Products", "sector": "Consumer Staples", "industry": "Food Products"},
    {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto", "sector": "Consumer Discretionary", "industry": "Automobiles"},
    {"symbol": "HINDALCO", "name": "Hindalco Industries", "sector": "Materials", "industry": "Metals"},
    {"symbol": "SHRIRAMFIN", "name": "Shriram Finance", "sector": "Financials", "industry": "NBFC"},
    {"symbol": "WIPRO", "name": "Wipro", "sector": "Technology", "industry": "IT Services"},
]

NIFTY_NEXT_50 = [
    {"symbol": "ADANIGREEN", "name": "Adani Green Energy", "sector": "Utilities", "industry": "Renewable Energy"},
    {"symbol": "ADANIPOWER", "name": "Adani Power", "sector": "Utilities", "industry": "Power Generation"},
    {"symbol": "AMBUJACEM", "name": "Ambuja Cements", "sector": "Materials", "industry": "Cement"},
    {"symbol": "BANKBARODA", "name": "Bank of Baroda", "sector": "Financials", "industry": "Banks"},
    {"symbol": "BEL", "name": "Bharat Electronics", "sector": "Industrials", "industry": "Defence"},
    {"symbol": "BERGEPAINT", "name": "Berger Paints", "sector": "Materials", "industry": "Paints"},
    {"symbol": "BOSCHLTD", "name": "Bosch", "sector": "Consumer Discretionary", "industry": "Auto Components"},
    {"symbol": "CANBK", "name": "Canara Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "CHOLAFIN", "name": "Cholamandalam Finance", "sector": "Financials", "industry": "NBFC"},
    {"symbol": "COLPAL", "name": "Colgate-Palmolive India", "sector": "Consumer Staples", "industry": "Personal Care"},
    {"symbol": "DABUR", "name": "Dabur India", "sector": "Consumer Staples", "industry": "FMCG"},
    {"symbol": "DLF", "name": "DLF", "sector": "Real Estate", "industry": "Real Estate Development"},
    {"symbol": "GAIL", "name": "GAIL India", "sector": "Energy", "industry": "Natural Gas"},
    {"symbol": "GODREJCP", "name": "Godrej Consumer Products", "sector": "Consumer Staples", "industry": "FMCG"},
    {"symbol": "HAVELLS", "name": "Havells India", "sector": "Industrials", "industry": "Electrical Equipment"},
    {"symbol": "HAL", "name": "Hindustan Aeronautics", "sector": "Industrials", "industry": "Defence"},
    {"symbol": "ICICIGI", "name": "ICICI Lombard", "sector": "Financials", "industry": "Insurance"},
    {"symbol": "ICICIPRULI", "name": "ICICI Prudential Life", "sector": "Financials", "industry": "Insurance"},
    {"symbol": "IDEA", "name": "Vodafone Idea", "sector": "Telecom", "industry": "Telecom Services"},
    {"symbol": "INDHOTEL", "name": "Indian Hotels", "sector": "Consumer Discretionary", "industry": "Hotels"},
    {"symbol": "INDUSTOWER", "name": "Indus Towers", "sector": "Telecom", "industry": "Telecom Infrastructure"},
    {"symbol": "IOC", "name": "Indian Oil Corp", "sector": "Energy", "industry": "Oil & Gas Refining"},
    {"symbol": "IRCTC", "name": "IRCTC", "sector": "Consumer Discretionary", "industry": "Travel"},
    {"symbol": "JINDALSTEL", "name": "Jindal Steel & Power", "sector": "Materials", "industry": "Steel"},
    {"symbol": "LICI", "name": "LIC of India", "sector": "Financials", "industry": "Insurance"},
    {"symbol": "LTIM", "name": "LTIMindtree", "sector": "Technology", "industry": "IT Services"},
    {"symbol": "LUPIN", "name": "Lupin", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "MARICO", "name": "Marico", "sector": "Consumer Staples", "industry": "FMCG"},
    {"symbol": "MCDOWELL-N", "name": "United Spirits", "sector": "Consumer Staples", "industry": "Alcoholic Beverages"},
    {"symbol": "NAUKRI", "name": "Info Edge (Naukri)", "sector": "Technology", "industry": "Internet Services"},
    {"symbol": "NHPC", "name": "NHPC", "sector": "Utilities", "industry": "Hydro Power"},
    {"symbol": "PFC", "name": "Power Finance Corp", "sector": "Financials", "industry": "NBFC"},
    {"symbol": "PIDILITIND", "name": "Pidilite Industries", "sector": "Materials", "industry": "Adhesives"},
    {"symbol": "PNB", "name": "Punjab National Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "RECLTD", "name": "REC Limited", "sector": "Financials", "industry": "NBFC"},
    {"symbol": "SAIL", "name": "Steel Authority of India", "sector": "Materials", "industry": "Steel"},
    {"symbol": "SIEMENS", "name": "Siemens India", "sector": "Industrials", "industry": "Electrical Equipment"},
    {"symbol": "SRF", "name": "SRF", "sector": "Materials", "industry": "Chemicals"},
    {"symbol": "TATAPOWER", "name": "Tata Power", "sector": "Utilities", "industry": "Power Generation"},
    {"symbol": "TRENT", "name": "Trent", "sector": "Consumer Discretionary", "industry": "Retail"},
    {"symbol": "TORNTPHARM", "name": "Torrent Pharma", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "UNIONBANK", "name": "Union Bank of India", "sector": "Financials", "industry": "Banks"},
    {"symbol": "VEDL", "name": "Vedanta", "sector": "Materials", "industry": "Mining & Metals"},
    {"symbol": "YESBANK", "name": "Yes Bank", "sector": "Financials", "industry": "Banks"},
    {"symbol": "ZOMATO", "name": "Zomato", "sector": "Technology", "industry": "Internet Services"},
    {"symbol": "ZYDUSLIFE", "name": "Zydus Lifesciences", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"symbol": "PAYTM", "name": "One97 Communications", "sector": "Technology", "industry": "Fintech"},
    {"symbol": "POLYCAB", "name": "Polycab India", "sector": "Industrials", "industry": "Electrical Equipment"},
    {"symbol": "ABB", "name": "ABB India", "sector": "Industrials", "industry": "Electrical Equipment"},
    {"symbol": "MAXHEALTH", "name": "Max Healthcare", "sector": "Healthcare", "industry": "Hospitals"},
]


def get_full_universe():
    """Return the full 100-stock universe with Yahoo Finance symbols."""
    seen = set()
    universe = []
    rank = 1

    for stock in NIFTY_50:
        if stock["symbol"] in seen:
            continue
        seen.add(stock["symbol"])
        universe.append({
            **stock,
            "yf_symbol": f"{stock['symbol']}.NS",
            "universe": "NIFTY50",
            "universe_rank": rank,
        })
        rank += 1

    for stock in NIFTY_NEXT_50:
        if stock["symbol"] in seen:
            continue
        seen.add(stock["symbol"])
        universe.append({
            **stock,
            "yf_symbol": f"{stock['symbol']}.NS",
            "universe": "NEXT50",
            "universe_rank": rank,
        })
        rank += 1

    return universe
