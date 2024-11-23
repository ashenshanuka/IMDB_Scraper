import requests
from bs4 import BeautifulSoup
import re
from database import create_connection, create_table, insert_movies

def scrape_imdb_top_250():
    """Scrape IMDb Top 250 Movies"""
    # IMDb Top 250 URL
    url = 'https://www.imdb.com/chart/top/'
    
    # Headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Send GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find movie list container
        movie_containers = soup.select('li.ipc-metadata-list-summary-item')
        
        movies_data = []
        
        # Extract movie details
        for movie in movie_containers:
            # Extract movie title
            title_elem = movie.select_one('.ipc-title__text')
            title = title_elem.text.split('. ', 1)[1] if title_elem else 'Unknown'
            
            # Extract year
            year_elem = movie.select_one('.sc-14dd939d-6')
            year = int(year_elem.text) if year_elem else None
            
            # Extract rating
            rating_elem = movie.select_one('.ipc-rating-star--imdb')
            rating = float(rating_elem.text.split()[0]) if rating_elem else None
            
            # Extract total ratings
            ratings_elem = movie.select_one('.sc-14dd939d-4')
            total_ratings = int(re.sub(r'[^\d]', '', ratings_elem.text)) if ratings_elem else None
            
            movies_data.append((title, year, rating, total_ratings))
        
        # Database operations
        connection = create_connection()
        if connection:
            create_table(connection)
            insert_movies(connection, movies_data)
            connection.close()
        
        print(f"Successfully scraped top{len(movies_data)} movies!")
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Scraping error: {e}")

def main():
    scrape_imdb_top_250()

if __name__ == "__main__":
    main()