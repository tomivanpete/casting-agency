import unittest
from faker import Faker
import random
import json

from app import create_app
from models import db, setup_db, Actor, Movie

class CastingAgencyTestCase(unittest.TestCase):
    """Test Case for the Casting Agency API"""
    
    @classmethod
    def setUpClass(cls):
        """Creates a new Casting Agency Flask app and binds it to the test DB."""
        cls.app = create_app(test_config=True)
        cls.client = cls.app.test_client
        
        cls.database_name = 'casting-agency-test'
        cls.database_path = 'postgres://{}/{}'.format('localhost:5432', cls.database_name)
        setup_db(cls.app, cls.database_path)
        cls.create_test_data(cls)
    
    @classmethod
    def tearDownClass(cls):
        """Drops the test DB after executing all tests"""
        db.session.remove()
        db.drop_all()

    def setUp(self):
        """Not used since everything is covered in the setUpClass method."""
        pass
    
    def tearDown(self):
        """Not used since everything is covered in the tearDownClass method."""
        pass

    def create_test_data(self):
        """Creates new data for the test DB using the Faker library."""
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
    
    def test_get_actors(self):
        """Verifies the /api/actors endpoint returns a 200 and 10 Actor objects."""
        res = self.client().get('/api/actors')
        self.assertEqual(res.status_code, 200)
        
        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['actors']), 10)
        self.assertEqual(res_body['totalActors'], len(Actor.query.all()))

    def test_get_actor_detail(self):
        """Verifies the /api/actors/<actor_id> endpoint returns a 200 and correct attributes from the DB."""
        actor = random.choice(Actor.query.all())

        res = self.client().get('/api/actors/' + str(actor.id))
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['actor']['name'], actor.name)
        self.assertEqual(res_body['actor']['age'], actor.age)
        self.assertEqual(res_body['actor']['gender'], actor.gender)
        self.assertEqual(res_body['actor']['movies'], actor.movies)
    
    def test_get_movies(self):
        """Verifies the /api/movies endpoint returns a 200 and 10 Movie objects."""
        res = self.client().get('/api/movies')
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(len(res_body['movies']), 10)
        self.assertEqual(res_body['totalMovies'], len(Movie.query.all()))

    def test_get_movie_detail(self):
        """Verifies the /api/movies/<movie_id> endpoint returns a 200 and correct attributes from the DB."""
        movie = random.choice(Movie.query.all())

        res = self.client().get('/api/movies/' + str(movie.id))
        self.assertEqual(res.status_code, 200)

        res_body = json.loads(res.data)
        self.assertEqual(res_body['movie']['title'], movie.title)
        self.assertEqual(res_body['movie']['releaseDate'], str(movie.release_date))
        self.assertEqual(res_body['movie']['actors'], movie.actors)
    
    def test_create_actor(self):
        """Verifies the /api/actors endpoint returns a 201 for valid POST requests.
        
        Verifies DB attributes are consistent with the request body."""
        res = self.client().post('/api/actors', json=self.actor_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_actor_id = res_body['created']
        new_actor = Actor.query.get(new_actor_id)
        self.assertEqual(self.actor_request['name'], new_actor.name)
        self.assertEqual(self.actor_request['age'], new_actor.age)
        self.assertEqual(self.actor_request['gender'], new_actor.gender)
    
    def test_create_movie(self):
        """Verifies the /api/movies endpoint returns a 201 for valid POST requests.
        
        Verifies DB attributes are consistent with the request body."""
        res = self.client().post('/api/movies', json=self.movie_request)
        self.assertEqual(res.status_code, 201)

        res_body = json.loads(res.data)
        self.assertTrue(res_body['created'])

        new_movie_id = res_body['created']
        new_movie = Movie.query.get(new_movie_id)
        self.assertEqual(self.movie_request['title'], new_movie.title)
        self.assertEqual(self.movie_request['releaseDate'], str(new_movie.release_date))
    
    def test_update_actor(self):
        """Verifies the /api/actors/<actor_id> endpoint returns a 200 for valid PATCH requests.
        
        Verifies DB attributes are consistent with the request body."""
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.actor_update_request['movies'] = [movie_id]
        
        res = self.client().patch('/api/actors/' + str(actor_id), json=self.actor_update_request)
        self.assertEqual(res.status_code, 200)

        updated_actor = Actor.query.get(actor_id)
        movie = Movie.query.get(movie_id)
        self.assertTrue(movie in updated_actor.movies)
    
    def test_update_movie(self):
        """Verifies the /api/movies/<movie_id> endpoint returns a 200 for valid PATCH requests.
        
        Verifies DB attributes are consistent with the request body."""
        actor_id = random.choice(Actor.query.all()).id
        movie_id = random.choice(Movie.query.all()).id
        self.movie_update_request['actors'] = [actor_id]

        res = self.client().patch('/api/movies/' + str(movie_id), json=self.movie_update_request)
        self.assertEqual(res.status_code, 200)

        updated_movie = Movie.query.get(movie_id)
        actor = Actor.query.get(actor_id)
        self.assertTrue(actor in updated_movie.actors)
    
    def test_delete_actor(self):
        """Verifies the /api/actors/<actor_id> endpoint returns a 200 for valid DELETE requests.
        
        Verifies Actor is successfully deleted from the DB and associated Movies remain."""
        actor_to_delete = random.choice(Actor.query.all())
        movie_ids = [movie.id for movie in actor_to_delete.movies]

        res = self.client().delete('/api/actors/' + str(actor_to_delete.id))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Actor.query.get(actor_to_delete.id))

        for id in movie_ids:
            self.assertTrue(Movie.query.get(id))
    
    def test_delete_movie(self):
        """Verifies the /api/movies/<movie_id> endpoint returns a 200 for valid DELETE requests.
        
        Verifies Movie is successfully deleted from the DB and associated Actors remain."""
        movie_to_delete = random.choice(Movie.query.all())
        actor_ids = [actor.id for actor in movie_to_delete.actors]

        res = self.client().delete('/api/movies/' + str(movie_to_delete.id))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Movie.query.get(movie_to_delete.id))

        for id in actor_ids:
            self.assertTrue(Actor.query.get(id))

    def test_actors_post_400(self):
        """Verifies the /api/actors endpoint returns a 400 for invalid POST requests"""
        res = self.client().post('/api/actors', json={'name': 'should fail with 400'})
        self.assertEqual(res.status_code, 400)
    
    def test_movies_post_400(self):
        """Verifies the /api/movies endpoint returns a 400 for invalid POST requests"""
        res = self.client().post('/api/movies', json={'title': 'should fail with 400', 'releaseDate': 'not a date'})
        self.assertEqual(res.status_code, 400)
    
    def test_actors_405(self):
        """Verifies the /api/actors endpoint returns a 405 for PUT requests"""
        actor_id = random.choice(Actor.query.all()).id

        res = self.client().put('/api/actors/' + str(actor_id), json=self.actor_update_request)
        self.assertEqual(res.status_code, 405)

    def test_movies_405(self):
        """Verifies the /api/movies endpoint returns a 405 for PUT requests"""
        movie_id = random.choice(Movie.query.all()).id

        res = self.client().put('/api/movies/' + str(movie_id), json=self.movie_update_request)
        self.assertEqual(res.status_code, 405)

    def test_update_actors_422(self):
        """Verifies the /api/actors endpoint returns a 422 for a PATCH request containing Movie IDs which do not exist."""
        actor_id = random.choice(Actor.query.all()).id

        res = self.client().patch('/api/actors/' + str(actor_id), json={'movies': [9000]})
        self.assertEqual(res.status_code, 422)

    def test_update_movies_422(self):
        """Verifies the /api/movies endpoint returns a 422 for a PATCH request containing Actor IDs which do not exist."""
        movie_id = random.choice(Movie.query.all()).id

        res = self.client().patch('/api/movies/' + str(movie_id), json={'actors': [9000]})
        self.assertEqual(res.status_code, 422)

    def test_get_actors_404(self):
        """Verifies the /api/actors endpoint returns a 404 for a page value that does not exist."""
        res = self.client().get('/api/actors?page=9000')
        self.assertEqual(res.status_code, 404)

    def test_get_movies_404(self):
        """Verifies the /api/movies endpoint returns a 404 for a page value that does not exist."""
        res = self.client().get('/api/movies?page=9000')
        self.assertEqual(res.status_code, 404)

    def test_get_actor_404(self):
        """Verifies the /api/actors/<actor_id> endpoint returns a 404 for an actor_id that does not exist."""
        res = self.client().get('/api/actors/9000')
        self.assertEqual(res.status_code, 404)

    def test_get_movie_404(self):
        """Verifies the /api/movies/<movie_id> endpoint returns a 404 for a movie_id that does not exist."""
        res = self.client().get('/api/movies/9000')
        self.assertEqual(res.status_code, 404)    

if __name__ == '__main__':
    unittest.main(verbosity=2)