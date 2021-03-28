# Casting Agency API

This app is a service for managing Actor and Movie relationships for a casting agency.

The API is hosted live on Heroku:

https://tomivanpete-casting-agency.herokuapp.com/

The API uses role-based access control with [Auth0](https://auth0.com) for the following user types:

- Casting Assistant
    - Can view actors and movies

- Casting Director
    - All permissions from Casting Assistant.
    - Add or delete an actor from the database.
    - Modify actors or movies

- Executive Producer
    - All permissions from Casting Director.
    - Add or delete a movie from the database.

## Getting Started with Local Development

### Install Key Dependencies

[Python 3.9](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

[PostgreSQL](https://www.postgresql.org)


### Virtual Enviornment

Create a new Python 3.9 virtual environment in the root project directory.
```bash
python3 -m pip install virtualenv

...

python3 -m venv env
```

Activate the virtual environment:
```bash
source env/bin/activate
```

More details on virtural environments can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


### Local Environment Settings

Create a file `.env` in the root project directory with the following content:
```bash
export APP_SETTINGS="config.DevelopmentConfig"
export DATABASE_URL="postgres://localhost:5432/casting-agency"
export FLASK_APP=app.py
export FLASK_ENV=development
export AUTH0_DOMAIN="YOUR_AUTH0_DOMAIN"
export ALGORITHMS="YOUR_AUTH0_ALGORIT"
export API_AUDIENCE="YOUR_AUTH0_API_AUDIENCE"
export CLIENT_ID="YOUR_AUTH0_CLIENT_ID"

```
Run `source .env` to activate the environment variables.


### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:

```bash
python3 -m pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

## Database Setup
With Postgres running, create new local databases for running the app and running unit tests.
```bash
createdb casting-agency
createdb casting-agency-test
```
Run `flask db migrate` to update the database schema.

## Running the server

First ensure you are working using your created virtual environment and the above steps have been completed.

To run the server, execute:

```bash
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to the `app.py` file to find the application. 

## Testing
To execute the tests, run the following:
```bash
python3 test_app.py
```
Test data is created for each execution using the [Faker](https://faker.readthedocs.io/en/master/) library. 

# API Endpoints

#### Common Behavior
- Each endpoint will return `{'success': true}` in the response body following successful processing of the request.
- Each endpoint will return `{'success': false}` in the response body if a request fails, along with the appropriate standard status code.


#### GET `'/api/actors'`
- Fetches a list of Actors and a the total number of Actors available. Pagination supported with 10 Actors per page.
- Request Arguments: `page` (optional)
- Returns: An object with keys `actors`, `success`, and `totalActors`. `actors` contains an array of Actors from the DB with `id`, `name`, `age`, and `gender` attributes.
- Errors: 404
```
{
    "actors": [
        {
            "age": 83,
            "gender": "M",
            "id": 1,
            "name": "Morgan Freeman"
        },
        {
            "age": 80,
            "gender": "M",
            "id": 2,
            "name": "Al Pacino"
        },
        {
            "age": 47,
            "gender": "M",
            "id": 3,
            "name": "Christian Bale"
        },
        {
            "age": 43,
            "gender": "F",
            "id": 4,
            "name": "Maggie Gyllenhaal"
        },
        {
            "age": 88,
            "gender": "M",
            "id": 5,
            "name": "Michael Caine"
        },
        {
            "age": 67,
            "gender": "M",
            "id": 6,
            "name": "John Travolta"
        },
        {
            "age": 40,
            "gender": "F",
            "id": 7,
            "name": "Uma Thurman"
        },
        {
            "age": 72,
            "gender": "M",
            "id": 8,
            "name": "Samuel L. Jackson"
        },
        {
            "age": 57,
            "gender": "M",
            "id": 9,
            "name": "Brad Pitt"
        },
        {
            "age": 51,
            "gender": "M",
            "id": 10,
            "name": "Edward Nortan"
        }
    ],
    "success": true,
    "totalActors": 27
}
```


#### GET `'/api/movies'`
- Fetches a list of Movies and a the total number of Movies available. Pagination supported with 10 Movies per page. 
- Request Arguments: `page` (optional)
- Returns: An object with keys `movies`, `success`, and `totalMovies`. `movies` contains an array of Movies from the DB with `id`, `title`, and `releaseDate` attributes.
- Errors: 404
```
{
    "movies": [
        {
            "id": 2,
            "releaseDate": "1972-03-24",
            "title": "The Godfather"
        },
        {
            "id": 3,
            "releaseDate": "2008-07-18",
            "title": "The Dark Knight"
        },
        {
            "id": 4,
            "releaseDate": "1994-10-14",
            "title": "Pulp Fiction"
        },
        {
            "id": 5,
            "releaseDate": "1999-10-15",
            "title": "Fight Club"
        },
        {
            "id": 6,
            "releaseDate": "1994-07-06",
            "title": "Forest Gump"
        },
        {
            "id": 7,
            "releaseDate": "2010-07-16",
            "title": "Inception"
        },
        {
            "id": 8,
            "releaseDate": "1999-03-31",
            "title": "The Matrix"
        },
        {
            "id": 9,
            "releaseDate": "1995-09-22",
            "title": "Se7en"
        },
        {
            "id": 10,
            "releaseDate": "1977-05-25",
            "title": "Star Wars"
        },
        {
            "id": 11,
            "releaseDate": "2006-10-06",
            "title": "The Departed"
        }
    ],
    "success": true,
    "totalMovies": 30
}
```


#### GET `'/api/actors/<actor_id>'`
- Fetches details of an Actor with `actor_id`.
- Request Arguments: None
- Returns: An `actor` object with keys `id`, `name`, `age`, `gender`, and `movies`. `movies` is an array of Movies from the DB associated to the given Actor.
- Errors: 404
```
{
    "actor": {
        "age": 83,
        "gender": "M",
        "id": 1,
        "movies": [
            {
                "id": 1,
                "releaseDate": "1994-10-14",
                "title": "The Shawshank Redemption"
            },
            {
                "id": 9,
                "releaseDate": "1995-09-22",
                "title": "Se7en"
            },
            {
                "id": 3,
                "releaseDate": "2008-07-18",
                "title": "The Dark Knight"
            }
        ],
        "name": "Morgan Freeman"
    },
    "success": true
}
```


#### GET `'/api/movies/<movie_id>'`
- Fetches details of an Movie with `movie_id`.
- Request Arguments: None
- Returns: A `movie` object with keys `id`, `title`, `releaseDate`, and `actors`. `actors` is an array of Actors from the DB associated to the given Movie.
- Errors: 404
```
{
    "movie": {
        "actors": [
            {
                "age": 83,
                "gender": "M",
                "id": 1,
                "name": "Morgan Freeman"
            },
            {
                "age": 57,
                "gender": "M",
                "id": 9,
                "name": "Brad Pitt"
            }
        ],
        "id": 9,
        "releaseDate": "1995-09-22",
        "title": "Se7en"
    },
    "success": true
}
```


#### POST `'/api/actors'`
- Creates a new Actor in the Casting Agency app database according to the request body.
- Schema: `schemas/post_actor.json`
- Request Arguments: None
- Returns: The ID of the new Actor in the key `created` on success.
- Errors: 400, 422 
```
Request:
{
    "name": "Kevin Costner",
    "age": 66,
    "gender": "M"
}
Response:
{
  "success": True,
  "created": 24
}
```


#### POST `'/api/movies`
- Creates a new Movie in the Casting Agency app database according to the request body.
- Schema: `schemas/post_movie.json`
- Request Arguments: None
- Returns: The ID of the new Movie in the key `created` on success.
- Errors: 400, 422 
```
Request:
{
    "title": "The Postman",
    "releaseDate": "1997-12-25"
}
Response:
{
  "success": True,
  "created": 25
}
```


#### PATCH `'/api/actors/<actor_id>'`
- Updates an existing Actor in the Casting Agency app database according to the request body.
- Schema: `schemas/patch_actor.json`
- Request Arguments: None
- Returns: The new JSON representation of the Actor with associated Movies.
- Errors: 400, 404, 422 
```
Request:
{
    "name": "Kevin Costner",
    "age": 67,
    "gender": "M"
}
Response:
{
    "actor": {
        "age": 67,
        "gender": "M",
        "id": 24,
        "movies": [
            {
                "id": 25,
                "title": "The Postman",
                "releaseDate": "1997-12-25"
            }
        ],
        "name": "Kevin Costner"
    },
    "success": true
}
```


#### PATCH `'/api/movies/<movie_id>'`
- Updates an existing Movie in the Casting Agency app database according to the request body.
- Schema: `schemas/patch_movie.json`
- Request Arguments: None
- Returns: The new JSON representation of the Movie with associated Actors.
- Errors: 400, 404, 422 
```
Request:
{
    "title": "The Postmann",
    "releaseDate": "1997-12-25"
}
Response:
{
    "movie": {
        "actors": [
            {
                "name": "Kevin Costner",
                "age": 66,
                "gender": "M"
            }
        ],
        "id": 25,
        "title": "The Postmann",
        "releaseDate": "1997-12-25"
    },
    "success": true
}
```


#### DELETE `'/api/actors/<actor_id>'`
- Deletes the Actor with `actor_id` from the Casting Agency app database. 
- Request Arguments: None
- Returns: The ID of the deleted Actor in the key `deleted` on success.
- Errors: 404
```
{
  "deleted": 24,
  "success": true
}
```


#### DELETE `'/api/movies/<movie_id>'`
- Deletes the Actor with `actor_id` from the Casting Agency app database. 
- Request Arguments: None
- Returns: The ID of the deleted Movie in the key `deleted` on success.
- Errors: 404
```
{
  "deleted": 25,
  "success": true
}
```
