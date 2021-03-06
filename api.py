from flask import Flask, jsonify, request
from pymodm import connect
from flask_cors import CORS
import models
import datetime
from validate_email import validate_email
import numpy as np

connect("mongodb://vcm-3581.vm.duke.edu/heart_rate_app")
app = Flask(__name__)
CORS(app)


@app.route("/api/get_users", methods=["GET"])
def get_users():
    emails = []
    users = models.User.objects.all()
    for user in users:
        emails.append(user.email)
    data = {
        "success": 1,
        "emails": emails
    }
    return jsonify(data), 200


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate():
    """
    Stores heart rate measurement for user with this email
    :param user_email: email (string) of user (POST param)
    :param heart_rate: heart rate (float/int) of user (POST param)
    :param user_age: user age (float/int) (POST param)
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    """
    r = request.get_json()
    ts_now = datetime.datetime.now()
    if(is_email_valid(r["user_email"]) is not True):
        data = {
            "success": 0,
            "error_message": "invalid email"
        }
        return jsonify(data), 400

    if(is_int_or_float(r["heart_rate"]) is not True):
        data = {
            "success": 0,
            "error_message": "invalid heart_rate. Expects float or int."
        }
        return jsonify(data), 400

    if(is_int_or_float(r["user_age"]) is not True):
        data = {
            "success": 0,
            "error_message": "invalid age. Expects float or int."
        }
        return jsonify(data), 400

    if(does_user_exist(r["user_email"])):
        add_heart_rate(r["user_email"], r["heart_rate"], ts_now)
    else:
        create_user(r["user_email"], r["user_age"], r["heart_rate"], ts_now)

    data = {"success": 1}
    return jsonify(data), 200


@app.route("/api/heart_rate/<user_email>", methods=["GET"])
def get_user_hr_readings(user_email):
    """
    Returns all heart rate readings for specified user
    :params user_email: user email (GET param)
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    :returns user_data.email: users email (when status = 200)
    :returns user_data.age: user age (when status = 200)
    :returns user_data.hr_reading: user heart rate readings (when status = 200)
    :returns user_data.readings_ts: ts of reading inserts (when status = 200)
    """

    if(is_email_valid(user_email) is not True):
        data = {
            "success": 0,
            "error_message": "invalid email"
        }
        return jsonify(data), 400

    if(does_user_exist(user_email)):
        user = models.User.objects.raw({"_id": user_email}).first()
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

    return jsonify(response_data), 200


@app.route("/api/heart_rate/average/<user_email>", methods=["GET"])
def get_user_average_hr_readings(user_email):
    """
    Returns average heart rate readings for specified user
    :params user_email: user email (GET param)
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    :returns user_data.email: users email (when status = 200)
    :returns user_data.age: user age (when status = 200)
    :returns user_data.hr_average: user average heart rate (when status = 200)
    :returns user_data.num_readings: num hr readings in avg (when status = 200)
    :returns is_user_tachycaric: bool is user avg hr tachycaric (status = 200)
    """

    if(is_email_valid(user_email) is not True):
        data = {
            "success": 0,
            "error_message": "invalid email"
        }
        return jsonify(data), 400

    if(does_user_exist(user_email)):
        user = models.User.objects.raw({"_id": user_email}).first()
        avg_rate = np.average(user.heart_rate)
        user_data = {
            "email": user.email,
            "age": user.age,
            "hr_average": avg_rate,
            "num_readings": len(user.heart_rate),
            "is_user_tachycaric": is_user_tachycaric(user.age, avg_rate)
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
    return jsonify(response_data), 200


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def get_user_average_hr_readings_interval():
    """
    Returns average heart rate readings for specified user within time range
    :params user_email: user email (POST param)
    :param heart_rate_average_since: datestring of when to start avg calc
    :returns success: 1/0 depending on request status
    :returns status: 200 if OK. 400 if param error
    :returns error_message: (only when status = 400)
    :returns user_data.email: users email (when status = 200)
    :returns user_data.age: user age (when status = 200)
    :returns user_data.datetime_threshold: threshold to calc avg (status =200)
    :returns user_data.hr_average: user average heart rate (when status = 200)
    :returns user_data.num_readings: num hr readings in avg (when status = 200)
    :returns is_user_tachycaric: bool is user avg hr tachycaric (status = 200)
    """
    r = request.get_json()
    if(is_email_valid(r["user_email"]) is not True):
        data = {
            "success": 0,
            "error_message": "invalid email"
        }
        return jsonify(data), 400

    if(is_datetime(r["heart_rate_average_since"]) is not True):
        data = {
            "success": 0,
            "error_message": "invalid heart_rate_average_since. datetime reqd"
        }
        return jsonify(data), 400

    ts_thresh = r["heart_rate_average_since"]
    datetime_threshold = datetime.datetime.strptime(ts_thresh,
                                                    "%Y-%m-%d %H:%M:%S.%f")
    if(does_user_exist(r["user_email"])):
        user = models.User.objects.raw({"_id": r["user_email"]}).first()
        heart_rates_to_average = []
        for idx, time in enumerate(user.heart_rate_times):
            if(time > datetime_threshold):
                print(idx, time)
                heart_rates_to_average.append(user.heart_rate[idx])
        avg_rate = np.average(heart_rates_to_average)
        user_data = {
            "email": user.email,
            "age": user.age,
            "datetime_threshold": datetime_threshold,
            "hr_average": avg_rate,
            "num_readings": len(heart_rates_to_average),
            "is_user_tachycaric": is_user_tachycaric(user.age, avg_rate)
        }
        response_data = {
            "status": 1,
            "user_data": user_data
        }
    else:
        response_data = {
            "status": 0,
            "error_message": r["user_email"] + " has no heart rate readings"
        }
    return jsonify(response_data), 200


def does_user_exist(email):
    """
    Returns whether user exists in Mongo
    :params email: user email
    :returns True/False: boolean
    """
    try:
        user = models.User.objects.raw({"_id": email}).first()
        return(True)
    except:
        return(False)


def is_email_valid(email):
    """
    Returns whether string is valid email address
    :params email: user email
    :returns True/False: boolean
    """
    return(validate_email(email))


def is_int_or_float(val):
    """
    Returns whether val is int/float
    :params val: value to test
    :returns True/False: boolean
    """
    if(isinstance(val, int) or isinstance(val, float)):
        return(True)
    else:
        return(False)


def is_datetime(val):
    """
    Returns whether val is able to be parsed as a datetime
    :params val: value to test
    :returns True/False: boolean
    """
    try:
        dt_string = datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S.%f")
        if(isinstance(dt_string, datetime.datetime)):
            return(True)
        else:
            return(False)
    except:
        return(False)


def create_user(email, age, heart_rate, time):
    """
    Creates a user with the specified email and age. If the user already exists
    in the DB this WILL overwrite that user. It also adds the specified
    heart_rate to the user
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
    Appends a heart_rate measurement at a specified time to the user specified
    by email. It is assumed that the user specified by email exists already.
    :param email: str email of the user
    :param heart_rate: number heart_rate measurement of the user
    :param time: the datetime of the heart_rate measurement
    """
    user = models.User.objects.raw({"_id": email}).first()
    user.heart_rate.append(heart_rate)
    user.heart_rate_times.append(time)
    user.save()


def is_user_tachycaric(age, heart_rate):
    """
    Determines if user heart rate is tachycaric
    :param age: str age of user
    :param heart_rate: number heart_rate measurement of the user
    :returns True/False: Boolean
    """
    tac_thresholds = [
        {"min_age_years": 0, "heart_rate": 159},  # 1-2 days
        {"min_age_years": 0.0082, "heart_rate": 166},  # 3-6 days
        {"min_age_years": 0.0192, "heart_rate": 182},  # 1-3 weeks
        {"min_age_years": 0.0822, "heart_rate": 179},  # 1-2 months
        {"min_age_years": 0.2466, "heart_rate": 186},  # 3-5 months
        {"min_age_years": 0.5, "heart_rate": 169},  # 6-11 months
        {"min_age_years": 1, "heart_rate": 151},  # 1-2 years
        {"min_age_years": 3, "heart_rate": 137},  # 3-4 years
        {"min_age_years": 5, "heart_rate": 133},  # 5-7 years
        {"min_age_years": 8, "heart_rate": 130},  # 8-11 years
        {"min_age_years": 12, "heart_rate": 119},  # 12 - 15 years
        {"min_age_years": 15, "heart_rate": 100},  # > 15 years
    ]
    for threshold in tac_thresholds:
        if(age > threshold["min_age_years"]):
            max_heart_rate = threshold["heart_rate"]
        else:
            pass
    if(heart_rate > max_heart_rate):
        return(True)
    else:
        return(False)
