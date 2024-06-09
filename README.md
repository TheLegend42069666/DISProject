# DISProject
## How to run and setup database
0. Open ``config.ini`` and ensure that the correct database credentials are in the ``[Database]`` section, so the app can connect to your local postgresql instance.  
1. Ensure requirements are installed by running ``pip install -r requirements.txt``  
2. Use ``flask run`` to start the app.  
3. In a seperate terminal use ``flask reset-db`` to create tables and load dummy data. Should take about 30 seconds to run.  
4. Open app in a browser with ``localhost:5000`` or the address shown in the terminal.  
  
Note: You can also use ``flask scrape-db n`` to scrape ``n`` books from [gutenberg.com](https://www.gutenberg.org/), but we have already done this with about 100 books, which are found in ``dump.csv`` (125 MB).  
To load use ``flask reset-db``.  


## Information about project
- Our schema is defined in ``schema.py`` or ``schema.sql``. We use sqlalchemy as our ORM.  
- We use regular expression in ``datagen.py`` to extract relevant info when scraping. This file is responsible for scraping and other dummy data generation.  
- Out E/R diagram is in ``diagram.png`` or ``diagram.svg``. 

### Project structure
- ``config.ini`` should contain login credentials to a local postgress database. Though it's currently left blank, so make sure to fill it out before running.   
- ``app.py`` is the entry point. Contains all the handlers for routers and cli. Can be ran with ``flask run`` or ``python app.py``  
- ``schema.py`` is where the database schema is defined. We use sqlalchemy as our ORM and thus use their syntax/api to define our schema. If a pure sql schema is needed see ``schema.sql``. This contains an equivalen schema as the one in ``schema.py`` just written in sql, though not used in the project.  
- ``database.py`` is where we collect all our database interactions. This is just for better code etiquette. It exposes a bunch of wrappers around the database connection allowing the changes needed with a single function call.
- ``datagen.py`` is responsible for dummy data generation. It contains a webscraper that uses regular expression to parse different properties needed by the database. It's also responsible for creating random users, reviews and loans to populate the database. It's ran every time ``flask reset-db`` is ran.  
- ``dump.csv`` contains ~100 books that we've scraped from [gutenberg.com](https://www.gutenberg.org/). This file is copied into the cleaned database every time ``flask reset-db`` is ran.
- ``templates/`` contains all html templates.

## Credits
Kevin Terkelsen \<lcx251@alumni.ku.dk>  
Christian Jordan \<gcp547@alumni.ku.dk>  
Michael Le \<xfm296@alumni.ku.dk>  
