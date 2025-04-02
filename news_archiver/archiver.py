"""
Module for archiving articles using archive.today.
"""
import requests
from bs4 import BeautifulSoup
import os
import time

def create_directory(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_archive_links(article_urls, output_path="data/archives"):
    """
    Generate archive.today links for a list of article URLs.
    
    Args:
        article_urls (list): List of article URLs to archive.
        output_path (str): Path to save the generated archive links.
    
    Returns:
        list: List of archive.today URLs.
    """
    create_directory(output_path)
    archive_links = []
    
    for url in article_urls:
        archive_links.append(f'http://archive.today/{url}')
    
    # Save the archive links to a file
    links_path = os.path.join(output_path, "archive_links.txt")
    with open(links_path, 'w') as outfile:
        for link in archive_links:
            outfile.write(f"{link}\n")
    
    print(f"Archive links generated and saved to {links_path}")
    return archive_links

def get_final_redirected_url(initial_url, max_retries=3, retry_delay=2):
    """
    Fetches the final URL after following all redirects.
    
    Args:
        initial_url (str): The starting URL that may redirect.
        max_retries (int): Maximum number of retry attempts.
        retry_delay (int): Delay between retries in seconds.
    
    Returns:
        str: The final URL after all redirects or None if failed.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(initial_url, headers=headers)
            return response.url
        except requests.RequestException as e:
            print(f"Attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print(f"Failed to get redirected URL for {initial_url} after {max_retries} attempts")
    return None

def extract_actual_archive_link(archive_page_url, max_retries=3, retry_delay=2):
    """
    Extract the actual archive link from an archive.today page.
    
    Args:
        archive_page_url (str): The URL of the archive.today page.
        max_retries (int): Maximum number of retry attempts.
        retry_delay (int): Delay between retries in seconds.
    
    Returns:
        str: The actual archive link or None if not found.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(archive_page_url, headers=headers)
            
            if response.status_code == 429:
                print("Rate limited (429). Waiting before retrying...")
                time.sleep(retry_delay * 2)  # Longer delay for rate limiting
                continue
            elif response.status_code != 200:
                print(f"Failed to fetch page: {response.status_code}")
                time.sleep(retry_delay)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the first div with class "TEXT-BLOCK"
            text_block = soup.find("div", class_="TEXT-BLOCK")
            
            if text_block:
                # Find the first anchor tag inside this div
                archive_link = text_block.find("a", href=True)
                if archive_link:
                    return archive_link["href"]
            
            print(f"No archive link found in {archive_page_url} on attempt {attempt+1}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    return None

def process_archive_links(archive_links, output_path="data/archives"):
    """
    Process a list of archive.today links to get the final archive URLs.
    
    Args:
        archive_links (list): List of archive.today URLs.
        output_path (str): Path to save the processed archive links.
    
    Returns:
        list: List of final archive URLs.
    """
    create_directory(output_path)
    final_archive_urls = []
    
    for link in archive_links:
        print(f"Processing: {link}")
        
        # Get the redirected URL
        redirected_url = get_final_redirected_url(link)
        if not redirected_url:
            continue
        
        print(f"Redirected to: {redirected_url}")
        
        # Extract the actual archive link
        actual_archive_link = extract_actual_archive_link(redirected_url)
        if actual_archive_link:
            print(f"Extracted archive link: {actual_archive_link}")
            final_archive_urls.append(actual_archive_link)
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    # Save the final archive links to a file
    final_links_path = os.path.join(output_path, "final_archive_links.txt")
    with open(final_links_path, 'w') as outfile:
        for link in final_archive_urls:
            outfile.write(f"{link}\n")
    
    print(f"Final archive links saved to {final_links_path}")
    return final_archive_urls

def archive_articles(article_urls, output_path="data/archives"):
    """
    Run the full archiving process for a list of article URLs.
    
    Args:
        article_urls (list): List of article URLs to archive.
        output_path (str): Path to save all output files.
    
    Returns:
        list: List of final archive URLs.
    """
    # Generate archive.today links
    archive_links = get_archive_links(article_urls, output_path)
    
    # Process the archive links to get the final archive URLs
    return process_archive_links(archive_links, output_path) 