#!/usr/bin/env python3
"""
MCP YFinance Server - Simple POC with Paper Trading

A minimal MCP server that provides stock data tools using yfinance
and basic paper trading functionality.
"""

import asyncio
import logging
import os
from typing import Any, Sequence
from datetime import datetime, timedelta
import json

import yfinance as yf
from mcp.server import InitializationOptions, NotificationOptions, Server
from mcp import Tool
from mcp.types import TextContent
from dotenv import load_dotenv
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import json_util
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-yfinance-server")

# Initialize the MCP server
server = Server("mcp-yfinance-server")

# Paper trading configuration
PAPER_API_KEY = os.getenv("paper_API_KEY")
PAPER_ACCOUNT_ID = os.getenv("paper_account_ID")
PAPER_PORTFOLIO_ID = os.getenv("paper_portfolio_ID")

# Paper Invest API settings
PAPER_BASE_URL = "https://api.paperinvest.io/v1"
_jwt_token = None  # Will be set when needed

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "portfolio_risk")
_mongo_client = None  # Global client for connection reuse

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
_neo4j_driver = None  # Global driver for connection reuse


def get_mongo_client():
    """Get or create MongoDB client with connection pooling."""
    global _mongo_client

    if _mongo_client is None:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI environment variable is not set")

        _mongo_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10
        )

    return _mongo_client


def get_mongo_database():
    """Get MongoDB database instance."""
    client = get_mongo_client()
    return client[MONGODB_DATABASE]


def get_neo4j_driver():
    """Get or create Neo4j driver with connection pooling."""
    global _neo4j_driver

    if _neo4j_driver is None:
        if not NEO4J_URI or not NEO4J_USERNAME or not NEO4J_PASSWORD:
            raise ValueError(
                "Neo4j credentials not configured in environment variables")

        try:
            _neo4j_driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                max_connection_pool_size=10
            )
            # Verify connectivity
            _neo4j_driver.verify_connectivity()
            logger.info("Neo4j driver initialized successfully")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise ValueError(f"Neo4j connection failed: {e}")

    return _neo4j_driver


def execute_neo4j_query(query: str, parameters: dict = None):
    """Execute a Neo4j query and return results."""
    driver = get_neo4j_driver()

    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


async def get_jwt_token():
    """Get JWT token from Paper Invest API"""
    global _jwt_token

    if _jwt_token is None:
        try:
            response = requests.post(
                f"{PAPER_BASE_URL}/auth/token",
                json={"apiKey": PAPER_API_KEY},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            _jwt_token = data["token"]
            logger.info("Successfully obtained JWT token")
        except Exception as e:
            logger.error(f"Failed to get JWT token: {e}")
            raise ValueError(f"Authentication failed: {e}")

    return _jwt_token

# Using REAL Paper Invest API only - no simulation!

# register tools


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for stock data queries and paper trading."""
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
        ),
        # Paper Trading Tools
        Tool(
            name="get_portfolio_balance",
            description="Get current paper trading portfolio balance and positions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="place_buy_order",
            description="Place a buy order for a stock in paper trading account",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                    },
                    "shares": {
                        "type": "number",
                        "description": "Number of shares to buy"
                    }
                },
                "required": ["symbol", "shares"]
            }
        ),
        Tool(
            name="place_sell_order",
            description="Place a sell order for a stock in paper trading account",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                    },
                    "shares": {
                        "type": "number",
                        "description": "Number of shares to sell"
                    }
                },
                "required": ["symbol", "shares"]
            }
        ),
        # MongoDB Query Tools
        Tool(
            name="query_portfolio_holdings",
            description="Query portfolio positions from MongoDB. Returns holdings data from the portfolio_risk database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Optional ticker symbol to filter holdings (e.g., AAPL)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100)",
                        "default": 100
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="query_price_history",
            description="Query historical price data from MongoDB by symbol with date range filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol to query (e.g., AAPL, GOOGL)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for price history (YYYY-MM-DD format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for price history (YYYY-MM-DD format)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 500)",
                        "default": 500
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="query_risk_metrics",
            description="Query risk calculations (VaR, CVaR, Sharpe, volatility) from MongoDB.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_type": {
                        "type": "string",
                        "description": "Filter by metric type (e.g., VaR, CVaR, Sharpe, volatility)"
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Optional ticker symbol to filter metrics"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100)",
                        "default": 100
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_mongodb_collections",
            description="List all collections in the portfolio_risk MongoDB database with document counts.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # Neo4j Sentiment Tools
        Tool(
            name="get_stock_sentiment",
            description="Get current sentiment summary for a stock symbol from Neo4j graph database",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, NVDA)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_recent_articles",
            description="Retrieve recent news articles for a stock with sentiment scores from Neo4j",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, NVDA)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum articles to return (default: 10)",
                        "default": 10
                    },
                    "sentiment_filter": {
                        "type": "string",
                        "description": "Filter by sentiment label: bullish, bearish, or neutral"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_sentiment_timeline",
            description="Get sentiment evolution over time for a stock from Neo4j",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, NVDA)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back (default: 7)",
                        "default": 7
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="compare_stock_sentiments",
            description="Compare sentiment across multiple stocks from Neo4j",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of stock ticker symbols to compare (e.g., ['AAPL', 'NVDA', 'GOOGL'])"
                    }
                },
                "required": ["symbols"]
            }
        ),
        Tool(
            name="search_articles_by_keyword",
            description="Search articles containing specific keywords in Neo4j",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search term to find in article titles and summaries"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 20)",
                        "default": 20
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_sentiment_statistics",
            description="Get aggregate sentiment statistics from Neo4j (avg, stdev, counts)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (optional - if omitted, returns stats for all stocks)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_data_sources_breakdown",
            description="Analyze sentiment by data source (RSS, Alpha Vantage, etc.) from Neo4j",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, NVDA)"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]

# Handle tool calls


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls for stock data operations and paper trading."""

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
        elif name == "get_portfolio_balance":
            return await get_portfolio_balance()
        elif name == "place_buy_order":
            symbol = arguments.get("symbol")
            shares = arguments.get("shares")
            if not symbol or not shares:
                raise ValueError("Symbol and shares are required")
            return await place_buy_order(symbol, shares)
        elif name == "place_sell_order":
            symbol = arguments.get("symbol")
            shares = arguments.get("shares")
            if not symbol or not shares:
                raise ValueError("Symbol and shares are required")
            return await place_sell_order(symbol, shares)
        # MongoDB Tools
        elif name == "query_portfolio_holdings":
            symbol = arguments.get("symbol")
            limit = arguments.get("limit", 100)
            return await query_portfolio_holdings(symbol, limit)
        elif name == "query_price_history":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            limit = arguments.get("limit", 500)
            return await query_price_history(symbol, start_date, end_date, limit)
        elif name == "query_risk_metrics":
            metric_type = arguments.get("metric_type")
            symbol = arguments.get("symbol")
            limit = arguments.get("limit", 100)
            return await query_risk_metrics(metric_type, symbol, limit)
        elif name == "list_mongodb_collections":
            return await list_mongodb_collections()
        # Neo4j tools
        elif name == "get_stock_sentiment":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            return await neo4j_get_stock_sentiment(symbol)
        elif name == "get_recent_articles":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            limit = arguments.get("limit", 10)
            sentiment_filter = arguments.get("sentiment_filter")
            return await neo4j_get_recent_articles(symbol, limit, sentiment_filter)
        elif name == "get_sentiment_timeline":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            days = arguments.get("days", 7)
            return await neo4j_get_sentiment_timeline(symbol, days)
        elif name == "compare_stock_sentiments":
            symbols = arguments.get("symbols")
            if not symbols or not isinstance(symbols, list):
                raise ValueError("symbols must be a non-empty array")
            return await neo4j_compare_stock_sentiments(symbols)
        elif name == "search_articles_by_keyword":
            keyword = arguments.get("keyword")
            if not keyword:
                raise ValueError("keyword is required")
            limit = arguments.get("limit", 20)
            return await neo4j_search_articles_by_keyword(keyword, limit)
        elif name == "get_sentiment_statistics":
            symbol = arguments.get("symbol")
            return await neo4j_get_sentiment_statistics(symbol)
        elif name == "get_data_sources_breakdown":
            symbol = arguments.get("symbol")
            if not symbol:
                raise ValueError("Symbol is required")
            return await neo4j_get_data_sources_breakdown(symbol)
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


# Paper Trading Functions

async def get_portfolio_balance() -> list[TextContent]:
    """Get current paper trading portfolio balance and positions from Paper Invest API."""
    try:
        token = await get_jwt_token()

        # Get orders for this portfolio to calculate positions
        response = requests.get(
            f"{PAPER_BASE_URL}/orders/portfolio/{PAPER_PORTFOLIO_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 404:
            # No orders yet - empty portfolio
            result = f"""💰 **REAL Paper Invest Portfolio**

**💵 Account Status:** Connected to Paper Invest
**📊 Portfolio ID:** {PAPER_PORTFOLIO_ID}
**� Orders:** No orders found yet

**✅ This is your REAL Paper Invest account - orders will be executed for real!**
"""
            return [TextContent(type="text", text=result)]

        response.raise_for_status()
        orders_data = response.json()

        # Process orders to show summary
        total_orders = len(orders_data.get("data", []))

        result = f"""💰 **Paper Trading Portfolio** (Paper Invest)

**📊 Portfolio Status:**
Connected to Paper Invest account
Portfolio ID: {PAPER_PORTFOLIO_ID}

**📋 Recent Orders:** {total_orders} total

*Note: Full portfolio details require additional API calls - this is a basic view*
"""

        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Failed to get portfolio balance: {str(e)}")
        # Fallback to basic info
        result = f"""💰 **Paper Trading Portfolio** (Paper Invest)

**📊 Status:** Connected to Paper Invest API
**Portfolio ID:** {PAPER_PORTFOLIO_ID}

**ℹ️ Note:** Full portfolio details loading...
**Error:** {str(e)}
"""
        return [TextContent(type="text", text=result)]


async def place_buy_order(symbol: str, shares: float) -> list[TextContent]:
    """Place a buy order using the real Paper Invest API."""
    try:
        token = await get_jwt_token()
        symbol = symbol.upper()
        shares = int(shares)

        if shares <= 0:
            raise ValueError("Shares must be positive")

        # Try to get current stock price for reference (optional, for display only)
        current_price = None
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
        except Exception as price_error:
            logger.warning(
                f"Could not fetch price for {symbol}: {price_error}")

        # Create order payload for Paper Invest API (corrected structure)
        order_data = {
            "accountId": PAPER_ACCOUNT_ID,
            "portfolioId": PAPER_PORTFOLIO_ID,
            "symbol": symbol,
            "assetClass": "EQUITY",
            "side": "BUY_TO_OPEN",
            "type": "MARKET",
            "quantity": shares,
            "timeInForce": "DAY"
        }

        # Place the order
        response = requests.post(
            f"{PAPER_BASE_URL}/orders",
            json=order_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        order_result = response.json()

        # Build result with optional price info
        price_info = ""
        if current_price:
            price_info = f"""**Reference Price:** ${current_price:.2f}
**Estimated Cost:** ${shares * current_price:.2f}

"""

        result = f"""✅ **Buy Order Submitted to Paper Invest**

**Symbol:** {symbol}
**Shares:** {shares}
**Order Type:** MARKET
{price_info}**Paper Invest Order Details:**
**Order ID:** {order_result.get('orderId', 'N/A')}
**Status:** {order_result.get('status', 'UNKNOWN')}
**Created:** {order_result.get('createdAt', 'N/A')}

**✨ Order has been sent to your real Paper Invest account!**
"""

        return [TextContent(type="text", text=result)]

    except requests.exceptions.HTTPError as e:
        error_msg = f"API Error: {e.response.status_code}"
        if e.response.text:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data.get('message', 'Unknown error')}"
            except:
                error_msg += f" - {e.response.text}"
        raise ValueError(error_msg)
    except Exception as e:
        raise ValueError(f"Failed to place buy order: {str(e)}")


async def place_sell_order(symbol: str, shares: float) -> list[TextContent]:
    """Place a sell order using the real Paper Invest API."""
    try:
        token = await get_jwt_token()
        symbol = symbol.upper()
        shares = int(shares)

        if shares <= 0:
            raise ValueError("Shares must be positive")

        # Try to get current stock price for reference (optional, for display only)
        current_price = None
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
        except Exception as price_error:
            logger.warning(
                f"Could not fetch price for {symbol}: {price_error}")

        # Create order payload for Paper Invest API (corrected structure)
        order_data = {
            "accountId": PAPER_ACCOUNT_ID,
            "portfolioId": PAPER_PORTFOLIO_ID,
            "symbol": symbol,
            "assetClass": "EQUITY",
            "side": "SELL_TO_CLOSE",
            "type": "MARKET",
            "quantity": shares,
            "timeInForce": "DAY"
        }

        # Place the order
        response = requests.post(
            f"{PAPER_BASE_URL}/orders",
            json=order_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        response.raise_for_status()
        order_result = response.json()

        # Build result with optional price info
        price_info = ""
        if current_price:
            price_info = f"""**Reference Price:** ${current_price:.2f}
**Estimated Proceeds:** ${shares * current_price:.2f}

"""

        result = f"""✅ **Sell Order Submitted to Paper Invest**

**Symbol:** {symbol}
**Shares:** {shares}
**Order Type:** MARKET
{price_info}**Paper Invest Order Details:**
**Order ID:** {order_result.get('orderId', 'N/A')}
**Status:** {order_result.get('status', 'UNKNOWN')}
**Created:** {order_result.get('createdAt', 'N/A')}

**✨ Order has been sent to your real Paper Invest account!**
"""

        return [TextContent(type="text", text=result)]

    except requests.exceptions.HTTPError as e:
        error_msg = f"API Error: {e.response.status_code}"
        if e.response.text:
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data.get('message', 'Unknown error')}"
            except:
                error_msg += f" - {e.response.text}"
        raise ValueError(error_msg)
    except Exception as e:
        raise ValueError(f"Failed to place sell order: {str(e)}")


# MongoDB Query Functions

def find_collection_by_keyword(db, keyword: str):
    """Find a collection in the database that matches the keyword."""
    collections = db.list_collection_names()
    keyword_lower = keyword.lower()

    for coll_name in collections:
        if keyword_lower in coll_name.lower():
            return db[coll_name]

    return None


async def query_portfolio_holdings(symbol: str = None, limit: int = 100) -> list[TextContent]:
    """Query portfolio positions from MongoDB."""
    try:
        db = get_mongo_database()

        # Find holdings collection
        collection = find_collection_by_keyword(db, "holdings")
        if collection is None:
            collection = find_collection_by_keyword(db, "portfolio")

        if collection is None:
            return [TextContent(
                type="text",
                text="Error: No holdings or portfolio collection found in database. Use list_mongodb_collections to see available collections."
            )]

        # Build query filter
        query_filter = {}
        if symbol:
            query_filter["$or"] = [
                {"symbol": symbol.upper()},
                {"ticker": symbol.upper()},
                {"Symbol": symbol.upper()},
                {"Ticker": symbol.upper()}
            ]

        # Execute query with limit
        cursor = collection.find(query_filter).limit(limit)
        results = list(cursor)

        if not results:
            return [TextContent(
                type="text",
                text=f"No holdings found{' for ' + symbol.upper() if symbol else ''}."
            )]

        # Format results using json_util for BSON serialization
        formatted_results = json.loads(json_util.dumps(results))

        result_text = f"**Portfolio Holdings** ({len(results)} records)\n\n"
        result_text += "```json\n"
        result_text += json.dumps(formatted_results, indent=2)
        result_text += "\n```"

        return [TextContent(type="text", text=result_text)]

    except ConnectionFailure as e:
        return [TextContent(type="text", text=f"MongoDB connection failed: {str(e)}")]
    except ServerSelectionTimeoutError as e:
        return [TextContent(type="text", text=f"MongoDB server selection timeout: {str(e)}")]
    except Exception as e:
        logger.error(f"Error querying portfolio holdings: {str(e)}")
        return [TextContent(type="text", text=f"Error querying portfolio holdings: {str(e)}")]


async def query_price_history(symbol: str, start_date: str = None, end_date: str = None, limit: int = 500) -> list[TextContent]:
    """Query historical price data from MongoDB."""
    try:
        db = get_mongo_database()

        # Find prices collection
        collection = find_collection_by_keyword(db, "price")

        if collection is None:
            return [TextContent(
                type="text",
                text="Error: No price collection found in database. Use list_mongodb_collections to see available collections."
            )]

        # Build query filter
        query_filter = {
            "$or": [
                {"symbol": symbol.upper()},
                {"ticker": symbol.upper()},
                {"Symbol": symbol.upper()},
                {"Ticker": symbol.upper()}
            ]
        }

        # Add date range filter if provided
        date_filter = {}
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                date_filter["$gte"] = start_dt
            except ValueError:
                return [TextContent(type="text", text=f"Invalid start_date format. Use YYYY-MM-DD.")]

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                date_filter["$lte"] = end_dt
            except ValueError:
                return [TextContent(type="text", text=f"Invalid end_date format. Use YYYY-MM-DD.")]

        if date_filter:
            # Try common date field names
            query_filter["$and"] = query_filter.get("$and", [])
            query_filter["$and"].append({
                "$or": [
                    {"date": date_filter},
                    {"Date": date_filter},
                    {"timestamp": date_filter},
                    {"Timestamp": date_filter}
                ]
            })

        # Execute query with limit and sort by date
        cursor = collection.find(query_filter).sort(
            [("date", -1), ("Date", -1)]).limit(limit)
        results = list(cursor)

        if not results:
            return [TextContent(
                type="text",
                text=f"No price history found for {symbol.upper()}"
                     + (f" between {start_date} and {end_date}" if start_date or end_date else "")
            )]

        # Format results using json_util for BSON serialization
        formatted_results = json.loads(json_util.dumps(results))

        result_text = f"**Price History for {symbol.upper()}** ({len(results)} records)\n\n"
        result_text += "```json\n"
        result_text += json.dumps(formatted_results, indent=2)
        result_text += "\n```"

        return [TextContent(type="text", text=result_text)]

    except ConnectionFailure as e:
        return [TextContent(type="text", text=f"MongoDB connection failed: {str(e)}")]
    except ServerSelectionTimeoutError as e:
        return [TextContent(type="text", text=f"MongoDB server selection timeout: {str(e)}")]
    except Exception as e:
        logger.error(f"Error querying price history: {str(e)}")
        return [TextContent(type="text", text=f"Error querying price history: {str(e)}")]


async def query_risk_metrics(metric_type: str = None, symbol: str = None, limit: int = 100) -> list[TextContent]:
    """Query risk calculations from MongoDB."""
    try:
        db = get_mongo_database()

        # Find risk metrics collection
        collection = find_collection_by_keyword(db, "risk")
        if collection is None:
            collection = find_collection_by_keyword(db, "metric")

        if collection is None:
            return [TextContent(
                type="text",
                text="Error: No risk or metrics collection found in database. Use list_mongodb_collections to see available collections."
            )]

        # Build query filter
        query_filter = {}

        if metric_type:
            query_filter["$or"] = [
                {"metric_type": {"$regex": metric_type, "$options": "i"}},
                {"metricType": {"$regex": metric_type, "$options": "i"}},
                {"type": {"$regex": metric_type, "$options": "i"}},
                {"metric": {"$regex": metric_type, "$options": "i"}}
            ]

        if symbol:
            symbol_filter = {
                "$or": [
                    {"symbol": symbol.upper()},
                    {"ticker": symbol.upper()},
                    {"Symbol": symbol.upper()},
                    {"Ticker": symbol.upper()}
                ]
            }
            if query_filter:
                query_filter = {"$and": [query_filter, symbol_filter]}
            else:
                query_filter = symbol_filter

        # Execute query with limit
        cursor = collection.find(query_filter).limit(limit)
        results = list(cursor)

        if not results:
            filter_desc = []
            if metric_type:
                filter_desc.append(f"type={metric_type}")
            if symbol:
                filter_desc.append(f"symbol={symbol.upper()}")
            filter_str = ", ".join(
                filter_desc) if filter_desc else "no filters"

            return [TextContent(
                type="text",
                text=f"No risk metrics found ({filter_str})."
            )]

        # Format results using json_util for BSON serialization
        formatted_results = json.loads(json_util.dumps(results))

        result_text = f"**Risk Metrics** ({len(results)} records)\n\n"
        result_text += "```json\n"
        result_text += json.dumps(formatted_results, indent=2)
        result_text += "\n```"

        return [TextContent(type="text", text=result_text)]

    except ConnectionFailure as e:
        return [TextContent(type="text", text=f"MongoDB connection failed: {str(e)}")]
    except ServerSelectionTimeoutError as e:
        return [TextContent(type="text", text=f"MongoDB server selection timeout: {str(e)}")]
    except Exception as e:
        logger.error(f"Error querying risk metrics: {str(e)}")
        return [TextContent(type="text", text=f"Error querying risk metrics: {str(e)}")]


async def list_mongodb_collections() -> list[TextContent]:
    """List all collections in the portfolio_risk database with document counts."""
    try:
        db = get_mongo_database()

        # Get all collection names
        collection_names = db.list_collection_names()

        if not collection_names:
            return [TextContent(
                type="text",
                text=f"No collections found in database '{MONGODB_DATABASE}'."
            )]

        result_text = f"**MongoDB Collections in '{MONGODB_DATABASE}'**\n\n"
        result_text += "| Collection | Document Count |\n"
        result_text += "|------------|----------------|\n"

        total_docs = 0
        for coll_name in sorted(collection_names):
            try:
                count = db[coll_name].estimated_document_count()
                total_docs += count
                result_text += f"| {coll_name} | {count:,} |\n"
            except Exception as e:
                result_text += f"| {coll_name} | Error: {str(e)} |\n"

        result_text += f"\n**Total Collections:** {len(collection_names)}\n"
        result_text += f"**Total Documents:** {total_docs:,}\n"

        return [TextContent(type="text", text=result_text)]

    except ConnectionFailure as e:
        return [TextContent(type="text", text=f"MongoDB connection failed: {str(e)}")]
    except ServerSelectionTimeoutError as e:
        return [TextContent(type="text", text=f"MongoDB server selection timeout: {str(e)}")]
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        return [TextContent(type="text", text=f"Error listing collections: {str(e)}")]


# Neo4j Tool Implementations

async def neo4j_get_stock_sentiment(symbol: str) -> list[TextContent]:
    """Get current sentiment summary for a stock from Neo4j."""
    try:
        symbol = symbol.upper()

        query = """
        MATCH (stock:Stock {symbol: $symbol})
        OPTIONAL MATCH (stock)-[:CURRENT_SENTIMENT]->(sentiment:Sentiment)
        OPTIONAL MATCH (stock)<-[:ABOUT]-(article:Article)
        RETURN 
          stock.symbol AS symbol,
          stock.name AS name,
          stock.last_updated AS last_updated,
          sentiment.score AS current_score,
          sentiment.label AS current_label,
          sentiment.confidence AS confidence,
          sentiment.timestamp AS sentiment_timestamp,
          COUNT(DISTINCT article) AS total_articles
        """

        results = execute_neo4j_query(query, {"symbol": symbol})

        if not results:
            return [TextContent(
                type="text",
                text=f"Stock {symbol} not found in Neo4j database."
            )]

        data = results[0]

        result_text = f"**Stock Sentiment: {data['symbol']}**\n\n"
        result_text += f"**Company:** {data.get('name', 'N/A')}\n"
        result_text += f"**Current Sentiment Score:** {data.get('current_score', 0):.3f}\n"
        result_text += f"**Current Label:** {data.get('current_label', 'N/A')}\n"
        result_text += f"**Confidence:** {data.get('confidence', 0):.2f}\n"
        result_text += f"**Total Articles:** {data.get('total_articles', 0)}\n"

        if data.get('sentiment_timestamp'):
            result_text += f"**Last Updated:** {data['sentiment_timestamp']}\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error getting stock sentiment: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def neo4j_get_recent_articles(symbol: str, limit: int = 10, sentiment_filter: str = None) -> list[TextContent]:
    """Retrieve recent articles for a stock with sentiment scores."""
    try:
        symbol = symbol.upper()

        query = """
        MATCH (stock:Stock {symbol: $symbol})<-[:ABOUT]-(article:Article)
        MATCH (article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
        WHERE $sentiment_filter IS NULL OR sentiment.label = $sentiment_filter
        RETURN 
          article.title AS title,
          article.url AS url,
          article.summary AS summary,
          article.published AS published,
          article.source AS source,
          sentiment.score AS sentiment_score,
          sentiment.label AS sentiment_label,
          sentiment.confidence AS confidence
        ORDER BY article.published DESC
        LIMIT $limit
        """

        results = execute_neo4j_query(query, {
            "symbol": symbol,
            "limit": limit,
            "sentiment_filter": sentiment_filter
        })

        if not results:
            filter_msg = f" ({sentiment_filter})" if sentiment_filter else ""
            return [TextContent(
                type="text",
                text=f"No articles found for {symbol}{filter_msg}."
            )]

        result_text = f"**Recent Articles for {symbol}** ({len(results)} articles)\n\n"

        for i, article in enumerate(results, 1):
            result_text += f"**{i}. {article['title']}**\n"
            result_text += f"   - Source: {article.get('source', 'N/A')}\n"
            result_text += f"   - Sentiment: {article['sentiment_label']} (score: {article['sentiment_score']:.3f})\n"
            result_text += f"   - Confidence: {article.get('confidence', 0):.2f}\n"
            result_text += f"   - URL: {article.get('url', 'N/A')}\n"
            if article.get('summary'):
                summary = article['summary'][:150] + \
                    "..." if len(article['summary']
                                 ) > 150 else article['summary']
                result_text += f"   - Summary: {summary}\n"
            result_text += "\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error getting recent articles: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def neo4j_get_sentiment_timeline(symbol: str, days: int = 7) -> list[TextContent]:
    """Get sentiment evolution over time for a stock."""
    try:
        symbol = symbol.upper()

        query = """
        MATCH (stock:Stock {symbol: $symbol})<-[:ABOUT]-(article:Article)
        MATCH (article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
        WHERE sentiment.timestamp >= datetime() - duration({days: $days})
        WITH date(sentiment.timestamp) AS date, sentiment
        RETURN 
          date,
          AVG(sentiment.score) AS avg_score,
          COUNT(sentiment) AS article_count,
          SUM(CASE WHEN sentiment.label = 'bullish' THEN 1 ELSE 0 END) AS bullish_count,
          SUM(CASE WHEN sentiment.label = 'bearish' THEN 1 ELSE 0 END) AS bearish_count,
          SUM(CASE WHEN sentiment.label = 'neutral' THEN 1 ELSE 0 END) AS neutral_count
        ORDER BY date DESC
        """

        results = execute_neo4j_query(query, {"symbol": symbol, "days": days})

        if not results:
            return [TextContent(
                type="text",
                text=f"No sentiment data found for {symbol} in the last {days} days."
            )]

        result_text = f"**Sentiment Timeline for {symbol}** (Last {days} days)\n\n"
        result_text += "| Date | Avg Score | Articles | Bullish | Bearish | Neutral |\n"
        result_text += "|------|-----------|----------|---------|---------|----------|\n"

        for row in results:
            date_str = str(row['date'])
            avg_score = row['avg_score']
            article_count = row['article_count']
            bullish = row['bullish_count']
            bearish = row['bearish_count']
            neutral = row['neutral_count']

            result_text += f"| {date_str} | {avg_score:.3f} | {article_count} | {bullish} | {bearish} | {neutral} |\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error getting sentiment timeline: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def neo4j_compare_stock_sentiments(symbols: list) -> list[TextContent]:
    """Compare sentiment across multiple stocks."""
    try:
        upper_symbols = [s.upper() for s in symbols]

        query = """
        MATCH (stock:Stock)
        WHERE stock.symbol IN $symbols
        OPTIONAL MATCH (stock)-[:CURRENT_SENTIMENT]->(sentiment:Sentiment)
        OPTIONAL MATCH (stock)<-[:ABOUT]-(article:Article)
        WITH stock, sentiment, COUNT(DISTINCT article) AS article_count
        RETURN 
          stock.symbol AS symbol,
          stock.name AS name,
          sentiment.score AS current_score,
          sentiment.label AS current_label,
          article_count
        ORDER BY sentiment.score DESC
        """

        results = execute_neo4j_query(query, {"symbols": upper_symbols})

        if not results:
            return [TextContent(
                type="text",
                text=f"No data found for stocks: {', '.join(upper_symbols)}"
            )]

        result_text = f"**Stock Sentiment Comparison**\n\n"
        result_text += "| Symbol | Name | Score | Label | Articles |\n"
        result_text += "|--------|------|-------|-------|----------|\n"

        for row in results:
            symbol = row['symbol']
            name = row.get('name', 'N/A')[:30]
            score = row.get('current_score', 0)
            label = row.get('current_label', 'N/A')
            articles = row.get('article_count', 0)

            result_text += f"| {symbol} | {name} | {score:.3f} | {label} | {articles} |\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error comparing stocks: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def neo4j_search_articles_by_keyword(keyword: str, limit: int = 20) -> list[TextContent]:
    """Search articles containing specific keywords."""
    try:
        query = """
        MATCH (article:Article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
        MATCH (article)-[:ABOUT]->(stock:Stock)
        WHERE toLower(article.title) CONTAINS toLower($keyword)
           OR toLower(article.summary) CONTAINS toLower($keyword)
        RETURN 
          stock.symbol AS symbol,
          article.title AS title,
          article.url AS url,
          article.published AS published,
          article.source AS source,
          sentiment.score AS sentiment_score,
          sentiment.label AS sentiment_label
        ORDER BY article.published DESC
        LIMIT $limit
        """

        results = execute_neo4j_query(
            query, {"keyword": keyword, "limit": limit})

        if not results:
            return [TextContent(
                type="text",
                text=f"No articles found containing '{keyword}'."
            )]

        result_text = f"**Articles containing '{keyword}'** ({len(results)} results)\n\n"

        for i, article in enumerate(results, 1):
            result_text += f"**{i}. [{article['symbol']}] {article['title']}**\n"
            result_text += f"   - Sentiment: {article['sentiment_label']} ({article['sentiment_score']:.3f})\n"
            result_text += f"   - Source: {article.get('source', 'N/A')}\n"
            result_text += f"   - URL: {article.get('url', 'N/A')}\n\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error searching articles: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def neo4j_get_sentiment_statistics(symbol: str = None) -> list[TextContent]:
    """Get aggregate sentiment statistics."""
    try:
        query = """
        MATCH (article:Article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
        MATCH (article)-[:ABOUT]->(stock:Stock)
        WHERE $symbol IS NULL OR stock.symbol = $symbol
        WITH stock, sentiment
        RETURN 
          stock.symbol AS symbol,
          COUNT(sentiment) AS total_sentiments,
          AVG(sentiment.score) AS avg_score,
          MIN(sentiment.score) AS min_score,
          MAX(sentiment.score) AS max_score,
          SUM(CASE WHEN sentiment.label = 'bullish' THEN 1 ELSE 0 END) AS bullish_count,
          SUM(CASE WHEN sentiment.label = 'bearish' THEN 1 ELSE 0 END) AS bearish_count,
          SUM(CASE WHEN sentiment.label = 'neutral' THEN 1 ELSE 0 END) AS neutral_count
        ORDER BY total_sentiments DESC
        """

        param_symbol = symbol.upper() if symbol else None
        results = execute_neo4j_query(query, {"symbol": param_symbol})

        if not results:
            scope = f" for {symbol.upper()}" if symbol else ""
            return [TextContent(
                type="text",
                text=f"No sentiment statistics found{scope}."
            )]

        scope_title = f" for {symbol.upper()}" if symbol else " (All Stocks)"
        result_text = f"**Sentiment Statistics{scope_title}**\n\n"
        result_text += "| Symbol | Total | Avg Score | Min | Max | Bullish | Bearish | Neutral |\n"
        result_text += "|--------|-------|-----------|-----|-----|---------|---------|----------|\n"

        for row in results:
            result_text += f"| {row['symbol']} | {row['total_sentiments']} | "
            result_text += f"{row['avg_score']:.3f} | {row['min_score']:.3f} | {row['max_score']:.3f} | "
            result_text += f"{row['bullish_count']} | {row['bearish_count']} | {row['neutral_count']} |\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error getting statistics: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def neo4j_get_data_sources_breakdown(symbol: str) -> list[TextContent]:
    """Analyze sentiment by data source."""
    try:
        symbol = symbol.upper()

        query = """
        MATCH (stock:Stock {symbol: $symbol})<-[:ABOUT]-(article:Article)
        MATCH (article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
        RETURN 
          article.source AS source,
          sentiment.method AS analysis_method,
          COUNT(*) AS article_count,
          AVG(sentiment.score) AS avg_sentiment,
          MIN(sentiment.score) AS min_sentiment,
          MAX(sentiment.score) AS max_sentiment
        ORDER BY article_count DESC
        """

        results = execute_neo4j_query(query, {"symbol": symbol})

        if not results:
            return [TextContent(
                type="text",
                text=f"No source data found for {symbol}."
            )]

        result_text = f"**Data Sources Breakdown for {symbol}**\n\n"
        result_text += "| Source | Method | Articles | Avg Score | Min | Max |\n"
        result_text += "|--------|--------|----------|-----------|-----|-----|\n"

        for row in results:
            source = row.get('source', 'N/A')
            method = row.get('analysis_method', 'N/A')
            count = row['article_count']
            avg = row['avg_sentiment']
            min_val = row['min_sentiment']
            max_val = row['max_sentiment']

            result_text += f"| {source} | {method} | {count} | {avg:.3f} | {min_val:.3f} | {max_val:.3f} |\n"

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Neo4j error getting sources breakdown: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


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
