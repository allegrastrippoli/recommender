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


def fetch_movie_image(title):
    url = f'http://www.omdbapi.com/?apikey={api_key}&t={title}'
    response = requests.get(url)
    data = response.json()
    return data.get('Poster')

def remove_year_from_title(title):
    pattern = r'\s*\(\d{4}\)'
    title = re.sub(pattern, '', title)
    return title.strip()

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


def update_csv(userId: int, selected_movies: list, rating: str):
    with open('ml-latest-small/ratings.csv', 'a', newline='') as csvfile_out:
        writer = csv.writer(csvfile_out)
    
        for movieId in selected_movies:
            row = [userId, movieId, rating, "None"]
            writer.writerow(row)

def update_db(userId: int, selected_movies: list, rating: str):
    for movieId in selected_movies:
        print('Adding ratings to the current session...')
        newrating = Rating(userId=userId, movieId=int(movieId), rating=rating)
        session.add(newrating)
    session.commit()

def insert_rating(userId: int, selected_movies: list, rating: str):
    # TODO: remove csv pls
    update_csv(userId, selected_movies, rating)
    update_db(userId, selected_movies, rating)

def select_random_movies():
    stmt = select(Movie).order_by(func.random()).limit(20)
    result = session.execute(stmt).scalars().all()
    return result

def select_user(userId: Integer):
    stmt = select(Rating).where(Rating.userId == userId)
    for _ in session.execute(stmt):
        return True
    return False


if __name__=='__main__':
    create_movie_table("ml-latest-small/movies.csv")
    create_rating_table("ml-latest-small/ratings.csv")

