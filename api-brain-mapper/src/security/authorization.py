from functools import wraps
from flask import g, abort, current_app
from sqlalchemy import select
from ..models.user import User
from ..models.scene import Scene
from ..models.inference import Inference
from ..database.dbConnection import db


class AuthorizationChecker:
    """Authorization utilities to prevent IDOR attacks"""
    
    @staticmethod
    def check_user_owns_resource(resource_type, resource_id, user_id):
        """
        Check if user owns the specified resource
        
        Args:
            resource_type: Type of resource ('scene', 'inference', etc.)
            resource_id: ID of the resource
            user_id: ID of the user
            
        Returns:
            bool: True if user owns resource
            
        Raises:
            ValueError: If resource type is not supported
        """
        if resource_type == 'scene':
            return AuthorizationChecker._check_scene_ownership(
                resource_id, user_id
            )
        elif resource_type == 'inference':
            return AuthorizationChecker._check_inference_ownership(
                resource_id, user_id
            )
        elif resource_type == 'user':
            return AuthorizationChecker._check_user_access(
                resource_id, user_id
            )
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    @staticmethod
    def _check_scene_ownership(scene_id, user_id):
        """Check if user owns the scene"""
        try:
            stmt = select(Scene).where(
                Scene.id == scene_id,
                Scene.user_id == user_id
            )
            result = db.session.execute(stmt)
            scene = result.scalar_one_or_none()
            return scene is not None
        except Exception:
            current_app.logger.error(
                f"Error checking scene ownership: scene_id={scene_id}, "
                f"user_id={user_id}"
            )
            return False
    
    @staticmethod
    def _check_inference_ownership(inference_id, user_id):
        """Check if user owns the inference through scene ownership"""
        try:
            # Get inference with associated scene
            stmt = select(Inference).join(Scene).where(
                Inference.id == inference_id,
                Scene.user_id == user_id
            )
            result = db.session.execute(stmt)
            inference = result.scalar_one_or_none()
            return inference is not None
        except Exception:
            current_app.logger.error(
                f"Error checking inference ownership: "
                f"inference_id={inference_id}, user_id={user_id}"
            )
            return False
    
    @staticmethod
    def _check_user_access(target_user_id, current_user_id):
        """Check if user can access another user's data"""
        # Users can always access their own data
        if target_user_id == current_user_id:
            return True
        
        # Check if current user is admin
        try:
            stmt = select(User).where(User.id == current_user_id)
            result = db.session.execute(stmt)
            current_user = result.scalar_one_or_none()
            
            if current_user and hasattr(current_user, 'role'):
                return current_user.role.name == 'ADMIN'
            
            return False
        except Exception:
            current_app.logger.error(
                "Error checking user access: "
                f"target_user_id={target_user_id}, "
                f"current_user_id={current_user_id}"
            )
            return False
    
    @staticmethod
    def get_user_resources(resource_type, user_id, limit=None, offset=None):
        """
        Get resources that belong to a specific user
        
        Args:
            resource_type: Type of resource
            user_id: User ID
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            Query result with user's resources
        """
        if resource_type == 'scene':
            stmt = select(Scene).where(Scene.user_id == user_id)
        elif resource_type == 'inference':
            stmt = (select(Inference).join(Scene)
                    .where(Scene.user_id == user_id))
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
        
        # Apply pagination
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        
        return db.session.execute(stmt)
    
    @staticmethod
    def validate_resource_access(resource_type, resource_id,
                                 required_permission='read'):
        """
        Validate that current user can access the resource
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            required_permission: Required permission
                ('read', 'write', 'delete')
            
        Raises:
            403: If access is denied
            404: If resource doesn't exist or user doesn't have access
        """
        # Get current user from request context
        current_user_id = getattr(g, 'user_id', None)
        
        if not current_user_id:
            abort(401, 'Authentication required')
        
        # Check if user owns the resource
        if not AuthorizationChecker.check_user_owns_resource(
            resource_type, resource_id, current_user_id
        ):
            # Return 404 to hide resource existence from unauthorized users
            abort(404, 'Resource not found')
        
        # Additional permission checks could go here
        # For now, ownership grants all permissions
        pass


def require_resource_ownership(resource_type):
    """
    Decorator to ensure user owns the specified resource
    
    Args:
        resource_type: Type of resource to check
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get resource ID from URL parameters or kwargs
            resource_id = kwargs.get(f'{resource_type}_id') or kwargs.get('id')
            
            if not resource_id:
                abort(400, 'Resource ID required')
            
            # Validate access
            AuthorizationChecker.validate_resource_access(
                resource_type, resource_id
            )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_user_access(allow_self=True, allow_admin=True):
    """
    Decorator to ensure user can access another user's data
    
    Args:
        allow_self: Allow users to access their own data
        allow_admin: Allow admins to access any user's data
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            target_user_id = kwargs.get('user_id') or kwargs.get('id')
            current_user_id = getattr(g, 'user_id', None)
            
            if not current_user_id:
                abort(401, 'Authentication required')
            
            if not target_user_id:
                abort(400, 'User ID required')
            
            # Check if access is allowed
            access_granted = False
            
            if allow_self and target_user_id == current_user_id:
                access_granted = True
            
            if allow_admin and not access_granted:
                # Check admin status
                try:
                    stmt = select(User).where(User.id == current_user_id)
                    result = db.session.execute(stmt)
                    current_user = result.scalar_one_or_none()
                    
                    if current_user and hasattr(current_user, 'role'):
                        access_granted = current_user.role.name == 'ADMIN'
                except Exception:
                    current_app.logger.error(
                        f"Error checking admin status for user "
                        f"{current_user_id}"
                    )
            
            if not access_granted:
                abort(403, 'Access denied')
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def filter_user_resources(query, resource_type, user_id):
    """
    Filter query to only return resources owned by the user
    
    Args:
        query: SQLAlchemy query object
        resource_type: Type of resource
        user_id: User ID
        
    Returns:
        Filtered query
    """
    if resource_type == 'scene':
        return query.where(Scene.user_id == user_id)
    elif resource_type == 'inference':
        return query.join(Scene).where(Scene.user_id == user_id)
    else:
        # For unknown resource types, return empty result for safety
        return query.where(False)
