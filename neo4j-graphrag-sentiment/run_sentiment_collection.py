import argparse
import logging
import sys
from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sentiment_collector import SentimentCollector
from neo4j_ingestion import Neo4jIngestion
from portfolio_config import (
    PORTFOLIO_TICKERS,
    get_pending_tickers,
    get_ticker_info,
    get_collection_params,
    get_all_symbols
)

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


def run_collection_for_stock(
    symbol: str,
    company_name: str,
    collector: SentimentCollector,
    ingestion: Neo4jIngestion,
    sources: List[str] = None,
    days: int = 7
) -> Dict:
    """
    Run the complete collection and ingestion pipeline for a single stock.

    Args:
        symbol: Stock ticker symbol
        company_name: Full company name
        collector: SentimentCollector instance
        ingestion: Neo4jIngestion instance
        sources: List of sources to use
        days: Number of days to look back

    Returns:
        Dict with results including stats and verification
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing {symbol} - {company_name}")
    logger.info(f"{'='*60}\n")

    start_time = datetime.now()

    try:
        articles = collector.collect_for_stock(
            symbol,
            company_name,
            sources=sources,
            days=days
        )

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


def run_full_portfolio(
    collector: SentimentCollector,
    ingestion: Neo4jIngestion,
    sources: List[str] = None,
    pending_only: bool = False,
    parallel: bool = False
) -> List[Dict]:
    """
    Run collection for multiple stocks in the portfolio.

    Args:
        collector: SentimentCollector instance
        ingestion: Neo4jIngestion instance
        sources: List of sources to use
        pending_only: Only process tickers with PENDING status
        parallel: Process tickers in parallel

    Returns:
        List of results for each stock
    """
    logger.info("\n" + "="*60)
    logger.info("STARTING PORTFOLIO SENTIMENT COLLECTION")
    logger.info("="*60 + "\n")

    start_time = datetime.now()
    results = []

    tickers_to_process = get_pending_tickers() if pending_only else PORTFOLIO_TICKERS

    logger.info(f"Processing {len(tickers_to_process)} tickers")

    if parallel:
        logger.info("Using parallel processing")
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for ticker_info in tickers_to_process:
                symbol = ticker_info['symbol']
                company_name = ticker_info['name']
                ticker_type = ticker_info['type']

                params = get_collection_params(ticker_type)

                future = executor.submit(
                    run_collection_for_stock,
                    symbol,
                    company_name,
                    collector,
                    ingestion,
                    sources,
                    params['days']
                )
                futures[future] = symbol

            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    results.append({
                        'symbol': symbol,
                        'status': 'error',
                        'error': str(e)
                    })
    else:
        for ticker_info in tickers_to_process:
            symbol = ticker_info['symbol']
            company_name = ticker_info['name']
            ticker_type = ticker_info['type']

            params = get_collection_params(ticker_type)

            result = run_collection_for_stock(
                symbol,
                company_name,
                collector,
                ingestion,
                sources,
                params['days']
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
    logger.info(f"  GDELT: {api_usage.get('gdelt', 0)} calls")
    logger.info(f"  Alpha Vantage: {api_usage['alpha_vantage']}/25 daily")
    logger.info(f"  NewsAPI: {api_usage['newsapi']}/100 daily")

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

    except Exception as e:
        logger.error(f"Verification failed: {e}")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Collect sentiment data for portfolio stocks and store in Neo4j'
    )
    parser.add_argument(
        '--ticker',
        type=str,
        help='Single stock symbol to process (e.g., NVDA)'
    )
    parser.add_argument(
        '--portfolio-mode',
        action='store_true',
        help='Process all portfolio stocks'
    )
    parser.add_argument(
        '--pending-only',
        action='store_true',
        help='Only process tickers with PENDING status'
    )
    parser.add_argument(
        '--sources',
        type=str,
        default='gdelt,alpha_vantage,newsapi',
        help='Comma-separated list of sources (gdelt,alpha_vantage,newsapi,yahoo,google)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for articles'
    )
    parser.add_argument(
        '--init-schema',
        action='store_true',
        help='Initialize Neo4j schema before collection'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Process multiple tickers in parallel'
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

        sources = args.sources.split(',') if args.sources else None

        if args.ticker:
            symbol = args.ticker.upper()
            ticker_info = get_ticker_info(symbol)

            if not ticker_info:
                logger.error(f"Unknown stock symbol: {symbol}")
                logger.info(f"Valid symbols: {', '.join(get_all_symbols())}")
                sys.exit(1)

            params = get_collection_params(ticker_info['type'])
            days = args.days if args.days != 7 else params['days']

            result = run_collection_for_stock(
                symbol,
                ticker_info['name'],
                collector,
                ingestion,
                sources,
                days
            )

            if result['status'] != 'success':
                sys.exit(1)

        elif args.portfolio_mode:
            results = run_full_portfolio(
                collector,
                ingestion,
                sources,
                args.pending_only,
                args.parallel
            )

            failed = [r for r in results if r['status'] != 'success']
            if failed:
                logger.warning(f"\n{len(failed)} stocks failed to process")
                for r in failed:
                    logger.warning(
                        f"  {r['symbol']}: {r.get('error', 'Unknown error')}")
        else:
            logger.error("Must specify either --ticker or --portfolio-mode")
            parser.print_help()
            sys.exit(1)

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
