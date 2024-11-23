import mysql.connector
from config import DB_CONFIG

def create_connection():
    """Establish MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as error:
        print(f"Database connection error: {error}")
        return None

def create_table(connection):
    """Create movies table with appropriate schema"""
    cursor = connection.cursor()
    
    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS top_movies")
    
    # Create new table with descriptive column names
    create_table_query = """
    CREATE TABLE top_movies (
        movie_id INT AUTO_INCREMENT PRIMARY KEY,
        movie_title VARCHAR(255) NOT NULL,
        release_year INT,
        rating DECIMAL(3,1),
        total_ratings INT
    )
    """
    
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()

def insert_movies(connection, movies_data):
    """Insert scraped movie data into database"""
    cursor = connection.cursor()
    
    insert_query = """
    INSERT INTO top_movies 
    (movie_title, release_year, rating, total_ratings) 
    VALUES (%s, %s, %s, %s)
    """
    
    cursor.executemany(insert_query, movies_data)
    connection.commit()
    cursor.close()