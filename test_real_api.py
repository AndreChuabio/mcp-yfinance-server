#!/usr/bin/env python3
"""
Test script to verify connection to real Paper Invest API and place the PSKY order
"""
import asyncio
import os
import requests
from dotenv import load_dotenv
import yfinance as yf

# Load environment variables
load_dotenv()

# Paper trading configuration
PAPER_API_KEY = os.getenv("paper_API_KEY")
PAPER_ACCOUNT_ID = os.getenv("paper_account_ID")
PAPER_PORTFOLIO_ID = os.getenv("paper_portfolio_ID")

# Paper Invest API settings
PAPER_BASE_URL = "https://api.paperinvest.io/v1"


async def get_jwt_token():
    """Get JWT token from Paper Invest API"""
    try:
        response = requests.post(
            f"{PAPER_BASE_URL}/auth/token",
            json={"apiKey": PAPER_API_KEY},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Successfully obtained JWT token")
        return data["token"]
    except Exception as e:
        print(f"❌ Failed to get JWT token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        raise


async def place_real_buy_order(symbol: str, shares: int):
    """Place a real buy order for PSKY using Paper Invest API"""
    try:
        token = await get_jwt_token()
        symbol = symbol.upper()

        print(f"🔍 Getting current price for {symbol}...")
        # Get current stock price
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        if hist.empty:
            raise ValueError(f"Cannot get current price for {symbol}")
        current_price = hist['Close'].iloc[-1]
        print(f"📈 Current price: ${current_price:.2f}")

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

        print(f"📤 Placing order: {shares} shares of {symbol}")
        print(f"Portfolio ID: {PAPER_PORTFOLIO_ID}")

        # Place the order
        response = requests.post(
            f"{PAPER_BASE_URL}/orders",
            json=order_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        print(f"📡 API Response Status: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Error response: {response.text}")
            response.raise_for_status()

        order_result = response.json()

        print(f"""✅ **REAL Order Placed Successfully!**

🎯 Symbol: {symbol}
📊 Shares: {shares}
💰 Reference Price: ${current_price:.2f}
💵 Estimated Cost: ${shares * current_price:.2f}

📋 Paper Invest Order Details:
   Order ID: {order_result.get('orderId', 'N/A')}
   Status: {order_result.get('status', 'UNKNOWN')}
   Created: {order_result.get('createdAt', 'N/A')}

🎉 This order should now appear in your real Paper Invest account!
""")

        return order_result

    except Exception as e:
        print(f"❌ Failed to place real order: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Response text: {e.response.text}")
        raise


async def get_portfolio_status():
    """Check portfolio status"""
    try:
        token = await get_jwt_token()

        print(f"📋 Checking portfolio {PAPER_PORTFOLIO_ID}...")

        # Get orders for this portfolio
        response = requests.get(
            f"{PAPER_BASE_URL}/orders/portfolio/{PAPER_PORTFOLIO_ID}",
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"📡 Portfolio API Response Status: {response.status_code}")

        if response.status_code == 404:
            print("ℹ️ No orders found yet - this is normal for a new portfolio")
            return

        response.raise_for_status()
        orders_data = response.json()

        orders = orders_data.get("data", [])
        print(f"📊 Found {len(orders)} orders in portfolio")

        for order in orders[-5:]:  # Show last 5 orders
            print(
                f"   {order.get('symbol')} - {order.get('quantity')} shares - {order.get('status')}")

    except Exception as e:
        print(f"⚠️ Portfolio check failed: {str(e)}")


async def main():
    print("🚀 Testing Real Paper Invest API Connection")
    print("=" * 50)

    # First check portfolio status
    await get_portfolio_status()

    print("\n" + "=" * 50)
    print("🎯 Placing REAL Order for 5 shares of PSKY")
    print("=" * 50)

    # Place the real order
    await place_real_buy_order("PSKY", 5)

    print("\n" + "=" * 50)
    print("✅ Done! Check your Paper Invest account for the new order.")

if __name__ == "__main__":
    asyncio.run(main())
