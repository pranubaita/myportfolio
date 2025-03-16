from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import hashlib

app = Flask(__name__)

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://prahnavm09:4DsfMW5nIiz9Iihr@portfolio.4jinc.mongodb.net/?retryWrites=true&w=majority")
db = client.get_database("portfolio")  # Use the 'portfolio' database
app.secret_key = '123'

# Home Page
@app.route("/")
def home():
    # Retrieve projects and achievements from the database
    projects = list(db.projects.find({}, {"_id": 0}))  # Exclude _id from the result
    achievements = list(db.achievements.find({}, {"_id": 0}))  # Exclude _id from the result

    return render_template("index.html", projects=projects, achievements=achievements)


# API Endpoints for Achievements and Projects
@app.route("/api/achievements", methods=["GET"])
def get_achievements():
    achievements = list(db.achievements.find({}, {"_id": 0}))  # Fetch achievements
    return jsonify(achievements)

@app.route("/api/projects", methods=["GET"])
def get_projects():
    projects = list(db.projects.find({}, {"_id": 0}))  # Fetch projects
    return jsonify(projects)

# Admin Page for Adding Content
@app.route("/admin", methods=["GET", "POST"])
def admin():

    # Check if the "projects" and "achievements" collections exist, if not, create them
    if "projects" not in db.list_collection_names():
        db.create_collection("projects")
    if "achievements" not in db.list_collection_names():
        db.create_collection("achievements")

    # Handling POST request to add projects or achievements
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        tags = request.form.get("tags").split(",")  # Convert the comma-separated tags into a list
        year = int(request.form.get("year"))  # Ensure the year is stored as an integer
        category = request.form.get("category")  # Could be "project" or "achievement"
        
        # Get the image URL (optional)
        image_url = request.form.get("image_url")

        # Prepare the data to be inserted
        data = {
            "title": title,
            "description": description,
            "tags": [tag.strip() for tag in tags],  # Remove any extra spaces from tags
            "year": year,
            "image": image_url  # Store the image URL
        }

        # Insert into the appropriate collection based on the category
        if category == "project":
            db.projects.insert_one(data)
        elif category == "achievement":
            db.achievements.insert_one(data)

        # Optionally, redirect to the admin page after submission to prevent re-submission on refresh
        return redirect(url_for("admin"))
    if request.method == 'GET':
        flash('Test')
    # Render the admin page with a form to add new projects or achievements
    
    return render_template("admin.html")

# Test Connection to MongoDB
@app.route("/test_connection")
def test_connection():
    try:
        # Test the connection by fetching data from a known collection
        project = db.projects.find_one()  # Get one project
        if project:
            return f"Connection successful, found project: {project.get('title')}"
        return "No projects found!"
    except Exception as e:
        return f"Error: {str(e)}"

# Endpoint for Creating Collections (If Needed)
@app.route("/create_collections")
def create_collections():
    try:
        # Check if "projects" collection exists; if not, create it
        if "projects" not in db.list_collection_names():
            db.create_collection("projects")
            print("Created 'projects' collection.")
        
        # Check if "achievements" collection exists; if not, create it
        if "achievements" not in db.list_collection_names():
            db.create_collection("achievements")
            print("Created 'achievements' collection.")
        
        return "Collections created successfully or already exist!"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
