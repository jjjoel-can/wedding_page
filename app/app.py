"""
Main entry point of the application.
"""

import os
from flask import Flask, render_template, request
from flask_migrate import Migrate
from app.resources import api
from app.models import db, Vendor

def test_something():
    print('this is a test')
    return 'this is a test'

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)

    # Set the absolute path for the SQLite database file
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'vendors.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    api.init_app(app)

    migrate = Migrate(app, db)  # Initialize the Migrate object

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

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        if request.method == 'POST':
            country = request.form.get('country')
            service = request.form.get('service')
            search_term = request.form.get('search')

            # Query the database based on the form data
            query = Vendor.query
            if country:
                query = query.filter(Vendor.address.contains(country))
            if service:
                query = query.filter(Vendor.service_type == service)
            if search_term:
                query = query.filter(Vendor.name.contains(search_term))

            results = query.all()

            return render_template('results.html', results=results)
        return render_template('index.html')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)