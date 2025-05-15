from app import create_app,db
from app.models.user import User
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import os

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8083)))