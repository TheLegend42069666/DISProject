import sys
import time
import requests
import re
import base64
import csv
from dateutil import parser as dateparser
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from multiprocessing import Pool, Lock
import schema

csv.field_size_limit(sys.maxsize)
__lock = Lock()

ROOT = "https://www.gutenberg.org/"
ROOT_INDEX = "https://www.gutenberg.org/ebooks/search/?sort_order=downloads"

WHITESPACE = re.compile(r'\s+')
REMOVE = re.compile(r'<.+>')
AUTHOR_REMVOE = re.compile(r',\s*\d+-\d+')
THEME_SPLIT = re.compile(r' ?, ?| ?-- ?')
THEME_EXTRACT = re.compile(r'\((.*)\)')
DOWNLOADS_EXTRACT = re.compile(r'\b(\d+)\b')
CONTENT_EXTRACT = re.compile(r'\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG.*\*\*\*(.*)\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG.*\*\*\*', re.DOTALL)


def req(url, trials = 5):
    print(f"Requesting: {repr(url)}")
    backoff = 0.1
    while trials > 0:
        time.sleep(backoff)
        try:
            res = requests.get(url)
            if res.status_code != 200: 
                backoff *= 5
                trials -= 1
                print(f'\nGot {res.status_code}, {trials} retrying in {backoff:.1f}s: {repr(url)}')
                continue
        except Exception as e:
            backoff *= 5
            trials -= 1
            print(f'\n{e}, {trials} retrying in {backoff:.1f}s: {repr(url)}')
            continue
        return res
    print(f'\nGiving up: {repr(url)}')
    return None


def scrape_links(n):
    if n <= 0: 
        return []
    links = []
    
    res = req(ROOT_INDEX)
    soup = BeautifulSoup(res.content, 'html.parser')
    while True:
        next = soup.find('a', {'title': 'Go to the next page of results.'})
        if next is None:
            break

        for elem in soup.find_all('li', {'class': 'booklink'}):
            tag = elem.find('a', {'class': 'link'})
            if tag is not None:
                links.append(urljoin(ROOT, tag['href']))
                if len(links) >= n:
                    return links

        res = req(urljoin(ROOT, next['href']))
        soup = BeautifulSoup(res.content, 'html.parser')

    return links

def worker(link, filepath):
    try:
        res = req(link)
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find('table', {'class': 'bibrec'})

        title_elem = table.find('td', {'itemprop': 'headline'})
        author_elem = table.find('a', {'itemprop': 'creator'})
        lang_elem = table.find('tr', {'property': 'dcterms:language'})
        date_elem = table.find('td', {'itemprop': 'datePublished'})
        theme_elems = table.find_all('td', {'property': 'dcterms:subject'})
        downloads_elem = table.find('td', {'itemprop': 'interactionCount'})

        content_url = link + '.txt.utf-8'
        cover_url = soup.find('img', {'class': 'cover-art'})
        if cover_url is not None: cover_url = cover_url['src']

        title = title_elem.text
        title = re.sub(WHITESPACE, ' ', re.sub(REMOVE, ' ', title))
        title = title.strip()
        
        author = author_elem.text
        author = re.sub(AUTHOR_REMVOE, ' ', author)
        author = re.sub(WHITESPACE, ' ', re.sub(REMOVE, ' ', author))
        author = author.strip().capitalize()

        lang = lang_elem.find('td').text
        lang = re.sub(WHITESPACE, ' ', re.sub(REMOVE, ' ', lang))
        lang = lang.strip().lower()
        
        date = None
        if date_elem is not None:
            date = dateparser.parse(date_elem.text)

        themes = []
        for theme_elem in theme_elems:
            theme = theme_elem.find('a', {'class': 'block'}).text
            theme = re.sub(WHITESPACE, ' ', re.sub(REMOVE, ' ', theme))
            theme = theme.lower()
            inner = re.findall(THEME_EXTRACT, theme)
            split = re.split(THEME_SPLIT, re.sub(THEME_EXTRACT, '', theme))
            total = [t.strip() for t in [*inner, *split]] 
            themes.extend(total)
        themes = list(set(themes))

        downloads = re.search(DOWNLOADS_EXTRACT, downloads_elem.text).group(1).strip()

        cover = None
        if cover_url is not None:
            cover = base64.b64encode(req(cover_url).content).decode()
        content = str(req(content_url).content)
        content = re.search(CONTENT_EXTRACT, str(content)).group(1).strip()
        content = content.encode().decode('unicode_escape').strip().encode()

        with __lock:
            with open(filepath, "a") as file:
                writer = csv.writer(file)
                writer.writerow([
                    downloads,
                    title,
                    author,
                    lang,
                    date,
                    ",".join([theme for theme in themes]),
                    content,
                    cover
                ])
    except Exception as e:
        print(e)

def scrape_to_dump(links, filepath):
    with open(filepath, "w") as file:
        file.write('downloads,title,author,lang,date,themes,content,cover\n')
        pass
    with Pool(8) as pool:
        pool.starmap(worker, [(link, filepath) for link in links])

def dump_to_db(filepath, session):
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                book = schema.new_book(
                    session, 
                    row['title'], 
                    None, 
                    row['lang'], 
                    row['author'], 
                    1000, 
                    dateparser.parse(row['date']), 
                    base64.b64decode(row['cover'].encode()), 
                    row['content'].encode(), 
                    row['themes'].split(',')
                )
                generate_random_reviews(int(row['downloads']), book)
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)


def generate_random_reviews(downloads, book):
    pass


if __name__ == '__main__':
    print('Use "flask run" and in a seperate terminal "flask scrape-db" to run the webscraper.')
    print('Then use "flask reset-db" to load the scraped data into the database')
