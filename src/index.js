const http = require('http');
const url = require('url');
const sentimentAnalyzer = require('./sentiment/sentimentAnalyzer');
require('dotenv').config();

const PORT = process.env.PORT || 3000;

async function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;

  res.setHeader('Content-Type', 'application/json');

  try {
    if (req.method === 'GET' && pathname === '/') {
      res.writeHead(200);
      res.end(JSON.stringify({
        status: 'ok',
        message: 'MCP YFinance server with sentiment analysis',
        endpoints: {
          health: 'GET /',
          ticker_sentiment: 'GET /sentiment/ticker/{symbol}',
          ticker_history: 'GET /sentiment/ticker/{symbol}/history?days=7',
          batch_analyze: 'POST /sentiment/analyze',
          trending: 'GET /sentiment/trending?threshold=0.3'
        }
      }));
      return;
    }

    if (req.method === 'GET' && pathname.startsWith('/sentiment/ticker/')) {
      const pathParts = pathname.split('/');
      const symbol = pathParts[3];

      if (!symbol) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: 'Missing ticker symbol' }));
        return;
      }

      if (pathParts[4] === 'history') {
        const days = parseInt(query.days) || 7;
        const result = await sentimentAnalyzer.getHistoricalSentiment(symbol, days);
        res.writeHead(200);
        res.end(JSON.stringify(result));
        return;
      }

      const includeSocial = query.social === 'true';
      const result = await sentimentAnalyzer.analyzeTicker(symbol, { includeSocial });
      res.writeHead(200);
      res.end(JSON.stringify(result));
      return;
    }

    if (req.method === 'POST' && pathname === '/sentiment/analyze') {
      let body = '';

      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        try {
          const data = JSON.parse(body);

          if (!data.tickers || !Array.isArray(data.tickers)) {
            res.writeHead(400);
            res.end(JSON.stringify({ error: 'Invalid request: tickers array required' }));
            return;
          }

          const options = {
            includeSocial: data.includeSocial || false,
            newsLimit: data.newsLimit || 20,
            socialLimit: data.socialLimit || 30
          };

          const result = await sentimentAnalyzer.analyzeBatch(data.tickers, options);
          res.writeHead(200);
          res.end(JSON.stringify(result));
        } catch (error) {
          res.writeHead(400);
          res.end(JSON.stringify({ error: 'Invalid JSON body' }));
        }
      });
      return;
    }

    if (req.method === 'GET' && pathname === '/sentiment/trending') {
      const tickersParam = query.tickers;
      const threshold = parseFloat(query.threshold) || 0.3;

      if (!tickersParam) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: 'Missing tickers parameter' }));
        return;
      }

      const tickers = tickersParam.split(',').map(t => t.trim());
      const result = await sentimentAnalyzer.getTrendingTickers(tickers, threshold);
      res.writeHead(200);
      res.end(JSON.stringify({ trending: result, threshold }));
      return;
    }

    res.writeHead(404);
    res.end(JSON.stringify({ error: 'not_found' }));
  } catch (error) {
    console.error('Request error:', error);
    res.writeHead(500);
    res.end(JSON.stringify({ error: 'Internal server error', message: error.message }));
  }
}

const server = http.createServer(handleRequest);

server.listen(PORT, () => {
  console.log(`MCP YFinance server listening on http://localhost:${PORT}`);
  console.log('Sentiment analysis enabled');
  console.log(`Gemini API: ${process.env.GEMINI_API_KEY ? 'configured' : 'not configured'}`);
});

module.exports = server;
