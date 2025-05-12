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