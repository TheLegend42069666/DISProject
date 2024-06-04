from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Configure the PostgreSQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:42069@localhost/ebook_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    bookid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    releaseDate = db.Column(db.Date, nullable=False)

    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Book {self.title}>'


@app.route('/')
def home():
    return render_template('website.html')

if __name__ == '__main__':
    app.run(debug=True)