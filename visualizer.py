import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from config import DB_CONFIG 

class DataVisualizer:
    def __init__(self):
        self.connection = mysql.connector.connect(**DB_CONFIG)

    def get_movies_dataframe(self):
        """Fetch movies data from MySQL database"""
        query = """
        SELECT 
            movie_title, 
            release_year, 
            imdb_rating, 
            duration_minutes, 
            total_ratings
        FROM top_movies
        """
        return pd.read_sql(query, self.connection)

    def plot_movie_genre_distribution(self, df):
        """Pie chart of movie genres"""
        # Note: You'll need to add genre extraction logic
        genre_counts = df['movie_genre'].value_counts()
        fig = px.pie(
            names=genre_counts.index,
            values=genre_counts.values,
            title='Movie Genre Distribution',
            labels={'value': 'Number of Movies', 'names': 'Genre'}
        )
        return fig

    def plot_average_rating_by_year(self, df):
        """Average IMDb Rating by Release Year"""
        average_ratings = df.groupby('release_year')['imdb_rating'].mean()
        fig = px.bar(
            x=average_ratings.index,
            y=average_ratings.values,
            title='Average IMDb Rating by Release Year',
            labels={'x': 'Release Year', 'y': 'Average IMDb Rating'}
        )
        return fig

    def plot_average_duration_by_year(self):
        """Average Movie Duration by Release Year"""
        df = self.get_movies_dataframe()
        avg_duration = df.groupby('release_year')['duration_minutes'].mean()
        
        fig = px.line(
            x=avg_duration.index, 
            y=avg_duration.values,
            title='Average Movie Duration Trend',
            labels={'x': 'Release Year', 'y': 'Average Duration (minutes)'}
        )
        return fig

    def plot_rating_vs_total_ratings(self):
        """Scatter plot of IMDb Rating vs Total Ratings"""
        df = self.get_movies_dataframe()
        fig = px.scatter(
            df,
            x='total_ratings',
            y='imdb_rating',
            title='IMDb Rating vs Total Ratings',
            labels={'total_ratings': 'Total Ratings', 'imdb_rating': 'IMDb Rating'},
            hover_data=['movie_title']
        )
        return fig

    def plot_top_movies_by_decade(self):
        """Top Movies by Decade"""
        df = self.get_movies_dataframe()
        
        # Create decade column
        df['decade'] = (df['release_year'] // 10) * 10
        
        # Top movies per decade
        top_movies_by_decade = df.groupby('decade').apply(
            lambda x: x.nlargest(5, 'imdb_rating')
        ).reset_index(drop=True)
        
        fig = px.bar(
            top_movies_by_decade, 
            x='decade', 
            y='imdb_rating',
            color='movie_title',
            title='Top Rated Movies by Decade',
            labels={'decade': 'Decade', 'imdb_rating': 'IMDb Rating'}
        )
        return fig