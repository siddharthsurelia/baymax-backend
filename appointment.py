from re import split
from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import app
from pymongo import MongoClient
import logging as log
import sys
from datetime import datetime, timedelta

appointment_blueprint = Blueprint('appointment_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


'''
    Get all the prescription
'''
@appointment_blueprint.route('/prescription', methods=["GET"])
def get_all_appointments():
    col = db['prescription'].aggregate([
        {
            '$lookup': {
                'from': 'doctor',
                'localField': 'doctor_id',
                'foreignField': '_id',
                'as': 'doctor'
            }
        }, {
            '$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'patient'
            }
        }
    ])

    res = [data for data in col]

    return Response(response=dumps(res),
                    status=200,
                    mimetype="application/json")


'''
    Add a prescription
'''
@appointment_blueprint.route('/prescription', methods=["POST"])
def add_prescription():
    body = request.json

    dataDict = {
        "doctor_id": ObjectId(body["doctor_id"]),
        "user_id": ObjectId(body["user_id"]),
        "appointment_id": ObjectId(body["appointment_id"]),
        "drugs": []
    }

    for drug in body["drugs"]:
        dataDict['drugs'].append({
                "drug_id": ObjectId(drug['drug_id']),
                "dose": drug['dose'],
                "units": drug['units']
        })


    try:
        db["prescription"].insert_one(dataDict)
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                status=500,
                mimetype='application/json')
    
    return Response(response=json.dumps({"Status": "Record has been added"}),
                    status=201,
                    mimetype='application/json')


'''
    Get appointments list based on specific fields
'''
@appointment_blueprint.route('/appointment', methods=["GET"])                    
def get_appointment_list():

    body = request.json

    filter = { fil: ObjectId(body[fil]) for fil in body.keys() }

    entries = db["appointment"].find(filter)

    return Response(response=dumps(entries),
                    status=201,
                    mimetype='application/json')
                    


'''
    Add Appointment
'''
@appointment_blueprint.route('/appointment', methods=["POST"])
def add_appointment():
    body = request.json

    duration = 30

    if 'duration' in body.keys():
        duration = int(body['duration'])

    y, m, d, H, M, S, *_ = split('-|/', body['start_time'])

    start_time = datetime(int(y), int(m), int(d), int(H), int(M), int(S), 00)
    
    if db['appointment'].count_documents({ "doctor_id": ObjectId(body['doctor_id']), "start_time": start_time }) > 0:
        return Response(response=json.dumps({ "Error": f"Cannot create a appointment at {start_time}" }))

    dataDict = {
        "doctor_id": ObjectId(body["doctor_id"]),
        "user_id": ObjectId(body["user_id"]),
        "start_time": start_time,
        "end_time": start_time + timedelta(minutes = duration)
    }

    try:
        db["appointment"].insert_one(dataDict)
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                status=500,
                mimetype='application/json')
        
    return Response(response=dumps({"Status": "Record has been added"}),
                    status=201,
                    mimetype='application/json')


'''
    Delete appointment 
'''
@appointment_blueprint.route("/appointment/<string:id>", methods=["DELETE"])
def delete_appointment(id):
    data = db["appointment"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['appointment'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')    

