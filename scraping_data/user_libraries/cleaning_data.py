'''
This script cleans and consolidates data for 
'''
import pandas as pd

# pulling user reviews from bookshelves and stacking them. 
## looking at reviews
all_reviews = pd.read_csv('all_review_data.csv')

all_reviews = all_reviews.drop_duplicates(subset = ['user_links'])

# removing results with no user info


all_reviews = all_reviews.droplevel(~(all_reviews['user_links'] == 'no user info'))

print(all_reviews.info())

#user_id = user_link.split('show/')[1].split('-')[0]