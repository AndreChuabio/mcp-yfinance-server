# MCP YFinance Server - Simple POC with Paper Trading

A minimal MCP (Model Context Protocol) server that provides stock data tools using yfinance for financial data q### 4. get_portfolio_balance
View your current REAL Paper Invest account balance and positions.

**Parameters:** None

**Example Output:**
```
💰 REAL Paper Invest Portfolio

💵 Account Status: Connected to Paper Invest
📊 Portfolio ID: 4996db29-73b2-42d9-a548-e3034aaa8451
📋 Orders: Recent orders from your account

✅ This is your REAL Paper Invest account - orders will be executed for real!
```paper trading functionality.

## 🌟 Features

This MCP server provides stock data analysis and paper trading tools:

### Stock Data Tools
1. **get_stock_price** - Get current stock price and basic trading information
2. **get_stock_history** - Get historical price data for specified date ranges  
3. **get_stock_info** - Get detailed company information and key financial metrics

### Paper Trading Tools (REAL API!)
4. **get_portfolio_balance** - View your REAL Paper Invest account balance and positions
5. **place_buy_order** - Execute a REAL buy order in your Paper Invest account  
6. **place_sell_order** - Execute a REAL sell order in your Paper Invest account

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (MCP requires Python 3.10+)
- Virtual environment (recommended)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "/Users/andrechuabio/MCP quant"
   ```

2. **The virtual environment and dependencies are already set up!**
   - Virtual environment: `.venv/`
   - Required packages: `mcp`, `yfinance`, `pydantic`, `requests`, `python-dotenv`

3. **Test the server:**
   ```bash
   .venv/bin/python test_paper_trading.py
   ```

## 🚀 Usage

### Claude Desktop (Recommended)
1. Follow the [setup guide](docs/CLAUDE_DESKTOP_SETUP.md)
2. Use natural language: "Buy 10 shares of AAPL", "What's my portfolio balance?"

### VS Code Development  
```bash
# Run tests
.venv/bin/python tests/test_server.py

# Demo all features
.venv/bin/python tests/demo_complete.py
```

- `claude_desktop_config.json` - Claude Desktop configuration  
- `.env` - Paper Invest API credentials

## 🛠 Tools Documentation

### Stock Data Tools

### 1. get_stock_price
Get current stock price and basic trading information.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)

**Example Output:**
```
📈 AAPL - Apple Inc.

Current Price: $175.23
Change: +2.15 (+1.24%)
Today's Range: $172.50 - $176.00
Open: $173.08
Volume: 45,234,567

Market Cap: $2,756,789,123,456
Sector: Technology
Industry: Consumer Electronics
```

### 2. get_stock_history
Get historical price data for a specified time period.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol
- `period` (string, optional): Time period - one of: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max (default: 1mo)

**Example Output:**
```
📊 AAPL Historical Data (1mo)

Period: 2024-08-09 to 2024-09-09
Total Return: +5.67%
Price Range: $170.12 - $178.45
Average Volume: 52,345,678

Recent Data (Last 5 Trading Days):
2024-09-05: $175.23 (Vol: 45,234,567)
2024-09-04: $173.45 (Vol: 48,123,456)
...
```

### 3. get_stock_info
Get detailed company information and financial metrics.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol

**Example Output:**
```
🏢 Apple Inc. (AAPL)

Basic Information:
• Sector: Technology
• Industry: Consumer Electronics
• Country: United States
• Employees: 164,000

Financial Metrics:
• Market Cap: $2,756,789,123,456
• Enterprise Value: $2,698,456,789,012
• P/E Ratio: 28.45
• Forward P/E: 25.67
...
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Test core server functionality
.venv/bin/python tests/test_server.py

# Test paper trading features
.venv/bin/python tests/test_paper_trading.py

# Complete demo with all features
.venv/bin/python tests/demo_complete.py
```

This will test all six tools with various stock symbols including:
- ✅ Valid symbols: AAPL, GOOGL, TSLA
- ❌ Invalid symbols: Proper error handling
- 📈 Paper trading: Buy/sell orders and portfolio management

## 📁 Project Structure

```
MCP quant/
├── mcp_yfinance_server.py      # Main MCP server
├── claude_desktop_config.json  # Claude Desktop config
├── .env                        # API credentials
├── requirements.txt            # Dependencies
├── docs/CLAUDE_DESKTOP_SETUP.md # Setup guide
└── tests/                      # Test scripts
```

...
```

### Paper Trading Tools

### 4. get_portfolio_balance
View your current paper trading portfolio balance and positions from your Paper Invest account.

**Parameters:** None

**Example Output:**
```
💰 Paper Trading Portfolio (Paper Invest)

� Portfolio Status:
Connected to Paper Invest account
Portfolio ID: your_portfolio_id

📋 Recent Orders: 5 total

*Note: Live connection to Paper Invest API*
```

### 5. place_buy_order
Execute a REAL buy order using your actual Paper Invest account.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol
- `shares` (number, required): Number of shares to buy

**Example Output:**
```
✅ Buy Order Submitted to Paper Invest

Symbol: NVDA
Shares: 100
Order Type: MARKET
Reference Price: $176.88
Estimated Cost: $17,687.50

Paper Invest Order Details:
Order ID: fc96371e-c114-416e-b16c-7fe89ea90429
Status: RESERVING
Created: 2025-09-11T17:54:54.634Z

✨ Order has been sent to your real Paper Invest account!
```

### 6. place_sell_order
Execute a REAL sell order using your actual Paper Invest account.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol  
- `shares` (number, required): Number of shares to sell

**Example Output:**
```
✅ Sell Order Submitted to Paper Invest

Symbol: PSKY
Shares: 50
Order Type: MARKET
Reference Price: $15.97
Estimated Proceeds: $798.50

Paper Invest Order Details:
Order ID: 84edc9f7-ba82-4a0b-882c-6277c3167280
Status: RESERVING
Created: 2025-09-11T17:55:00Z

✨ Order has been sent to your real Paper Invest account!
```

## 📈 Paper Trading Features

- **REAL Paper Invest Integration** - Connected to your actual Paper Invest API account
- **LIVE Order Placement** - All orders are placed directly in your real Paper Invest account
- **JWT Authentication** - Secure API authentication with Paper Invest
- **Market Orders** - Simplified order types using real market execution
- **Real-time Pricing** - Uses current market prices from yfinance for reference
- **NO SIMULATION** - All orders are real and will show up in your Paper Invest dashboard

**IMPORTANT:** This server places REAL orders in your Paper Invest account. No simulation or fake portfolios!

## 🎯 Success Criteria Met

✅ **Server starts without errors** - Tested and verified  
✅ **Tools respond correctly to valid stock symbols** - All major stocks work  
✅ **Graceful error handling for invalid symbols** - Proper error messages  
✅ **Easy integration with Claude Desktop** - Configuration provided  
✅ **Simple and functional POC** - Clean, focused implementation  
✅ **Paper trading functionality** - REAL Paper Invest API integration (no simulation)
✅ **Real-time pricing integration** - Live stock prices for trading decisions
✅ **Portfolio management** - Connected to your actual Paper Invest account
✅ **JWT Authentication** - Secure API integration with Paper Invest
✅ **Live order execution** - All orders executed in real Paper Invest account

## 🔧 Technical Details

- **MCP SDK Version:** 1.13.1
- **Python Version:** 3.11.5
- **YFinance Version:** 0.2.65
- **Architecture:** Async/await based for performance
- **Error Handling:** Comprehensive exception handling with user-friendly messages

## 🚨 Error Handling

The server handles various error conditions:
- Invalid stock symbols
- Network connectivity issues  
- Yahoo Finance API limitations
- Missing or incomplete data

All errors are returned as descriptive text messages rather than raw exceptions.

## 📊 Supported Stock Symbols

The server works with any valid stock symbol supported by Yahoo Finance, including:
- US stocks (AAPL, GOOGL, MSFT, etc.)
- International stocks with proper suffixes
- ETFs and mutual funds
- Cryptocurrencies (BTC-USD, ETH-USD, etc.)

## 🤝 Contributing

This is a simple POC implementation. For production use, consider:
- Adding authentication/rate limiting
- Implementing caching mechanisms
- Adding more financial data sources
- Enhanced error recovery

---

**Built with ❤️ for the MCP ecosystem**
