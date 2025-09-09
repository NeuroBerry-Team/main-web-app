import os
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, abort, g
from logs.logger import logger

from ..database.dbConnection import db
from ..models.model import Model
from ..models.dataset import Dataset
from ..models.audit_log import AuditLog
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator
from ..cloudServices.nnApiConnections import NnAPIClient

# Instantiate a NnAPIClient
nnClient = NnAPIClient(
    base_url=os.getenv("NN_API_HOST"),
    secret_key=os.getenv("NN_API_SECRET_KEY"),
)

# Define router prefix
models = Blueprint("models", __name__, url_prefix="/models")


# ------- Model Routes -------


@models.route('/', methods=['GET'])
@auth_required(["ADMIN", "SUPERADMIN"])
def getAvailableModels():
    """
    Get all available models, syncing with NN API
    """
    try:
        # First, try to sync with NN API
        try:
            nn_models_response = nnClient.getAvailableModels()
            
            # Handle different response formats from NN API
            nn_models = []
            if isinstance(nn_models_response, dict):
                if nn_models_response.get('success') and nn_models_response.get('models'):
                    nn_models = nn_models_response['models']
                elif 'models' in nn_models_response:
                    nn_models = nn_models_response['models']
            elif isinstance(nn_models_response, list):
                nn_models = nn_models_response
            
            if nn_models:
                # Sync models with database
                for nn_model in nn_models:
                    model_name = nn_model.get('name')
                    if not model_name:
                        continue
                        
                    existing_model = Model.query.filter_by(name=model_name).first()
                    
                    if not existing_model:
                        # Create new model
                        new_model = Model(
                            name=model_name,
                            version='1.0',
                            description=nn_model.get('description', f'Model: {model_name}'),
                            modelType='YOLOv8',  # Default type
                            createdOn=datetime.utcnow(),
                            updatedOn=datetime.utcnow()
                        )
                        db.session.add(new_model)
                
                db.session.commit()
                logger.info(f"Synced {len(nn_models)} models from NN API")
        
        except Exception as sync_error:
            logger.warning(f"Could not sync with NN API: {sync_error}")
            # Continue with database-only models if NN API is unavailable

        # Query all models from database
        models_query = Model.query.order_by(Model.createdOn.desc()).all()

        models_list = []
        for model in models_query:
            created_on = (model.createdOn.isoformat()
                          if model.createdOn else None)
            updated_on = (model.updatedOn.isoformat()
                          if model.updatedOn else None)
            models_list.append({
                'id': model.id,
                'name': model.name,
                'version': model.version,
                'description': model.description,
                'modelType': model.modelType,
                'createdOn': created_on,
                'updatedOn': updated_on
            })

        logger.info(f"Retrieved {len(models_list)} models for user {g.uid}")

        return jsonify({
            'success': True,
            'models': models_list,
            'count': len(models_list)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        abort(500)


@models.route("/train", methods=["POST"])
@auth_required(["ADMIN", "SUPERADMIN"])
def trainModel():
    """
    Start training a new model with given parameters
    """
    try:
        data = request.get_json()

        # Validate required fields
        validator = InputValidator()

        # Validate model name
        model_name = data.get("modelName")
        if (
            not model_name
            or not isinstance(model_name, str)
            or len(model_name.strip()) == 0
        ):
            return jsonify({"success": False, "message": "Invalid model name"}), 400

        model_name = validator.sanitize_string(model_name, max_length=100)
        if len(model_name) > 100:
            return jsonify({"success": False, "message": "Model name is too long"}), 400

        if not data.get("datasetId") or not isinstance(data.get("datasetId"), int):
            return jsonify({"success": False, "message": "Invalid dataset ID"}), 400

        # Validate dataset exists
        dataset = Dataset.query.get(data["datasetId"])
        if not dataset:
            return jsonify({"success": False, "message": "Dataset not found"}), 404

        # Check if model name already exists
        existing_model = Model.query.filter_by(name=model_name).first()
        if existing_model:
            return (
                jsonify({"success": False, "message": "Model name already exists"}),
                409,
            )

        # Validate training parameters
        training_params = data.get("trainingParams", {})
        epochs = training_params.get("epochs", 50)
        image_size = training_params.get("imageSize", 640)
        batch_size = training_params.get("batchSize", 16)
        learning_rate = training_params.get("learningRate", 0.01)
        patience = training_params.get("patience", 30)

        # Validate ranges
        if not (1 <= epochs <= 1000):
            return (
                jsonify(
                    {"success": False, "message": "Epochs must be between 1 and 1000"}
                ),
                400,
            )

        if image_size not in [416, 512, 640, 800]:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Image size must be 416, 512, 640, or 800",
                    }
                ),
                400,
            )

        if batch_size not in [8, 16, 32, 64]:
            return (
                jsonify(
                    {"success": False, "message": "Batch size must be 8, 16, 32, or 64"}
                ),
                400,
            )

        if not (0.0001 <= learning_rate <= 0.1):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Learning rate must be between 0.0001 and 0.1",
                    }
                ),
                400,
            )

        # Create new model record (initially with training status)
        new_model = Model(
            name=model_name,
            version="1.0",  # Start with version 1.0
            description=data.get("description", ""),
            modelType=data.get("modelType", "YOLOv8_m"),
            createdOn=datetime.utcnow(),
            updatedOn=datetime.utcnow(),
        )

        db.session.add(new_model)
        db.session.commit()

        # Log audits are done through vite composable

        # Prepare training data for NN API
        flask_api_base_url = os.getenv("FLASK_API_BASE_URL", "http://localhost:5000")
        training_data = {
            "modelId": new_model.id,
            "modelName": model_name,
            "modelType": data.get("modelType", "YOLOv8_m"),
            "datasetId": data["datasetId"],
            "datasetPath": dataset.s3Path,
            "trainingParams": {
                "epochs": epochs,
                "imageSize": image_size,
                "batchSize": batch_size,
                "learningRate": learning_rate,
                "patience": patience,
            },
            "callbackUrls": {
                "completed": f"{flask_api_base_url}/models/training-callback/completed",
                "failed": f"{flask_api_base_url}/models/training-callback/failed",
            },
        }

        # Call NN API to start training
        try:
            logger.info(f"Sending training data to NN API: {training_data}")
            training_response = nnClient.requestTraining(training_data)

            # Extract job information from response
            job_id = training_response.get("jobId")
            estimated_time = training_response.get(
                "estimatedTime", f"{epochs * 2} minutes"
            )

            logger.info(
                f"Training started for model {new_model.id} " f"with job ID {job_id}"
            )

            return (
                jsonify(
                    {
                        "success": True,
                        "message": (
                            "Training job created and started. Check training "
                            "progress for status updates."
                        ),
                        "modelId": new_model.id,
                        "jobId": job_id,
                        "estimatedTime": estimated_time,
                    }
                ),
                201,
            )

        except requests.exceptions.RequestException as nn_error:
            # If NN API fails, rollback the model creation
            db.session.delete(new_model)
            db.session.commit()

            logger.error(f"NN API error: {str(nn_error)}")
            return (
                jsonify(
                    {"success": False, "message": "Failed to start training on NN API"}
                ),
                503,
            )

        except Exception as nn_error:
            # If NN API fails, rollback the model creation
            db.session.delete(new_model)
            db.session.commit()

            logger.error(f"NN API error: {str(nn_error)}")
            return (
                jsonify(
                    {"success": False, "message": "Failed to start training on NN API"}
                ),
                503,
            )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error starting model training: {str(e)}")
        abort(500)


@models.route("/training-jobs", methods=["GET"])
@auth_required(["ADMIN", "SUPERADMIN"])
def getTrainingJobs():
    """
    Get list of all training jobs from NN API
    """
    try:
        # Forward the request to NN API
        response = nnClient.getTrainingJobs()

        return jsonify(response), 200

    except requests.exceptions.RequestException as nn_error:
        logger.error(f"NN API error getting training jobs: {str(nn_error)}")
        return (
            jsonify(
                {"success": False, "message": "Failed to get training jobs from NN API"}
            ),
            503,
        )

    except Exception as e:
        logger.error(f"Error getting training jobs: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


@models.route("/training-jobs/<job_id>", methods=["DELETE"])
@auth_required(["ADMIN", "SUPERADMIN"])
def cancelTrainingJob(job_id):
    """
    Cancel a training job
    """
    try:
        # Get the job details first to find associated model
        model_deleted = False
        model_id = None
        model_name = None

        try:
            jobs_response = nnClient.getTrainingJobs()
            job = None
            for j in jobs_response.get("jobs", []):
                if j.get("jobId") == job_id:
                    job = j
                    break

            if job:
                model_id = job.get("trainingData", {}).get("modelId")
                if model_id:
                    # Delete the model from database since training is cancelled
                    model = Model.query.get(model_id)
                    if model:
                        model_name = model.modelName
                        db.session.delete(model)
                        db.session.commit()
                        model_deleted = True
                        logger.info(
                            f"Deleted model {model_id} ({model_name}) "
                            f"for cancelled job {job_id}"
                        )

                        # Create audit log for model deletion due to cancellation
                        audit_log = AuditLog(
                            userId=g.uid,  # User who cancelled
                            action="MODEL_TRAINING_CANCELLED_DELETED",
                            entityType="model",
                            entityId=model_id,
                            timestamp=datetime.utcnow(),
                        )
                        db.session.add(audit_log)
                        db.session.commit()

        except Exception as cleanup_error:
            logger.warning(
                f"Could not cleanup model for cancelled job: " f"{cleanup_error}"
            )

        # Create audit log for the training cancellation action
        try:
            audit_log = AuditLog(
                userId=g.uid,
                action="MODEL_TRAINING_CANCELLED",
                entityType="training_job",
                entityId=None,
                timestamp=datetime.utcnow(),
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as audit_error:
            logger.warning(
                f"Could not create audit log for cancellation: " f"{audit_error}"
            )

        # Forward the cancellation request to NN API
        response = nnClient.cancelTrainingJob(job_id)

        # Add metadata to response
        if isinstance(response, dict):
            response["modelDeleted"] = model_deleted
            response["modelId"] = model_id

        return jsonify(response), 200

    except requests.exceptions.RequestException as nn_error:
        logger.error(f"NN API error cancelling job {job_id}: {str(nn_error)}")
        return (
            jsonify({"success": False, "message": "Failed to cancel training job"}),
            503,
        )

    except Exception as e:
        logger.error(f"Error cancelling training job {job_id}: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


@models.route("/training-callback/completed", methods=["POST"])
def trainingCompletedCallback():
    """
    Callback endpoint for when training completes successfully
    """
    try:
        data = request.get_json()
        job_id = data.get("jobId")
        model_id = data.get("modelId")
        model_path = data.get("modelPath")

        if model_id:
            # Update model record with completion status
            model = Model.query.get(model_id)
            if model:
                model.updatedOn = datetime.utcnow()
                # You might want to add a status field to track training completion
                db.session.commit()
                logger.info(f"Updated model {model_id} after training completion")

        return jsonify({"success": True, "message": "Callback processed"}), 200

    except Exception as e:
        logger.error(f"Error processing training completion callback: {str(e)}")
        return jsonify({"success": False, "message": "Callback failed"}), 500


@models.route("/training-callback/failed", methods=["POST"])
def trainingFailedCallback():
    """
    Callback endpoint for when training fails
    """
    try:
        data = request.get_json()
        job_id = data.get("jobId")
        error_message = data.get("error")

        logger.info(f"Processing training failure callback for job {job_id}")

        # Try to find and delete the model that failed to train
        model_deleted = False
        model_id = None

        try:
            jobs_response = nnClient.getTrainingJobs()
            for job in jobs_response.get("jobs", []):
                if job.get("jobId") == job_id:
                    model_id = job.get("trainingData", {}).get("modelId")
                    if model_id:
                        model = Model.query.get(model_id)
                        if model:
                            model_name = model.modelName
                            db.session.delete(model)
                            db.session.commit()
                            model_deleted = True
                            logger.info(
                                f"Deleted failed model {model_id} "
                                f"({model_name}) for job {job_id}"
                            )

                            # Create audit log for model deletion
                            audit_log = AuditLog(
                                userId=None,  # System action
                                action="MODEL_TRAINING_FAILED_DELETED",
                                entityType="model",
                                entityId=model_id,
                                timestamp=datetime.utcnow(),
                            )
                            db.session.add(audit_log)
                            db.session.commit()

                    break
        except Exception as cleanup_error:
            logger.warning(
                f"Could not cleanup failed model for job " f"{job_id}: {cleanup_error}"
            )

        # Log the training failure event
        if model_id:
            try:
                audit_log = AuditLog(
                    userId=None,  # System action
                    action="MODEL_TRAINING_FAILED",
                    entityType="training_job",
                    entityId=None,
                    timestamp=datetime.utcnow(),
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as audit_error:
                logger.warning(
                    f"Could not create audit log for failed " f"training: {audit_error}"
                )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Failure callback processed",
                    "modelDeleted": model_deleted,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error processing training failure callback: {str(e)}")
        return jsonify({"success": False, "message": "Callback failed"}), 500


@models.route("/sync", methods=["POST"])
@auth_required(["ADMIN", "SUPERADMIN"])
def sync_models_from_api():
    try:
        nn_models = nnClient.getAvailableModels()

        for nn_model in nn_models:
            model_exists = Model.query.filter_by(name=nn_model["name"]).first()
            if not model_exists:
                new_model = Model(
                    name=nn_model["name"],
                    version=nn_model.get("version", "1.0"),
                    description=nn_model.get("description", ""),
                    modelType=nn_model.get(
                        "modelType", "TBD"
                    ),  # TODO: Set a proper modelType and description
                    createdOn=datetime.utcnow(),
                    updatedOn=datetime.utcnow(),
                )
                db.session.add(new_model)
                logger.info(f"Added new model from NN API: {nn_model['name']}")
            else:
                # TODO: Implement logic to update a model
                logger.info(f"Model already exists in DB: {nn_model['name']}")
        db.session.commit()
        return (
            jsonify({"success": True, "message": "Models synchronized successfully"}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error synchronizing models from NN API: {str(e)}")
        return jsonify({"success": False, "message": "Error synchronizing models"}), 500
