from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb+srv://20220024573:T7CmWQ47ed9s8kpv@recipecluster.81ir5.mongodb.net/")
db = client['RecAPI']
recipes_collection = db['Recipes']
ingredients_collection = db['Ingredients']
dietarybenefits_collection = db['Dietarybenefits']
nutritioninfo_collection = db['Nutritioninfo']
users_collection = db['Users']


@app.route('/', methods=['GET'])
def getAll():
    recipes = recipes_collection.find({})
    response = []
    for recipe in recipes:
        recipe_ingredients = ingredients_collection.find({'recipeID': recipe['recipeID']})
        ingredients = [{'name': ing['name'], 'quantity': ing['quantity']} for ing in recipe_ingredients]

        recipe_dietarybenefits = dietarybenefits_collection.find({'recipeID': recipe['recipeID']})
        dietarybenefits = [
            {
                'is_vegan': diet['is_vegan'],
                'is_vegetarian': diet['is_vegetarian'],
                'is_gluten_free': diet['is_gluten_free'],
                'allergens': diet['allergens']
            } 
            for diet in recipe_dietarybenefits
        ]
        response.append({
            'recipeID': recipe['recipeID'],
            'name': recipe['name'],
            'description': recipe.get('description', ''),
            'origin': recipe.get('origin', ''),
            'category': recipe.get('type', ''),
            'serving': recipe.get('servings', ''),
            'preptime': recipe.get('prep_time', ''),
            'cooktime': recipe.get('cook_time', ''),
            'difficulty': recipe.get('difficulty', ''),
            'majorIngredient': recipe.get('majorIngredient', ''),
            'instructions': recipe.get('instructions', ''),
            'createdDate': recipe.get('createdAt', ''),
            'UpdatedDate': recipe.get('updatedAt', ''),
            'ingredients': ingredients,
            'dietarybenefits': dietarybenefits
        })
    
    return jsonify(response)


@app.route('/recipes/<name>/ingredients', methods=['GET'])
def getIngredients(name):
    try:
        recipe = recipes_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}}, {'_id': 0})
        
        if not recipe:
            return jsonify({"message": f"Recipe '{name}' not found"}), 404
        
        recipe_id = recipe['recipeID']
        ingredients_cursor = ingredients_collection.find({'recipeID': recipe_id})
        
        ingredients = [{'name': ing['name'], 'quantity': ing['quantity']} for ing in ingredients_cursor]
        
        response = {
            'recipeID': recipe['recipeID'],
            'name': recipe['name'],
            'description': recipe.get('description', ''),
            'majorIngredient': recipe.get('majorIngredient', ''),
            'ingredients': ingredients
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == '__main__':
    app.run(debug=True)