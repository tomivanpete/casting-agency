from flask import Flask, request, redirect, jsonify, abort
from models import db, setup_db

app = Flask(__name__)
setup_db(app)

@app.route('/')
def health_check():
    return jsonify({
        'status': 'online'
    })

if __name__ == '__main__':
    app.run(debug=True)
