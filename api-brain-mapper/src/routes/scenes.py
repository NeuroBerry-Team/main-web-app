import os
import json
import uuid
import datetime
from dotenv import load_dotenv

from flask import Blueprint, request, jsonify, abort, g
from logs.logger import logger

from ..database.dbConnection import db
from ..models.scene import Scene
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator
from ..security.file_upload_security import FileUploadSecurity
from ..security.rate_limiter import rate_limit_api, rate_limit_file_upload
from ..cloudServices.minioConnections import getMinioClient

load_dotenv()

# Define router prefix
scenes = Blueprint('scenes', __name__, url_prefix='/scenes')


# ------- All the routes -------
@scenes.route('/getScenePresignedUrls', methods=['GET'])
@auth_required()
@rate_limit_file_upload(max_attempts=10, window_minutes=60)
def getScenePresignedUrls():
    # Validate user can upload scenes (only authenticated users)
    if not g.uid:
        abort(401, 'Authentication required')
    
    # Instantiate a minio client
    minioClient = getMinioClient()

    # Create unique foldername
    folderName = str(uuid.uuid4().hex)

    # Configure s3 constants for scenes(dataset) bucket
    s3Bucket = os.getenv('S3_BUCKET_DATASET')
    s3LiveUrl = os.getenv('S3_LIVE_BASE_URL') + s3Bucket
    presignedExpTime = int(os.getenv('S3_PRESIGNED_EXPIRATION'))

    # Generate live and upload urls for the scene image
    try:
        imgObjectKey = f"dataset/{folderName}/img.jpg"
        imgLiveUrl = f"{s3LiveUrl}/{imgObjectKey}"
        imgUploadUrl = minioClient.presigned_put_object(
            s3Bucket,
            imgObjectKey,
            expires=datetime.timedelta(seconds=presignedExpTime)
        )
    except Exception:
        logger.exception('S3 presigned error')
        abort(500, 'Error getting presigned url for img')

    # Generate live and upload urls for the scene map
    try:
        mapObjectKey = f"dataset/{folderName}/map.txt"
        mapLiveUrl = f"{s3LiveUrl}/{mapObjectKey}"
        mapUploadUrl = minioClient.presigned_put_object(
            s3Bucket,
            mapObjectKey,
            expires=datetime.timedelta(seconds=presignedExpTime)
        )
    except Exception:
        logger.error('S3 presigned error')
        abort(500, 'Error getting presigned url for txt')

    # Setup response data
    responseData = {
        "mapUrls": {"uploadURL": mapUploadUrl, "liveURL": mapLiveUrl},
        "imgUrls": {"uploadURL": imgUploadUrl, "liveURL": imgLiveUrl}
    }

    return jsonify(responseData), 200


@scenes.route('/addScene', methods=['POST'])
@auth_required()
@rate_limit_api(max_attempts=50, window_minutes=60)
def addScene():
    # Validate request structure
    req = InputValidator.validate_json_request(
        request, ['name', 'imageUrl', 'mapUrl']
    )

    # Validate and sanitize input fields
    name = InputValidator.validate_name(
        req['name'], "Scene name", max_length=200
    )
    imageUrl = InputValidator.sanitize_string(req['imageUrl'], max_length=500)
    mapUrl = InputValidator.sanitize_string(req['mapUrl'], max_length=500)
    
    # Validate URLs are from expected S3 bucket
    expected_bucket = os.getenv('S3_BUCKET_DATASET')
    expected_base_url = os.getenv('S3_LIVE_BASE_URL') + expected_bucket
    
    if not imageUrl.startswith(expected_base_url):
        abort(400, 'Invalid image URL')
    if not mapUrl.startswith(expected_base_url):
        abort(400, 'Invalid map URL')

    new_scene = Scene(
        userId=g.uid,  # Use authenticated user's ID
        name=name,
        imageUrl=imageUrl,
        mapUrl=mapUrl,
        uploadedOn=datetime.datetime.now()
    )

    try:
        db.session.add(new_scene)
        db.session.commit()
    except Exception:
        logger.exception('Error saving scene in DB')
        abort(500, 'Error while saving scene')

    return jsonify({"message": "scene added successfully"}), 200


@scenes.route('/getUserScenes', methods=['GET'])
@auth_required()
def getUserScenes():
    """Get scenes for the authenticated user only"""
    try:
        # Only return scenes belonging to the authenticated user
        from sqlalchemy import select
        stmt = select(Scene).where(Scene.userId == g.uid)
        result = db.session.execute(stmt)
        user_scenes = result.scalars().all()
        
        # Serialize scenes (you may want to create a scene schema)
        scenes_data = []
        for scene in user_scenes:
            scenes_data.append({
                'id': scene.id,
                'name': scene.name,
                'imageUrl': scene.imageUrl,
                'mapUrl': scene.mapUrl,
                'uploadedOn': (scene.uploadedOn.isoformat()
                               if scene.uploadedOn else None)
            })
        
        return jsonify({'scenes': scenes_data}), 200
        
    except Exception:
        logger.exception('Error fetching user scenes')
        abort(500, 'Error fetching scenes')


@scenes.route('/deleteScene/<int:scene_id>', methods=['DELETE'])
@auth_required()
def deleteScene(scene_id):
    """Delete a scene - only if user owns it"""
    try:
        # Check if scene exists and belongs to user
        from sqlalchemy import select
        stmt = select(Scene).where(
            Scene.id == scene_id,
            Scene.userId == g.uid  # Ensure user owns the scene
        )
        result = db.session.execute(stmt)
        scene = result.scalar_one_or_none()
        
        if not scene:
            abort(404, 'Scene not found')
        
        db.session.delete(scene)
        db.session.commit()
        
        return jsonify({'message': 'Scene deleted successfully'}), 200
        
    except Exception:
        logger.exception(f'Error deleting scene {scene_id}')
        abort(500, 'Error deleting scene')