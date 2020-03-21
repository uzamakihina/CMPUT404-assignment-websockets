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

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):

        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''

    
    return redirect("/static/index.html", code=301)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    
    # string = request.data.decode('utf-8')
    # resp = json.loads(string)
    # myWorld.set(entity, resp)
    # res = make_response(resp, 200)

    string = request.data.decode('utf-8')
    resp = json.loads(string)
    
    myWorld.set(entity, resp)
    
    res = make_response(string ,200)
   
    
    return res

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''

    res = make_response(json.dumps(myWorld.space), 200)
    
   
    return res

people = []

@app.route("/entity/<entity>")    
def get_entity(entity, method=['GET']):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    
    temp = myWorld.get(entity)
   
    res = make_response(json.dumps(temp), 200)

    

    return res

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.space = {}
    res = make_response(json.dumps(myWorld.space), 200)
    return res


Painters = []



def sendout():
    
    for i in Painters:
        i.update()
        
        
    

def paint(ws,painter):
    
    try:
        while True:
            
            
            msg = json.loads(ws.receive())
            for key,val in msg.items():
                myWorld.space[key] = val
            
                
            sendout()

            if msg == None:
                break

    except Exception as e:
        print(e)

class Painter:
    def __init__(self):
        self.queue = queue.Queue()

    def draw(self,data):
        pass
    def update(self):
        self.queue.put(json.dumps(myWorld.space))
       
        
    def get(self):
        return self.queue.get()


@sockets.route('/subscribe')
def subscribe_socket(ws):

    painter = Painter()
    Painters.append(painter)
    
    thread = gevent.spawn(paint,ws,painter)
    while True:
        msg = painter.get()
        ws.send(msg)
   
            


# setTimer = gevent.spawn(sendout)

if __name__ == "__main__":
    os.system("gunicorn -k flask_sockets.worker sockets:app")
    # app.run(host='0.0.0.0',use_reloader=True)
