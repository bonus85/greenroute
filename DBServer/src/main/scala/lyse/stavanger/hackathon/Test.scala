package lyse.stavanger.hackathon

import org.apache.spark.rdd.RDD
import fr.simply._
import fr.simply.util.ContentType
import fr.simply.util.Text_Json
import org.simpleframework.http.Request

import scala.io.Source

object Utils {
  val d2r = math.Pi / 180.0
  def haversine_km(lat1: Double, long1: Double, lat2: Double, long2: Double) = {
    val dlong = (long2 - long1) * d2r;
    val dlat = (lat2 - lat1) * d2r;
    val a = math.pow(math.sin(dlat / 2.0), 2) + math.cos(lat1 * d2r) * math.cos(lat2 * d2r) * math.pow(math.sin(dlong / 2.0), 2);
    val c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    val d = 6367 * c;
    d
  }

  def haversine_mi(lat1: Double, long1: Double, lat2: Double, long2: Double) = {
    val dlong = (long2 - long1) * d2r;
    val dlat = (lat2 - lat1) * d2r;
    val a = math.pow(math.sin(dlat / 2.0), 2) + math.cos(lat1 * d2r) * math.cos(lat2 * d2r) * math.pow(math.sin(dlong / 2.0), 2);
    val c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    val d = 3956 * c;
    d
  }
}

object Test {
  def main(args: Array[String]) = {
    val numCores = args(0).toInt
    val datasetNamesFilePath = args(1)
    val dataSetDir = args(2)
    val sc = CustomSparkContext.create(numCores = numCores)

    val datasets = DataStructures.getDataSetNames(sc, datasetNamesFilePath)
    val datasetNameIndexMap = datasets.map({ var i = (-1); d => i += 1; (d -> i) }).toMap

    val rdds = new Array[RDD[String]](datasets.length)
    for (i <- 0 until datasets.length) {
      val path = dataSetDir + "/data.norge/current/" + datasets(i) + ".csv"
      rdds(i) = sc.textFile(path, numCores)
    }

    val lekeplasserRDD = DataStructures.createRDDLekeplasser(rdds, "lekeplasser", datasetNameIndexMap).cache()
    val skoleruterRDD = DataStructures.createRDDSkoleruter(rdds, "skoleruter", datasetNameIndexMap).cache()
    val barnehagerRDD = DataStructures.createRDDBarnehager(rdds, "barnehager", datasetNameIndexMap).cache()
    val helsestasjonerRDD = DataStructures.createRDDHelsestasjoner(rdds, "helsestasjoner", datasetNameIndexMap).cache()
    val offentligetoalettRDD = DataStructures.createRDDOffentligetoalett(rdds, "offentligetoalett", datasetNameIndexMap).cache()
    val utsiktspunktRDD = DataStructures.createRDDUtsiktspunkt(rdds, "utsiktspunkt", datasetNameIndexMap).cache()
    val gravlunderRDD = DataStructures.createRDDGravlunder(rdds, "gravlunder", datasetNameIndexMap).cache()
    val kirkerkapellermoskeerRDD = DataStructures.createRDDKirkerkapellermoskeer(rdds, "kirkerkapellermoskeer", datasetNameIndexMap).cache()
    val badeplasserRDD = DataStructures.createRDDBadeplasser(rdds, "badeplasser", datasetNameIndexMap).cache()
    val helsebyggRDD = DataStructures.createRDDHelsebygg(rdds, "helsebygg", datasetNameIndexMap).cache()

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
        //        //for datasource Skoleruter we use either of the following conditions
        val dato = request.getParameter("dato")
        val skole = request.getParameter("skole")

        var out = ""
        if (datasets.contains("badeplasser")) {
          badeplasserRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("barnehager")) {
          barnehagerRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("gravlunder")) {
          gravlunderRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("helsebygg")) {
          helsebyggRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("helsestasjoner")) {
          helsestasjonerRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("kirkerkapellermoskeer")) {
          kirkerkapellermoskeerRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("lekeplasser")) {
          lekeplasserRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("offentligetoalett")) {
          offentligetoalettRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("skoleruter")) {
          println(dato, skole)
          skoleruterRDD.filter { x => x.dato == dato && x.skole == skole }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        if (datasets.contains("utsiktspunkt")) {
          utsiktspunktRDD.filter { x => Utils.haversine_km(x.latitude, x.longitude, latitude, longitude) <= radius }
            .map(_.toString)
            .collect().foreach(s => out += s + "\\n")
        }

        println(out)
        println("I use dynamic code !!!")
        StaticServerResponse(Text_Json, out, 200)
    }
    val route = GET(
      path = "/DataNorge",
      response = DynamicServerResponse(filteredRDDResponse))

    val server = new StubServer(8080, route).start

  }
}