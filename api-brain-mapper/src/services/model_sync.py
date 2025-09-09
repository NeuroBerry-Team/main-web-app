import os
from datetime import datetime
from logs.logger import logger
from ..database.dbConnection import db
from ..models.model import Model
from ..cloudServices.nnApiConnections import NnAPIClient

def sync_models_with_nn_api():
    """
    Synchronize models from Neural Network API with the local database.
    This function is called at application startup to ensure the model list is current.
    """
    try:
        # Initialize NN API client
        nn_client = NnAPIClient(
            base_url=os.getenv("NN_API_HOST"),
            secret_key=os.getenv("NN_API_SECRET_KEY"),
        )
        
        # Get models from NN API
        logger.info("Syncing models from Neural Network API...")
        nn_models_response = nn_client.getAvailableModels()
        
        if isinstance(nn_models_response, dict):
            if nn_models_response.get('success') and nn_models_response.get('models'):
                nn_models = nn_models_response['models']
            elif 'models' in nn_models_response:
                nn_models = nn_models_response['models']
            else:
                logger.warning("No models found in NN API response")
                return
        elif isinstance(nn_models_response, list):
            nn_models = nn_models_response
        else:
            logger.warning("Invalid response format from NN API")
            return
        
        if not nn_models:
            logger.warning("No models returned from NN API")
            return
        
        synced_count = 0
        updated_count = 0
        
        for nn_model in nn_models:
            model_name = nn_model.get('name')
            if not model_name:
                logger.warning(f"Model without name found: {nn_model}")
                continue
            
            # Check if model exists in database
            existing_model = Model.query.filter_by(name=model_name).first()
            
            if not existing_model:
                # Create new model
                new_model = Model(
                    name=model_name,
                    description=nn_model.get('description', f'Model: {model_name}'),
                    version='1.0',  # Default version
                    modelType='YOLOv8',  # Default type
                    createdOn=datetime.utcnow(),
                    updatedOn=datetime.utcnow()
                )
                db.session.add(new_model)
                synced_count += 1
                logger.info(f"Added new model: {model_name}")
            else:
                # Update existing model if description changed
                new_description = nn_model.get('description', existing_model.description)
                if existing_model.description != new_description:
                    existing_model.description = new_description
                    existing_model.updatedOn = datetime.utcnow()
                    updated_count += 1
                    logger.info(f"Updated model description: {model_name}")
        
        # Commit all changes
        db.session.commit()
        logger.info(f"Model sync completed: {synced_count} new models added, {updated_count} updated")
        
    except Exception as e:
        logger.exception(f"Error syncing models from NN API: {e}")
        db.session.rollback()
        # Don't raise the exception to prevent startup failure