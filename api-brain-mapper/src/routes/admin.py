from flask import Blueprint, jsonify, abort, g, request
from logs.logger import logger
from sqlalchemy import select, func
from datetime import datetime

from ..models.user import User
from ..models.role import Role
from ..models.inference import Inference
from ..models.user_session import UserSession
from ..database.dbConnection import db
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator

# Define router prefix
admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/users", methods=["GET"])
@auth_required(["ADMIN", "SUPERADMIN"])
def get_all_users():
    """
    Get all users with their basic information and statistics
    Admin and SuperAdmin only
    """
    try:
        # Query all users with their roles
        stmt = select(User).order_by(User.id)
        result = db.session.execute(stmt)
        all_users = result.scalars().all()

        users_data = []
        for user in all_users:
            # Get inference count for each user
            inference_count = (
                db.session.query(func.count(Inference.id))
                .filter(Inference.userId == user.id)
                .scalar()
            )

            # Get last login
            last_login = (
                db.session.query(func.max(UserSession.loginAt))
                .filter(UserSession.userId == user.id)
                .scalar()
            )

            users_data.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "lastName": user.lastName,
                    "email": user.email,
                    "role": {
                        "id": user.role.id,
                        "name": user.role.name,
                    },
                    "inferenceCount": inference_count or 0,
                    "lastLogin": last_login.isoformat() if last_login else None,
                }
            )

        logger.info(f"Admin user {g.uid} retrieved all users list")

        return (
            jsonify(
                {
                    "success": True,
                    "users": users_data,
                    "total": len(users_data),
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(f"Error retrieving all users: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


@admin.route("/roles", methods=["GET"])
@auth_required(["ADMIN", "SUPERADMIN"])
def get_all_roles():
    """
    Get all available roles
    Admin and SuperAdmin only
    """
    try:
        stmt = select(Role).order_by(Role.id)
        result = db.session.execute(stmt)
        all_roles = result.scalars().all()

        roles_data = [{"id": role.id, "name": role.name} for role in all_roles]

        return (
            jsonify(
                {
                    "success": True,
                    "roles": roles_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(f"Error retrieving roles: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


@admin.route("/users/<int:user_id>/role", methods=["PUT"])
@auth_required(["ADMIN", "SUPERADMIN"])
def update_user_role(user_id):
    """
    Update a user's role
    Admin and SuperAdmin only
    """
    try:
        # Validate request
        data = InputValidator.validate_json_request(request, ["roleId"])
        new_role_id = InputValidator.validate_integer(
            data["roleId"], "Role ID", min_value=1
        )

        # Get the user
        stmt = select(User).where(User.id == user_id)
        result = db.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Prevent modifying SUPERADMIN users (only SUPERADMIN can modify SUPERADMIN)
        if user.role.name == "SUPERADMIN" and g.role != "SUPERADMIN":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Only SUPERADMIN can modify SUPERADMIN users",
                    }
                ),
                403,
            )

        # Verify the new role exists
        stmt = select(Role).where(Role.id == new_role_id)
        result = db.session.execute(stmt)
        new_role = result.scalar_one_or_none()

        if not new_role:
            return jsonify({"success": False, "message": "Invalid role"}), 400

        # Prevent changing TO SUPERADMIN role unless user is SUPERADMIN
        if new_role.name == "SUPERADMIN" and g.role != "SUPERADMIN":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Only SUPERADMIN can assign SUPERADMIN role",
                    }
                ),
                403,
            )

        old_role = user.role.name
        user.roleId = new_role_id
        db.session.commit()

        logger.info(
            f"Admin user {g.uid} changed role of user {user_id} from {old_role} to {new_role.name}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User role updated successfully",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "lastName": user.lastName,
                        "email": user.email,
                        "role": {"id": user.role.id, "name": user.role.name},
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(f"Error updating user role: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@admin.route("/users/<int:user_id>", methods=["DELETE"])
@auth_required(["ADMIN", "SUPERADMIN"])
def delete_user(user_id):
    """
    Delete a user account
    Admin and SuperAdmin only
    """
    try:
        # Get the user
        stmt = select(User).where(User.id == user_id)
        result = db.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Prevent deletion of SUPERADMIN accounts
        if user.role.name == "SUPERADMIN":
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "SUPERADMIN accounts cannot be deleted",
                    }
                ),
                403,
            )

        # Prevent admins from deleting themselves
        if user.id == g.uid:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "You cannot delete your own account",
                    }
                ),
                400,
            )

        user_email = user.email
        user_name = f"{user.name} {user.lastName}"

        # Close all user sessions first
        UserSession.close_all_sessions(user_id)

        # Delete the user (cascade will handle related records)
        db.session.delete(user)
        db.session.commit()

        logger.info(
            f"Admin user {g.uid} deleted user {user_id} ({user_email})"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"User {user_name} deleted successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(f"Error deleting user: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@admin.route("/users/<int:user_id>/stats", methods=["GET"])
@auth_required(["ADMIN", "SUPERADMIN"])
def get_user_statistics(user_id):
    """
    Get detailed statistics for a specific user
    Admin and SuperAdmin only
    """
    try:
        # Verify user exists
        stmt = select(User).where(User.id == user_id)
        result = db.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        from datetime import timedelta

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Basic analysis statistics
        total_analyses = (
            db.session.query(Inference).filter_by(userId=user_id).count()
        )

        analyses_this_week = (
            db.session.query(Inference)
            .filter(Inference.userId == user_id, Inference.createdOn >= week_ago)
            .count()
        )

        # Session statistics
        last_login = (
            db.session.query(func.max(UserSession.loginAt))
            .filter_by(userId=user_id)
            .scalar()
        )

        active_days_count = (
            db.session.query(func.count(func.distinct(func.date(UserSession.loginAt))))
            .filter(
                UserSession.userId == user_id,
                UserSession.loginAt >= month_ago,
            )
            .scalar()
        )

        # Calculate login streak
        from ..routes.users import calculate_login_streak

        login_streak = calculate_login_streak(user_id)

        return (
            jsonify(
                {
                    "success": True,
                    "userId": user_id,
                    "userName": f"{user.name} {user.lastName}",
                    "totalAnalyses": total_analyses,
                    "analysesThisWeek": analyses_this_week,
                    "lastLogin": last_login.isoformat() if last_login else None,
                    "activeDays": active_days_count or 0,
                    "loginStreak": login_streak,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(f"Error retrieving user statistics: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
