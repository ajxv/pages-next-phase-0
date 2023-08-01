from flask import current_app as app
import mysql.connector as mysql
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = mysql.connect(
    host='localhost',
    user='user',
    password='password',
    database='pages_db'
)

class User:
    table_name = "user"

    def __init__(self):
        cur = db.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name}(email VARCHAR(255), name VARCHAR(255), password VARCHAR(255), PRIMARY KEY(email))")
        db.commit()
        cur.close()
        return
    
    def create(self, email="", name="", password=""):

        user = self.get_by_email(email)

        if user:
            return "User already exists"
        
        cur = db.cursor()
        cur.execute(f"INSERT INTO {self.table_name} VALUES (%s, %s, %s)", (email, name, generate_password_hash(password)))
        db.commit()
        cur.close()

        # return id of record inserted
        return f"Inserted {email}"

    def get_all(self):
        cur = db.cursor()
        cur.execute(f"SELECT * from {self.table_name}")
        users = cur.fetchall()
        cur.close()

        # return a list of dictionary
        return [{"email": u[0], "username": u[1]} for u in users]

    # def get_by_id(self, id):
    #     cur = db.cursor()
    #     cur.execute(f"SELECT * from {self.table_name} WHERE id=%d", (id,))

    #     # if no records found
    #     if not cur.fetchall():
    #         return False
        
    #     user = cur.fetchall()[0]
    #     cur.close()

    #     return {"id": user[0], "name": user[1], "email": user[2]}
    
    def get_by_email(self, email):
        cur = db.cursor()
        cur.execute(f"SELECT * from {self.table_name} WHERE email=%s", ((email, )))

        # if no records found
        if not cur.fetchall():
            return False
        
        user = cur.fetchall()[0]
        cur.close()

        return {"email": user[0], "username": user[1]}
    
    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
        
    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    
    def login(self, email, password):
        cur = db.cursor()
        cur.execute(f"SELECT * from {self.table_name} WHERE email=%s", (email, ))
        user = cur.fetchall()[0]
        cur.close()
        
        # compare password
        if not user or not check_password_hash(user[2], password):
            return
        
        # remove password from user record and return it
        user = list(user)
        user.pop(2)

        return {"email": user[0], "username": user[1]}
    

    
