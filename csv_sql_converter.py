import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, registry

engine = create_engine('sqlite:///recsys.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

# from sqlalchemy Docs:
# Base: A class that links database tables with python classes
# MetaData: A collection of Table objects and their associated schema constructs
# the MetaData is accessed via the Base class
Base = declarative_base()

class MovieTable(Base):
    __tablename__ = 'movie_table'
    
    id = Column(Integer, primary_key=True)
    movieId = Column(String)
    title = Column(String)
    genres = Column(String)
    
    def __init__(self, movieId, title, genres):
        self.movieId = movieId
        self.title = title
        self.genres = genres
    
    def __repr__(self):
        return f'{self.movieId, self.title, self.genres}'
    
class RatingTable(Base): # userId,movieId,rating,
    __tablename__ = 'rating_table'
    
    id = Column(Integer, primary_key=True)
    userId = Column(String)
    movieId = Column(String)
    rating = Column(String)
    
    def __init__(self, userId, movieId, rating):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
    
    def __repr__(self):
        return f'{self.rating, self.movieId, self.rating}'


def create_movie_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        movie = MovieTable(movieId=row[0], title=row[1], genres=row[2])
        session.add(movie)
    
    session.commit()

def create_rating_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        rating = MovieTable(movieId=row[0], title=row[1], genres=row[2])
        session.add(rating)
    
    session.commit()

create_movie_table("ml-latest-small/movies.csv")
create_rating_table("ml-latest-small/ratings.csv")
