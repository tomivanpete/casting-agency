import json
from functools import wraps
from jsonschema import validate, FormatChecker
from flask import request

def get_schemas():
    """Returns a dictionary of JSON schemas located in the schemas/ directory"""
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
    """Decorator to validate JSON request bodies against the schema
    
    Raises:
        ValidationError: An error occurred validating the JSON request body against the schema
    """
    def schema_validator_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            request_json = request.get_json()
            validate(request_json, schema, format_checker=FormatChecker())
            return f(*args, **kwargs)

        return wrapper
    return schema_validator_decorator