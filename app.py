from os import path
from configparser import ConfigParser
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
import click

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
from schema import * 
from database import *

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