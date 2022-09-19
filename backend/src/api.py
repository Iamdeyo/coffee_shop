import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES
@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)
    all_drinks = []
    for drink in drinks:
        all_drinks.append(drink.short())
    return jsonify({"success": True, "drinks": all_drinks})


@app.route("/drinks-detail")
@requires_auth('get:drinks')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)
    all_drinks = []
    for drink in drinks:
        all_drinks.append(drink.long())
    return jsonify({"success": True, "drinks": all_drinks})



@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drinks(payload):
    body = request.get_json()
    req_title = body.get("title", None)
    req_recipe = body.get("recipe", None)

    # converting the req_recipe to a string
    req_recipe_str =json.dumps(req_recipe)

    try:
        if req_recipe is None or req_title is None:
            abort(400)
        if req_title == "" or req_recipe_str == "":
            abort(400)

        new_drink = Drink(title=req_title, recipe=req_recipe_str)
        new_drink.insert()
        drink = []
        drink.append(new_drink.long())
    
        return jsonify({"success": True, "drinks": drink})
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload, id):
    body = request.get_json()
    req_title = body.get("title", None)
    req_recipe = body.get("recipe", None)
    # converting the req_recipe to a string
    req_recipe_str =json.dumps(req_recipe)
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        updated_drink = []
        # check the input field
        if req_recipe is not None:
            drink.recipe = req_recipe_str
        if req_title is not None:
            drink.title = req_title


        updated_drink.append(drink.long())
        drink.update()
        return jsonify({
            "success" : True,
            "drinks" : updated_drink  
        })
    except:
        abort(422)
    

@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
        "success" : True,
        "delete" : id 
    })
    except:
        abort(422)

    

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
