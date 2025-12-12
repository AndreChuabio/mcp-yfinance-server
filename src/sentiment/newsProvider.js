const axios = require('axios');
require('dotenv').config();

class NewsProvider {
    constructor() {
        this.alphaVantageKey = process.env.ALPHA_VANTAGE_API_KEY;
        this.newsApiKey = process.env.NEWS_API_KEY;
    }

    async fetchNews(ticker, limit = 20) {
        const results = [];

        try {
            if (this.alphaVantageKey) {
                const avNews = await this.fetchAlphaVantageNews(ticker, limit);
                results.push(...avNews);
            }
        } catch (error) {
            console.error(`Alpha Vantage news fetch error for ${ticker}:`, error.message);
        }

        try {
            if (this.newsApiKey && results.length < limit) {
                const newsApiResults = await this.fetchNewsAPI(ticker, limit - results.length);
                results.push(...newsApiResults);
            }
        } catch (error) {
            console.error(`NewsAPI fetch error for ${ticker}:`, error.message);
        }

        return results.slice(0, limit);
    }

    async fetchAlphaVantageNews(ticker, limit = 20) {
        try {
            const url = `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=${ticker}&apikey=${this.alphaVantageKey}&limit=${limit}`;

            const response = await axios.get(url, { timeout: 10000 });

            if (response.data.Note) {
                throw new Error('Alpha Vantage API rate limit reached');
            }

            if (!response.data.feed || !Array.isArray(response.data.feed)) {
                return [];
            }

            return response.data.feed.map(article => ({
                title: article.title || '',
                summary: article.summary || '',
                url: article.url || '',
                source: article.source || 'Alpha Vantage',
                timestamp: article.time_published || new Date().toISOString(),
                sentiment: this.parseAlphaVantageSentiment(article, ticker)
            }));
        } catch (error) {
            if (error.code === 'ECONNABORTED') {
                throw new Error('Alpha Vantage request timeout');
            }
            throw error;
        }
    }

    parseAlphaVantageSentiment(article, ticker) {
        if (!article.ticker_sentiment || !Array.isArray(article.ticker_sentiment)) {
            return null;
        }

        const tickerSentiment = article.ticker_sentiment.find(
            ts => ts.ticker === ticker
        );

        if (!tickerSentiment) {
            return null;
        }

        return {
            score: parseFloat(tickerSentiment.ticker_sentiment_score) || 0,
            label: tickerSentiment.ticker_sentiment_label || 'neutral'
        };
    }

    async fetchNewsAPI(ticker, limit = 20) {
        try {
            const query = encodeURIComponent(ticker);
            const url = `https://newsapi.org/v2/everything?q=${query}&language=en&sortBy=publishedAt&pageSize=${limit}&apiKey=${this.newsApiKey}`;

            const response = await axios.get(url, { timeout: 10000 });

            if (response.data.status !== 'ok') {
                throw new Error(`NewsAPI error: ${response.data.message || 'Unknown error'}`);
            }

            if (!response.data.articles || !Array.isArray(response.data.articles)) {
                return [];
            }

            return response.data.articles.map(article => ({
                title: article.title || '',
                summary: article.description || '',
                url: article.url || '',
                source: article.source?.name || 'NewsAPI',
                timestamp: article.publishedAt || new Date().toISOString(),
                sentiment: null
            }));
        } catch (error) {
            if (error.code === 'ECONNABORTED') {
                throw new Error('NewsAPI request timeout');
            }
            throw error;
        }
    }

    async fetchNewsBatch(tickers, limitPerTicker = 10) {
        const promises = tickers.map(ticker =>
            this.fetchNews(ticker, limitPerTicker).catch(error => {
                console.error(`Error fetching news for ${ticker}:`, error.message);
                return [];
            })
        );

        const results = await Promise.all(promises);

        return tickers.reduce((acc, ticker, index) => {
            acc[ticker] = results[index];
            return acc;
        }, {});
    }
}

module.exports = new NewsProvider();
