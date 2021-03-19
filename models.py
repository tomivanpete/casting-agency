from sqlalchemy import Column, String, Integer, Date, Enum
from flask_sqlalchemy import SQLAlchemy

database_name = "casting-agency"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)
#database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()

movie_actors = db.Table('movie_actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id', ondelete='CASCADE'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id', ondelete='CASCADE'), primary_key=True)
)

class Movie(db.Model):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    actors = db.relationship('Actor', secondary=movie_actors, back_populates='movies', cascade='all, delete', passive_deletes=True)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date
    
    def get_data(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': str(self.release_date)
        }
    
    def get_data_with_actors(self):
        formatted_actors = [actor.get_data() for actor in self.actors]
        
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
            'actors': formatted_actors
        }
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


"""
TODO: update gender enum for transgender, non-binary
"""
class Actor(db.Model):
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
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }
    
    def get_data_with_movies(self):
        formatted_movies = [movie.get_data() for movie in self.movies]

        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'movies': formatted_movies
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

