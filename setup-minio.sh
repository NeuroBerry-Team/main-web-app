#!/bin/sh

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
until mc alias set local http://s3:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}; do
    echo "MinIO not ready yet, retrying in 5 seconds..."
    sleep 5
done

echo "MinIO is ready, starting configuration..."

# Create buckets only if they don't exist
echo "Checking and creating buckets..."
if ! mc ls local/dataset >/dev/null 2>&1; then
    echo "Creating dataset bucket..."
    mc mb local/dataset
else
    echo "Dataset bucket already exists, skipping..."
fi

if ! mc ls local/inferences >/dev/null 2>&1; then
    echo "Creating inferences bucket..."
    mc mb local/inferences
else
    echo "Inferences bucket already exists, skipping..."
fi

# Set anonymous read access only if not already set
echo "Checking and setting anonymous read access..."
dataset_policy=$(mc anonymous get local/dataset 2>/dev/null)
case "$dataset_policy" in
    *download*)
        echo "Anonymous read access already set for dataset bucket, skipping..."
        ;;
    *)
        echo "Setting anonymous read access for dataset bucket..."
        mc anonymous set download local/dataset
        ;;
esac

inferences_policy=$(mc anonymous get local/inferences 2>/dev/null)
case "$inferences_policy" in
    *download*)
        echo "Anonymous read access already set for inferences bucket, skipping..."
        ;;
    *)
        echo "Setting anonymous read access for inferences bucket..."
        mc anonymous set download local/inferences
        ;;
esac

# Create app user only if it doesn't exist
echo "Checking and creating app user..."
if ! mc admin user info local ${S3_ACCESS_KEY} >/dev/null 2>&1; then
    echo "Creating app user..."
    mc admin user add local ${S3_ACCESS_KEY} ${S3_SECRET_KEY}
else
    echo "App user already exists, skipping..."
fi

# Create policy only if it doesn't exist
echo "Checking and creating policy..."
if ! mc admin policy info local myapp-policy >/dev/null 2>&1; then
    echo "Creating policy..."
    mc admin policy create local myapp-policy /workspace/minio-policy.json
else
    echo "Policy already exists, skipping..."
fi

# Attach policy to user only if not already attached
echo "Checking and attaching policy to user..."
user_policies=$(mc admin user info local ${S3_ACCESS_KEY} 2>/dev/null)
case "$user_policies" in
    *myapp-policy*)
        echo "Policy already attached to user, skipping..."
        ;;
    *)
        echo "Attaching policy to user..."
        mc admin policy attach local myapp-policy --user ${S3_ACCESS_KEY}
        ;;
esac

echo "Checking and uploading datasets if needed..."
# Upload datasets only if they don't already exist in MinIO
for dataset in /workspace/datasets/*/; do
    if [ -d "$dataset" ]; then
        dataset_name=$(basename "$dataset")
        echo "Checking dataset: $dataset_name"
        
        # Check if dataset already exists in MinIO by looking for actual content
        dataset_content=$(mc ls "local/dataset/$dataset_name/" 2>/dev/null)
        if [ -n "$dataset_content" ]; then
            echo "Dataset $dataset_name already exists in MinIO, skipping..."
        else
            echo "Uploading dataset: $dataset_name"
            mc cp --recursive "$dataset" "local/dataset/$dataset_name/"
            echo "✓ Uploaded $dataset_name"
        fi
    fi
done

echo "All datasets checked and uploaded if needed!"

echo "MinIO setup completed successfully!"