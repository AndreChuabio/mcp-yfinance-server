# Paper Trading Setup Guide

## Overview
This MCP server integrates with Paper Invest API for real paper trading functionality. This guide will help you configure your Paper Invest credentials.

## Prerequisites
- Active Paper Invest account
- API access enabled on your account

## Step 1: Get Your Paper Invest Credentials

### API Key
1. Log in to [Paper Invest](https://paperinvest.io)
2. Navigate to Settings > API Keys
3. Create a new API key
4. Copy the API key (it will only be shown once)

### Account ID and Portfolio ID
1. In Paper Invest dashboard, navigate to your trading account
2. Your Account ID is typically visible in the account settings or URL
3. Your Portfolio ID can be found under Portfolio > Settings

## Step 2: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Paper Invest API credentials for paper trading
paper_API_KEY=your_actual_api_key_here
paper_account_ID=your_actual_account_id_here
paper_portfolio_ID=your_actual_portfolio_id_here
```

Example (with fake values):
```bash
paper_API_KEY=pi_sk_1234567890abcdef
paper_account_ID=acc_9876543210
paper_portfolio_ID=port_1111222233
```

## Step 3: Verify Configuration

Run the test suite to verify everything is working:

```bash
python tests/test_paper_trading.py
```

You should see:
- Credentials check passing
- Portfolio balance retrieval working
- Order placement successful

## Step 4: Test Trading Operations

### Get Portfolio Balance
```python
from mcp_yfinance_server import get_portfolio_balance
import asyncio

result = asyncio.run(get_portfolio_balance())
print(result[0].text)
```

### Place a Buy Order
```python
from mcp_yfinance_server import place_buy_order
import asyncio

result = asyncio.run(place_buy_order("AAPL", 1))
print(result[0].text)
```

### Place a Sell Order
```python
from mcp_yfinance_server import place_sell_order
import asyncio

result = asyncio.run(place_sell_order("AAPL", 1))
print(result[0].text)
```

## Troubleshooting

### Error: "Authentication failed"
- Verify your API key is correct
- Ensure API access is enabled on your Paper Invest account
- Check if the API key has expired

### Error: "Portfolio not found"
- Verify your Portfolio ID is correct
- Ensure the portfolio exists in your Paper Invest account
- Check if you have access to the specified portfolio

### Error: "Insufficient funds"
- Check your portfolio balance
- Ensure you have enough cash for the order
- Consider the commission costs

### Error: "Invalid symbol"
- Verify the stock ticker is correct
- Ensure the stock is supported by your broker
- Check if the market is open

## API Endpoints Used

### Authentication
```
POST /v1/auth/token
Body: {"apiKey": "your_api_key"}
Returns: {"token": "jwt_token"}
```

### Get Portfolio Orders
```
GET /v1/orders/portfolio/{portfolioId}
Headers: {"Authorization": "Bearer {token}"}
```

### Place Order
```
POST /v1/orders
Headers: {"Authorization": "Bearer {token}"}
Body: {
  "accountId": "your_account_id",
  "portfolioId": "your_portfolio_id",
  "symbol": "AAPL",
  "assetClass": "EQUITY",
  "side": "BUY_TO_OPEN" | "SELL_TO_CLOSE",
  "type": "MARKET",
  "quantity": 10,
  "timeInForce": "DAY"
}
```

## Security Best Practices

1. **Never commit your .env file** to version control
2. **Rotate API keys** regularly
3. **Use read-only keys** for development/testing when possible
4. **Monitor account activity** regularly
5. **Set up alerts** for unusual trading activity

## Features

### Supported Order Types
- Market orders (immediate execution)
- Day orders (valid until market close)

### Supported Actions
- BUY_TO_OPEN (open new position)
- SELL_TO_CLOSE (close existing position)

### Asset Classes
- EQUITY (stocks)

## Rate Limits

Paper Invest API rate limits:
- Authentication: 10 requests/minute
- Order placement: 60 requests/minute
- Portfolio queries: 120 requests/minute

The server automatically handles JWT token caching to minimize authentication calls.

## Next Steps

After setup is complete:
1. Run the complete demo: `python tests/demo_complete.py`
2. Integrate with Claude Desktop (see CLAUDE_DESKTOP_SETUP.md)
3. Start using the MCP tools in your trading workflows

## Support

For Paper Invest API issues:
- Documentation: https://docs.paperinvest.io
- Support: support@paperinvest.io

For MCP Server issues:
- Create an issue on GitHub
- Contact: andre102599@gmail.com
