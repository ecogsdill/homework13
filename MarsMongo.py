import pymongo
from flask import Flask, jsonify

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.marsDB
x=db.mars.find()
print(x[0])
'''
def function():
    return (jsonify(x[0]))

print(function())
'''