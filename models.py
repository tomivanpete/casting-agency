from sqlalchemy import Column, String, Integer, Date, Enum
from flask_sqlalchemy import SQLAlchemy

database_name = "casting-agency"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)
#database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    """Binds a Flask App and a SQLAlchemy service"""
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()

"""Creates a many-to-many association for Movies and Actors"""
movie_actors = db.Table('movie_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id', ondelete='CASCADE'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), primary_key=True)
)

class Movie(db.Model):
    """A class to represent a Movie

    Attributes:
        id: Primary key in the DB
        title: The title of the Movie
        release_date: The release date of the Movie
        actors: A list of actors associated to the Movie
    """
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    actors = db.relationship('Actor', secondary=movie_actors, back_populates='movies', cascade='all, delete', passive_deletes=True)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date
    
    def get_data(self):
        """Returns a dictionary representation of the Movie"""
        return {
            'id': self.id,
            'title': self.title,
            'releaseDate': str(self.release_date)
        }
    
    def get_data_with_actors(self):
        """Returns a dictionary representation of the Movie with associated Actors"""
        formatted_actors = [actor.get_data() for actor in self.actors]
        
        return {
            'id': self.id,
            'title': self.title,
            'releaseDate': str(self.release_date),
            'actors': formatted_actors
        }
        
    def insert(self):
        """Inserts the Movie into the DB"""
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        """Updates the DB with the current representation of the Movie"""
        db.session.commit()

    def delete(self):
        """Deletes the Movie from the DB"""
        db.session.delete(self)
        db.session.commit()


class Actor(db.Model):
    """A class to represent an Actor

    Attributes:
        id: Primary key in the DB
        name: The name of the Actor
        age: The age of the Actor in years
        gender: The gender of the Actor, 'M' or 'F'
        movies: A list of Movies associated to the Actor
    """
    __tablename__ = 'actor'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum('M', 'F', name='gender_types'))
    movies = db.relationship('Movie', secondary=movie_actors, back_populates='actors', cascade='all, delete', passive_deletes=True)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender
    
    def get_data(self):
        """Returns a dictionary representation of the Actor"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }
    
    def get_data_with_movies(self):
        """Returns a dictionary representation of the Actor with associated Movies"""
        formatted_movies = [movie.get_data() for movie in self.movies]

        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'movies': formatted_movies
        }

    def insert(self):
        """Inserts the Actor into the DB"""
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        """Updates the DB with the current representation of the Actor"""
        db.session.commit()

    def delete(self):
        """Deletes the Actor from the DB"""
        db.session.delete(self)
        db.session.commit()
