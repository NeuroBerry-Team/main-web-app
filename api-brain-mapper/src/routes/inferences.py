import os
import uuid
import datetime
import requests
import json
from dotenv import load_dotenv
from io import BytesIO

from flask import Blueprint, request, jsonify, abort, g, send_file
from logs.logger import logger

from ..database.dbConnection import db
from ..models.inference import Inference
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
        payload = {"imgObjectKey": imgObjectKey}
        logger.info(f"Generating inference for user {g.uid}: {imgObjectKey}")
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
        # TODO: Should be set on the web app, for now it's the default model 1
        modelId=1,
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

    # Respond with the generatedImageUrl
    return jsonify({"generatedImgUrl": generatedImageUrl}), 200


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
