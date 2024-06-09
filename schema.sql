START TRANSACTION;

DROP TABLE IF EXISTS Books CASCADE;
DROP TABLE IF EXISTS BookContents;
DROP TABLE IF EXISTS BookCovers;
DROP TABLE IF EXISTS BookThemes;
DROP INDEX IF EXISTS idx_book_genres;
DROP INDEX IF EXISTS idx_genre_books;
DROP INDEX IF EXISTS idx_title;
DROP INDEX IF EXISTS idx_summary;

DROP TABLE IF EXISTS Ledger;
DROP INDEX IF EXISTS idx_loans;

DROP TABLE IF EXISTS Authors;
DROP TABLE IF EXISTS Themes;
DROP TABLE IF EXISTS Languages;

DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Ratings;
DROP INDEX IF EXISTS idx_book_ratings;
DROP INDEX IF EXISTS idx_user_ratings;

COMMIT;



START TRANSACTION;

CREATE TABLE IF NOT EXISTS Authors(
	author_id serial PRIMARY KEY,
	author_name varchar(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS Themes(
	theme_id serial PRIMARY KEY,
	theme_name varchar(64)
);
CREATE TABLE IF NOT EXISTS Languages(
	lang_id serial PRIMARY KEY,
	lang_name varchar(64)
);

CREATE TABLE IF NOT EXISTS Users(
	user_id serial PRIMARY KEY,
	user_name varchar(50) UNIQUE NOT NULL,
	user_email varchar(255) UNIQUE NOT NULL,
	pass_hash varchar(255) NOT NULL,
	wallet_cents int DEFAULT 0 NOT NULL
);


CREATE TABLE IF NOT EXISTS Books(
	book_id serial PRIMARY KEY,	
	title text NOT NULL,
	summary text,
	lang_id serial REFERENCES Languages(lang_id),
	author_id serial REFERENCES Authors(author_id),
	price_cents int NOT NULL,
	release_date date
);
CREATE TABLE IF NOT EXISTS BookContents(
	book_id serial PRIMARY KEY,
	text_content text NOT NULL,
	FOREIGN KEY(book_id) REFERENCES Books(book_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS BookCovers(
	book_id serial PRIMARY KEY,
	image_content bytea NOT NULL,
	FOREIGN KEY(book_id) REFERENCES Books(book_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS BookThemes(
	book_id serial REFERENCES Books(book_id) ON DELETE CASCADE,
	theme_id serial REFERENCES Themes(theme_id),
	PRIMARY KEY(book_id, theme_id)
);
CREATE INDEX idx_book_genres ON BookThemes(book_id);
CREATE INDEX idx_genre_books ON BookThemes(theme_id);
CREATE INDEX idx_title ON Books(title);
CREATE INDEX idx_summary ON Books(summary);


CREATE TABLE Ledger(
	loan_id serial PRIMARY KEY,
	book_id serial REFERENCES Books(book_id) ON DELETE CASCADE,
	user_id serial REFERENCES Users(user_id) ON DELETE CASCADE,
	start_date date NOT NULL,
	end_date date NOT NULL,
	CONSTRAINT unique_start UNIQUE(book_id, user_id, start_date),
	CONSTRAINT unique_end UNIQUE(book_id, user_id, end_date)
);
CREATE INDEX idx_loans ON Ledger(book_id, user_id);


CREATE TABLE IF NOT EXISTS Reviews(
	book_id serial REFERENCES Books(book_id),
	user_id serial REFERENCES Users(user_id),
	rating int NOT NULL CHECK (rating >= 0 AND rating <= 5),
	comment text,
	review_time timestamp DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(book_id, user_id)
);
CREATE INDEX idx_book_ratings ON Reviews(book_id, rating);
CREATE INDEX idx_user_ratings ON Reviews(user_id, rating);
CREATE TABLE IF NOT EXISTS Ratings (
    book_id serial PRIMARY KEY REFERENCES Books(book_id),
    avg_rating NUMERIC(3, 2)
);

COMMIT;
