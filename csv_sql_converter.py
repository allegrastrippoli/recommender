import pandas as pd
from sqlalchemy.sql.expression import func
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select

engine = create_engine('sqlite:///recsys.sqlite')
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
    
    def __init__(self, movieId, title, genres):
        self.movieId = movieId
        self.title = title
        self.genres = genres
    
    def __repr__(self):
        return f'{self.movieId, self.title, self.genres}'
    
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


def create_movie_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        movie = Movie(movieId=row[0], title=row[1], genres=row[2])
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

def insert_rating(userId, movieId, rating):
    rating = Rating(userId=userId, movieId=movieId, rating=rating)
    session.add(rating)
    session.commit()

def select_random_movies():
    stmt = select(Movie).order_by(func.random()).limit(20)
    result = session.execute(stmt).scalars().all()
    return result

def select_user(userId: Integer):
    stmt = select(Rating).where(Rating.userId == userId)
    for _ in session.execute(stmt):
        return True
    return False

# create_movie_table("ml-latest-small/movies.csv")
# create_rating_table("ml-latest-small/ratings.csv")

if __name__=='__main__':
    pass
