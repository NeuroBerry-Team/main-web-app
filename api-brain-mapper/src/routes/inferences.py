import os
import uuid
import datetime
import requests
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Blueprint, request, jsonify, abort, g, send_file, Response
from logs.logger import logger

from ..database.dbConnection import db
from ..models.inference import Inference
from ..models.model import Model
from ..security.decorators_utils import auth_required
from ..security.input_validation import InputValidator
from ..security.file_upload_security import FileUploadSecurity
from ..security.rate_limiter import rate_limit_api, rate_limit_file_upload
from ..cloudServices.minioConnections import getMinioClient
from ..cloudServices.nnApiConnections import NnAPIClient

load_dotenv()

# Instantiate a NnAPIClient
nnClient = NnAPIClient(
    base_url=os.getenv("NN_API_HOST"),
    secret_key=os.getenv("NN_API_SECRET_KEY"),
)

# Define router prefix
inferences = Blueprint("inferences", __name__, url_prefix="/inferences")


# ------- All the routes -------
@inferences.route("/getBaseImgPresignedUrls", methods=["GET"])
@auth_required()
@rate_limit_file_upload(max_attempts=10, window_minutes=60)
def getBaseImgPresignedUrls():
    # Instantiate a minio client
    minioClient = getMinioClient()

    # Creates unique foldername
    folderName = str(uuid.uuid4().hex)

    # Configure s3 constants for inferences bucket
    s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")
    s3LiveUrl = os.getenv("S3_LIVE_BASE_URL") + s3Bucket
    presignedExpTime = int(os.getenv("S3_PRESIGNED_EXPIRATION"))

    # Generate live and upload urls for the image
    try:
        # Include user ID for security
        imgObjectKey = f"{g.uid}/{folderName}/original_img.jpg"
        imgLiveUrl = f"{s3LiveUrl}/{imgObjectKey}"
        logger.info(f"Generating presigned URL for user {g.uid}: {imgLiveUrl}")

        imgUploadUrl = minioClient.presigned_put_object(
            s3Bucket, imgObjectKey, expires=datetime.timedelta(seconds=presignedExpTime)
        )

    except Exception:
        logger.exception("Presigned S3 error")
        abort(500, "Error getting presigned url for img")

    # Setup response data
    file_security = FileUploadSecurity.ALLOWED_EXTENSIONS["image"]
    allowed_extensions = file_security["extensions"]
    responseData = {
        "uploadURL": imgUploadUrl,
        "liveURL": imgLiveUrl,
        "imgObjectKey": imgObjectKey,
        "maxFileSize": FileUploadSecurity.MAX_FILE_SIZES["image"],
        "allowedExtensions": allowed_extensions,
    }

    return jsonify(responseData), 200


@inferences.route("/generateInference", methods=["POST"])
@auth_required()
@rate_limit_api(max_attempts=5, window_minutes=10)
def generateInference():
    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Request data: {request.get_json()}")

    # Validate request structure
    req = InputValidator.validate_json_request(
        request, ["name", "imgUrl", "imgObjectKey"]
    )

    # Get optional modelId, default to 1 if not provided
    model_id = req.get("modelId", 1)
    if not isinstance(model_id, int) or model_id <= 0:
        abort(400, "Invalid model ID")

    # Validate that the model exists in the database
    model = Model.query.get(model_id)
    if not model:
        abort(404, "Model not found")

    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Validated request: {req}")

    # Validate and sanitize inputs
    name = InputValidator.sanitize_string(req["name"], max_length=200)
    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Validated name: {name}")

    baseImageUrl = InputValidator.sanitize_string(req["imgUrl"], max_length=500)
    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Validated imgUrl: {baseImageUrl}")

    imgObjectKey = InputValidator.sanitize_string(req["imgObjectKey"], max_length=500)
    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Validated imgObjectKey: {imgObjectKey}")

    # Validate that imgObjectKey belongs to the authenticated user
    expected_prefix = f"{g.uid}/"
    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Expected prefix: {expected_prefix}")
        logger.debug(
            f"[INFERENCE DEBUG] ObjectKey starts with prefix: {imgObjectKey.startswith(expected_prefix)}"
        )

    if not imgObjectKey.startswith(expected_prefix):
        abort(403, "Access denied to image resource")

    # Validate that imgUrl is from expected bucket
    expected_bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")
    expected_base_url = os.getenv("S3_LIVE_BASE_URL") + expected_bucket
    if os.getenv("ENV_MODE") != "production":
        logger.debug(f"[INFERENCE DEBUG] Expected bucket: {expected_bucket}")
        logger.debug(f"[INFERENCE DEBUG] Expected base URL: {expected_base_url}")
        logger.debug(
            f"[INFERENCE DEBUG] URL starts with base: {baseImageUrl.startswith(expected_base_url)}"
        )

    if not baseImageUrl.startswith(expected_base_url):
        abort(400, "Invalid image URL")

    # Make API call to ANN-API to make the inference
    try:
        # Get the name of the model. NN API needs it to switch models.
        model_name = model.name
        payload = {"imgObjectKey": imgObjectKey, "modelName": model_name}
        logger.info(
            f"Generating inference for user {g.uid}: {imgObjectKey} with model {model_name}"
        )
        json_response = nnClient.generateInference(payload)
        generatedImageUrl = json_response["generatedImgUrl"]
        # Get the metadata URL from NN API response
        metadataUrl = json_response.get("metadataUrl")
    except Exception:
        logger.exception(f"Error generating inference for {imgObjectKey}")
        abort(500, "Error generating inference")

    user_id = getattr(g, "uid", None)

    # Make new instance of inference model
    new_inference = Inference(
        userId=user_id,
        modelId=model_id,  # Use the selected model ID
        name=name,
        baseImageUrl=baseImageUrl,
        generatedImageUrl=generatedImageUrl,
        metadataUrl=metadataUrl,  # Add the metadata URL to the database
        createdOn=datetime.datetime.utcnow(),
    )

    # Save inference in DB
    try:
        db.session.add(new_inference)
        db.session.commit()
    except Exception:
        logger.exception(f"Error saving in DB inference of {imgObjectKey}")
        abort(500, "Error while saving inference")

    # Respond with the generatedImageUrl and id
    return (
        jsonify(
            {
                "generatedImgUrl": generatedImageUrl,
                "id": new_inference.id,
                "baseImageUrl": baseImageUrl,
            }
        ),
        200,
    )


@inferences.route("/getInferenceMetadata/<int:inference_id>", methods=["GET"])
@auth_required()
@rate_limit_api(max_attempts=10, window_minutes=5)
def getInferenceMetadata(inference_id):
    """
    Get metadata for a specific inference
    """
    try:
        # Get the inference from database
        inference = Inference.query.filter_by(id=inference_id, userId=g.uid).first()

        if not inference:
            abort(404, "Inference not found")

        # Assuming metadata is stored alongside the generated image
        base_object_key = inference.generatedImageUrl.split("/")[
            -2:
        ]  # Get folder and filename
        metadata_object_key = f"{g.uid}/{base_object_key[0]}/metadata.json"

        # Get MinIO client
        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")

        logger.info(
            f"Fetching metadata for inference {inference_id} from MinIO: {metadata_object_key}"
        )

        try:
            # Stream the metadata file directly from MinIO
            response = minioClient.get_object(s3Bucket, metadata_object_key)
            metadata_content = response.read()
            response.close()
            response.release_conn()

            # Parse JSON content
            metadata = json.loads(metadata_content.decode("utf-8"))

            return (
                jsonify({"success": True, "metadata": metadata, "source": "minio"}),
                200,
            )

        except Exception as e:
            logger.warning(f"Error reading metadata from MinIO: {str(e)}")

            # Fallback to HTTP URL if available
            if inference.metadataUrl:
                response = requests.get(inference.metadataUrl)
                if response.status_code == 200:
                    return (
                        jsonify(
                            {
                                "success": True,
                                "metadata": response.json(),
                                "source": "url",
                            }
                        ),
                        200,
                    )

        abort(404, "Metadata not found")

    except Exception:
        logger.exception(f"Error fetching metadata for inference {inference_id}")
        abort(500, "Error fetching metadata")


@inferences.route("/<int:inference_id>/download", methods=["GET"])
@auth_required()
@rate_limit_api(max_attempts=5, window_minutes=10)
def download_inferences(inference_id):
    import tempfile
    import zipfile
    import os
    import shutil
    
    # Create a temporary directory for this operation
    temp_dir = None
    zip_path = None
    
    def cleanup_temp_dir():
        """Clean up temporary directory"""
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                pass
            except Exception:
                pass
    
    try:
        # Fetch the inference from the database
        inference = Inference.query.filter_by(id=inference_id, userId=g.uid).first()
        if not inference:
            return jsonify({"error": "Inference not found", "inference_id": inference_id}), 404
            
        if not inference.baseImageUrl or not inference.generatedImageUrl:
            return jsonify({"error": "Incomplete inference data - missing image URLs"}), 400

        temp_dir = tempfile.mkdtemp(prefix=f"inference_{inference_id}_")
        
        # Prepare file paths in temp directory
        base_image_path = os.path.join(temp_dir, f"original_image_{inference.id}.jpg")
        generated_image_path = os.path.join(temp_dir, f"analyzed_image_{inference.id}.jpg")
        metadata_path = os.path.join(temp_dir, f"metadata_{inference.id}.json")

        # Download files from MinIO
        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")

        try:
            s3_live_base_url = os.getenv('S3_LIVE_BASE_URL')
            s3_port = os.getenv('S3_PORT', '9000')
            
            def extract_object_key_from_url(url):
                if url.startswith(s3_live_base_url):
                    path_after_base = url[len(s3_live_base_url):]
                else:
                    alternative_bases = [
                        f"http://localhost:{s3_port}/",
                        f"http://127.0.0.1:{s3_port}/",
                        f"http://s3:{s3_port}/",
                    ]
                    
                    matched_base = None
                    for alt_base in alternative_bases:
                        if url.startswith(alt_base):
                            matched_base = alt_base
                            break
                    
                    if not matched_base:
                        import re
                        port_pattern = f"://[^/]+:{s3_port}/"
                        match = re.search(port_pattern, url)
                        if match:
                            matched_base = url[:match.end()]
                        else:
                            url_parts = url.split('/')
                            if len(url_parts) >= 4 and ':' in url_parts[2]:
                                matched_base = '/'.join(url_parts[:3]) + '/'
                            else:
                                raise ValueError(f"URL doesn't match any expected MinIO pattern: {url}")
                    
                    path_after_base = url[len(matched_base):]
                
                if path_after_base.startswith(f"{s3Bucket}/"):
                    return path_after_base[len(f"{s3Bucket}/"):]
                else:
                    return path_after_base
            
            base_object_key = extract_object_key_from_url(inference.baseImageUrl)
            generated_object_key = extract_object_key_from_url(inference.generatedImageUrl)
            
            folder_path = "/".join(base_object_key.split("/")[:-1])
            metadata_object_key = f"{folder_path}/metadata.json"

            try:
                minioClient.fget_object(s3Bucket, base_object_key, base_image_path)
            except Exception as e:
                raise Exception(f"Failed to download original image: {str(e)}")
            
            try:
                minioClient.fget_object(s3Bucket, generated_object_key, generated_image_path)
            except Exception as e:
                raise Exception(f"Failed to download analyzed image: {str(e)}")
            
            try:
                minioClient.fget_object(s3Bucket, metadata_object_key, metadata_path)
            except Exception as e:
                raise Exception(f"Failed to download metadata: {str(e)}")

        except Exception as e:
            cleanup_temp_dir()
            abort(500, f"Download error: {str(e)}")

        # Verify all files exist and have content
        files_to_check = [
            (base_image_path, "original image"),
            (generated_image_path, "analyzed image"),
            (metadata_path, "metadata")
        ]
        
        for file_path, file_desc in files_to_check:
            if not os.path.exists(file_path):
                cleanup_temp_dir()
                raise Exception(f"Failed to download {file_desc}")
            if os.path.getsize(file_path) == 0:
                cleanup_temp_dir()
                raise Exception(f"{file_desc} is empty")

        # Create ZIP file
        zip_filename = f"inference_{inference.id}_results.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            # Add files with descriptive names
            zipf.write(base_image_path, f"original_image_{inference.id}.jpg")
            zipf.write(generated_image_path, f"analyzed_image_{inference.id}.jpg")
            zipf.write(metadata_path, f"analysis_metadata_{inference.id}.json")
            
            # Add a README file
            readme_content = f"""Resultados de Análisis - ID: {inference.id}
Generado el: {inference.createdOn}
Modelo utilizado: {inference.modelId}

Archivos incluidos:
- original_image_{inference.id}.jpg: La imagen original subida
- analyzed_image_{inference.id}.jpg: Imagen con los objetos detectados resaltados
- analysis_metadata_{inference.id}.json: Datos detallados del análisis (coordenadas de detección, puntuaciones de confianza, etc.)

Este archivo ZIP fue generado por el sistema de análisis de IA NeuroBerry.
"""
            zipf.writestr(f"README_{inference.id}.txt", readme_content)

        if not os.path.exists(zip_path):
            cleanup_temp_dir()
            raise Exception("Failed to create ZIP file")
        
        zip_size = os.path.getsize(zip_path)
        if zip_size == 0:
            cleanup_temp_dir()
            raise Exception("Created ZIP file is empty")

        def generate_file():
            try:
                with open(zip_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            finally:
                cleanup_temp_dir()

        response = Response(
            generate_file(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{secure_filename(zip_filename)}"',
                'Content-Length': str(zip_size),
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/zip'
            }
        )
        
        return response

    except Exception as e:
        cleanup_temp_dir()
        
        return jsonify({
            "error": "Download failed",
            "message": str(e),
            "inference_id": inference_id
        }), 500
