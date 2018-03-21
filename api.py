from flask import Flask, jsonify, request
from pymodm import connect
import models
import datetime
app = Flask(__name__)

@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
  """
  Stores heart rate measurement for user with this email
  """
  r = request.get_json()
  print(r["user_email"])
  print(r["user_age"])
  print(r["heart_rate"])

  data = {
    "success": "1"
  }
  return jsonify(data)

# @app.route("/name", methods=["GET"])
# def getName():
#   """
#   Returns the data dictionary below to the caller as JSON
#   """
#   data = {
#     "name": "Cole"
#   }
#   return jsonify(data) # respond to the API caller with a JSON representation of data

# @app.route("/name/<name>", methods=["GET"])
# def getCustomName(name):
#   """
#   Returns the data dictionary below to the caller as JSON
#   """
#   # data = {
#   #   "name": "Cole"
#   # }
#   data = {
#     "message": "Hello there, {0}".format(name)
#   }
#   return jsonify(data) # respond to the API caller with a JSON representation of data
