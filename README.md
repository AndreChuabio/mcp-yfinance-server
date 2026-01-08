# MCP YFinance Server - Complete Financial Analysis Suite

A comprehensive MCP (Model Context Protocol) server that combines real-time sentiment analysis, stock data analysis, and paper trading functionality. Includes Node.js HTTP server for sentiment analysis and Python MCP server with Neo4j graph database integration.

## 🌟 Features

### Stock Data Analysis
- Get current stock prices and trading information
- Historical price data with customizable periods
- Detailed company information and financial metrics

### Advanced Sentiment Analysis  
- Real-time sentiment analysis using Google Gemini AI
- News sentiment from Alpha Vantage and NewsAPI
- Social media sentiment from Reddit (r/wallstreetbets, r/stocks, r/investing)
- Intelligent caching to minimize API calls
- Batch processing for multiple tickers
- Historical sentiment tracking
- Trending ticker detection

### Neo4j Graph Database Integration (Python MCP Server)
- GraphRAG for sentiment data queries via MCP tools
- Stock sentiment tracking with historical data
- Article-to-stock relationship mapping
- Multi-source sentiment aggregation
- Time-series sentiment analysis
- Cross-stock sentiment comparison
- Keyword-based article search

### Paper Trading (REAL API Integration)
- View your REAL Paper Invest account balance and positions
- Execute REAL buy/sell orders in your Paper Invest account
- JWT authentication with Paper Invest API
- Live order execution and portfolio management

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ for sentiment analysis server
- Python 3.11+ for MCP server (if using Python components)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd mcp-server
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

4. **Add your API keys to `.env`:**
   - `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - `ALPHA_VANTAGE_API_KEY`: Get from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - `NEWS_API_KEY`: Get from [NewsAPI](https://newsapi.org/register)
   - `FMP_API_KEY`: Get from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs)
   - Reddit credentials (optional): Get from [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Neo4j credentials (for Python MCP server): `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`

5. **Start the Node.js sentiment server:**
   ```bash
   npm start
   ```

6. **Or start the Python MCP server (with Neo4j):**
   ```bash
   python3 mcp_yfinance_server.py
   ```

## 📊 Sentiment Analysis API Endpoints (Node.js Server)

### Single Ticker Sentiment
```bash
GET /sentiment/ticker/{symbol}?social=true
```

Analyzes sentiment for a single ticker with comprehensive source breakdown.

**Parameters:**
- `symbol`: Stock ticker (e.g., AAPL, TSLA)
- `social`: Include social media sentiment (optional, default: false)

**Response:**
```json
{
  "ticker": "AAPL",
  "timestamp": "2025-12-12T00:00:00Z",
  "sentiment_score": 0.45,
  "sentiment_label": "positive",
  "confidence": 0.78,
  "sources_analyzed": 25,
  "source_breakdown": {
    "news": {"score": 0.52, "count": 15},
    "social": {"score": 0.38, "count": 10}
  },
  "top_headlines": [
    {
      "title": "Apple announces new product",
      "score": 0.8,
      "source": "Reuters",
      "url": "https://..."
    }
  ]
}
```

### Batch Analysis
```bash
POST /sentiment/analyze
```

Analyzes multiple tickers simultaneously for efficient bulk processing.

**Request Body:**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "includeSocial": false,
  "newsLimit": 20,
  "socialLimit": 30
}
```

### Trending Sentiment Detection
```bash
GET /sentiment/trending?tickers=AAPL,TSLA,NVDA&threshold=0.3
```

Identifies tickers with significant sentiment shifts and momentum.

## 🛠 MCP Tools Documentation

### Stock Data Tools

#### get_stock_price
Get current stock price and basic trading information.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)

#### get_stock_history  
Get historical price data for specified date ranges.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol
- `period` (string, optional): 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: 1mo)

#### get_stock_info
Get detailed company information and key financial metrics.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol

### Paper Trading Tools

#### get_portfolio_balance
View your current REAL Paper Invest account balance and positions.

**Parameters:** None

#### place_buy_order
Execute a REAL buy order in your Paper Invest account.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol
- `shares` (number, required): Number of shares to buy

#### place_sell_order  
Execute a REAL sell order in your Paper Invest account.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol
- `shares` (number, required): Number of shares to sell

## 📈 Sentiment Scoring System

Sentiment scores range from -1 (very negative) to +1 (very positive):
- **0.2 to 1.0**: Positive sentiment - Bullish indicators
- **-0.2 to 0.2**: Neutral sentiment - Mixed signals  
- **-1.0 to -0.2**: Negative sentiment - Bearish indicators

## 🧪 Testing

### Run Sentiment Analysis Tests:
```bash
npm test
```

### Test Individual Components:
```bash
# Start sentiment server
npm start

# In another terminal
node tests/sentiment.test.js
node tests/health.test.js
```

### Test Paper Trading:
```bash
# Test paper trading functionality
.venv/bin/python tests/test_paper_trading.py

# Complete demo with all features
.venv/bin/python tests/demo_complete.py
```

## 🏗 Architecture

```
mcp-server/
├── src/
│   ├── index.js                    # Node.js HTTP server with sentiment API
│   └── sentiment/
│       ├── sentimentAnalyzer.js    # Core sentiment logic with Gemini AI
│       ├── newsProvider.js         # Financial news integration
│       ├── socialProvider.js       # Social media sentiment
│       └── cache.js                # Intelligent caching layer
├── mcp_yfinance_server.py         # Python MCP server with Neo4j integration
├── tests/                          # Comprehensive test suite
│   ├── health.test.js              # Node.js server tests
│   ├── sentiment.test.js           # Sentiment analysis tests
│   └── test_neo4j_mcp.py          # Neo4j MCP tools tests
└── docs/                          # Setup and configuration guides
```

## 📊 Python MCP Server Tools (Claude Desktop)

## 📊 Python MCP Server Tools (Claude Desktop)

The Python MCP server (`mcp_yfinance_server.py`) provides 17 tools for Claude Desktop:

### Stock Data Tools (3)
- **get_stock_price** - Current price and trading info
- **get_stock_history** - Historical price data
- **get_stock_info** - Detailed company information

### Paper Trading Tools (3)
- **get_portfolio_balance** - Account balance and positions
- **place_buy_order** - Execute buy orders
- **place_sell_order** - Execute sell orders

### MongoDB Tools (4)
- **query_portfolio_holdings** - Query holdings data
- **query_price_history** - Historical price queries
- **query_risk_metrics** - Risk calculations (VaR, CVaR, Sharpe)
- **list_mongodb_collections** - Database collections

### Neo4j Sentiment Tools (7)
- **get_stock_sentiment** - Current sentiment summary with article count
- **get_recent_articles** - Recent news with sentiment filtering
- **get_sentiment_timeline** - 7-day sentiment evolution
- **compare_stock_sentiments** - Multi-stock comparison
- **search_articles_by_keyword** - Keyword-based article search
- **get_sentiment_statistics** - Aggregate statistics
- **get_data_sources_breakdown** - Sentiment by data source

All Neo4j tools query the graph database containing 103+ articles with sentiment scores from multiple sources (Yahoo RSS, Google RSS, Alpha Vantage).

## ⚡ Performance & Optimization

- **Intelligent Caching**: Reduces API calls by 60%+ with 30-minute TTL
- **Batch Processing**: Analyze 5 tickers in under 5 seconds
- **Rate Limiting**: Respects all API limits and provides fallback strategies
- **Async Architecture**: Non-blocking operations for optimal performance

## 🔒 API Rate Limits & Management

**Free Tier Limits:**
- Gemini AI: 60 requests/minute  
- Alpha Vantage: 25 requests/day
- NewsAPI: 100 requests/day
- Reddit: 60 requests/minute
- Financial Modeling Prep: 250 requests/day

**Rate Limit Strategies:**
- Automatic fallback to VADER sentiment when Gemini is rate limited
- Intelligent caching prevents duplicate API calls
- Batch processing optimizes API usage
- Graceful degradation when services are unavailable

## 🚨 Error Handling & Reliability

The server provides comprehensive error handling for:
- Invalid stock symbols with helpful suggestions
- Network connectivity issues and timeouts
- API service limitations and outages  
- Missing or incomplete financial data
- Authentication failures with clear guidance

## 🎯 Production Readiness Features

- **Real Paper Trading Integration**: Live connection to Paper Invest API
- **Comprehensive Logging**: Full request/response logging for debugging
- **Environment Configuration**: Secure API key management
- **Modular Architecture**: Easily extendable for new data sources
- **Test Coverage**: Full test suite for all major functionality

## 🔮 Future Enhancements

1. **Advanced Analytics**: Technical indicator integration
2. **Real-time Streaming**: WebSocket support for live updates  
3. **Database Persistence**: Historical data storage for backtesting
4. **Visualization Dashboard**: Interactive charts and analytics
5. **ML Model Integration**: Custom sentiment models and predictions
6. **Multi-broker Support**: Additional trading platform integrations

## 📊 Supported Data Sources

**Stock Symbols:** All Yahoo Finance supported symbols including:
- US stocks (AAPL, GOOGL, MSFT, etc.)
- International markets with proper suffixes
- ETFs, mutual funds, and indexes
- Cryptocurrencies (BTC-USD, ETH-USD, etc.)

**News Sources:** 
- Alpha Vantage financial news
- NewsAPI comprehensive coverage
- Financial Modeling Prep earnings data

**Social Media:**
- Reddit (r/wallstreetbets, r/stocks, r/investing)
- Twitter integration (configurable)

## 👨‍💻 Author

**Andre Chua** (andre102599@gmail.com)  
GitHub: [https://github.com/AndreChuabio](https://github.com/AndreChuabio)

---

**Built for quantitative traders and financial analysts who demand real-time sentiment intelligence combined with seamless trading execution.**
