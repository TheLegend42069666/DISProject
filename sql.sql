CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    release_date DATE NOT NULL,
    cover_image VARCHAR(255) NOT NULL,
    price FLOAT NOT NULL
);

CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE written_by (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books (book_id),
    FOREIGN KEY (author_id) REFERENCES authors (author_id)
);

CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre VARCHAR(100) NOT NULL
);

CREATE TABLE what_genre (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books (book_id),
    FOREIGN KEY (genre_id) REFERENCES genres (genre_id)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    pass_hash VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    wallet FLOAT NOT NULL
);

CREATE TABLE ledger (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    loan_id INT,
    expiry_date DATE,
    lend_date DATE,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES book (book_id),
    FOREIGN KEY (genre_id) REFERENCES genres (genre_id)
);

CREATE TABLE admin (
    admin_id SERIAL PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    admin_id INT NOT NULL,
    type_id INT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES admin (admin_id),
    FOREIGN KEY (type_id) REFERENCES event_types (type_id)
);

CREATE TABLE event_types (
    type_id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL
);