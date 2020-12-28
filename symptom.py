from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from bson.json_util import dumps
from pymongo import MongoClient
import hashlib
import logging as log
import datetime
import sys

symptom_blueprint = Blueprint('symptom_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@symptom_blueprint.route("/symptoms/all", methods=["GET"])
def get_all_symptoms():
    col = db["symptoms"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "name": data["name"]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@symptom_blueprint.route("/symptoms/<string:id>", methods=["GET"])
def get_symptoms(id):
    data = db["symptoms"].find_one({"_id": ObjectId(id)})

    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                        status=204,
                        mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),
        "name": data["name"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')


@symptom_blueprint.route("/symptoms", methods=["POST"])
def add_symptoms():
    data = request.json

    try:
        db["symptoms"].insert_one({
            "name": data["name"]
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


@symptom_blueprint.route("/symptoms/<string:id>", methods=["PUT"])
def update_symptoms(id):
    body = request.json

    filter = {fil: body[fil] for fil in body.keys()}

    try:
        db["symptoms"].update_one({
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


@symptom_blueprint.route("/symptoms/<string:id>", methods=["DELETE"])
def del_symptoms(id):
    data = db["symptoms"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['symptoms'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                        status=200,
                        mimetype='application/json')


@symptom_blueprint.route("/symptoms/search", methods=["GET"])
def search_symptoms():
    body = request.json

    symptoms = db["symptoms"].find({ "name": { "$in" : body["symptomps_list"] } })
    sym_id = []
    for s in symptoms:
        sym_id.append(s["_id"])

    illnesses = db["illness"].find()

    suggested_illness = {"obj": None, "cnt": 0}

    for illness in illnesses:
        cnt = 0
        illness_symptoms = [sid for sid in illness["symptom_id"]]
        for id in sym_id:
            if id in illness_symptoms:
                cnt += 1         

        if cnt > suggested_illness["cnt"]:
            suggested_illness["obj"] = illness 
            suggested_illness["cnt"] = cnt
    
    if suggested_illness["obj"] is None:
        return Response(response=json.dumps({"Status": "No data found"}),
                        status=204,
                        mimetype='application/json')

    illness = suggested_illness["obj"]

    doctors = db["doctors"].find({"specialization": illness["specialist"]})

    suggested_doctors = []
    for doctor in doctors:
        user = db["users"].find_one({"_id": ObjectId(doctor["_id"])})
        suggested_doctors.append({
            "doctor_id": str(doctor["_id"]),
            "name": "Dr. "+str(user["firstname"])+" "+str(user["lastname"]),
            "base_fee": doctor["base_fee"]
        })

    dataDict = {
        "id": str(illness["_id"]),
        "illness_name": illness["name"],
        "specialist_needed": illness["specialist"],
        "suggested_doctors": suggested_doctors
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')