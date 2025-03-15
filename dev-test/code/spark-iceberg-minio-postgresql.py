import os
import pandas as pd
import boto3
import logging
from pyspark.sql import SparkSession
from botocore.client import Config
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d - %(funcName)s]'
)
logger = logging.getLogger(__name__)

minio_endpoint = 'http://minio-s3:9000'  # Change to your MinIO endpoint if different
minio_access_key = 'user'
minio_secret_key = 'password'
bucket_name = 'kxu-iceberg-data'
object_name = 'input-data.csv'
file_path = 'dev-test/testdata/input-data.csv'  # test data file path

def upload_data_to_s3():
    # Initialize the S3 client with MinIO configuration
    s3_client = boto3.client(
        's3',
        endpoint_url=minio_endpoint,
        aws_access_key_id=minio_access_key,
        aws_secret_access_key=minio_secret_key,
        config=Config(signature_version='s3v4')
    )

    # Check if the object exists
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_name)
        logger.info(f"Object '{object_name}' already exists in bucket '{bucket_name}'. Skipping upload.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Object does not exist, proceed with upload
            try:
                s3_client.upload_file(file_path, bucket_name, object_name)
                logger.info(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
            except Exception as e:
                logger.error(f"Error uploading file: {e}")
        else:
            # Something else has gone wrong.
            logger.error(f"Error checking if object exists: {e}")

def run_spark_job():
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("IcebergExample") \
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint) \
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.defaultCatalog", "cdc") \
        .getOrCreate()

    # Step 1: Read input-data.csv
    df = spark.read.csv(f"s3a://{bucket_name}/input-data.csv", header=True, inferSchema=True)
    logger.info("\n==================CSV data loaded:==================\n")
    df.show()
    logger.info("\n=======================================================\n")

    table_name = "input_data_test_pg_catalog"
    namespace = "db_test_2"
    # Step 2: Save as Iceberg table
    df.writeTo(f"{namespace}.{table_name}").createOrReplace()

    # Step 3: Read the data and print out
    iceberg_df = spark.read.format("iceberg").load(f"{namespace}.{table_name}")
    logger.info("\n==================Iceberg Table Data:==================\n")
    iceberg_df.show()
    logger.info("\n=======================================================\n")

    # Step 4: Add another row to the table
    new_data = [("New James", "Smith")]
    df = spark.createDataFrame(data=new_data, schema=iceberg_df.schema)
    df.writeTo(f"{namespace}.{table_name}").append()

    # Read the data again and print out
    updated_iceberg_df = spark.read.format("iceberg").load(f"{namespace}.{table_name}")
    logger.info("\n==================Iceberg Table Data:==================\n")
    updated_iceberg_df.show()
    logger.info("\n=======================Test Completed and Success================================\n")

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    logger.info("\n=======================Test Started================================\n")
    # Step 1: upload data to S3
    upload_data_to_s3()

    # Step 2: Run PySpark job to process the data
    run_spark_job()
    logger.info("\n=======================Test Completed and Success================================\n")