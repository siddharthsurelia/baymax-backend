import re
from flask import Blueprint, jsonify, request, Response, json
from bson.objectid import ObjectId
from bson.json_util import dumps
from pymongo import MongoClient
import logging as log
import sys
from datetime import datetime

schedule_blueprint = Blueprint('schedule_blueprint', __name__)

client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]

@schedule_blueprint.route('/schedule', methods=['POST'])
def add_schedule():
    body = request.json

    dataDict = {
        "doctor_id": ObjectId(body['doctor_id']),
        "business_hour": {
            "start_time": body['start_time'],
            "end_time": body['end_time']
        },
        "duration": body['duration']
    }
    try:
        db['schedule'].insert_one(dataDict)
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient Data"}), status=200, mimetype='application/json')    

    return Response(response=dumps(dataDict), status=200, mimetype='application/json')
    


@schedule_blueprint.route('/schedule/<string:id>', methods=['GET'])
def get_schedule(id):
    res = db['schedule'].aggregate(        
        [
            {
                "$match": { "doctor_id": ObjectId(id)}
            },
            {
                '$lookup': {
                    'from': 'doctor', 
                    'localField': 'doctor_id', 
                    'foreignField': '_id', 
                    'as': 'doctor'
                }
            }
        ]
    ) 

    return Response(response=dumps(res), status=200, mimetype="application/json")



@schedule_blueprint.route('/schedule/<string:id>', methods=['PUT'])
def update_schedule(id):
    body = request.json
    
    dataDict = {
        "doctor_id": ObjectId(body['doctor_id']),
        "business_hour": {
            "start_time": body['start_time'],
            "end_time": body['end_time']
        },
        "duration": body['duration']
    }
    try:
        db['schedule'].update_one({"doctor_id": ObjectId(id) },{
            "$set": { dataDict }
        })
    except KeyError:
        return Response(response=json.dumps({"Status": "Insufficient Data"}), status=200, mimetype='application/json')    

    return Response(response=dumps(dataDict), status=200, mimetype='application/json')
    

@schedule_blueprint.route('/schedule/<string:id>', methods=['DELETE'])
def delete_schedule(id):

    data = db["doctor"].find_one_and_delete({"doctor_id": ObjectId(id)})

    if bool(data):        
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')   