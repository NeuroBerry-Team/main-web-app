#!/bin/sh

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
until mc alias set local http://s3:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}; do
    echo "MinIO not ready yet, retrying in 5 seconds..."
    sleep 5
done

echo "MinIO is ready, starting configuration..."

# Create buckets
echo "Creating buckets..."
mc mb local/dataset --ignore-existing
mc mb local/inferences --ignore-existing

# Set anonymous read access for buckets
echo "Setting anonymous read access..."
mc anonymous set download local/dataset
mc anonymous set download local/inferences

# Create app user
echo "Creating app user..."
mc admin user add local ${S3_ACCESS_KEY} ${S3_SECRET_KEY}

# Create policy from mounted file
echo "Creating policy..."
mc admin policy create local myapp-policy /workspace/minio-policy.json

# Attach policy to user
echo "Attaching policy to user..."
mc admin policy attach local myapp-policy --user ${S3_ACCESS_KEY}

echo "MinIO setup completed successfully!"
