from os import path
from configparser import ConfigParser
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask.cli import with_appcontext
import click
from datetime import datetime, timedelta
import base64
import codecs

config = ConfigParser()
config.read(path.join(path.dirname(__file__), 'config.ini'))
t = config['Database']

app = Flask(__name__)
uri = f"postgresql://{t['user']}:{t['password']}@{t['host']}:{t['port']}/{t['dbname']}"
app.config['SECRET_KEY'] = config['App']['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from schema import *

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.username.data).first()
        if user and user.pass_hash == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.username.data).first()
        if user:
            flash('Username already exists')
        else:
            new_user = User(
                user_name=form.username.data, 
                user_email=form.email.data,
                pass_hash=form.password.data, 
                wallet_cents=100000
            )
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully, please log in')

            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    books_pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    books = books_pagination.items

    for book in books:
        if book.cover and book.cover.image_content:
            book.cover_image = base64.b64encode(book.cover.image_content).decode('utf-8')
        else:
            book.cover_image = ''
        rating = Rating.query.filter_by(book_id=book.book_id).first()
        book.avg_rating = rating.avg_rating if rating else 'No rating'

    next_url = url_for('home', page=books_pagination.next_num) if books_pagination.has_next else None
    prev_url = url_for('home', page=books_pagination.prev_num) if books_pagination.has_prev else None

    return render_template(
        'home.html', 
        books=books, 
        books_pagination=books_pagination, 
        next_url=next_url, 
        prev_url=prev_url
    )

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    if book.cover and book.cover.image_content:
        book.cover_image = base64.b64encode(book.cover.image_content).decode('utf-8')
    else:
        book.cover_image = ''
    rating = Rating.query.filter_by(book_id=book.book_id).first()
    book.avg_rating = rating.avg_rating if rating else 'No rating'
    if request.method == 'POST':
        new_rating = request.form.get('rating')
        comment = request.form.get('comment')
        if new_rating and comment:
            review = Review(
                book_id=book_id,
                user_id=current_user.user_id,
                rating=int(rating),
                comment=comment
            )
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted!')
    book.reviews = sorted(book.reviews, key=lambda r: r.review_time, reverse=True)

    return render_template('book_detail.html', book=book)

@app.route('/add_review/<int:book_id>', methods=['POST'])
@login_required
def add_review(book_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    if not rating or not comment:
        flash('Rating and comment are required.')
        return redirect(url_for('book_detail', book_id=book_id))
    
    try:
        existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.user_id).first()
        
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            db.session.commit()
            flash('Review updated successfully.')
        else:
            new_review = Review(
                book_id=book_id,
                user_id=current_user.user_id,
                rating=rating,
                comment=comment
            )
            db.session.add(new_review)
            db.session.commit()
            flash('Review added successfully.')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')
    
    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/buy/<int:book_id>', methods=['POST'])
@login_required
def buy_book(book_id):
    book = Book.query.get_or_404(book_id)
    existing_entry = db.session.query(Ledger).filter_by(
        book_id=book_id, 
        user_id=current_user.user_id
    ).first()

    if existing_entry:
        flash('Book already bought')
    elif current_user.wallet_cents >= book.price_cents:
        current_user.wallet_cents -= book.price_cents

        max_loan_id = db.session.query(db.func.max(Ledger.loan_id)).scalar()
        new_loan_id = (max_loan_id or 0) + 1

        lend_date = datetime.now()
        expiry_date = lend_date + timedelta(days=30)

        ledger_entry = Ledger(
            loan_id=new_loan_id, 
            book_id=book_id, 
            user_id=current_user.user_id,
            start_date=lend_date,
            end_date=expiry_date
        )
        db.session.add(ledger_entry)
        db.session.commit()
        flash('Book purchased successfully')
    else:
        flash('Insufficient funds')
    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    book = Book.query.get_or_404(book_id)
    purchased = db.session.query(Ledger).filter_by(book_id=book_id, user_id=current_user.user_id).first()
    if not purchased:
        flash("You haven't purchased this book.")
        return redirect(url_for('profile'))
    
    book_content = BookContent.query.filter_by(book_id=book_id).first()
    if book_content and book_content.text_content:
        content = book_content.text_content
        content = content.replace('\\x', '')
        try:
            hex_content = bytes.fromhex(content)
            book_text_content = hex_content.decode('utf-8')
        except ValueError as e:
            book_text_content = f"Decoding error: {e}"
    else:
        book_text_content = "Content not available"
            

    return render_template('read_book.html', book=book, book_text_content=book_text_content)


@app.route('/browse_books', methods=['GET', 'POST'])
@login_required
def browse_books(): 
    if request.method == 'POST':
        search_query = request.form.get('search')
    else:
        search_query = request.args.get('search', '')
    
    page = request.args.get('page', 1, type=int)
    per_page_first_page = 10
    per_page_other_pages = 10

    query = Book.query

    if search_query:
        query = query.join(Author).outerjoin(BookTheme).outerjoin(Theme).outerjoin(Language).filter(
            db.or_(
                Book.title.ilike(f'%{search_query}%'),
                Author.author_name.ilike(f'%{search_query}%'),
                Theme.theme_name.ilike(f'%{search_query}%'),
                Language.lang_name.ilike(f'%{search_query}%')
            )
        )

    all_books = query.all()
    total_books = len(all_books)

    if page == 1:
        start_index = 0
        end_index = per_page_first_page
    else:
        start_index = per_page_first_page + (page - 2) * per_page_other_pages
        end_index = start_index + per_page_other_pages

    books = all_books[start_index:end_index]

    for book in books:
        if book.cover and book.cover.image_content:
            book.cover_image = base64.b64encode(book.cover.image_content).decode('utf-8')
        else:
            book.cover_image = ''
        rating = Rating.query.filter_by(book_id=book.book_id).first()
        book.avg_rating = rating.avg_rating if rating else 'No rating'

    next_url = url_for('browse_books', page=page + 1, search=search_query) if end_index < total_books else None
    prev_url = url_for('browse_books', page=page - 1, search=search_query) if page > 1 else None

    return render_template(
        'browse_books.html', 
        books=books, 
        total_books=total_books,
        current_page=page, 
        next_url=next_url, 
        prev_url=prev_url, 
        search_query=search_query,
        per_page_other_pages=per_page_other_pages
    )



user_bp = Blueprint('user', __name__)

@app.route('/profile')
@login_required
def profile():
    ledger_entries = db.session.query(Ledger).filter_by(user_id=current_user.user_id).all()
    books = Book.query.filter(Book.book_id.in_([entry.book_id for entry in ledger_entries])).all()
    books_dict = {book.book_id: book for book in books}
    
    return render_template(
        'profile.html', 
        ledger_entries=ledger_entries, 
        books_dict=books_dict
    )

@app.route('/remove_book/<int:book_id>', methods=['POST'])
@login_required
def remove_book(book_id):
    entry = db.session.query(Ledger).filter_by(BookID=book_id, UserID=current_user.UserID).first()
    
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash(f'Book has been removed from your profile')
    
    return redirect(url_for('user.profile'))



@app.cli.command("reset-db")
@with_appcontext
def reset_db():
    import datagen
    print('Dropping all tables.')
    db.drop_all()
    print('Creating new tables.')
    db.create_all()
    print('Generating 100 random users')
    datagen.generate_users(db.session, 100)
    print('Loading books from dump and generating reviews and loans for each')
    datagen.dump_to_db('dump.csv', db.session)

@app.cli.command("scrape-db")
@click.argument('n', type=int)
@with_appcontext
def scrape_db(n):
    print("Scraping books from https://www.gutenberg.org/ and saving to dump")
    print('User "reset-db" after, to load the dump into the database.')
    import datagen
    links = datagen.scrape_links(n)
    datagen.scrape_to_dump(links, 'dump.csv')

if __name__ == '__main__':
    app.run(debug=bool(config['Misc']['debug']))