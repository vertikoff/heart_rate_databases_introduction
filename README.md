# heart_rate_databases_starter [![Build Status](https://travis-ci.org/vertikoff/heart_rate_databases_introduction.svg?branch=master)](https://travis-ci.org/vertikoff/heart_rate_databases_introduction)
This code creates an API that fetches and persists heart rate data to a mongodb database. The assignement outline can be found [here](https://github.com/mlp6/Medical-Software-Design/blob/master/Lectures/databases/main.md#mini-projectassignment).

## Getting started
To get the API up and running, perform the following commands in the root directory of this repository: 
1) create a virtual environment: `virtualenv env`
2) start the virtual environment: `source env/bin/activate`
3) install all requirements: `pip install -r requirements.txt`  
**NOTE:** the use of [screens](https://github.com/mlp6/Medical-Software-Design/blob/master/Lectures/cloud_deployment/main.md#screen) is helpful for the following steps  
4) run `docker run -v $PWD/db:/data/db -p 27017:27017 mongo`
5) run `gunicorn --bind 0.0.0.0:5003 api:app` (you can select the port you'd like gunicorn to listen to requests on - this repo defaults to 5003)

## Exposed endpoints
Note: all endpoints return additional info when an error is thrown. This info is to help the end user deduce the issue(s) that cause the request to fail.  

* `POST /api/heart_rate` with
  ```sh
  {
      "user_email": REQUIRED,
      "user_age": REQUIRED, // in years
      "heart_rate": REQUIRED
  }
  ```  
  returns:  
  ```sh
  {
      "success": 1 OR 0  
  }
  ```  
* `GET /api/heart_rate/<user_email>`  
  returns all heart rate measurements for given user:  
  ```sh
  {
      "status": 1 OR 0,
      "user_data": {
          "age": int,
          "email": string,
          "hr_readings": array,
          "readings_ts": array
      }
  }
  ```
* `GET /api/heart_rate/average/<user_email>`  
  returns the user's average heart rate over all measurements:
  ```sh
  {
      "status": 1 OR 0,
      "user_data": {
          "age": int,
          "email": string,
          "hr_average": float,
          "is_user_tachycaric": boolean,
          "num_readings": int
      }
  }
  ```
* `POST /api/heart_rate/interval_average` with 
  ```
  {
      "user_email": REQUIRED,
      "heart_rate_average_since": REQUIRED // date string
  }
  ```  
  returns the average heart rate for the user since the time specified:
  ```sh
  {
      "status": 1 OR 0,
      "user_data": {
          "age": int,
          "datetime_threshold": date string,
          "email": string,
          "hr_average": float,
          "is_user_tachycaric": boolean,
          "num_readings": int
      }
  }
  ```  
* `GET /api/get_users`  
  returns all users with at least one heart rate reading:  
  ```sh
  {
      "success": 1 OR 0,
      "emails": array
  }
  ```
