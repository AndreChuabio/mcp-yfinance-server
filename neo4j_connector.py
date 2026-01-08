import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jConnector:
    """
    Neo4j Aura connector for sentiment data storage and retrieval.
    Manages connection pooling, schema initialization, and CRUD operations.
    """

    def __init__(self):
        """Initialize Neo4j connection using environment variables."""
        self.uri = os.getenv('NEO4J_URI')
        self.username = os.getenv('NEO4J_USERNAME')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')

        if not all([self.uri, self.username, self.password]):
            raise ValueError("Missing Neo4j credentials in .env file")

        self.driver: Optional[Driver] = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to Neo4j Aura with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password),
                    max_connection_pool_size=10,
                    connection_timeout=30
                )
                self.driver.verify_connectivity()
                logger.info(f"Connected to Neo4j at {self.uri}")
                return
            except (ServiceUnavailable, AuthError) as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise

    def close(self) -> None:
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def initialize_schema(self) -> None:
        """Create constraints and indexes for optimal performance."""
        constraints_and_indexes = [
            "CREATE CONSTRAINT stock_symbol_unique IF NOT EXISTS FOR (s:Stock) REQUIRE s.symbol IS UNIQUE",
            "CREATE CONSTRAINT article_url_unique IF NOT EXISTS FOR (a:Article) REQUIRE a.url IS UNIQUE",
            "CREATE INDEX sentiment_timestamp IF NOT EXISTS FOR (s:Sentiment) ON (s.timestamp)",
            "CREATE INDEX article_published IF NOT EXISTS FOR (a:Article) ON (a.published)"
        ]

        with self.driver.session(database=self.database) as session:
            for query in constraints_and_indexes:
                try:
                    session.run(query)
                    logger.info(f"Executed: {query}")
                except Exception as e:
                    logger.warning(
                        f"Schema query failed (may already exist): {e}")

    def create_stock(self, symbol: str, name: str) -> None:
        """
        Create or update a Stock node.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            name: Full company name
        """
        query = """
        MERGE (s:Stock {symbol: $symbol})
        SET s.name = $name,
            s.last_updated = datetime()
        RETURN s
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol, name=name)
            logger.info(f"Created/updated Stock node: {symbol}")

    def create_article(self, article_data: Dict[str, Any]) -> bool:
        """
        Create an Article node if it doesn't exist.

        Args:
            article_data: Dict with keys: url, title, summary, published, source

        Returns:
            True if article was created, False if it already exists
        """
        query = """
        MERGE (a:Article {url: $url})
        ON CREATE SET 
            a.title = $title,
            a.summary = $summary,
            a.published = datetime($published),
            a.fetched = datetime(),
            a.source = $source,
            a.is_new = true
        ON MATCH SET
            a.is_new = false
        RETURN a.is_new AS is_new
        """

        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                url=article_data['url'],
                title=article_data['title'],
                summary=article_data.get('summary', ''),
                published=article_data['published'],
                source=article_data['source']
            )
            record = result.single()
            is_new = record.get('is_new', False) if record else False

            if is_new:
                logger.info(
                    f"Created Article: {article_data['title'][:50]}...")
            else:
                logger.debug(f"Article already exists: {article_data['url']}")

            return is_new

    def create_sentiment(self, sentiment_data: Dict[str, Any]) -> str:
        """
        Create a Sentiment node.

        Args:
            sentiment_data: Dict with keys: score, label, confidence, method

        Returns:
            sentiment_id: UUID of created sentiment node
        """
        query = """
        CREATE (s:Sentiment {
            id: randomUUID(),
            score: $score,
            label: $label,
            confidence: $confidence,
            timestamp: datetime(),
            method: $method
        })
        RETURN s.id AS sentiment_id
        """

        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                score=sentiment_data['score'],
                label=sentiment_data['label'],
                confidence=sentiment_data['confidence'],
                method=sentiment_data['method']
            )
            sentiment_id = result.single()['sentiment_id']
            logger.debug(
                f"Created Sentiment: {sentiment_data['label']} ({sentiment_data['score']:.2f})")
            return sentiment_id

    def link_article_to_stock(self, article_url: str, stock_symbol: str) -> None:
        """Create ABOUT relationship between Article and Stock."""
        query = """
        MATCH (a:Article {url: $url})
        MATCH (s:Stock {symbol: $symbol})
        MERGE (a)-[:ABOUT]->(s)
        """

        with self.driver.session(database=self.database) as session:
            session.run(query, url=article_url, symbol=stock_symbol)
            logger.debug(f"Linked article to {stock_symbol}")

    def link_article_to_sentiment(self, article_url: str, sentiment_id: str) -> None:
        """Create HAS_SENTIMENT relationship between Article and Sentiment."""
        query = """
        MATCH (a:Article {url: $url})
        MATCH (s:Sentiment {id: $sentiment_id})
        MERGE (a)-[:HAS_SENTIMENT]->(s)
        """

        with self.driver.session(database=self.database) as session:
            session.run(query, url=article_url, sentiment_id=sentiment_id)
            logger.debug(f"Linked article to sentiment")

    def update_current_sentiment(self, stock_symbol: str, sentiment_id: str) -> None:
        """
        Update CURRENT_SENTIMENT relationship for a stock.
        Removes old relationship and creates new one pointing to latest sentiment.

        Args:
            stock_symbol: Stock ticker symbol
            sentiment_id: UUID of the new current sentiment
        """
        query = """
        MATCH (s:Stock {symbol: $symbol})
        OPTIONAL MATCH (s)-[r:CURRENT_SENTIMENT]->()
        DELETE r
        WITH s
        MATCH (sent:Sentiment {id: $sentiment_id})
        CREATE (s)-[:CURRENT_SENTIMENT]->(sent)
        """

        with self.driver.session(database=self.database) as session:
            session.run(query, symbol=stock_symbol, sentiment_id=sentiment_id)
            logger.info(f"Updated CURRENT_SENTIMENT for {stock_symbol}")

    def get_stock_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve current sentiment for a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dict with sentiment data or None if not found
        """
        query = """
        MATCH (s:Stock {symbol: $symbol})-[:CURRENT_SENTIMENT]->(sent:Sentiment)
        RETURN sent.score AS score, 
               sent.label AS label, 
               sent.confidence AS confidence,
               sent.timestamp AS timestamp
        """

        with self.driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol)
            record = result.single()
            if record:
                return {
                    'score': record['score'],
                    'label': record['label'],
                    'confidence': record['confidence'],
                    'timestamp': record['timestamp']
                }
            return None

    def get_article_count_by_source(self) -> List[Dict[str, Any]]:
        """Get article counts grouped by source."""
        query = """
        MATCH (a:Article)
        RETURN a.source AS source, count(*) AS count
        ORDER BY count DESC
        """

        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            return [dict(record) for record in result]

    def get_recent_articles_for_stock(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent articles for a specific stock.

        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        query = """
        MATCH (a:Article)-[:ABOUT]->(s:Stock {symbol: $symbol})
        RETURN a.title AS title, 
               a.source AS source, 
               a.published AS published,
               a.url AS url
        ORDER BY a.published DESC
        LIMIT $limit
        """

        with self.driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol, limit=limit)
            return [dict(record) for record in result]

    def batch_ingest_articles(self, articles_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Batch ingest multiple articles with their sentiments and relationships.

        Args:
            articles_data: List of dicts, each containing:
                - article: Dict with url, title, summary, published, source
                - sentiment: Dict with score, label, confidence, method
                - stock_symbol: str

        Returns:
            Dict with counts of created/skipped articles
        """
        stats = {'created': 0, 'skipped': 0, 'errors': 0}

        for item in articles_data:
            try:
                article = item['article']
                sentiment = item['sentiment']
                stock_symbol = item['stock_symbol']

                is_new = self.create_article(article)
                if is_new:
                    sentiment_id = self.create_sentiment(sentiment)
                    self.link_article_to_stock(article['url'], stock_symbol)
                    self.link_article_to_sentiment(
                        article['url'], sentiment_id)
                    self.update_current_sentiment(stock_symbol, sentiment_id)
                    stats['created'] += 1
                else:
                    stats['skipped'] += 1

            except Exception as e:
                logger.error(f"Error ingesting article: {e}")
                stats['errors'] += 1

        logger.info(
            f"Batch ingestion complete - Created: {stats['created']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        return stats

    def verify_data(self) -> Dict[str, Any]:
        """
        Run verification queries to check data quality.

        Returns:
            Dict with verification results
        """
        results = {}

        with self.driver.session(database=self.database) as session:
            stock_sentiment_query = """
            MATCH (s:Stock)-[:CURRENT_SENTIMENT]->(sent:Sentiment)
            RETURN s.symbol AS symbol, 
                   sent.score AS score, 
                   sent.label AS label, 
                   sent.timestamp AS timestamp
            ORDER BY s.symbol
            """
            result = session.run(stock_sentiment_query)
            results['stock_sentiments'] = [dict(record) for record in result]

            article_count_query = """
            MATCH (a:Article)
            RETURN a.source AS source, count(*) AS count
            ORDER BY count DESC
            """
            result = session.run(article_count_query)
            results['article_counts'] = [dict(record) for record in result]

            total_stocks_query = "MATCH (s:Stock) RETURN count(s) AS count"
            result = session.run(total_stocks_query)
            results['total_stocks'] = result.single()['count']

            total_articles_query = "MATCH (a:Article) RETURN count(a) AS count"
            result = session.run(total_articles_query)
            results['total_articles'] = result.single()['count']

        return results


def main():
    """Test Neo4j connection and schema initialization."""
    connector = Neo4jConnector()

    try:
        logger.info("Initializing schema...")
        connector.initialize_schema()

        logger.info("Creating test stock...")
        connector.create_stock('NVDA', 'NVIDIA Corporation')

        logger.info("Testing article creation...")
        test_article = {
            'url': 'https://test.com/nvda-article',
            'title': 'NVIDIA Hits New High',
            'summary': 'Test article summary',
            'published': '2026-01-08T10:00:00',
            'source': 'test'
        }
        connector.create_article(test_article)

        logger.info("Schema initialization complete")

        results = connector.verify_data()
        logger.info(f"Verification results: {results}")

    finally:
        connector.close()


if __name__ == '__main__':
    main()
