import os
import pandas as pd
import boto3
import pyspark
from pyspark.sql import SparkSession
from botocore.client import Config
spark = SparkSession.builder.master("spark://localhost:7077").appName("Pi").getOrCreate()




minio_endpoint = 'http://localhost:9000'  # Change to your MinIO endpoint if different
minio_access_key = 'user'
minio_secret_key = 'password'
bucket_name = 'kxu-iceberg-data'


def generate_and_upload_input_data():
    # MinIO configuration
    file_path = 'input-data.csv'  # Change to the path of your input-data.csv file
    object_name = 'input-data.csv'

    # Initialize the S3 client with MinIO configuration
    s3_client = boto3.client(
        's3',
        endpoint_url=minio_endpoint,
        aws_access_key_id=minio_access_key,
        aws_secret_access_key=minio_secret_key,
        config=Config(signature_version='s3v4')
    )

    # Upload the file to the bucket
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{object_name}'.")
    except Exception as e:
        print(f"Error uploading file: {e}")

"""
spark = SparkSession.builder \
    .appName("GlueIceberg") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse", "s3://your-bucket/iceberg") \
    .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2,software.amazon.awssdk:bundle:2.20.18") \
    .config("spark.hadoop.fs.s3a.access.key", "YOUR_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET") \
    .getOrCreate()

"""

def run_spark_job():
    # Initialize Spark session
    spark = SparkSession.builder.appName("IcebergExample").getOrCreate()
    # Step 1: Read input-data.csv
    df = spark.read.csv("s3a://kxu-iceberg-data/input-data.csv", header=True, inferSchema=True)

    # Step 2: Save as Iceberg table
    df.write.format("iceberg").mode("overwrite").save("data.default.input_data")

    # Step 3: Read the data and print out
    iceberg_df = spark.read.format("iceberg").load("data.default.input_data")
    iceberg_df.show()

    # Step 4: Add another row to the table
    new_row = spark.createDataFrame([(4, "new_data")], ["id", "data"])
    new_row.write.format("iceberg").mode("append").save("data.default.input_data")

    # Read the data again and print out
    updated_iceberg_df = spark.read.format("iceberg").load("data.default.input_data")
    updated_iceberg_df.show()

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    # Step 1: Generate and upload input data to LocalStack S3
    #generate_and_upload_input_data()

    # Step 2: Run PySpark job to process the data
    run_spark_job()
