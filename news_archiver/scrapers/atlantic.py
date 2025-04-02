"""
Module for scraping articles from The Atlantic magazine.
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

class AtlanticScraper(BaseScraper):
    """Scraper for The Atlantic magazine."""
    
    def __init__(self, output_path="data/atlantic", selected_issue=None):
        """
        Initialize the Atlantic scraper.
        
        Args:
            output_path (str): Directory to save output files.
            selected_issue (str, optional): Specific issue to scrape (e.g., "April 2025").
                                           If None, will prompt for selection.
        """
        super().__init__(output_path)
        create_directory(self.output_path)
        self.backissues_url = "https://www.theatlantic.com/magazine/backissues/"
        self.selected_issue = selected_issue
        self.issue_urls = {}
    
    def get_available_issues(self):
        """
        Get a list of available magazine issues from the backissues page.
        
        Returns:
            dict: Dictionary mapping issue names to their URLs.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            print(f"Fetching magazine issues from {self.backissues_url}...")
            response = requests.get(self.backissues_url, headers=headers)
            response.raise_for_status()
            
            # Save the HTML content for debugging
            debug_path = os.path.join(self.output_path, "backissues_debug.html")
            with open(debug_path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Saved debug HTML to {debug_path}")
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # The backissues page has each issue in the layout
            issue_links = {}
            
            # Try to find the issue links based on what we know about the page structure
            # Look for links containing month names which are likely to be issue links
            month_patterns = ['January', 'February', 'March', 'April', 'May', 'June', 
                             'July', 'August', 'September', 'October', 'November', 'December',
                             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            # First, try to find all issues the standard way
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.text.strip()
                
                # Check if it's an issue link - either by URL pattern or by text content
                if ('/magazine/archive/' in href or '/magazine/toc/' in href) and text:
                    # Check if the text contains a month name and a year (like "April 2023")
                    if any(month in text for month in month_patterns) and any(str(year) in text for year in range(2000, 2030)):
                        issue_name = text.replace('Latest Issue', '').strip()
                        full_url = href if href.startswith('http') else f"https://www.theatlantic.com{href}"
                        issue_links[issue_name] = full_url
            
            # If no issues found, try a more aggressive approach by looking at all links
            if not issue_links:
                print("No issues found with standard approach, trying alternative method...")
                
                # Find all links anywhere on the page that look like issue links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.text.strip()
                    
                    # Look for any link that mentions a month and year
                    if text and any(month in text for month in month_patterns) and any(str(year) in text for year in range(2000, 2030)):
                        # Make sure it's an Atlantic URL
                        if '/magazine/' in href:
                            issue_name = text
                            full_url = href if href.startswith('http') else f"https://www.theatlantic.com{href}"
                            issue_links[issue_name] = full_url
            
            # If still no issues found, try an even more aggressive approach
            if not issue_links:
                print("Still no issues found, trying pattern matching on text...")
                
                # Look for text nodes that match month/year patterns
                for element in soup.find_all(text=True):
                    text = element.strip()
                    # Check if it looks like "Month Year"
                    if text and any(month in text for month in month_patterns) and any(str(year) in text for year in range(2000, 2030)):
                        # Try to find a nearby link
                        parent = element.parent
                        if parent:
                            nearby_link = parent.find('a', href=True)
                            if nearby_link and '/magazine/' in nearby_link.get('href', ''):
                                href = nearby_link.get('href', '')
                                issue_name = text
                                full_url = href if href.startswith('http') else f"https://www.theatlantic.com{href}"
                                issue_links[issue_name] = full_url
            
            # Manual fallback with known patterns if automatic detection fails
            if not issue_links:
                print("Automatic detection failed, using manual fallback with known URLs...")
                current_year = 2025  # Update this as needed
                
                # Generate URLs for the current and previous year's issues
                for year in range(current_year-1, current_year+1):
                    for month_num, month_name in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 
                                        'July', 'August', 'September', 'October', 'November', 'December'], 1):
                        issue_name = f"{month_name} {year}"
                        # Format month as 2 digits (01, 02, etc.)
                        month_str = f"{month_num:02d}"
                        url = f"https://www.theatlantic.com/magazine/toc/{year}/{month_str}/"
                        issue_links[issue_name] = url
            
            self.issue_urls = issue_links
            
            if issue_links:
                print(f"Found {len(issue_links)} issues.")
            else:
                print("No issues found. The website structure may have changed.")
                
            return issue_links
            
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching backissues: {e}")
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
        
        # Sort issues - this is tricky because they're in Month Year format
        # For simplicity, we'll display them as is (they appear newest first on the site)
        issues_list = list(self.issue_urls.keys())
        
        # Try to sort by most recent first
        try:
            # Sort issues by year (descending) and then by month (descending)
            month_order = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            def get_sort_key(issue_name):
                # Extract year and month from issue name (format: "Month Year")
                parts = issue_name.split()
                if len(parts) >= 2:
                    try:
                        year = int(parts[-1])  # Last part should be the year
                        # Find the month in the remaining parts
                        month = 0
                        for part in parts[:-1]:
                            if part in month_order:
                                month = month_order[part]
                                break
                        return (-year, -month)  # Negative to sort descending
                    except (ValueError, IndexError):
                        pass
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
        file_path = os.path.join(self.output_path, "atlantic_issue.html")
        
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
    
    def extract_article_tags(self, html_path):
        """
        Extract article tags from the HTML file.
        
        Args:
            html_path (str): Path to the HTML file.
        
        Returns:
            str: Path to the saved article tags file or None if failed.
        """
        tags_path = os.path.join(self.output_path, "article_tags.txt")
        
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file.read(), "html.parser")
            
            # Try different approaches to find article content
            article_tags = soup.find_all("article")
            
            # If no article tags found, try other common containers
            if not article_tags:
                # Look for divs with article-like classes
                article_containers = soup.find_all(["div", "section"], class_=lambda c: c and any(
                    term in c.lower() for term in ["article", "post", "content", "entry"]
                ))
                article_tags.extend(article_containers)
            
            # If still no article tags found, try with link elements that seem to be article links
            if not article_tags:
                article_links = soup.find_all("a", href=lambda h: h and "/magazine/archive/" in h)
                article_tags.extend(article_links)
            
            with open(tags_path, "w", encoding="utf-8") as output_file:
                for tag in article_tags:
                    output_file.write(str(tag) + "\n")
            
            print(f"Article tags extracted and saved to {tags_path}")
            return tags_path
        
        except FileNotFoundError:
            print(f"Error: HTML file {html_path} not found.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    
    def extract_article_links(self, tags_path):
        """
        Extract article links from the article tags file.
        
        Args:
            tags_path (str): Path to the article tags file.
        
        Returns:
            list: List of article links or empty list if failed.
        """
        links_path = os.path.join(self.output_path, "articles.txt")
        
        try:
            with open(tags_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Try different patterns to extract article links
                links = re.findall(r'href=\"(https://www.theatlantic.com/magazine/archive/[^\'\" >]+)\"', content)
                
                # If no links found with the above pattern, try a more general one
                if not links:
                    links = re.findall(r'href=\"([^\'\" >]+?)\"', content)
                    # Filter to only include Atlantic magazine links
                    links = [link for link in links if 'theatlantic.com/magazine/' in link]
                
                # If links still empty, try once more with a very broad pattern
                if not links:
                    links = re.findall(r'(https://www.theatlantic.com/[^\'\" >]+)', content)
                    # Filter to only include magazine links
                    links = [link for link in links if '/magazine/' in link]
            
            # Ensure all links are properly formed
            article_links = []
            for link in set(links):
                if not link.startswith('http'):
                    link = f"https://www.theatlantic.com{link}" if link.startswith('/') else f"https://www.theatlantic.com/{link}"
                article_links.append(link)
            
            with open(links_path, "w", encoding="utf-8") as output_file:
                for link in article_links:
                    output_file.write(link + "\n")
            
            print(f"Article links extracted and saved to {links_path}")
            if not article_links:
                print("No article links found. The website structure may have changed.")
            else:
                print(f"Found {len(article_links)} article links.")
                
            return article_links
        
        except FileNotFoundError:
            print(f"Error: Tags file {tags_path} not found.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
    
    def scrape(self):
        """
        Run the full scraping process for The Atlantic.
        
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
        
        tags_path = self.extract_article_tags(html_path)
        if not tags_path:
            return []
        
        return self.extract_article_links(tags_path)

# For backward compatibility
def run_full_scrape(output_path="data/atlantic", selected_issue=None):
    """
    Run the full scraping process for The Atlantic.
    
    Args:
        output_path (str): Path to save all output files.
        selected_issue (str, optional): Specific issue to scrape.
    
    Returns:
        list: List of article links or empty list if failed.
    """
    scraper = AtlanticScraper(output_path, selected_issue)
    return scraper.scrape() 