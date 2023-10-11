'''
Description: Script to scrape data from goodreads bookshelf and exported as csv.
'''

from bs4 import BeautifulSoup
import requests
import pandas as pd

username = 'abigail_beasley'
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

    # quitting while loop if table is empty at nth page
    if len(reviews) == 0:
        break
    
    book_links = list()


    data_labels = [value.label.string for value in reviews[1].find_all('td')]
    data_labels.append('link')

    for review in reviews:
        row_data = review.find_all('td')

        # getting link 
        book_link = row_data[3].find('a', href = True)['href']

        # extracting other values from book
        for i in range(1, len(row_data)):
            raw_value_as_text = row_data[i].text#.strip()
            cleaned_value = raw_value_as_text.replace('\n', '')
            cleaned_value = cleaned_value.replace(data_labels[i], '').strip()
            row_data[i] = cleaned_value

        # adding link to book data
        row_data.append(book_link)

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

path = '../data/' + username + '_bookshelf_data.csv'
df.to_csv(path)

#print(re.search('<div class="value">(.*)<div', books[1]).group())

#reviews = {review_id: book for (review_id, book) in zip(review_ids, books)}
# converting list of fields to a dictionary for each book
#books = [for book in books]
