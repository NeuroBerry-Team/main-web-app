import os
import uuid
import datetime
import requests
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Blueprint, request, jsonify, abort, g, Response
from logs.logger import logger

from ..database.dbConnection import db
from ..models.inference import Inference
from ..models.model import Model
from ..models.audit_log import AuditLog
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
@inferences.route("/generateInference", methods=["POST"])
@auth_required()
@rate_limit_api(max_attempts=5, window_minutes=10)
def generateInference():
    # Get form data
    img_file = request.files.get("image")
    model_id = request.form.get("modelId", "1")
    name = request.form.get("name", "unnamed")

    # Validate model_id
    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        abort(400, "Invalid model ID")

    if model_id <= 0:
        abort(400, "Invalid model ID")

    # Validate that the model exists in the database
    model = Model.query.get(model_id)
    if not model:
        abort(404, "Model not found")

    # Validate and sanitize inputs
    name = InputValidator.sanitize_string(name, max_length=200)

    # Validate image
    if not img_file:
        abort(400, "Image file is required")

    image_data = img_file.read()

    try:
        FileUploadSecurity.validate_file_type(name, image_data, "image")
        FileUploadSecurity.validate_file_size(image_data, "image")
    except ValueError as e:
        abort(400, str(e))

    # Generate unique folder and object keys
    folder_name = str(uuid.uuid4().hex)
    imgObjectKey = f"{g.uid}/{folder_name}/original_img.jpg"
    result_object_key = f"{g.uid}/{folder_name}/inference_result.jpg"
    metadata_object_key = f"{g.uid}/{folder_name}/metadata.json"

    # Send to NN API
    try:
        # Get the name of the model. NN API needs it to switch models.
        model_name = model.name

        logger.info(
            f"Generating inference for user {g.uid}: {imgObjectKey} with model {model_name}"
        )

        # Send binary image data to NN API
        json_response = nnClient.generateInferenceWithBinary(
            image_data, model_name, imgObjectKey
        )

        # Extract base64 image and metadata from NN API response
        result_image_b64 = json_response["result_image"]
        metadata = json_response["metadata"]

        import base64

        result_image_data = base64.b64decode(result_image_b64)

        # Upload images and metadata to MinIO
        from io import BytesIO

        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")

        # Upload original image
        minioClient.put_object(
            s3Bucket,
            imgObjectKey,
            BytesIO(image_data),
            length=len(image_data),
            content_type="image/jpeg",
        )

        # Upload inference result image
        minioClient.put_object(
            s3Bucket,
            result_object_key,
            BytesIO(result_image_data),
            length=len(result_image_data),
            content_type="image/jpeg",
        )

        # Upload metadata as JSON
        import json as json_lib

        metadata_json = json_lib.dumps(metadata).encode("utf-8")
        minioClient.put_object(
            s3Bucket,
            metadata_object_key,
            BytesIO(metadata_json),
            length=len(metadata_json),
            content_type="application/json",
        )

        # Generate URLs for the uploaded files
        s3LiveBaseUrl = os.getenv("S3_LIVE_BASE_URL") + s3Bucket
        baseImageUrl = f"{s3LiveBaseUrl}/{imgObjectKey}"
        generatedImageUrl = f"{s3LiveBaseUrl}/{result_object_key}"
        metadataUrl = f"{s3LiveBaseUrl}/{metadata_object_key}"

    except Exception:
        logger.exception(f"Error generating inference for {imgObjectKey}")
        abort(500, "Error generating inference")

    user_id = getattr(g, "uid", None)

    # Create new inference record
    new_inference = Inference(
        userId=user_id,
        modelId=model_id,
        name=name,
        baseImageUrl=baseImageUrl,
        generatedImageUrl=generatedImageUrl,
        metadataUrl=metadataUrl,
        createdOn=datetime.datetime.utcnow(),
    )

    # Save inference in DB
    try:
        db.session.add(new_inference)
        db.session.commit()
    except Exception:
        logger.exception(f"Error saving in DB inference of {imgObjectKey}")
        abort(500, "Error while saving inference")

    # Respond with the generated data
    try:
        presigned_base_url = minioClient.presigned_get_object(
            s3Bucket,
            imgObjectKey,
            expires=datetime.timedelta(hours=24)
        )
        presigned_generated_url = minioClient.presigned_get_object(
            s3Bucket,
            result_object_key,
            expires=datetime.timedelta(hours=24)
        )
    except Exception as e:
        logger.warning(f"Failed to generate presigned URLs: {str(e)}")
        presigned_base_url = baseImageUrl
        presigned_generated_url = generatedImageUrl
    
    return (
        jsonify(
            {
                "success": True,
                "generatedImgUrl": presigned_generated_url,
                "baseImageUrl": presigned_base_url,
                "id": new_inference.id,
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
            return (
                jsonify({"error": "Inference not found", "inference_id": inference_id}),
                404,
            )

        if not inference.baseImageUrl or not inference.generatedImageUrl:
            return (
                jsonify({"error": "Incomplete inference data - missing image URLs"}),
                400,
            )

        temp_dir = tempfile.mkdtemp(prefix=f"inference_{inference_id}_")

        # Prepare file paths in temp directory
        base_image_path = os.path.join(temp_dir, f"original_image_{inference.id}.jpg")
        generated_image_path = os.path.join(
            temp_dir, f"analyzed_image_{inference.id}.jpg"
        )
        metadata_path = os.path.join(temp_dir, f"metadata_{inference.id}.json")

        # Download files from MinIO
        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")

        try:
            s3_live_base_url = os.getenv("S3_LIVE_BASE_URL")
            s3_port = os.getenv("S3_PORT", "9000")

            def extract_object_key_from_url(url):
                if url.startswith(s3_live_base_url):
                    path_after_base = url[len(s3_live_base_url) :]
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
                            matched_base = url[: match.end()]
                        else:
                            url_parts = url.split("/")
                            if len(url_parts) >= 4 and ":" in url_parts[2]:
                                matched_base = "/".join(url_parts[:3]) + "/"
                            else:
                                raise ValueError(
                                    f"URL doesn't match any expected MinIO pattern: {url}"
                                )

                    path_after_base = url[len(matched_base) :]

                if path_after_base.startswith(f"{s3Bucket}/"):
                    return path_after_base[len(f"{s3Bucket}/") :]
                else:
                    return path_after_base

            base_object_key = extract_object_key_from_url(inference.baseImageUrl)
            generated_object_key = extract_object_key_from_url(
                inference.generatedImageUrl
            )

            folder_path = "/".join(base_object_key.split("/")[:-1])
            metadata_object_key = f"{folder_path}/metadata.json"

            try:
                minioClient.fget_object(s3Bucket, base_object_key, base_image_path)
            except Exception as e:
                raise Exception(f"Failed to download original image: {str(e)}")

            try:
                minioClient.fget_object(
                    s3Bucket, generated_object_key, generated_image_path
                )
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
            (metadata_path, "metadata"),
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

        with zipfile.ZipFile(
            zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
        ) as zipf:
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
                with open(zip_path, "rb") as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            finally:
                cleanup_temp_dir()

        response = Response(
            generate_file(),
            mimetype="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{secure_filename(zip_filename)}"',
                "Content-Length": str(zip_size),
                "Cache-Control": "no-cache",
                "Content-Type": "application/zip",
            },
        )

        return response

    except Exception as e:
        cleanup_temp_dir()

        return (
            jsonify(
                {
                    "error": "Download failed",
                    "message": str(e),
                    "inference_id": inference_id,
                }
            ),
            500,
        )


@inferences.route("/<int:inference_id>", methods=["DELETE"])
@auth_required()
@rate_limit_api(max_attempts=5, window_minutes=10)
def delete_inference(inference_id):
    try:
        # Get the inference from database
        inference = Inference.query.filter_by(id=inference_id, userId=g.uid).first()

        if not inference:
            return (
                jsonify({"error": "Inference not found", "inference_id": inference_id}),
                404,
            )

        # If we have inference data (there should always be), construct the folder path
        if inference.generatedImageUrl:
            base_object_key = inference.generatedImageUrl.split("/")[-2:]
            folder_name = base_object_key[0]  # UUID
        elif inference.baseImageUrl:
            base_object_key = inference.baseImageUrl.split("/")[-2:]
            folder_name = base_object_key[0]  # UUID
        else:
            return (
                jsonify(
                    {
                        "error": "Inference has no associated images to delete",
                        "inference_id": inference_id,
                    }
                ),
                400,
            )

        minioClient = getMinioClient()
        s3Bucket = os.getenv("S3_BUCKET_INFERENCES_RESULTS")
        try:
            from minio.deleteobjects import DeleteObject

            # List and delete all objects under the user's inference folder
            objects = list(
                minioClient.list_objects(s3Bucket, prefix=f"{g.uid}/{folder_name}/")
            )
            if objects:
                delete_object_list = [DeleteObject(obj.object_name) for obj in objects]
                delete_results = minioClient.remove_objects(
                    s3Bucket, delete_object_list
                )
                errors = list(delete_results)
                if errors:
                    for error in errors:
                        logger.error(
                            f"Error deleting object {error.object_name} for inference {inference_id}: {error.code} - {error.message}"
                        )
                    raise Exception(
                        f"Error deleting object {error.object_name}: {error.code} - {error.message}"
                    )
                logger.info(
                    f"Deleted {len(objects)} objects from MinIO for inference {inference_id}"
                )
            else:
                logger.warning(
                    f"No objects found in MinIO for inference {inference_id}"
                )
        except Exception as e:
            logger.exception(
                f"Error deleting objects from MinIO for inference {inference_id}: {str(e)}"
            )
            return (
                jsonify(
                    {
                        "error": "Error deleting associated images from storage",
                        "message": str(e),
                        "inference_id": inference_id,
                    }
                ),
                500,
            )

        # Only after successfully deleting from MinIO, delete the DB record
        db.session.delete(inference)
        db.session.commit()
        logger.info(f"Deleted inference {inference_id} from database")

        # Create audit log for inference deletion
        try:
            audit_log = AuditLog(
                userId=g.uid,
                action="INFERENCE_DELETED",
                entityType="inference",
                entityId=inference_id,
                timestamp=datetime.datetime.utcnow(),
            )
            db.session.add(audit_log)
            db.session.commit()
            logger.info(
                f"Audit log created for inference deletion {inference_id} by user {g.uid}"
            )
        except Exception as audit_error:
            logger.warning(
                f"Could not create audit log for inference deletion: {audit_error}"
            )

        return jsonify({"success": True, "message": "Inference deleted"}), 200
    except Exception as e:
        logger.exception(f"Error deleting inference {inference_id}: {str(e)}")
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Error deleting inference",
                    "message": str(e),
                    "inference_id": inference_id,
                }
            ),
            500,
        )
