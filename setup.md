# dremio- minioS3

Connection Properties:
"Enable compatibility mode"

fs.s3a.path.style.access 
fs.s3a.endpoint: minio-s3:9000
fs.s3a.access.key
fs.s3a.secret.key

# python in vscode
Clear everything: delete ~/.vscode folder

Auto-Complete:
In your workspace or user settings (settings.json), set:
{
    "python.languageServer": "Pylance"
}

Parameter Hints:
Ensure that parameter hints are enabled. In your settings, verify:
{
    "editor.parameterHints.enabled": true
}
Now, when you type a function name and open a parenthesis, VS Code will display the function signature.
Auto-Completion Settings:
VS Code should automatically show suggestions as you type. To reinforce this, check that:
{
    "editor.quickSuggestions": {
        "other": true,
        "comments": false,
        "strings": true
    },
    "editor.suggestOnTriggerCharacters": true
}

Some libraries (like pyspark, pandas, etc.) may not have type hints.
Install type stub packages for better auto-completion, e.g.:
pip install pyspark-stubs
pip install pandas-stubs

# kafka and kafka connect, CDC, Iceberg Kafka Connect Demo

This demonstration will send data into an Apache Kafka topic which will be picked up by the Iceberg Connector for Kafka Connect and written to an Iceberg table.

## Technologies involved
- Apache Iceberg
- Apache Spark / PySpark
- MinIo
- Apache Kafka
- Kafka Connect
- Python

## Steps to run demo
1. Launch server applications

    `docker compose up -d`s
2. Create Kafka topic3

    `docker exec -t broker kafka-topics --create --topic completed-pizzas --partitions 6 --bootstrap-server broker:9092`
3. Launch the Iceberg connector (installed via docker compose)
- create a connector using local S3 as catalog

`curl -X PUT http://localhost:8083/connectors/pizzas-on-ice/config \
     -i -H "Content-Type: application/json" -d @dev-test/kafka-connect/pizza_on_ice_hadoop_catalog.json`

- create a connector using jdbc as catalog
    `curl -X PUT http://localhost:8083/connectors/pizzas-on-ice/config \
     -i -H "Content-Type: application/json" -d @dev-test/kafka-connect/pizza_on_ice_jdbc_catalog.json`
4. Check status of connector

    `curl http://localhost:8083/connectors/pizzas-on-ice/status |jq`
5. Install `confluent-kafka` package

    `pip install confluent-kafka`
6. In a seperate terminal window, run the pizza loader script

    `python pizza_loader.py`
7. Launch PySpark

    `docker exec -it spark-iceberg pyspark`
8. Explore Iceberg table

    `df = spark.table("demo.rpc.pizzas")`

    `df.count()`

    `df.show(5)`

    `df.groupBy("store_id").count().sort("count", ascending=False).show(5)`

9. Clean up resources when you're done.

    `docker compose down`

# Test 
`docker compose exec spark-iceberg spark-submit dev-test/code/spark-iceberg-minio-nessie.py` 

Some spark catalog config can be override in the test and some are not.
if not set in the code, it will use the default catalog config form spark-default.conf filed