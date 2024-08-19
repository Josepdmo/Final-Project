-- 1. Which genres are the most popular among the highest-rated books?

SELECT Genres.genre, AVG(Books.average_rating) AS avg_rating, COUNT(*) AS book_count
FROM Books
JOIN Book_Genres ON Books.book_id = Book_Genres.book_id
JOIN Genres ON Genres.genre_id = Book_Genres.genre_id
GROUP BY Genres.genre
HAVING AVG(Books.average_rating) > 4
ORDER BY avg_rating DESC;

-- 2. Which authors have the most books with high ratings?

SELECT author, count(author) as "Number of Books rated", avg(average_rating) as Average_Rating
from Authors join Books on Authors.author_id = Books.author_id
group by author
having count(author) > 10 and Average_Rating >= 4
order by Average_Rating desc;


-- 3. Which formats are the most in-demand (e.g., hardcover, paperback)?

Select book_format, count(book_format) 
from Formats
group by book_format
order by count(book_format) DESC;

-- 4. Which genres have the highest number of reviews?

SELECT Genres.genre, SUM(Books.num_reviews) AS sum_reviews
FROM Books
JOIN Book_Genres ON Books.book_id = Book_Genres.book_id
JOIN Genres ON Genres.genre_id = Book_Genres.genre_id
GROUP BY Genres.genre
ORDER BY sum_reviews DESC;

-- 5. Which books have the highest number of 5-star reviews?

SELECT book_title, author, num_ratings, average_rating, 5_star_reviews
FROM  Authors join Books on Authors.author_id = Books.author_id
join Ratings on Books.book_id = Ratings.book_id
where num_ratings > 1000
order by 5_star_reviews desc;

-- 6. Which books have high average ratings but a low number of reviews (less than 100)?

SELECT book_title, author, num_ratings, average_rating
FROM  Authors join Books on Authors.author_id = Books.author_id
where num_ratings < 100 and num_ratings > 30
order by average_rating DESC;



-- 

