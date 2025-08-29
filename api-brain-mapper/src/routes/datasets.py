from flask import Blueprint, jsonify, abort, g
from logs.logger import logger

from ..models.dataset import Dataset
from ..security.decorators_utils import auth_required

# Define router prefix
datasets = Blueprint('datasets', __name__, url_prefix='/datasets')


# ------- Dataset Routes -------

@datasets.route('/', methods=['GET'])
@auth_required(["ADMIN", "SUPERADMIN"])
def getAvailableDatasets():
    """
    Get all available datasets for training
    """
    try:
        # Query all datasets from database
        datasets_query = Dataset.query.order_by(Dataset.createdOn.desc()).all()

        datasets_list = []
        for dataset in datasets_query:
            created_on = (dataset.createdOn.isoformat()
                          if dataset.createdOn else None)
            datasets_list.append({
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'datasetType': dataset.datasetType,
                's3Path': dataset.s3Path,
                'createdBy': dataset.createdBy,
                'createdOn': created_on
            })

        logger.info(f"Retrieved {len(datasets_list)} datasets for "
                    f"user {g.uid}")

        return jsonify({
            'success': True,
            'datasets': datasets_list,
            'count': len(datasets_list)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving datasets: {str(e)}")
        abort(500)


@datasets.route('/<int:dataset_id>', methods=['GET'])
@auth_required(["ADMIN", "SUPERADMIN"])
def getDatasetById(dataset_id):
    """
    Get specific dataset by ID
    """
    try:
        dataset = Dataset.query.get(dataset_id)

        if not dataset:
            return jsonify({
                'success': False,
                'message': 'Dataset not found'
            }), 404

        created_on = (dataset.createdOn.isoformat()
                      if dataset.createdOn else None)

        return jsonify({
            'success': True,
            'dataset': {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'datasetType': dataset.datasetType,
                's3Path': dataset.s3Path,
                'createdBy': dataset.createdBy,
                'createdOn': created_on
            }
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving dataset {dataset_id}: {str(e)}")
        abort(500)
