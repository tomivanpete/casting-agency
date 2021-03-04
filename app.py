import os, sys, json
from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from flask_expects_json import expects_json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from models import setup_db, Movie, Actor
from util import get_schemas, schema_validator

ITEMS_PER_PAGE = 10
SCHEMAS = get_schemas()

"""
TODO: implement authentication and permission checks
"""
def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def alive():
        return 'App is online'

    @app.route('/api/actors')
    def get_actors():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * ITEMS_PER_PAGE
            end = start + ITEMS_PER_PAGE
            
            actors = Actor.query.all()
            formatted_actors = [actor.get_data() for actor in actors]
            if start > len(formatted_actors):
                raise IndexError

            return jsonify({
                'success': True,
                'actors': formatted_actors
            })
        except IndexError:
            abort(404)
        except BaseException:
            abort(500)


    @app.route('/api/movies')
    def get_movies():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * ITEMS_PER_PAGE
            end = start + ITEMS_PER_PAGE
            
            movies = Movie.query.all()
            formatted_movies = [movie.get_data() for movie in movies]
            if start > len(formatted_movies):
                raise IndexError

            return jsonify({
                'success': True,
                'movies': formatted_movies
            })
        except IndexError:
            abort(404)
        except BaseException:
            abort(500)
    
    @app.route('/api/actors/<int:actor_id>')
    def get_actor(actor_id):
        try:
            actor = Actor.query.get(actor_id)

            # Will raise AttributeError if Actor with actor_id does not exist
            return jsonify({
                'success': True,
                'actor': actor.get_data_with_movies()
            })
        except AttributeError:
            abort(404)
        except BaseException:
            abort(500)

    
    @app.route('/api/movies/<int:movie_id>')
    def get_movie(movie_id):
        try:
            movie = Movie.query.get(movie_id)

            #  Will raise AttributeError if Movie with movie_id does not exist
            return jsonify({
                'success': True,
                'movie': movie.get_data_with_actors()
            })
        except AttributeError:
            abort(404)
        except BaseException:
            abort(500)
    
    @app.route('/api/actors', methods=['POST'])
    @schema_validator(schema=SCHEMAS['post_actor'])
    def create_actor():
        try:
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
        except BaseException:
            abort(500)
    
    @app.route('/api/movies', methods=['POST'])
    @schema_validator(schema=SCHEMAS['post_movie'])
    def create_movie():
        try:
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
        except ValidationError:
            abort(400)
        except BaseException:
            abort(500)
    
    @app.route('/api/actors/<int:actor_id>', methods=['PATCH'])
    @schema_validator(schema=SCHEMAS['patch_actor'])
    def update_actor(actor_id):
        actor_to_update = Actor.query.get(actor_id)
        if actor_to_update is None:
            abort(404)

        request_body = request.get_json()
        name = request_body.get('name', None)
        age = request_body.get('age', None)
        gender = request_body.get('gender', None)
        movie_ids = request_body.get('movies', None)

        # Accept update for name, age, or gender in the message body
        if name:
            actor_to_update.name = name
        if age:
            actor_to_update.age = age
        if gender:
            actor_to_update.gender = gender
        if movie_ids:
            movies = [Movie.query.get(id) for id in movie_ids]
            actor_to_update.movies = movies            

        actor_to_update.update()

        return jsonify({
            'success': True,
            'actor': actor_to_update.get_data_with_movies()
        })
    
    @app.route('/api/movies/<int:movie_id>', methods=['PATCH'])
    @schema_validator(schema=SCHEMAS['patch_movie'])
    def update_movie(movie_id):
        movie_to_update = Movie.query.get(movie_id)
        if movie_to_update is None:
            abort(404)

        request_body = request.get_json()
        title = request_body.get('title', None)
        release_date = request_body.get('release_date', None)
        actor_ids = request_body.get('actors', None)

        # Accept update for title or release date in the message body
        if title:
            movie_to_update.title = title
        if release_date:
            movie_to_update.release_date = release_date
        if actor_ids:
            actors = [Actor.query.get(id) for id in actor_ids]
            movie_to_update.actors = actors

        movie_to_update.update()

        return jsonify({
            'success': True,
            'movie': movie_to_update.get_data()
        })
    
    @app.route('/api/actors/<int:actor_id>', methods=['DELETE'])
    def delete_actor(actor_id):
        try:
            actor = Actor.query.get(actor_id)
            actor.delete()

            return jsonify({
                'success': True,
                'deleted': actor_id
            })
        except BaseException:
            abort(404)

    @app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
        try:
            movie = Movie.query.get(movie_id)
            movie.delete()

            return jsonify({
                'success': True,
                'deleted': movie_id
            })
        except BaseException:
            abort(404)

    @app.errorhandler(ValidationError)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': error.message
        }), 400

    @app.errorhandler(400)
    def generic_bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
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