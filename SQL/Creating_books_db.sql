CREATE DATABASE Books;

USE Books

CREATE TABLE Authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author VARCHAR(255) NOT NULL,
    authorlink VARCHAR(255)
);

CREATE TABLE Formats (
    format_id INT AUTO_INCREMENT PRIMARY KEY,
    num_pages INT NOT NULL,
    book_format VARCHAR(255) NOT NULL
);

CREATE TABLE Genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre VARCHAR(255) NOT NULL
    
);

CREATE TABLE Books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    book_title VARCHAR(255) NOT NULL,
    book_details TEXT,
    publication_info VARCHAR(255),
    num_ratings INT,
    num_reviews INT,
    average_rating DECIMAL(3,2),
    author_id INT,
    format_id INT,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id),
    FOREIGN KEY (format_id) REFERENCES Formats(format_id)
);





CREATE TABLE Book_Genres (
    book_id INT,
    genre_id INT,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

CREATE TABLE Ratings (
    book_id INT PRIMARY KEY,
    5_star_reviews INT, 
    4_star_reviews INT,
    3_star_reviews INT,
    2_star_reviews INT,
    1_star_reviews INT,
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);



