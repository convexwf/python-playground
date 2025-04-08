# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : new_crawler/nachrichtenleicht.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-04-08 11:17
# @UpdateTime : 2025-04-08 11:17

import requests
from pyquery import PyQuery as pq
import time
import re
import json
from typing import List, Dict, Optional


class NachrichtenleichtCrawler:
    """Crawler for nachrichtenleicht.de website articles"""

    def __init__(self):
        self.base_url = "https://www.nachrichtenleicht.de"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def get_article_list(self, url: str) -> List[Dict[str, str]]:
        """
        Get article titles and URLs from article list page

        Args:
            url: URL of the article list page

        Returns:
            List of article info, each element contains title and url
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            response.encoding = "utf-8"

            doc = pq(response.text)
            articles = []

            # Find all article elements
            article_elements = doc("article")

            for article in article_elements.items():
                # Find the link within the article
                link = article.find("a[href]").eq(0)
                if not link:
                    continue

                href = link.attr("href")
                if not href or not href.endswith(".html"):
                    continue

                # Extract article title
                title_text = link.text().strip()

                # Skip if title is too short or contains unwanted text
                if len(title_text) < 10 or "Audio abspielen" in title_text:
                    continue

                # Clean title text
                title = re.sub(r"\s+", " ", title_text).strip()

                # Build full URL
                if href.startswith("/"):
                    full_url = self.base_url + href
                else:
                    full_url = href

                # Avoid duplicates
                if not any(
                    article_info["url"] == full_url for article_info in articles
                ):
                    articles.append({"title": title, "url": full_url})

            print(f"Found {len(articles)} articles")
            return articles

        except Exception as e:
            print(f"Failed to get article list: {e}")
            return []

    def get_article_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        Get detailed content from article URL

        Args:
            url: Article page URL

        Returns:
            Dictionary containing title, summary, content, url. Returns None if failed
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            response.encoding = "utf-8"

            doc = pq(response.text)

            # Extract title - usually in h1 tag
            title_tag = doc("h1").eq(0)
            title = title_tag.text().strip() if title_tag else "No title found"

            # Extract summary from p tag with class article-header-description
            summary_tag = doc("p.article-header-description").eq(0)
            summary = summary_tag.text().strip() if summary_tag else ""

            # Extract main content paragraphs
            doc.remove("figure")  # Remove any figure tags to avoid images
            paragraphs = doc(
                'section > div[class="article-details-text u-space-bottom-xl"]'
            )
            article_content = []

            for p in paragraphs.items():
                text = p.text().strip()
                if text and len(text) > 20:
                    # Skip navigation and footer text
                    if any(
                        skip in text.lower()
                        for skip in [
                            "deutschlandfunk",
                            "kontakt",
                            "impressum",
                            "datenschutz",
                            "ein angebot von",
                            "wie benutze ich",
                            "was ist nachrichtenleicht",
                        ]
                    ):
                        continue

                    # Skip if this is the summary paragraph
                    if summary and text == summary:
                        continue

                    # Skip if this is the title
                    if title and text == title:
                        continue

                    article_content.append(text)

            return {
                "title": title,
                "summary": summary if summary else "No summary found",
                "content": "\n\n".join(article_content),
                "url": url,
            }

        except Exception as e:
            print(f"Failed to get article content {url}: {e}")
            return None

    def crawl_articles(
        self, list_url: str, max_articles: int = 10, delay: float = 1.0
    ) -> List[Dict[str, str]]:
        """
        Complete crawling process: get article list, then get detailed content for each article

        Args:
            list_url: Article list page URL
            max_articles: Maximum number of articles to crawl
            delay: Request interval in seconds

        Returns:
            List of detailed article information
        """
        print("Step 1: Getting article list...")
        article_list = self.get_article_list(list_url)

        if not article_list:
            print("No articles found")
            return []

        # Limit number of articles
        article_list = article_list[:max_articles]

        print(f"Step 2: Getting detailed content for {len(article_list)} articles...")
        detailed_articles = []

        for i, article in enumerate(article_list, 1):
            print(
                f"Processing article {i}/{len(article_list)}: {article['title'][:50]}..."
            )

            detailed_content = self.get_article_content(article["url"])
            if detailed_content:
                detailed_articles.append(detailed_content)

            # Add delay to avoid too frequent requests
            if i < len(article_list):
                time.sleep(delay)

        print(
            f"Successfully got detailed content for {len(detailed_articles)} articles"
        )
        return detailed_articles

    def save_to_json(
        self, articles: List[Dict[str, str]], filename: str = "articles.json"
    ):
        """Save articles to JSON file"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"Articles saved to {filename}")
        except Exception as e:
            print(f"Failed to save file: {e}")


def main():
    """Main function"""
    crawler = NachrichtenleichtCrawler()

    # Target URL
    target_url = (
        "https://www.nachrichtenleicht.de/nachrichtenleicht-vermischtes-100.html"
    )

    # Crawl articles (limit to 5 articles for testing)
    articles = crawler.crawl_articles(target_url, max_articles=50, delay=1.0)

    # Display results
    print("\n=== Crawling Results ===")
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print(f"Title: {article['title']}")
        print(f"Summary: {article['summary'][:100]}...")
        print(f"Content length: {len(article['content'])} characters")
        print(f"URL: {article['url']}")

    # Save to file
    if articles:
        crawler.save_to_json(articles, "tmp/nachrichtenleicht_articles.json")


if __name__ == "__main__":
    main()
