from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from pymongo import MongoClient
import hashlib
import logging as log
import sys

user_blueprint = Blueprint('user_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@user_blueprint.route("/")
def index():
    return jsonify({"Message": "You have reached the home page"})


@user_blueprint.route("/users/login", methods=["POST"])
def login():
    body = request.json
    username = body["username"]
    password = body["password"]

    data = db["users"].find_one({"username": username})

    if data is not None and hashlib.sha512(password.encode()).hexdigest() == data["password"]:
        res = "Login Successful"
        status = 200
    else:
        res = "Username or Password incorrect"
        status = 401
    
    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@user_blueprint.route("/users/all", methods=["GET"])
def get_all_users():
    col = db["users"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "username": data["username"],
            "name": data["name"],
            "age": data["age"]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@user_blueprint.route("/users/<string:id>", methods=["GET"])
def get_user(id):
    data = db["users"].find_one({"_id": ObjectId(id)})
    
    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                    status=204,
                    mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),
        "username": data["username"],
        "name": data["name"],
        "age": data["age"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')


@user_blueprint.route("/users", methods=["POST"])
def add_user():
    body = request.json
    password = body["password"]
    result = hashlib.sha512(password.encode())

    try:
        db["users"].insert_one({
            "name": body["name"],
            "username": body["username"],
            "password": result.hexdigest(),
            "age": body["age"]
        })
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                status=500,
                mimetype='application/json')
    except Exception as e:
        return Response(response=json.dumps({"Status": "Internal server error - "+str(e.__class__)}),
                status=500,
                mimetype='application/json')

    return Response(response=json.dumps({"Status": "Record has been added"}),
                    status=201,
                    mimetype='application/json')


@user_blueprint.route("/users/<string:id>", methods=["PUT"])
def update_user(id):
    body = request.json

    try:
        db["users"].update_one({
            '_id': ObjectId(id)},
            {
                "$set": {
                    "name": body["name"],
                    "age": body["age"]
                }
        })
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                status=500,
                mimetype='application/json')

    return Response(response=json.dumps({"Status": "Record has been updated"}),
                    status=201,
                    mimetype='application/json')


@user_blueprint.route("/users/<string:id>", methods=["DELETE"])
def del_user(id):
    data = db["users"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['users'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')