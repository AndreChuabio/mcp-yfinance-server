# Copilot Sentiment Tools Implementation

## Summary

Added two new Neo4j write tools to the MCP yfinance server to enable agentic workflows to store and query AI-generated sentiment analysis with caching support.

## New Tools

### 1. write_article_sentiment

Creates or updates a `:SENTIMENT_COPILOT` relationship from Article to Stock with comprehensive sentiment analysis.

**Parameters:**
- `url` (required): Article URL (unique identifier)
- `symbol` (required): Stock ticker symbol
- `score` (required): Sentiment score from -1.0 (bearish) to 1.0 (bullish)
- `label` (required): Sentiment label (bearish, neutral, or bullish)
- `confidence` (required): Confidence score from 0 to 1
- `reasoning` (required): Explanation of the sentiment analysis
- `themes` (optional): List of themes identified in the article
- `trading_impact` (optional): Assessment of potential trading impact
- `analyzed_by` (optional): Analyzer identifier (default: "copilot")

**Features:**
- Uses MERGE to avoid duplicate relationships
- Automatically adds `analyzed_at` timestamp
- Updates existing relationships with new analysis
- Returns confirmation with article details

**Cypher Query:**
```cypher
MATCH (article:Article {url: $url})
MATCH (stock:Stock {symbol: $symbol})
MERGE (article)-[r:SENTIMENT_COPILOT]->(stock)
SET r.score = $score,
    r.label = $label,
    r.confidence = $confidence,
    r.reasoning = $reasoning,
    r.themes = $themes,
    r.trading_impact = $trading_impact,
    r.analyzed_by = $analyzed_by,
    r.analyzed_at = datetime()
RETURN article.title, article.url, r.score, r.label, r.confidence
```

### 2. has_copilot_sentiment

Checks if an article already has a `:SENTIMENT_COPILOT` relationship to enable caching.

**Parameters:**
- `url` (required): Article URL to check

**Returns:**
JSON object with:
- `has_sentiment` (boolean): True if sentiment exists
- `url` (string): The article URL
- `analyzed_at` (string, optional): When the sentiment was analyzed
- `analyzed_by` (string, optional): Who analyzed it

**Cypher Query:**
```cypher
MATCH (article:Article {url: $url})-[r:SENTIMENT_COPILOT]->(:Stock)
RETURN COUNT(r) > 0 AS has_sentiment,
       r.analyzed_at AS analyzed_at,
       r.analyzed_by AS analyzed_by
LIMIT 1
```

## Implementation Details

### Files Modified

1. **mcp_yfinance_server.py**
   - Added tool definitions to `handle_list_tools()` with proper inputSchema
   - Added cases to `handle_call_tool()` switch statement
   - Implemented `neo4j_write_article_sentiment()` function
   - Implemented `neo4j_has_copilot_sentiment()` function
   - Both functions use the existing `execute_neo4j_query()` helper

### Code Structure

Follows existing patterns:
- Uses `execute_neo4j_query()` helper for Neo4j operations
- Returns `list[TextContent]` for MCP compatibility
- Proper error handling with logging
- Input validation for required parameters
- JSON serialization for structured responses

### Test File

Created `tests/test_copilot_sentiment.py` to verify functionality:
- Tests `has_copilot_sentiment` before writing (should return False)
- Tests `write_article_sentiment` to create relationship
- Tests `has_copilot_sentiment` after writing (should return True)
- Tests updating existing sentiment relationship

## Use Case: Agentic Workflow

This enables an agentic workflow to:
1. Check if article already has Copilot sentiment using `has_copilot_sentiment`
2. Skip analysis if sentiment exists (caching)
3. Generate new sentiment analysis with AI
4. Store results using `write_article_sentiment`
5. Include detailed reasoning, themes, and trading impact
6. Update analysis if new information becomes available

## Benefits

- **Caching**: Avoid redundant sentiment analysis
- **Rich Context**: Store reasoning and themes alongside scores
- **Traceability**: Track who analyzed and when
- **Flexibility**: Update analysis as new information emerges
- **Integration**: Works seamlessly with existing Neo4j tools

## Next Steps

To use these tools in your agentic workflow:
1. Ensure Neo4j connection is configured in `.env`
2. Ensure Articles and Stocks exist in Neo4j before writing sentiment
3. Use `has_copilot_sentiment` to check for existing analysis
4. Call `write_article_sentiment` with comprehensive analysis
5. Query sentiment using existing tools like `get_recent_articles`

## Example Usage

```python
# Check if sentiment exists
result = await neo4j_has_copilot_sentiment("https://example.com/article")

# Write new sentiment
result = await neo4j_write_article_sentiment(
    url="https://example.com/article",
    symbol="AAPL",
    score=0.75,
    label="bullish",
    confidence=0.85,
    reasoning="Strong earnings beat expectations...",
    themes=["earnings", "revenue growth"],
    trading_impact="Potential short-term upside",
    analyzed_by="copilot"
)
```
