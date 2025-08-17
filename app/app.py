"""
Main entry point of the application.
"""

import os
from flask import Flask, render_template, request
from flask_migrate import Migrate
from app.resources import api
from app.models import db, Vendor
from sqlalchemy import and_
import logging

# Configure logging before anything else
logging.basicConfig(level=logging.DEBUG)

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

    # Register models
    # @app.shell_context_processor
    # def make_shell_context():
    #     return {'db': db, 'Vendor': Vendor}

    # todo: integrate into the app
    # @app.route('/run_pipeline')
    # def run_pipeline():
    #     from data_pipeline import main
    #     main()
    # return "Pipeline executed!"

    # Register routes
    @app.route('/')
    def home():
        return render_template('index.html')  # Render the HTML template

    @app.route("/no_results")
    def no_results():
        return render_template("no_results.html")
    
    @app.route("/contact")
    def contact():
        return render_template("contact.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/privacy")
    def privacy():
        return render_template("privacy.html")

    # this is where the search function is
    @app.route('/search', methods=['GET', 'POST'])
    def search():
        if request.method == 'POST':
            # get search terms from the form
            country = request.form.get('country')
            service = request.form.get('service')
            search_term = request.form.get('search')
            
            # Combine filters using and_
            filters = []
            if country:
                filters.append(Vendor.country.contains(country))
            if service:
                filters.append(Vendor.service_type == service)
            if search_term: 
                filters.append(Vendor.name.contains(search_term))

            # Apply combined filters to the query
            query = Vendor.query.filter(and_(*filters))
            results = query.all()

            #print(results)
            if not results:
                error_message = f"No results found for the search term: {search_term}"
                return render_template('no_results.html')
            
            # Filter out vendors without a website (better approach)
            #filtered_results = [vendor for vendor in results if vendor.website != 'N/A' or None]
            # Filter out vendors without a website (better approach)
            filtered_results = [vendor for vendor in results if vendor.website and vendor.website != 'N/A']

            return render_template('results.html', results=filtered_results)
        return render_template('index.html')
    
    # Custom 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        error_message = "The page you are looking for does not exist."
        return render_template('no_results.html', error_message=error_message), 404

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)