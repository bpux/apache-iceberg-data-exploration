#!/bin/bash

SPARK_WORKLOAD=$1

echo "SPARK_WORKLOAD: $SPARK_WORKLOAD"

if [ "$SPARK_WORKLOAD" == "master" ];
then
  start-master.sh -p 7077

  #eval notebook
elif [ "$SPARK_WORKLOAD" == "worker" ];
then
  WORKER_PORT=${2:-8081}
  echo "$WORKER_PORT"

  start-worker.sh spark://spark-iceberg:7077 --webui-port "$WORKER_PORT"
elif [ "$SPARK_WORKLOAD" == "history" ]
then
  start-history-server.sh

elif [ "$SPARK_WORKLOAD" == "notebook" ]; then
  export PYSPARK_DRIVER_PYTHON=jupyter
  export PYSPARK_DRIVER_PYTHON_OPTS="lab --notebook-dir=/home/iceberg/notebooks --ip='0.0.0.0' --NotebookApp.token='' --port=8888 --no-browser --allow-root"
  #start pyspark with jupyter lab, set max core to 2
  exec pyspark --master spark://spark-iceberg:7077 --conf spark.cores.max=2
else
  echo "Unknown SPARK_WORKLOAD: $SPARK_WORKLOAD"
fi

# Keep the container running. debug only
#tail -f /dev/null
