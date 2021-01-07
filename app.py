import os
from flask import Flask
from flask_cors import CORS
from models import setup_db

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def alive():
        return 'App is online'

    @app.route('/api/actors')
    def get_actors():
        return 'not implemented'

    @app.route('/api/movies')
    def get_movies():
        return 'not implemented'
    
    @app.route('/api/actors', methods=['POST'])
    def create_actor():
        return 'not implemented'
    
    @app.route('/api/movies', methods=['POST'])
    def create_movie():
        return 'not implemented'
    
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

    return app

app = create_app()

if __name__ == '__main__':
    app.run()