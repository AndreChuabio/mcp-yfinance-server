# MCP YFinance Server with Sentiment Analysis

A financial sentiment analysis server that combines news and social media data to provide real-time sentiment scores for stock tickers.

## Features

- Real-time sentiment analysis using Google Gemini AI
- News sentiment from Alpha Vantage and NewsAPI
- Social sentiment from Reddit (r/wallstreetbets, r/stocks, r/investing)
- Intelligent caching to minimize API calls
- Batch processing for multiple tickers
- Historical sentiment tracking
- Trending ticker detection

## Setup

1. Install dependencies:
```bash
cd mcp-server
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Add your API keys to `.env`:
   - `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - `ALPHA_VANTAGE_API_KEY`: Get from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - `NEWS_API_KEY`: Get from [NewsAPI](https://newsapi.org/register)
   - Reddit credentials (optional): Get from [Reddit Apps](https://www.reddit.com/prefs/apps)

4. Start the server:
```bash
npm start
```

## API Endpoints

### Health Check
```bash
GET /
```

Returns server status and available endpoints.

### Single Ticker Sentiment
```bash
GET /sentiment/ticker/{symbol}?social=true
```

Analyzes sentiment for a single ticker.

**Parameters:**
- `symbol`: Stock ticker (e.g., AAPL, TSLA)
- `social`: Include social media sentiment (optional, default: false)

**Response:**
```json
{
  "ticker": "AAPL",
  "timestamp": "2025-12-10T00:00:00Z",
  "sentiment_score": 0.45,
  "sentiment_label": "positive",
  "confidence": 0.78,
  "sources_analyzed": 25,
  "source_breakdown": {
    "news": {"score": 0.52, "count": 15},
    "social": {"score": 0.38, "count": 10}
  },
  "top_headlines": [
    {
      "title": "Apple announces new product",
      "score": 0.8,
      "source": "Reuters",
      "url": "https://..."
    }
  ]
}
```

### Historical Sentiment
```bash
GET /sentiment/ticker/{symbol}/history?days=7
```

Retrieves cached historical sentiment data.

**Parameters:**
- `symbol`: Stock ticker
- `days`: Number of days to retrieve (default: 7)

### Batch Analysis
```bash
POST /sentiment/analyze
```

Analyzes multiple tickers simultaneously.

**Request Body:**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "includeSocial": false,
  "newsLimit": 20,
  "socialLimit": 30
}
```

**Response:**
```json
{
  "AAPL": { "sentiment_score": 0.45, ... },
  "MSFT": { "sentiment_score": 0.32, ... },
  "GOOGL": { "sentiment_score": -0.12, ... }
}
```

### Trending Tickers
```bash
GET /sentiment/trending?tickers=AAPL,TSLA,NVDA&threshold=0.3
```

Identifies tickers with significant sentiment shifts.

**Parameters:**
- `tickers`: Comma-separated list of tickers
- `threshold`: Minimum absolute sentiment score (default: 0.3)

## Sentiment Scoring

Scores range from -1 (very negative) to +1 (very positive):
- **0.2 to 1.0**: Positive sentiment
- **-0.2 to 0.2**: Neutral sentiment
- **-1.0 to -0.2**: Negative sentiment

## Testing

Run all tests:
```bash
npm test
```

Or test individual components:
```bash
# Start server first
npm start

# In another terminal
node tests/sentiment.test.js
```

## Architecture

```
src/
├── index.js                    # Main server with routes
└── sentiment/
    ├── sentimentAnalyzer.js    # Core sentiment logic with Gemini AI
    ├── newsProvider.js         # Alpha Vantage & NewsAPI integration
    ├── socialProvider.js       # Reddit API integration
    └── cache.js                # In-memory caching layer
```

## Performance

- Cached responses reduce API calls by 60%+
- Single ticker analysis: <2s
- Batch analysis (5 tickers): <5s
- Cache TTL: 30 minutes (configurable)

## Rate Limits

Free tier limits:
- Gemini AI: 60 requests/minute
- Alpha Vantage: 25 requests/day
- NewsAPI: 100 requests/day
- Reddit: 60 requests/minute

## Limitations

- Historical data limited to cached entries
- Social sentiment requires Reddit API credentials
- News sentiment quality depends on article availability
- Gemini AI fallback to VADER if rate limited

## Next Steps

1. Integrate with trading strategies
2. Add database persistence for backtesting
3. Implement real-time streaming
4. Add more sentiment data sources
5. Create visualization dashboard

## Author

Andre Chua (andre102599@gmail.com)
GitHub: https://github.com/AndreChuabio
