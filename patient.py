from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from pymongo import MongoClient
import hashlib
import logging as log
import datetime
import sys

patient_blueprint = Blueprint('patient_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@patient_blueprint.route("/patients/all", methods=["GET"])
def get_all_patients():
    col = db["patients"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "height": data["height"],
            "weight": data["weight"],
            "cholestrol": data["cholestrol"],
            "sugar_level": data["sugar_level"],
            "blood_pressure": data["blood_pressure"],
            "blood_group": data["blood_group"]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@patient_blueprint.route("/patients/<string:id>", methods=["GET"])
def get_patient(id):
    data = db["patients"].find_one({"_id": ObjectId(id)})

    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                        status=204,
                        mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),
        "height": data["height"],
        "weight": data["weight"],
        "cholestrol": data["cholestrol"],
        "sugar_level": data["sugar_level"],
        "blood_pressure": data["blood_pressure"],
        "blood_group": data["blood_group"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')


@patient_blueprint.route("/patients", methods=["POST"])
def add_user():
    body = request.json
    password = body["password"]
    result = hashlib.sha512(password.encode())
    # height = body["height"]
    # weight = body["weight"]
    # bmi = weight/height**2
    # dob = datetime.datetime.strptime(body["dob"], "%Y-%m-%d").date()
    # today = datetime.date.today()
    # age = today.year - dob.year - \
    #     ((today.month, today.day) < (dob.month, dob.day))

    try:
        _patient = db["users"].insert_one({
            "name": {
                "first_name": body["first_name"],
                "last_name": body["last_name"]
            },
            "email": body["email"],
            "password": result.hexdigest(),
            "dob": body["dob"],
            "gender": body["gender"],
            "address": body["address"]
        })

        db["patients"].insert_one({
            "patient_id": _patient.inserted_id,
            "height": body["height"],
            "weight": body["weight"],
            "cholestrol": body["cholestrol"],
            "sugar_level": body["sugar_level"],
            "blood_pressure": body["blood_pressure"],
            "blood_group": body["blood_group"]    
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


@patient_blueprint.route("/patients/<string:id>", methods=["PUT"])
def update_patient(id):
    body = request.json

    try:
        db["patients"].update_one({
            '_id': ObjectId(id)},
            {
                "$set": {
                    "height": body["height"],
                    "weight": body["weight"],
                    "cholestrol": body["cholestrol"],
                    "sugar_level": body["sugar_level"],
                    "blood_pressure": body["blood_pressure"],
                    "blood_group": body["blood_group"]  
                }
        })
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                        status=500,
                        mimetype='application/json')

    return Response(response=json.dumps({"Status": "Record has been updated"}),
                    status=201,
                    mimetype='application/json')


@patient_blueprint.route("/patients/<string:id>", methods=["DELETE"])
def del_user(id):
    data = db["patients"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['patients'].delete_many({'_id': ObjectId(id)})

        db['user'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                        status=200,
                        mimetype='application/json')
