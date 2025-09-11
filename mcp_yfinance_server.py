#!/usr/bin/env python3
"""
MCP YFinance Server - Simple POC

A minimal MCP server that provides stock data tools using yfinance.
Implements basic stock price queries, historical data, and company information.
"""

import asyncio
import logging
from typing import Any, Sequence
from datetime import datetime, timedelta

import yfinance as yf
from mcp.server import InitializationOptions, NotificationOptions, Server
from mcp import Tool
from mcp.types import TextContent
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-yfinance-server")

# Initialize the MCP server
server = Server("mcp-yfinance-server")

# register tools


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for stock data queries."""
    return [
        Tool(
            name="get_stock_price",
            description="Get current stock price and basic trading info for a given ticker symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_stock_history",
            description="Get historical price data for a stock over a specified date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for historical data",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                        "default": "1mo"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_stock_info",
            description="Get detailed company information and key financial metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]

# Handle tool calls


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls for stock data operations."""

    try:
        if name == "get_stock_price":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            return await get_stock_price(symbol)
        elif name == "get_stock_history":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            period = arguments.get("period", "1mo")
            return await get_stock_history(symbol, period)
        elif name == "get_stock_info":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            return await get_stock_info(symbol)
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def get_stock_price(symbol: str) -> list[TextContent]:
    """Get current stock price and basic trading information."""
    if not symbol:
        raise ValueError("Symbol is required")

    symbol = symbol.upper()

    try:
        # Get stock data
        stock = yf.Ticker(symbol)
        info = stock.info

        # Get current price data
        hist = stock.history(period="1d")
        if hist.empty:
            raise ValueError(f"No data found for symbol {symbol}")

        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        high_price = hist['High'].iloc[-1]
        low_price = hist['Low'].iloc[-1]
        volume = hist['Volume'].iloc[-1]

        # Calculate change
        change = current_price - open_price
        change_percent = (change / open_price) * 100

        result = f"""📈 **{symbol} - {info.get('longName', 'N/A')}**

**Current Price:** ${current_price:.2f}
**Change:** ${change:+.2f} ({change_percent:+.2f}%)
**Today's Range:** ${low_price:.2f} - ${high_price:.2f}
**Open:** ${open_price:.2f}
**Volume:** {volume:,}

**Market Cap:** ${info.get('marketCap', 0):,}
**Sector:** {info.get('sector', 'N/A')}
**Industry:** {info.get('industry', 'N/A')}
"""

        return [TextContent(type="text", text=result)]

    except Exception as e:
        raise ValueError(f"Failed to get stock price for {symbol}: {str(e)}")


async def get_stock_history(symbol: str, period: str = "1mo") -> list[TextContent]:
    """Get historical price data for a stock."""
    if not symbol:
        raise ValueError("Symbol is required")

    symbol = symbol.upper()

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError(f"No historical data found for symbol {symbol}")

        # Get basic statistics
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        total_return = ((end_price - start_price) / start_price) * 100

        high_price = hist['High'].max()
        low_price = hist['Low'].min()
        avg_volume = hist['Volume'].mean()

        result = f"""📊 **{symbol} Historical Data ({period})**

**Period:** {hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}
**Total Return:** {total_return:+.2f}%
**Price Range:** ${low_price:.2f} - ${high_price:.2f}
**Average Volume:** {avg_volume:,.0f}

**Recent Data (Last 5 Trading Days):**
"""

        # Add recent data
        recent_data = hist.tail(5)
        for date, row in recent_data.iterrows():
            # Convert pandas Timestamp to string
            date_str = str(date)[:10]  # Get YYYY-MM-DD format
            result += f"{date_str}: ${row['Close']:.2f} (Vol: {row['Volume']:,.0f})\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        raise ValueError(
            f"Failed to get historical data for {symbol}: {str(e)}")


async def get_stock_info(symbol: str) -> list[TextContent]:
    """Get detailed company information and key financial metrics."""
    if not symbol:
        raise ValueError("Symbol is required")

    symbol = symbol.upper()

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        if not info or 'symbol' not in info:
            raise ValueError(
                f"No company information found for symbol {symbol}")

        result = f"""🏢 **{info.get('longName', symbol)} ({symbol})**

**Basic Information:**
• Sector: {info.get('sector', 'N/A')}
• Industry: {info.get('industry', 'N/A')}
• Country: {info.get('country', 'N/A')}
• Employees: {info.get('fullTimeEmployees', 'N/A'):,}

**Financial Metrics:**
• Market Cap: ${info.get('marketCap', 0):,}
• Enterprise Value: ${info.get('enterpriseValue', 0):,}
• P/E Ratio: {info.get('trailingPE', 'N/A')}
• Forward P/E: {info.get('forwardPE', 'N/A')}
• Price/Book: {info.get('priceToBook', 'N/A')}
• Debt/Equity: {info.get('debtToEquity', 'N/A')}

**Dividend Information:**
• Dividend Yield: {info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 'N/A'}%
• Payout Ratio: {info.get('payoutRatio', 'N/A')}

**Trading Information:**
• 52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
• 52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
• Average Volume: {info.get('averageVolume', 'N/A'):,}
• Beta: {info.get('beta', 'N/A')}

**Business Summary:**
{info.get('longBusinessSummary', 'No business summary available')[:500]}...
"""

        return [TextContent(type="text", text=result)]

    except Exception as e:
        raise ValueError(
            f"Failed to get company information for {symbol}: {str(e)}")


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-yfinance-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
if __name__ == "__main__":
    asyncio.run(main())
