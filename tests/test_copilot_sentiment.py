#!/usr/bin/env python3
"""
Test script for the new Copilot sentiment tools in MCP yfinance server.
"""

from mcp_yfinance_server import (
    neo4j_write_article_sentiment,
    neo4j_has_copilot_sentiment
)
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_copilot_sentiment_tools():
    """Test the new Copilot sentiment writing and checking tools."""

    print("Testing Copilot Sentiment Tools\n")
    print("=" * 60)

    test_url = "https://example.com/test-article"
    test_symbol = "AAPL"

    print("\n1. Testing has_copilot_sentiment (should return False initially)...")
    result = await neo4j_has_copilot_sentiment(test_url)
    print(f"Result: {result[0].text}")

    print("\n2. Testing write_article_sentiment...")
    result = await neo4j_write_article_sentiment(
        url=test_url,
        symbol=test_symbol,
        score=0.75,
        label="bullish",
        confidence=0.85,
        reasoning="Strong positive earnings report with better than expected revenue growth.",
        themes=["earnings", "revenue growth", "market expansion"],
        trading_impact="Potential upside momentum in short term",
        analyzed_by="copilot"
    )
    print(f"Result: {result[0].text}")

    print("\n3. Testing has_copilot_sentiment again (should return True now)...")
    result = await neo4j_has_copilot_sentiment(test_url)
    print(f"Result: {result[0].text}")

    print("\n4. Testing write_article_sentiment update (should update existing relationship)...")
    result = await neo4j_write_article_sentiment(
        url=test_url,
        symbol=test_symbol,
        score=0.65,
        label="bullish",
        confidence=0.90,
        reasoning="Updated analysis with more data points confirming positive outlook.",
        themes=["earnings", "revenue growth", "product launch"],
        trading_impact="Strong buy signal",
        analyzed_by="copilot-v2"
    )
    print(f"Result: {result[0].text}")

    print("\n" + "=" * 60)
    print("Test completed successfully")


if __name__ == "__main__":
    try:
        asyncio.run(test_copilot_sentiment_tools())
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
