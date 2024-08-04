from surprise import Dataset
from surprise import Reader
from surprise import KNNBasic

from collections import defaultdict
from operator import itemgetter
import heapq
import csv

def load_dataset():
    reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
    ratings_dataset = Dataset.load_from_file( 'ml-latest-small/ratings.csv', reader=reader)
   
    movieID_to_name = {} # {1:'Friends', 2: ... }
    with open ('ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile:
        movie_reader = csv.reader(csvfile)
        next(movie_reader)
        for row in movie_reader:
            movieID = int(row[0])
            movie_name = row[1]
            movieID_to_name[movieID] = movie_name


    return (ratings_dataset, movieID_to_name)


class Recommender:


    def __init__(self):
        self.dataset, self.movieID_to_name = load_dataset()
        self.trainset = self.dataset.build_full_trainset()
        self.similarity_matrix = KNNBasic(sim_options={'name': 'cosine', 'user_based': False}).fit(self.trainset).compute_similarities()

    
    def getMovieName(self, movieID):
        if int(movieID) in self.movieID_to_name:
            return self.movieID_to_name[int(movieID)]
        else:
            return ""

    # When using Surprise, there are RAW and INNER IDs.
    # Raw IDs are the IDs, you use when creating the trainset. 
    # The raw ID will be converted to an unique integer Surprise can more easily manipulate  for computations.
    #
    # So in order to find an user inside the trainset, you need to convert their RAW ID to the INNER Id. 
    # Read here for more info https://surprise.readthedocs.io/en/stable/FAQ.html#what-are-raw-and-inner-ids
    
 
    def get_top_k_recommendations(self, user_rid: str, k=20):

        user_iid = self.trainset.to_inner_uid(user_rid) # e.g. the raw id is '500' -> string, while the inner is 499 -> integer (used by surprise)
        user_ratings =  self.trainset.ur[user_iid] # [(itemID, score), ...]
        k_neighbors = heapq.nlargest(k, user_ratings, key=lambda t: t[1]) # sorted list of ratings to get the top 20
        candidates = defaultdict(float)

        for itemID, rating in k_neighbors:
            try: 
                similarities = self.similarity_matrix[itemID]
                for innerID, score in enumerate(similarities):
                    candidates[innerID] += score * (rating/5) # 0.98 * (4/5) 
            except:
                continue

        watched = {}
        for itemID, rating in self.trainset.ur[user_iid]:
            watched[itemID] = 1

        recommendations = []

        position = 0 
        for itemID, _ in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            if not itemID in watched:
                recommendations.append(self.getMovieName(self.trainset.to_raw_iid(itemID)))
                position += 1
                if position > 10: break

        return recommendations


if __name__=='__main__': 
    # rec = Recommender()
    # recs = rec.get_top_k_recommendations("1")
    pass
