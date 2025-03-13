'''
Contains book recommendation functions

'''

from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.sparse import csr_matrix

def load_data():

    return pd.read_csv('data/combined_ratings_2024-11-23.csv', usecols=['user_id', 'book_id', 'title', 'rating', 'author'])

def clean_data(ratings):
    ratings['author'] = ratings['author'].str.replace('*', '')
    ratings['book_tag'] = ratings['title'] + '; ' + ratings['author']
    ratings['book_tag'] = ratings['book_tag'].apply(str)

    # removing null ratings (=0)
    ratings = ratings[ratings['rating'] > 0]

    print(ratings.info())

    ratings['book_id'] = ratings['book_id'].apply(int)

    books = ratings[['book_id', 'book_tag', 'title']].drop_duplicates()

    books['link'] = 'https://www.goodreads.com/book/show/' + str(books['book_id'])

def find_similar_books(book_id, X, book_mapper, book_inv_mapper, k, metric='cosine'):
    """
    Finds k-nearest neighbours for a given book id.
    
    Args:
        book_id: id of the book of interest
        X: user-item utility matrix
        k: number of similar movies to retrieve
        metric: distance metric for kNN calculations
    
    Output: returns list of k similar book ID's
    """
    X = X.T
    neighbour_ids = []
    
    book_ind = book_mapper[book_id]
    book_vec = X[book_ind]
    if isinstance(book_vec, (np.ndarray)):
        book_vec = book_vec.reshape(1,-1)
    # use k+1 since kNN output includes the movieId of interest
    kNN = NearestNeighbors(n_neighbors=k+1, algorithm="brute", metric=metric)
    kNN.fit(X)
    neighbour = kNN.kneighbors(book_vec, return_distance=False)
    for i in range(0,k):
        n = neighbour.item(i)
        neighbour_ids.append(book_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids

def create_X(df, user_id, book_id, rating):
        """
        Generates a sparse matrix from ratings dataframe.
        
        Args:
            df: pandas dataframe
            user_id: column name of user id
            book_id: column name of book id
            rating: column name of rating
        
        Returns:
            X: sparse matrix
            user_mapper: dict that maps user id's to user indices
            user_inv_mapper: dict that maps user indices to user id's
            book_mapper: dict that maps book id's to book indices
            book_inv_mapper: dict that maps book indices to book id's
        """
        M = df[user_id].nunique()
        N = df[book_id].nunique()

        user_mapper = dict(zip(np.unique(df[user_id]), list(range(M))))
        book_mapper = dict(zip(np.unique(df[book_id]), list(range(N))))
        
        user_inv_mapper = dict(zip(list(range(M)), np.unique(df[user_id])))
        book_inv_mapper = dict(zip(list(range(N)), np.unique(df[book_id])))
        
        user_index = [user_mapper[i] for i in df[user_id]]
        item_index = [book_mapper[i] for i in df[book_id]]

        X = csr_matrix((df[rating], (user_index,item_index)), shape=(M,N))
        
        return X, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper