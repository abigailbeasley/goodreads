'''
Description: This file scrapes goodreads for up-to-date book info
'''

from bs4 import BeautifulSoup
import requests
import pandas as pd


reviews_as_dicts = list()

url_beginning = 'https://www.goodreads.com/review/list/8300563?page='
url_end = '&ref=nav_mybooks'

page_num = 1

url=url_beginning + str(page_num) + url_end

page = requests.get(url)

page_exists = True

while page_exists:
    print('Beginning page: ' + str(page_num))

    page_to_text = page.text

    soup = BeautifulSoup(page_to_text, 'html.parser')

    bookshelf = soup.find('table', class_ = 'table stacked')

    #list of lists
    reviews = bookshelf.find_all('tr', class_= 'bookalike review')

    if len(reviews) == 0:
        break

    data_labels = [value.label.string for value in reviews[1].find_all('td')]

    for review in reviews:
        row_data = review.find_all('td')

        for i in range(1, len(row_data)):
            raw_value_as_text = row_data[i].text#.strip()
            cleaned_value = raw_value_as_text.replace('\n', '')
            cleaned_value = cleaned_value.replace(data_labels[i], '').strip()
            row_data[i] = cleaned_value

        reviews_as_dicts.append({k:v for (k,v) in zip(data_labels, row_data)})

    print(str(page_num) + ' Complete!')
    # getting next page
    page_num = page_num + 1

    url= url_beginning + str(page_num) + url_end

    page = requests.get(url)

    page_exists = page.status_code == 200
    print(page_exists)

# converting to dataframe
df = pd.DataFrame(reviews_as_dicts)
print(df.info())

df.to_csv('bookshelf_data.csv')

#print(re.search('<div class="value">(.*)<div', books[1]).group())

#reviews = {review_id: book for (review_id, book) in zip(review_ids, books)}
# converting list of fields to a dictionary for each book
#books = [for book in books]




