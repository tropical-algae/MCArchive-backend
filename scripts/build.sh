set -a
. ./.env
set +a

IMAGE_VERSION=${IMAGE_VERSION:-$(poetry version -s)}

docker build -t mcarchive-backend:$IMAGE_VERSION .
echo "✅ Successfully built build Docker Image!"
