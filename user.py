from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from pymongo import MongoClient
import hashlib
import logging as log
import datetime
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
    email = body["email"]
    password = body["password"]

    data = db["users"].find_one({"email": email})

    if data is not None and hashlib.sha512(password.encode()).hexdigest() == data["password"]:
        res = {"Status": "Login Successful"}
        status = 200
    else:
        res = {"Status": "Email or Password incorrect"}
        status = 401

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@user_blueprint.route("/users/all", methods=["GET"])
def get_all_users():
    col = db["users"].find({})
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "firstname": data["firstname"],
            "lastname": data["lastname"],
            "email": data["email"],
            "dob": data["dob"],
            "mobile": data["mobile"],
            "address": data["address"]
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
        "firstname": data["firstname"],
        "lastname": data["lastname"],
        "email": data["email"],
        "dob": data["dob"],
        "mobile": data["mobile"],
        "address": data["address"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')


@user_blueprint.route("/users/<string:id>", methods=["PUT"])
def update_user(id):
    body = request.json

    filter = {fil: body[fil] for fil in body.keys()}

    try:
        db["users"].update_one({'_id': ObjectId(id)},
                               {
            "$set": filter
        })
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                        status=500,
                        mimetype='application/json')

    return Response(response=json.dumps({"Status": "Record has been updated"}),
                    status=201,
                    mimetype='application/json')


# @user_blueprint.route("/users/<string:id>", methods=["DELETE"])
# def del_user(id):
#     data = db["users"].find_one({"_id": ObjectId(id)})

#     if bool(data):
#         db['users'].delete_many({'_id': ObjectId(id)})

#         return Response(response=json.dumps({"Status": "Record has been deleted"}),
#                         status=200,
#                         mimetype='application/json')
#     else:
#         return Response(response=json.dumps({"Status": "Record has been deleted"}),
#                         status=200,
#                         mimetype='application/json')
