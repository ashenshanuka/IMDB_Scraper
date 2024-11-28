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
            connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            logging.info("Successfully connected to MySQL server")
            return connection
        except mysql.connector.Error as error:
            logging.error(f"Database connection error: {error}")
            return None

    @staticmethod
    def create_database_if_not_exists(connection, db_name):
        """
        Create database if it does not exist
        
        :param connection: MySQL database connection
        :param db_name: Name of the database to create
        """
        logging.info(f"Checking/creating database '{db_name}'")
        cursor = connection.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            logging.info(f"Database '{db_name}' checked/created successfully")
        except mysql.connector.Error as error:
            logging.error(f"Error creating database '{db_name}': {error}")
        finally:
            cursor.close()

    @staticmethod
    def create_movies_table_if_not_exists(connection):
        """
        Create movies table if it does not exist
        
        :param connection: MySQL database connection
        """
        cursor = connection.cursor()
        try:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS top_movies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                movie_rank INT NOT NULL,
                movie_title VARCHAR(255) NOT NULL,
                release_year INT,
                duration_minutes INT,
                imdb_rating DECIMAL(3,1),
                total_ratings INT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                status INT DEFAULT 1
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            logging.info("Movies table checked/created successfully")
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