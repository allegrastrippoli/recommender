import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, registry

engine = create_engine('sqlite:///movies.sqlite')
Session = sessionmaker(bind=engine)
session = Session()

# Map which table in database will be related to each class
Base = declarative_base()

# A metadata is an object container that will store attributes and name of table 
metadata = MetaData()

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

def create_table(filepath):
    csv_data = pd.read_csv(filepath)
    csv_data = csv_data.values.tolist()
    
    Base.metadata.create_all(engine)
    
    for row in csv_data:
        movie = MovieTable(movieId=row[0], title=row[1], genres=row[2])
        session.add(movie)
    
    session.commit()

create_table("ml-latest-small/movies.csv")
