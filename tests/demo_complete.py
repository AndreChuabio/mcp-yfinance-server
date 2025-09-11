#!/usr/bin/env python3
"""
Comprehensive demo of the MCP YFinance Server with Paper Trading
"""

import asyncio
from mcp_yfinance_server import (
    get_stock_price,
    get_portfolio_balance,
    place_buy_order,
    place_sell_order,
    PAPER_PORTFOLIO
)


async def demo_paper_trading():
    """Demonstrate the complete paper trading workflow"""

    print("🚀 MCP YFinance Server with Paper Trading Demo")
    print("=" * 60)

    # Reset portfolio for demo
    PAPER_PORTFOLIO["cash_balance"] = 100000.0
    PAPER_PORTFOLIO["positions"] = {}
    PAPER_PORTFOLIO["orders"] = []

    print("\n💼 Starting with fresh paper trading account...\n")

    # 1. Check initial portfolio
    print("1️⃣ Initial Portfolio Status:")
    result = await get_portfolio_balance()
    print(result[0].text)
    print("\n" + "="*50 + "\n")

    # 2. Get stock price for AAPL
    print("2️⃣ Checking Apple (AAPL) stock price:")
    result = await get_stock_price("AAPL")
    print(result[0].text[:400] + "...\n")
    print("="*50 + "\n")

    # 3. Buy some AAPL
    print("3️⃣ Buying 10 shares of AAPL:")
    result = await place_buy_order("AAPL", 10)
    print(result[0].text)
    print("\n" + "="*50 + "\n")

    # 4. Buy some TSLA
    print("4️⃣ Buying 5 shares of TSLA:")
    try:
        result = await place_buy_order("TSLA", 5)
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    print("\n" + "="*50 + "\n")

    # 5. Check portfolio after purchases
    print("5️⃣ Portfolio after purchases:")
    result = await get_portfolio_balance()
    print(result[0].text)
    print("\n" + "="*50 + "\n")

    # 6. Sell some AAPL
    print("6️⃣ Selling 5 shares of AAPL:")
    try:
        result = await place_sell_order("AAPL", 5)
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    print("\n" + "="*50 + "\n")

    # 7. Final portfolio check
    print("7️⃣ Final portfolio status:")
    result = await get_portfolio_balance()
    print(result[0].text)
    print("\n" + "="*60)

    print("\n🎉 Paper Trading Demo Complete!")
    print("\n📋 Summary:")
    print("• Started with $100,000 cash")
    print("• Bought stocks using real-time prices")
    print("• Tracked positions and P&L automatically")
    print("• Sold positions with profit/loss calculation")
    print("• All data persists during server session")
    print("\n✨ This shows the MCP server successfully integrating stock data with paper trading!")

if __name__ == "__main__":
    asyncio.run(demo_paper_trading())
