'''
main entry point of application
'''

from flask import Flask, render_template
from models import db
from resources import api

# Initialize Flask app instance
app = Flask(__name__)

# Set up configurations for the app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vendors.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy and Flask-RESTful
db.init_app(app)
api.init_app(app)

# Route for home page (root URL)
@app.route('/')
def home():
    return render_template('index.html')  # Render the HTML template

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# # Create the database tables (run this once)
# @app.before_first_request
# def create_tables():
#     # Ensure that db.create_all() is called only once before the first request
#     db.create_all()

# Run the application
# Directly create the tables here if needed
if __name__ == "__main__":
    with app.app_context():  # Make sure we have an application context
        db.create_all()  # Create tables directly
    app.run(debug=True)