import requests
import hashlib
import logging
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GDELTCollector:
    """
    GDELT DOC 2.0 API collector for real-time global news monitoring.
    Provides high-volume article collection with built-in tone scores.
    """

    BASE_URL = 'http://api.gdeltproject.org/api/v2/doc/doc'

    TRUSTED_DOMAINS = [
        'reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com',
        'cnbc.com', 'marketwatch.com', 'forbes.com', 'barrons.com',
        'businessinsider.com', 'seekingalpha.com', 'benzinga.com',
        'investing.com', 'fool.com', 'thestreet.com', 'nasdaq.com',
        'finance.yahoo.com', 'ap.org', 'nytimes.com', 'economist.com'
    ]

    def __init__(self):
        """Initialize GDELT collector with session management."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GDELTCollector/1.0 (Research Project)'
        })
        self.article_cache = set()
        self.gdelt_calls = 0

    def collect_articles(
        self,
        ticker: str,
        company_name: str,
        days: int = 7,
        max_records: int = 250,
        min_relevance: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Collect articles from GDELT for a ticker.

        Args:
            ticker: Stock ticker symbol
            company_name: Full company name for search
            days: Number of days to look back
            max_records: Maximum articles to retrieve
            min_relevance: Minimum relevance score to include

        Returns:
            List of processed article dictionaries
        """
        logger.info(f"Collecting GDELT articles for {ticker} ({company_name})")

        search_terms = self._build_search_query(ticker, company_name)

        params = {
            'query': search_terms,
            'mode': 'artlist',
            'maxrecords': max_records,
            'format': 'json',
            'timespan': f'{days}d',
            'sort': 'hybridrel'
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            self.gdelt_calls += 1

            if not response.text or response.text.strip() == '':
                logger.warning(f"Empty response from GDELT for {ticker}")
                return []

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Response text: {response.text[:500]}")
                return []

            articles = data.get('articles', [])

            logger.info(
                f"GDELT returned {len(articles)} raw articles for {ticker}")

            processed = self._process_articles(articles, ticker, min_relevance)

            logger.info(
                f"Processed {len(processed)} relevant articles for {ticker}")

            return processed

        except requests.exceptions.RequestException as e:
            logger.error(f"GDELT API error for {ticker}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected GDELT error for {ticker}: {e}")
            return []

    def _build_search_query(self, ticker: str, company_name: str) -> str:
        """
        Build optimized GDELT search query.

        Args:
            ticker: Stock ticker
            company_name: Full company name

        Returns:
            Search query string
        """
        company_short = company_name.split()[0]

        # Special case for META - use longer recognizable names
        if ticker == "META":
            return '("Meta Platforms" OR Facebook)'

        if 'ETF' in company_name or 'Trust' in company_name:
            return f'({ticker} OR "{company_name}")'
        elif len(ticker) < 4 or len(company_short) < 5:
            return f'("{company_name}")'
        else:
            return f'({ticker} OR "{company_short}")'

    def _process_articles(
        self,
        articles: List[Dict],
        ticker: str,
        min_relevance: float
    ) -> List[Dict[str, Any]]:
        """
        Filter and normalize GDELT articles.

        Args:
            articles: Raw GDELT articles
            ticker: Stock ticker for relevance calculation
            min_relevance: Minimum relevance threshold

        Returns:
            List of processed articles
        """
        processed = []

        for article in articles:
            url = article.get('url', '')

            if not url:
                continue

            url_hash = self._hash_url(url)
            if url_hash in self.article_cache:
                continue

            relevance = self._calculate_relevance(article, ticker)
            if relevance < min_relevance:
                continue

            tone = float(article.get('tone', 0))
            sentiment_score = self._normalize_tone(tone)
            confidence = self._calculate_confidence(article, tone)

            try:
                published_dt = datetime.strptime(
                    article.get('seendate', ''),
                    '%Y%m%dT%H%M%SZ'
                )
            except (ValueError, TypeError):
                published_dt = datetime.now()

            processed_article = {
                'url': url,
                'url_hash': url_hash,
                'title': article.get('title', ''),
                'summary': article.get('socialimage', ''),
                'published': published_dt.isoformat(),
                'source': 'gdelt',
                'domain': article.get('domain', ''),
                'language': article.get('language', 'en'),
                'sentiment': {
                    'score': sentiment_score,
                    'label': self._classify_sentiment(tone),
                    'confidence': confidence,
                    'method': 'gdelt_tone',
                    'tone_raw': tone
                },
                'metadata': {
                    'themes': self._parse_semicolon_list(article.get('themes', '')),
                    'locations': self._parse_semicolon_list(article.get('locations', '')),
                    'organizations': self._parse_semicolon_list(article.get('organizations', '')),
                    'persons': self._parse_semicolon_list(article.get('persons', ''))
                },
                'relevance': relevance
            }

            self.article_cache.add(url_hash)
            processed.append(processed_article)

        processed.sort(key=lambda x: abs(
            x['sentiment']['tone_raw']), reverse=True)

        return processed

    def _hash_url(self, url: str) -> str:
        """
        Generate hash of URL for deduplication.

        Args:
            url: Article URL

        Returns:
            MD5 hash of URL
        """
        return hashlib.md5(url.encode()).hexdigest()

    def _calculate_relevance(self, article: Dict, ticker: str) -> float:
        """
        Score article relevance to ticker.

        Args:
            article: GDELT article dict
            ticker: Stock ticker

        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.0
        ticker_lower = ticker.lower()
        title = article.get('title', '').lower()
        url = article.get('url', '').lower()
        domain = article.get('domain', '')
        tone = abs(float(article.get('tone', 0)))

        if ticker_lower in title:
            score += 0.5

        if ticker_lower in url:
            score += 0.2

        if any(d in domain for d in self.TRUSTED_DOMAINS):
            score += 0.3

        if tone > 5:
            score += 0.2
        elif tone > 2:
            score += 0.1

        return min(1.0, score)

    def _calculate_confidence(self, article: Dict, tone: float) -> float:
        """
        Calculate confidence based on source quality and tone strength.

        Args:
            article: GDELT article dict
            tone: GDELT tone value

        Returns:
            Confidence score (0.0 to 1.0)
        """
        domain = article.get('domain', '')

        base_confidence = 0.5

        if any(d in domain for d in self.TRUSTED_DOMAINS):
            base_confidence += 0.2

        abs_tone = abs(tone)
        if abs_tone > 10:
            base_confidence += 0.15
        elif abs_tone > 5:
            base_confidence += 0.1
        elif abs_tone > 2:
            base_confidence += 0.05

        return min(0.85, base_confidence)

    def _normalize_tone(self, tone: float) -> float:
        """
        Normalize GDELT tone to -1.0 to 1.0 scale.

        Args:
            tone: GDELT tone value (-100 to 100)

        Returns:
            Normalized sentiment score (-1.0 to 1.0)
        """
        return max(-1.0, min(1.0, tone / 100.0))

    def _classify_sentiment(self, tone: float) -> str:
        """
        Classify GDELT tone into sentiment label.

        Args:
            tone: GDELT tone value

        Returns:
            Sentiment label (POSITIVE/NEGATIVE/NEUTRAL)
        """
        if tone > 2:
            return 'POSITIVE'
        elif tone < -2:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'

    def _parse_semicolon_list(self, value: str) -> List[str]:
        """
        Parse GDELT semicolon-separated list into array.

        Args:
            value: Semicolon-separated string

        Returns:
            List of strings
        """
        if not value:
            return []
        return [item.strip() for item in value.split(';') if item.strip()]

    def get_call_count(self) -> int:
        """Return number of GDELT API calls made."""
        return self.gdelt_calls

    def clear_cache(self) -> None:
        """Clear the article URL cache."""
        self.article_cache.clear()
        logger.info("GDELT article cache cleared")


def main():
    """Test GDELT collection for NVDA."""
    collector = GDELTCollector()

    try:
        articles = collector.collect_articles(
            ticker='NVDA',
            company_name='NVIDIA Corporation',
            days=7,
            max_records=100
        )

        logger.info(f"\nCollected {len(articles)} articles from GDELT")

        if articles:
            logger.info("\nTop 5 articles by tone strength:")
            for i, article in enumerate(articles[:5], 1):
                logger.info(f"\n{i}. {article['title']}")
                logger.info(f"   Source: {article['domain']}")
                logger.info(f"   Sentiment: {article['sentiment']['label']} "
                            f"(score: {article['sentiment']['score']:.2f}, "
                            f"confidence: {article['sentiment']['confidence']:.2f})")
                logger.info(f"   Relevance: {article['relevance']:.2f}")
                logger.info(f"   URL: {article['url'][:80]}...")

            avg_sentiment = sum(a['sentiment']['score']
                                for a in articles) / len(articles)
            logger.info(f"\nAverage sentiment: {avg_sentiment:.3f}")

            trusted = sum(1 for a in articles
                          if any(d in a['domain'] for d in collector.TRUSTED_DOMAINS))
            logger.info(f"Articles from trusted domains: {trusted}/{len(articles)} "
                        f"({trusted/len(articles)*100:.1f}%)")

        logger.info(f"\nGDELT API calls: {collector.get_call_count()}")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == '__main__':
    main()
