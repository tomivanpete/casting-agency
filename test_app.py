import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import db, setup_db

"""
TODO: seed casting-agency-test DB with more test data, instead of empty DB
TODO: add more assertions to test methods
TODO: test pagination
"""
class CastingAgencyTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'casting-agency-test'
        self.database_path = 'postgres://{}/{}'.format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.actor_request = {
            'name': 'Nicolas Cage',
            'age': 57,
            'gender': 'M'
        }

        self.movie_request = {
            'title': 'The Wickerman',
            'releaseDate': '2006-09-01'
        }

        self.actor_update_request = {
            'name': 'Cicolas Nage',
            'movies': [1]
        }

        self.movie_update_request = {
            'title': 'The Mickerwan',
            'actors': [1]
        }
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
        self.client().post('/api/actors', json=self.actor_request)
        self.client().post('/api/movies', json=self.movie_request)
        res = self.client().patch('/api/actors/1', json=self.actor_update_request)

        self.assertEqual(res.status_code, 200)

    def test_update_movie(self):
        self.client().post('/api/actors', json=self.actor_request)
        self.client().post('/api/movies', json=self.movie_request)
        res = self.client().patch('/api/movies/1', json=self.movie_update_request)

        self.assertEqual(res.status_code, 200)
    
    def test_delete_actor(self):
        self.client().post('/api/actors', json=self.actor_request)
        res = self.client().delete('/api/actors/1')

        self.assertEqual(res.status_code, 200)

    def test_delete_movie(self):
        self.client().post('/api/movies', json=self.movie_request)
        res = self.client().delete('/api/movies/1')

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