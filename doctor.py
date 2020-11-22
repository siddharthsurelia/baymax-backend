from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from bson.json_util import dumps
from pymongo import MongoClient
import logging as log
import sys
import hashlib

doctor_blueprint = Blueprint('doctor_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


'''
    Get a list of doctors
'''
@doctor_blueprint.route("/doctor", methods=["GET"])
def get_all_doctors():    
    col = db["doctors"].aggregate([
        {
            '$lookup': {
                'from': 'users', 
                'localField': '_id', 
                'foreignField': '_id', 
                'as': 'User'
            }
        }
    ])
    # res = []

    # for data in col:
    #     dataDict = {
    #         "id": str(data["_id"]),
    #         "name": data["name"],
    #         "age": data["age"]
    #     }

    #     res.append(dataDict)

    return Response(response=dumps(col),
                    status=200,
                    mimetype="application/json" ) 

'''
    Get specific doctor based on _id
'''
@doctor_blueprint.route("/doctor/<string:id>", methods=["GET"])
def get_doctor(id):
    data = db["doctors"].aggregate([
        {
            "$match": {
                "_id": ObjectId(id)
            }
        },
        {
            '$lookup': {
                'from': 'users', 
                'localField': '_id', 
                'foreignField': '_id', 
                'as': 'User'
            }
        }
    ])
    
    # .find_one({"_id": ObjectId(id)})

    if not bool(data):
        return Response(
            response=json.dumps({"error": "No such record found"}),
            status=204,
            mimetype="application/json"
        )

    # dataDict = {
    #         "id": str(data["_id"]),
    #         "name": data["name"],
    #         "age": data["age"]
    # }
    return Response(response=dumps(data),
                    status=200,
                    mimetype="application/json" )


'''
    Add a doctors
'''
@doctor_blueprint.route("/doctor", methods=["POST"])
def add_doctor():
    body = request.json
    password = body["password"]
    result = hashlib.sha512(password.encode())

    try:
        _doc = db["users"].insert_one({
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

        db["doctors"].insert_one({
            "_id": _doc.inserted_id,
            "base_fee": body['base_fee'],
            "specialization": body['specialization']     
        })

        db["schedules"].insert_one({
            "doctor_id": _doc.inserted_id,
            "business_hour": {
                "start_time": body['start_time'] if 'start_time' in body else '',
                "end_time": body['end_time'] if 'end_time' in body else '',
                "duration": body['duration'] if 'duration' in body else ''
            }
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


'''
    Update a specific doctors
'''
@doctor_blueprint.route("/doctor/<string:id>", methods=["PUT"])
def update_doctor(id):
    body = request.json

    filter = { fil: body[fil] for fil in body.keys() }

    print(filter)

    try:
        db["doctors"].update_one({
            "_id": ObjectId(id) },
            {
                "$set": filter
                    # "base_fee": body["base_fee"],
                    # "specialization": body["specialization"]
                           
        })
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                status=500,
                mimetype='application/json')

    return Response(response=json.dumps({"Status": "Record has been updated"}),
                    status=201,
                    mimetype='application/json')


'''
    Delete a specific doctors
'''
@doctor_blueprint.route("/doctor/<string:id>", methods=["DELETE"])
def delete_doctor(id):
    data = db["doctors"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['doctors'].delete_many({'_id': ObjectId(id)})

        db['schedules'].find_one_and_delete({'doctor_id': ObjectId(id) })

        db['users'].find_one_and_delete({'_id': ObjectId(id) })

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')                    