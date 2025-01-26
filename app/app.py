"""
Main entry point of the application.
"""

from flask import Flask, render_template
from app.resources import api
from app.models import db

def test_something():
    print('this is a test')
    return 'this is a test'

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)

    # Set up configurations for the app
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/vendors.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    api.init_app(app)

    # Register routes
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

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables directly
    app.run(debug=True)