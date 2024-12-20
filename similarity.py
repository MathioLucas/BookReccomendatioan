import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import spacy
from typing import List, Dict, Tuple
import re

class BookSimilarityEngine:
    CONTENT_WEIGHT = 0.6
    METADATA_WEIGHT = 0.4

    def __init__(self):
        """Initialize the similarity engine with necessary models and vectorizers."""
        self.tfidf = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2)
        )
        self.nlp = spacy.load("en_core_web_sm")

    def preprocess_text(self, text: str) -> str:
        """Preprocess text by removing special characters and normalizing."""
        if not text:
            return ""
        text = re.sub(r"[^\w\s]", " ", text.lower())
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def calculate_content_similarity(self, book1: Dict, book2: Dict) -> float:
        """Calculate content similarity based on book descriptions and metadata."""
        text1 = self._get_combined_text(book1)
        text2 = self._get_combined_text(book2)

        try:
            tfidf_matrix = self.tfidf.fit_transform([text1, text2])
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except ValueError:
            return 0.0

    def _get_combined_text(self, book: Dict) -> str:
        """Combine relevant text fields from a book."""
        text_fields = [
            book.get("title", ""),
            " ".join(book.get("authors", [])),
            book.get("description", ""),
            " ".join(book.get("categories", [])),
        ]
        return " ".join(self.preprocess_text(text) for text in text_fields if text)

    def calculate_metadata_similarity(self, book1: Dict, book2: Dict) -> float:
        """Calculate similarity based on metadata (genres, authors, ratings, etc.)."""
        score = 0.0
        weights = {
            "categories": 0.4,
            "authors": 0.3,
            "ratings": 0.2,
            "length": 0.1,
        }

        categories1 = set(book1.get("categories", []))
        categories2 = set(book2.get("categories", []))
        if categories1 and categories2:
            score += weights["categories"] * len(categories1 & categories2) / max(len(categories1 | categories2), 1)

        authors1 = set(book1.get("authors", []))
        authors2 = set(book2.get("authors", []))
        if authors1 and authors2:
            score += weights["authors"] * len(authors1 & authors2) / max(len(authors1 | authors2), 1)

        rating1 = book1.get("average_rating", 0)
        rating2 = book2.get("average_rating", 0)
        if rating1 and rating2:
            score += weights["ratings"] * (1 - abs(rating1 - rating2) / 5)

        pages1 = book1.get("page_count", 0)
        pages2 = book2.get("page_count", 0)
        if pages1 and pages2:
            score += weights["length"] * (1 - abs(pages1 - pages2) / max(pages1, pages2))

        return score

    def find_similar_books(
        self, target_book: Dict, candidate_books: List[Dict], num_recommendations: int = 5
    ) -> List[Tuple[Dict, float]]:
        """Find similar books by combining content and metadata similarity."""
        similarities = []

        for candidate in candidate_books:
            if candidate.get("id") == target_book.get("id"):
                continue

            content_sim = self.calculate_content_similarity(target_book, candidate)
            metadata_sim = self.calculate_metadata_similarity(target_book, candidate)

            combined_sim = (content_sim * self.CONTENT_WEIGHT) + (metadata_sim * self.METADATA_WEIGHT)
            similarities.append((candidate, combined_sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:num_recommendations]

    def get_recommendations(
        self, user_books: List[Dict], candidate_books: List[Dict], num_recommendations: int = 5
    ) -> List[Dict]:
        """Get book recommendations based on user's reading history."""
        scores = defaultdict(float)

        for user_book in user_books:
            similar_books = self.find_similar_books(
                user_book, candidate_books, num_recommendations=len(candidate_books)
            )
            for book, sim_score in similar_books:
                scores[book["id"]] += sim_score / len(user_books)

        ranked_books = sorted(
            [(book, scores[book["id"]]) for book in candidate_books if book["id"] in scores],
            key=lambda x: x[1],
            reverse=True,
        )

        return [book for book, _ in ranked_books[:num_recommendations]]

if __name__ == "__main__":
    engine = BookSimilarityEngine()

    book1 = {
        "id": "1",
        "title": "The Hobbit",
        "authors": ["J.R.R. Tolkien"],
        "categories": ["Fantasy", "Adventure"],
        "description": "A fantasy novel about a hobbit who goes on an adventure.",
        "average_rating": 4.5,
        "page_count": 300,
    }

    book2 = {
        "id": "2",
        "title": "The Lord of the Rings",
        "authors": ["J.R.R. Tolkien"],
        "categories": ["Fantasy", "Epic"],
        "description": "An epic fantasy novel about a quest to destroy a powerful ring.",
        "average_rating": 4.7,
        "page_count": 1200,
    }

    print("Content similarity:", engine.calculate_content_similarity(book1, book2))
    print("Metadata similarity:", engine.calculate_metadata_similarity(book1, book2))
