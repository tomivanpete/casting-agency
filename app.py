import sys
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from jsonschema.exceptions import ValidationError

from models import setup_db, Movie, Actor
from schema_utils import get_schemas, schema_validator
from auth import AuthError, requires_auth

ITEMS_PER_PAGE = 10
SCHEMAS = get_schemas()

def create_app(test_config=None):
    """Flask App for the Casting Agency API"""
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def alive():
        return 'App is online'

    @app.route('/api/actors')
    @requires_auth('get:actors')
    def get_actors(payload):
        """Returns all Actors in the DB with 10 per page"""
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        
        actors = Actor.query.all()
        formatted_actors = [actor.get_data() for actor in actors]
        if start > len(formatted_actors):
            abort(404)

        return jsonify({
            'success': True,
            'actors': formatted_actors[start:end],
            'totalActors': len(formatted_actors)
        })


    @app.route('/api/movies')
    @requires_auth('get:movies')
    def get_movies(payload):
        """Returns all Movies in the DB with 10 per page"""
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        
        movies = Movie.query.all()
        formatted_movies = [movie.get_data() for movie in movies]
        if start > len(formatted_movies):
            abort(404)

        return jsonify({
            'success': True,
            'movies': formatted_movies[start:end],
            'totalMovies': len(formatted_movies)
        })
    
    @app.route('/api/actors/<int:actor_id>')
    @requires_auth('get:actor-detail')
    def get_actor(payload, actor_id):
        """Returns an Actor with actor_id and the associated Movies"""
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)

        return jsonify({
            'success': True,
            'actor': actor.get_data_with_movies()
        })

    
    @app.route('/api/movies/<int:movie_id>')
    @requires_auth('get:movie-detail')
    def get_movie(payload, movie_id):
        """Returns a Movie with movie_id and the associated actors"""
        movie = Movie.query.get(movie_id)
        if movie is None:
            abort(404)

        return jsonify({
            'success': True,
            'movie': movie.get_data_with_actors()
        })
    
    @app.route('/api/actors', methods=['POST'])
    @requires_auth('post:actors')
    @schema_validator(schema=SCHEMAS['post_actor'])
    def create_actor(payload):
        """Creates a new Actor in the DB 
        
        Raises a ValidationError and returns a 400 status code if
        JSON request body does not conform to post_actor.json schema
        """
        request_body = request.get_json()
        name = request_body['name']
        age = request_body['age']
        gender = request_body['gender']

        new_actor = Actor(
            name=name,
            age=age,
            gender=gender
        )
        new_actor.insert()

        return jsonify({
            'success': True,
            'created': new_actor.id
        }), 201
    
    @app.route('/api/movies', methods=['POST'])
    @requires_auth('post:movies')
    @schema_validator(schema=SCHEMAS['post_movie'])
    def create_movie(payload):
        """Creates a new Movie in the DB
        
        Raises a ValidationError and returns a 400 status code if
        JSON request body does not conform to post_movie.json schema
        """
        request_body = request.get_json()
        title = request_body['title']
        release_date = request_body['releaseDate']

        new_movie = Movie(
            title=title,
            release_date=release_date
        )
        new_movie.insert()

        return jsonify({
            'success': True,
            'created': new_movie.id
        }), 201
    
    @app.route('/api/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    @schema_validator(schema=SCHEMAS['patch_actor'])
    def update_actor(payload, actor_id):
        """Updates an existing Actor with actor_id
        
        Raises a ValidationError and returns a 400 status code if
        JSON request body does not conform to patch_actor.json schema
        """
        actor_to_update = Actor.query.get(actor_id)
        if actor_to_update is None:
            abort(404)

        request_body = request.get_json()
        name = request_body.get('name', None)
        age = request_body.get('age', None)
        gender = request_body.get('gender', None)
        movie_ids = request_body.get('movies', None)

        # Accept update for name, age, gender, or movies in the message body
        if name:
            actor_to_update.name = name
        if age:
            actor_to_update.age = age
        if gender:
            actor_to_update.gender = gender
        if movie_ids:
            movies = []
            for id in movie_ids:
                movie = Movie.query.get(id)
                if movie is not None:
                    movies.append(movie)
            if len(movies) > 0:
                actor_to_update.movies = movies
            else:
                abort(422)

        actor_to_update.update()

        return jsonify({
            'success': True,
            'actor': actor_to_update.get_data_with_movies()
        })
    
    @app.route('/api/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    @schema_validator(schema=SCHEMAS['patch_movie'])
    def update_movie(payload, movie_id):
        """Updates an existing Movie with movie_id
        
        Raises a ValidationError and returns a 400 status code if
        JSON request body does not conform to patch_movie.json schema
        """
        movie_to_update = Movie.query.get(movie_id)
        if movie_to_update is None:
            abort(404)

        request_body = request.get_json()
        title = request_body.get('title', None)
        release_date = request_body.get('releaseDate', None)
        actor_ids = request_body.get('actors', None)

        # Accept update for title, release date, or movies in the message body
        if title:
            movie_to_update.title = title
        if release_date:
            movie_to_update.release_date = release_date
        if actor_ids:
            actors = []
            for id in actor_ids:
                actor = Actor.query.get(id)
                if actor is not None:
                    actors.append(actor)
            if len(actors) > 0:
                movie_to_update.actors = actors
            else:
                abort(422)

        movie_to_update.update()

        return jsonify({
            'success': True,
            'movie': movie_to_update.get_data()
        })
    
    @app.route('/api/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        """Deletes an Actor with actor_id from the DB"""
        actor = Actor.query.get(actor_id)
        if actor is None:
            abort(404)

        actor.delete()

        return jsonify({
            'success': True,
            'deleted': actor_id
        })

    @app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        """Deletes a Movie with movie_id from the DB"""
        movie = Movie.query.get(movie_id)
        if movie is None:
            abort(404)
        
        movie.delete()

        return jsonify({
            'success': True,
            'deleted': movie_id
        })

    @app.errorhandler(AuthError)
    def auth_error(auth_error):
        """Handles AuthErrors raised when parsing the Auth0 JWT"""
        return jsonify({
            'success': False,
            'error': auth_error.status_code,
            'message': auth_error.error['description']
        }), auth_error.status_code
    
    @app.errorhandler(ValidationError)
    def bad_request(error):
        """Handles ValidationErrors raised when validating the POST and PATCH schemas"""
        return jsonify({
            'success': False,
            'error': 400,
            'message': error.message
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """Handles errors for resources not found in the app"""
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handles errors for request methods not allowed"""
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handles errors for valid request body that cannot be processed"""
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        """Handles all other app exceptions"""
        print(sys.exc_info())
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run()