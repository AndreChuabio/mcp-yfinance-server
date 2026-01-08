import logging
from typing import Dict, List, Any
from neo4j_connector import Neo4jConnector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jIngestion:
    """
    Handles batch ingestion of sentiment data into Neo4j.
    Manages data validation, deduplication, and relationship updates.
    """

    def __init__(self, connector: Neo4jConnector = None):
        """
        Initialize ingestion handler.

        Args:
            connector: Optional Neo4jConnector instance. Creates new one if not provided.
        """
        self.connector = connector if connector else Neo4jConnector()
        self.own_connector = connector is None

    def validate_article_data(self, article_data: Dict[str, Any]) -> bool:
        """
        Validate article data before ingestion.

        Args:
            article_data: Dict containing article, sentiment, and stock_symbol

        Returns:
            True if data is valid, False otherwise
        """
        try:
            article = article_data.get('article', {})
            sentiment = article_data.get('sentiment', {})
            stock_symbol = article_data.get('stock_symbol')

            if not article.get('url'):
                logger.warning("Article missing URL, skipping")
                return False

            if not article.get('title'):
                logger.warning(f"Article missing title: {article.get('url')}")
                return False

            if not stock_symbol:
                logger.warning(
                    f"Article missing stock symbol: {article.get('url')}")
                return False

            if not isinstance(sentiment.get('score'), (int, float)):
                logger.warning(
                    f"Invalid sentiment score: {sentiment.get('score')}")
                return False

            if sentiment['score'] < -1.0 or sentiment['score'] > 1.0:
                logger.warning(
                    f"Sentiment score out of range: {sentiment['score']}")
                return False

            if sentiment.get('label') not in ['bullish', 'bearish', 'neutral']:
                logger.warning(
                    f"Invalid sentiment label: {sentiment.get('label')}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating article data: {e}")
            return False

    def ingest_batch(self, articles_data: List[Dict[str, Any]], batch_size: int = 15) -> Dict[str, int]:
        """
        Ingest articles in batches with validation.

        Args:
            articles_data: List of article dictionaries
            batch_size: Number of articles to process at once

        Returns:
            Dict with statistics: created, skipped, errors, invalid
        """
        stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'invalid': 0,
            'total': len(articles_data)
        }

        valid_articles = []
        for article_data in articles_data:
            if self.validate_article_data(article_data):
                valid_articles.append(article_data)
            else:
                stats['invalid'] += 1

        logger.info(
            f"Validated {len(valid_articles)}/{len(articles_data)} articles")

        for i in range(0, len(valid_articles), batch_size):
            batch = valid_articles[i:i + batch_size]
            logger.info(
                f"Processing batch {i//batch_size + 1}: {len(batch)} articles")

            try:
                batch_stats = self.connector.batch_ingest_articles(batch)
                stats['created'] += batch_stats['created']
                stats['skipped'] += batch_stats['skipped']
                stats['errors'] += batch_stats['errors']

            except Exception as e:
                logger.error(f"Batch ingestion failed: {e}")
                stats['errors'] += len(batch)

        logger.info(f"Ingestion complete - Total: {stats['total']}, Created: {stats['created']}, "
                    f"Skipped: {stats['skipped']}, Invalid: {stats['invalid']}, Errors: {stats['errors']}")

        return stats

    def ingest_for_stock(self, stock_symbol: str, company_name: str,
                         articles_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Ingest articles for a specific stock.
        Ensures stock node exists before ingesting articles.

        Args:
            stock_symbol: Stock ticker symbol
            company_name: Full company name
            articles_data: List of processed articles from collector

        Returns:
            Dict with ingestion statistics
        """
        logger.info(f"Starting ingestion for {stock_symbol}")

        try:
            self.connector.create_stock(stock_symbol, company_name)
            logger.info(f"Stock node ready: {stock_symbol}")

        except Exception as e:
            logger.error(f"Failed to create stock node: {e}")
            return {
                'created': 0,
                'skipped': 0,
                'errors': len(articles_data),
                'invalid': 0,
                'total': len(articles_data)
            }

        stats = self.ingest_batch(articles_data)

        logger.info(f"Completed ingestion for {stock_symbol}: {stats}")
        return stats

    def verify_ingestion(self, stock_symbol: str) -> Dict[str, Any]:
        """
        Verify data was ingested correctly for a stock.

        Args:
            stock_symbol: Stock ticker to verify

        Returns:
            Dict with verification details
        """
        results = {}

        try:
            current_sentiment = self.connector.get_stock_sentiment(
                stock_symbol)
            results['current_sentiment'] = current_sentiment

            recent_articles = self.connector.get_recent_articles_for_stock(
                stock_symbol, limit=5)
            results['recent_articles'] = recent_articles
            results['article_count'] = len(recent_articles)

            logger.info(f"Verification for {stock_symbol}:")
            logger.info(f"  Current sentiment: {current_sentiment}")
            logger.info(f"  Recent articles: {len(recent_articles)}")

        except Exception as e:
            logger.error(f"Verification failed for {stock_symbol}: {e}")
            results['error'] = str(e)

        return results

    def close(self) -> None:
        """Close the Neo4j connection if we own it."""
        if self.own_connector and self.connector:
            self.connector.close()


def main():
    """Test ingestion with sample data."""
    from sentiment_collector import SentimentCollector

    logger.info("Testing ingestion pipeline")

    collector = SentimentCollector()
    ingestion = Neo4jIngestion()

    try:
        logger.info("Initializing Neo4j schema...")
        ingestion.connector.initialize_schema()

        logger.info("Collecting sample data for NVDA...")
        articles = collector.collect_for_stock('NVDA', 'NVIDIA Corporation')

        if not articles:
            logger.warning("No articles collected for testing")
            return

        logger.info(f"Ingesting {len(articles)} articles...")
        stats = ingestion.ingest_for_stock(
            'NVDA', 'NVIDIA Corporation', articles)

        logger.info(f"\nIngestion results: {stats}")

        logger.info("\nVerifying ingestion...")
        verification = ingestion.verify_ingestion('NVDA')

        logger.info("\nAPI usage:")
        logger.info(collector.get_rate_limit_status())

    except Exception as e:
        logger.error(f"Test failed: {e}")

    finally:
        ingestion.close()


if __name__ == '__main__':
    main()
