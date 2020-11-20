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


@user_blueprint.route("/patients/all", methods=["GET"])
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


@user_blueprint.route("/patients/<string:id>", methods=["GET"])
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


@user_blueprint.route("/users", methods=["POST"])
def add_user():
    body = request.json
    password = body["password"]
    result = hashlib.sha512(password.encode())
    height = body["height"]
    weight = body["weight"]
    bmi = weight/height**2
    dob = datetime.datetime.strptime(body["dob"], "%Y-%m-%d").date()
    today = datetime.date.today()
    age = today.year - dob.year - \
        ((today.month, today.day) < (dob.month, dob.day))

    biometrics = db["biometrics"].insert_one({
        "height": height,
        "weight": weight,
        "bmi": bmi,
        "cholestrol": body["cholestrol"],
        "diabetic": body["diabetic"],
        "blood_pressure": body["blood_pressure"],
        "blood_group": body["blood_group"]
    })

    try:

        db["users"].insert_one({
            "name": body["name"],
            "username": body["username"],
            "password": result.hexdigest(),
            "dob": str(dob),
            "age": age,
            "mobile": body["mobile"],
            "address": body["address"],
            "biometrics_id": biometrics._InsertOneResult__inserted_id
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
