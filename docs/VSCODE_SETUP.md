# VS Code Integration Guide

## 🚀 Using the MCP YFinance Server in VS Code

While the MCP server is primarily designed for Claude Desktop integration, it can also be used within VS Code environments for development and testing.

## 🛠️ VS Code Usage Options

### 1. Direct Python Execution
Run the server directly in VS Code terminals:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run server directly (for testing)
python mcp_yfinance_server.py

# Run test scripts
python test_paper_trading.py
python demo_complete.py
```

### 2. MCP Extension Integration
If VS Code supports MCP extensions in the future, the server can be configured similarly to Claude Desktop.

### 3. Development and Testing
Use VS Code for:
- **Server Development** - Edit and improve the MCP server code
- **Testing** - Run test scripts to verify functionality
- **Debugging** - Debug the server and API integrations
- **Documentation** - Maintain project documentation

## 🧪 Testing in VS Code

### Run Individual Functions
```python
# Test stock price functionality
python -c "
import asyncio
from mcp_yfinance_server import get_stock_price
async def test():
    result = await get_stock_price('AAPL')
    print(result[0].text)
asyncio.run(test())
"
```

### Run Complete Workflow
```bash
python demo_complete.py
```

## 🔧 Development Workflow

1. **Edit Code** in VS Code
2. **Test Changes** using test scripts
3. **Debug Issues** using VS Code debugger
4. **Deploy to Claude** by updating Claude Desktop config

## 📊 Available Test Scripts

- `test_paper_trading.py` - Basic paper trading functionality
- `demo_complete.py` - Complete workflow demonstration
- `test_mcp_integration.py` - MCP tool integration tests

## 🎯 Best Practices

- **Use VS Code** for development and testing
- **Use Claude Desktop** for actual trading and analysis
- **Keep credentials secure** in .env file
- **Test thoroughly** before deploying to Claude

---

**💡 Tip:** VS Code is perfect for developing and testing your MCP server, while Claude Desktop provides the best user experience for actual financial analysis and trading!
