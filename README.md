# DessertRecipeFinderAPI
Description of the file inside the Repository
- RecipeAPI Folder: Extracted data from each of the collections in the mobngodb database 
- app.py: The python code to run the api (in localhost)
- openAPI.yaml: Is the Api design using swagger

## Api Functionality
- Retrieve all Recipes in the Database
- Post Recipes
- Retrieve a recipe through its NAME
- Push a recipe: Update individual fields of a recipe
- Put a recipe: Updated all fields in the selected recipe 
- Delete a recipe 
- Author: can search an author to check what recipes they have posted

## Personalized Element

## Unique Feature

## How to setup and use the API

## Http requests
- ###### GET ALL RECIPES: http://127.0.0.1:5000/recipes/ 
- ###### GET A RECIPE TROUGH PARAMS: http://127.0.0.1:5000/recipes/search?<param=value>
- ###### POST A RECIPE: http://127.0.0.1:5000/recipes/ use in post method
- ###### GET ALL INGREDIENTS ONLY OF 1 RECIPE: http://127.0.0.1:5000/recipes/<name>/ingredients
- ###### GET ALL NUTRITION ONLY OF 1 RECIPE: http://127.0.0.1:5000/recipes/<name>/nutrition
- ###### CREATE A USER: http://127.0.0.1:5000/user/create



add
user/recipe/create

user/recipe/delete

user/recipe/update


recipe/<name>/ingredients

recipe/<name>/nutrition

recipe/<name>/dietarybenefits

recipe/search?
