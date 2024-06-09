from schema import *
from sqlalchemy import func, select
from datetime import datetime


def new_or_get_author(session, author_name):
    author = session.query(Author).filter_by(author_name=author_name).first()
    if not author:
        author = Author(author_name=author_name)
        session.add(author)
    return author

def new_or_get_lang(session, lang_name):
    lang = session.query(Language).filter_by(lang_name=lang_name).first()
    if not lang:
        lang = Language(lang_name=lang_name)
        session.add(lang)
    return lang
    
def new_or_get_theme(session, theme_name):
    theme = session.query(Theme).filter_by(theme_name=theme_name).first()
    if not theme:
        theme = Theme(theme_name=theme_name)
        session.add(theme)
    return theme

def new_book(session, title, summary, lang_name, author_name, price_cents, release_date, cover, content, themes):
    with session.begin() and session.no_autoflush:
        book = Book(
            title=title,
            summary=summary,
            lang=new_or_get_lang(session, lang_name),
            author=new_or_get_author(session, author_name),
            price_cents=price_cents,
            release_date=release_date
        )
        session.add(book)
        session.add(BookCover(
            book=book,
            image_content=cover
        ))
        session.add(BookContent(
            book=book,
            text_content=content
        ))
        for theme in themes:
            session.add(BookTheme(
                book=book,
                theme=new_or_get_theme(session, theme)
            ))
        session.add(Rating(
            book=book,
            avg_rating=None
        ))
    return book

def new_user(session, username, passhash, email, wallet):
    session.add(User(
        user_name=username,
        user_email=email,
        pass_hash=passhash,
        wallet_cents=wallet,
    ))

def new_review(session, book, user, rating, comment, time):
    session.add(Review(
        book=book,
        user=user,
        rating=rating,
        comment=comment,
        review_time=time,
    ))

def new_loan(session, book, user, start, end):
    session.add(Ledger(
        book=book,
        user=user,
        start_date=start,
        end_date=end,
    ))

def get_loans(session, user):
    return (
        session.query(Ledger, Book)
        .filter(Ledger.user_id == user.user_id)
        .join(Book, Ledger.book_id == Book.book_id)
    )

def update_rating(session, book):
    ratings_query = (
        session.query(Review.book_id, func.avg(Review.rating))
        .filter(Review.book_id == book.book_id)
        .group_by(Review.book_id)
        .first()
    )
    if ratings_query:
        avg_rating = ratings_query[1]
        rating = session.query(Rating).filter_by(book_id=book.book_id).first()
        if rating:
            rating.avg_rating = avg_rating

def update_ledger(session):
    now = datetime.now()
    session.query(Ledger).filter(Ledger.end_date < now).delete()

def get_random_users(session, n):
    return session.query(User).order_by(func.random()).limit(n).all()
