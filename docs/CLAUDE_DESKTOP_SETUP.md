# Claude Desktop Setup

## Quick Setup

1. **Get your Paper Invest API credentials** (from your Paper Invest account)

2. **Find your Claude Desktop config file:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add this to your config file** (update the paths):
   ```json
   {
     "mcpServers": {
       "mcp-yfinance-server": {
         "command": "/YOUR_PATH_HERE/.venv/bin/python",
         "args": ["/YOUR_PATH_HERE/mcp_yfinance_server.py"],
         "env": {
           "paper_API_KEY": "your_paper_invest_api_key",
           "paper_account_ID": "your_account_id",
           "paper_portfolio_ID": "your_portfolio_id"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

# Claude Desktop Setup

## Quick Setup

1. **Get your Paper Invest API credentials** (from your Paper Invest account)

2. **Find your Claude Desktop config file:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

3. **Add this to your config file** (update the paths):
   ```json
   {
     "mcpServers": {
       "mcp-yfinance-server": {
         "command": "/YOUR_PATH_HERE/.venv/bin/python",
         "args": ["/YOUR_PATH_HERE/mcp_yfinance_server.py"],
         "env": {
           "paper_API_KEY": "your_paper_invest_api_key",
           "paper_account_ID": "your_account_id",
           "paper_portfolio_ID": "your_portfolio_id"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

## Usage

- "Buy 10 shares of AAPL"
- "What's Tesla's stock price?"
- "Show my portfolio balance"

## Troubleshooting

- **Server not loading?** Check file paths in config
- **Auth errors?** Verify your Paper Invest credentials
- **Need help?** Check the main README.md
