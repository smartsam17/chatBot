from flask import Flask, jsonify, request
#from flask_httpauth import HTTPBasicAuth
#import pymongo
#from flask_cors import CORS
#from googlesearch import search 
app = Flask(__name__)
#cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
#auth = HTTPBasicAuth()
import requests
#from bs4 import BeautifulSoup

#myclient = pymongo.MongoClient("mongodb://sachin17:Sapple123!@ds125953.mlab.com:25953/homoeopathy_in_kanpur")
#mydb = myclient["homoeopathy_in_kanpur"]
#reviewsCol = mydb["reviews"]


@app.route("/")
def index():
    return "Welcome Page"

@app.route("/user")
def user():
    return "User Page"



if __name__ == "__main__":
    app.run(debug = True)




    
