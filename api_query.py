import requests
import os
import time
from dotenv import load_dotenv
from functools import lru_cache
from typing import Dict, List, Optional
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
BASE_URL = "https://www.googleapis.com/books/v1/volumes"

# Ensure API key is available
if not API_KEY:
    raise ValueError("GOOGLE_BOOKS_API_KEY not set in environment variables")

# Set up logging
logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

class GoogleBooksAPIError(Exception):
    """Custom exception for Google Books API errors."""
    pass

class RateLimitExceeded(GoogleBooksAPIError):
    """Exception for when rate limit is exceeded."""
    pass

def create_api_url(endpoint: Optional[str], params: Dict) -> str:
    """
    Creates a properly formatted API URL with parameters.
    """
    params["key"] = API_KEY
    param_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{BASE_URL}/{endpoint}?{param_string}" if endpoint else f"{BASE_URL}?{param_string}"

@lru_cache(maxsize=1000)
def fetch_book_details(book_id: str) -> Dict:
    """
    Fetches detailed information about a specific book using its Google Books ID.
    """
    url = create_api_url(book_id, {})
    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 429:  # Rate limit exceeded
            raise RateLimitExceeded("Google Books API rate limit exceeded")

        data = response.json()
        volume_info = data.get("volumeInfo", {})
        return {
            "id": book_id,
            "title": volume_info.get("title", "Unknown"),
            "authors": volume_info.get("authors", []),
            "description": volume_info.get("description", ""),
            "categories": volume_info.get("categories", []),
            "average_rating": volume_info.get("averageRating"),
            "ratings_count": volume_info.get("ratingsCount", 0),
            "publication_date": volume_info.get("publishedDate"),
            "page_count": volume_info.get("pageCount"),
            "language": volume_info.get("language"),
            "preview_link": volume_info.get("previewLink"),
            "isbn": [
                identifier.get("identifier")
                for identifier in volume_info.get("industryIdentifiers", [])
                if identifier.get("type") == "ISBN_13"
            ],
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch book details for {book_id}: {str(e)}")
        raise GoogleBooksAPIError(f"Failed to fetch book details: {str(e)}")

def search_books(query: str, max_results: int = 10) -> List[Dict]:
    """
    Searches for books using various parameters.
    """
    params = {
        "q": query,
        "maxResults": max_results,
        "printType": "books",
        "langRestrict": "en",
    }

    url = create_api_url("", params)

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        books = []

        for item in data.get("items", []):
            book_id = item.get("id")
            if book_id:
                try:
                    book_details = fetch_book_details(book_id)
                    books.append(book_details)
                except GoogleBooksAPIError as e:
                    logging.error(f"Error fetching details for book {book_id}: {str(e)}")
                    continue

                # Add delay only if there are more items to process
                if len(data.get("items", [])) > 1:
                    time.sleep(0.1)

        return books

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to search books: {str(e)}")
        raise GoogleBooksAPIError(f"Failed to search books: {str(e)}")

def get_similar_books(book_id: str, max_results: int = 5) -> List[Dict]:
    """
    Finds similar books based on a given book's categories and authors.
    """
    try:
        book = fetch_book_details(book_id)
        search_terms = []

        if book["categories"]:
            search_terms.extend(book["categories"][:2])  # Use first two categories
        if book["authors"]:
            search_terms.append(f"inauthor:{book['authors'][0]}")  # Use first author

        query = " OR ".join(search_terms)
        similar_books = search_books(query, max_results + 1)  # Add 1 to account for the original book
        similar_books = [b for b in similar_books if b["id"] != book_id]  # Exclude the original book

        return similar_books[:max_results]

    except GoogleBooksAPIError as e:
        logging.error(f"Failed to find similar books for {book_id}: {str(e)}")
        raise GoogleBooksAPIError(f"Failed to find similar books: {str(e)}")

if __name__ == "__main__":
    # Example usage
    try:
        books = search_books("The Hobbit")
        print(f"Found {len(books)} books")

        if books:
            similar = get_similar_books(books[0]["id"])
            print(f"Found {len(similar)} similar books")

    except GoogleBooksAPIError as e:
        print(f"Error: {str(e)}")
