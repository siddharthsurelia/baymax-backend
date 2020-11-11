from flask import Flask, request, jsonify, Response, json
from pymongo import MongoClient
import logging as log
from bson.objectid import ObjectId
import sys

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017")
db = client["baymax"]


@app.route("/")
def index():
    return jsonify({"Message": "You have reached the home page"})


@app.route("/users", methods=["GET"])
def get_all_users():
    col = db["users"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "name": data["name"],
            "age": data["age"]
        }
        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype='application/json')


@app.route("/users/<string:id>", methods=["GET"])
def get_user(id):
    data = db["users"].find_one({"_id": ObjectId(id)})
    
    if not bool(data):
        return Response(response=json.dumps({"Error": "No such record found"}),
                    status=204,
                    mimetype='application/json')

    dataDict = {
        "id": str(data["_id"]),
        "name": data["name"],
        "age": data["age"]
    }

    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype='application/json')


@app.route("/users", methods=["POST"])
def add_user():
    body = request.json

    try:
        db["users"].insert_one({
            "name": body["name"],
            "age": body["age"]
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


@app.route("/users/<string:id>", methods=["PUT"])
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


@app.route("/users/<string:id>", methods=["DELETE"])
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


'''
    Get a list of doctors
'''
@app.route("/doctor", methods=["GET"])
def get_all_doctors():
    col = db["doctor"].find()
    res = []

    for data in col:
        dataDict = {
            "id": str(data["_id"]),
            "name": data["name"],
            "age": data["age"]
        }

        res.append(dataDict)

    return Response(response=json.dumps(res),
                    status=200,
                    mimetype="application/json" )    



'''
    Get specific doctor based on _id
'''
@app.route("/doctor/<string:id>", methods=["GET"])
def get_doctor(id):
    data = db["doctor"].find_one({"_id": ObjectId(id)})

    if not bool(data):
        return Response(
            response=json.dumps({"error": "No such record found"}),
            status=204,
            mimetype="application/json"
        )

    dataDict = {
            "id": str(data["_id"]),
            "name": data["name"],
            "age": data["age"]
    }
    return Response(response=json.dumps(dataDict),
                    status=200,
                    mimetype="application/json" )


'''
    Add a doctors
'''
@app.route("/doctor", methods=["POST"])
def add_doctor():
    body = request.json

    try:
        db["doctor"].insert_one({
            "name": body["name"],
            "age": body["age"]
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
@app.route("/doctor/<string:id>", methods=["PUT"])
def update_doctor(id):
    body = request.json

    try:
        db["doctor"].update_one({
            "_id": ObjectId(id) },
            {
                "$set": {
                    "name": body["name"],
                    "age": body["name"]
                }            
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
@app.route("/doctor/<string:id>", methods=["DELETE"])
def delete_doctor(id):
    data = db["doctor"].find_one({"_id": ObjectId(id)})

    if bool(data):
        db['doctor'].delete_many({'_id': ObjectId(id)})

        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')
    else:
        return Response(response=json.dumps({"Status": "Record has been deleted"}),
                    status=200,
                    mimetype='application/json')



if __name__ == '__main__':
    app.debug = True
    app.run()
