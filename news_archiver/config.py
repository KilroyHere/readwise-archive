"""
Configuration module for the news_archiver.
"""
import os
import json

# Default configuration values
DEFAULT_CONFIG = {
    "readwise_token": None,
    "output_directory": "data",
    "sources": {
        "atlantic": {
            "enabled": True,
            "output_path": "data/atlantic",
            "tags": ["the atlantic"]
        }
    }
}

def create_directory(dir_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def load_config(config_path="config.json"):
    """
    Load configuration from a JSON file, or create a default one if not exists.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        dict: Configuration settings.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Merge with default config for any missing keys
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Creating default configuration.")
        save_config(DEFAULT_CONFIG, config_path)
        return DEFAULT_CONFIG
    except json.JSONDecodeError:
        print(f"Error parsing config file {config_path}. Using default configuration.")
        return DEFAULT_CONFIG

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

def add_news_source(source_name, enabled=True, output_path=None, tags=None, config_path="config.json"):
    """
    Add a new news source to the configuration.
    
    Args:
        source_name (str): Name of the news source.
        enabled (bool): Whether the source is enabled.
        output_path (str, optional): Custom output path for the source.
        tags (list, optional): Tags for articles from this source.
        config_path (str): Path to the configuration file.
    """
    config = load_config(config_path)
    
    if 'sources' not in config:
        config['sources'] = {}
    
    if not output_path:
        output_path = os.path.join(config.get('output_directory', 'data'), source_name)
    
    if not tags:
        tags = [source_name]
    
    config['sources'][source_name] = {
        'enabled': enabled,
        'output_path': output_path,
        'tags': tags
    }
    
    save_config(config, config_path) 