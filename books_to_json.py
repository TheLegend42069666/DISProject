from book_scrape import get_book_details
import json

book_details = []
for i in range(1, 101):
    print(i)
    book = get_book_details(i)
    book_details.append(book)


with open('books.json', 'w') as f:
    json.dump(book_details, f)