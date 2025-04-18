from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
CORS(app)

# --------------------- Configuration ---------------------
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

app_config = {
    'JWT_SECRET_KEY':os.getenv('JWT'),
    'APP_URL': os.getenv('APP_URL'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET'),
    'SECRET_KEY': os.getenv('SECRET_KEY')
}


jwt = JWTManager(app)


# --------------------- Routes ---------------------

log_filename = "script.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)

mysql=MySQL(app)

@app.route('/testdb')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        logging.info("hello")
        print("DB")
        return "DB Connected!"
    except Exception as e:
        return {"error": str(e)},400 
    

@app.route('/',methods=['GET'])
def home():
    data={"message":"welcome to react-world","name":"shirish"}
    return jsonify(data),200
    

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify({"message": "User already exists. Please login."}), 409

  
    hashed_password = generate_password_hash(password)

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password, org_password, email) VALUES (%s, %s, %s, %s)", 
                   (username, hashed_password, password, email))
    mysql.connection.commit()
    cursor.close()

    access_token = create_access_token(identity=email)

    return jsonify({
        "message": "User registered successfully!",
        "access_token": access_token
    }), 201


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
