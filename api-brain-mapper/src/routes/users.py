from flask import Blueprint, request, jsonify, abort, g
from logs.logger import logger
from datetime import datetime, timedelta
from sqlalchemy import func, distinct, select
import os

from ..models.inference import Inference
from ..models.user_session import UserSession
from ..models.user import User
from ..database.dbConnection import db
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator
from ..security.crypto_utils import hashPassword, checkPasswordHash
from ..cloudServices.minioConnections import getMinioClient


# Define router prefix
users = Blueprint("users", __name__, url_prefix="/users")


def generate_presigned_url_from_s3_url(s3_url, expires_hours=24):
    """
    Generate a presigned URL from an S3 URL stored in database
    
    Args:
        s3_url: The S3 URL (e.g., http://localhost:9000/bucket/path/to/file.jpg)
        expires_hours: Hours until the presigned URL expires (default: 24)
    
    Returns:
        Presigned URL string or original URL if generation fails
    """
    if not s3_url:
        return None
    
    try:
        # Extract bucket and object key from S3 URL
        s3_live_base_url = os.getenv("S3_LIVE_BASE_URL")
        
        if not s3_url.startswith(s3_live_base_url):
            logger.warning(f"URL doesn't match expected S3 base: {s3_url}")
            return s3_url
        
        # Remove base URL to get bucket/object_key
        path = s3_url.replace(s3_live_base_url, "")
        
        # Split into bucket and object_key
        parts = path.split("/", 1)
        if len(parts) != 2:
            logger.warning(f"Invalid S3 URL format: {s3_url}")
            return s3_url
        
        bucket, object_key = parts
        
        # Generate presigned URL
        minioClient = getMinioClient()
        presigned_url = minioClient.presigned_get_object(
            bucket,
            object_key,
            expires=timedelta(hours=expires_hours)
        )
        
        return presigned_url
        
    except Exception as e:
        logger.error(f"Error generating presigned URL for {s3_url}: {str(e)}")
        return s3_url  # Return original URL as fallback


@users.route("/stats", methods=["GET"])
@auth_required()
def get_user_stats():
    """
    Get comprehensive user statistics including:
    - Total analyses count
    - Recent analyses (this week)
    - Images processed
    - Last login time
    - Active days this month
    - Login streak
    - Recent analysis history
    - Login activity logs
    """
    try:
        user_id = g.uid
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Basic analysis statistics
        total_analyses = db.session.query(Inference).filter_by(userId=user_id).count()

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
            db.session.query(func.count(distinct(func.date(UserSession.loginAt))))
            .filter(UserSession.userId == user_id, UserSession.loginAt >= month_ago)
            .scalar()
            or 0
        )

        # Recent analyses (last 10)
        recent_analyses = (
            db.session.query(Inference)
            .filter_by(userId=user_id)
            .order_by(Inference.createdOn.desc())
            .limit(10)
            .all()
        )

        # Recent sessions (last 10)
        recent_sessions = (
            db.session.query(UserSession)
            .filter_by(userId=user_id)
            .order_by(UserSession.loginAt.desc())
            .limit(10)
            .all()
        )

        # Calculate login streak
        login_streak = calculate_login_streak(user_id)

        # Format response data
        stats = {
            "success": True,
            "summary": {
                "totalAnalyses": total_analyses,
                "analysesThisWeek": analyses_this_week,
                "imagesProcessed": total_analyses,  # Same as analyses for now
                "lastLogin": last_login.isoformat() if last_login else None,
                "activeDaysThisMonth": active_days_count,
                "currentLoginStreak": login_streak,
            },
            "recentAnalyses": [
                {
                    "id": analysis.id,
                    "name": analysis.name,
                    "result": getattr(analysis, "result", analysis.name),
                    "baseImageUrl": generate_presigned_url_from_s3_url(analysis.baseImageUrl),
                    "generatedImageUrl": generate_presigned_url_from_s3_url(analysis.generatedImageUrl),
                    "metadataUrl": analysis.metadataUrl,
                    "createdOn": analysis.createdOn.isoformat() + "Z",
                    "modelId": analysis.modelId,
                    # Add confidence if available (placeholder for now)
                    "confidence": getattr(analysis, "confidence", 0.95),
                }
                for analysis in recent_analyses
            ],
            "recentSessions": [
                {
                    "id": session.id,
                    "loginAt": session.loginAt.isoformat() + "Z",
                    "logoutAt": (
                        session.logoutAt.isoformat() + "Z" if session.logoutAt else None
                    ),
                    "ipAddress": session.ipAddress,
                    "isActive": session.is_active,
                }
                for session in recent_sessions
            ],
        }

        logger.info(f"User stats retrieved for user {user_id}")
        return jsonify(stats), 200

    except Exception:
        logger.exception(f"Error getting user stats for user {g.uid}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve user statistics"}),
            500,
        )


def calculate_login_streak(user_id):
    """Calculate the current login streak for a user"""
    try:
        # Get distinct login dates for the user, ordered by date descending
        login_dates = (
            db.session.query(func.date(UserSession.loginAt).label("login_date"))
            .filter_by(userId=user_id)
            .distinct()
            .order_by(func.date(UserSession.loginAt).desc())
            .all()
        )

        if not login_dates:
            return 0

        streak = 0
        current_date = datetime.utcnow().date()

        for date_row in login_dates:
            login_date = date_row.login_date

            # If this is the first date and it's today or yesterday, start counting
            if streak == 0:
                if login_date == current_date:
                    streak = 1
                    current_date = current_date - timedelta(days=1)
                elif login_date == current_date - timedelta(days=1):
                    streak = 1
                    current_date = login_date - timedelta(days=1)
                else:
                    break  # No recent activity
            else:
                # Check if this date continues the streak
                if login_date == current_date:
                    streak += 1
                    current_date = current_date - timedelta(days=1)
                else:
                    break  # Streak is broken

        return streak

    except Exception:
        logger.exception(f"Error calculating login streak for user {user_id}")
        return 0


@users.route("/inferences", methods=["GET"])
@auth_required()
def get_user_inferences():
    """
    Get paginated list of user's inferences
    Query parameters:
    - page: page number (default: 1)
    - limit: items per page (default: 20, max: 100)
    - id: specific inference ID to fetch
    """
    try:
        user_id = g.uid

        # Check if requesting specific inference
        inference_id = request.args.get("id")
        if inference_id:
            inference = (
                db.session.query(Inference)
                .filter_by(userId=user_id, id=inference_id)
                .first()
            )
            # TODO: Let an admin/superadmin see specific inference of any user

            if not inference:
                return jsonify({"success": False, "error": "Inference not found"}), 404

            return (
                jsonify(
                    {
                        "success": True,
                        "inference": {
                            "id": inference.id,
                            "name": inference.name,
                            "result": getattr(inference, "result", inference.name),
                            "baseImageUrl": generate_presigned_url_from_s3_url(inference.baseImageUrl),
                            "generatedImageUrl": generate_presigned_url_from_s3_url(inference.generatedImageUrl),
                            "metadataUrl": inference.metadataUrl,
                            "createdOn": inference.createdOn.isoformat() + "Z",
                            "modelId": inference.modelId,
                            "confidence": getattr(inference, "confidence", 0.95),
                        },
                    }
                ),
                200,
            )

        # Pagination parameters
        page = int(request.args.get("page", 1))
        limit = min(int(request.args.get("limit", 20)), 100)
        offset = (page - 1) * limit

        # Get total count
        total_count = db.session.query(Inference).filter_by(userId=user_id).count()

        # Get paginated inferences
        inferences = (
            db.session.query(Inference)
            .filter_by(userId=user_id)
            .order_by(Inference.createdOn.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1

        return (
            jsonify(
                {
                    "success": True,
                    "inferences": [
                        {
                            "id": inference.id,
                            "name": inference.name,
                            "result": getattr(inference, "result", inference.name),
                            "baseImageUrl": generate_presigned_url_from_s3_url(inference.baseImageUrl),
                            "generatedImageUrl": generate_presigned_url_from_s3_url(inference.generatedImageUrl),
                            "metadataUrl": inference.metadataUrl,
                            "createdOn": inference.createdOn.isoformat() + "Z",
                            "modelId": inference.modelId,
                            "confidence": getattr(inference, "confidence", 0.95),
                        }
                        for inference in inferences
                    ],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "total_pages": total_pages,
                        "has_next": has_next,
                        "has_prev": has_prev,
                    },
                }
            ),
            200,
        )

    except ValueError:
        return (
            jsonify({"success": False, "error": "Invalid pagination parameters"}),
            400,
        )
    except Exception:
        logger.exception(f"Error getting inferences for user {g.uid}")
        return (
            jsonify({"success": False, "error": "Failed to retrieve inferences"}),
            500,
        )


@users.route("/update-profile", methods=["PUT"])
@auth_required()
def update_profile():
    """
    Update user profile information (name, lastName, email)
    """
    try:
        # Validate JSON request and required fields
        data = InputValidator.validate_json_request(request, ["name", "lastName", "email"])

        # Get current user
        stmt = select(User).where(User.id == g.uid)
        result = db.session.execute(statement=stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Validate fields using InputValidator
        name = InputValidator.validate_name(data["name"], "Name")
        last_name = InputValidator.validate_name(data["lastName"], "Last name")
        email = InputValidator.validate_email_format(data["email"])

        # Check if email is already taken by another user
        if email != user.email:
            stmt = select(User).where(User.email == email)
            result = db.session.execute(statement=stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                return jsonify({"success": False, "message": "Email is already in use"}), 400

        # Update user information
        user.name = name
        user.lastName = last_name
        user.email = email
        
        db.session.commit()
        
        logger.info(f"User {g.uid} updated their profile information")
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "lastName": user.lastName,
                "email": user.email,
                "role": user.role.name
            }
        }), 200

    except Exception as e:
        logger.exception(f"Error updating profile for user {g.uid}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@users.route("/change-password", methods=["PUT"])
@auth_required()
def change_password():
    """
    Change user password with current password verification
    """
    try:
        # Validate JSON request and required fields
        data = InputValidator.validate_json_request(request, ["currentPassword", "newPassword"])
        
        current_password = data["currentPassword"]
        new_password = data["newPassword"]

        # Get current user
        stmt = select(User).where(User.id == g.uid)
        result = db.session.execute(statement=stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Verify current password
        if not checkPasswordHash(user.password, current_password):
            return jsonify({"success": False, "message": "Current password is incorrect"}), 400

        # Validate new password using InputValidator
        new_password = InputValidator.validate_password(new_password)

        # Update password
        user.password = hashPassword(new_password)
        db.session.commit()
        
        logger.info(f"User {g.uid} changed their password")
        
        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        }), 200

    except Exception as e:
        logger.exception(f"Error changing password for user {g.uid}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@users.route("/delete-account", methods=["DELETE"])
@auth_required()
def delete_account():
    """
    Delete user account permanently
    """
    try:
        # Get current user
        stmt = select(User).where(User.id == g.uid)
        result = db.session.execute(statement=stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Prevent deletion of SUPERADMIN accounts
        if user.role.name == 'SUPERADMIN':
            return jsonify({
                "success": False,
                "message": "SUPERADMIN accounts cannot be deleted"
            }), 403

        user_id = user.id
        user_email = user.email
        
        # Close all user sessions first
        UserSession.close_all_sessions(user_id)
        
        # Delete the user (this will cascade delete related records due to foreign key constraints)
        db.session.delete(user)
        db.session.commit()
        
        logger.info(f"User account {user_email} (ID: {user_id}) was permanently deleted")
        
        return jsonify({
            "success": True,
            "message": "Account deleted successfully"
        }), 200

    except Exception as e:
        logger.exception(f"Error deleting account for user {g.uid}: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500
