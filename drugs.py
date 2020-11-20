from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from pymongo import MongoClient
import logging as log
import sys

import med_search

drugs_blueprint = Blueprint('drugs_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@drugs_blueprint.route("/drugs/search/<string:med_name>", methods=["GET"])
def search_drugs(med_name):
    data = med_search.search_medname(med_name)

    if data is not None:
        response = json.dumps(data)
        status = 200

        db["drugs"].insert_one(data)
    else:
        response = json.dumps({"Status": "No such drug found"})
        status = 204

    return Response(response=response,
                    status=status,
                    mimetype="application/json")


@drugs_blueprint.route("/drugs/all", methods=["GET"])
def get_all_drugs():
    col = db["drugs"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "name": data["name"],
            "manufacturer": data["manufacturer"],
            "composition": data["composition"],
            "side_effects": data["side_effects"],
            "substitutes": data["substitutes"],
            "illness_id": data["illness_id"]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@drugs_blueprint.route("/drugs/<string:id>", methods=["GET"])
def get_drug(id):
    data = db["drugs"].find_one({"_id": ObjectId(id)})
    
    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                    status=204,
                    mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),            
        "name": data["name"],
        "manufacturer": data["manufacturer"],
        "composition": data["composition"],
        "side_effects": data["side_effects"],
        "substitutes": data["substitutes"],
        "illness_id": data["illness_id"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')