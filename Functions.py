import pandas as pd
import ast
import Functions as fc
import pymysql
from sqlalchemy import create_engine
from sqlalchemy import text
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import os
from collections import defaultdict

def load_book_details():
    # Read the CSV file into a DataFrame
    df = pd.read_csv("Book_Details.csv")
    # Return the DataFrame
    return df



def create_subtables(df):
    """
    This function creates three subtables from the original DataFrame: 
    Books_df, Authors_df, and Formats_df. It selects necessary columns 
    for each table, assigns unique IDs where necessary, and links 
    authors and formats with the books.

    Args:
    df (DataFrame): The original DataFrame containing all the data.

    Returns:
    books_df (DataFrame): The Books table with linked author and format IDs.
    authors_df (DataFrame): The Authors table with unique author IDs.
    formats_df (DataFrame): The Formats table with unique format IDs.
    """
    
    # 1. Select the necessary columns for the Books table
    books_df = df[['book_id', 'book_title', 'book_details', 'publication_info', 
                   'num_ratings', 'num_reviews', 'average_rating', 
                   'rating_distribution', 'author', 'format']].copy()

    # 2. Create the Authors table
    authors_df = df[['author', 'authorlink']].drop_duplicates().reset_index(drop=True)
    authors_df['author_id'] = authors_df.index + 1

    # Link authors with books in the Books table
    books_df = pd.merge(books_df, authors_df[['author_id', 'author']], on='author', how='left').drop(columns=['author'])

    # 3. Create the Formats table
    formats_df = df[['format']].drop_duplicates().reset_index(drop=True)
    formats_df['format_id'] = formats_df.index + 1

    # Link formats with books in the Books table
    books_df = pd.merge(books_df, formats_df[['format_id', 'format']], on='format', how='left').drop(columns=['format'])

    return books_df, authors_df, formats_df

def format_format_table(formats_df):
    """
    This function processes the 'format' column in the formats_df DataFrame 
    by splitting it into two separate columns: 'num_pages' and 'book_format'.
    It also cleans and converts the 'num_pages' column to an integer type.

    Args:
    formats_df (DataFrame): The original DataFrame containing the 'format' column.

    Returns:
    formats_df (DataFrame): The cleaned DataFrame with separate 'num_pages' and 'book_format' columns.
    """
    
    # Split the 'format' column into two separate columns
    split_format = formats_df["format"].str.split(",", expand=True)

    # Clean up the number of pages column
    formats_df["num_pages"] = (
        split_format[0]
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("'", "", regex=False)
        .str.replace("pages", "", regex=False)
        .str.strip()
    )

    # Clean up the book format column
    formats_df["book_format"] = (
        split_format[1]
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("'", "", regex=False)
        .str.strip()
    )

    # Drop the original 'format' column as it's no longer needed
    formats_df = formats_df.drop(columns=["format"])

    # Convert 'num_pages' to numeric, handling non-numeric values
    formats_df["num_pages"] = pd.to_numeric(formats_df['num_pages'], errors='coerce')
    formats_df.dropna(subset="num_pages", inplace=True)

    # Convert 'num_pages' to string to manipulate characters
    formats_df['num_pages'] = formats_df['num_pages'].astype(str)

    # Remove the last digit '0' from 'num_pages' if it exists
    formats_df['num_pages'] = formats_df['num_pages'].apply(lambda x: x[:-1] if x.endswith('0') else x)

    # Remove any remaining non-numeric characters
    formats_df['num_pages'] = formats_df['num_pages'].str.replace(r'\D', '', regex=True)

    # Convert 'num_pages' back to int
    formats_df['num_pages'] = formats_df['num_pages'].astype(int)

    # Return the cleaned DataFrame
    return formats_df

def format_books_table(books_df, formats_df):
    """
    This function cleans the Books_df DataFrame by removing duplicates 
    and ensuring that all foreign keys (format_id) in Books_df are linked 
    to a valid primary key in Formats_df.

    Args:
    books_df (DataFrame): The original Books DataFrame containing book details.
    formats_df (DataFrame): The Formats DataFrame containing format information.

    Returns:
    books_df_cleaned (DataFrame): The cleaned Books DataFrame with valid foreign keys.
    """
    
    # Remove duplicates based on the 'book_id' column
    books_df.drop_duplicates(subset=['book_id'], keep='first', inplace=True)

    # Check for any format_id in books_df that is not in formats_df
    invalid_format_ids = books_df[~books_df['format_id'].isin(formats_df['format_id'])]

    # Display the rows in books_df with invalid format_id values, if any
    if not invalid_format_ids.empty:
        print("The following format_id values in books_df do not exist in formats_df:")
        print(invalid_format_ids[['format_id']].drop_duplicates())
    else:
        print("All format_id values in books_df are valid.")

    # Get the total number of invalid format_id rows
    total_invalid_format_ids = invalid_format_ids.shape[0]
    print(f"Total number of invalid format_id values in books_df: {total_invalid_format_ids}")

    # Keep only rows with valid format_id values in books_df
    books_df_cleaned = books_df[books_df['format_id'].isin(formats_df['format_id'])]

    return books_df_cleaned



def format_genres_table(df):
    """
    This function processes the 'genres' column in the original DataFrame to create a clean and 
    structured genres_df DataFrame. It removes duplicates, assigns unique genre IDs, and explodes 
    the list of genres into separate rows.

    Args:
    df (DataFrame): The original DataFrame containing the 'genres' column.

    Returns:
    genres_df (DataFrame): The cleaned and structured DataFrame with unique genre IDs.
    """
    
    # Create a genres DataFrame with unique genres
    genres_df = df[['genres']].drop_duplicates().reset_index(drop=True)
    
    # Assign a unique genre_id to each genre
    genres_df['genre_id'] = genres_df.index + 1
    
    # Explode the list of genres into separate rows
    genres_df = genres_df.explode('genres')
    
    # Remove brackets and clean up the genres
    genres_df['genres'] = genres_df['genres'].str.replace(r"[\[\]']", "", regex=True).str.strip()
    
    # Rename the 'genres' column to 'genre'
    genres_df.rename(columns={'genres': 'genre'}, inplace=True)
    
    return genres_df




def create_book_genres_table(df, genres_df):
    """
    This function creates the book_genres_df DataFrame, which links book IDs to genre IDs.
    It first renames the 'genres' column to 'genre', then merges this data with the genres_df
    to associate each book with its corresponding genre ID.

    Args:
    df (DataFrame): The original DataFrame containing book and genre information.
    genres_df (DataFrame): The cleaned and structured genres DataFrame with genre IDs.

    Returns:
    book_genres_df (DataFrame): The DataFrame linking book IDs to genre IDs.
    """
    
    # Rename the 'genres' column to 'genre' in the original DataFrame
    df.rename(columns={'genres': 'genre'}, inplace=True)
    
    # Create the book_genres DataFrame with book IDs and genres
    book_genres_df = df[['book_id', 'genre']].copy()
    
    # Merge with genres_df to link book IDs with genre IDs
    book_genres_df = pd.merge(book_genres_df, genres_df[['genre_id', 'genre']], on='genre', how='left').drop(columns=['genre'])
    
    return book_genres_df

def create_ratings_table(df):
    """
    This function creates and formats the Ratings table by extracting the number 
    of reviews for each star rating (1 to 5 stars) from the 'rating_distribution' 
    column in the original DataFrame.

    Args:
    df (DataFrame): The original DataFrame containing book and rating information.

    Returns:
    ratings_df (DataFrame): The formatted DataFrame with separate columns for each star rating.
    """
    
    # Create a DataFrame with book_id and rating_distribution
    ratings_df = df[['book_id', 'rating_distribution']].copy()
    
    # Function to extract star ratings from the rating_distribution string
    def extract_ratings(rating_dist):
        # Convert the string into a dictionary
        rating_dict = ast.literal_eval(rating_dist)
        
        # Extract values for each star rating, handling commas
        stars_5 = int(rating_dict.get('5', '0').replace(",", ""))
        stars_4 = int(rating_dict.get('4', '0').replace(",", ""))
        stars_3 = int(rating_dict.get('3', '0').replace(",", ""))
        stars_2 = int(rating_dict.get('2', '0').replace(",", ""))
        stars_1 = int(rating_dict.get('1', '0').replace(",", ""))
        
        return pd.Series([stars_5, stars_4, stars_3, stars_2, stars_1])
    
    # Apply the extraction function to the rating_distribution column
    ratings_df[['5_star_reviews', '4_star_reviews', '3_star_reviews', '2_star_reviews', '1_star_reviews']] = ratings_df['rating_distribution'].apply(extract_ratings)
    
    # Drop the original 'rating_distribution' column
    ratings_df = ratings_df.drop(columns=['rating_distribution'])
    
    return ratings_df


def create_db_engine():
    """
    This function retrieves the database connection string from an environment variable 
    and creates a SQLAlchemy engine for connecting to the database.

    Returns:
    engine (Engine): A SQLAlchemy engine connected to the database.
    """
    
    # Retrieve the connection string from environment variables
    connection_string = os.getenv("DB_CONNECTION_STRING")
    
    # Create a SQLAlchemy engine
    engine = create_engine(connection_string)
    
    return engine

def create_db_engine():
    """
    This function retrieves the database connection string from an environment variable 
    and creates a SQLAlchemy engine for connecting to the database.

    Returns:
    engine (Engine): A SQLAlchemy engine connected to the database.
    """
    load_dotenv()

    # Retrieve the connection string from environment variables
    connection_string = os.getenv("DB_CONNECTION_STRING")
    
    # Create a SQLAlchemy engine
    engine = create_engine(connection_string)
    
    return engine

def plot_top_10_books_5_stars(engine):
    """
    This function retrieves the top 10 books with the most 5-star reviews from the database,
    then creates a bar chart to display the results.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get books with more than 1000 ratings, ordered by 5-star reviews
    with engine.connect() as connection:
        query = text('''SELECT book_title, author, num_ratings, average_rating, 5_star_reviews
                        FROM Authors
                        JOIN Books ON Authors.author_id = Books.author_id
                        JOIN Ratings ON Books.book_id = Ratings.book_id
                        WHERE num_ratings > 1000
                        ORDER BY 5_star_reviews DESC;''')
        result1 = connection.execute(query)
    
    # Convert the result into a DataFrame
    highest_rated_books_5_stars = pd.DataFrame(result1)
    
    # Combine the book title and author into one string for easier labeling
    highest_rated_books_5_stars['book_author'] = highest_rated_books_5_stars['book_title'] + ' - ' + highest_rated_books_5_stars['author']
    
    # Select the top 10 books with the most 5-star reviews
    top_10_books_5_stars = highest_rated_books_5_stars.sort_values(by='5_star_reviews', ascending=False).head(10)
    
    # Plotting the data
    plt.figure(figsize=(12, 8))
    plt.barh(top_10_books_5_stars['book_author'], top_10_books_5_stars['5_star_reviews'], color='skyblue')
    
    # Adding titles and labels
    plt.xlabel('Number of 5-Star Reviews')
    plt.ylabel('Book Title - Author')
    plt.title('Top 10 Books with Most 5-Star Reviews')
    
    # Invert y-axis to have the book with the most 5-star reviews at the top
    plt.gca().invert_yaxis()
    
    # Display the plot
    plt.show()

def plot_top_10_highest_rated_books(engine):
    """
    This function retrieves books with a low number of reviews (between 30 and 100)
    and high average ratings, then plots the top 10 books.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get books with low reviews and high ratings
    with engine.connect() as connection:
        query = text('''SELECT book_title, author, num_ratings, average_rating
                        FROM Authors
                        JOIN Books ON Authors.author_id = Books.author_id
                        WHERE num_ratings < 100 AND num_ratings > 30
                        ORDER BY average_rating DESC;''')
        result2 = connection.execute(query)
    
    # Convert the result into a DataFrame
    high_rated_books_low_number_reviews = pd.DataFrame(result2)
    
    # Convert the average_rating column to numeric (float)
    high_rated_books_low_number_reviews['average_rating'] = pd.to_numeric(high_rated_books_low_number_reviews['average_rating'])
    
    # Sort by average rating in descending order and select the top 10
    top_10_books = high_rated_books_low_number_reviews.nlargest(10, 'average_rating')
    
    # Plotting the top 10 books
    plt.figure(figsize=(10, 6))
    sns.barplot(x='average_rating', y='book_title', data=top_10_books, palette='viridis')
    
    plt.title('Top 10 Books with Highest Average Rating (Low Number of Reviews)', fontsize=16)
    plt.xlabel('Average Rating', fontsize=14)
    plt.ylabel('Book Title', fontsize=14)
    plt.xlim(0, 5)  # Assuming ratings are out of 5
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.show()

def plot_top_10_best_authors(engine):
    """
    This function retrieves authors who have more than 10 books rated and an average rating of 4 or higher,
    then plots the top 10 authors.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get authors with more than 10 books rated and average rating >= 4
    with engine.connect() as connection:
        query = text('''SELECT author, count(author) as "Number of Books rated", avg(average_rating) as Average_Rating
                        FROM Authors
                        JOIN Books ON Authors.author_id = Books.author_id
                        GROUP BY author
                        HAVING count(author) > 10 AND avg(average_rating) >= 4
                        ORDER BY Average_Rating DESC;''')
        result3 = connection.execute(query)
    
    # Convert the result into a DataFrame
    best_authors = pd.DataFrame(result3)
    
    # Convert necessary columns to numeric types
    best_authors['Average_Rating'] = pd.to_numeric(best_authors['Average_Rating'])
    best_authors['Number of Books rated'] = pd.to_numeric(best_authors['Number of Books rated'])
    
    # Sort by Average Rating in descending order and select the top 10 authors
    top_10_authors = best_authors.sort_values(by="Average_Rating", ascending=False).head(10)
    
    # Plotting the top 10 best authors
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Average_Rating', y='author', data=top_10_authors, palette='plasma')
    
    plt.title('Top 10 Authors with More Than 10 Books Rated and Average Rating >= 4', fontsize=16)
    plt.xlabel('Average Rating', fontsize=14)
    plt.ylabel('Author', fontsize=14)
    plt.xlim(4, 5)  # Assuming ratings are out of 5
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.show()

def plot_most_in_demand_book_formats(engine):
    """
    This function retrieves the most in-demand book formats from the database
    and plots the data.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get the count of each book format
    with engine.connect() as connection:
        query = text('''SELECT book_format, count(book_format) 
                        FROM Formats
                        GROUP BY book_format
                        ORDER BY count(book_format) DESC;''')
        result4 = connection.execute(query)
    
    # Convert the result into a DataFrame
    best_formats = pd.DataFrame(result4)
    
    # Plotting the data
    plt.figure(figsize=(10, 6))  # Adjust the size of the figure if needed
    plt.barh(best_formats['book_format'], best_formats['count(book_format)'], color='skyblue')
    
    # Adding titles and labels
    plt.xlabel('Count')
    plt.ylabel('Book Format')
    plt.title('Most In-Demand Book Formats')
    
    # Invert y-axis to have the most popular formats at the top
    plt.gca().invert_yaxis()
    
    # Display the plot
    plt.show()

def plot_avg_rating_by_genre(engine):
    """
    This function retrieves genres with an average rating greater than 4, processes the data
    to calculate average ratings for individual genres, and plots the results. Only genres with
    500 or more occurrences are included in the final plot.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get genres with an average rating > 4
    with engine.connect() as connection:
        query = text('''SELECT Genres.genre, AVG(Books.average_rating) AS avg_rating, COUNT(*) AS book_count
                        FROM Books
                        JOIN Book_Genres ON Books.book_id = Book_Genres.book_id
                        JOIN Genres ON Genres.genre_id = Book_Genres.genre_id
                        GROUP BY Genres.genre
                        HAVING AVG(Books.average_rating) > 4
                        ORDER BY avg_rating DESC;''')
        result5 = connection.execute(query)
    
    # Convert the result into a DataFrame
    best_genres = pd.DataFrame(result5)
    
    # Initialize dictionaries to hold cumulative ratings and counts
    genre_ratings = defaultdict(float)
    genre_counts = defaultdict(int)
    
    # Process each row in the DataFrame
    for index, row in best_genres.iterrows():
        genres = row['genre'].split(', ')
        avg_rating = float(row['avg_rating'])  # Convert avg_rating to float
        
        for genre in genres:
            genre_ratings[genre] += avg_rating
            genre_counts[genre] += 1
    
    # Calculate the final average ratings for each genre
    final_avg_ratings = {genre: genre_ratings[genre] / genre_counts[genre] for genre in genre_ratings}
    
    # Convert the result to a DataFrame for better readability
    final_avg_ratings_df = pd.DataFrame({
        'Genre': list(final_avg_ratings.keys()),
        'Avg_Rating': list(final_avg_ratings.values()),
        'Count': list(genre_counts.values())  # Adding the count of occurrences for each genre
    })
    
    # Filter out genres with a count less than 500
    best_genres_clean = final_avg_ratings_df[final_avg_ratings_df['Count'] >= 500]
    
    # Sort the DataFrame by Avg_Rating in descending order
    best_genres_clean.sort_values(by="Avg_Rating", ascending=False, inplace=True)
    
    # Plotting the data
    plt.figure(figsize=(12, 8))  # Adjust the size of the figure if needed
    plt.barh(best_genres_clean['Genre'], best_genres_clean['Avg_Rating'], color='skyblue')
    
    # Set the x-axis limit to start at 4
    plt.xlim(4, best_genres_clean['Avg_Rating'].max() + 0.1)
    
    # Adding titles and labels
    plt.xlabel('Average Rating')
    plt.ylabel('Genre')
    plt.title('Average Rating by Genre')
    
    # Invert y-axis to have the highest-rated genres at the top
    plt.gca().invert_yaxis()
    
    # Display the plot
    plt.show()

def plot_top_10_genres_by_reviews(engine):
    """
    This function retrieves the total number of reviews for each genre from the database,
    processes the data to accumulate reviews for individual genres, and plots the top 10 genres.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get the sum of reviews for each genre
    with engine.connect() as connection:
        query = text('''SELECT Genres.genre, SUM(Books.num_reviews) AS sum_reviews
                        FROM Books
                        JOIN Book_Genres ON Books.book_id = Book_Genres.book_id
                        JOIN Genres ON Genres.genre_id = Book_Genres.genre_id
                        GROUP BY Genres.genre
                        ORDER BY sum_reviews DESC;''')
        result6 = connection.execute(query)
    
    # Convert the result into a DataFrame
    genres_most_reviews = pd.DataFrame(result6)
    
    # Initialize a dictionary to hold cumulative reviews per genre
    genre_reviews = defaultdict(int)
    
    # Process each row in the DataFrame
    for index, row in genres_most_reviews.iterrows():
        genres = row['genre'].split(', ')
        sum_reviews = row['sum_reviews']
        
        for genre in genres:
            genre_reviews[genre] += sum_reviews
    
    # Convert the result to a DataFrame for better readability
    final_genre_reviews_df = pd.DataFrame({
        'Genre': list(genre_reviews.keys()),
        'Total_Reviews': list(genre_reviews.values())
    })
    
    # Sort the DataFrame by Total Reviews in descending order
    final_genre_reviews_df.sort_values(by="Total_Reviews", ascending=False, inplace=True)
    
    # Filter the top 10 genres by total reviews
    top_10_genres = final_genre_reviews_df.head(10)
    
    # Plotting the data
    plt.figure(figsize=(12, 8))
    plt.barh(top_10_genres['Genre'], top_10_genres['Total_Reviews'], color='skyblue')
    
    # Adding titles and labels
    plt.xlabel('Total Reviews')
    plt.ylabel('Genre')
    plt.title('Top 10 Genres by Total Reviews')
    
    # Invert y-axis to have the genre with the most reviews at the top
    plt.gca().invert_yaxis()
    
    # Display the plot
    plt.show()

def plot_correlation_num_pages_avg_rating(engine):
    """
    This function retrieves the average rating by the number of pages from the database,
    calculates the correlation between the number of pages and average rating, and 
    plots a scatter plot to visualize the relationship.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get the average rating by the number of pages
    with engine.connect() as connection:
        query = text('''SELECT num_pages as "Number of Pages", avg(average_rating) as "Average Rating"
                        FROM Books
                        JOIN Formats ON Books.format_id = Formats.format_id
                        GROUP BY num_pages
                        ORDER BY "Average Rating" DESC;''')
        result7 = connection.execute(query)
    
    # Convert the result into a DataFrame
    num_pages_avg_rating = pd.DataFrame(result7)
    
    # Calculate the correlation between Number of Pages and Average Rating
    correlation = num_pages_avg_rating['Number of Pages'].corr(num_pages_avg_rating['Average Rating'])
    
    print(f"The correlation between Number of Pages and Average Rating is: {correlation:.4f}")
    
    # Create a scatter plot to visualize the correlation between Number of Pages and Average Rating
    plt.figure(figsize=(10, 6))
    plt.scatter(num_pages_avg_rating['Number of Pages'], num_pages_avg_rating['Average Rating'], alpha=0.5, color='green')
    plt.title('Correlation between Number of Pages and Average Rating')
    plt.xlabel('Number of Pages')
    plt.ylabel('Average Rating')
    plt.show()

def plot_top_10_books_by_avg_rating(engine):
    """
    This function retrieves the top 10 books with the highest average ratings (for books with more than 300 ratings)
    from the database and plots the data.

    Args:
    engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
    None
    """
    
    # Execute the SQL query to get the highest average rating books with more than 300 ratings
    with engine.connect() as connection:
        query = text('''SELECT book_title, average_rating
                        FROM Books
                        WHERE num_ratings > 300
                        ORDER BY average_rating DESC;''')
        result8 = connection.execute(query)
    
    # Convert the result into a DataFrame
    highest_avg_rating = pd.DataFrame(result8)
    
    # Select the top 10 books by average rating
    top_10_books = highest_avg_rating.head(10)
    
    # Plotting the data
    plt.figure(figsize=(12, 8))
    plt.barh(top_10_books['book_title'], top_10_books['average_rating'], color='skyblue')
    
    # Adding titles and labels
    plt.xlabel('Average Rating')
    plt.ylabel('Book Title')
    plt.title('Top 10 Books by Average Rating')
    
    # Set the x-axis limit to start at 4
    plt.xlim(4, top_10_books['average_rating'].max() + 0.1)
    
    # Invert y-axis to have the highest-rated books at the top
    plt.gca().invert_yaxis()
    
    # Display the plot
    plt.show()