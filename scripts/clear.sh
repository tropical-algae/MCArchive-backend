set -a
. ./.env
set +a

IMAGE_VERSION=${IMAGE_VERSION:-$(poetry version -s)}

docker rm -f mcarchive-backend
docker rmi -f mcarchive-backend:$IMAGE_VERSION
