import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Your news URL to scrape
NEWS_URL = "https://www.ada.lk/latest-news/11"

# File to store previously fetched news links
LOG_FILE = "news_log.txt"
MARKDOWN_FILE = "news.md"

# Function to fetch and parse news page
def fetch_news():
    response = requests.get(NEWS_URL)
    if response.status_code != 200:
        print("Failed to fetch news.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []

    # Find all news preview containers
    for news_div in soup.find_all("div", class_="row bg-white cat-b-row mt-3"):
        link = news_div.find("a", href=True)["href"]
        title = news_div.find("h5").get_text(strip=True)
        date = news_div.find("h6").get_text(strip=True).replace("•", "").strip()
        short_desc = news_div.find("p", class_="cat-b-text").get_text(strip=True)
        image_url = news_div.find("img")["src"]

        news_items.append({
            "link": link,
            "title": title,
            "date": date,
            "short_desc": short_desc,
            "image_url": image_url
        })

    return news_items

# Function to read previous news URLs from the log file
def read_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read().splitlines()

# Function to update the log file with new news URLs
def update_log(new_urls):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(new_urls) + "\n")

# Function to format the news into markdown format with improved readability
def format_news_to_markdown(news_items):
    markdown_content = ""
    for item in news_items:
        # Format the date to a more readable form
        news_date = datetime.strptime(item['date'], "%d %m %Y %H:%M:%S").strftime("%B %d, %Y, %I:%M %p")

        # Adding a line separator before each news item for clarity
        markdown_content += f"\n\n---\n\n"
        
        # Title with the link
        markdown_content += f"**[{item['title']}]({item['link']})**\n"

        # Date of the article
        markdown_content += f"*Published on: {news_date}*\n\n"

        # Short description
        markdown_content += f"_{item['short_desc']}_\n\n"
        
        # Image associated with the news
        markdown_content += f"![Image]({item['image_url']})\n\n"

        # Read more link
        markdown_content += f"[Read more]({item['link']})\n"

    return markdown_content

# Function to update the README file with new news
def update_news_md(new_news):
    existing_news = ""
    if os.path.exists(MARKDOWN_FILE):
        with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
            existing_news = f.read()

    # Append new news to the existing markdown content
    new_news_markdown = format_news_to_markdown(new_news)
    new_content = existing_news + "\n" + new_news_markdown

    with open(MARKDOWN_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

# Main function to scrape and update
def main():
    # Fetch the news
    news_items = fetch_news()

    # Read previously fetched news links from the log
    logged_urls = read_log()

    # Filter out news that has already been logged
    new_news = [news for news in news_items if news['link'] not in logged_urls]

    if new_news:
        # Update the log file with new news URLs
        new_urls = [news['link'] for news in new_news]
        update_log(new_urls)

        # Update the markdown file with new news
        update_news_md(new_news)

        print(f"Added {len(new_news)} new news articles to news.md.")
    else:
        print("No new news to add.")

if __name__ == "__main__":
    main()
