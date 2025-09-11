#!/usr/bin/env python3
"""
Test MCP server with paper trading integration
"""

import asyncio
import json
from mcp_yfinance_server import server, handle_call_tool


async def test_mcp_paper_trading():
    """Test MCP server paper trading tools"""
    print("🚀 Testing MCP Paper Trading Integration\n")

    # Test portfolio balance
    print("1️⃣ Getting portfolio balance...")
    result = await handle_call_tool("get_portfolio_balance", {})
    print(result[0].text)
    print("\n" + "="*50 + "\n")

    # Test stock price (existing functionality)
    print("2️⃣ Getting TSLA stock price...")
    result = await handle_call_tool("get_stock_price", {"symbol": "TSLA"})
    text_content = result[0].text
    print(text_content[:300] + "..." if len(text_content)
          > 300 else text_content)
    print("\n" + "="*50 + "\n")

    # Test buy order
    print("3️⃣ Placing buy order for TSLA...")
    result = await handle_call_tool("place_buy_order", {"symbol": "TSLA", "shares": 5})
    print(result[0].text)
    print("\n" + "="*50 + "\n")

    # Test portfolio balance after trade
    print("4️⃣ Portfolio after buying TSLA...")
    result = await handle_call_tool("get_portfolio_balance", {})
    print(result[0].text)
    print("\n" + "="*50 + "\n")

    print("✅ MCP Paper Trading Integration Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_paper_trading())
