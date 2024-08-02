import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, registry
from sqlalchemy import insert

engine = create_engine('sqlite:///recsys.sqlite')

# From sqlalchemy Docs:
# Base: A class that links database tables with python classes
# MetaData: A collection of Table objects and their associated schema constructs
# The MetaData is accessed via the Base class
Base = declarative_base()
    
movie_table = Table('movie_table', Base.metadata,
                        Column('id', Integer, primary_key=True), 
                        Column('movieId', String),
                        Column('title', String), 
                        Column('genres', String))

rating_table = Table('rating_table', Base.metadata,
                        Column('id', Integer, primary_key=True), 
                        Column('userId', String),
                        Column('movieId', String), 
                        Column('rating', String))

def create_movie_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        stmt = insert(movie_table).values(movieId=row[0], title=row[1], genres=row[2])
        print(stmt)


def create_rating_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        stmt = insert(rating_table).values(userId=row[0], movieId=row[1], rating=row[2])
        print(stmt)


def insert_rating(userId, movieId, rating):
    stmt = insert(rating_table).values(userId=userId, movieId=movieId, rating=rating)
    print(stmt)
    compiled = stmt.compile()
    print(compiled.params)

create_movie_table("ml-latest-small/movies.csv")
create_rating_table("ml-latest-small/ratings.csv")
insert_rating("611","1","4.0")
