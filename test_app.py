import unittest
from faker import Faker
import random
import json
import os

from sqlalchemy.sql.expression import update
from app import create_app
from models import db, setup_db, Actor, Movie

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
    
    def test_get_actors_assistant(self):
        res = self.client().get('/api/actors', headers=self.assistant_headers)
        self.assertEqual(res.status_code, 200)
        
        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['actors']), 10)
        self.assertEqual(res_body['totalActors'], len(Actor.query.all()))

    def test_get_actors_director(self):
        res = self.client().get('/api/actors', headers=self.director_headers)
        self.assertEqual(res.status_code, 200)
        
        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['actors']), 10)
        self.assertEqual(res_body['totalActors'], len(Actor.query.all()))
    
    def test_get_actors_producer(self):
        res = self.client().get('/api/actors', headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)
        
        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['actors']), 10)
        self.assertEqual(res_body['totalActors'], len(Actor.query.all()))

    def test_get_actor_detail_assistant(self):
        actor = random.choice(Actor.query.all())

        res = self.client().get('/api/actors/' + str(actor.id), headers=self.assistant_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['actor']['name'], actor.name)
        self.assertEqual(res_body['actor']['age'], actor.age)
        self.assertEqual(res_body['actor']['gender'], actor.gender)
        self.assertEqual(res_body['actor']['movies'], actor.movies)
    
    def test_get_actor_detail_director(self):
        actor = random.choice(Actor.query.all())

        res = self.client().get('/api/actors/' + str(actor.id), headers=self.director_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['actor']['name'], actor.name)
        self.assertEqual(res_body['actor']['age'], actor.age)
        self.assertEqual(res_body['actor']['gender'], actor.gender)
        self.assertEqual(res_body['actor']['movies'], actor.movies)

    def test_get_actor_detail_producer(self):
        actor = random.choice(Actor.query.all())

        res = self.client().get('/api/actors/' + str(actor.id), headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['actor']['name'], actor.name)
        self.assertEqual(res_body['actor']['age'], actor.age)
        self.assertEqual(res_body['actor']['gender'], actor.gender)
        self.assertEqual(res_body['actor']['movies'], actor.movies)
    
    def test_get_movies_assistant(self):
        res = self.client().get('/api/movies', headers=self.assistant_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['movies']), 10)
        self.assertEqual(res_body['totalMovies'], len(Movie.query.all()))
    
    def test_get_movies_director(self):
        res = self.client().get('/api/movies', headers=self.director_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['movies']), 10)
        self.assertEqual(res_body['totalMovies'], len(Movie.query.all()))
    
    def test_get_movies_producer(self):
        res = self.client().get('/api/movies', headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['movies']), 10)
        self.assertEqual(res_body['totalMovies'], len(Movie.query.all()))

    def test_get_movie_detail_assistant(self):
        movie = random.choice(Movie.query.all())

        res = self.client().get('/api/movies/' + str(movie.id), headers=self.assistant_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['movie']['title'], movie.title)
        self.assertEqual(res_body['movie']['releaseDate'], str(movie.release_date))
        self.assertEqual(res_body['movie']['actors'], movie.actors)

    def test_get_movie_detail_director(self):
        movie = random.choice(Movie.query.all())

        res = self.client().get('/api/movies/' + str(movie.id), headers=self.director_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['movie']['title'], movie.title)
        self.assertEqual(res_body['movie']['releaseDate'], str(movie.release_date))
        self.assertEqual(res_body['movie']['actors'], movie.actors)

    def test_get_movie_detail_producer(self):
        movie = random.choice(Movie.query.all())

        res = self.client().get('/api/movies/' + str(movie.id), headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['movie']['title'], movie.title)
        self.assertEqual(res_body['movie']['releaseDate'], str(movie.release_date))
        self.assertEqual(res_body['movie']['actors'], movie.actors)

    def test_create_actor_assistant(self):
        res = self.client().post('/api/actors', headers=self.assistant_headers, json=self.actor_request)
        self.assertEqual(res.status_code, 403)
    
    def test_create_actor_director(self):
        res = self.client().post('/api/actors', headers=self.director_headers, json=self.actor_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_actor_id = res_body['created']
        new_actor = Actor.query.get(new_actor_id)
        self.assertEqual(self.actor_request['name'], new_actor.name)
        self.assertEqual(self.actor_request['age'], new_actor.age)
        self.assertEqual(self.actor_request['gender'], new_actor.gender)
    
    def test_create_actor_producer(self):
        res = self.client().post('/api/actors', headers=self.producer_headers, json=self.actor_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_actor_id = res_body['created']
        new_actor = Actor.query.get(new_actor_id)
        self.assertEqual(self.actor_request['name'], new_actor.name)
        self.assertEqual(self.actor_request['age'], new_actor.age)
        self.assertEqual(self.actor_request['gender'], new_actor.gender)
    
    def test_create_movie_assistant(self):
        res = self.client().post('/api/movies', headers=self.assistant_headers, json=self.movie_request)
        self.assertEqual(res.status_code, 403)
    
    def test_create_movie_director(self):
        res = self.client().post('/api/movies', headers=self.director_headers, json=self.movie_request)
        self.assertEqual(res.status_code, 403)
    
    def test_create_movie_producer(self):
        res = self.client().post('/api/movies', headers=self.producer_headers, json=self.movie_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_movie_id = res_body['created']
        new_movie = Movie.query.get(new_movie_id)
        self.assertEqual(self.movie_request['title'], new_movie.title)
        self.assertEqual(self.movie_request['releaseDate'], str(new_movie.release_date))

    def test_update_actor_assistant(self):
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.actor_update_request['movies'] = [movie_id]
        
        res = self.client().patch('/api/actors/' + str(actor_id), headers=self.assistant_headers, json=self.actor_update_request)
        self.assertEqual(res.status_code, 403)
    
    def test_update_actor_director(self):
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.actor_update_request['movies'] = [movie_id]
        
        res = self.client().patch('/api/actors/' + str(actor_id), headers=self.director_headers, json=self.actor_update_request)
        self.assertEqual(res.status_code, 200)

        updated_actor = Actor.query.get(actor_id)
        movie = Movie.query.get(movie_id)
        self.assertTrue(movie in updated_actor.movies)
    
    def test_update_actor_producer(self):
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.actor_update_request['movies'] = [movie_id]
        
        res = self.client().patch('/api/actors/' + str(actor_id), headers=self.producer_headers, json=self.actor_update_request)
        self.assertEqual(res.status_code, 200)

        updated_actor = Actor.query.get(actor_id)
        movie = Movie.query.get(movie_id)
        self.assertTrue(movie in updated_actor.movies)

    def test_update_movie_assistant(self):
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.movie_update_request['actors'] = [actor_id]

        res = self.client().patch('/api/movies/' + str(movie_id), headers=self.assistant_headers, json=self.movie_update_request)
        self.assertEqual(res.status_code, 403)
    
    def test_update_movie_director(self):
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.movie_update_request['actors'] = [actor_id]

        res = self.client().patch('/api/movies/' + str(movie_id), headers=self.director_headers, json=self.movie_update_request)
        self.assertEqual(res.status_code, 200)

        updated_movie = Movie.query.get(movie_id)
        actor = Actor.query.get(actor_id)
        self.assertTrue(actor in updated_movie.actors)
    
    def test_update_movie_producer(self):
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.movie_update_request['actors'] = [actor_id]

        res = self.client().patch('/api/movies/' + str(movie_id), headers=self.producer_headers, json=self.movie_update_request)
        self.assertEqual(res.status_code, 200)

        updated_movie = Movie.query.get(movie_id)
        actor = Actor.query.get(actor_id)
        self.assertTrue(actor in updated_movie.actors)
    
    def test_delete_actor_assistant(self):
        actor_to_delete = random.choice(Actor.query.all())
        movie_ids = [movie.id for movie in actor_to_delete.movies]

        res = self.client().delete('/api/actors/' + str(actor_to_delete.id), headers=self.assistant_headers)
        self.assertEqual(res.status_code, 403)
    
    def test_delete_actor_director(self):
        actor_to_delete = random.choice(Actor.query.all())
        movie_ids = [movie.id for movie in actor_to_delete.movies]

        res = self.client().delete('/api/actors/' + str(actor_to_delete.id), headers=self.director_headers)
        self.assertEqual(res.status_code, 200)

        for id in movie_ids:
            self.assertTrue(Movie.query.get(id))
    
    def test_delete_actor_producer(self):
        actor_to_delete = random.choice(Actor.query.all())
        movie_ids = [movie.id for movie in actor_to_delete.movies]

        res = self.client().delete('/api/actors/' + str(actor_to_delete.id), headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        for id in movie_ids:
            self.assertTrue(Movie.query.get(id))

    def test_delete_movie_assistant(self):
        movie_to_delete = random.choice(Movie.query.all())

        res = self.client().delete('/api/movies/' + str(movie_to_delete.id), headers=self.assistant_headers)
        self.assertEqual(res.status_code, 403)
    
    def test_delete_movie_director(self):
        movie_to_delete = random.choice(Movie.query.all())

        res = self.client().delete('/api/movies/' + str(movie_to_delete.id), headers=self.director_headers)
        self.assertEqual(res.status_code, 403)
    
    def test_delete_movie_producer(self):
        movie_to_delete = random.choice(Movie.query.all())
        actor_ids = [actor.id for actor in movie_to_delete.actors]

        res = self.client().delete('/api/movies/' + str(movie_to_delete.id), headers=self.producer_headers)
        self.assertEqual(res.status_code, 200)

        for id in actor_ids:
            self.assertTrue(Actor.query.get(id))

    def test_movies_post_400(self):
        res = self.client().post('/api/movies', headers=self.producer_headers, json={'title': 'should fail with 400', 'releaseDate': 'not a date'})
        self.assertEqual(res.status_code, 400)

    def test_actors_post_400(self):
        res = self.client().post('/api/actors', headers=self.producer_headers, json={'name': 'should fail with 400'})
        self.assertEqual(res.status_code, 400)

    def test_get_actors_401(self):
        res = self.client().get('/api/actors')
        self.assertEqual(res.status_code, 401)

    def test_get_movies_401(self):
        res = self.client().get('/api/movies')
        self.assertEqual(res.status_code, 401)
    
    def test_actors_405(self):
        actor_id = random.choice(Actor.query.all()).id

        res = self.client().put('/api/actors/' + str(actor_id), headers=self.producer_headers, json=self.actor_update_request)
        self.assertEqual(res.status_code, 405)

    def test_movies_405(self):
        movie_id = random.choice(Movie.query.all()).id

        res = self.client().put('/api/movies/' + str(movie_id), headers=self.producer_headers, json=self.movie_update_request)
        self.assertEqual(res.status_code, 405)

    def test_update_actors_422(self):
        actor_id = random.choice(Actor.query.all()).id

        res = self.client().patch('/api/actors/' + str(actor_id), headers=self.producer_headers, json={'movies': [9000]})
        self.assertEqual(res.status_code, 422)

    def test_update_movies_422(self):
        movie_id = random.choice(Movie.query.all()).id

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