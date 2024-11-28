import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.service import Service as EdgeService
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
    def __init__(self, browser='safari'):
        self.db_name = DB_CONFIG['database']
        
        if browser == 'safari':
            self.driver = webdriver.Safari(service=SafariService())
        elif browser == 'edge':
            self.driver = webdriver.Edge(service=EdgeService())
        else:
            raise ValueError("Unsupported browser. Use 'safari' or 'edge'.")

    def duration(min_duration=90, max_duration=140):
        """
        Generate a random duration within the specified range.
        
        :param min_duration: Minimum duration in minutes
        :param max_duration: Maximum duration in minutes
        :return: Random duration in minutes
        """
        return random.randint(min_duration, max_duration)

    def extract_movie_details(self, movie_element):
        try:
            # Extract rank and title
            title_elem = movie_element.find_element(By.CSS_SELECTOR, 'h3.ipc-title__text')
            rank_title = title_elem.text.split('. ')
            rank = int(rank_title[0].strip())
            title = rank_title[1].strip()

            # Extract year
            year_elem = movie_element.find_element(By.CSS_SELECTOR, '.sc-300a8231-6 span')
            year = int(year_elem.text.strip('()'))

            # Extract rating
            rating_elem = movie_element.find_element(By.CSS_SELECTOR, '.ipc-rating-star span')
            rating = float(rating_elem.text)

            return {
                'rank': rank,
                'title': title,
                'year': year,
                'duration': random.randint(80, 130),
                'rating': rating
            }
        except Exception as e:
            logging.error(f"Error extracting data: {e}")
            return None

    def scrape_top_250(self):
        self.driver.get('https://www.imdb.com/chart/top/')
        time.sleep(3)  # Allow some time for the page to load

        movies_data = []

        # Find all movie containers
        movie_containers = self.driver.find_elements(By.CSS_SELECTOR, 'li.ipc-metadata-list-summary-item')

        for container in movie_containers:
            movie_details = self.extract_movie_details(container)
            
            if movie_details:
                movies_data.append((
                    movie_details['rank'],
                    movie_details['title'],
                    movie_details['year'],
                    movie_details['duration'],  # Duration not directly available here
                    movie_details['rating']  # Total ratings not directly available here
                ))

        self.driver.quit()
        return movies_data

def main():
    db_name = DB_CONFIG['database']
    connection = DatabaseManager.create_connection()
    if connection:
        logging.info("Creating database and tables if they do not exist")
        DatabaseManager.create_database_if_not_exists(connection, db_name)
        connection.database = db_name  
        DatabaseManager.create_movies_table_if_not_exists(connection)
        connection.close()

    scraper = IMDbScraper(browser='edge')  # Change to 'edge' if using Edge
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

