import os
import json
from flask import Blueprint, request, redirect, jsonify, abort, g, make_response
from werkzeug.exceptions import HTTPException
from logs.logger import logger

from sqlalchemy import select
from ..models.user import User
from ..models.user_session import UserSession
from ..schemas.user import user_schema
from ..database.dbConnection import db

from ..security.jwt_utils import *
from ..security.decorators_utils import auth_required
from ..security.crypto_utils import *
from ..security.rate_limiter import (rate_limit_login, check_account_lockout,
                                     handle_failed_login)
from ..security.input_validation import InputValidator
from ..security.csrf_protection import get_csrf_token

# Open file with available roles
rolesFile = os.path.join(os.getcwd(), "src/database/reference-data/ROLES.json")
with open(rolesFile) as f:
  availableRoles = json.load(f)

# Setup blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/addUser', methods=['POST'])
@auth_required(["ADMIN"])
def addUser():
    # Validate request structure
    req = InputValidator.validate_json_request(
        request, ['name', 'lastName', 'email', 'passwd', 'roleId']
    )

    # Validate and sanitize input fields
    name = InputValidator.validate_name(req['name'], "First name")
    lastName = InputValidator.validate_name(req['lastName'], "Last name")
    email = InputValidator.validate_email_format(req['email'])
    password = InputValidator.validate_password(req['passwd'])
    roleId = InputValidator.validate_integer(
        req['roleId'], "Role ID", min_value=1
    )

    # Search for existent user with same email
    try:
        stmt = select(User).where(User.email == email)
        result = db.session.execute(statement=stmt)
    except Exception:
        logger.exception('Error fetching from DB')
        abort(500, 'INTERNAL ERROR')

    userExists = result.fetchone() is not None
    if userExists:
        abort(400, 'Email already exists')

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
    except Exception:
        logger.exception('Error saving user in DB')
        abort(500, 'Error saving new user')

    # Return response
    return jsonify({"message": "user added successfully"})


@auth.route('/register', methods=['POST'])
def register():
    """Public user registration endpoint"""
    # Validate request structure
    req = InputValidator.validate_json_request(
        request, ['name', 'lastName', 'email', 'password']
    )

    # Validate and sanitize input fields
    name = InputValidator.validate_name(req['name'], field_name="Nombre", min_length=2, max_length=100)
    lastName = InputValidator.validate_name(req['lastName'], field_name="Apellido", min_length=2, max_length=100)
    email = InputValidator.validate_email_format(req['email'])
    password = InputValidator.validate_password(req['password'])
    
    # Set default role for new users (AI_USER)
    default_role_name = "AI_USER"
    
    # Check if email already exists
    try:
        stmt = select(User).where(User.email == email)
        result = db.session.execute(statement=stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            abort(409, 'User with this email already exists')
    except Exception:
        logger.exception('Error checking existing user during registration')
        abort(500, 'Registration failed')

    # Find the default role
    try:
        from ..models.role import Role
        stmt = select(Role).where(Role.name == default_role_name)
        result = db.session.execute(stmt)
        default_role = result.scalar_one_or_none()
        
        if not default_role:
            logger.error(f'Default role {default_role_name} not found')
            abort(500, 'Registration failed - invalid role configuration')
            
        roleId = default_role.id
    except Exception:
        logger.exception('Error finding default role during registration')
        abort(500, 'Registration failed')

    # Create new user
    try:
        # Hash password 
        hashed_password = hashPassword(password)
        
        # Create user object
        new_user = User(
            name=name,
            lastName=lastName,
            email=email,
            password=hashed_password,
            roleId=roleId
        )

        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f'New user registered: {email}')
        
        # Return success (don't auto-login for security)
        return jsonify({
            "message": "¡Registro exitoso! Por favor inicia sesión con tus credenciales."
        }), 201
        
    except Exception:
        logger.exception('Error creating user during registration')
        db.session.rollback()
        abort(500, 'Registration failed')


@auth.route('/login', methods=['POST'])
@rate_limit_login(max_attempts=5, window_minutes=15)
def login():
    # Validate request structure
    req = InputValidator.validate_json_request(
        request, ['email', 'passwd']
    )

    # Validate and normalize email
    email = InputValidator.validate_email_format(req['email'])
    password = req['passwd']
    
    # Basic password validation
    if not password or len(password.strip()) == 0:
        abort(400, 'Password is required')
    
    # Sanitize password (remove null bytes, limit length)
    password = InputValidator.sanitize_string(password, max_length=200)
    
    # Check if account is locked (60 minutes if too many attempts failed)
    check_account_lockout(email)

    try:
        # Query to search user by email
        stmt = select(User).where(
            User.email == email
        )
        result = db.session.execute(statement=stmt)
    except Exception:
        logger.exception('Error fetching from DB')
        abort(500, 'INTERNAL ERROR')

    # If no user matched the email in req, return standardized error
    user = result.scalar_one_or_none()
    if user is None: # TODO: Should only lock if the email matches a user but the password is wrong
        # Handle failed login for rate limiting
        handle_failed_login(email)
        # Use same error as wrong password to prevent username enumeration
        abort(401, 'Invalid email or password')

    # If password not match, return error
    if not checkPasswordHash(user.password, password):
        # Handle failed login for rate limiting
        handle_failed_login(email)
        abort(401, 'Invalid email or password')

    # Serialize into JSON the DB response Obj (also exclude unwanted info)
    user_serialized = user_schema.dump(user)

    # Create jwt
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
    
    # Add login session to DB
    try:
        user_session = UserSession.create_session(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(user_session)
        db.session.commit()
    except Exception:
        logger.exception('Error creating user session')
        db.session.rollback()
    
    # Still login if no login session could be added

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
@auth_required()
def logout():
    try:
        resp = make_response(jsonify({'loggedIn': False}), 200)
        resp.set_cookie('access_token', '', expires=0)

        # Close user session
        # TODO: Add session ID to JWT token to close only one session
        UserSession.close_all_sessions(g.uid)
        db.session.commit()

        return resp
    except Exception:
        logger.error('Error while logging out')
        db.session.rollback()
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


@auth.route('/csrf-token', methods=['GET'])
def get_csrf_token_endpoint():
    """Get CSRF token for frontend"""
    try:
        token = get_csrf_token()
        return jsonify({'csrf_token': token}), 200
    except Exception:
        logger.exception('Error generating CSRF token')
        abort(500, 'Error generating CSRF token')

