from flask import Flask, jsonify, request
from pymodm import connect
import models
import datetime
import numpy as np

connect("mongodb://localhost:27017/heart_rate_app")  # open up connection to db
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
  if(does_user_exist(r["user_email"])):
      add_heart_rate(r["user_email"], r["heart_rate"], datetime.datetime.now())
  else:
      create_user(r["user_email"], r["user_age"], r["heart_rate"], datetime.datetime.now())

  data = {
    "success": "1"
  }
  return jsonify(data)

@app.route("/api/heart_rate/<user_email>", methods=["GET"])
def get_user_hr_readings(user_email):
  """
  Returns all heart rate readings for specified user
  """
  # data = {
  #   "name": "Cole"
  # }
  if(does_user_exist(user_email)):
      user = models.User.objects.raw({"_id": user_email}).first()  # Get the first user where _id=email
      user_data = {
        "email": user.email,
        "age": user.age,
        "hr_readings": user.heart_rate,
        "readings_ts": user.heart_rate_times
      }
      response_data = {
        "status": 1,
        "user_data": user_data
      }
  else:
      response_data = {
        "status": 0,
        "error_message": user_email + " has no heart rate readings"
      }

  return jsonify(response_data) # respond to the API caller with a JSON representation of data

@app.route("/api/heart_rate/average/<user_email>", methods=["GET"])
def get_user_average_hr_readings(user_email):
  """
  Returns average heart rate readings for specified user
  """
  # data = {
  #   "name": "Cole"
  # }
  if(does_user_exist(user_email)):
      user = models.User.objects.raw({"_id": user_email}).first()  # Get the first user where _id=email
      user_data = {
        "email": user.email,
        "age": user.age,
        "hr_average": np.average(user.heart_rate),
        "num_readings": len(user.heart_rate)
      }
      response_data = {
        "status": 1,
        "user_data": user_data
      }
  else:
      response_data = {
        "status": 0,
        "error_message": user_email + " has no heart rate readings"
      }

  return jsonify(response_data) # respond to the API caller with a JSON representation of data

def does_user_exist(email):
    try:
        user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
        return(True)
    except:
        return(False)

def create_user(email, age, heart_rate, time):
    """
    Creates a user with the specified email and age. If the user already exists in the DB this WILL
    overwrite that user. It also adds the specified heart_rate to the user
    :param email: str email of the new user
    :param age: number age of the new user
    :param heart_rate: number initial heart_rate of this new user
    :param time: datetime of the initial heart rate measurement
    """
    u = models.User(email, age, [], [])  # create a new User instance
    u.heart_rate.append(heart_rate)  # add initial heart rate
    u.heart_rate_times.append(time)  # add initial heart rate time
    u.save()  # save the user to the database

def add_heart_rate(email, heart_rate, time):
    """
    Appends a heart_rate measurement at a specified time to the user specified by
    email. It is assumed that the user specified by email exists already.
    :param email: str email of the user
    :param heart_rate: number heart_rate measurement of the user
    :param time: the datetime of the heart_rate measurement
    """
    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    user.heart_rate.append(heart_rate)  # Append the heart_rate to the user's list of heart rates
    user.heart_rate_times.append(time)  # append the current time to the user's list of heart rate times
    user.save()  # save the user to the database

def print_user(email):
    """
    Prints the user with the specified email
    :param email: str email of the user of interest
    :return:
    """
    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    print(user.email)
    print(user.heart_rate)
    print(user.heart_rate_times)
