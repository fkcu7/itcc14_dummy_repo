from flask import Flask, request, jsonify
from pymongo import MongoClient
import hashlib

app = Flask(__name__)

client = MongoClient("mongodb+srv://20220024573:T7CmWQ47ed9s8kpv@recipecluster.81ir5.mongodb.net/")
db = client['RecAPI']
recipes_collection = db['Recipes']
ingredients_collection = db['Ingredients']
dietarybenefits_collection = db['Dietarybenefits']
nutritioninfo_collection = db['Nutritioninfo']
users_collection = db['Users']



## FUNCTIONS ##
def checkKey(username, key):
    user = users_collection.find_one({'userID': username})
    userAPIkey = user['key']
    
    if userAPIkey == key:
        return True
    
def getRecipes(recipes):
    response = []
    for recipe in recipes:
        dietarybenefits = getDietaryBenefits(recipe['recipeID'])
        nutritioninfo = getNutritionInfo(recipe['recipeID'])
        
        response.append(
                {
                    'recipeID': recipe['recipeID'],
                    'name': recipe['name'],
                    'description': recipe['description'],
                    'origin': recipe['origin'],
                    'category': recipe['type'],
                    'serving': recipe['servings'],
                    'preptime': recipe['prep_time'],
                    'cooktime': recipe['cook_time'],
                    'difficulty': recipe['difficulty'],
                    'majorIngredient': recipe['majorIngredient'],
                    'instructions': recipe['instructions'],
                    'ingredients': recipe['ingredients'],
                    'dietarybenefits': dietarybenefits,
                    'nutrition': nutritioninfo,
                    'author': recipe['user']
                }
            )
    return response

def getDietaryBenefits(recipeID):
    recipe_dietarybenefits = dietarybenefits_collection.find({'recipeID': recipeID})
    dietarybenefits = [
        {
            'is_vegan': benefits['is_vegan'],
            'is_vegetarian': benefits['is_vegetarian'],
            'is_gluten_free': benefits['is_gluten_free'],
            'allergens': benefits['allergens']
        } 
        for benefits in recipe_dietarybenefits
    ]
    return dietarybenefits

def getNutritionInfo(recipeID):
    recipe_nutrition = nutritioninfo_collection.find({'recipeID': recipeID})
    nutritioninfo = [
        {
            'calories_per_serving': nutrition['calories_per_serving'],
            'protein_grams': nutrition['protein_grams'],
            'fat_grams': nutrition['fat_grams'],
            'carbohydrates_grams': nutrition['carbohydrates_grams'],
            'sugar_grams': nutrition['sugar_grams']
        }
        for nutrition in recipe_nutrition
    ]
    return nutritioninfo
    
def deleteNutritionInfo(recipeID):
    nutritioninfo_collection.delete_one({'recipeID': recipeID})

def deleteDietaryBenefits(recipeID):
    dietarybenefits_collection.delete_one({'recipeID': recipeID})
 
 
 
## RECIPES ##   
@app.route('/recipes', methods=['GET'])
def getAll():
    try:
        recipes = recipes_collection.find({})
        response = getRecipes(recipes)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recipes/<name>/nutrition-info', methods=['GET'])
def getNutrition(name):
    try:
        recipe = recipes_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}}, {'_id': 0})

        if not recipe:
            return jsonify({"message": f"Recipe '{name}' not found"}), 404
        
        response = [
            {
                'name': recipe['name'],
                'nutrition_info': getNutritionInfo(recipe['recipeID'])
            }
        ]
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/recipes/<name>/dietary-benefits', methods=['GET'])
def getDietary(name):
    try:
        recipe = recipes_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}}, {'_id': 0})

        if not recipe:
            return jsonify({"message": f"Recipe '{name}' not found"}), 404
        
        response = [
            {
                'name': recipe['name'],
                'nutrition_info': getDietaryBenefits(recipe['recipeID'])
            }
        ] 
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
 
## USER ##  
 
@app.route('/users/create', methods=['POST'])
def createUser():
    try: 
        if not request.is_json:
            return jsonify({'error': 'Request must be in JSON format'}), 400
        
        user_data = request.get_json()
        username = user_data.get('username')
        password = user_data.get('password')
        name = user_data.get('name')
        email = user_data.get('email')
        role = user_data.get('role')
        
        if not username or not password or not name or not email or not role:
            return jsonify({'error': 'All fields (username, password, name, email, role) are required'}), 400
        
        if users_collection.find_one({'userID': username}):
            return jsonify({'error': 'Username already exists'}), 409
        
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 409
        
        hashpass = hashlib.md5(password.encode()).hexdigest()
        
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
 
@app.route('/users/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be in JSON format'}), 400
        
        user_data = request.get_json()
        username = user_data.get('username')
        password = user_data.get('password')
            
        if not username or not password:
            return jsonify({'error': "Both 'username' and 'password' fields are required."}), 400
        
        user = users_collection.find_one({'userID': username})
        hashpass = hashlib.md5(password.encode()).hexdigest()
        
        if not user:
            return jsonify({'error': "Invalid username."}), 401
        
        if  hashpass != user['password']: 
            return jsonify({'error': "Invalid  password."}), 401
        
        return jsonify({'key': user['key']}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/users/delete', methods=['DELETE'])
def deleteUser():
    try:
        if request.is_json:
            user_data = request.get_json()
            username = user_data.get('username')
            password = user_data.get('password')
            
        if not username or not password:
            return jsonify({'error': "Both 'username' and 'password' fields are required."}), 404
        
        user = users_collection.find_one({'userID': username})
        hashpass = hashlib.md5(password.encode()).hexdigest()
        
        if not user:
            return jsonify({'error': "Invalid username."}), 401
        
        if  hashpass != user['password']: 
            return jsonify({'error': "Invalid  password."}), 401
        
        users_collection.delete_one({'userID': username})
        return jsonify({'message': "User deletion successful."}), 200
    except Exception as e:
        return jsonify({'error': str(e)})
   
@app.route('/<userID>/recipes', methods=['GET'])    
def getRecipesByAuthor(userID):
    key = request.args.get('key')
    
    if(checkKey(userID, key)):
        try:
            recipes = recipes_collection.find({'user': userID},{'_id': 0})
            response = getRecipes(recipes) 
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'message':"Unauthorized access"}), 200
  
@app.route('/<userID>/recipes/<name>', methods=['GET'])    
def getSpecificRecipeByAuthor(userID, name):
    key = request.args.get('key')
    
    if(checkKey(userID, key)):
        try:
            recipes = recipes_collection.find({'user': userID, 'name': {'$regex': f'^{name}$', '$options': 'i'}},{'_id': 0})
            response = getRecipes(recipes) 
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'message':"Unauthorized access"}), 200   

@app.route('/<userID>/recipes/delete', methods=['DELETE']) 
def deleteRecipe(userID):
    key = request.args.get('key')

    if(checkKey(userID, key)):
        try:
            if request.is_json:
                recipe_data = request.get_json()
                recipename = recipe_data.get('name')
                
                recipe = recipes_collection.find_one({'name': recipename})
                 
                if recipe:
                    if recipe['user'] == userID:
                        recipeID = recipe['recipeID']
                        deleteNutritionInfo(recipeID)
                        deleteDietaryBenefits(recipeID)
                        if recipes_collection.delete_one({'name': recipename}):
                            return jsonify({'message': "Deletion successful"}), 200
                    else:
                        return jsonify({'error': "Unauthorized to delete recipe"}), 409 
                else:
                    return jsonify({'error': "Recipe not found"}), 404           
        except Exception as e:
            return jsonify({'error': str(e)})    
        
    
if __name__ == '__main__':
    app.run(debug=True)