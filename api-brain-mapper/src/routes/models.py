import os
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, abort, g
from logs.logger import logger

from ..database.dbConnection import db
from ..models.model import Model
from ..models.dataset import Dataset
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator
from ..cloudServices.nnApiConnections import NnAPIClient

# Instantiate a NnAPIClient
nnClient = NnAPIClient(
    base_url=os.getenv('NN_API_HOST'),
    secret_key=os.getenv('NN_API_SECRET_KEY'),
)

# Define router prefix
models = Blueprint('models', __name__, url_prefix='/models')


# ------- Model Routes -------

@models.route('/', methods=['GET'])
@auth_required(["ADMIN", "SUPERADMIN"])
def getAvailableModels():
    """
    Get all available models
    """
    try:
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


@models.route('/train', methods=['POST'])
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
        model_name = data.get('modelName')
        if (not model_name or not isinstance(model_name, str) or
                len(model_name.strip()) == 0):
            return jsonify({
                'success': False,
                'message': 'Invalid model name'
            }), 400
        
        model_name = validator.sanitize_string(model_name, max_length=100)
        if len(model_name) > 100:
            return jsonify({
                'success': False,
                'message': 'Model name is too long'
            }), 400

        if not data.get('datasetId') or not isinstance(data.get('datasetId'),
                                                       int):
            return jsonify({
                'success': False,
                'message': 'Invalid dataset ID'
            }), 400

        # Validate dataset exists
        dataset = Dataset.query.get(data['datasetId'])
        if not dataset:
            return jsonify({
                'success': False,
                'message': 'Dataset not found'
            }), 404

        # Check if model name already exists
        existing_model = Model.query.filter_by(name=model_name).first()
        if existing_model:
            return jsonify({
                'success': False,
                'message': 'Model name already exists'
            }), 409

        # Validate training parameters
        training_params = data.get('trainingParams', {})
        epochs = training_params.get('epochs', 50)
        image_size = training_params.get('imageSize', 640)
        batch_size = training_params.get('batchSize', 16)
        learning_rate = training_params.get('learningRate', 0.01)
        patience = training_params.get('patience', 30)

        # Validate ranges
        if not (1 <= epochs <= 1000):
            return jsonify({
                'success': False,
                'message': 'Epochs must be between 1 and 1000'
            }), 400

        if image_size not in [416, 512, 640, 800]:
            return jsonify({
                'success': False,
                'message': 'Image size must be 416, 512, 640, or 800'
            }), 400

        if batch_size not in [8, 16, 32, 64]:
            return jsonify({
                'success': False,
                'message': 'Batch size must be 8, 16, 32, or 64'
            }), 400

        if not (0.0001 <= learning_rate <= 0.1):
            return jsonify({
                'success': False,
                'message': 'Learning rate must be between 0.0001 and 0.1'
            }), 400

        # Create new model record (initially with training status)
        new_model = Model(
            name=model_name,
            version='1.0',  # Start with version 1.0
            description=data.get('description', ''),
            modelType=data.get('modelType', 'YOLOv8_m'),
            createdOn=datetime.utcnow(),
            updatedOn=datetime.utcnow()
        )

        db.session.add(new_model)
        db.session.commit()

        # Log audits are done through vite composable

        # Prepare training data for NN API
        training_data = {
            'modelId': new_model.id,
            'modelName': model_name,
            'modelType': data.get('modelType', 'YOLOv8_m'),
            'datasetId': data['datasetId'],
            'datasetPath': dataset.s3Path,
            'trainingParams': {
                'epochs': epochs,
                'imageSize': image_size,
                'batchSize': batch_size,
                'learningRate': learning_rate,
                'patience': patience
            }
        }

        # Call NN API to start training
        try:
            training_response = nnClient.requestTraining(training_data)
            
            # Extract job information from response
            job_id = training_response.get('jobId')
            estimated_time = training_response.get(
                'estimatedTime', f"{epochs * 2} minutes")
            
            logger.info(f"Training started for model {new_model.id} "
                        f"with job ID {job_id}")

            return jsonify({
                'success': True,
                'message': 'Model training started successfully',
                'modelId': new_model.id,
                'jobId': job_id,
                'estimatedTime': estimated_time
            }), 201

        except requests.exceptions.RequestException as nn_error:
            # If NN API fails, rollback the model creation
            db.session.delete(new_model)
            db.session.commit()

            logger.error(f"NN API error: {str(nn_error)}")
            return jsonify({
                'success': False,
                'message': 'Failed to start training on NN API'
            }), 503

        except Exception as nn_error:
            # If NN API fails, rollback the model creation
            db.session.delete(new_model)
            db.session.commit()

            logger.error(f"NN API error: {str(nn_error)}")
            return jsonify({
                'success': False,
                'message': 'Failed to start training on NN API'
            }), 503

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error starting model training: {str(e)}")
        abort(500)


# TODO: Add a status watcher to track status training
