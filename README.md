## 📚 Project Description -- Welcome to my Library!

Welcome to the Goodreads Data Analysis Project! 📊 This project focuses on analyzing a comprehensive dataset from the Goodreads platform, which contains detailed information about books, including their authors, the number of reviews, average ratings, and more. 🌟

The objective is to deconstruct this extensive table, organizing it into multiple related tables to create a well-structured relational database in MySQL. 🗄️ By doing so, we can better manage and analyze the data.

Once the database is set up, the next step is to use this data for a business analysis. The goal is to develop a hypothetical business plan for a bookstore 🏬. By analyzing genre popularity, review counts, and average ratings, we aim to determine the best books to stock to maximize the bookstore's success. 📈

This project combines data analysis, database management, and strategic planning to provide valuable insights for a potential bookstore. 📖✨


## 🛠️ Creating the Database

This project began with a rich dataset sourced from [Kaggle](https://www.kaggle.com/datasets/dk123891/books-dataset-goodreadsmay-2024), which provided comprehensive information on books, authors, and reviews from Goodreads. Using Python, I meticulously broke down this extensive dataset into a well-organized relational database, consisting of six interrelated tables.

The tables and their respective columns are as follows:

1. **Authors** 📚
   - `author_id`: A unique identifier for each author.
   - `author`: The name of the author.
   - `authorlink`: The Goodreads link for the author.

2. **Books** 📖
   - `book_id`: A unique identifier for each book.
   - `book_title`: The title of the book.
   - `book_details`: Additional details about the book.
   - `publication_info`: Information about when the book was published.
   - `num_ratings`: The number of ratings the book has received.
   - `num_reviews`: The number of reviews the book has received.
   - `average_rating`: The average rating of the book.
   - `author_id`: A foreign key linking to the `Authors` table.
   - `format_id`: A foreign key linking to the `Formats` table.

3. **Formats** 📑
   - `format_id`: A unique identifier for each format.
   - `num_pages`: The number of pages in the book.
   - `book_format`: The format of the book (e.g., paperback, digital).

4. **Genres** 🎭
   - `genre_id`: A unique identifier for each genre combination.
   - `genre`: The genre or combination of genres associated with a book.

5. **Ratings** ⭐
   - `book_id`: A unique identifier for each book, linking to the `Books` table.
   - `5_star_reviews`: The total number of 5-star reviews.
   - `4_star_reviews`: The total number of 4-star reviews.
   - `3_star_reviews`: The total number of 3-star reviews.
   - `2_star_reviews`: The total number of 2-star reviews.
   - `1_star_reviews`: The total number of 1-star reviews.

6. **Book_Genres** 📚🎭
   - `book_id`: A foreign key linking to the `Books` table.
   - `genre_id`: A foreign key linking to the `Genres` table.

These tables are interconnected, forming the backbone of a relational database that efficiently organizes the data for further analysis. This structure allows for in-depth exploration of book trends, author popularity, and genre performance, all of which are crucial for the subsequent business analysis.

## 📊 Data Analysis Using SQL

In this step, the focus was on conducting data analysis to gain insights that would help in making informed decisions for the bookstore. The following questions were considered crucial for understanding the market and selecting the right books for the store:

### 🔍 Key Questions and Their Importance

1. **Which books have the highest number of 5-star reviews?**
   - **Importance:** Books with a high number of 5-star reviews are likely to be well-loved by readers. Stocking these books ensures that the bookstore offers popular, high-quality titles that are more likely to attract and satisfy customers.

2. **Which books have high average ratings but a low number of reviews (less than 100)?**
   - **Importance:** Identifying books with high average ratings but fewer reviews can uncover hidden gems. These books, although not widely known, have strong potential and could appeal to discerning readers looking for quality literature that is not mainstream.

3. **Which authors (with more than 10 books) have the highest average ratings?**
   - **Importance:** Authors who consistently receive high ratings across multiple books are likely to have a dedicated following. Featuring these authors prominently in the bookstore can attract loyal customers and ensure a reliable stream of high-quality content.

4. **Which formats are the most in-demand (e.g., hardcover, paperback)?**
   - **Importance:** Understanding the preferred book formats helps in optimizing inventory. For example, if paperback books are more popular, focusing on increasing the stock of this format can lead to better sales and higher customer satisfaction.

5. **Which genres are the most popular among the highest-rated books?**
   - **Importance:** Knowing which genres are most popular among highly-rated books helps in curating a selection that aligns with readers' preferences. This insight ensures that the bookstore offers genres that are in demand and have a proven track record of high quality.

6. **Which genres have the highest number of reviews?**
   - **Importance:** Genres with the highest number of reviews indicate strong reader engagement. Stocking books in these genres can cater to a broad audience and ensure that the bookstore meets the demands of active readers.

7. **Do the number of pages correlate with the average rating of the book?**
   - **Importance:** Understanding if there is a correlation between the length of a book and its average rating can help in curating a balanced selection. For instance, if longer books tend to receive higher ratings, the bookstore might prioritize stocking more comprehensive works.

8. **Which books have the highest average rating?**
   - **Importance:** Books with the highest average ratings are likely to be universally appreciated for their quality. Featuring these books prominently in the store ensures that the bookstore offers the best of the best, attracting customers who seek highly rated literature.


