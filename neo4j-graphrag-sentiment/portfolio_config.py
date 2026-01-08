"""
Portfolio configuration for sentiment data collection.
Defines all tickers across technology, energy, and benchmark sectors.
"""

PORTFOLIO_TICKERS = [
    {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'sector': 'technology',
        'type': 'stock',
        'status': 'COMPLETE'
    },
    {
        'symbol': 'MSFT',
        'name': 'Microsoft Corporation',
        'sector': 'technology',
        'type': 'stock',
        'status': 'PENDING'
    },
    {
        'symbol': 'GOOGL',
        'name': 'Alphabet Inc.',
        'sector': 'technology',
        'type': 'stock',
        'status': 'PENDING'
    },
    {
        'symbol': 'NVDA',
        'name': 'NVIDIA Corporation',
        'sector': 'technology',
        'type': 'stock',
        'status': 'COMPLETE'
    },
    {
        'symbol': 'META',
        'name': 'Meta Platforms Inc.',
        'sector': 'technology',
        'type': 'stock',
        'status': 'PENDING'
    },
    {
        'symbol': 'XLK',
        'name': 'Technology Select Sector SPDR ETF',
        'sector': 'technology',
        'type': 'etf',
        'status': 'PENDING'
    },
    {
        'symbol': 'XOM',
        'name': 'ExxonMobil Corporation',
        'sector': 'energy',
        'type': 'stock',
        'status': 'PENDING'
    },
    {
        'symbol': 'CVX',
        'name': 'Chevron Corporation',
        'sector': 'energy',
        'type': 'stock',
        'status': 'PENDING'
    },
    {
        'symbol': 'COP',
        'name': 'ConocoPhillips',
        'sector': 'energy',
        'type': 'stock',
        'status': 'PENDING'
    },
    {
        'symbol': 'XLE',
        'name': 'Energy Select Sector SPDR ETF',
        'sector': 'energy',
        'type': 'etf',
        'status': 'PENDING'
    },
    {
        'symbol': 'SPY',
        'name': 'S&P 500 ETF Trust',
        'sector': 'benchmark',
        'type': 'etf',
        'status': 'PENDING'
    },
    {
        'symbol': 'QQQ',
        'name': 'Invesco QQQ Trust',
        'sector': 'benchmark',
        'type': 'etf',
        'status': 'PENDING'
    },
    {
        'symbol': 'IWM',
        'name': 'iShares Russell 2000 ETF',
        'sector': 'benchmark',
        'type': 'etf',
        'status': 'PENDING'
    }
]


def get_portfolio_by_sector():
    """Group portfolio tickers by sector."""
    sectors = {}
    for ticker in PORTFOLIO_TICKERS:
        sector = ticker['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(ticker)
    return sectors


def get_pending_tickers():
    """Get list of tickers with PENDING status."""
    return [t for t in PORTFOLIO_TICKERS if t['status'] == 'PENDING']


def get_ticker_info(symbol: str):
    """Get ticker information by symbol."""
    for ticker in PORTFOLIO_TICKERS:
        if ticker['symbol'] == symbol:
            return ticker
    return None


def get_all_symbols():
    """Get list of all ticker symbols."""
    return [t['symbol'] for t in PORTFOLIO_TICKERS]


def get_collection_params(ticker_type: str):
    """
    Get recommended collection parameters by ticker type.

    Args:
        ticker_type: 'stock' or 'etf'

    Returns:
        Dict with days, max_records, and gemini_top params
    """
    if ticker_type == 'etf':
        return {
            'days': 14,
            'max_records': 300,
            'gemini_top': 25
        }
    else:
        return {
            'days': 7,
            'max_records': 250,
            'gemini_top': 20
        }


SECTOR_ALLOCATION = {
    'technology': {'min': 0.52, 'max': 0.58, 'positions': 6},
    'energy': {'min': 0.10, 'max': 0.14, 'positions': 4},
    'benchmark': {'min': 0.30, 'max': 0.35, 'positions': 3}
}


if __name__ == '__main__':
    print("Portfolio Configuration Summary")
    print("="*60)

    by_sector = get_portfolio_by_sector()
    for sector, tickers in by_sector.items():
        print(f"\n{sector.upper()} ({len(tickers)} positions):")
        for t in tickers:
            status = t['status']
            print(f"  {t['symbol']:6s} - {t['name']:40s} [{status}]")

    print(f"\n{'='*60}")
    print(f"Total Portfolio: {len(PORTFOLIO_TICKERS)} positions")

    pending = get_pending_tickers()
    print(f"Pending Collection: {len(pending)} tickers")
    print(f"Completed: {len(PORTFOLIO_TICKERS) - len(pending)} tickers")
