from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from pymongo import MongoClient
import logging as log
import sys

import med_search

medicine_blueprint = Blueprint('medicine_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@medicine_blueprint.route("/medicines/search/<string:med_name>", methods=["GET"])
def search_medicines(med_name):
    data = med_search.search_medname(med_name)

    if data is not None:
        response = json.dumps(data)
        status = 200

        db["medicines"].insert_one(data)
    else:
        response = json.dumps({"Status": "No such medicine found"})
        status = 204

    return Response(response=response,
                    status=status,
                    mimetype="application/json")


@medicine_blueprint.route("/medicines/all", methods=["GET"])
def get_all_meds():
    col = db["medicines"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "name": data["name"],
            "manufacturer": data["manufacturer"],
            "composition": data["composition"],
            "symptoms": data["symptoms"],
            "side_effects": data["side_effects"],
            "substitutes": data["substitutes"]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@medicine_blueprint.route("/medicines/<string:id>", methods=["GET"])
def get_med(id):
    data = db["medicines"].find_one({"_id": ObjectId(id)})
    
    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                    status=204,
                    mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),            
        "name": data["name"],
        "manufacturer": data["manufacturer"],
        "composition": data["composition"],
        "symptoms": data["symptoms"],
        "side_effects": data["side_effects"],
        "substitutes": data["substitutes"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')