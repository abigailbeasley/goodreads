
## importing functions
from helper_funs import find_similar_books, generate_sparse_matrix, get_new_recs, load_data, get_recent_reads, upload_recs

# getting ratings data
ratings = load_data()

# putting into sparse matrix
Xf, user_map, book_map, user_inv_map, book_inv_map = generate_sparse_matrix(ratings, user_id='user_id', book_id='book_tag', rating='rating')

# getting recent likes
recent_likes = get_recent_reads()

# getting recommendations
recs = get_new_recs(recent_likes)

upload_recs(recs)

print(recs)