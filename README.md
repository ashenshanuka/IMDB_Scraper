# IMDb Top 250 Movies Web Scraper  

## Project Overview  
A Python-based web scraper that extracts the top 250 movies from IMDb and stores them in a MySQL database.

---

## Project Structure  
```
imdb-movies-scraper/  
│  
├── config.py          # Database and scraper configurations  
├── database.py        # Database management functions  
├── scraper.py         # Main scraping logic  
├── utils.py           # Utility functions for data parsing  
├── requirements.txt   # Python package dependencies  
└── README.md          # Project documentation  
```

---

## Prerequisites  
1. Python 3.8+  
2. MySQL Server  
3. Git  
4. pip (Python package manager)

---

## Steps to Set Up and Run  

### 1. Clone the Repository  
```bash  
# Clone the repository  
git clone https://github.com/your-username/imdb-movies-scraper.git  

# Navigate to the project directory  
cd imdb-movies-scraper  
```

### 2. Create a Virtual Environment  
```bash  
# Create a virtual environment  
python -m venv venv  

# Activate the virtual environment  
# On Windows  
venv\Scripts\activate  

# On macOS/Linux  
source venv/bin/activate  
```

### 3. Install Dependencies  
```bash  
# Install required Python packages  
pip install -r requirements.txt  
```

### 4. Set Up the MySQL Database  
1. **Launch MySQL Command Line or Workbench**.  
2. **Run the following commands** to create the database:  
   ```sql  
   -- Create the database  
   CREATE DATABASE imdb_movies;  

   -- Use the database  
   USE imdb_movies;  

   -- Verify the database creation  
   SHOW DATABASES;  
   ```  

3. **Edit the `config.py` file** with your MySQL credentials:  
   ```python  
   DB_CONFIG = {  
       'host': 'localhost',  
       'user': 'root',        # Replace with your MySQL username  
       'password': '1234',    # Replace with your MySQL password  
       'database': 'imdb_movies'  
   }  
   ```

### 5. Run the Web Scraper  
```bash  
# Run the scraper script  
python scraper.py  
```

### 6. Verify the Results in MySQL  
1. **Connect to MySQL**:  
   ```bash  
   mysql -u root -p  
   ```  

2. **Run the following commands to check the scraped data**:  
   ```sql  
   -- Use the database  
   USE imdb_movies;  

   -- Check table creation  
   SHOW TABLES;  

   -- View a sample of the scraped movies  
   SELECT * FROM top_movies LIMIT 10;  

   -- Count the total number of movies  
   SELECT COUNT(*) FROM top_movies;  
   ```

---

## Notes  
- Ensure MySQL Server is running during the setup and scraping process.  
- If errors occur, refer to the logs in `scraper.py` or database configuration in `config.py`. 