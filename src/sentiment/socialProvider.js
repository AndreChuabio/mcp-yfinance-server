const axios = require('axios');
require('dotenv').config();

class SocialProvider {
    constructor() {
        this.redditClientId = process.env.REDDIT_CLIENT_ID;
        this.redditClientSecret = process.env.REDDIT_CLIENT_SECRET;
        this.redditToken = null;
        this.tokenExpiry = null;
    }

    async getRedditToken() {
        if (this.redditToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
            return this.redditToken;
        }

        if (!this.redditClientId || !this.redditClientSecret) {
            throw new Error('Reddit API credentials not configured');
        }

        try {
            const auth = Buffer.from(`${this.redditClientId}:${this.redditClientSecret}`).toString('base64');

            const response = await axios.post(
                'https://www.reddit.com/api/v1/access_token',
                'grant_type=client_credentials',
                {
                    headers: {
                        'Authorization': `Basic ${auth}`,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'mcp-sentiment-bot/1.0'
                    },
                    timeout: 10000
                }
            );

            this.redditToken = response.data.access_token;
            this.tokenExpiry = Date.now() + (response.data.expires_in * 1000);

            return this.redditToken;
        } catch (error) {
            throw new Error(`Reddit authentication failed: ${error.message}`);
        }
    }

    async fetchRedditPosts(ticker, subreddits = ['wallstreetbets', 'stocks', 'investing'], limit = 50) {
        try {
            const token = await this.getRedditToken();
            const posts = [];

            for (const subreddit of subreddits) {
                try {
                    const response = await axios.get(
                        `https://oauth.reddit.com/r/${subreddit}/search`,
                        {
                            params: {
                                q: ticker,
                                limit: Math.ceil(limit / subreddits.length),
                                sort: 'new',
                                restrict_sr: true,
                                t: 'day'
                            },
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'User-Agent': 'mcp-sentiment-bot/1.0'
                            },
                            timeout: 10000
                        }
                    );

                    if (response.data?.data?.children) {
                        const subredditPosts = response.data.data.children.map(child => ({
                            title: child.data.title || '',
                            text: child.data.selftext || '',
                            score: child.data.score || 0,
                            numComments: child.data.num_comments || 0,
                            created: child.data.created_utc ? new Date(child.data.created_utc * 1000).toISOString() : new Date().toISOString(),
                            url: `https://reddit.com${child.data.permalink}`,
                            subreddit: subreddit,
                            author: child.data.author || 'unknown'
                        }));

                        posts.push(...subredditPosts);
                    }
                } catch (error) {
                    console.error(`Error fetching from r/${subreddit}:`, error.message);
                }
            }

            return posts.slice(0, limit);
        } catch (error) {
            throw new Error(`Reddit fetch error: ${error.message}`);
        }
    }

    async fetchSocialBatch(tickers, limitPerTicker = 30) {
        const promises = tickers.map(ticker =>
            this.fetchRedditPosts(ticker, ['wallstreetbets', 'stocks', 'investing'], limitPerTicker)
                .catch(error => {
                    console.error(`Error fetching social data for ${ticker}:`, error.message);
                    return [];
                })
        );

        const results = await Promise.all(promises);

        return tickers.reduce((acc, ticker, index) => {
            acc[ticker] = results[index];
            return acc;
        }, {});
    }

    async getSubredditActivity(ticker, timeframe = 'day') {
        try {
            const posts = await this.fetchRedditPosts(ticker, ['wallstreetbets', 'stocks', 'investing'], 100);

            const totalPosts = posts.length;
            const totalScore = posts.reduce((sum, post) => sum + post.score, 0);
            const totalComments = posts.reduce((sum, post) => sum + post.numComments, 0);

            return {
                ticker,
                timeframe,
                totalPosts,
                averageScore: totalPosts > 0 ? totalScore / totalPosts : 0,
                totalComments,
                engagement: totalScore + totalComments,
                topPosts: posts
                    .sort((a, b) => b.score - a.score)
                    .slice(0, 5)
                    .map(post => ({
                        title: post.title,
                        score: post.score,
                        url: post.url
                    }))
            };
        } catch (error) {
            throw new Error(`Activity fetch error: ${error.message}`);
        }
    }
}

module.exports = new SocialProvider();
