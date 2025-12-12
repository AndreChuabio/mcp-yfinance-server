#!/usr/bin/env python3
"""
Test suite for paper trading functionality
"""

from mcp_yfinance_server import (
    get_stock_price,
    get_portfolio_balance,
    place_buy_order,
    place_sell_order,
    PAPER_API_KEY,
    PAPER_ACCOUNT_ID,
    PAPER_PORTFOLIO_ID
)
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_credentials():
    """Test if Paper Invest credentials are configured"""
    print("Testing Paper Invest Credentials...")
    print("-" * 60)

    if not PAPER_API_KEY:
        print("❌ paper_API_KEY not found in environment")
        return False
    if not PAPER_ACCOUNT_ID:
        print("❌ paper_account_ID not found in environment")
        return False
    if not PAPER_PORTFOLIO_ID:
        print("❌ paper_portfolio_ID not found in environment")
        return False

    print(
        f"✅ API Key: {'*' * 20}{PAPER_API_KEY[-4:] if len(PAPER_API_KEY) > 4 else 'SET'}")
    print(f"✅ Account ID: {PAPER_ACCOUNT_ID}")
    print(f"✅ Portfolio ID: {PAPER_PORTFOLIO_ID}")
    return True


async def test_stock_price():
    """Test stock price retrieval"""
    print("\nTesting Stock Price Retrieval...")
    print("-" * 60)

    try:
        result = await get_stock_price("AAPL")
        print("✅ Stock price retrieval successful")
        print(result[0].text[:200] + "...")
        return True
    except Exception as e:
        print(f"❌ Stock price test failed: {e}")
        return False


async def test_portfolio_balance():
    """Test portfolio balance retrieval"""
    print("\nTesting Portfolio Balance...")
    print("-" * 60)

    try:
        result = await get_portfolio_balance()
        print("✅ Portfolio balance retrieval successful")
        print(result[0].text)
        return True
    except Exception as e:
        print(f"❌ Portfolio balance test failed: {e}")
        print(f"   Error details: {str(e)}")
        return False


async def test_buy_order():
    """Test placing a buy order"""
    print("\nTesting Buy Order...")
    print("-" * 60)

    try:
        result = await place_buy_order("AAPL", 1)
        print("✅ Buy order placed successfully")
        print(result[0].text)
        return True
    except Exception as e:
        print(f"❌ Buy order test failed: {e}")
        print(f"   Error details: {str(e)}")
        return False


async def test_sell_order():
    """Test placing a sell order"""
    print("\nTesting Sell Order...")
    print("-" * 60)

    try:
        result = await place_sell_order("AAPL", 1)
        print("✅ Sell order placed successfully")
        print(result[0].text)
        return True
    except Exception as e:
        print(f"❌ Sell order test failed: {e}")
        print(f"   Error details: {str(e)}")
        return False


async def run_all_tests():
    """Run all paper trading tests"""
    print("\n" + "=" * 60)
    print("Paper Trading Functionality Test Suite")
    print("=" * 60 + "\n")

    results = {}

    # Test credentials first
    results['credentials'] = await test_credentials()

    if not results['credentials']:
        print("\n" + "=" * 60)
        print("⚠️  Paper Invest credentials not configured!")
        print("=" * 60)
        print("\nTo configure, add these to your .env file:")
        print("paper_API_KEY=your_api_key_here")
        print("paper_account_ID=your_account_id_here")
        print("paper_portfolio_ID=your_portfolio_id_here")
        return

    # Test stock price (doesn't require Paper Invest)
    results['stock_price'] = await test_stock_price()

    # Test Paper Invest functionality
    results['portfolio'] = await test_portfolio_balance()
    results['buy_order'] = await test_buy_order()
    results['sell_order'] = await test_sell_order()

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title():.<40} {status}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Paper trading is fully operational.")
    else:
        print(
            f"\n⚠️  {total - passed} test(s) failed. Check the details above.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
