import os
import pandas as pd
from PyPDF2 import PdfReader

def parse_folder(folder_path):
    """
    Parses all files in the folder and extracts book metadata.
    
    Supported Formats:
    - PDF: Extracts title, author, and a sample of text.
    - CSV: Reads structured data with columns: title, author, genre, year, sample_text.
    
    Args:
        folder_path (str): Path to the folder containing book files.

    Returns:
        list[dict]: A list of dictionaries with parsed book metadata.
    """
    books = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if file_name.endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                title = reader.metadata.get('/Title', 'Unknown Title')
                author = reader.metadata.get('/Author', 'Unknown Author')
                genre = 'Unknown Genre'
                year = 'Unknown Year'
                
                sample_text = ""
                for page in reader.pages[:2]:  # Extract text from the first two pages
                    text = page.extract_text()
                    if text:
                        sample_text += text + " "
                
                books.append({
                    'title': title.strip(),
                    'author': author.strip(),
                    'genre': genre,
                    'year': year,
                    'sample_text': sample_text.strip()
                })
            except Exception as e:
                print(f"Error processing PDF {file_name}: {e}")
        
        elif file_name.endswith(".csv"):
            try:
                csv_data = pd.read_csv(file_path)
                required_columns = {'title', 'author', 'genre', 'year', 'sample_text'}
                if not required_columns.issubset(csv_data.columns):
                    print(f"CSV {file_name} is missing required columns.")
                    continue
                
                for _, row in csv_data.iterrows():
                    books.append({
                        'title': row.get('title', 'Unknown Title'),
                        'author': row.get('author', 'Unknown Author'),
                        'genre': row.get('genre', 'Unknown Genre'),
                        'year': row.get('year', 'Unknown Year'),
                        'sample_text': row.get('sample_text', 'No sample text available')
                    })
            except Exception as e:
                print(f"Error processing CSV {file_name}: {e}")
        else:
            print(f"Skipping unsupported file type: {file_name}")
    
    # Filter out incomplete entries
    books = [book for book in books if book['title'] != 'Unknown Title' and book['author'] != 'Unknown Author']
    return books

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing the book files: ")
    if os.path.isdir(folder_path):
        if not os.listdir(folder_path):
            print("The specified folder is empty.")
        else:
            parsed_books = parse_folder(folder_path)
            for book in parsed_books:
                print(book)
    else:
        print("Invalid folder path.")
