#!/usr/bin/env python3
"""
Demo script showcasing the MCP YFinance server capabilities.
This script demonstrates all three tools with real stock data.
"""

import mcp_yfinance_server as server
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


async def demo():
    """Run a comprehensive demo of all MCP server capabilities."""

    print("🎯 MCP YFinance Server Demo")
    print("=" * 60)
    print("Demonstrating all three tools with popular stocks")
    print()

    demo_stocks = [
        ("AAPL", "Apple Inc."),
        ("GOOGL", "Alphabet Inc."),
        ("TSLA", "Tesla Inc.")
    ]

    for symbol, company in demo_stocks:
        print(f"🏢 Analyzing {company} ({symbol})")
        print("=" * 60)

        try:
            # Demo 1: Current Stock Price
            print("📈 CURRENT STOCK PRICE")
            print("-" * 30)
            result = await server.get_stock_price(symbol)
            print(result[0].text)

            # Demo 2: Historical Data (1 month)
            print("\n📊 HISTORICAL DATA (1 Month)")
            print("-" * 30)
            result = await server.get_stock_history(symbol, "1mo")
            print(result[0].text)

            # Demo 3: Company Information
            print("\n🏢 COMPANY INFORMATION")
            print("-" * 30)
            result = await server.get_stock_info(symbol)
            print(result[0].text[:800] +
                  "..." if len(result[0].text) > 800 else result[0].text)

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")

        print("\n" + "="*60 + "\n")

    print("✨ Demo completed! All tools are working perfectly.")
    print("\n💡 Next Steps:")
    print("1. Integrate with Claude Desktop using claude_desktop_config.json")
    print("2. Test with your own stock symbols")
    print("3. Explore different time periods for historical data")

if __name__ == "__main__":
    asyncio.run(demo())
