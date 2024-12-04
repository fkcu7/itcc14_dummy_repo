from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
import hashlib

app = Flask(__name__)

client = MongoClient("mongodb+srv://20220024573:T7CmWQ47ed9s8kpv@recipecluster.81ir5.mongodb.net/")
db = client['RecAPI']
recipes_collection = db['Recipes']
ingredients_collection = db['Ingredients']
dietarybenefits_collection = db['Dietarybenefits']
nutritioninfo_collection = db['Nutritioninfo']
users_collection = db['Users']

@app.route('/recipes', methods=['GET'])
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

@app.route('/recipes/<name>/nutrition', methods=['GET'])
def getNutrition(name):
    try:
        recipe = recipes_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}}, {'_id': 0})
        
        if not recipe:
            return jsonify({"message": f"Recipe '{name}' not found"}), 404
        
        recipe_id = recipe['recipeID']
        nutrition_cursor = nutritioninfo_collection.find({'recipeID': recipe_id})
        
        nutrition = [{'calories_per_serving': ing['calories_per_serving'], 'protein_grams': ing['protein_grams'], 'fat_grams': ing['fat_grams'], 'carbohydrates_grams': ing['carbohydrates_grams'], 'sugar_grams': ing['sugar_grams']} for ing in nutrition_cursor]
        
        response = {
            'recipeID': recipe['recipeID'],
            'name': recipe['name'],
            'description': recipe.get('description', ''),
            'majorIngredient': recipe.get('majorIngredient', ''),
            'nutritionInformation': nutrition
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/users/create', methods=['POST'])
def createUser():
    try: 
        if not request.is_json:
            return jsonify({'error': 'Request must be in JSON format'}), 400
        
        user_data = request.get_json()
        username = user_data.get('username')
        password = user_data.get('password')
        password2 = user_data.get('password2')
        name = user_data.get('name')
        email = user_data.get('email')
        role = user_data.get('role')
        
        if not username or not password or not name or not email or not role:
            return jsonify({'error': 'All fields (username, password, name, email, role) are required'}), 400
        
        if password != password2:
            return jsonify({'error': 'Password mismatched.'}), 400
        
        if users_collection.find_one({'username': username}):
            return jsonify({'error': 'Username already exists'}), 409
        
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 409
        
        hashpass = generate_password_hash(password)
        
        forAPI = role + username + password + email
        
        apiKey = hashlib.md5(forAPI.encode()).hexdigest()

        new_user = {
            'userID': username,
            'password': hashpass,
            'name': name,
            'email': email,
            'role': role,
            'key': apiKey
        }
        
        users_collection.insert_one(new_user)
         
        return jsonify({'message': 'User created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.post('/users/login')
def login():
    if request.is_json():
        user_data = request.get_json()
        userID = user_data.get('username')
        hashpass = user_data.get('password')
                
    if not userID or not hashpass:
            return jsonify({"error": "Both 'username' and 'password' fields are required"}), 400
    
    user = users_collection.find_one({'username': userID})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    
    if not check_password_hash(user['password'], hashpass):
        return jsonify({"error": "Invalid username or password"}), 401
    
    return jsonify({"message": "Login successful", "username": userID}), 200



if __name__ == '__main__':
    app.run(debug=True)
