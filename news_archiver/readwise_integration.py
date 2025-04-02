"""
Module for integrating with Readwise Reader API.
"""
import requests
import os
from urllib.parse import urlparse
import json

def load_config(config_path="config.json"):
    """
    Load configuration from a JSON file.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        dict: Configuration settings or empty dict if failed.
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using default settings.")
        return {}
    except json.JSONDecodeError:
        print(f"Error parsing config file {config_path}. Using default settings.")
        return {}

def save_config(config, config_path="config.json"):
    """
    Save configuration to a JSON file.
    
    Args:
        config (dict): Configuration settings.
        config_path (str): Path to save the configuration file.
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {config_path}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def add_document_to_readwise(url, title=None, author=None, tags=None, access_token=None):
    """
    Adds a document to Readwise Reader.

    Parameters:
        url (str): The document's unique URL.
        title (str, optional): The document's title.
        author (str, optional): The document's author.
        tags (list of str, optional): A list of tags for the document.
        access_token (str, optional): Readwise access token. If None, loads from config.

    Returns:
        dict: The response from the Readwise API or None if failed.
    """
    # Get access token from config if not provided
    if not access_token:
        config = load_config()
        access_token = config.get('readwise_token')
        
    if not access_token:
        print("No Readwise access token provided or found in config.")
        return None

    # Endpoint URL
    api_url = 'https://readwise.io/api/v3/save/'

    # Headers for authentication
    headers = {
        'Authorization': f'Token {access_token}',
        'Content-Type': 'application/json'
    }

    # Extract domain for auto-tagging if no tags provided
    if not tags:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain:
            tags = [domain.split('.')[-2]] if len(domain.split('.')) > 1 else []

    # Payload with required and optional fields
    payload = {'url': url}
    if title:
        payload['title'] = title
    if author:
        payload['author'] = author
    if tags:
        payload['tags'] = tags

    try:
        # Make the POST request to add the document
        response = requests.post(api_url, headers=headers, json=payload)

        # Check for successful request
        if response.status_code in [200, 201]:
            return response.json()
        else:
            response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error adding document to Readwise: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Error adding document to Readwise: {err}")
        return None

def add_articles_to_readwise(archive_urls, titles=None, author=None, tags=None, access_token=None):
    """
    Add multiple articles to Readwise Reader.
    
    Args:
        archive_urls (list): List of archive URLs to add to Readwise.
        titles (list, optional): List of article titles corresponding to the URLs.
        author (str, optional): Author name to use for all articles.
        tags (list, optional): List of tags to apply to all articles.
        access_token (str, optional): Readwise access token.
    
    Returns:
        list: List of successful additions (responses from the Readwise API).
    """
    successful_additions = []
    
    for i, url in enumerate(archive_urls):
        title = titles[i] if titles and i < len(titles) else None
        
        print(f"Adding to Readwise: {url}")
        response = add_document_to_readwise(url, title, author, tags, access_token)
        
        if response:
            print(f"Successfully added to Readwise: {url}")
            successful_additions.append(response)
        else:
            print(f"Failed to add to Readwise: {url}")
    
    return successful_additions

def set_readwise_token(token, config_path="config.json"):
    """
    Set the Readwise API token in the configuration.
    
    Args:
        token (str): The Readwise API token.
        config_path (str): Path to the configuration file.
    """
    config = load_config(config_path)
    config['readwise_token'] = token
    save_config(config, config_path) 