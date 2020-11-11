from flask import Flask
from user import user_blueprint
from medicine import medicine_blueprint


app = Flask(__name__)
app.register_blueprint(user_blueprint)
app.register_blueprint(medicine_blueprint)


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
            "age": body["age"],
            "type": '',
            "clinic_address": ''            
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
