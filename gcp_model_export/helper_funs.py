
## loading libraries
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from google.cloud import bigquery
import re


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
    QUERY = ('SELECT * FROM `civic-shell-419721.ratings.ratings_filtered`')
    query_job = client.query(QUERY)  # API request
    df = query_job.to_dataframe()    # Convert the query results to a DataFrame

    return df

def get_recent_reads():
    '''
    Returns the most recent 10 books with a 5 star review
    '''
    client = bigquery.Client()

    # Perform a query.
    QUERY = (
    "SELECT author, title, date_read, "
    "SAFE.PARSE_DATE('%b %d, %Y', date_read) AS parsed_date "
    "FROM `civic-shell-419721.my_goodreads_library.bookshelf` "
    "WHERE my_rating = 5 "
    "AND SAFE.PARSE_DATE('%b %d, %Y', date_read) IS NOT NULL "
    "ORDER BY parsed_date DESC "
    "LIMIT 10")
    query_job = client.query(QUERY)  # API request
    df = query_job.to_dataframe()    # Convert the query results to a DataFrame

    # Removing * symbol that is on some author names
    df['author'] = df['author'].str.replace('*', '')  

    # Cleaning book titles
    df['title'] = df['title'].astype(str)
    df['title'] = list(map(lambda x: re.sub(r"[\(\[].*?[\)\]]", "", x), df['title']))
    df['title'] = df['title'].str.strip()

    df['book_tag'] = df['title'] + "; " + df['author']

    return df['book_tag']

def get_new_recs(book_list):
    #recent_favorites = recent_favorites#
    suggestions = list()
    for book_tag in book_list:
        try:
            sugs = find_similar_books(book_tag, Xf, book_map, book_inv_map, k=10)
            suggestions.append({"Recently Read": book_tag, **{f"Suggestion {i+1}": sugs[i] for i in range(len(sugs))}})
        except:
            print('There is no data on: ' + book_tag)
    return pd.DataFrame(suggestions)

def upload_recs(df, table_id = 'civic-shell-419721.ratings.recommendations'):
    """
    Writes a pandas DataFrame to a BigQuery table.

    Args:
        df (pandas.DataFrame): DataFrame to write.
        table_id (str): Full table ID in format "project.dataset.table".
    """
    # Initialize the BigQuery client
    client = bigquery.Client()

    # Optional: Configure load job settings (e.g., overwrite or append)
    job_config = bigquery.LoadJobConfig(
        # overwrites existing table
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        # Enable schema autodetect if you want BigQuery to infer column types.
        autodetect=True,
    )

    # Load the DataFrame to BigQuery
    load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

    # Wait for the job to complete.
    load_job.result()

    # Print the result
    print(f"Loaded {load_job.output_rows} rows into {table_id}.")
