# News Archiver

A Python package for scraping news articles from The Atlantic and The Economist magazines, archiving them via [archive.today](https://archive.today/), and saving them to [Readwise Reader](https://readwise.io/reader).

## Features

- Browse and select issues from The Atlantic and The Economist magazine archives
- Archive articles using archive.today
- Save archived articles to Readwise Reader
- Modular design for easy extension to additional news sources

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/news_archiver.git
cd news_archiver

# Install the package
pip install -e .
```

## Configuration

Create a `config.json` file or let the application create a default one for you. You can customize it as follows:

```json
{
  "readwise_token": "your_readwise_token_here",
  "output_directory": "data",
  "sources": {
    "atlantic": {
      "enabled": true,
      "output_path": "data/atlantic",
      "tags": ["the atlantic", "magazine"]
    },
    "economist": {
      "enabled": true,
      "output_path": "data/economist",
      "tags": ["the economist", "magazine"]
    }
  }
}
```

## Usage

### Easy Start (Windows)

Simply run the `run_archiver.bat` file and follow the on-screen prompts. You'll be presented with options to select which magazine to archive.

### Easy Start (Unix/Linux/Mac)

```bash
./run_archiver.sh
```

### Command Line

```bash
# List available issues for The Atlantic
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--list-issues', '--source', 'atlantic']); main()"

# List available issues for The Economist
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--list-issues', '--source', 'economist']); main()"

# Archive a specific issue from The Atlantic
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--issue', 'April 2025', '--source', 'atlantic']); main()"

# Archive a specific issue from The Economist
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--issue', 'Mar 29th 2025', '--source', 'economist']); main()"

# Interactive issue selection for The Atlantic
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--source', 'atlantic']); main()"

# Interactive issue selection for The Economist
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--source', 'economist']); main()"

# Set your Readwise API token
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--token', 'YOUR_TOKEN']); main()"

# Use a custom config file
python -c "from news_archiver.main import main; import sys; sys.argv.extend(['--config', 'custom_config.json']); main()"
```

### Python Module

```python
from news_archiver import run

# Run with interactive issue selection for all sources
results = run()

# Run with interactive issue selection for a specific source
results = run(source='atlantic')  # or 'economist'

# Run with a specific issue from The Atlantic
results = run(source='atlantic', selected_issue="April 2025")

# Run with a specific issue from The Economist
results = run(source='economist', selected_issue="Mar 29th 2025")

# Just list available issues
run(list_issues_only=True)  # all sources
run(source='economist', list_issues_only=True)  # specific source

# Run with custom config path
results = run(config_path='custom_config.json')
```

## Supported News Sources

### The Atlantic

The Atlantic scraper supports browsing and archiving articles from The Atlantic magazine's backissues. It provides a list of available issues and allows you to select one to archive.

### The Economist

The Economist scraper supports browsing and archiving articles from The Economist's weekly editions. It uses a regex-based pattern matching approach to extract article links from the weekly edition pages. The article extraction is particularly robust, identifying articles based on the URL pattern `/section/YYYY/MM/DD/article-slug`.

## Adding New News Sources

To add support for a new news source:

1. Create a new scraper module in `news_archiver/scrapers/`
2. Subclass the `BaseScraper` class and implement the `scrape()` method
3. Add your scraper to the `SCRAPERS` dictionary in `news_archiver/scrapers/__init__.py`
4. Update the configuration file to include your new source

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 