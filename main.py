from src.file_path import get_folder_path
from src.parser_file import parse_folder
from src.nlp_analysis import analyze_text_tone_and_style
from src.api_query import search_books, get_similar_books
from src.similarity import BookSimilarityEngine
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    similarity_engine = BookSimilarityEngine()
    
    while True:
        print("\nBook Recommendation System")
        print("1. Search for books")
        print("2. Get recommendations from your reading history (PDF/CSV)")
        print("3. Get similar books to a specific book")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            query = input("Enter search term: ")
            try:
                books = search_books(query, max_results=5)
                print("\nSearch Results:")
                for i, book in enumerate(books, 1):
                    print(f"\n{i}. {book['title']}")
                    print(f"   Author(s): {', '.join(book['authors'])}")
                    print(f"   Categories: {', '.join(book['categories'] if book['categories'] else ['N/A'])}")
            except Exception as e:
                print(f"Error searching books: {str(e)}")
                
        elif choice == "2":
            folder_path = get_folder_path()
            try:
                # Parse user's reading history
                user_books = parse_folder(folder_path)
                
                # Get candidate books for recommendations
                print("Fetching potential recommendations...")
                all_genres = set()
                for book in user_books:
                    if book.get('genre'):
                        all_genres.add(book['genre'])
                
                candidate_books = []
                for genre in all_genres:
                    candidates = search_books(f"subject:{genre}", max_results=20)
                    candidate_books.extend(candidates)
                
                # Generate recommendations
                recommendations = similarity_engine.get_recommendations(
                    user_books,
                    candidate_books,
                    num_recommendations=5
                )
                
                print("\nRecommended Books:")
                for i, book in enumerate(recommendations, 1):
                    print(f"\n{i}. {book['title']}")
                    print(f"   Author(s): {', '.join(book['authors'])}")
                    print(f"   Categories: {', '.join(book['categories'] if book['categories'] else ['N/A'])}")
                    
            except Exception as e:
                print(f"Error generating recommendations: {str(e)}")
                
        elif choice == "3":
            query = input("Enter book title to find similar books: ")
            try:
                # Search for the book
                books = search_books(query, max_results=5)
                
                if not books:
                    print("No books found!")
                    continue
                    
                print("\nSelect a book:")
                for i, book in enumerate(books, 1):
                    print(f"{i}. {book['title']} by {', '.join(book['authors'])}")
                
                book_choice = int(input("\nEnter number: ")) - 1
                if 0 <= book_choice < len(books):
                    similar_books = get_similar_books(books[book_choice]['id'])
                    
                    print("\nSimilar Books:")
                    for i, book in enumerate(similar_books, 1):
                        print(f"\n{i}. {book['title']}")
                        print(f"   Author(s): {', '.join(book['authors'])}")
                        print(f"   Categories: {', '.join(book['categories'] if book['categories'] else ['N/A'])}")
                        
            except Exception as e:
                print(f"Error finding similar books: {str(e)}")
                
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()