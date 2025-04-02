"""
Module for scraping articles from The Economist magazine.
"""
import os
import re
import requests
from bs4 import BeautifulSoup
import time
from news_archiver.scrapers import BaseScraper

def create_directory(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

class EconomistScraper(BaseScraper):
    """Scraper for The Economist magazine."""
    
    def __init__(self, output_path="data/economist", selected_issue=None):
        """
        Initialize the Economist scraper.
        
        Args:
            output_path (str): Directory to save output files.
            selected_issue (str, optional): Specific issue to scrape (e.g., "Mar 29th 2025").
                                           If None, will prompt for selection.
        """
        super().__init__(output_path)
        create_directory(self.output_path)
        self.archive_url = "https://www.economist.com/weeklyedition/archive"
        self.selected_issue = selected_issue
        self.issue_urls = {}
    
    def get_available_issues(self):
        """
        Get a list of available magazine issues from the archive page.
        
        Returns:
            dict: Dictionary mapping issue names to their URLs.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            print(f"Fetching magazine issues from {self.archive_url}...")
            response = requests.get(self.archive_url, headers=headers)
            response.raise_for_status()
            
            # Save the HTML content for debugging
            debug_path = os.path.join(self.output_path, "archive_debug.html")
            with open(debug_path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Saved debug HTML to {debug_path}")
            
            soup = BeautifulSoup(response.content, "html.parser")
            issue_links = {}
            
            # Find all issues on the page with date headers
            date_pattern = re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\w+\s+\d{4}\b')
            
            # Look for date elements
            for date_elem in soup.find_all(text=date_pattern):
                date_text = date_elem.strip()
                parent = date_elem.parent
                
                # Find the nearest heading with a title
                title_elem = None
                current = parent
                # Look up for title in parent elements
                while current and not title_elem and current.name != 'body':
                    title_elem = current.find(['h2', 'h3', 'h4'], recursive=False)
                    if not title_elem:
                        current = current.parent
                
                # If no title found looking up, try looking down
                if not title_elem:
                    title_elem = parent.find_next(['h2', 'h3', 'h4'])
                
                # Extract title text or use a default
                title_text = title_elem.text.strip() if title_elem and title_elem != parent else "Weekly Edition"
                
                # Get the issue URL
                # First, try to find a link in the parent element
                issue_link = parent.find('a', href=True)
                # If not found, look for nearby links
                if not issue_link:
                    issue_link = parent.find_next('a', href=True)
                
                if issue_link:
                    href = issue_link.get('href', '')
                    if '/weeklyedition/' in href or '/printedition/' in href:
                        full_url = href if href.startswith('http') else f"https://www.economist.com{href}"
                        issue_name = f"{date_text} - {title_text}"
                        issue_links[issue_name] = full_url
            
            # If no issues found, try a more general approach
            if not issue_links:
                # Find all links that seem to point to weekly editions
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if '/weeklyedition/' in href:
                        # Try to extract date from the URL or from the link text
                        date_match = date_pattern.search(link.text)
                        if date_match:
                            date_text = date_match.group(0)
                            issue_name = f"{date_text} - Weekly Edition"
                            full_url = href if href.startswith('http') else f"https://www.economist.com{href}"
                            issue_links[issue_name] = full_url
            
            self.issue_urls = issue_links
            
            if issue_links:
                print(f"Found {len(issue_links)} issues.")
            else:
                print("No issues found. The website structure may have changed.")
                
            return issue_links
            
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching archive: {e}")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def select_issue(self):
        """
        Prompt the user to select an issue from the available issues.
        
        Returns:
            str: The URL of the selected issue.
        """
        if not self.issue_urls:
            self.get_available_issues()
        
        if not self.issue_urls:
            print("No issues found to select from.")
            return None
            
        # If a specific issue was provided during initialization, use that
        if self.selected_issue and self.selected_issue in self.issue_urls:
            return self.issue_urls[self.selected_issue]
        
        # Otherwise, prompt the user to select an issue
        print("\nAvailable issues:")
        
        # Sort issues by date (newest first)
        issues_list = list(self.issue_urls.keys())
        
        # Try to sort by most recent first
        try:
            # Extract dates and sort
            def get_sort_key(issue_name):
                # Try to extract the date part from the issue name
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\w+\s+(\d{4})', issue_name)
                if date_match:
                    month_str = date_match.group(1)
                    year_str = date_match.group(2)
                    
                    month_order = {
                        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
                    }
                    
                    month = month_order.get(month_str, 0)
                    year = int(year_str) if year_str.isdigit() else 0
                    
                    return (-year, -month)  # Negative to sort descending
                return (0, 0)  # Default sort key
            
            issues_list.sort(key=get_sort_key)
        except Exception as e:
            print(f"Error sorting issues: {e}")
            # If sorting fails, just continue with the unsorted list
        
        for i, issue in enumerate(issues_list):
            print(f"{i+1}. {issue}")
        
        while True:
            try:
                selection = input("\nEnter the number of the issue to archive (or 'q' to quit): ")
                if selection.lower() == 'q':
                    return None
                
                index = int(selection) - 1
                if 0 <= index < len(issues_list):
                    selected_issue = issues_list[index]
                    print(f"Selected issue: {selected_issue}")
                    self.selected_issue = selected_issue
                    return self.issue_urls[selected_issue]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def download_issue_page(self, issue_url):
        """
        Download the HTML content from the selected issue's page.
        
        Args:
            issue_url (str): URL of the selected issue.
            
        Returns:
            str: Path to the saved HTML file or None if failed.
        """
        file_path = os.path.join(self.output_path, "economist_issue.html")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(issue_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(str(soup))
            
            print(f"Issue HTML content downloaded and saved to {file_path}")
            return file_path
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading issue: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    
    def extract_article_links(self, html_path):
        """
        Extract article links from the issue HTML file using the improved regex pattern.
        
        Args:
            html_path (str): Path to the HTML file.
        
        Returns:
            list: List of article links or empty list if failed.
        """
        links_path = os.path.join(self.output_path, "articles.txt")
        
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file.read(), "html.parser")
            
            # Using the regex pattern approach as suggested
            article_links = set()
            # Pattern matches paths like /section/YYYY/MM/DD/article-slug
            article_pattern = re.compile(r"^/[^/]+/\d{4}/\d{2}/\d{2}/[^/]+/?$")
            
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                # Normalize the URL path
                if href.startswith("http") and "economist.com" in href:
                    path = "/" + "/".join(href.split("/")[3:])
                elif href.startswith("/"):
                    path = href
                else:
                    continue
                
                if article_pattern.match(path):
                    full_url = "https://www.economist.com" + path
                    article_links.add(full_url)
            
            # Convert to list and sort
            article_links_list = sorted(article_links)
            
            # Save to file
            with open(links_path, "w", encoding="utf-8") as output_file:
                for link in article_links_list:
                    output_file.write(link + "\n")
            
            print(f"Article links extracted and saved to {links_path}")
            if not article_links_list:
                print("No article links found. The website structure may have changed.")
            else:
                print(f"Found {len(article_links_list)} article links.")
                
            return article_links_list
        
        except FileNotFoundError:
            print(f"Error: HTML file {html_path} not found.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape(self):
        """
        Run the full scraping process for The Economist.
        
        Returns:
            list: List of article links or empty list if failed.
        """
        # Get available issues and let the user select one
        issue_url = self.select_issue()
        if not issue_url:
            print("No issue selected. Exiting.")
            return []
        
        # Download the selected issue page
        html_path = self.download_issue_page(issue_url)
        if not html_path:
            return []
        
        # Extract article links using the regex pattern approach
        return self.extract_article_links(html_path)

# For backward compatibility
def run_full_scrape(output_path="data/economist", selected_issue=None):
    """
    Run the full scraping process for The Economist.
    
    Args:
        output_path (str): Path to save all output files.
        selected_issue (str, optional): Specific issue to scrape.
    
    Returns:
        list: List of article links or empty list if failed.
    """
    scraper = EconomistScraper(output_path, selected_issue)
    return scraper.scrape() 