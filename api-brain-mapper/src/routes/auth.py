import os
import json
from flask import Blueprint, request, redirect, jsonify, abort, g, make_response
from werkzeug.exceptions import HTTPException
from logs.logger import logger

from sqlalchemy import select
from ..models.user import User
from ..schemas.user import user_schema
from ..database.dbConnection import db

from ..security.jwt_utils import *
from ..security.decorators_utils import auth_required
from ..security.crypto_utils import *

# Open file with available roles
rolesFile = os.path.join(os.getcwd(), "src/database/reference-data/ROLES.json")
with open(rolesFile) as f:
  availableRoles = json.load(f)

# Setup blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/addUser', methods=['POST'])
@auth_required(["ADMIN"])
def addUser():
    req = request.json

    # Check if request has enough properties needed
    required_keys = ['name', 'lastName', 'email', 'passwd', 'roleId']
    if not all(key in req for key in required_keys):
        abort(400, 'BAD REQUEST')

    # Get request properties
    name = req['name']
    lastName = req['lastName']
    email = req['email']
    password = req['passwd']
    roleId = req['roleId']

    # Search for existent user with same email
    try:
        stmt = select(User).where(User.email == email)
        result = db.session.execute(statement=stmt)
    except Exception as exc:
        logger.exception('Error fetching from DB')
        abort(500, 'INTERNAL ERROR')

    userExists = result.fetchone() is not None
    if(userExists):
        abort(400, 'BAD REQUEST')

    # Check password length, limited to 50 due to mitigate 70+ chars error with hash
    if len(password) > 50:
        abort(400, 'passwd_length')

    # Add new user to DB
    new_user = User(
        name=name,
        lastName=lastName,
        email=email,
        password=hashPassword(password),
        roleId=roleId
    )

    # Add user to DB
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as exc:
        logger.exception('Error saving user in DB')
        abort(500, 'Error saving new user')

    # Return response
    return jsonify({"message": "user added successfully"})


@auth.route('/login', methods=['POST'])
def login():
    req = request.json

    # Check if request has enough properties needed
    required_keys = ['email', 'passwd']
    if not all(key in req for key in required_keys):
        abort(400, 'BAD REQUEST')

    # Get request properties
    email = req['email']
    password = req['passwd']

    try:
        # Query to search user by email
        stmt = select(User).where(
            User.email == email
        )
        result = db.session.execute(statement=stmt)
    except Exception as exc:
        logger.exception('Error fetching from DB')
        abort(500, 'INTERNAL ERROR')

    # If no user matched the email in req, return error
    user = result.scalar_one_or_none()
    if(user is None):
        abort(400, 'BAD REQUEST')

    # If password not match, return error
    if (not checkPasswordHash(user.password, password)):
        abort(401, 'wrong_password')

    # Serialize into JSON the DB response Obj (also exclude unwanted info)
    user_serialized = user_schema.dump(user)

    #Create jwt
    try:
        # Set JWT expiration to 24 hours to match cookie expiration
        auth_jwt = encode_auth_jwt(user.id, expires_in=1440)
    except Exception:
        logger.exception('Error generating JWT')
        abort(500, 'INTERNAL ERROR')

    # Generate and return response
    responseData = {
        'loggedIn': True,
        'user': user_serialized
    }

    resp = make_response(jsonify(responseData), 200)
    
    # Determine if we're in production
    is_production = os.getenv('ENV_MODE') == 'production'
    
    resp.set_cookie('access_token', auth_jwt,
                    httponly=True,
                    secure=is_production,  # Only secure in production
                    samesite='Strict' if is_production else 'Lax',
                    max_age=60*60*24,  # 24 hours
                    path='/')  # Available for all paths

    return resp


@auth.route('/isLoggedIn', methods=['GET'])
def isLoggedIn():
    # Try to get token from cookie first, then fallback to Authorization header
    token = request.cookies.get('access_token')
    
    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    # If no token, return not logged in (but don't return 401)
    if not token:
        return jsonify({
            'loggedIn': False,
            'message': 'No authentication token'
        }), 200

    # Check if token is valid
    isLoggedIn = True
    uid = None
    message = 'Authenticated'
    
    try:
        uid = decode_auth_jwt(token)
        if not uid:
            isLoggedIn = False
            message = 'Invalid token'
    except Exception as exc:
        isLoggedIn = False
        error_msg = str(exc)
        if 'invalid_token' in error_msg:
            logger.warning('Invalid token in session check')
            message = 'Invalid token'
        elif 'expired_token' in error_msg:
            logger.info('Expired token in session check')
            message = 'Token expired'
        else:
            message = 'Token validation failed'

    # If token is valid, verify user still exists
    if isLoggedIn and uid:
        try:
            stmt = select(User).where(User.id == uid)
            result = db.session.execute(statement=stmt)
            user = result.scalar_one_or_none()
            if user is None:
                isLoggedIn = False
                message = 'User not found'
        except Exception:
            logger.exception('Error checking user existence in isLoggedIn')
            isLoggedIn = False
            message = 'Database error'

    # Always return 200, but with appropriate loggedIn status
    responseData = {
        'loggedIn': isLoggedIn,
        'message': message
    }
    
    return jsonify(responseData), 200


@auth.route('/getUserRole', methods=['GET'])
@auth_required()
def getRole():
    responseData = {
        "role": g.role
    }
    return jsonify(responseData), 200


@auth.route('/logout', methods=['POST'])
def logout():
    try:
        resp = make_response(jsonify({'loggedIn': False}), 200)
        resp.set_cookie('access_token', '', expires=0)
        return resp
    except Exception:
        logger.error('Error while logging out')
        abort(500)


@auth.route('/protected', methods=['GET'])
@auth_required(["ADMIN"])
def protected():
    try:
        return jsonify({'message': 'Funciona'})
    except Exception as e:
        if isinstance(e, HTTPException):
            abort(e.code, e.description)
        else:
            abort(500)

