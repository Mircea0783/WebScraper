# WebScraper
Web Scraper
Let's create a Python web scraper for collecting data on a topic of interest. Since you haven't specified a particular interest, I'll build a scraper that collects information about recent books from a popular book review site like Goodreads. You can easily modify the target site or data points to suit your interests (e.g., tech gadgets, movies, recipes). I'll use requests for HTTP requests and BeautifulSoup for parsing HTML, as they’re simple and effective for most scraping tasks.
Prerequisites
Install required libraries: pip install requests beautifulsoup4

Web Scraper Code
This scraper targets the Goodreads "New Releases" page to collect book titles, authors, ratings, and publication dates. It includes error handling, respects the site’s robots.txt, and saves data to a CSV file.
python

import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_robots_txt(url):
    """Check if scraping is allowed by robots.txt."""
    robots_url = '/'.join(url.split('/')[:3]) + '/robots.txt'
    try:
        response = requests.get(robots_url, timeout=5)
        if response.status_code == 200:
            if 'Disallow: /search' in response.text or 'Disallow: /' in response.text:
                logging.warning("Scraping may be restricted by robots.txt")
                return False
        return True
    except requests.RequestException as e:
        logging.error(f"Error checking robots.txt: {e}")
        return True  # Assume allowed if robots.txt is inaccessible

def scrape_goodreads_books(url, max_books=50):
    """Scrape book data from Goodreads."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    book_data = []

    # Check robots.txt
    if not check_robots_txt(url):
        logging.error("Scraping blocked by robots.txt. Exiting.")
        return book_data

    try:
        # Send HTTP request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find book containers (adjust selector based on site structure)
        books = soup.select('tr[itemscope]')  # Goodreads book list items
        if not books:
            logging.warning("No books found. Check the CSS selector or page structure.")
            return book_data

        for book in books[:max_books]:
            try:
                # Extract title
                title_elem = book.select_one('a.bookTitle')
                title = title_elem.get_text(strip=True) if title_elem else 'N/A'

                # Extract author
                author_elem = book.select_one('a.authorName')
                author = author_elem.get_text(strip=True) if author_elem else 'N/A'

                # Extract rating
                rating_elem = book.select_one('span[itemprop="ratingValue"]')
                rating = rating_elem.get_text(strip=True) if rating_elem else 'N/A'

                # Extract publication date
                pub_date_elem = book.select_one('span[itemprop="datePublished"]')
                pub_date = pub_date_elem.get_text(strip=True) if pub_date_elem else 'N/A'

                book_data.append({
                    'title': title,
                    'author': author,
                    'rating': rating,
                    'publication_date': pub_date
                })
                logging.info(f"Scraped: {title}")

            except Exception as e:
                logging.error(f"Error processing book: {e}")
                continue

        logging.info(f"Scraped {len(book_data)} books successfully.")
        return book_data

    except requests.RequestException as e:
        logging.error(f"Error fetching page: {e}")
        return book_data

def save_to_csv(data, filename='books_data.csv'):
    """Save scraped data to a CSV file."""
    if not data:
        logging.warning("No data to save.")
        return

    keys = data[0].keys()
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")

def main():
    # Target URL (Goodreads new releases page)
    url = 'https://www.goodreads.com/book/popular_by_date'
    max_books = 20  # Limit to avoid overloading the server

    # Scrape data
    books = scrape_goodreads_book(url, max_books)

    # Save to CSV
    if books:
        save_to_csv(books, f'books_data_{datetime.now().strftime("%Y%m%d")}.csv')

    # Respectful delay
    time.sleep(2)

if __name__ == '__main__':
    main()

How It Works
Robots.txt Check: Verifies if scraping is allowed by checking the site’s robots.txt.

HTTP Request: Uses requests to fetch the webpage with a user-agent header to mimic a browser.

Parsing: BeautifulSoup parses the HTML to extract book details (title, author, rating, publication date).

Data Storage: Saves the scraped data to a CSV file with a timestamp.

Error Handling: Includes logging for debugging and handles network or parsing errors gracefully.

Rate Limiting: Adds a delay (time.sleep) to avoid overwhelming the server.

Customization
To scrape something else (e.g., tech gadgets from a site like TechRadar):
Change the URL: Update the url in main() to your target site (e.g., https://www.techradar.com/reviews).

Update Selectors: Inspect the target site’s HTML (using browser developer tools) and modify the select calls in scrape_goodreads_books to match the new site’s structure. For example, for TechRadar gadgets, you might use soup.select('article.review') and extract fields like product name, price, or review score.

Adjust Data Fields: Modify the dictionary in book_data.append to include fields relevant to your interest (e.g., price, release_date for gadgets).

Example for Gadgets:
python

# Example for TechRadar
url = 'https://www.techradar.com/reviews'
# In scrape function:
gadgets = soup.select('article.review')
for gadget in gadgets:
    name = gadget.select_one('h2').get_text(strip=True) if gadget.select_one('h2') else 'N/A'
    price = gadget.select_one('.price').get_text(strip=True) if gadget.select_one('.price') else 'N/A'
    # Add to data list

Ethical Considerations
Respect Robots.txt: The script checks robots.txt to ensure compliance.

Rate Limiting: The time.sleep(2) avoids overloading the server. Adjust based on the site’s terms.

Terms of Service: Some sites prohibit scraping. Check the site’s ToS before running the scraper.

Data Usage: Use scraped data responsibly, avoiding redistribution or commercial use without permission.

Output
The script generates a CSV file (e.g., books_data_20250512.csv) with columns: title, author, rating, publication_date. Example:

title,author,rating,publication_date
"Book Title 1","Author Name",4.2,"May 2025"
"Book Title 2","Another Author",3.9,"April 2025"

Notes
Site Structure Changes: Websites update their HTML, which may break selectors. Use browser developer tools to find new selectors if errors occur.

Dynamic Content: If the site uses JavaScript to load data, requests won’t work. Use selenium or playwright instead (e.g., for sites like Amazon with heavy JavaScript).

Legal Risks: Scraping can violate site policies. For personal use, keep requests minimal and non-disruptive.

Scalability: For larger projects, consider using scrapy for better performance and scheduling.

