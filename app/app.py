from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import logging
app = Flask(__name__)
CORS(app)

# --------------------- Configuration ---------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yourpassword@localhost/justdial_clone'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'

db = SQLAlchemy(app)
jwt = JWTManager(app)


# --------------------- Routes ---------------------

log_filename = "script.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)




@app.route('test_db',methods=['GET'])
def check_db():
    try:
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT 1')
        return jsonify(message="DB connected"),200
    except:
        return jsonify(message="not connected"),401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    

@app.route('/api/businesses', methods=['POST'])
@jwt_required()
def create_business():
    data = request.get_json()
    # new_biz = Business(
    #     name=data['name'],
    #     category=data.get('category'),
    #     location=data.get('location'),
    #     contact=data.get('contact'),
    #     description=data.get('description')
    # )
    

@app.route('/api/businesses', methods=['GET'])
def get_businesses():
    pass

# --------------------- Main ---------------------

if __name__ == '__main__':
    app.run(debug=True)
