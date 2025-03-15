FROM python:3.11-bullseye AS pyspark-base

# Install tools required by the OS
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      curl \
      vim \
      unzip \
      openjdk-11-jdk \
      build-essential \
      software-properties-common \
      telnet \
      rsync \
      ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Setup the directories for our Spark and Hadoop installations
ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV HADOOP_HOME=${HADOOP_HOME:-"/opt/hadoop"}
ENV PYTHONPATH=$SPARK_HOME/python/:$SPARK_HOME/python/lib/py4j-0.10.9.5-src.zip:$PYTHONPATH

RUN mkdir -p ${HADOOP_HOME} && mkdir -p ${SPARK_HOME}
WORKDIR ${SPARK_HOME}

# Download and install Spark
ENV SPARK_VERSION=3.5.4

RUN curl https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz -o spark-${SPARK_VERSION}-bin-hadoop3.tgz \
 && tar xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz --directory ${SPARK_HOME} --strip-components 1 \
 && rm -rf spark-${SPARK_VERSION}-bin-hadoop3.tgz

# Install python deps
COPY requirements/requirements.txt .
RUN pip3 install -r requirements.txt

# Setup Spark related environment variables
ENV PATH="${SPARK_HOME}/sbin:${SPARK_HOME}/bin:${PATH}"
ENV SPARK_MASTER="spark://spark-iceberg:7077"
ENV SPARK_MASTER_HOST spark-iceberg
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3


RUN chmod u+x ${SPARK_HOME}/sbin/* && \
    chmod u+x ${SPARK_HOME}/bin/*


# spark-iceberg-base install basic required packages, like AWS, Iceberg, etc..
FROM pyspark-base AS spark-iceberg-base

# Extract the major version from SPARK_VERSION
ARG SPARK_MAJOR_VERSION=${SPARK_VERSION%.*}
ARG ICEBERG_VERSION=1.8.1
ARG ICEBERG_SPARK_SCALA="${SPARK_MAJOR_VERSION}_2.12"
ARG JAR_PACKAGE="iceberg-spark-runtime-${ICEBERG_SPARK_SCALA}-${ICEBERG_VERSION}.jar"

# Download iceberg spark runtime
RUN curl https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-${ICEBERG_SPARK_SCALA}/${ICEBERG_VERSION}/${JAR_PACKAGE} -Lo ${SPARK_HOME}/jars/${JAR_PACKAGE}

# Download Java AWS bundle
# RUN curl https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.17.257/bundle-2.17.257.jar -Lo ${SPARK_HOME}/jars/bundle-2.17.257.jar
RUN curl -s https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar -Lo ${SPARK_HOME}/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && unzip awscliv2.zip \
 && sudo ./aws/install \
 && rm awscliv2.zip \
 && rm -rf aws/

# Download Hadoop AWS and AWS SDK JARs. 
# These are needed for the Hadoop AWS module to work for AWS S3 access
# when we use localstack as the S3 endpoint. 
# use newer version has issues to access s3 "missing s3/model/ObjectTransfer??"
RUN curl -s https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.3/hadoop-aws-3.3.3.jar -Lo ${SPARK_HOME}/jars/hadoop-aws-3.3.3.jar \
    && curl -s https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar -Lo ${SPARK_HOME}/jars/aws-java-sdk-bundle-1.11.901.jar

# install jupyterlab and ijava. we have it running inside spark-master container
ARG jupyterlab_version=4.0.8
RUN apt-get update -y && \
     apt-get install -y python3-pip python3-dev && \
     pip3 install --upgrade pip && \
     pip3 install wget jupyterlab==${jupyterlab_version}
 
# config the spark-iceberg images     
FROM spark-iceberg-base AS spark-iceberg-plugins

########### install requried 3rd party catalog jars ##################
# Install PostgreSQL JDBC Driver, we use postgresql as our metastore
RUN curl "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.5/postgresql-42.7.5.jar" -o "postgresql-42.7.5.jar" \
    && mv postgresql-42.7.5.jar "${SPARK_HOME}/jars/postgresql-42.7.5.jar"

RUN curl "https://repo1.maven.org/maven2/org/projectnessie/nessie-integrations/nessie-spark-extensions-${ICEBERG_SPARK_SCALA}/0.103.0/nessie-spark-extensions-${ICEBERG_SPARK_SCALA}-0.103.0.jar" -o "nessie-spark-extensions-${ICEBERG_SPARK_SCALA}.jar" \
    && mv nessie-spark-extensions-${ICEBERG_SPARK_SCALA}.jar "${SPARK_HOME}/jars/nessie-spark-extensions-${ICEBERG_SPARK_SCALA}.jar"

# config the spark-iceberg images, final touches.. should be configs at here only 
FROM spark-iceberg-plugins AS spark-iceberg

# Add iceberg spark runtime jar to IJava classpath, it's jupter kernel for running java
ENV IJAVA_CLASSPATH=${SPARK_HOME}/jars/*

#=============== Temp Debug start, delete the whole section after debug =========
# the ke-jars folder is used to add customized jars, 
# then we can add volume map in docker-compose file 
#================================================================================
RUN mkdir -p ${SPARK_HOME}/ke-jars
ENV IJAVA_CLASSPATH=${SPARK_HOME}/ke-jars:${IJAVA_CLASSPATH}
ENV SPARK_CLASSPATH=${SPARK_HOME}/ke-jars:${SPARK_CLASSPATH}
ENV PYSPARK_SUBMIT_ARGS="--jars ${SPARK_HOME}/ke-jars/* pyspark-shell"

# RUN rm ${SPARK_HOME}/jars/iceberg-spark-runtime-3.5_2.12-1.4.3.jar

# COPY ./iceberg-spark-runtime-3.5_2.12*.jar "${SPARK_HOME}/jars/iceberg-spark-runtime-3.5_2.12-1.4.3-ke.jar"
#=============== Temp Debug end =========


RUN mkdir -p /home/iceberg/localwarehouse /home/iceberg/notebooks /home/iceberg/warehouse /home/iceberg/spark-events /home/iceberg

# Add a notebook command
RUN echo '#! /bin/sh' >> /bin/notebook \
 && echo 'export PYSPARK_DRIVER_PYTHON=jupyter' >> /bin/notebook \
 && echo "export PYSPARK_DRIVER_PYTHON_OPTS=\"lab --notebook-dir=/home/iceberg/notebooks --ip='0.0.0.0' --NotebookApp.token='' --port=8888 --no-browser --allow-root\"" >> /bin/notebook \
# && echo 'pyspark --master local[*]' >> /bin/notebook \
    && echo 'pyspark --conf spark.cores.max=2' >> /bin/notebook \
 && chmod u+x /bin/notebook

# Copy appropriate entrypoint script
COPY entrypoint.sh .
ENTRYPOINT ["./entrypoint.sh"]
CMD ["notebook"]
