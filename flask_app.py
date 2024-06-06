from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
import json
from datetime import datetime, timedelta
import re


app = Flask(__name__)

# Configure the PostgreSQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:42069@localhost/ebook_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bruh'

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Authors(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Author: {self.name}>'

written_by = db.Table('written_by',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id'), primary_key=True)
)

class Genres(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Genre: {self.genre}>'


what_genre = db.Table('what_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True)
)

class Books(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    cover_image = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    authors = db.relationship('Authors', secondary=written_by,
                              primaryjoin="Books.book_id == written_by.c.book_id",
                              secondaryjoin="Authors.author_id == written_by.c.author_id",
                              backref=db.backref('books', lazy=True))
    genres = db.relationship('Genres', secondary=what_genre, backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f'<Book: {self.title}>'
    
    def get_description(self):
        sentences = re.split(r'(?<=[.!?]) +', self.content)
        description = ""
        word_count = 0
        for sentence in sentences:
            words = sentence.split()
            word_count += len(words)
            description += sentence + " "
            if word_count >= 100:
                break
        if word_count > 100:
            description = ' '.join(description.split()[:100])
        return description.strip() + "..."


class Users(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    wallet = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User: {self.name}>'
    
    def get_id(self):
        return self.user_id


ledger = db.Table('ledger',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('loan_id', db.Integer),
    db.Column('lend_date', db.Date),
    db.Column('expiry_date', db.Date)
)

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    user = db.relationship('Users', backref='Admin')
    events = db.relationship('Events', backref='admin')

    def __repr__(self):
        return f'<Admin id:{self.admin_id}, User:{self.user.name}>'



class Events(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('event_types.type_id'), nullable=False)

    def __repr__(self):
        return f'<Event {self.event_id} at {self.timestamp}>'


class EventTypes(db.Model):
    type_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    events = db.relationship('Events', backref='event_type')

    def __repr__(self):
        return f'<EventType: {self.type_id}, {self.type}>'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')



@app.route('/')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    books_pagination = Books.query.paginate(page=page, per_page=per_page, error_out=False)
    books = books_pagination.items
    for book in books:
        book.description = book.get_description()
    next_url = url_for('home', page=books_pagination.next_num) if books_pagination.has_next else None
    prev_url = url_for('home', page=books_pagination.prev_num) if books_pagination.has_prev else None
    return render_template('home.html', books=books, books_pagination=books_pagination, next_url=next_url, prev_url=prev_url)


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Books.query.get_or_404(book_id)
    book.description = book.get_description()
    return render_template('book_detail.html', book=book)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists')
        else:
            new_user = Users(username=form.username.data, password=form.password.data, wallet=1000.0)
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


@app.route('/profile')
@login_required
def profile():
    ledger_entries = db.session.query(ledger).filter_by(user_id=current_user.user_id).all()
    books = Books.query.filter(Books.book_id.in_([entry.book_id for entry in ledger_entries])).all()
    books_dict = {book.book_id: book for book in books}
    return render_template('profile.html', ledger_entries=ledger_entries, books_dict=books_dict)


@app.route('/buy/<int:book_id>', methods=['POST'])
@login_required
def buy_book(book_id):
    book = Books.query.get_or_404(book_id)
    existing_entry = db.session.query(ledger).filter_by(book_id=book_id, user_id=current_user.user_id).first()

    if existing_entry:
        flash('Book already bought')
    elif current_user.wallet >= book.price:
        current_user.wallet -= book.price

        max_loan_id = db.session.query(db.func.max(ledger.c.loan_id)).scalar()
        new_loan_id = (max_loan_id or 0) + 1

        lend_date = datetime.now()
        expiry_date = lend_date + timedelta(days=30)

        ledger_entry = ledger.insert().values(
            book_id=book_id, 
            user_id=current_user.user_id,
            loan_id=new_loan_id, 
            lend_date=lend_date,
            expiry_date=expiry_date)
        db.session.execute(ledger_entry)
        db.session.commit()
        flash('Book purchased successfully')
    else:
        flash('Insufficient funds')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    book = Books.query.get_or_404(book_id)
    purchased = db.session.query(ledger).filter_by(book_id=book_id, user_id=current_user.user_id).first()
    if not purchased:
        flash("You haven't purchased this book.")
        return redirect(url_for('profile'))
    
    return render_template('read_book.html', book=book)



def insert_books_from_json():
    with open('books.json', 'r') as f:
            books = json.load(f)
        
    for book in books:
        title, author_name, release_date_str, cover_image, content, price, genres = book

        print(f'Processing book: {title} by {author_name}')

        try:
            release_date = datetime.strptime(release_date_str, '%b %d, %Y').date()

            author = Authors.query.filter_by(name=author_name).first()
            if not author:
                author = Authors(name=author_name)
                db.session.add(author)
                db.session.commit()
                print(f'Added new author: {author_name}')

            new_book = Books(
                title=title,
                content=content,
                release_date=release_date,
                cover_image=cover_image,
                price=price
            )
            db.session.add(new_book)
            db.session.commit()
            print(f'Added new book: {title}')

            # new_book_author = written_by.insert().values(book_id=new_book.book_id, author_id=author.author_id)
            # db.session.execute(new_book_author)
            # db.session.commit()
            # print(f'Linked book {title} with author {author_name}')

            new_book.authors.append(author)
            db.session.commit()
            print(f'Linked book {title} with author {author_name}')

            for genre_name in genres:
                genre = Genres.query.filter_by(genre=genre_name).first()
                if not genre:
                    genre = Genres(genre=genre_name)
                    db.session.add(genre)
                    db.session.commit()
                    print(f'Added new genre: {genre_name}')

                new_book_genre = what_genre.insert().values(book_id=new_book.book_id, genre_id=genre.genre_id)
                db.session.execute(new_book_genre)
                db.session.commit()
                print(f'Linked book {title} with genre {genre_name}')

        except Exception as e:
            print(f'Error processing book {title}: {e}')
            db.session.rollback()

@app.cli.command('insert_books')
def insert_books_command():
    """Insert books from books.json into the database."""
    insert_books_from_json()
    print("Books inserted successfully.")


if __name__ == '__main__':
    app.run(debug=True)