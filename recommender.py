from surprise import accuracy, Dataset, Reader, KNNBasic
import random
import csv

def get_movie_name(movieID, movieID_to_name):
        if int(movieID) in movieID_to_name:
            return movieID_to_name[int(movieID)]
        else:
            return ""
        
def get_movies_dict():
    movieID_to_name = {} 
    with open ('ml-latest-small/movies.csv', newline='', encoding='utf-8') as csvfile:
        movie_reader = csv.reader(csvfile)
        next(movie_reader)
        for row in movie_reader:
            movieID = int(row[0])
            movie_name = row[1]
            movieID_to_name[movieID] = movie_name
    return movieID_to_name


def load_dataset():
    reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
    return Dataset.load_from_file( 'ml-latest-small/ratings.csv', reader=reader)
    
def get_top_n_rec(user_rid: str, n=20):
    movieID_to_name = get_movies_dict()
    dataset = load_dataset()
    trainset = dataset.build_full_trainset() # the trainset is built from the whole dataset 
    algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': False})
    algo.fit(trainset) 

    predictions = {}

    user_iid = trainset.to_inner_uid(user_rid) # e.g. the user raw id is '500' -> string, while the user inner is 499 -> integer (used by surprise)
    user_ratings =  trainset.ur[user_iid] 
    watched = []
    for item_iid, _ in user_ratings:
        watched.append(trainset.to_raw_iid(item_iid))
    for movieId in movieID_to_name:
        if not movieId in watched:
            uid, iid, true_r, est, details = algo.predict(user_rid, str(movieId))
            predictions[movieId] = est

    pred_list = list(predictions.items())   
    random.shuffle(pred_list) 
    pred_shuffled = dict(pred_list)
    pred_sorted = sorted(pred_shuffled.items(), key=lambda x: x[1], reverse=True)

    recommendations = []
    for movieId, _ in pred_sorted[:n]:
        title = get_movie_name(movieId, movieID_to_name)
        recommendations.append(title)

    return recommendations
        
def get_accuracy(user_rid: str):
    dataset = load_dataset()
    trainset = dataset.build_full_trainset()
    algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': False})
    algo.fit(trainset)

    predictions = []

    user_iid = trainset.to_inner_uid(user_rid) 
    user_ratings =  trainset.ur[user_iid] 
    
    watched = []
    for item_iid, rating in user_ratings:
        watched.append((trainset.to_raw_iid(item_iid), rating))  

    for movieId, actual_rating in watched:
        pred = algo.predict(user_rid, str(movieId), r_ui=actual_rating)
        predictions.append(pred)

    accuracy.rmse(predictions, verbose=True) 
   

if __name__=='__main__': 
    # print(get_accuracy('13'))
    # print(get_top_n_rec('13'))
    pass
    
    
    
        