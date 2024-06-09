# DISProject
## How to run and setup database
1. Open ``config.ini`` and ensure that the correct database credentials are in the ``[Database]`` section, so the app can connect to your local postgresql instance.  
2. Ensure requirements are installed by running ``pip install -r requirements.txt``  
3. Use ``flask run`` to start the app.  
4. In a seperate terminal window use ``flask reset-db`` to create tables and load dummy data. Should take about 30 seconds to run.  
5. Open app in a browser with ``localhost:5000`` or the address shown in the terminal.  
  
Note: You can also use ``flask scrape-db n`` to scrape ``n`` books from [gutenberg.com](https://www.gutenberg.org/), but we have already done this with about 50 books, which are found in ``dump.csv`` (~50 MB). To load use ``flask reset-db``.  


## Information about the project
- Our schema is defined in ``schema.py`` or ``schema.sql``. We use sqlalchemy as our ORM.  
- We use regular expression in ``datagen.py`` to extract relevant info when web scraping.   
- Our E/R diagram is ``diagram.png`` and/or ``diagram.svg``. 

### Project structure
- ``config.ini`` should contain login credentials to a local postgress database. Though it's currently left blank, so make sure to fill it out before running.   
- ``app.py`` is the entry point. Contains all the handlers for routers and cli. Can be ran with ``flask run`` or ``python app.py``  
- ``schema.py`` is where the database schema is defined. We use sqlalchemy as our ORM and thus use their syntax/api to define our schema. If a pure sql schema is needed then see ``schema.sql``. This contains an equivalen schema as the one in ``schema.py`` just written in sql, though not used in the project. Therefore it might be outdated.  
- ``database.py`` is where we collect all our database interactions. This is just for better code etiquette. It exposes a bunch of wrappers around the database connection allowing the changes needed with a single function call.
- ``datagen.py`` is responsible for dummy data generation. It contains a webscraper that uses regular expression to parse different properties needed by the database. It's also responsible for creating random users, reviews and loans to populate the database. It's ran every time ``flask reset-db`` is ran.  

## Credits
Kevin Terkelsen \<lcx251@alumni.ku.dk>  
Christian Jordan \<gcp547@alumni.ku.dk>  
Michael Le \<xfm296@alumni.ku.dk>  
