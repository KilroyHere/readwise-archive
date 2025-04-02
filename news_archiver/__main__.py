"""
Entry point for running the package as a module.
"""
import sys
import os

# Add the parent directory to the path if needed
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    # Import here to avoid circular imports
    from news_archiver.main import main
    main() 