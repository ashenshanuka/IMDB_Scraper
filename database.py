import mysql.connector
from config import DB_CONFIG
import logging

class DatabaseManager:
    @staticmethod
    def create_connection():
        """
        Establish MySQL database connection
        
        :return: Database connection or None
        """
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except mysql.connector.Error as error:
            logging.error(f"Database connection error: {error}")
            return None

    @staticmethod
    def create_movies_table(connection):
        """
        Create or reset movies table
        
        :param connection: MySQL database connection
        """
        cursor = connection.cursor()
        
        try:
            # Drop existing table if it exists
            cursor.execute("DROP TABLE IF EXISTS top_movies")
            
            # Create new table with comprehensive schema
            create_table_query = """
            CREATE TABLE top_movies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                movie_rank INT NOT NULL,
                movie_title VARCHAR(255) NOT NULL,
                release_year INT,
                duration_minutes INT,
                imdb_rating DECIMAL(3,1),
                total_ratings INT
            )
            """
            
            cursor.execute(create_table_query)
            connection.commit()
            logging.info("Movies table created successfully")
        
        except mysql.connector.Error as error:
            logging.error(f"Error creating movies table: {error}")
        finally:
            cursor.close()

    @staticmethod
    def insert_movies(connection, movies_data):
        """
        Insert movies data into the database
        
        :param connection: MySQL database connection
        :param movies_data: List of movie tuples to insert
        """
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO top_movies 
        (movie_rank, movie_title, release_year, duration_minutes, imdb_rating, total_ratings) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            cursor.executemany(insert_query, movies_data)
            connection.commit()
            logging.info(f"Successfully inserted {cursor.rowcount} movies")
        
        except mysql.connector.Error as error:
            logging.error(f"Failed to insert movies: {error}")
            connection.rollback()
        
        finally:
            cursor.close()