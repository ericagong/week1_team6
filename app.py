from pymongo import MongoClient
import certifi
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)