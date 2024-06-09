from app import db
from flask_login import UserMixin


class Author(db.Model):
    __tablename__ = 'authors'
    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_name = db.Column(db.String(255), nullable=False)

class Theme(db.Model):
    __tablename__ = 'themes'
    theme_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    theme_name = db.Column(db.String(64))

class Language(db.Model):
    __tablename__ = 'languages'
    lang_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lang_name = db.Column(db.String(64))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_email = db.Column(db.String(255), unique=True, nullable=False)
    pass_hash = db.Column(db.String(255), nullable=False)
    wallet_cents = db.Column(db.Integer, default=0, nullable=False)

    def get_id(self):
        return self.UserID

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False, index=True)
    summary = db.Column(db.Text, index=True)
    lang_id = db.Column(db.Integer, db.ForeignKey('languages.lang_id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'))
    price_cents = db.Column(db.Integer, nullable=False)
    release_date = db.Column(db.Date)

    lang = db.relationship('Language', backref=db.backref('books', lazy=True))
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

class BookContent(db.Model):
    __tablename__ = 'bookcontents'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    text_content = db.Column(db.Text, nullable=False)

    book = db.relationship('Book', backref=db.backref('content', uselist=False, cascade='all, delete-orphan'))

class BookCover(db.Model):
    __tablename__ = 'bookcovers'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    image_content = db.Column(db.LargeBinary, nullable=False)

    book = db.relationship('Book', backref=db.backref('cover', uselist=False, cascade='all, delete-orphan'))
    
class BookTheme(db.Model):
    __tablename__ = 'bookthemes'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.theme_id'), primary_key=True)

    book = db.relationship('Book', backref=db.backref('bookthemes', lazy=True))
    theme = db.relationship('Theme', backref=db.backref('bookthemes', lazy=True))

    __table_args__ = (
        db.Index('idx_book_genres', 'book_id'),
        db.Index('idx_genre_books', 'theme_id')
    )

class Ledger(db.Model):
    __tablename__ = 'ledger'
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    book = db.relationship('Book', backref=db.backref('ledger', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('ledger', lazy=True, cascade='all, delete-orphan'))


    __table_args__ = (
        db.UniqueConstraint('book_id', 'user_id', 'start_date', name='unique_start'),
        db.UniqueConstraint('book_id', 'user_id', 'end_date', name='unique_end'),
        db.Index('idx_loans', 'book_id', 'user_id')
    )

class Rating(db.Model):
    __tablename__ = 'ratings'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True)
    avg_rating = db.Column(db.Numeric(3, 2))

    book = db.relationship('Book', backref=db.backref('rating', lazy=True))

class Review(db.Model):
    __tablename__ = 'reviews'
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    review_time = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    book = db.relationship('Book', backref=db.backref('reviews', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (
        db.CheckConstraint('rating >= 0 AND rating <= 5', name='check_rating'),
        db.Index('idx_book_ratings', 'book_id', 'rating'),
        db.Index('idx_user_ratings', 'user_id', 'rating')
    )
