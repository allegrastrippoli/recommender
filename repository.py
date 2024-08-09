import pandas as pd
import csv
import requests
from sqlalchemy.sql.expression import func
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select
import re

api_key = '4994ff47'

engine = create_engine('sqlite:///movies.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

# From sqlalchemy Docs:
# Base: A class that links database tables with python classes
# MetaData: A collection of Table objects and their associated schema constructs
# The MetaData is accessed via the Base class

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movie_table'
    
    id = Column(Integer, primary_key=True)
    movieId = Column(Integer)
    title = Column(String)
    genres = Column(String)
    image_url = Column(String) 
    
    def __init__(self, movieId, title, genres, image_url):
        self.movieId = movieId
        self.title = title
        self.genres = genres
        self.image_url = image_url
    
    def __repr__(self):
        return f'{self.movieId, self.title, self.genres, self.image_url}'
    
class Rating(Base): 
    __tablename__ = 'rating_table'
    
    id = Column(Integer, primary_key=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    rating = Column(String)
    
    def __init__(self, userId, movieId, rating):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
    
    def __repr__(self):
        return f'{self.userId, self.movieId, self.rating}'


def check_movie_image(movieId: str):
    stmt = select(Movie).where(Movie.movieId == movieId)
    result = session.execute(stmt).first()
    try:
        if result[0].image_url is None:
            return True
        return False
    except:
        Exception('NoneType obj found')

def remove_year_from_title(title):
    pattern = r'\s*\(\d{4}\)'
    title = re.sub(pattern, '', title)
    return title.strip()

def fetch_movie_image(title):
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={title}'
    response = requests.get(url)
    data = response.json()
    if 'Error' in data.get('Response') or 'False' in data.get('Response'):
        print(data)
        return 'Response Error'
    return data.get('Poster')

def update_movie(movieId, url, commit_counter):
     movie = session.execute(select(Movie).filter_by(movieId=movieId)).scalar_one()
     movie.image_url = url
     print('Udating image_url...')
     if commit_counter >= 100:
        session.commit()

def retrieve_images():
    number_of_requests = 0
    commit_counter = 0 
    
    with open('ml-latest-small/movies.csv', mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  
        for row in reader:
            movieId, title, _ = row
            if check_movie_image(movieId):
                newtitle = remove_year_from_title(title)
                image_url = fetch_movie_image(newtitle)
                number_of_requests += 1
                if number_of_requests == 1000:
                            if commit_counter > 0:
                                session.commit()
                                return
                if not 'Response Error' in image_url:
                    commit_counter += 1 
                    update_movie(movieId, image_url, commit_counter)
                    if commit_counter >= 100:
                        commit_counter = 0 
                        
        if commit_counter > 0:
            session.commit()
    
def select_movie_from_title(titles: list):
    result = []
    for title in titles:
        stmt = select(Movie).where(Movie.title == title)
        result.append(session.execute(stmt).scalars().first())
    return result
    
def select_random_movies():
    stmt = select(Movie).order_by(func.random()).limit(20)
    result = session.execute(stmt).scalars().all()
    return result

def create_movie_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        newtitle = remove_year_from_title(row[1])
        image_url = fetch_movie_image(newtitle)
        movie = Movie(movieId=row[0], title=row[1], genres=row[2], image_url=image_url )
        session.add(movie)
    
    session.commit()

    print(session.query(Movie).count())

def create_rating_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        rating = Rating(userId=row[0], movieId=row[1], rating=row[2])
        session.add(rating)
    
    session.commit()

    print(session.query(Rating).count())

def check_user_rating(userId: int, movieId: int):
    # instead of this work around, the primary key should be <userId, movieId>
    stmt = select(Rating).where(Rating.userId == userId).where(Rating.movieId == movieId)
    result = session.execute(stmt).first()
    if result is None:
        return True
    return False

def update_db(userId: int, selected_movies: list):
    for movie in selected_movies:
        movieId, rating = movie.split(',')
        if check_user_rating(userId, int(movieId)):
            print('Adding ratings to the current session...')
            newrating = Rating(userId=userId, movieId=int(movieId), rating=rating)
            session.add(newrating)
    session.commit()

def update_csv(userId: int, selected_movies: list):
    with open('ml-latest-small/ratings.csv', 'a', newline='') as csvfile_out:
        writer = csv.writer(csvfile_out)
    
        for movie in selected_movies:
            movieId, rating = movie.split(',')
            row = [userId, movieId, rating, "None"]
            writer.writerow(row)

def insert_rating(userId: int, selected_movies: list):
    # TODO: remove csv, only db should be updated!
    update_csv(userId, selected_movies)
    update_db(userId, selected_movies)

def check_if_user_has_ratings(userId: int):
    stmt = select(Rating).where(Rating.userId == userId)
    result = session.execute(stmt).first()
    if result is None:
        return False
    return True

def delete_user_ratings(from_id: int, to_id: int):
    """
    id: database id, NOT userId
    """
    for id in range(from_id, to_id):
        rating = session.get(Rating, id)
        session.delete(rating)
    session.commit()

def delete_user_rating(id: int):
    """
    id: database id, NOT userId
    """
    rating = session.get(Rating, id)
    session.delete(rating)
    session.commit()


if __name__=='__main__':
    # create_movie_table("ml-latest-small/movies.csv")
    # create_rating_table("ml-latest-small/ratings.csv")
    pass
