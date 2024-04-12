import pandas as pd
from scrape_goodreads import get_bookshelf
from scrape_user_ratings import grab_reviewers_and_ratings, load_reviews
import time
# Part A. Pulls top reviews from each book in my read shelf
# Part B. Pulls rating data from each reviewer

# Part A: Pull top reviews from each book I have rated

# Step 1: Get my bookshelf

my_shelf = pd.read_csv('user_libraries/8300563_bookshelf_data.csv')

# cleaning up links to books
my_shelf['url'] = 'https://www.goodreads.com' + my_shelf['link'].astype(str) + '/reviews'

# creating book id
my_shelf['book_id'] = (my_shelf['link'].str.replace('/book/show/', '')
                       .str.replace('/', ''))

# filter to only include books I have reviewed
my_shelf = my_shelf.dropna(subset = ["Abigail's rating"])
'''
# grabbing reviews:
books_grabbed = 0

for _, row in my_shelf.iterrows():

    save_path = 'book_reviews/' + str(row['book_id']) + '_reviews.csv'

    try:
        df = pd.read_csv(save_path)

    except:
        page = load_reviews(10, row['url'], 5)

        print('done loading!')

        reviews = grab_reviewers_and_ratings(page)

        save_path = 'book_reviews/' + str(row['book_id']) + '_reviews.csv'

        reviews.to_csv(save_path)

    if len(df) < 330:

    # need to add check for cases when there are less than 330 reviews

'''

# combining all data
all_data = pd.DataFrame()

not_gathered = list()

for _, row in my_shelf.iterrows():

    save_path = 'book_reviews/' + str(row['book_id']) + '_reviews.csv'

    try:
        df = pd.read_csv(save_path)
        df['book_id'] = row['book_id']
        all_data = pd.concat([all_data, df], axis = 0)
        print('adding reviews from ' + row['title'])
    except:
        not_gathered.append(row['title'])
    
all_data.to_csv('all_review_data.csv')
pd.DataFrame(not_gathered).to_csv('book_reviews_not_gathered.csv')

## looking at reviews
all_reviews = pd.read_csv('all_review_data.csv')

all_reviews = all_reviews.drop_duplicates(subset = ['user_links'])

print(all_reviews.info())

failed_on_user = list()

## getting user libraries
for user_link in all_reviews['user_links']:
    try:
        user_id = user_link.split('show/')[1].split('-')[0]
        print(user_id)

        try:
            get_bookshelf(user_id)
        except:
            failed_on_user.append(user_id)
    except:
        print('no user info')

pd.DataFrame(failed_on_user).to_csv('failed_to_retrieve_users.csv')

