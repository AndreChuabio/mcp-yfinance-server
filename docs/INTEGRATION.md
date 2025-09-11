# Claude Desktop Integration Guide

## 📋 Setup Instructions

To integrate the MCP YFinance server with Claude Desktop, follow these steps:

### 1. Locate Claude Desktop Configuration

Find your Claude Desktop configuration file:

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Add Server Configuration

Add the following configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "mcp-yfinance-server": {
      "command": "/Users/andrechuabio/MCP quant/.venv/bin/python",
      "args": ["/Users/andrechuabio/MCP quant/mcp_yfinance_server.py"],
      "env": {}
    }
  }
}
```

**Important:** Update the paths to match your actual installation directory!

### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the new MCP server.

### 4. Verify Integration

In Claude Desktop, you should now be able to:

✅ **Get current stock prices:**
> "What's the current price of Apple stock?"

✅ **Get historical data:**  
> "Show me Tesla's stock performance over the last 3 months"

✅ **Get company information:**
> "Tell me about Google's financial metrics and company details"

## 🔧 Troubleshooting

### Server Not Loading
- Check that all file paths in the config are correct
- Ensure Python virtual environment is activated
- Verify all dependencies are installed: `mcp`, `yfinance`, `pydantic`

### Permission Issues
- Make sure the Python script is executable: `chmod +x mcp_yfinance_server.py`
- Check that the virtual environment has proper permissions

### Python Path Issues
- Use absolute paths in the configuration
- Verify virtual environment Python: `/path/to/.venv/bin/python --version`

## 💡 Usage Examples

Once integrated, try these commands in Claude Desktop:

**Basic Stock Query:**
> "Get the current price of Microsoft stock"

**Historical Analysis:**
> "Show me Amazon's stock history for the past year"

**Company Research:**
> "I need detailed information about Netflix's financials"

**Multi-Stock Comparison:**
> "Compare the current prices of Apple, Google, and Microsoft"

## 🎯 Success Indicators

You'll know the integration is working when:
- Claude can respond with real-time stock data
- Historical charts and data are available
- Detailed company information is accessible
- Error messages are handled gracefully for invalid symbols

---

**Happy trading! 📈**
