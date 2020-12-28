from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from pymongo import MongoClient
import hashlib
import logging as log
import datetime
import sys

illness_blueprint = Blueprint('illness_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@illness_blueprint.route("/illness/all", methods=["GET"])
def get_all_illnesss():
    col = db["illness"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "name": data["name"],
            "specialist": data["specialist"],
            "symptom_id": [str(s) for s in data["symptom_id"]]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@illness_blueprint.route("/illness/<string:id>", methods=["GET"])
def get_illness(id):
    data = db["illness"].find_one({"_id": ObjectId(id)})

    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                        status=204,
                        mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),
        "name": data["name"],
        "specialist": data["specialist"],
        "symptom_id": [str(s) for s in data["symptom_id"]]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')


@illness_blueprint.route("/illness", methods=["POST"])
def add_illness():
    data = request.json

    try:
        db["illness"].insert_one({
            "name": data["name"],
            "specialist": data["specialist"],
            "symptom_id": data["symptom_id"]
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


@illness_blueprint.route("/illness/<string:id>", methods=["PUT"])
def update_illness(id):
    body = request.json

    filter = {fil: body[fil] for fil in body.keys()}

    try:
        db["illness"].update_one({
            "_id": ObjectId(id)},
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


@illness_blueprint.route("/illness/<string:id>", methods=["DELETE"])
def del_illness(id):
    data = db["illness"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['illness'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                        status=200,
                        mimetype='application/json')
