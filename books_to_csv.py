import pandas

import requests
from bs4 import BeautifulSoup
import random
import re

base_url = "https://www.gutenberg.org/ebooks/"

def get_book_content(book_id):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    response = requests.get(url)

    if response.status_code == 404:
        return f'Audiobook: {base_url}{book_id}'
    
    content = response.text

    start_text = r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK.*\*\*\*\s*"
    end_text = '*** END OF THE PROJECT GUTENBERG EBOOK'

    start_match = re.search(start_text, content)
    if start_match:
        content = content[start_match.end():]

    end_index = content.find(end_text)
    if end_index != -1:
        content = content[:end_index]
    
    content = content.replace('\r', ' ').replace('\n', ' ')

    return content[:500]


# def calculate_price(content):
#     number_of_words = 0
#     for word in content:
#         number_of_words += 1
#     if number_of_words < 50:
#         return 150
    
#     word_ranges = [
#             (50, 30000), (30000, 90000), (90000, 150000), (150000, 210000), 
#             (210000, 270000), (270000, 330000), (330000, 390000), (390000, 450000),
#             (450000, 510000), (510000, float('inf'))
#         ]
    
#     price_ranges = [
#         [50, 55, 60, 65, 70, 75, 80, 85, 90, 95],
#         [75, 80, 85, 90, 95, 100, 105, 110, 115, 120],
#         [100, 105, 110, 115, 120, 125, 130, 135, 140, 145],
#         [125, 130, 135, 140, 145, 150, 155, 160, 165, 170],
#         [150, 155, 160, 165, 170, 175, 180, 185, 190, 195],
#         [175, 180, 185, 190, 195, 200, 205, 210, 215, 220],
#         [200, 205, 210, 215, 220, 225, 230, 235, 240, 245],
#         [225, 230, 235, 240, 245, 250, 255, 260, 265, 270],
#         [250, 255, 260, 265, 270, 275, 280, 285, 290, 295],
#         [275, 280, 285, 290, 295, 300, 305, 310, 315, 320]
#     ]

    # for (low, high), prices in zip(word_ranges, price_ranges):
    #     if low <= number_of_words < high:
    #         price = random.choice(prices)
    #         return price, number_of_words


def get_book_details(book_id):
    url = f"{base_url}{book_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_text = soup.find('h1', {'itemprop': 'name'}).get_text(separator="by")
    
    title = title_text.split("by")[0].strip()
    try:
        author = title_text.split("by")[1].strip()
    except IndexError:
        author = "Anonymous"

    release_date = soup.find('td', {'itemprop': 'datePublished'}).get_text()

    cover_image_url = soup.find('img', {'class': 'cover-art'})['src']

    content = get_book_content(book_id)

    return title, author, release_date, cover_image_url, content


book_details = []
for i in range(11, 21):
    book = get_book_details(i)
    book_details.append(book)

dataframe = pandas.DataFrame(book_details, columns=[
    'Title', 'Author', 'Release Date', 'Cover Image URL', 'Content'])

# Ensure proper handling of large text fields and commas
dataframe.to_csv('books.csv', index=False)