const { GoogleGenerativeAI } = require('@google/generative-ai');
const Sentiment = require('sentiment');
const newsProvider = require('./newsProvider');
const socialProvider = require('./socialProvider');
const cache = require('./cache');
require('dotenv').config();

class SentimentAnalyzer {
    constructor() {
        this.sentiment = new Sentiment();
        this.genAI = process.env.GEMINI_API_KEY
            ? new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
            : null;
        this.model = this.genAI ? this.genAI.getGenerativeModel({ model: 'gemini-pro' }) : null;
    }

    async analyzeTicker(ticker, options = {}) {
        const cacheKey = `sentiment:${ticker}:${Date.now() / 60000 | 0}`;

        const cached = cache.get(cacheKey);
        if (cached && !options.skipCache) {
            return { ...cached, fromCache: true };
        }

        try {
            const [newsArticles, socialPosts] = await Promise.all([
                newsProvider.fetchNews(ticker, options.newsLimit || 20),
                options.includeSocial
                    ? socialProvider.fetchRedditPosts(ticker, ['wallstreetbets', 'stocks', 'investing'], options.socialLimit || 30)
                    : Promise.resolve([])
            ]);

            const newsResults = await this.analyzeNewsSentiment(newsArticles);
            const socialResults = options.includeSocial
                ? await this.analyzeSocialSentiment(socialPosts)
                : { score: 0, count: 0, breakdown: [] };

            const totalSources = newsResults.count + socialResults.count;
            const combinedScore = totalSources > 0
                ? (newsResults.score * newsResults.count + socialResults.score * socialResults.count) / totalSources
                : 0;

            const result = {
                ticker: ticker.toUpperCase(),
                timestamp: new Date().toISOString(),
                sentiment_score: this.normalizeScore(combinedScore),
                sentiment_label: this.getLabel(this.normalizeScore(combinedScore)),
                confidence: this.calculateConfidence(totalSources, newsResults.count, socialResults.count),
                sources_analyzed: totalSources,
                source_breakdown: {
                    news: {
                        score: this.normalizeScore(newsResults.score),
                        count: newsResults.count
                    },
                    social: {
                        score: this.normalizeScore(socialResults.score),
                        count: socialResults.count
                    }
                },
                top_headlines: newsResults.topHeadlines
            };

            cache.set(cacheKey, result, 1800);

            return result;
        } catch (error) {
            throw new Error(`Sentiment analysis failed for ${ticker}: ${error.message}`);
        }
    }

    async analyzeNewsSentiment(articles) {
        if (!articles || articles.length === 0) {
            return { score: 0, count: 0, topHeadlines: [] };
        }

        const analyzed = [];

        for (const article of articles) {
            let score = 0;

            if (article.sentiment && typeof article.sentiment.score === 'number') {
                score = article.sentiment.score;
            } else {
                const text = `${article.title} ${article.summary}`.substring(0, 500);

                if (this.model && text.length > 50) {
                    try {
                        score = await this.analyzeWithGemini(text);
                    } catch (error) {
                        console.error('Gemini analysis failed, falling back to VADER:', error.message);
                        score = this.analyzeWithVADER(text);
                    }
                } else {
                    score = this.analyzeWithVADER(text);
                }
            }

            analyzed.push({
                title: article.title,
                score: score,
                source: article.source,
                url: article.url,
                timestamp: article.timestamp
            });
        }

        const avgScore = analyzed.reduce((sum, item) => sum + item.score, 0) / analyzed.length;

        const topHeadlines = analyzed
            .sort((a, b) => Math.abs(b.score) - Math.abs(a.score))
            .slice(0, 5);

        return {
            score: avgScore,
            count: analyzed.length,
            topHeadlines
        };
    }

    async analyzeSocialSentiment(posts) {
        if (!posts || posts.length === 0) {
            return { score: 0, count: 0, breakdown: [] };
        }

        const analyzed = [];

        for (const post of posts) {
            const text = `${post.title} ${post.text}`.substring(0, 500);

            let score = 0;
            if (this.model && text.length > 50) {
                try {
                    score = await this.analyzeWithGemini(text);
                } catch (error) {
                    score = this.analyzeWithVADER(text);
                }
            } else {
                score = this.analyzeWithVADER(text);
            }

            const weightedScore = score * Math.log10(post.score + 10);

            analyzed.push({
                text: post.title,
                score: weightedScore,
                engagement: post.score + post.numComments,
                subreddit: post.subreddit
            });
        }

        const avgScore = analyzed.reduce((sum, item) => sum + item.score, 0) / analyzed.length;

        return {
            score: avgScore,
            count: analyzed.length,
            breakdown: analyzed.slice(0, 10)
        };
    }

    async analyzeWithGemini(text) {
        if (!this.model) {
            return this.analyzeWithVADER(text);
        }

        try {
            const prompt = `Analyze the sentiment of the following financial text and return ONLY a single number between -1 and 1, where -1 is very negative, 0 is neutral, and 1 is very positive. Be precise and consider financial context.\n\nText: "${text}"\n\nSentiment score:`;

            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            const scoreText = response.text().trim();

            const score = parseFloat(scoreText);

            if (isNaN(score) || score < -1 || score > 1) {
                console.warn('Invalid Gemini response, falling back to VADER');
                return this.analyzeWithVADER(text);
            }

            return score;
        } catch (error) {
            console.error('Gemini API error:', error.message);
            return this.analyzeWithVADER(text);
        }
    }

    analyzeWithVADER(text) {
        if (!text || text.length === 0) {
            return 0;
        }

        const result = this.sentiment.analyze(text);
        return result.comparative;
    }

    normalizeScore(score) {
        return Math.max(-1, Math.min(1, score));
    }

    getLabel(score) {
        if (score >= 0.2) return 'positive';
        if (score <= -0.2) return 'negative';
        return 'neutral';
    }

    calculateConfidence(total, newsCount, socialCount) {
        if (total === 0) return 0;

        const volumeScore = Math.min(total / 50, 1);
        const diversityScore = (newsCount > 0 && socialCount > 0) ? 1.0 : 0.7;

        return parseFloat((volumeScore * diversityScore).toFixed(2));
    }

    async analyzeBatch(tickers, options = {}) {
        const promises = tickers.map(ticker =>
            this.analyzeTicker(ticker, options).catch(error => ({
                ticker: ticker.toUpperCase(),
                error: error.message,
                sentiment_score: 0,
                sentiment_label: 'error'
            }))
        );

        const results = await Promise.all(promises);

        return results.reduce((acc, result) => {
            acc[result.ticker] = result;
            return acc;
        }, {});
    }

    async getHistoricalSentiment(ticker, days = 7) {
        const history = [];
        const now = Date.now();

        for (let i = 0; i < days; i++) {
            const dayKey = `sentiment:${ticker}:${(now - i * 86400000) / 60000 | 0}`;
            const cached = cache.get(dayKey);

            if (cached) {
                history.push({
                    date: new Date(now - i * 86400000).toISOString().split('T')[0],
                    score: cached.sentiment_score,
                    label: cached.sentiment_label
                });
            }
        }

        return {
            ticker: ticker.toUpperCase(),
            period: `${days} days`,
            data: history.reverse()
        };
    }

    async getTrendingTickers(tickers, threshold = 0.3) {
        const batch = await this.analyzeBatch(tickers, { includeSocial: true });

        const trending = Object.values(batch)
            .filter(result => !result.error && Math.abs(result.sentiment_score) >= threshold)
            .sort((a, b) => Math.abs(b.sentiment_score) - Math.abs(a.sentiment_score));

        return trending;
    }
}

module.exports = new SentimentAnalyzer();
