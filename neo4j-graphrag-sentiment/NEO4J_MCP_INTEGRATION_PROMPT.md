# Neo4j Integration Prompt for MCP Server

**Objective:** Integrate Neo4j Aura database as MCP tools in the Node.js MCP server to expose sentiment data stored in the graph database to Claude Desktop.

---

## Current Architecture

### MCP Server (Node.js)
- **Location:** `/Users/andrechuabio/mcp-paperinvest/mcp-server/`
- **Main file:** `src/index.js` (HTTP server with sentiment endpoints)
- **Current tools:** Sentiment analysis via yfinance, news, and social media
- **Dependencies:** axios, dotenv, sentiment, node-cache, @google/generative-ai

### Neo4j Database (Python)
- **Location:** `/Users/andrechuabio/mcp-paperinvest/neo4j-graphrag-sentiment/`
- **Connector:** `neo4j_connector.py` (394 lines, Python implementation)
- **Data:** 103+ articles for AAPL and NVDA with sentiment scores
- **Schema:**
  - **Stock nodes:** symbol, name, last_updated
  - **Article nodes:** url (unique), title, summary, published, source
  - **Sentiment nodes:** id (UUID), score (-1 to 1), label, confidence, timestamp, method
  - **Relationships:** ABOUT (Article→Stock), HAS_SENTIMENT (Article→Sentiment), CURRENT_SENTIMENT (Stock→Sentiment)

---

## Implementation Requirements

### 1. Add Neo4j Node.js Driver
Install the official Neo4j JavaScript driver:
```bash
npm install neo4j-driver
```

### 2. Create Neo4j Tool Module
**File:** `src/neo4j/neo4jTools.js`

Required functionality:
- Initialize driver with credentials from `.env`
- Connection pooling (maxPoolSize: 10)
- Session management
- Query execution with error handling
- Tool definitions for MCP protocol

### 3. Environment Variables
Add to `.env`:
```env
NEO4J_URI=neo4j+s://2d1c3589.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=[your_password]
NEO4J_DATABASE=neo4j
```

---

## Required MCP Tools

### Tool 1: `get_stock_sentiment`
**Description:** Get current sentiment summary for a stock symbol
**Input:** 
- `symbol` (string, required): Stock ticker (e.g., "AAPL")

**Query:**
```cypher
MATCH (stock:Stock {symbol: $symbol})
OPTIONAL MATCH (stock)-[:CURRENT_SENTIMENT]->(sentiment:Sentiment)
OPTIONAL MATCH (stock)<-[:ABOUT]-(article:Article)
RETURN 
  stock.symbol AS symbol,
  stock.name AS name,
  stock.last_updated AS last_updated,
  sentiment.score AS current_score,
  sentiment.label AS current_label,
  sentiment.confidence AS confidence,
  sentiment.timestamp AS sentiment_timestamp,
  COUNT(DISTINCT article) AS total_articles
```

**Output Schema:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_score": 0.75,
  "current_label": "bullish",
  "confidence": 0.85,
  "sentiment_timestamp": "2026-01-08T10:30:00Z",
  "total_articles": 50,
  "last_updated": "2026-01-08T10:30:00Z"
}
```

---

### Tool 2: `get_recent_articles`
**Description:** Retrieve recent news articles for a stock
**Input:**
- `symbol` (string, required): Stock ticker
- `limit` (integer, optional, default: 10): Max articles to return
- `sentiment_filter` (string, optional): Filter by sentiment label ("bullish", "bearish", "neutral")

**Query:**
```cypher
MATCH (stock:Stock {symbol: $symbol})<-[:ABOUT]-(article:Article)
MATCH (article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
WHERE $sentiment_filter IS NULL OR sentiment.label = $sentiment_filter
RETURN 
  article.title AS title,
  article.url AS url,
  article.summary AS summary,
  article.published AS published,
  article.source AS source,
  sentiment.score AS sentiment_score,
  sentiment.label AS sentiment_label,
  sentiment.confidence AS confidence,
  sentiment.method AS analysis_method
ORDER BY article.published DESC
LIMIT $limit
```

**Output Schema:**
```json
{
  "symbol": "AAPL",
  "articles": [
    {
      "title": "Apple Reports Record Revenue",
      "url": "https://...",
      "summary": "Apple Inc. announced...",
      "published": "2026-01-08T09:00:00Z",
      "source": "yahoo_finance_rss",
      "sentiment_score": 0.85,
      "sentiment_label": "bullish",
      "confidence": 0.9,
      "analysis_method": "gemini"
    }
  ],
  "count": 10
}
```

---

### Tool 3: `get_sentiment_timeline`
**Description:** Get sentiment evolution over time for a stock
**Input:**
- `symbol` (string, required): Stock ticker
- `days` (integer, optional, default: 7): Number of days to look back

**Query:**
```cypher
MATCH (stock:Stock {symbol: $symbol})<-[:ABOUT]-(article:Article)
MATCH (article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
WHERE sentiment.timestamp >= datetime() - duration({days: $days})
RETURN 
  date(sentiment.timestamp) AS date,
  AVG(sentiment.score) AS avg_score,
  COUNT(sentiment) AS article_count,
  COLLECT({
    score: sentiment.score,
    label: sentiment.label,
    timestamp: sentiment.timestamp
  }) AS sentiments
ORDER BY date DESC
```

**Output Schema:**
```json
{
  "symbol": "AAPL",
  "days": 7,
  "timeline": [
    {
      "date": "2026-01-08",
      "avg_score": 0.65,
      "article_count": 15,
      "sentiments": [...]
    }
  ]
}
```

---

### Tool 4: `compare_stock_sentiments`
**Description:** Compare sentiment across multiple stocks
**Input:**
- `symbols` (array of strings, required): Stock tickers to compare

**Query:**
```cypher
MATCH (stock:Stock)
WHERE stock.symbol IN $symbols
OPTIONAL MATCH (stock)-[:CURRENT_SENTIMENT]->(sentiment:Sentiment)
OPTIONAL MATCH (stock)<-[:ABOUT]-(article:Article)
WITH stock, sentiment, COUNT(DISTINCT article) AS article_count
RETURN 
  stock.symbol AS symbol,
  stock.name AS name,
  sentiment.score AS current_score,
  sentiment.label AS current_label,
  article_count
ORDER BY sentiment.score DESC
```

**Output Schema:**
```json
{
  "comparison": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "current_score": 0.75,
      "current_label": "bullish",
      "article_count": 50
    },
    {
      "symbol": "NVDA",
      "name": "NVIDIA Corporation",
      "current_score": 0.62,
      "current_label": "bullish",
      "article_count": 37
    }
  ]
}
```

---

### Tool 5: `search_articles_by_keyword`
**Description:** Search articles containing specific keywords
**Input:**
- `keyword` (string, required): Search term
- `limit` (integer, optional, default: 20): Max results

**Query:**
```cypher
MATCH (article:Article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
MATCH (article)-[:ABOUT]->(stock:Stock)
WHERE toLower(article.title) CONTAINS toLower($keyword)
   OR toLower(article.summary) CONTAINS toLower($keyword)
RETURN 
  stock.symbol AS symbol,
  article.title AS title,
  article.url AS url,
  article.published AS published,
  article.source AS source,
  sentiment.score AS sentiment_score,
  sentiment.label AS sentiment_label
ORDER BY article.published DESC
LIMIT $limit
```

---

### Tool 6: `get_sentiment_statistics`
**Description:** Get aggregate sentiment statistics
**Input:**
- `symbol` (string, optional): Stock ticker (if null, returns all stocks)

**Query:**
```cypher
MATCH (article:Article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
MATCH (article)-[:ABOUT]->(stock:Stock)
WHERE $symbol IS NULL OR stock.symbol = $symbol
WITH stock, sentiment
RETURN 
  stock.symbol AS symbol,
  COUNT(sentiment) AS total_sentiments,
  AVG(sentiment.score) AS avg_score,
  STDEV(sentiment.score) AS score_stdev,
  SUM(CASE WHEN sentiment.label = 'bullish' THEN 1 ELSE 0 END) AS bullish_count,
  SUM(CASE WHEN sentiment.label = 'bearish' THEN 1 ELSE 0 END) AS bearish_count,
  SUM(CASE WHEN sentiment.label = 'neutral' THEN 1 ELSE 0 END) AS neutral_count
```

---

### Tool 7: `get_data_sources_breakdown`
**Description:** Analyze sentiment by data source
**Input:**
- `symbol` (string, required): Stock ticker

**Query:**
```cypher
MATCH (stock:Stock {symbol: $symbol})<-[:ABOUT]-(article:Article)
MATCH (article)-[:HAS_SENTIMENT]->(sentiment:Sentiment)
RETURN 
  article.source AS source,
  sentiment.method AS analysis_method,
  COUNT(*) AS article_count,
  AVG(sentiment.score) AS avg_sentiment,
  MIN(sentiment.score) AS min_sentiment,
  MAX(sentiment.score) AS max_sentiment
ORDER BY article_count DESC
```

---

## Implementation Pattern

### Neo4j Tool Module Structure
```javascript
// src/neo4j/neo4jTools.js
const neo4j = require('neo4j-driver');
require('dotenv').config();

class Neo4jTools {
  constructor() {
    this.driver = neo4j.driver(
      process.env.NEO4J_URI,
      neo4j.auth.basic(process.env.NEO4J_USERNAME, process.env.NEO4J_PASSWORD),
      { maxConnectionPoolSize: 10 }
    );
  }

  async executeQuery(query, params = {}) {
    const session = this.driver.session({ 
      database: process.env.NEO4J_DATABASE || 'neo4j' 
    });
    try {
      const result = await session.run(query, params);
      return result.records.map(record => record.toObject());
    } catch (error) {
      throw new Error(`Neo4j query failed: ${error.message}`);
    } finally {
      await session.close();
    }
  }

  // Tool implementations...
  async getStockSentiment(symbol) { ... }
  async getRecentArticles(symbol, limit = 10, sentimentFilter = null) { ... }
  async getSentimentTimeline(symbol, days = 7) { ... }
  async compareStockSentiments(symbols) { ... }
  async searchArticlesByKeyword(keyword, limit = 20) { ... }
  async getSentimentStatistics(symbol = null) { ... }
  async getDataSourcesBreakdown(symbol) { ... }

  async close() {
    await this.driver.close();
  }
}

module.exports = new Neo4jTools();
```

---

## Integration Steps

1. **Install dependencies:**
   ```bash
   cd /Users/andrechuabio/mcp-paperinvest/mcp-server
   npm install neo4j-driver
   ```

2. **Create `src/neo4j/neo4jTools.js`** with all 7 tool implementations

3. **Update `src/index.js`:**
   - Import neo4jTools
   - Add Neo4j endpoints (or integrate into MCP protocol)
   - Handle tool calls

4. **Add to `claude_desktop_config.json`:**
   ```json
   {
     "mcp-server": {
       "command": "node",
       "args": ["/Users/andrechuabio/mcp-paperinvest/mcp-server/src/index.js"],
       "env": {
         "NEO4J_URI": "neo4j+s://2d1c3589.databases.neo4j.io",
         "NEO4J_USERNAME": "neo4j",
         "NEO4J_PASSWORD": "[password]",
         "NEO4J_DATABASE": "neo4j"
       }
     }
   }
   ```

5. **Test each tool:**
   - Create test file `tests/neo4j.test.js`
   - Verify connection
   - Test each query with AAPL/NVDA data

---

## Error Handling

Required error scenarios:
- Connection failures (retry logic)
- Invalid stock symbols (return empty results)
- Query timeouts (30s limit)
- Session management (always close)
- Invalid parameters (validate before query)

---

## Performance Optimization

- Use connection pooling (already configured)
- Limit result sizes (use LIMIT in all queries)
- Index on timestamp and published fields (already created in schema)
- Cache frequently accessed data (stock summaries)
- Batch queries when possible

---

## Testing Checklist

- [ ] Connection to Neo4j Aura successful
- [ ] get_stock_sentiment returns data for AAPL
- [ ] get_recent_articles retrieves 10 articles
- [ ] get_sentiment_timeline shows 7-day trend
- [ ] compare_stock_sentiments compares AAPL vs NVDA
- [ ] search_articles_by_keyword finds "revenue" articles
- [ ] get_sentiment_statistics calculates aggregates
- [ ] get_data_sources_breakdown shows RSS vs Alpha Vantage
- [ ] Error handling for invalid symbols
- [ ] Session cleanup on errors

---

## Expected Benefits

1. **GraphRAG:** Claude can query sentiment data directly from Neo4j
2. **Real-time insights:** Access latest sentiment without re-running Python scripts
3. **Relationship queries:** Leverage graph structure (Article→Stock→Sentiment)
4. **Historical analysis:** Track sentiment evolution over time
5. **Multi-stock comparison:** Analyze portfolio sentiment in one query
6. **Source attribution:** Know which API/RSS feed provided each sentiment

---

## Next Phase (After Integration)

1. Add Gemini sentiment analysis for RSS articles (replace neutral placeholders)
2. Implement entity extraction (people, companies, products mentioned)
3. Add trend detection queries (sentiment momentum, volatility)
4. Create composite sentiment scores (weighted by source reliability)
5. Vectorize articles for semantic search
6. Add GraphRAG query templates for common trading signals
