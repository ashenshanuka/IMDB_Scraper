import requests
from bs4 import BeautifulSoup
import re
import time
import random
import logging
from database import DatabaseManager
import mysql.connector
from config import SCRAPER_CONFIG, DB_CONFIG
from utils import (
    clean_text, 
    parse_year, 
    parse_duration, 
    parse_rating, 
    parse_total_ratings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class IMDbScraper:
    def __init__(self):
        self.db_name = DB_CONFIG['database']

    @classmethod
    def extract_movie_details(cls, movie_html):
        soup = BeautifulSoup(movie_html, 'lxml')
        
        # Extract movie title and rank
        title_elem = soup.select_one('.ipc-title')
        if not title_elem:
            return None
        
        full_title = clean_text(title_elem.text)
        if not full_title:
            return None
        
        rank_match = re.match(r'^(\d+)\.\s*(.+)$', full_title)
        if not rank_match:
            return None
        
        movie_rank = int(rank_match.group(1))
        movie_title = clean_text(rank_match.group(2))
        
        # Extract metadata items
        metadata_items = soup.select('.cli-title-metadata-item')
        
        release_year = parse_year(metadata_items[0].text) if metadata_items else None
        duration_minutes = parse_duration(metadata_items[1].text) if len(metadata_items) > 1 else None
        
        # Extract IMDb rating
        rating_elem = soup.select_one('.ipc-rating-star--rating')
        imdb_rating = parse_rating(rating_elem.text if rating_elem else None)
        
        # Extract total ratings
        ratings_count_elem = soup.select_one('.ipc-rating-star--voteCount')
        total_ratings = parse_total_ratings(ratings_count_elem.text if ratings_count_elem else None)
        
        if not all([movie_title, release_year, imdb_rating]):
            return None
        
        return {
            'rank': movie_rank,
            'title': movie_title,
            'year': release_year,
            'duration': duration_minutes,
            'rating': imdb_rating,
            'total_ratings': total_ratings
        }

    @classmethod
    def scrape_top_250(cls):
        for attempt in range(SCRAPER_CONFIG['retry_attempts']):
            try:
                time.sleep(random.uniform(1, 3))
                
                response = requests.get(
                    SCRAPER_CONFIG['url'], 
                    headers=SCRAPER_CONFIG['headers']
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Find all movie containers
                movie_containers = soup.select('.ipc-metadata-list-summary-item__tc')
                
                movies_data = []
                
                for container in movie_containers:
                    movie_details = cls.extract_movie_details(str(container))
                    
                    if movie_details:
                        movies_data.append((
                            movie_details['rank'],
                            movie_details['title'],
                            movie_details['year'],
                            movie_details['duration'],
                            movie_details['rating'],
                            movie_details['total_ratings']
                        ))
                
                logging.info(f"Scraped {len(movies_data)} movies")
                return movies_data
            
            except requests.RequestException as e:
                logging.warning(f"Request attempt {attempt + 1} failed: {e}")
                time.sleep(SCRAPER_CONFIG['retry_delay'])
        
        logging.error("Failed to scrape movies after multiple attempts")
        return []

def main():
    db_name = DB_CONFIG['database']
    connection = DatabaseManager.create_connection()
    if connection:
        logging.info("Creating database and tables if they do not exist")
        DatabaseManager.create_database_if_not_exists(connection, db_name)
        connection.database = db_name  
        DatabaseManager.create_movies_table_if_not_exists(connection)
        connection.close()

    scraper = IMDbScraper()
    movies_data = scraper.scrape_top_250()
    
    if movies_data:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=db_name
        )
        if connection:
            DatabaseManager.insert_movies(connection, movies_data)
            connection.close()

if __name__ == "__main__":
    main()