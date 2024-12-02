from flask import Flask, request, jsonify
from pymongo import MongoClient
import json 

app = Flask(__name__)

client = MongoClient('mongodb+srv://20220024573:T7CmWQ47ed9s8kpv@recipecluster.81ir5.mongodb.net/')

db = client['RecAPI']
recipe_collection = db['Recipes']

@app.route('/', methods=['GET'])
def getAll():
    recipes = list(recipe_collection.find({}, {'_id': 0}))
    if not recipes:
        return jsonify({"message": "No recipes found"}), 404  
    return jsonify(recipes)


if __name__ == "__main__":
    app.run(debug=True)
 