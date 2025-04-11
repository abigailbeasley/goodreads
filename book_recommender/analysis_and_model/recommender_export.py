
## loading libraries
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from google.cloud import bigquery


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

def generate_sparse_matrix(df, user_id, book_id, rating):
    """
    Generates a sparse matrix from ratings dataframe.
    
    Arguments:
        df: pandas dataframe
        user_id: column name of user id
        book_id: column name of book id
        rating: column name of rating
    
    Returns:
        R: sparse ratings matrix
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

    R = csr_matrix((df[rating], (user_index,item_index)), shape=(M,N))
    
    return R, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper

def load_data():
    client = bigquery.Client()

    # Perform a query.
    QUERY = ('SELECT * FROM `civic-shell-419721.ratings.ratings_filtered')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        print(row.name)

    return ratings

ratings = load_data()

ratings.info()

#Xf, user_map, book_map, user_inv_map, book_inv_map = generate_sparse_matrix(ratings, user_id='user_id', book_id='book_tag', rating='rating')

#recs = find_similar_books(book_id = 'Pride and Prejudice; Austen, Jane', k= 11, book_mapper=book_map, book_inv_mapper = book_inv_map, X=Xf)

#print(recs)