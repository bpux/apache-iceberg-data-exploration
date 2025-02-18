#postgres catalog instructions
down-pg-catalog:
	docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml down

start-pg-catalog:
	make stop-pg-catalog && docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml up

stop-pg-catalog:
	docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml stop

run-pg-catalog:
	make stop-pg-catalog && docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml up

spark-build-services-pg-catalog:
	docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml build spark-iceberg spark-worker spark-history-server --no-cache

build-pg-catalog:
	make down-pg-catalog && docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml build

clean-pg-catalog:
	docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml down --volumes --remove-orphans

clean-all-pg-catalog:
	docker compose -f docker-compose.yml -f docker-compose-pg-catalog.yml down --rmi="all" --volumes


#iceberg with minio s3 storage and pg catalog instructions
down-iceberg-minio:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml down


start-iceberg-minio:
	make stop-iceberg-minio && docker compose -f docker-compose.yml -f docker-compose-minio.yml up

stop-iceberg-minio:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml stop

run-iceberg-minio:
	make stop-iceberg-minio && docker compose -f docker-compose.yml -f docker-compose-minio.yml up

build-services-spark-iceberg-minio:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml build minio-s3 spark-iceberg spark-worker spark-history-server --no-cache

build-iceberg-minio:
	make down-iceberg-minio && docker compose -f docker-compose.yml -f docker-compose-minio.yml build

clean-iceberg-minio:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml down --volumes --remove-orphans

clean-all-iceberg-minio:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml down --rmi="all" --volumes


# minio s3 storage only instructions
build-minio:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml build minio-s3 minio-s3-init --no-cache

run-minio:
	make down-iceberg-minio && docker compose -f docker-compose.yml -f docker-compose-minio.yml up minio-s3 minio-s3-init

start-s3-storage:
	docker compose -f docker-compose.yml -f docker-compose-minio.yml up minio-s3

# localstack
stop-iceberg-localstack:
	docker compose -f docker-compose.yml -f docker-compose-localstack.yml stop

run-iceberg-localstack:
	make stop-iceberg-localstack && docker compose -f docker-compose.yml -f docker-compose-localstack.yml up --build

clean-iceberg-localstack:
	docker compose -f docker-compose.yml -f docker-compose-localstack.yml down --volumes --remove-orphans

clean-all-iceberg-localstack:
	docker compose -f docker-compose.yml -f docker-compose-localstack.yml down --rmi="all" --volumes

