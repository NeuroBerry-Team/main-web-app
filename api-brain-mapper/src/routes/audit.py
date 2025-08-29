from datetime import datetime
from flask import Blueprint, request, jsonify, abort, g
from logs.logger import logger

from ..database.dbConnection import db
from ..models.audit_log import AuditLog
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator

# Define router prefix
audit = Blueprint('audit', __name__, url_prefix='/audit')


# ------- Audit Routes -------

@audit.route('/log', methods=['POST'])
@auth_required()
def logAuditAction():
    """
    Log an audit action
    """
    try:
        data = request.get_json()

        # Validate required fields
        validator = InputValidator()
        
        # Validate action field
        action = data.get('action')
        if (not action or not isinstance(action, str) or
                len(action.strip()) == 0):
            return jsonify({
                'success': False,
                'message': 'Invalid action'
            }), 400

        action = validator.sanitize_string(action, max_length=100)
        if len(action) > 100:
            return jsonify({
                'success': False,
                'message': 'Action is too long'
            }), 400

        # Validate entityType field
        entity_type = data.get('entityType')
        if (not entity_type or not isinstance(entity_type, str) or
                len(entity_type.strip()) == 0):
            return jsonify({
                'success': False,
                'message': 'Invalid entity type'
            }), 400
        
        entity_type = validator.sanitize_string(entity_type, max_length=50)
        if len(entity_type) > 50:
            return jsonify({
                'success': False,
                'message': 'Entity type is too long'
            }), 400

        # Create audit log entry
        audit_log = AuditLog(
            userId=g.uid,
            action=action,
            entityType=entity_type,
            entityId=data.get('entityId'),
            timestamp=datetime.utcnow()
        )

        db.session.add(audit_log)
        db.session.commit()

        logger.info(f"Audit log created: {action} by user {g.uid}")

        return jsonify({
            'success': True,
            'message': 'Audit action logged successfully',
            'auditLogId': audit_log.id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error logging audit action: {str(e)}")
        abort(500)


@audit.route('/logs', methods=['GET'])
@auth_required(["ADMIN", "SUPERADMIN"])
def getAuditLogs():
    """
    Get audit logs (admin only)
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        action_filter = request.args.get('action')
        entity_type_filter = request.args.get('entityType')
        user_id_filter = request.args.get('userId', type=int)

        # Build query
        query = AuditLog.query

        if action_filter:
            query = query.filter(AuditLog.action.ilike(f'%{action_filter}%'))

        if entity_type_filter:
            query = query.filter(AuditLog.entityType == entity_type_filter)

        if user_id_filter:
            query = query.filter(AuditLog.userId == user_id_filter)

        # Order by timestamp descending
        query = query.order_by(AuditLog.timestamp.desc())

        # Paginate
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        audit_logs = []
        for log in pagination.items:
            timestamp = (log.timestamp.isoformat()
                         if log.timestamp else None)
            audit_logs.append({
                'id': log.id,
                'userId': log.userId,
                'action': log.action,
                'entityType': log.entityType,
                'entityId': log.entityId,
                'timestamp': timestamp
            })

        return jsonify({
            'success': True,
            'auditLogs': audit_logs,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        abort(500)


@audit.route('/logs/<int:log_id>', methods=['GET'])
@auth_required(["ADMIN", "SUPERADMIN"])
def getAuditLogById(log_id):
    """
    Get specific audit log by ID
    """
    try:
        audit_log = AuditLog.query.get(log_id)

        if not audit_log:
            return jsonify({
                'success': False,
                'message': 'Audit log not found'
            }), 404

        return jsonify({
            'success': True,
            'auditLog': {
                'id': audit_log.id,
                'userId': audit_log.userId,
                'action': audit_log.action,
                'entityType': audit_log.entityType,
                'entityId': audit_log.entityId,
                'timestamp': (audit_log.timestamp.isoformat()
                              if audit_log.timestamp else None)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving audit log {log_id}: {str(e)}")
        abort(500)
