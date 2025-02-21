import os
import pandas as pd
import boto3
import pyspark
from pyspark.sql import SparkSession
from botocore.client import Config
from botocore.exceptions import ClientError




minio_endpoint = 'http://minio-s3:9000'  # Change to your MinIO endpoint if different
minio_access_key = 'user'
minio_secret_key = 'password'
bucket_name = 'kxu-iceberg-data'


def upload_data_to_s3():
    # MinIO configuration
    file_path = 'dev-test/testdata/input-data.csv'  # Change to the path of your input-data.csv file
    object_name = 'input-data.csv'

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
        print(f"Object '{object_name}' already exists in bucket '{bucket_name}'. Skipping upload.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Object does not exist, proceed with upload
            try:
                s3_client.upload_file(file_path, bucket_name, object_name)
                print(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
            except Exception as e:
                print(f"Error uploading file: {e}")
        else:
            # Something else has gone wrong.
            print(f"Error checking if object exists: {e}")



def run_spark_job():
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("IcebergExample") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint) \
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.sql.catalog.data", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.data.warehouse", "s3://kxu-iceberg-data") \
        .config("spark.sql.catalog.data.s3.endpoint", "http://minio-s3:9000") \
        .config("spark.sql.catalog.data.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
        .config("spark.sql.catalog.data.catalog-impl", "org.apache.iceberg.jdbc.JdbcCatalog") \
        .config("spark.sql.catalog.data.uri", "jdbc:postgresql://pg-catalog:5432/kxuiceberg") \
        .config("spark.sql.catalog.data.jdbc.user", "kxuiceberg") \
        .config("spark.sql.catalog.data.jdbc.password", "kxuiceberg") \
        .getOrCreate()
    # Step 1: Read input-data.csv
    df = spark.read.csv("s3a://kxu-iceberg-data/input-data.csv", header=True, inferSchema=True)

    # Step 2: Save as Iceberg table
    df.writeTo("data.db.input_data").create()
    #df.write.format("iceberg").mode("overwrite").save("data.db.input_data")

    # Step 3: Read the data and print out
    iceberg_df = spark.read.format("iceberg").load("data.db.input_data")
    iceberg_df.show()

    # Step 4: Add another row to the table
    new_row = spark.createDataFrame([(4, "new_data")], ["id", "data"])
    new_row.write.format("iceberg").mode("append").save("data.db.input_data")

    # Read the data again and print out
    updated_iceberg_df = spark.read.format("iceberg").load("data.db.input_data")
    updated_iceberg_df.show()

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    # Step 1: upload data to S3
    upload_data_to_s3()

    # Step 2: Run PySpark job to process the data
    run_spark_job()
