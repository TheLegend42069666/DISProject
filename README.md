# DISProject
## How to run and setup database
0. Open ``config.ini`` and ensure that the correct database credentials are in the ``[Database]`` section, so the app can connect to your local postgresql instance.  
1. Use ``flask run`` to start the app.  
2. In a seperate terminal use ``flask reset-db`` to create tables and load data.  
3. Open app in a browser with ``localhost:5000`` or the address shown in the terminal.  
  
Note: You can also use ``flask scrape-db n`` to scrape ``n`` books from [gutenberg.com](https://www.gutenberg.org/), but we have already done this with about 100 books, which are found in ``dump.csv`` (125 MB).  
To load use ``flask reset-db``.  

## Information about project
* Our schema is defined in ``schema.py``. We use sqlalchemy as our ORM.  
* We use regular expression in ``datagen.py`` to extract relevant info when scraping. This file is responsible for scraping and other dummy data generation.  
* Out E/R diagram is in ``diagram.png`` or ``diagram.svg``.  


## Credits
Kevin Terkelsen \<lcx251@alumni.ku.dk>  
Christian Jordan \<gcp547@alumni.ku.dk>  
Michael Le \<xfm296@alumni.ku.dk>  
