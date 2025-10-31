set -a
. ./.env
set +a

IMAGE_VERSION=${IMAGE_VERSION:-$(poetry version -s)}

CONTAINER_PORT=12345

docker run -itd --name mcarchive-backend \
--restart=unless-stopped \
-p $CONTAINER_PORT:8080 \
-e SQL_DATABASE_URI="sqlite:////database/database.db" \
-v /mnt/docker/mcarchive/config:/workspace/.env \
-v /mnt/docker/mcarchive/database.db:/database/database.db \
mcarchive-backend:$IMAGE_VERSION
