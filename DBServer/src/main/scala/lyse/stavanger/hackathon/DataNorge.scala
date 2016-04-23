package lyse.stavanger.hackathon

import org.apache.spark.rdd.RDD
import fr.simply._
import fr.simply.util.ContentType
import fr.simply.util.Text_Json
import org.simpleframework.http.Request
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Column
import org.apache.spark.sql.functions._
import java.net.Socket
import java.net.InetAddress
import scala.io.BufferedSource
import java.io.PrintStream

object Utils {
  val d2r = math.Pi / 180.0
  def haversine_km(lat1: Column, long1: Column, lat2: Double, long2: Double) = {
    val dlong = (long1 - long2) * d2r;
    val dlat = (lat1 - lat2) * d2r;
    val a = pow(sin(dlat / 2.0), 2) + cos(lat1 * d2r) * math.cos(lat2 * d2r) * pow(sin(dlong / 2.0), 2);

    val c = atan2(sqrt(a), sqrt((a - 1) * -1)) * 2
    val d = c * 6367
    d
  }

  def socketWrite(hostname: String, port: Int = 4242, opentsdbin: String) {
    val s = new Socket(InetAddress.getByName(hostname), port)
    lazy val in = new BufferedSource(s.getInputStream()).getLines()
    val outStream = new PrintStream(s.getOutputStream())
    outStream.println(opentsdbin)
    outStream.flush()
    s.close()
  }
}
object DataNorge {

  def main(args: Array[String]) = {
    val numCores = args(0).toInt
    val datasetNamesFilePath = args(1)
    val dataSetDir = args(2)
    val opentsdbHost = args(3)
    val sc = CustomSparkContext.create(numCores = numCores)
    val sqlContext = new org.apache.spark.sql.SQLContext(sc)

    val datasets = DataStructures.getDataSetNames(sc, datasetNamesFilePath)
    val datasetNameIndexMap = datasets.map({ var i = (-1); d => i += 1; (d -> i) }).toMap

    val columnsAndAliasOfTypeLongitude = Array("longitude", "lengdegrad")
    val columnsAndAliasOfTypeLatitude = Array("latitude", "breddegrad")

    //Based on a list of datasource names, we automatically load them in memory and infer their datatype. We dont need to seperately write logic for each data source as the following handles all
    for (i <- 0 until datasets.length) {
      val path = dataSetDir + "/data.norge/current/" + datasets(i) + ".csv"
      val x = sqlContext.read
        .format("com.databricks.spark.csv")
        .option("header", "true") // Use first line of all files as header
        .option("inferSchema", "true") // Automatically infer data types
        .option("delimiter", ";") //Set a custom seperator
        .load(path)

      //#Hotfix: Removes a hidden prefix char byte to the 1st col.header of each table
      val firstColumnIndex = 0
      val oldFirstColumn = x.schema.fieldNames(firstColumnIndex)
      val newFirstColumn = ({ if (oldFirstColumn.charAt(0).toByte == -1) oldFirstColumn.drop(1) else oldFirstColumn })

      x.withColumnRenamed(oldFirstColumn, newFirstColumn)
        .registerTempTable(datasets(i))

      sqlContext.cacheTable(datasets(i))
    }

    //Create a HTTP server to serve requests
    val filteredRDDResponse: Request => StaticServerResponse = {
      request =>
        val datasets = request.getParameter("source").split(",")
        
        //All datasources has longitude and latitude except Skoleruter
        val _longitude = request.getParameter("longitude")
        val longitude = if (_longitude != null) _longitude.toDouble else 0.toDouble
        val _latitude = request.getParameter("latitude")
        val latitude = if (_latitude != null) _latitude.toDouble else 0.toDouble

        val _radius = request.getParameter("radius")
        val radius = if (_radius != null) _radius.toFloat else 0.toFloat
        //for datasource Skoleruter we use either of the following conditions
        val dato = request.getParameter("dato")
        val skole = request.getParameter("skole")
        val timestamp: Long = System.currentTimeMillis / 1000
        val out =
          datasets.map {
            var out = ""

            source =>
              val df = sqlContext.sql("select * from " + source)

              //99% of datasets from Data.Norge has a lat, log
              if (longitude != 0.toDouble && latitude != 0.toDouble && source != "skoleruter") {
                val dfFields = df.schema.fields.map(_.name)
                val dfLongitudeArtName = dfFields.filter { x =>
                  columnsAndAliasOfTypeLongitude.contains(x.toLowerCase())
                }.head
                val dfLatitudeArtName = dfFields.filter { x =>
                  columnsAndAliasOfTypeLatitude.contains(x.toLowerCase())
                }.head

                //Store the request about what people want to see about their city. We can later perform some form of machine learning 
                val opentsdbin = "put data.norge." + source + " " + timestamp + " 1 longitude=" + longitude + " latitude=" + latitude                
                Utils.socketWrite(opentsdbHost, 4242, opentsdbin)

                out = "{" + source + "={" + df.where(Utils.haversine_km(df(dfLatitudeArtName), df(dfLongitudeArtName), latitude, longitude).leq(radius))
                  .toJSON.collect.mkString(",") + "}}"
              }

              //Data.Norge has a dataset "skoleruter" with no lat, lon. We process query o it differently
              if (dato != null && skole != null && source == "skoleruter") {
                //Store the request about what people want to see about their city. We can later perform some form of machine learning 
                val opentsdbin = "put data.norge." + source + " " + timestamp + " 1 dato=" + longitude + " skole=" + skole
                out = "{" + source + "={" + df.where(df("dato") === dato && df("skole") === skole)
                  .toJSON.collect.mkString(",") + "}}"
                Utils.socketWrite(opentsdbHost, 4242, opentsdbin)
              }

              out
          }.mkString(",")

        StaticServerResponse(Text_Json, out, 200)
    }

    val route = GET(
      path = "/DataNorge",
      response = DynamicServerResponse(filteredRDDResponse))

    val server = new StubServer(8080, route).start
  }
}