#!/usr/bin/env python3
"""
Test script to verify the MCP YFinance server functions work correctly.
"""

import mcp_yfinance_server as server
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


async def test_functions():
    """Test the main functions of our MCP server."""

    print("🧪 Testing MCP YFinance Server Functions")
    print("=" * 50)

    # Test symbols to use
    test_symbols = ["AAPL", "GOOGL", "TSLA", "INVALID"]

    for symbol in test_symbols:
        print(f"\n📊 Testing symbol: {symbol}")
        print("-" * 30)

        try:
            # Test get_stock_price
            print("Testing get_stock_price...")
            result = await server.get_stock_price(symbol)
            print(
                f"✅ get_stock_price: {len(result[0].text[:100])}... characters")

            # Test get_stock_history (only for valid symbols)
            if symbol != "INVALID":
                print("Testing get_stock_history...")
                result = await server.get_stock_history(symbol, "1mo")
                print(
                    f"✅ get_stock_history: {len(result[0].text[:100])}... characters")

                # Test get_stock_info
                print("Testing get_stock_info...")
                result = await server.get_stock_info(symbol)
                print(
                    f"✅ get_stock_info: {len(result[0].text[:100])}... characters")

        except Exception as e:
            print(f"❌ Error for {symbol}: {str(e)}")

    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_functions())
