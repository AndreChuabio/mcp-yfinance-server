# Neo4j Sentiment Data Ingestion - Phase 1

## Goal
Store sentiment data from existing APIs (Alpha Vantage, NewsAPI, Reddit) into Neo4j for the portfolio stocks. Keep it simple, get data flowing, verify storage is working.

## Target Stocks
```python
PORTFOLIO = [
  {"symbol": "AAPL", "shares": 9},
  {"symbol": "MSFT", "shares": 6},
  {"symbol": "GOOGL", "shares": 13},
  {"symbol": "NVDA", "shares": 12},
  {"symbol": "META", "shares": 7}
]
```

## Simple Graph Schema

### Node Types

#### 1. Stock
```cypher
(:Stock {
  symbol: STRING,
  name: STRING,
  last_updated: DATETIME
})
```

#### 2. Article
```cypher
(:Article {
  url: STRING,              // Primary key
  title: STRING,
  summary: STRING,
  published: DATETIME,
  fetched: DATETIME,
  source: STRING            // "alpha_vantage", "newsapi", "reddit"
})
```

#### 3. Sentiment
```cypher
(:Sentiment {
  id: STRING,               // UUID
  score: FLOAT,             // -1.0 to 1.0
  label: STRING,            // "bullish", "bearish", "neutral"
  confidence: FLOAT,        // 0.0 to 1.0
  timestamp: DATETIME,
  method: STRING            // "gemini", "vader", "alpha_vantage"
})
```

### Relationships

```cypher
(:Article)-[:ABOUT]->(:Stock)
(:Article)-[:HAS_SENTIMENT]->(:Sentiment)
(:Stock)-[:CURRENT_SENTIMENT]->(:Sentiment)  // Most recent only
```

## GraphRAG Implementation Strategy

### Phase 1: Data Ingestion Pipeline
```python
# Integration points:
# 1. Sentiment analyzer outputs -> Neo4j nodes
# 2. News articles -> Article nodes
# 3. Relationships extracted via NLP -> Edges
# 4. Real-time updates every 15-60 minutes
```

### Phase 2: Knowledge Graph Construction
- Extract entities from articles using NER (spaCy or Gemini)
- Build topic clusters using LDA or embedding similarity
- Calculate stock correlations from sentiment patterns
- Track source reliability based on prediction accuracy

### Phase 3: RAG Query System
Enable natural language queries like:
- "What drove NVDA sentiment down yesterday?"
- "Show me stocks with similar sentiment patterns to AAPL"
- "Which news sources are most reliable for META?"
- "What entities are frequently mentioned with bearish GOOGL sentiment?"

### Phase 4: Predictive Features
- Sentiment momentum indicators
- Cross-stock sentiment contagion detection
- Early warning system for sentiment shifts
- Source credibility weighting for trading signals

## Technical Implementation

### Required Packages
```
neo4j
neo4j-driver
langchain
langchain-community
sentence-transformers
spacy
python-dotenv
```

### Environment Variables
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=sentiment_graph

# Or Neo4j Aura Cloud
NEO4J_AURA_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_AURA_USERNAME=neo4j
NEO4J_AURA_PASSWORD=your_aura_password
```

### Core Components

#### 1. Graph Manager (`sentiment_graph_manager.py`)
- Connection handling
- Node/relationship CRUD operations
- Batch insertion for performance
- Schema initialization

#### 2. Sentiment Ingestion Service (`sentiment_ingestion.py`)
- Poll sentiment analyzer
- Transform to graph nodes
- Extract entities and relationships
- Queue management for async processing

#### 3. Graph Query Service (`graph_query_service.py`)
- Cypher query templates
- Natural language to Cypher translation (via LangChain)
- Aggregation functions
- Vector similarity search (Neo4j vector index)

#### 4. RAG Integration (`sentiment_rag.py`)
- Embedding generation for articles/sentiment
- Vector storage in Neo4j
- Context retrieval for LLM queries
- Prompt engineering for graph-aware responses

#### 5. MCP Tool Extensions (`mcp_sentiment_tools.py`)
- `query_sentiment_graph`: Natural language graph queries
- `get_sentiment_trends`: Time-series analysis
- `Data Flow

```
1. Existing Sentiment Analyzer (JS)
   Step-by-Step Implementation

### Step 1: Setup Neo4j
```bash
# Option A: Local (Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/yourpassword \
  neo4j:latest

# Option B: Neo4j Aura (Cloud) - Just sign up and get credentials
```

### Step 2: Initialize Schema
```python
# neo4j_connector.py will create constraints and indexes
# Run once to set up the database
python neo4j_connector.py --init
```

### Step 3: Run Collection
```python
# Collect sentiment for all portfolio stocks
pytBasic Queries (For Verification)

### Get Current Sentiment
```cypher
MATCH (s:Stock)-[:CURRENT_SENTIMENT]->(sent:Sentiment)
RETURN s.symbol, sent.score, sent.label, sent.confidence
ORDER BY s.symbol
```

### Count Articles by Source
```cypher
MATCH (a:Article)
RETURN a.source, count(*) as article_count
ORDER BY article_count DESC
```

### Recent Articles for a Stock
```cypher
MATCH (a:Article)-[:ABOUT]->(s:Stock {symbol: 'AAPL'})
RETURN a.title, a.source, a.published
ORDER BY a.published DESC
LIMIT 20 ] RAG response quality validation

### Deployment Phase
- [ ] Deploy Neo4j instance (cloud or local)
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Document API endpoints and usage

## Performance Considerations

### Indexing Strategy
```cypher
// Create indexes for fast lookups
CREATE INDEX stock_symbol FOR (s:Stock) ON (s.symbol);
CREATE INDEX sentiment_timestamp FOR (s:Sentiment) ON (s.timestamp);
CREATE INDEX article_date FOR (a:Article) ON (a.published_date);
CREATE CONSTRAINT stock_unique FOR (s:Stock) REQUIRE s.symbol IS UNIQUE;

// Vector index for RAG
CREATE VECTOR INDEX article_embeddings FOR (a:Article) ON (a.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 768,
  `vector.similarity_function`: 'cosine'
}};
```

### Query Optimization
- Use parameterized queries to enable query caching
- Batch write operations (use UNWIND)
- Limit relationship depth in traversals
- Use PROFILE to identify slow queries

### Data Retention
- Archive sentiment data older than 6 months
- Keep only high-impact articles long-term
- Aggregate historical sentiment into daily summaries

## Next Steps
Phase 1: Get Data Flowing
- [ ] Install Neo4j locally or sign up for Aura
- [ ] Add Neo4j credentials to .env
- [ ] Install Python packages: `pip install neo4j python-dotenv google-generativeai requests`
- [ ] Create `neo4j_connector.py` with basic connection and schema setup
- [ ] Create `sentiment_collector.py` to fetch and analyze articles
- [ ] Create `neo4j_ingestion.py` to write data to graph
- [ ] Test with one stock (NVDA)
- [ ] Run for all 5 portfolio stocks
- [ ] Verify data in Neo4j Browser

### Phase 2: Automation (Later)
- [ ] Schedule collection to run every hour
- [ ] Add error handling and retry logic
- [ ] Set up logging

### Phase 3: Analysis (Future)
- [ ] Build query patterns for trends
- [ ] Add MCP tools to expose graph data
- [ ] Connect to trading signals

## Notes

- Start simple, verify data is flowing correctly
- Gemini API has 60 requests/minute on free tier
- Alpha Vantage has 25 requests/day limit
- Focus on getting clean data stored before building analysis
- Can always expand the schema later