import os
import logging
import time
import json
import requests
import feedparser
import hashlib
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dotenv import load_dotenv
from gdelt_collector import GDELTCollector

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SentimentCollector:
    """
    Collects financial news from multiple sources.
    Sentiment analysis handled by downstream agents.
    """

    def __init__(self):
        """Initialize API clients and rate limiters."""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')

        self.gdelt_collector = GDELTCollector()

        self.alpha_vantage_calls = 0
        self.news_api_calls = 0
        self.url_cache: Set[str] = set()

    def _respect_rate_limit(self, api_name: str, calls: int, max_calls: int, period_seconds: int) -> None:
        """Simple rate limiting implementation."""
        if calls >= max_calls:
            wait_time = period_seconds
            logger.warning(
                f"{api_name} rate limit reached. Waiting {wait_time}s...")
            time.sleep(wait_time)

    def fetch_alpha_vantage_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news with sentiment from Alpha Vantage API.

        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles to fetch

        Returns:
            List of article dictionaries with native sentiment scores
        """
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured, skipping")
            return []

        self._respect_rate_limit(
            'Alpha Vantage', self.alpha_vantage_calls, 25, 86400)

        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'apikey': self.alpha_vantage_key,
            'limit': min(limit, 50)
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            self.alpha_vantage_calls += 1

            if 'feed' not in data:
                logger.warning(
                    f"Alpha Vantage returned no feed data for {symbol}")
                return []

            articles = []
            for item in data['feed'][:limit]:
                ticker_sentiment = None
                for ticker_data in item.get('ticker_sentiment', []):
                    if ticker_data.get('ticker') == symbol:
                        ticker_sentiment = ticker_data
                        break

                if not ticker_sentiment:
                    continue

                sentiment_score = float(ticker_sentiment.get(
                    'ticker_sentiment_score', 0.0))
                sentiment_label = ticker_sentiment.get(
                    'ticker_sentiment_label', 'neutral').lower()

                if 'bullish' in sentiment_label:
                    sentiment_label = 'bullish'
                elif 'bearish' in sentiment_label:
                    sentiment_label = 'bearish'
                else:
                    sentiment_label = 'neutral'

                article = {
                    'url': item.get('url', ''),
                    'title': item.get('title', ''),
                    'summary': item.get('summary', ''),
                    'published': item.get('time_published', ''),
                    'source': 'alpha_vantage',
                    'sentiment_score': sentiment_score,
                    'sentiment_label': sentiment_label
                }

                if article['published']:
                    try:
                        dt = datetime.strptime(
                            article['published'], '%Y%m%dT%H%M%S')
                        article['published'] = dt.isoformat()
                    except ValueError:
                        article['published'] = datetime.now().isoformat()

                articles.append(article)

            logger.info(
                f"Fetched {len(articles)} articles from Alpha Vantage for {symbol}")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Alpha Vantage news: {e}")
            return []

    def fetch_newsapi_articles(self, symbol: str, company_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch news articles from NewsAPI.

        Args:
            symbol: Stock ticker symbol
            company_name: Company name for search query
            limit: Maximum number of articles to fetch

        Returns:
            List of article dictionaries
        """
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured, skipping")
            return []

        self._respect_rate_limit('NewsAPI', self.news_api_calls, 100, 86400)

        url = 'https://newsapi.org/v2/everything'

        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        params = {
            'q': f'{symbol} OR {company_name}',
            'from': from_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.news_api_key,
            'pageSize': min(limit, 100)
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            self.news_api_calls += 1

            if data.get('status') != 'ok':
                logger.warning(
                    f"NewsAPI returned status: {data.get('status')}")
                return []

            articles = []
            for item in data.get('articles', [])[:limit]:
                article = {
                    'url': item.get('url', ''),
                    'title': item.get('title', ''),
                    'summary': item.get('description', ''),
                    'published': item.get('publishedAt', datetime.now().isoformat()),
                    'source': 'newsapi'
                }

                if article['url'] and article['title']:
                    articles.append(article)

            logger.info(
                f"Fetched {len(articles)} articles from NewsAPI for {symbol}")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching NewsAPI articles: {e}")
            return []

    def fetch_yahoo_finance_rss(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch news articles from Yahoo Finance RSS feed.

        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles to fetch

        Returns:
            List of article dictionaries
        """
        url = f'https://finance.yahoo.com/rss/headline?s={symbol}'

        try:
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                article = {
                    'url': entry.get('link', ''),
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source': 'yahoo_finance_rss'
                }

                if entry.get('published_parsed'):
                    dt = datetime(*entry.published_parsed[:6])
                    article['published'] = dt.isoformat()

                if article['url'] and article['title']:
                    articles.append(article)

            logger.info(
                f"Fetched {len(articles)} articles from Yahoo Finance RSS for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"Yahoo Finance RSS error: {e}")
            return []

    def fetch_google_news_rss(self, symbol: str, company_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch news articles from Google News RSS feed.

        Args:
            symbol: Stock ticker symbol
            company_name: Company name for search
            limit: Maximum number of articles to fetch

        Returns:
            List of article dictionaries
        """
        query = f'{symbol} OR {company_name} stock'
        url = f'https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en'

        try:
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                article = {
                    'url': entry.get('link', ''),
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source': 'google_news_rss'
                }

                if entry.get('published_parsed'):
                    dt = datetime(*entry.published_parsed[:6])
                    article['published'] = dt.isoformat()

                if article['url'] and article['title']:
                    articles.append(article)

            logger.info(
                f"Fetched {len(articles)} articles from Google News RSS for {symbol}")
            return articles

        except Exception as e:
            logger.error(f"Google News RSS error: {e}")
            return []

    def analyze_sentiment_with_gemini(self, text: str, retry_count: int = 3) -> Dict[str, Any]:
        """
        Analyze sentiment using Google Gemini API.

        Args:
            text: Article text to analyze
            retry_count: Number of retries on failure

        Returns:
            Dict with score (-1 to 1), label (bullish/bearish/neutral), and confidence
        """
        if not self.gemini_model:
            logger.warning(
                "Gemini model not available - returning neutral sentiment")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}

        self._respect_rate_limit('Gemini', self.gemini_calls, 60, 60)

        prompt = f"""Analyze the sentiment of this financial news article and respond with ONLY a JSON object in this exact format:
{{"score": <float between -1.0 and 1.0>, "label": "<bullish/bearish/neutral>", "confidence": <float between 0.0 and 1.0>}}

Guidelines:
- score: -1.0 = very bearish, 0.0 = neutral, 1.0 = very bullish
- label: "bullish" (positive), "bearish" (negative), or "neutral"
- confidence: 0.0 = very uncertain, 1.0 = very certain

Article text:
{text[:1000]}

Respond with ONLY the JSON object, no other text."""

        for attempt in range(retry_count):
            try:
                response = self.gemini_model.generate_content(prompt)
                self.gemini_calls += 1

                response_text = response.text.strip()

                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                sentiment = json.loads(response_text)

                sentiment['score'] = max(-1.0, min(1.0,
                                         float(sentiment.get('score', 0.0))))
                sentiment['confidence'] = max(
                    0.0, min(1.0, float(sentiment.get('confidence', 0.5))))
                sentiment['label'] = sentiment.get('label', 'neutral').lower()

                if sentiment['label'] not in ['bullish', 'bearish', 'neutral']:
                    sentiment['label'] = 'neutral'

                logger.debug(f"Gemini sentiment: {sentiment}")
                return sentiment

            except json.JSONDecodeError as e:
                logger.warning(
                    f"Gemini JSON parse error (attempt {attempt + 1}): {e}")
                if attempt == retry_count - 1:
                    return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
                time.sleep(1)

            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt == retry_count - 1:
                    return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
                time.sleep(2)

        return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}

    def _hash_url(self, url: str) -> str:
        """Generate hash for URL deduplication."""
        return hashlib.md5(url.encode()).hexdigest()

    def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate articles based on URL.

        Args:
            articles: List of article dicts

        Returns:
            Deduplicated list
        """
        unique_articles = []
        seen_urls = set()

        for article in articles:
            url = article.get('url', '')
            url_hash = self._hash_url(url)

            if url_hash not in seen_urls and url_hash not in self.url_cache:
                unique_articles.append(article)
                seen_urls.add(url_hash)
                self.url_cache.add(url_hash)

        if len(articles) > len(unique_articles):
            logger.info(
                f"Removed {len(articles) - len(unique_articles)} duplicate articles")

        return unique_articles

    def collect_for_stock(
        self,
        symbol: str,
        company_name: str,
        sources: List[str] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Collect raw articles for a specific stock.

        Args:
            symbol: Stock ticker symbol
            company_name: Full company name
            sources: List of sources to use (gdelt, alpha_vantage, newsapi, yahoo, google)
            days: Number of days to look back

        Returns:
            List of raw articles ready for ingestion
        """
        logger.info(f"Collecting articles for {symbol} ({company_name})")

        if sources is None:
            sources = ['gdelt', 'alpha_vantage', 'yahoo', 'google', 'newsapi']

        all_articles = []

        if 'gdelt' in sources:
            gdelt_articles = self.gdelt_collector.collect_articles(
                ticker=symbol,
                company_name=company_name,
                days=days,
                max_records=250
            )
            all_articles.extend(gdelt_articles)
            logger.info(f"GDELT contributed {len(gdelt_articles)} articles")

        if 'alpha_vantage' in sources:
            av_articles = self.fetch_alpha_vantage_news(symbol, limit=10)
            all_articles.extend(av_articles)

        if 'yahoo' in sources:
            yahoo_articles = self.fetch_yahoo_finance_rss(symbol, limit=20)
            all_articles.extend(yahoo_articles)

        if 'google' in sources:
            google_articles = self.fetch_google_news_rss(
                symbol, company_name, limit=20)
            all_articles.extend(google_articles)

        if 'newsapi' in sources:
            newsapi_articles = self.fetch_newsapi_articles(
                symbol, company_name, limit=15)
            all_articles.extend(newsapi_articles)

        logger.info(f"Total articles collected: {len(all_articles)}")

        all_articles = self._deduplicate_articles(all_articles)
        logger.info(f"After deduplication: {len(all_articles)} articles")

        processed_articles = []
        for article in all_articles:
            try:
                processed_article = {
                    'article': {
                        'url': article.get('url', ''),
                        'title': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'published': article.get('published', ''),
                        'source': article.get('source', ''),
                        'domain': article.get('domain', ''),
                        'metadata': article.get('metadata', {})
                    },
                    'stock_symbol': symbol
                }

                processed_articles.append(processed_article)

            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue

        logger.info(
            f"Successfully processed {len(processed_articles)} articles for {symbol}")
        return processed_articles

    def _select_top_articles_for_gemini(
        self,
        articles: List[Dict[str, Any]],
        top_n: int
    ) -> List[Dict[str, Any]]:
        """
        Select top articles for Gemini analysis based on relevance and tone.

        Args:
            articles: List of articles
            top_n: Number to select

        Returns:
            List of top articles
        """
        scored_articles = []

        for article in articles:
            score = 0.0

            if article.get('source') == 'gdelt':
                score += article.get('relevance', 0.0) * 0.5

                tone_raw = article.get('sentiment', {}).get('tone_raw', 0)
                score += abs(tone_raw) / 100.0 * 0.5
            else:
                score += 0.7

            scored_articles.append((score, article))

        scored_articles.sort(key=lambda x: x[0], reverse=True)

        return [article for _, article in scored_articles[:top_n]]

    def get_rate_limit_status(self) -> Dict[str, int]:
        """Return current API call counts."""
        return {
            'alpha_vantage': self.alpha_vantage_calls,
            'newsapi': self.news_api_calls,
            'gdelt': self.gdelt_collector.get_call_count()
        }


def main():
    """Test sentiment collection for NVDA."""
    collector = SentimentCollector()

    try:
        articles = collector.collect_for_stock('NVDA', 'NVIDIA Corporation')

        logger.info(f"\nCollected {len(articles)} articles")

        if articles:
            logger.info("\nSample article:")
            sample = articles[0]
            logger.info(f"Title: {sample['article']['title']}")
            logger.info(f"Source: {sample['article']['source']}")
            logger.info(
                f"Sentiment: {sample['sentiment']['label']} (score: {sample['sentiment']['score']:.2f})")

        logger.info(f"\nAPI usage: {collector.get_rate_limit_status()}")

    except Exception as e:
        logger.error(f"Test failed: {e}")


if __name__ == '__main__':
    main()
