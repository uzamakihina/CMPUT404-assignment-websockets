#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask

import time
from time import sleep
import flask
from flask import Flask, request, redirect, make_response, jsonify
import json
from flask_sockets import Sockets
import gevent
from gevent import queue
app = Flask(__name__)
sockets = Sockets(app)
# app.debug = True
import os

import logging

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }


class World:
    def __init__(self):
        self.space = {}
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity)
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = {}

    def get(self, entity):
        return self.space.get(entity)
    
    def world(self):
        return self.space


myWorld = World()          



@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''

    
    return redirect("/static/index.html", code=301)



Painters = []

def sendout(msg):
    
    for i in Painters:
        i.update(msg)
        

def paint(ws,painter):
    
    try:
        while True:
            
            
            msg = ws.receive()
            diction = json.loads(msg)
            for key in diction:
                myWorld.space[key] = diction[key]
            

            
            sendout(msg)

            if msg == None:
                break

    except Exception as e:
        print("Finished painting")

class Painter:
    def __init__(self):
        self.queue = queue.Queue()

    def draw(self,data):
        pass
    def update(self,msg):
        self.queue.put(msg)
       
        
    def get(self):
        return self.queue.get()


@sockets.route('/subscribe')
def subscribe_socket(ws):

    painter = Painter()
    Painters.append(painter)
    
    ws.send(json.dumps(myWorld.space))
    thread = gevent.spawn(paint,ws,painter)
    try:
        while True:
            msg = painter.get()
            print(msg)
            ws.send(msg)
    except:
        pass
    finally:
        Painters.remove(painter)
        gevent.kill(thread)
   
            


# setTimer = gevent.spawn(sendout)

if __name__ == "__main__":
    os.system("gunicorn -k flask_sockets.worker sockets:app")
    # app.run(host='0.0.0.0',use_reloader=True)