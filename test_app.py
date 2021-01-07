import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db

class CastingAgencyTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'casting-agency-test'
        self.database_path = 'postgres://{}/{}'.format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    def tearDown(self):
        pass

    def test_get_actors(self):
        res = self.client().get('/api/actors')

        self.assertEqual(res.status_code, 200)

    def test_get_movies(self):
        res = self.client().get('/api/movies')

        self.assertEqual(res.status_code, 200)

    def test_create_actor(self):
        res = self.client().post('/api/actors', json={'test': 1})

        self.assertEqual(res.status_code, 200)
    
    def test_create_movie(self):
        res = self.client().post('/api/movies', json={'test': 1})

        self.assertEqual(res.status_code, 200)

    def test_update_actor(self):
        res = self.client().patch('/api/actors/1', json={'test': 1})

        self.assertEqual(res.status_code, 200)

    def test_update_movie(self):
        res = self.client().patch('/api/movies/1', json={'test': 1})

        self.assertEqual(res.status_code, 200)
    
    def test_delete_actor(self):
        res = self.client().delete('/api/actors/1')

        self.assertEqual(res.status_code, 200)

    def test_delete_movie(self):
        res = self.client().delete('/api/movies/1')

        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()