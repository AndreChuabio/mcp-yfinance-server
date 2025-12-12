#!/usr/bin/env python3
"""Quick test to get NVIDIA stock price"""

import mcp_yfinance_server as server
import asyncio
import sys
import os

# Add current directory to path
current_dir = "/Users/andrechuabio/MCP quant"
sys.path.insert(0, current_dir)


async def get_nvidia_price():
    try:
        print('🎯 Getting NVIDIA Stock Price...')
        print('=' * 50)
        result = await server.get_stock_price('NVDA')
        print(result[0].text)
        print('=' * 50)
        print('✅ Data retrieved successfully from Yahoo Finance!')
    except Exception as e:
        print(f'❌ Error: {str(e)}')

if __name__ == "__main__":
    asyncio.run(get_nvidia_price())
