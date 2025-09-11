# MCP YFinance Server - Simple POC with Paper Trading

A minimal MCP (Model Context Protocol) server that provides stock data tools using yfinance for financial data queries and basic paper trading functionality.

## 🌟 Features

This MCP server provides stock data analysis and paper trading tools:

### Stock Data Tools
1. **get_stock_price** - Get current stock price and basic trading information
2. **get_stock_history** - Get historical price data for specified date ranges  
3. **get_stock_info** - Get detailed company information and key financial metrics

### Paper Trading Tools (NEW!)
4. **get_portfolio_balance** - View your paper trading portfolio balance and positions
5. **place_buy_order** - Execute a buy order in your paper trading account  
6. **place_sell_order** - Execute a sell order in your paper trading account

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

### Running the MCP Server

**For direct testing:**
```bash
.venv/bin/python mcp_yfinance_server.py
```

**For Claude Desktop integration:**
Use the provided `claude_desktop_config.json` configuration file.

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
.venv/bin/python test_server.py
```

This will test all three tools with various stock symbols including:
- ✅ Valid symbols: AAPL, GOOGL, TSLA
- ❌ Invalid symbols: Proper error handling

## 📁 Project Structure

```
MCP quant/
├── mcp_yfinance_server.py      # Main MCP server implementation
├── test_server.py              # Test script for verification
├── claude_desktop_config.json  # Configuration for Claude Desktop
├── mcp.json                    # MCP server configuration
├── README.md                   # This file
├── .venv/                      # Python virtual environment
└── .github/
    └── prompts/
        └── mcp-yfinance.prompt.md  # Original requirements
```

...
```

### Paper Trading Tools

### 4. get_portfolio_balance
View your current paper trading portfolio balance and positions.

**Parameters:** None

**Example Output:**
```
💰 Paper Trading Portfolio

💵 Cash Balance: $97,712.88
📈 Position Value: $2,287.12
🏦 Total Portfolio Value: $100,000.00

📊 Current Positions:
• AAPL: 10 shares @ $228.71 (Avg Cost: $228.71, P&L: $+0.00 [+0.0%])

📋 Recent Orders: 1 total
```

### 5. place_buy_order
Execute a buy order for a specified stock and number of shares.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol
- `shares` (number, required): Number of shares to buy

**Example Output:**
```
✅ Buy Order Executed

Symbol: AAPL
Shares: 10
Price: $228.71
Total Cost: $2287.12

Updated Portfolio:
Cash Balance: $97,712.88
AAPL Position: 10 shares @ $228.71 avg cost
```

### 6. place_sell_order
Execute a sell order for a specified stock and number of shares.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol  
- `shares` (number, required): Number of shares to sell

**Example Output:**
```
✅ Sell Order Executed

Symbol: AAPL
Shares: 5
Price: $228.71
Total Proceeds: $1143.56
P&L: $+0.00 (+0.0%)

Updated Portfolio:
Cash Balance: $98,856.44
AAPL Position: 5 shares remaining
```

## 📈 Paper Trading Features

- **$100,000 Starting Balance** - Begin with realistic capital
- **Real-time Pricing** - Uses current market prices from yfinance
- **Position Tracking** - Automatic P&L calculation and position management
- **Order History** - Track all your trades
- **Risk-free Trading** - Perfect for learning and strategy testing

**Note:** This is a POC implementation using in-memory storage. Positions reset when the server restarts.

## 🎯 Success Criteria Met

✅ **Server starts without errors** - Tested and verified  
✅ **Tools respond correctly to valid stock symbols** - All major stocks work  
✅ **Graceful error handling for invalid symbols** - Proper error messages  
✅ **Easy integration with Claude Desktop** - Configuration provided  
✅ **Simple and functional POC** - Clean, focused implementation  
✅ **Paper trading functionality** - Buy/sell orders and portfolio tracking
✅ **Real-time pricing integration** - Live stock prices for trading decisions
✅ **Portfolio management** - Balance tracking and P&L calculations

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
