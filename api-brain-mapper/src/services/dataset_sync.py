import os
from datetime import datetime
from logs.logger import logger
from ..cloudServices.minioConnections import getMinioClient
from ..models.dataset import Dataset
from ..database.dbConnection import db


def sync_datasets_with_minio():
    """
    Synchronize datasets between MinIO bucket and database on app startup.
    """
    try:
        logger.info("Starting dataset synchronization with MinIO...")
        
        # Get MinIO client and bucket
        client = getMinioClient()
        datasets_bucket = os.environ.get("S3_BUCKET_DATASET", "datasets")
        
        # List all objects in MinIO bucket
        try:
            minio_objects = list(client.list_objects(datasets_bucket))
            minio_filenames = [obj.object_name for obj in minio_objects]
            logger.info(f"Found {len(minio_filenames)} files in MinIO: "
                        f"{minio_filenames}")
        except Exception as e:
            logger.error(f"Error accessing MinIO bucket '{datasets_bucket}': "
                         f"{str(e)}")
            return False
        
        # Get all existing datasets from database
        existing_datasets = Dataset.query.all()
        existing_names = {ds.name for ds in existing_datasets}
        logger.info(f"Found {len(existing_names)} datasets in database: "
                    f"{list(existing_names)}")
        
        # Find new files in MinIO that don't exist in database
        new_files = []
        reactivate_datasets = []
        for filename in minio_filenames:
            # Use filename without extension as the dataset name for comparison
            dataset_name = (filename.rsplit('.', 1)[0]
                            if '.' in filename else filename)
            if dataset_name not in existing_names:
                new_files.append((filename, dataset_name))
            else:
                # Check if existing dataset is inactive and reactivate it
                existing_dataset = next(
                    (ds for ds in existing_datasets
                     if ds.name == dataset_name),
                    None
                )
                if existing_dataset and not existing_dataset.active:
                    reactivate_datasets.append(existing_dataset)
        
        # Create database entries for new files
        created_count = 0
        for filename, dataset_name in new_files:
            try:
                # Get system user ID (assuming user ID 1 is system/admin)
                system_user_id = 1
                
                new_dataset = Dataset(
                    name=dataset_name,
                    description=f'Auto-synced dataset from MinIO: {filename}',
                    datasetType='YOLO',  # Default type
                    s3Path=f's3://{datasets_bucket}/{filename}',
                    createdBy=system_user_id,
                    createdOn=datetime.utcnow(),
                    active=True
                )
                
                db.session.add(new_dataset)
                created_count += 1
                logger.info(f"Created database entry for dataset: "
                            f"{dataset_name} (file: {filename})")
                
            except Exception as e:
                logger.error(f"Error creating dataset entry for "
                             f"{filename}: {str(e)}")
                continue
        
        # Reactivate datasets that were inactive but are back in MinIO
        reactivated_count = 0
        for dataset in reactivate_datasets:
            dataset.active = True
            reactivated_count += 1
            logger.info(f"Reactivated dataset: {dataset.name}")
        
        # Find database entries that no longer exist in MinIO
        minio_dataset_names = {
            (filename.rsplit('.', 1)[0] if '.' in filename else filename)
            for filename in minio_filenames
        }
        orphaned_datasets = existing_names - minio_dataset_names
        
        # Mark orphaned datasets as inactive
        deactivated_count = 0
        if orphaned_datasets:
            logger.warning(f"Found {len(orphaned_datasets)} datasets "
                           f"in database but not in MinIO: "
                           f"{list(orphaned_datasets)}")
            # Mark as inactive
            for dataset in existing_datasets:
                if dataset.name in orphaned_datasets and dataset.active:
                    dataset.active = False
                    deactivated_count += 1
                    logger.info(f"Marking dataset as inactive: {dataset.name}")

        # Commit all changes
        total_changes = created_count + reactivated_count + deactivated_count
        if total_changes > 0:
            db.session.commit()
            logger.info(f"Dataset sync completed - Created: {created_count}, "
                        f"Reactivated: {reactivated_count}, "
                        f"Deactivated: {deactivated_count}")
        else:
            logger.info("No dataset changes needed")
            
        return True
        
    except Exception as e:
        logger.error(f"Error during dataset synchronization: {str(e)}")
        db.session.rollback()
        return False


def get_system_user_id():
    """
    Get the system user ID for auto-created datasets.
    Falls back to user ID 1 if no specific system user exists.
    """
    try:
        from ..models.user import User
        # Try to find a system or admin user
        system_user = User.query.filter_by(
            email='admin@neuroberry.com'
        ).first()
        if system_user:
            return system_user.id
        
        # Fallback to first user or create a default
        first_user = User.query.first()
        if first_user:
            return first_user.id
            
        # Last resort fallback
        return 1
        
    except Exception as e:
        logger.warning(f"Could not determine system user ID: {str(e)}, "
                       f"using fallback ID 1")
        return 1
