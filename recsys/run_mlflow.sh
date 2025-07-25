#while read line; do export $line; done < .env
source .env

export MLFLOW_S3_ENDPOINT_URL=https://storage.yandexcloud.net
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export AWS_BUCKET_NAME=$S3_BUCKET_NAME

mlflow server \
  --registry-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
  --backend-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
    --default-artifact-root s3://$AWS_BUCKET_NAME \
    --no-serve-artifacts