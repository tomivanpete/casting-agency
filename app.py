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

    return app

app = create_app()

if __name__ == '__main__':
    app.run()