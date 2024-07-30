from surprise import Dataset
from surprise import Reader
from surprise import KNNBasic

from collections import defaultdict
from operator import itemgetter
import heapq
import csv

def getMovieName(movieID):
    if int(movieID) in movieID_to_name:
        return movieID_to_name[int(movieID)]
    else:
        return ""

def load_dataset():
    ratings_dataset = 0
    reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
    ratings_dataset = Dataset.load_from_file( 'ml-latest-small/ratings.csv', reader=reader)
   
    movieID_to_name = {}
    with open ('ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile:
        movie_reader = csv.reader(csvfile)
        next(movie_reader)
        for row in movie_reader:
            movieID = int(row[0])
            movie_name = row[1]
            movieID_to_name[movieID] = movie_name
    
    return (ratings_dataset, movieID_to_name)

dataset, movieID_to_name = load_dataset()
trainset = dataset.build_full_trainset()

similarity_matrix = KNNBasic(sim_options={'name':'cosine', 'user_based':False}).fit(trainset).compute_similarities()

test_subject = '500'
k = 20 # top-k items

# When using Surprise, there are RAW and INNER IDs.
# Raw IDs are the IDs, strings or numbers, you use when
# creating the trainset. The raw ID will be converted to
# an unique integer Surprise can more easily manipulate
# for computations.
#
# So in order to find an user inside the trainset, you
# need to convert their RAW ID to the INNER Id. 
# Read here for more info https://surprise.readthedocs.io/en/stable/FAQ.html#what-are-raw-and-inner-ids
test_subject_iid = trainset.to_inner_uid(test_subject)
test_subject_ratings = trainset.ur[test_subject_iid]
k_neighbors = heapq.nlargest(k, test_subject_ratings, key=lambda t: t[1])

candidates = defaultdict(float)

# for each item rated by a neighbor
for itemID, rating in k_neighbors:
    try: 
        similarities = similarity_matrix[itemID]
        for innerID, score in enumerate(similarities):
            candidates[innerID] += score * (rating/5)
    except:
        continue


watched = {}
for itemID, rating in trainset.ur[test_subject_iid]:
    watched[itemID] = 1

recommendations = []

position = 0 
for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
    if not itemID in watched:
        recommendations.append(getMovieName(trainset.to_raw_iid(itemID)))
        position += 1
        if position > 10: break

for rec in recommendations:
    print('Movie: ', rec)
