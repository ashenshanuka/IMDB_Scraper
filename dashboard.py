import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import mysql.connector
import logging
from config import DB_CONFIG

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

class IMDbDashboard:
    def __init__(self):
        # Initialize Dash App with custom CSS
        self.app = dash.Dash(__name__, external_stylesheets=[
            'https://codepen.io/chriddyp/pen/bWLwgP.css'
        ])
        
        # Database Connection
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            logging.info("Database connection established successfully")
        except mysql.connector.Error as err:
            logging.error(f"Database connection error: {err}")
            raise
        
        # Setup Dashboard Layout
        self.setup_layout()

    def get_movies_dataframe(self):
        """Fetch and preprocess movies data from MySQL database"""
        try:
            query = """
            SELECT 
                movie_title, 
                release_year, 
                imdb_rating, 
                duration_minutes, 
                total_ratings
            FROM top_movies
            """
            df = pd.read_sql(query, self.connection)
            
            # Data Cleaning and Preprocessing
            df['total_ratings'] = pd.to_numeric(df['total_ratings'], errors='coerce').fillna(0)
            df['imdb_rating'] = pd.to_numeric(df['imdb_rating'], errors='coerce')
            df['duration_minutes'] = pd.to_numeric(df['duration_minutes'], errors='coerce')
            
            # Create Decade Column
            df['decade'] = (df['release_year'] // 10) * 10
            
            return df
        except Exception as e:
            logging.error(f"Error fetching dataframe: {e}")
            return pd.DataFrame()

    def create_visualizations(self, df):
        """Create all dashboard visualizations"""
        visualizations = {
            'rating_distribution': self.plot_rating_distribution(df),
            'year_wise_movies': self.plot_year_wise_movies(df),
            'avg_rating_decade': self.plot_average_rating_by_decade(df),
            'rating_vs_total_ratings': self.plot_rating_vs_total_ratings(df),
            'duration_trend': self.plot_duration_trend(df),
            'top_movies_decade': self.plot_top_movies_by_decade(df)
        }
        return visualizations

    def plot_rating_distribution(self, df):
        """Rating Distribution Histogram"""
        fig = px.histogram(
            df, 
            x='imdb_rating', 
            title='IMDb Rating Distribution',
            labels={'imdb_rating': 'IMDb Rating'},
            color_discrete_sequence=['blue'],
            marginal='box'  # Add box plot
        )
        return fig

    def plot_year_wise_movies(self, df):
        """Movies Count by Release Year"""
        year_counts = df['release_year'].value_counts().sort_index()
        fig = px.bar(
            x=year_counts.index, 
            y=year_counts.values,
            title='Number of Top Movies by Release Year',
            labels={'x': 'Release Year', 'y': 'Number of Movies'},
            color_discrete_sequence=['green']
        )
        return fig

    def plot_average_rating_by_decade(self, df):
        """Average Rating by Decade"""
        avg_rating_by_decade = df.groupby('decade')['imdb_rating'].mean()
        fig = px.bar(
            x=avg_rating_by_decade.index, 
            y=avg_rating_by_decade.values,
            title='Average IMDb Rating by Decade',
            labels={'x': 'Decade', 'y': 'Average Rating'},
            color_discrete_sequence=['purple']
        )
        return fig

    def plot_rating_vs_total_ratings(self, df):
        """Scatter Plot: Rating vs Total Ratings"""
        fig = px.scatter(
            df,
            x='total_ratings',
            y='imdb_rating',
            title='IMDb Rating vs Total Ratings',
            labels={'total_ratings': 'Total Ratings', 'imdb_rating': 'IMDb Rating'},
            hover_data=['movie_title', 'release_year'],
            size='total_ratings',
            color='imdb_rating',
            color_continuous_scale='viridis'
        )
        return fig

    def plot_duration_trend(self, df):
        """Movie Duration Trend by Year"""
        avg_duration = df.groupby('release_year')['duration_minutes'].mean()
        fig = px.line(
            x=avg_duration.index, 
            y=avg_duration.values,
            title='Average Movie Duration Trend',
            labels={'x': 'Release Year', 'y': 'Average Duration (minutes)'},
            line_shape='spline'
        )
        return fig

    def plot_top_movies_by_decade(self, df):
        """Top 5 Movies by Decade"""
        top_movies = df.groupby('decade').apply(
            lambda x: x.nlargest(5, 'imdb_rating')
        ).reset_index(drop=True)
        
        fig = px.bar(
            top_movies, 
            x='decade', 
            y='imdb_rating',
            color='movie_title',
            title='Top Rated Movies by Decade',
            labels={'decade': 'Decade', 'imdb_rating': 'IMDb Rating'}
        )
        return fig

    def setup_layout(self):
        """Create Dashboard Layout"""
        self.app.layout = html.Div([
            # Title
            html.H1('IMDb Top 250 Movies Analytics Dashboard', 
                    style={'textAlign': 'center', 'color': '#1E90FF'}),
            
            # Dropdown for Year Filter
            html.Div([
                html.Label('Filter by Decade:'),
                dcc.Dropdown(
                    id='decade-filter',
                    options=[
                        {'label': f'{decade}s', 'value': decade} 
                        for decade in range(1920, 2030, 10)
                    ],
                    placeholder='Select a Decade'
                )
            ], style={'width': '50%', 'margin': 'auto'}),
            
            # Visualization Rows
            html.Div([
                html.Div([
                    html.H3('Rating Distribution'),
                    dcc.Graph(id='rating-distribution')
                ], className='six columns'),
                
                html.Div([
                    html.H3('Movies by Release Year'),
                    dcc.Graph(id='year-wise-movies')
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                html.Div([
                    html.H3('Average Rating by Decade'),
                    dcc.Graph(id='avg-rating-decade')
                ], className='six columns'),
                
                html.Div([
                    html.H3('Rating vs Total Ratings'),
                    dcc.Graph(id='rating-vs-total-ratings')
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                html.Div([
                    html.H3('Movie Duration Trend'),
                    dcc.Graph(id='duration-trend')
                ], className='six columns'),
                
                html.Div([
                    html.H3('Top Movies by Decade'),
                    dcc.Graph(id='top-movies-decade')
                ], className='six columns')
            ], className='row'),
            
            # Data Table
            html.Div([
                html.H3('Top Movies Data'),
                dash_table.DataTable(
                    id='movie-data-table',
                    columns=[
                        {'name': col, 'id': col} 
                        for col in ['movie_title', 'release_year', 'imdb_rating', 'duration_minutes']
                    ],
                    page_size=10,
                    style_table={'overflowX': 'auto'}
                )
            ])
        ])

        # Setup Callbacks
        self.setup_callbacks()

    def setup_callbacks(self):
        """Create Dash Callbacks for Dynamic Updates"""
        @self.app.callback(
            [
                Output('rating-distribution', 'figure'),
                Output('year-wise-movies', 'figure'),
                Output('avg-rating-decade', 'figure'),
                Output('rating-vs-total-ratings', 'figure'),
                Output('duration-trend', 'figure'),
                Output('top-movies-decade', 'figure'),
                Output('movie-data-table', 'data')
            ],
            [Input('decade-filter', 'value')]
        )
        def update_graphs(selected_decade):
            """Update All Graphs based on Decade Filter"""
            df = self.get_movies_dataframe()
            
            # Apply decade filter if selected
            if selected_decade is not None:
                df = df[df['decade'] == selected_decade]
            
            # Create visualizations
            visualizations = self.create_visualizations(df)
            
            # Prepare data table
            table_data = df.to_dict('records')
            
            return (
                visualizations['rating_distribution'],
                visualizations['year_wise_movies'],
                visualizations['avg_rating_decade'],
                visualizations['rating_vs_total_ratings'],
                visualizations['duration_trend'],
                visualizations['top_movies_decade'],
                table_data
            )

    def run(self, debug=True, port=8050):
        """Run Dash Application"""
        try:
            self.app.run_server(debug=debug, port=port)
        except Exception as e:
            logging.error(f"Dashboard run error: {e}")

def main():
    try:
        dashboard = IMDbDashboard()
        dashboard.run()
    except Exception as e:
        logging.error(f"Application startup error: {e}")

if __name__ == '__main__':
    main()