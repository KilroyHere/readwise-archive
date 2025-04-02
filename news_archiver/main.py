"""
Main module for the news_archiver package.
"""
import os
import argparse
from news_archiver.config import load_config, set_readwise_token, create_directory
from news_archiver.scrapers import SCRAPERS
from news_archiver.archiver import archive_articles
from news_archiver.readwise_integration import add_articles_to_readwise

def setup_directories(config):
    """
    Set up the necessary directories based on the configuration.
    
    Args:
        config (dict): The configuration dictionary.
    """
    # Create main output directory
    output_dir = config.get('output_directory', 'data')
    create_directory(output_dir)
    
    # Create directories for each source
    sources = config.get('sources', {})
    for source_name, source_config in sources.items():
        if source_config.get('enabled', False):
            create_directory(source_config.get('output_path'))

def scrape_articles(config, source=None, selected_issue=None):
    """
    Scrape articles from all enabled sources or a specific source.
    
    Args:
        config (dict): The configuration dictionary.
        source (str, optional): Specific source to scrape (if None, scrape all enabled sources).
        selected_issue (str, optional): Specific issue to scrape.
    
    Returns:
        dict: Dictionary mapping source names to lists of article URLs.
    """
    results = {}
    sources = config.get('sources', {})
    
    # If a specific source is provided, only scrape that source
    if source and source in sources and source in SCRAPERS:
        if sources[source].get('enabled', False):
            print(f"Scraping articles from {source.capitalize()}...")
            output_path = sources[source].get('output_path')
            scraper_class = SCRAPERS[source]
            scraper = scraper_class(output_path, selected_issue)
            urls = scraper.scrape()
            if urls:
                results[source] = urls
            else:
                print(f"No articles were found from {source.capitalize()} or the process was cancelled.")
        return results
    
    # Otherwise, scrape all enabled sources
    for source_name, source_config in sources.items():
        if source_name in SCRAPERS and source_config.get('enabled', False):
            print(f"Scraping articles from {source_name.capitalize()}...")
            output_path = source_config.get('output_path')
            scraper_class = SCRAPERS[source_name]
            scraper = scraper_class(output_path, selected_issue)
            urls = scraper.scrape()
            if urls:
                results[source_name] = urls
            else:
                print(f"No articles were found from {source_name.capitalize()} or the process was cancelled.")
    
    return results

def list_available_issues(config, source=None):
    """
    List available issues for a specific source or all sources.
    
    Args:
        config (dict): The configuration dictionary.
        source (str, optional): Specific source to list issues for (if None, list for all sources).
    
    Returns:
        dict: Dictionary mapping source names to lists of available issues.
    """
    sources = config.get('sources', {})
    results = {}
    
    # If a specific source is provided, only list issues for that source
    if source and source in sources and source in SCRAPERS:
        if sources[source].get('enabled', False):
            output_path = sources[source].get('output_path')
            scraper_class = SCRAPERS[source]
            scraper = scraper_class(output_path)
            issues = scraper.get_available_issues()
            
            if issues:
                print(f"\nAvailable issues for {source.capitalize()}:")
                for i, issue_name in enumerate(issues.keys()):
                    print(f"{i+1}. {issue_name}")
                results[source] = list(issues.keys())
            else:
                print(f"No issues found for {source.capitalize()}. Please check your internet connection or the website structure may have changed.")
        return results
    
    # Otherwise, list issues for all enabled sources
    for source_name, source_config in sources.items():
        if source_name in SCRAPERS and source_config.get('enabled', False):
            output_path = source_config.get('output_path')
            scraper_class = SCRAPERS[source_name]
            scraper = scraper_class(output_path)
            issues = scraper.get_available_issues()
            
            if issues:
                print(f"\nAvailable issues for {source_name.capitalize()}:")
                for i, issue_name in enumerate(issues.keys()):
                    print(f"{i+1}. {issue_name}")
                results[source_name] = list(issues.keys())
            else:
                print(f"No issues found for {source_name.capitalize()}. Please check your internet connection or the website structure may have changed.")
    
    return results

def process_articles(config, article_urls_by_source):
    """
    Process articles by archiving them and adding to Readwise.
    
    Args:
        config (dict): The configuration dictionary.
        article_urls_by_source (dict): Dictionary mapping source names to lists of article URLs.
    
    Returns:
        dict: Dictionary mapping source names to lists of processed archive URLs.
    """
    results = {}
    sources = config.get('sources', {})
    
    for source_name, article_urls in article_urls_by_source.items():
        if not article_urls:
            print(f"No articles found for {source_name}.")
            continue
        
        source_config = sources.get(source_name, {})
        output_path = source_config.get('output_path')
        
        # Archive the articles
        print(f"Archiving {len(article_urls)} articles from {source_name}...")
        archive_output_path = os.path.join(output_path, 'archives')
        archive_urls = archive_articles(article_urls, archive_output_path)
        
        if not archive_urls:
            print(f"No articles were successfully archived for {source_name}.")
            continue
        
        # Add to Readwise if token is available
        readwise_token = config.get('readwise_token')
        if readwise_token:
            print(f"Adding {len(archive_urls)} archived articles to Readwise...")
            tags = source_config.get('tags', [source_name])
            successful_additions = add_articles_to_readwise(
                archive_urls,
                tags=tags,
                access_token=readwise_token
            )
            print(f"Successfully added {len(successful_additions)} articles to Readwise.")
        else:
            print("Readwise token not configured. Skipping Readwise integration.")
            print("You can set your Readwise token using: news-archiver --token YOUR_TOKEN")
        
        results[source_name] = archive_urls
    
    return results

def run(config_path="config.json", source=None, selected_issue=None, list_issues_only=False):
    """
    Run the full news archiving process.
    
    Args:
        config_path (str): Path to the configuration file.
        source (str, optional): Specific source to use (if None, use all sources).
        selected_issue (str, optional): Specific issue to scrape.
        list_issues_only (bool): If True, only list available issues and exit.
    
    Returns:
        dict: Results of the archiving process.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Set up directories
    setup_directories(config)
    
    # List issues if requested
    if list_issues_only:
        list_available_issues(config, source)
        return {}
    
    # Scrape articles
    article_urls_by_source = scrape_articles(config, source, selected_issue)
    
    # Process articles
    results = process_articles(config, article_urls_by_source)
    
    return results

def main():
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(description="Archive news articles and add them to Readwise.")
    parser.add_argument('--config', default='config.json', help='Path to the configuration file')
    parser.add_argument('--token', help='Set the Readwise API token')
    parser.add_argument('--list-issues', action='store_true', help='List available issues and exit')
    parser.add_argument('--issue', help='Specify issue to archive (e.g., "April 2025")')
    parser.add_argument('--source', choices=['atlantic', 'economist'], help='Specify which news source to use')
    
    args = parser.parse_args()
    
    # Show banner
    print("\n=============================================")
    print("     News Magazine Archiver")
    print("=============================================\n")
    
    # Set Readwise token if provided
    if args.token:
        set_readwise_token(args.token, args.config)
        print(f"Readwise token set in {args.config}")
        return
    
    # Run the main process
    results = run(
        args.config,
        source=args.source,
        selected_issue=args.issue, 
        list_issues_only=args.list_issues
    )
    
    # Don't print summary if just listing issues
    if args.list_issues:
        return
    
    # Print summary
    if results:
        print("\nSummary:")
        for source_name, archive_urls in results.items():
            print(f"{source_name}: {len(archive_urls)} articles archived")
        
        print("\nProcess completed successfully!")
        print("The archived articles will be available in your Readwise Reader account.")
        print("You can view them at: https://readwise.io/reader")
    else:
        print("\nNo articles were archived.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check your internet connection and try again.") 