"""
Setup script for the news_archiver package.
"""
from setuptools import setup, find_packages

setup(
    name="news_archiver",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "news-archiver=news_archiver.main:main",
        ],
    },
    python_requires=">=3.6",
    description="A package for archiving news articles and saving them to Readwise Reader",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/news_archiver",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 