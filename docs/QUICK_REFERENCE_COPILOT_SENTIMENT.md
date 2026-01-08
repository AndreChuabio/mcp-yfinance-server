# Quick Reference: Copilot Sentiment Tools

## write_article_sentiment

**Purpose:** Store AI-generated sentiment analysis in Neo4j

**Required Parameters:**
```json
{
  "url": "https://article-url.com",
  "symbol": "AAPL",
  "score": 0.75,
  "label": "bullish",
  "confidence": 0.85,
  "reasoning": "Detailed explanation..."
}
```

**Optional Parameters:**
```json
{
  "themes": ["earnings", "growth", "innovation"],
  "trading_impact": "Short-term bullish momentum expected",
  "analyzed_by": "copilot"
}
```

**Returns:** Success message with article details

---

## has_copilot_sentiment

**Purpose:** Check if article already has Copilot analysis

**Required Parameters:**
```json
{
  "url": "https://article-url.com"
}
```

**Returns:**
```json
{
  "has_sentiment": true,
  "url": "https://article-url.com",
  "analyzed_at": "2026-01-08T12:00:00Z",
  "analyzed_by": "copilot"
}
```

---

## Workflow Pattern

```
1. Check: has_copilot_sentiment(url)
   ↓
2. If False → Analyze with AI
   ↓
3. Store: write_article_sentiment(...)
   ↓
4. Query: get_recent_articles(symbol)
```

---

## Relationship Created

```
(Article)-[:SENTIMENT_COPILOT {
  score: float,
  label: string,
  confidence: float,
  reasoning: string,
  themes: [string],
  trading_impact: string,
  analyzed_by: string,
  analyzed_at: datetime
}]->(Stock)
```

---

## Prerequisites

- Neo4j connection configured
- Article node must exist in Neo4j
- Stock node must exist in Neo4j
- MCP server running

---

## Error Handling

Tool validates:
- Article exists in Neo4j
- Stock exists in Neo4j
- Required parameters present
- Score in range [-1.0, 1.0]
- Confidence in range [0, 1]

Returns error message if validation fails.
