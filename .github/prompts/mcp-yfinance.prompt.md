---
mode: agent
---

# MCP YFinance Server - Simple POC

You are an expert Python developer specializing in MCP (Model Context Protocol) servers and financial data integration. Build a simple, functional MCP server that connects to yfinance for stock data queries.

## Task
Create a minimal MCP server in Python that:
- Provides basic stock data tools using yfinance
- Allows querying stock prices, basic info, and historical data
- Is simple, clean, and works reliably as a POC

## Core Tools to Implement
1. **get_stock_price** - Get current stock price and basic info
2. **get_stock_history** - Get historical price data for a date range
3. **get_stock_info** - Get company information and key metrics

## Requirements
- Use Python with the MCP SDK
- Keep it simple - focus on core functionality over features
- Include proper error handling for invalid tickers
- Make tools intuitive and well-documented
- Test with common stocks (AAPL, GOOGL, TSLA, etc.)

## Success Criteria
- Server starts without errors
- Tools respond correctly to valid stock symbols
- Graceful error handling for invalid symbols
- Can be easily integrated with Claude Desktop or other MCP clients

Keep it POC-level - functional and clean, not over-engineered.

