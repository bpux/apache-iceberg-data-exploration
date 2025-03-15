import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.SaveMode

object IcebergExample {
  def main(args: Array[String]): Unit = {
    // Initialize Spark session
    val spark = SparkSession.builder.appName("IcebergExample").getOrCreate()

    // Step 1: Read input-data.csv
    val df = spark.read.option("header", "true").option("inferSchema", "true").csv("s3a://kxu-iceberg-data/input-data.csv")

    // Step 2: Save as Iceberg table
    df.write
      .format("iceberg")
      .mode(SaveMode.Overwrite)
      .save("data.default.input_data")

    // Step 3: Read the data and print out
    val icebergDf = spark.read
      .format("iceberg")
      .load("data.default.input_data")
    icebergDf.show()

    // Step 4: Add another row to the table
    import spark.implicits._
    val newRow = Seq((4, "new_data")).toDF("id", "data")
    newRow.write
      .format("iceberg")
      .mode(SaveMode.Append)
      .save("data.default.input_data")

    // Read the data again and print out
    val updatedIcebergDf = spark.read
      .format("iceberg")
      .load("data.default.input_data")
    updatedIcebergDf.show()

    // Stop the Spark session
    spark.stop()
  }
}