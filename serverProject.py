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
    bookid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    releaseDate = db.Column(db.Date, nullable=False)
    coverImage = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

class Authors(db.Model):
    Autorid = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Authors {self.Name}>'

written_by = db.Table('written_by',
    db.Column('book_id', db.Integer, db.ForeignKey('book.bookid'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.Autorid'), primary_key=True)
)


@app.route('/')
def home():
    return render_template('website.html')

if __name__ == '__main__':
    app.run(debug=True)