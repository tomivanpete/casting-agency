import json
from functools import wraps
from jsonschema import validate, FormatChecker
from flask import request

"""
TODO: refactor, remove duplicated imports from app.py and models.py  
"""
def get_schemas():
    schemas = {}

    with open('schemas/post_actor.json') as f:
        schemas['post_actor'] = json.load(f)

    with open('schemas/post_movie.json') as f:
        schemas['post_movie'] = json.load(f)

    with open('schemas/patch_actor.json') as f:
        schemas['patch_actor'] = json.load(f)

    with open('schemas/patch_movie.json') as f:
        schemas['patch_movie'] = json.load(f)

    return schemas

def schema_validator(schema=''):
    def schema_validator_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            request_json = request.get_json()
            validate(request_json, schema, format_checker=FormatChecker())
            return f(*args, **kwargs)

        return wrapper
    return schema_validator_decorator