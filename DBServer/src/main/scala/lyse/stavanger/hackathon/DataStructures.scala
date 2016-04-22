package lyse.stavanger.hackathon

import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD

object DataStructures {
  /**
   * Get the names of all the datasets collected from data.norge
   */
  def getDataSetNames(sc: SparkContext, datasetNamesFilePath: String): Array[String] = {

    val datasets = sc.textFile(datasetNamesFilePath).collect()
    datasets
  }

  def isHeader(line: String, token: String): Boolean = {
    line.contains(token)
  }
}
