from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

# Configure the PostgreSQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:42069@localhost/ebook_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    cover_image = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Book: {self.title}>'

class Authors(db.Model):
    autor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Author: {self.name}>'

written_by = db.Table('written_by',
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.autor_id'), primary_key=True)
)

class Genres(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Genre: {self.genre}>'


what_genre = db.Table('what_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True)
)


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    wallet = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User: {self.name}>'


ledger = db.Table('ledger',
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True),
    db.Column('loan_id', db.Integer),
    db.Column('expiry_date', db.Date),
    db.Column('lend_date', db.Date)
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



@app.route('/')
def home():
    return render_template('website.html')

if __name__ == '__main__':
    app.run(debug=True)