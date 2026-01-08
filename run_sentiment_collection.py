import argparse
import logging
import sys
from typing import Dict, List
from datetime import datetime
from sentiment_collector import SentimentCollector
from neo4j_ingestion import Neo4jIngestion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORTFOLIO_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'shares': 9},
    'NVDA': {'name': 'NVIDIA Corporation', 'shares': 12},
    'MSFT': {'name': 'Microsoft Corporation', 'shares': 6},
    'GOOGL': {'name': 'Alphabet Inc.', 'shares': 13},
    'META': {'name': 'Meta Platforms Inc.', 'shares': 7}
}


def run_collection_for_stock(symbol: str, company_name: str,
                             collector: SentimentCollector,
                             ingestion: Neo4jIngestion) -> Dict:
    """
    Run the complete collection and ingestion pipeline for a single stock.

    Args:
        symbol: Stock ticker symbol
        company_name: Full company name
        collector: SentimentCollector instance
        ingestion: Neo4jIngestion instance

    Returns:
        Dict with results including stats and verification
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing {symbol} - {company_name}")
    logger.info(f"{'='*60}\n")

    start_time = datetime.now()

    try:
        articles = collector.collect_for_stock(symbol, company_name)

        if not articles:
            logger.warning(f"No articles collected for {symbol}")
            return {
                'symbol': symbol,
                'status': 'no_data',
                'articles_collected': 0,
                'stats': {},
                'duration_seconds': 0
            }

        stats = ingestion.ingest_for_stock(symbol, company_name, articles)

        verification = ingestion.verify_ingestion(symbol)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            'symbol': symbol,
            'status': 'success',
            'articles_collected': len(articles),
            'stats': stats,
            'verification': verification,
            'duration_seconds': duration
        }

        logger.info(f"\n{symbol} Summary:")
        logger.info(f"  Articles collected: {len(articles)}")
        logger.info(f"  Articles created: {stats.get('created', 0)}")
        logger.info(f"  Articles skipped: {stats.get('skipped', 0)}")
        logger.info(f"  Duration: {duration:.1f}s")

        if verification.get('current_sentiment'):
            sent = verification['current_sentiment']
            logger.info(
                f"  Current sentiment: {sent.get('label')} ({sent.get('score'):.2f})")

        return result

    except Exception as e:
        logger.error(f"Error processing {symbol}: {e}")
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            'symbol': symbol,
            'status': 'error',
            'error': str(e),
            'duration_seconds': duration
        }


def run_full_portfolio(collector: SentimentCollector, ingestion: Neo4jIngestion) -> List[Dict]:
    """
    Run collection for all stocks in the portfolio.

    Args:
        collector: SentimentCollector instance
        ingestion: Neo4jIngestion instance

    Returns:
        List of results for each stock
    """
    logger.info("\n" + "="*60)
    logger.info("STARTING FULL PORTFOLIO SENTIMENT COLLECTION")
    logger.info("="*60 + "\n")

    start_time = datetime.now()
    results = []

    for symbol, info in PORTFOLIO_STOCKS.items():
        result = run_collection_for_stock(
            symbol,
            info['name'],
            collector,
            ingestion
        )
        results.append(result)

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    logger.info("\n" + "="*60)
    logger.info("PORTFOLIO COLLECTION COMPLETE")
    logger.info("="*60 + "\n")

    successful = sum(1 for r in results if r['status'] == 'success')
    total_articles = sum(r.get('articles_collected', 0) for r in results)
    total_created = sum(r.get('stats', {}).get('created', 0) for r in results)

    logger.info(f"Overall Summary:")
    logger.info(f"  Stocks processed: {len(results)}")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Total articles collected: {total_articles}")
    logger.info(f"  Total articles created in Neo4j: {total_created}")
    logger.info(f"  Total duration: {total_duration/60:.1f} minutes")

    api_usage = collector.get_rate_limit_status()
    logger.info(f"\nAPI Usage:")
    logger.info(f"  Alpha Vantage: {api_usage['alpha_vantage']}/25 daily")
    logger.info(f"  NewsAPI: {api_usage['newsapi']}/100 daily")
    logger.info(f"  Gemini: {api_usage['gemini']}/60 per minute")

    return results


def print_final_verification(ingestion: Neo4jIngestion) -> None:
    """Print final verification queries."""
    logger.info("\n" + "="*60)
    logger.info("FINAL DATA VERIFICATION")
    logger.info("="*60 + "\n")

    try:
        verification = ingestion.connector.verify_data()

        logger.info(f"Total stocks: {verification.get('total_stocks', 0)}")
        logger.info(f"Total articles: {verification.get('total_articles', 0)}")

        logger.info("\nArticles by source:")
        for source_data in verification.get('article_counts', []):
            logger.info(f"  {source_data['source']}: {source_data['count']}")

        logger.info("\nStock sentiments:")
        for stock_data in verification.get('stock_sentiments', []):
            logger.info(f"  {stock_data['symbol']}: {stock_data['label']} "
                        f"(score: {stock_data['score']:.2f})")

    except Exception as e:
        logger.error(f"Verification failed: {e}")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Collect sentiment data for portfolio stocks and store in Neo4j'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        help='Single stock symbol to process (e.g., NVDA). If not provided, processes all portfolio stocks.'
    )
    parser.add_argument(
        '--init-schema',
        action='store_true',
        help='Initialize Neo4j schema (constraints and indexes) before collection'
    )

    args = parser.parse_args()

    collector = None
    ingestion = None

    try:
        logger.info("Initializing collector and ingestion handlers...")
        collector = SentimentCollector()
        ingestion = Neo4jIngestion()

        if args.init_schema:
            logger.info("Initializing Neo4j schema...")
            ingestion.connector.initialize_schema()
            logger.info("Schema initialization complete\n")

        if args.symbol:
            symbol = args.symbol.upper()
            if symbol not in PORTFOLIO_STOCKS:
                logger.error(f"Unknown stock symbol: {symbol}")
                logger.info(
                    f"Valid symbols: {', '.join(PORTFOLIO_STOCKS.keys())}")
                sys.exit(1)

            result = run_collection_for_stock(
                symbol,
                PORTFOLIO_STOCKS[symbol]['name'],
                collector,
                ingestion
            )

            if result['status'] != 'success':
                sys.exit(1)

        else:
            results = run_full_portfolio(collector, ingestion)

            failed = [r for r in results if r['status'] != 'success']
            if failed:
                logger.warning(f"\n{len(failed)} stocks failed to process")
                for r in failed:
                    logger.warning(
                        f"  {r['symbol']}: {r.get('error', 'Unknown error')}")

        print_final_verification(ingestion)

        logger.info("\n" + "="*60)
        logger.info(
            "Collection complete. View data at https://console.neo4j.io")
        logger.info("="*60 + "\n")

    except KeyboardInterrupt:
        logger.info("\nCollection interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        if ingestion:
            ingestion.close()


if __name__ == '__main__':
    main()
