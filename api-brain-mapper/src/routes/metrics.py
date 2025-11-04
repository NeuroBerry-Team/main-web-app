from flask import Blueprint, jsonify, g, request
from logs.logger import logger
from datetime import datetime, timedelta
from sqlalchemy import func
from collections import defaultdict
import json

from ..models.inference import Inference
from ..database.dbConnection import db
from ..security.decorators_utils import auth_required
from ..cloudServices.minioConnections import getMinioClient
import os

# Define router prefix
metrics = Blueprint("metrics", __name__, url_prefix="/metrics")


@metrics.route("/class-detections", methods=["GET"])
@auth_required()
def get_class_detection_metrics():
    """
    Get aggregated class detection counts across all user inferences
    Fetches and processes metadata from each inference to count detections
    """
    try:
        user_id = g.uid
        
        # Get all inferences for the user
        inferences = Inference.query.filter_by(userId=user_id).all()
        
        if not inferences:
            return jsonify({
                "success": True,
                "totalInferences": 0,
                "totalDetections": 0,
                "classCounts": {},
                "classPercentages": {},
                "inferenceHistory": []
            }), 200
        
        # Initialize counters
        class_counts = defaultdict(int)
        total_detections = 0
        inference_history = []
        
        # MinIO client
        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")
        
        # Process each inference
        for inference in inferences:
            try:
                # Extract metadata object key from URL
                if not inference.generatedImageUrl:
                    continue
                    
                url_parts = inference.generatedImageUrl.split("/")
                if len(url_parts) >= 2:
                    folder_name = url_parts[-2]
                    metadata_object_key = f"{user_id}/{folder_name}/metadata.json"
                    
                    # Fetch metadata from MinIO
                    try:
                        response = minioClient.get_object(s3Bucket, metadata_object_key)
                        metadata_content = response.read()
                        response.close()
                        response.release_conn()
                        
                        metadata = json.loads(metadata_content.decode('utf-8'))
                        
                        # Count detections by class
                        detections = metadata.get('detections', [])
                        inference_detection_counts = defaultdict(int)
                        
                        for detection in detections:
                            class_id = detection.get('class_id')
                            if class_id is not None:
                                class_counts[class_id] += 1
                                inference_detection_counts[class_id] += 1
                                total_detections += 1
                        
                        # Add to history
                        inference_history.append({
                            "id": inference.id,
                            "date": inference.createdOn.isoformat() if inference.createdOn else None,
                            "totalDetections": len(detections),
                            "classCounts": dict(inference_detection_counts)
                        })
                        
                    except Exception as e:
                        logger.warning(f"Could not fetch metadata for inference {inference.id}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error processing inference {inference.id}: {str(e)}")
                continue
        
        # Calculate percentages
        class_percentages = {}
        if total_detections > 0:
            for class_id, count in class_counts.items():
                class_percentages[class_id] = round((count / total_detections) * 100, 2)
        
        # Sort inference history by date
        inference_history.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
        
        return jsonify({
            "success": True,
            "totalInferences": len(inferences),
            "totalDetections": total_detections,
            "classCounts": dict(class_counts),
            "classPercentages": class_percentages,
            "inferenceHistory": inference_history
        }), 200
        
    except Exception as e:
        logger.exception(f"Error getting class detection metrics: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


@metrics.route("/time-series", methods=["GET"])
@auth_required()
def get_time_series_metrics():
    """
    Get time-series data for detection counts over time
    Groups detections by day, week, or month
    """
    try:
        user_id = g.uid
        
        # Get grouping parameter (day, week, month)
        grouping = request.args.get('grouping', 'day')
        
        # Get date range parameters
        days_back = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Get all inferences in date range
        inferences = Inference.query.filter(
            Inference.userId == user_id,
            Inference.createdOn >= start_date,
            Inference.createdOn <= end_date
        ).order_by(Inference.createdOn).all()
        
        if not inferences:
            return jsonify({
                "success": True,
                "timeSeries": [],
                "totalDetections": 0
            }), 200
        
        # MinIO client
        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")
        
        # Group data by date
        time_series_data = defaultdict(lambda: {
            "totalDetections": 0,
            "classCounts": defaultdict(int),
            "inferenceCount": 0
        })
        
        total_detections = 0
        
        # Process each inference
        for inference in inferences:
            try:
                # Group by date
                if grouping == 'day':
                    date_key = inference.createdOn.date().isoformat()
                elif grouping == 'week':
                    week_start = inference.createdOn.date() - timedelta(days=inference.createdOn.weekday())
                    date_key = week_start.isoformat()
                else:  # month
                    date_key = inference.createdOn.strftime('%Y-%m')
                
                # Extract metadata
                if not inference.generatedImageUrl:
                    continue
                
                url_parts = inference.generatedImageUrl.split("/")
                if len(url_parts) >= 2:
                    folder_name = url_parts[-2]
                    metadata_object_key = f"{user_id}/{folder_name}/metadata.json"
                    
                    try:
                        response = minioClient.get_object(s3Bucket, metadata_object_key)
                        metadata_content = response.read()
                        response.close()
                        response.release_conn()
                        
                        metadata = json.loads(metadata_content.decode('utf-8'))
                        detections = metadata.get('detections', [])
                        
                        time_series_data[date_key]["inferenceCount"] += 1
                        time_series_data[date_key]["totalDetections"] += len(detections)
                        
                        for detection in detections:
                            class_id = detection.get('class_id')
                            if class_id is not None:
                                time_series_data[date_key]["classCounts"][class_id] += 1
                                total_detections += 1
                        
                    except Exception as e:
                        logger.warning(f"Could not fetch metadata for inference {inference.id}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error processing inference {inference.id}: {str(e)}")
                continue
        
        # Convert to list and sort by date
        time_series = []
        for date_key, data in sorted(time_series_data.items()):
            time_series.append({
                "date": date_key,
                "totalDetections": data["totalDetections"],
                "classCounts": dict(data["classCounts"]),
                "inferenceCount": data["inferenceCount"]
            })
        
        return jsonify({
            "success": True,
            "timeSeries": time_series,
            "totalDetections": total_detections,
            "dateRange": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.exception(f"Error getting time series metrics: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


@metrics.route("/summary", methods=["GET"])
@auth_required()
def get_metrics_summary():
    """
    Get a summary of all metrics for quick dashboard view
    """
    try:
        user_id = g.uid
        
        # Get total inference count
        total_inferences = Inference.query.filter_by(userId=user_id).count()
        
        # Get inferences in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_inferences = Inference.query.filter(
            Inference.userId == user_id,
            Inference.createdOn >= thirty_days_ago
        ).count()
        
        # Get first and last inference dates
        first_inference = Inference.query.filter_by(userId=user_id).order_by(Inference.createdOn.asc()).first()
        last_inference = Inference.query.filter_by(userId=user_id).order_by(Inference.createdOn.desc()).first()
        
        return jsonify({
            "success": True,
            "totalInferences": total_inferences,
            "recentInferences": recent_inferences,
            "firstInferenceDate": first_inference.createdOn.isoformat() if first_inference else None,
            "lastInferenceDate": last_inference.createdOn.isoformat() if last_inference else None,
            "accountAge": (datetime.utcnow() - first_inference.createdOn).days if first_inference else 0
        }), 200
        
    except Exception as e:
        logger.exception(f"Error getting metrics summary: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
