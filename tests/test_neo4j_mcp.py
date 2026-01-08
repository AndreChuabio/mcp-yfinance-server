#!/usr/bin/env python3
"""
Test script for Neo4j MCP tools
"""
from mcp_yfinance_server import (
    neo4j_get_stock_sentiment,
    neo4j_get_recent_articles,
    neo4j_get_sentiment_timeline,
    neo4j_compare_stock_sentiments,
    neo4j_search_articles_by_keyword,
    neo4j_get_sentiment_statistics,
    neo4j_get_data_sources_breakdown
)
import asyncio
import sys
sys.path.insert(0, '/Users/andrechuabio/mcp-paperinvest/mcp-server')


async def run_tests():
    print("=== Testing Neo4j MCP Tools ===\n")

    try:
        print("Test 1: Get Stock Sentiment (AAPL)")
        result = await neo4j_get_stock_sentiment("AAPL")
        print(result[0].text)
        print("\n" + "="*50 + "\n")

        print("Test 2: Get Recent Articles (AAPL, limit=3)")
        result = await neo4j_get_recent_articles("AAPL", limit=3)
        print(result[0].text[:500] + "...")
        print("\n" + "="*50 + "\n")

        print("Test 3: Get Sentiment Timeline (AAPL, 7 days)")
        result = await neo4j_get_sentiment_timeline("AAPL", days=7)
        print(result[0].text)
        print("\n" + "="*50 + "\n")

        print("Test 4: Compare Stock Sentiments (AAPL vs NVDA)")
        result = await neo4j_compare_stock_sentiments(["AAPL", "NVDA"])
        print(result[0].text)
        print("\n" + "="*50 + "\n")

        print("Test 5: Search Articles by Keyword ('revenue')")
        result = await neo4j_search_articles_by_keyword("revenue", limit=3)
        print(result[0].text[:500] + "...")
        print("\n" + "="*50 + "\n")

        print("Test 6: Get Sentiment Statistics (AAPL)")
        result = await neo4j_get_sentiment_statistics("AAPL")
        print(result[0].text)
        print("\n" + "="*50 + "\n")

        print("Test 7: Get Data Sources Breakdown (AAPL)")
        result = await neo4j_get_data_sources_breakdown("AAPL")
        print(result[0].text)
        print("\n" + "="*50 + "\n")

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_tests())
