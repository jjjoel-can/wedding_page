import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.app import db, create_app

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()