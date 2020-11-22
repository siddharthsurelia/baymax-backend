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
    col = db['prescriptions'].aggregate([
        {
            '$lookup': {
                'from': 'users',
                'localField': 'doctor_id',
                'foreignField': '_id',
                'as': 'doctor'
            }
        }, {
            '$lookup': {
                'from': 'users',
                'localField': 'patient_id',
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
        "patient_id": ObjectId(body["patient_id"]),
        "appointment_id": ObjectId(body["appointment_id"]),
        "drugs": []
    }

    for drug in body["drugs"]:
        dataDict['drugs'].append({
                "drug_id": ObjectId(drug['drug_id']),
                "dosage": drug['dosage'],
                "units": drug['units']
        })


    try:
        db["prescriptions"].insert_one(dataDict)
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

    print(filter)

    entries = db["appointments"].find(filter)

    return Response(response=dumps(entries),
                    status=201,
                    mimetype='application/json')
                    


'''
    Add Appointment
'''
@appointment_blueprint.route('/appointment', methods=["POST"])
def add_appointment():
    body = request.json

    duration = db['schedules'].find_one({"doctor_id": ObjectId(body["doctor_id"])})

    duration = int(duration['duration'])

    y, m, d, H, M, S, *_ = split('-|/', body['start_time'])

    start_time = datetime(int(y), int(m), int(d), int(H), int(M), int(S), 00)
    
    if db['appointments'].count_documents({ "doctor_id": ObjectId(body['doctor_id']), "start_time": start_time }) > 0:
        return Response(response=json.dumps({ "Error": f"Cannot create a appointment at {start_time}" }))

    dataDict = {
        "doctor_id": ObjectId(body["doctor_id"]),
        "patient_id": ObjectId(body["patient_id"]),
        "start_time": start_time,
        "end_time": start_time + timedelta(minutes = duration),
        "status": "Available"
    }

    try:
        db["appointments"].insert_one(dataDict)
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
    data = db["appointments"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['appointments'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record not found"}),
                    status=200,
                    mimetype='application/json')    


'''
    Get Appointment from appointment id
'''
@appointment_blueprint.route("/appointment/<string:id>", methods=["GET"])
def get_appointment(id):
    data = db["appointments"].find_one({"_id": ObjectId(id)})

    if bool(data):
        return Response(response=dumps(data),
                    status=200,
                    mimetype="application/json")


'''
    Update Appointment
'''
@appointment_blueprint.route("/appointment/<string:id>", methods=["PUT"])
def update_appointment(id):
    body = request.json

    # duration = 30

    # if 'duration' in body.keys():
    #     duration = int(body['duration'])

    # y, m, d, H, M, S, *_ = split('-|/', body['start_time'])

    # start_time = datetime(int(y), int(m), int(d), int(H), int(M), int(S), 00)

    try:
        db["appointments"].update_one({
            '_id': ObjectId(id)},
            {
                "$set": {
                    # "start_time": start_time,
                    # "end_time": start_time + timedelta(minutes=duration),
                    "status": body['status']
                }
            }
        )
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient data"}),
                status=500,
                mimetype='application/json')
    except Exception as e:
        return Response(response=json.dumps({"error": "Weird Internal Server Error"}),
                status=500,
                mimetype='application/json')

    return Response(response=json.dumps({"status": "Updated"}),
                status=500,
                mimetype='application/json')                