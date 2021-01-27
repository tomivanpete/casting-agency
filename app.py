import os, sys
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from models import setup_db, Movie, Actor

ITEMS_PER_PAGE = 10

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
        # Return a 400 error if any required fields are not present in the
        # request body
        except KeyError:
            abort(400)
        except BaseException:
            abort(500)
    
    @app.route('/api/movies', methods=['POST'])
    def create_movie():
        try:
            request_body = request.get_json()
            title = request_body['title']
            release_date = request_body['release_date']

            new_movie = Movie(
                title=title,
                release_date=release_date
            )
            new_movie.insert()

            return jsonify({
                'success': True,
                'created': new_movie.id
            }), 201
        # Return a 400 error if any required fields are not present in the
        # request body
        except KeyError:
            abort(400)
        except BaseException:
            abort(500)
    
    @app.route('/api/actors/<int:actor_id>', methods=['PATCH'])
    def update_actor(actor_id):
        return 'not implemented'
    
    @app.route('/api/movies/<int:movie_id>', methods=['PATCH'])
    def update_movie(movie_id):
        return 'not implemented'
    
    @app.route('/api/actors/<int:actor_id>', methods=['DELETE'])
    def delete_actor(actor_id):
        return 'not implemented'

    @app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
        return 'not implemented'

    @app.errorhandler(400)
    def bad_request(error):
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