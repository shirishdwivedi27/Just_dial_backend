from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import MySQLdb.cursors
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

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['APP_URL'] = os.getenv('APP_URL')
app.config['API_KEY'] = os.getenv('API_KEY')
app.config['API_SECRET'] = os.getenv('API_SECRET')



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
    
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)


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

def get_db_connection():
    conn = mysql.connection
    return conn.cursor()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  #
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    logging.info(user['username'])

    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=user['username'])
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user['username'],
                "email": user['email']
            }
        }), 200
    else:
        return jsonify({"msg": "Invalid email or password"}), 401

@app.route('/businesses', methods=['POST'])
@jwt_required()
def create_business():
    data = request.get_json()
    #user_id = get_jwt_identity()
    #logging.info("____",user_id)
    #print(user_id)
    cursor = mysql.connection.cursor()  #
    cursor.execute("""
    INSERT INTO businesses (name, category, location, contact, description, owner_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (
    data['name'],
    data.get('category'),
    data.get('location'),
    data.get('contact'),
    data.get('description'),
    12
    ))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"msg": "Business created successfully"}), 201



@app.route('/businesses', methods=['GET'])
def get_businesses():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, category, location, contact, description FROM businesses")
    businesses = cursor.fetchall()
    cursor.close()
    #print(businesses)
    result = []
    for biz in businesses:
        result.append({
            "id": biz[0],
            "name": biz[1],
            "category": biz[2],
            "location": biz[3],
            "contact": biz[4],
            "description": biz[5]
        })

    return jsonify(result), 200

# business by id -> in future i have to check if id is primary key or not , right now i added manually
@app.route('/businesses/<int:id>', methods=['GET'])
def get_business(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, category, location, contact, description FROM businesses WHERE id = %s", (id,))
    business = cursor.fetchone()
    cursor.close()
    print(business)
    if business:
        return jsonify({
            "id": id,
            "name": business[0],
            "category": business[1],
            "location": business[2],
            "contact": business[3],
            "description": business[4]
        }), 200
    else:
        return jsonify({"message": "Business not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
