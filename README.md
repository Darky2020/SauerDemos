
# SauerDemos

Demo collector for Cube 2: Sauerbraten.

Written in python3 with the use of flask, ponyorm, apscheduler, webargs and pyenet.

## Requirements

**python** >= 3.8
**ponyorm**
**flask**
**apscheduler**
**webargs**
**pyenet**

**Go**

## Setup

Run **setup.py** and set password for auth access.

Then you can add auth keys for bot to use at endpoint **/auth/authkey/add**

Then compile **auth.go** in /backend directory via
``go build -buildmode=c-shared -o auth.so auth.go``

## Running

To run the demo collector client run **run_client.py**.
To run the flask server run **run_flask.py**.
