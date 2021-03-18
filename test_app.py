import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
import random

from app import create_app
from models import db, setup_db, Actor, Movie

"""
TODO: seed casting-agency-test DB with more test data, instead of empty DB
TODO: add more assertions to test methods
TODO: test pagination
"""
class CastingAgencyTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client
        cls.database_name = 'casting-agency-test'
        cls.database_path = 'postgres://{}/{}'.format('localhost:5432', cls.database_name)
        setup_db(cls.app, cls.database_path)
        cls.create_test_data(cls)

        cls.actor_request = {
            'name': 'Nicolas Cage',
            'age': 57,
            'gender': 'M'
        }

        cls.movie_request = {
            'title': 'The Wickerman',
            'releaseDate': '2006-09-01'
        }

        cls.actor_update_request = {
            'name': 'Cicolas Nage',
        }

        cls.movie_update_request = {
            'title': 'The Mickerwan',
        }
    
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def create_test_data(self):
        fake = Faker(['en_US', 'ja_JP', 'el_GR'])

        for _ in range(30):
            actor_name = fake.name()
            actor_age = random.randint(22, 88)
            actor_gender = random.choice(['M', 'F'])

            movie_title = fake.color_name() + ' ' + fake.street_suffix()
            movie_release_date = str(fake.date_between())

            actor = Actor(actor_name, actor_age, actor_gender)
            actor.insert()

            movie = Movie(movie_title, movie_release_date)
            movie.insert()
        
        for _ in range(20):
            actors = Actor.query.all()
            movies = Movie.query.all()

            actor_to_update = random.choice(actors)
            movie_to_update = random.choice(movies)
            actor_to_update.movies.append(movie_to_update)

    def test_get_actors(self):
        res = self.client().get('/api/actors')

        self.assertEqual(res.status_code, 200)

    def test_get_movies(self):
        res = self.client().get('/api/movies')

        self.assertEqual(res.status_code, 200)

    def test_create_actor(self):
        res = self.client().post('/api/actors', json=self.actor_request)

        self.assertEqual(res.status_code, 201)
    
    def test_create_movie(self):
        res = self.client().post('/api/movies', json=self.movie_request)

        self.assertEqual(res.status_code, 201)

    def test_update_actor(self):
        actor_id = Actor.query.first().id
        movie_id = Movie.query.first().id
        self.actor_update_request['movies'] = [movie_id]
        
        res = self.client().patch('/api/actors/' + str(actor_id), json=self.actor_update_request)

        self.assertEqual(res.status_code, 200)

    def test_update_movie(self):
        actor_id = Actor.query.first().id
        movie_id = Movie.query.first().id
        self.movie_update_request['actors'] = [actor_id]

        res = self.client().patch('/api/movies/' + str(movie_id), json=self.movie_update_request)

        self.assertEqual(res.status_code, 200)
    
    def test_delete_actor(self):
        actor_id = Actor.query.first().id
        res = self.client().delete('/api/actors/' + str(actor_id))

        self.assertEqual(res.status_code, 200)

    def test_delete_movie(self):
        movie_id = Movie.query.first().id
        res = self.client().delete('/api/movies/' + str(movie_id))

        self.assertEqual(res.status_code, 200)

    def test_movies_post_400(self):
        res = self.client().post('/api/movies', json={'title': 'should fail with 400', 'releaseDate': 'not a date'})

        self.assertEqual(res.status_code, 400)

    def test_actors_post_400(self):
        res = self.client().post('/api/actors', json={'test': 'should fail with 400'})

        self.assertEqual(res.status_code, 400)

    def test_actors_405(self):
        self.client().post('/api/actors', json=self.actor_request)
        res = self.client().put('/api/actors/1', json=self.actor_update_request)

        self.assertEqual(res.status_code, 405)

    def test_movies_405(self):
        self.client().post('/api/movies', json=self.movie_request)
        res = self.client().put('/api/movies/1', json=self.movie_update_request)

        self.assertEqual(res.status_code, 405)

if __name__ == '__main__':
    unittest.main()