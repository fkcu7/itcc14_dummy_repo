from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb+srv://20220024573:T7CmWQ47ed9s8kpv@recipecluster.81ir5.mongodb.net/")
db = client['RecAPI']
recipes_collection = db['Recipes']
ingredients_collection = db['Ingredients']
dietarybenefits_collection = db['Dietarybenefits']
nutritioninfo_collection = db['Nutritioninfo']
pictures_collection = db['Pictures']
users_collection = db['Users']
videos_collection = db['Videos']

@app.route('/', methods=['GET'])
def getAll():
    recipes = list(recipes_collection.find({},{'_id': 0}))
    return jsonify(recipes)

if __name__ == '__main__':
    app.run(debug=True)

