from auth import get_token_auth_header
import unittest
from faker import Faker
import random
import json
import os

from sqlalchemy.sql.expression import update
from app import create_app
from models import db, setup_db, Actor, Movie

"""
DONE: seed casting-agency-test DB with more test data, instead of empty DB
TODO: add more assertions to test methods
TODO: test pagination
"""
class CastingAgencyTestCase(unittest.TestCase):
    """Test Case for the Casting Agency API"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client
        
        cls.database_name = 'casting-agency-test'
        cls.database_path = 'postgres://{}/{}'.format('localhost:5432', cls.database_name)
        setup_db(cls.app, cls.database_path)
        cls.create_test_data(cls)

        cls.assistant_headers = cls.get_auth_headers(cls, 'ASSISTANT_TOKEN')
        cls.director_headers = cls.get_auth_headers(cls, 'DIRECTOR_TOKEN')
        cls.producer_headers = cls.get_auth_headers(cls, 'PRODUCER_TOKEN')
    
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

        self.actor_request = {
            'name': fake.name(),
            'age': random.randint(22, 88),
            'gender': random.choice(['M', 'F'])
        }

        self.movie_request = {
            'title': fake.color_name() + ' ' + fake.street_suffix(),
            'releaseDate': str(fake.date_between())
        }

        self.actor_update_request = {
            'name': fake.name(),
        }

        self.movie_update_request = {
            'title': fake.color_name() + ' ' + fake.street_suffix(),
        }

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
    
    def get_auth_headers(self, token_name):
        token = os.getenv(token_name, default=None)

        return {'Authorization': 'Bearer ' + token}
    
    def test_get_actors(self):
        res = self.client().get('/api/actors', headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)
        
        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['actors']), 10)
        self.assertEqual(res_body['totalActors'], len(Actor.query.all()))

    def test_get_movies(self):
        res = self.client().get('/api/movies', headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['movies']), 10)
        self.assertEqual(res_body['totalMovies'], len(Movie.query.all()))

    def test_create_actor(self):
        res = self.client().post('/api/actors', headers=self.producer_headers, json=self.actor_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_actor_id = res_body['created']
        new_actor = Actor.query.get(new_actor_id)
        self.assertEqual(self.actor_request['name'], new_actor.name)
        self.assertEqual(self.actor_request['age'], new_actor.age)
        self.assertEqual(self.actor_request['gender'], new_actor.gender)
    
    def test_create_movie(self):
        res = self.client().post('/api/movies', headers=self.producer_headers, json=self.movie_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_movie_id = res_body['created']
        new_movie = Movie.query.get(new_movie_id)
        self.assertEqual(self.movie_request['title'], new_movie.title)
        self.assertEqual(self.movie_request['releaseDate'], str(new_movie.release_date))

    def test_update_actor(self):
        actor_id = Actor.query.first().id
        movie_id = Movie.query.first().id
        self.actor_update_request['movies'] = [movie_id]
        
        res = self.client().patch('/api/actors/' + str(actor_id), headers=self.producer_headers, json=self.actor_update_request)
        self.assertEqual(res.status_code, 200)

        updated_actor = Actor.query.get(actor_id)
        movie = Movie.query.get(movie_id)
        self.assertTrue(movie in updated_actor.movies)

    def test_update_movie(self):
        actor_id = Actor.query.first().id
        movie_id = Movie.query.first().id
        self.movie_update_request['actors'] = [actor_id]

        res = self.client().patch('/api/movies/' + str(movie_id), headers=self.producer_headers, json=self.movie_update_request)
        self.assertEqual(res.status_code, 200)

        updated_movie = Movie.query.get(movie_id)
        actor = Actor.query.get(actor_id)
        self.assertTrue(actor in updated_movie.actors)
    
    def test_delete_actor(self):
        actor_to_delete = Actor.query.first()
        movie_ids = [movie.id for movie in actor_to_delete.movies]

        res = self.client().delete('/api/actors/' + str(actor_to_delete.id), headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        for id in movie_ids:
            self.assertTrue(Movie.query.get(id))

    def test_delete_movie(self):
        movie_to_delete = Movie.query.first()
        actor_ids = [actor.id for actor in movie_to_delete.actors]

        res = self.client().delete('/api/movies/' + str(movie_to_delete.id), headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        for id in actor_ids:
            self.assertTrue(Actor.query.get(id))

    def test_movies_post_400(self):
        res = self.client().post('/api/movies', headers=self.producer_headers, json={'title': 'should fail with 400', 'releaseDate': 'not a date'})
        self.assertEqual(res.status_code, 400)

    def test_actors_post_400(self):
        res = self.client().post('/api/actors', headers=self.producer_headers, json={'test': 'should fail with 400'})
        self.assertEqual(res.status_code, 400)

    def test_actors_405(self):
        actor_id = Actor.query.first().id

        res = self.client().put('/api/actors/' + str(actor_id), headers=self.producer_headers, json=self.actor_update_request)
        self.assertEqual(res.status_code, 405)

    def test_movies_405(self):
        movie_id = Movie.query.first().id

        res = self.client().put('/api/movies/' + str(movie_id), headers=self.producer_headers, json=self.movie_update_request)
        self.assertEqual(res.status_code, 405)

    def test_update_actors_422(self):
        actor_id = Actor.query.first().id

        res = self.client().patch('/api/actors/' + str(actor_id), headers=self.producer_headers, json={'movies': [9000]})
        self.assertEqual(res.status_code, 422)

    def test_update_movies_422(self):
        movie_id = Movie.query.first().id

        res = self.client().patch('/api/movies/' + str(movie_id), headers=self.producer_headers, json={'actors': [9000]})
        self.assertEqual(res.status_code, 422)

    def test_get_actors_404(self):
        res = self.client().get('/api/actors?page=9000', headers=self.producer_headers)
        self.assertEqual(res.status_code, 404)

    def test_get_movies_404(self):
        res = self.client().get('/api/movies?page=9000', headers=self.producer_headers)
        self.assertEqual(res.status_code, 404)

    def test_get_actor_404(self):
        res = self.client().get('/api/actors/9000', headers=self.producer_headers)
        self.assertEqual(res.status_code, 404)

    def test_get_movie_404(self):
        res = self.client().get('/api/movies/9000', headers=self.producer_headers)
        self.assertEqual(res.status_code, 404)    

if __name__ == '__main__':
    unittest.main()