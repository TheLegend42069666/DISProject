from app import db
from flask_login import UserMixin


class Author(db.Model):
    __tablename__ = 'authors'
    AuthorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    AuthorName = db.Column(db.String(255), nullable=False)

class Theme(db.Model):
    __tablename__ = 'themes'
    ThemeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ThemeName = db.Column(db.String(64))

class Language(db.Model):
    __tablename__ = 'languages'
    LangID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    LangName = db.Column(db.String(64))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(50), unique=True, nullable=False)
    UserEmail = db.Column(db.String(255), unique=True, nullable=False)
    PassHash = db.Column(db.String(255), nullable=False)
    WalletCents = db.Column(db.Integer, default=0, nullable=False)

    def get_id(self):
        return self.UserID

class Book(db.Model):
    __tablename__ = 'books'
    BookID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Title = db.Column(db.Text, nullable=False, index=True)
    Summary = db.Column(db.Text, index=True)
    LangID = db.Column(db.Integer, db.ForeignKey('languages.LangID'))
    AuthorID = db.Column(db.Integer, db.ForeignKey('authors.AuthorID'))
    PriceCents = db.Column(db.Integer, nullable=False)
    ReleaseDate = db.Column(db.Date)

    lang = db.relationship('Language', backref=db.backref('books', lazy=True))
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

class BookContent(db.Model):
    __tablename__ = 'bookcontents'
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID', ondelete='CASCADE'), primary_key=True)
    TextContent = db.Column(db.Text, nullable=False)

    book = db.relationship('Book', backref=db.backref('content', uselist=False, cascade='all, delete-orphan'))

class BookCover(db.Model):
    __tablename__ = 'bookcovers'
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID', ondelete='CASCADE'), primary_key=True)
    ImageContent = db.Column(db.LargeBinary, nullable=False)

    book = db.relationship('Book', backref=db.backref('cover', uselist=False, cascade='all, delete-orphan'))
    
class BookTheme(db.Model):
    __tablename__ = 'bookthemes'
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID', ondelete='CASCADE'), primary_key=True)
    ThemeID = db.Column(db.Integer, db.ForeignKey('themes.ThemeID'), primary_key=True)

    book = db.relationship('Book', backref=db.backref('bookthemes', lazy=True))
    theme = db.relationship('Theme', backref=db.backref('bookthemes', lazy=True))

    __table_args__ = (
        db.Index('idx_book_genres', 'BookID'),
        db.Index('idx_genre_books', 'ThemeID')
    )

class Ledger(db.Model):
    __tablename__ = 'ledger'
    LoanID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID', ondelete='CASCADE'))
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', ondelete='CASCADE'))
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('BookID', 'UserID', 'StartDate', name='unique_start'),
        db.UniqueConstraint('BookID', 'UserID', 'EndDate', name='unique_end'),
        db.Index('idx_loans', 'BookID', 'UserID')
    )

class Rating(db.Model):
    __tablename__ = 'ratings'
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID'), primary_key=True)
    AvgRating = db.Column(db.Numeric(3, 2))

class Review(db.Model):
    __tablename__ = 'reviews'
    BookID = db.Column(db.Integer, db.ForeignKey('books.BookID', ondelete='CASCADE'), primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID', ondelete='CASCADE'), primary_key=True)
    Rating = db.Column(db.Integer, nullable=False)
    Comment = db.Column(db.Text)
    ReviewTime = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    __table_args__ = (
        #db.CheckConstraint('Rating >= 0 AND Rating <= 5', name='check_rating'),
        db.Index('idx_book_ratings', 'BookID', 'Rating'),
        db.Index('idx_user_ratings', 'UserID', 'Rating')
    )


def new_or_get_author(session, author_name):
    author = session.query(Author).filter_by(AuthorName=author_name).first()
    if not author:
        author = Author(AuthorName=author_name)
        session.add(author)
    return author

def new_or_get_lang(session, lang_name):
    lang = session.query(Language).filter_by(LangName=lang_name).first()
    if not lang:
        lang = Language(LangName=lang_name)
        session.add(lang)
    return lang
    
def new_or_get_theme(session, theme_name):
    theme = session.query(Theme).filter_by(ThemeName=theme_name).first()
    if not theme:
        theme = Theme(ThemeName=theme_name)
        session.add(theme)
    return theme


def new_book(session, title, summary, lang_name, author_name, price_cents, release_date, cover, content, themes):
    with session.begin() and session.no_autoflush:
        book = Book(
            Title=title,
            Summary=summary,
            lang=new_or_get_lang(session, lang_name),
            author=new_or_get_author(session, author_name),
            PriceCents=price_cents,
            ReleaseDate=release_date
        )
        session.add(book)
        session.add(BookCover(
            book=book,
            ImageContent=cover
        ))
        session.add(BookContent(
            book=book,
            TextContent=content
        ))
        for theme in themes:
            session.add(BookTheme(
                book=book,
                theme=new_or_get_theme(session, theme)
            ))
    return book
