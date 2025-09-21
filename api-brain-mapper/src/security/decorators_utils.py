from functools import wraps
from flask import request, abort, g
from werkzeug.exceptions import HTTPException
from sqlalchemy import select
from ..security.jwt_utils import decode_auth_jwt
from ..models.user import User
from ..schemas.user import user_schema
from ..database.dbConnection import db


def auth_required(requiredRoles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Try to get token from cookie first, then fallback to header
            # for backward compatibility
            token = request.cookies.get("access_token")

            # Fallback to header-based token (for API clients or transition)
            if not token:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]

            # If still no token found, return unauthorized
            if not token:
                abort(401, "UNAUTHORIZED: No authentication token provided")

            try:
                uid = decode_auth_jwt(token)
                if not uid:
                    abort(401, "UNAUTHORIZED: Invalid token")
            except Exception as e:
                if isinstance(e, HTTPException):
                    abort(e.code, e.description)
                else:
                    # More specific error handling
                    error_msg = str(e)
                    if "expired_token" in error_msg:
                        abort(401, "UNAUTHORIZED: Token has expired")
                    elif "invalid_token" in error_msg:
                        abort(401, "UNAUTHORIZED: Invalid token")
                    else:
                        abort(401, "UNAUTHORIZED: Token validation failed")

            # Check if user exists
            try:
                stmt = select(User).where(User.id == uid)
                result = db.session.execute(statement=stmt)
                user = result.scalar_one_or_none()

                if user is None:
                    abort(401, "UNAUTHORIZED: User not found")
            except Exception:
                abort(500, "INTERNAL ERROR: Database error")

            # Store the uid, role, and user info in g so it's accessible
            # throughout the request
            g.uid = uid
            g.role = user.role.name
            g.user_name = user.name
            g.user_last_name = user.lastName
            g.user_email = user.email

            # Check role permissions if required
            if requiredRoles is not None:
                if user.role.name not in requiredRoles:
                    required_roles_str = ", ".join(requiredRoles)
                    error_msg = f"FORBIDDEN: Required role(s): {required_roles_str}"
                    abort(403, error_msg)

            return f(*args, **kwargs)

        return decorated

    return decorator
