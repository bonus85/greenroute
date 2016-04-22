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

  //  def createRDD(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
  //    val index = datasetNameIndexMap(dataset)
  //    val rdd = rdds(index).map(r => r.split(";"))
  //    val out = ({
  //      if (dataset == "badeplasser") {
  //        rdd.map(v =>
  //          new Badeplasser(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  //      } else if (dataset == "barnehager") {
  //        rdd.map(v =>
  //          new Barnehager(v(0).toFloat, v(1).toFloat, v(2).toDouble, v(3).toDouble, v(4), v(5)))
  //      } else if (dataset == "gravlunder") {
  //        rdd.map(v =>
  //          new Gravlunder(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  //      } else if (dataset == "helsebygg") {
  //        rdd.map(v =>
  //          new Helsebygg(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  //      } else if (dataset == "helsestasjoner") {
  //        rdd.map(v =>
  //          new Helsestasjoner(v(0).toFloat, v(1).toFloat, v(2).toDouble, v(3).toDouble, v(4), v(5)))
  //      } else if (dataset == "kirkerkapellermoskeer") {
  //        rdd.map(v =>
  //          new Kirkerkapellermoskeer(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  //      } else if (dataset == "lekeplasser") {
  //        rdd.map(v =>
  //          new Lekeplasser(v(0).toFloat, v(1).toFloat, v(2).toFloat, v(3).toDouble, v(4).toDouble))
  //      } else if (dataset == "offentligetoalett") {
  //        rdd.map(v => new Offentligetoalett(v(0), v(1), v(2).toInt, v(3), v(4), v(5), v(6), v(7), v(8).toDouble, v(9).toDouble))
  //      } else if (dataset == "skoleruter") {
  //        rdd.map(v => new Skoleruter(v(0), v(1), v(2), v(3), v(4), v(5)))
  //      } else {
  //        rdd.map(v =>
  //          new Utsiktspunkt(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  //      }
  //    })
  //    out
  //  }

  def isHeader(line: String, token: String): Boolean = {
    line.contains(token)
  }


  def createRDDBadeplasser(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v =>
      new Badeplasser(v(0).toDouble, v(1).toDouble, v(2), if(v.length==3) "" else v(3)))
  }

  def createRDDBarnehager(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)   
    val rdd = rdds(index).filter(!isHeader(_, "adresse")).map(r => r.split(";"))
    rdd.map(v =>
      new Barnehager(v(0).toFloat, v(1).toFloat, v(2).toDouble, v(3).toDouble, v(4), v(5)))
  }

  def createRDDGravlunder(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v =>
      new Gravlunder(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  }

  def createRDDHelsebygg(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v =>
      new Helsebygg(v(0).toDouble, v(1).toDouble, v(2), v(3)))    
  }

  def createRDDHelsestasjoner(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "nord")).map(r => r.split(";"))
    rdd.map(v =>
      new Helsestasjoner(v(0).toFloat, v(1).toFloat, v(2).toDouble, v(3).toDouble, v(4), v(5)))
  }

  def createRDDKirkerkapellermoskeer(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v =>
      new Kirkerkapellermoskeer(v(0).toDouble, v(1).toDouble, v(2), v(3)))
  }

  def createRDDLekeplasser(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v =>
      new Lekeplasser(v(0).toFloat, v(1).toFloat, v(2).toFloat, v(3).toDouble, v(4).toDouble))
  }

  def createRDDOffentligetoalett(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v => new Offentligetoalett(v(0), v(1), v(2).toInt, v(3), v(4), v(5), v(6), v(7), v(8).toDouble, v(9).toDouble))
  }

  def createRDDSkoleruter(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)    
    val rdd = rdds(index).filter(!isHeader(_, "dato")).map(r => r.split(";"))
    rdd.map(v => new Skoleruter(v(0), v(1), v(2), v(3), v(4), if(v.length==5) "" else v(5)))
  }

  def createRDDUtsiktspunkt(rdds: Array[RDD[String]], dataset: String, datasetNameIndexMap: Map[String, Int]) = {
    val index = datasetNameIndexMap(dataset)
    val rdd = rdds(index).filter(!isHeader(_, "longitude")).map(r => r.split(";"))
    rdd.map(v =>
      new Utsiktspunkt(v(0).toDouble, v(1).toDouble, v(2), if(v.length==3) "" else v(3)))
  }

  /*Translation made using google for each data object*/
  /*School routes for children and youth schools in Stavanger*/
  case class Badeplasser(longitude: Double, latitude: Double, name: String, address: String) {
    override def toString = {
      longitude + "," + latitude + "," + name + "," + address
    }
  }
  /*Local kindergartens*/
  case class Barnehager(north: Float, east: Float, latitude: Double, longitude: Double, address: String, name: String) {
    override def toString = {
      longitude + "," + latitude + "," +  name + "," + address + "," + north + "," + east 
    }
  }
  /*Local cemeteries*/
  case class Gravlunder(longitude: Double, latitude: Double, name: String, address: String) {
    override def toString = {
      longitude + "," + latitude + "," + name + "," + address
    }
  }
  /*Local healthcare centers*/
  case class Helsebygg(longitude: Double, latitude: Double, name: String, address: String) {
    override def toString = {
      longitude + "," + latitude + "," + name + "," + address
    }
  }
  /*Summary of heath centers*/
  case class Helsestasjoner(north: Float, east: Float, latitude: Double, longitude: Double, address: String, name: String) {
    override def toString = {
      longitude + "," + latitude + "," +  name + "," + address + "," + north + "," + east 
    }
  }
  /*Local places of worship*/
  case class Kirkerkapellermoskeer(longitude: Double, latitude: Double, name: String, address: String) {
    override def toString = {
      longitude + "," + latitude + "," + name + "," + address
    }
  }
  /*Local playgrounds*/
  case class Lekeplasser(north: Float, east: Float, zone: Float, longitude: Double, latitude: Double) {
    override def toString = {
      longitude + "," + latitude + "," + north + "," + east + "," + zone 
    }
  }
  /*?*/
  case class Offentligetoalett(plassering: String, address: String, pris: Int, aapningstiderHverdag: String,
                               aapningstiderLoerdag: String, aapningstiderSoendag: String, rullestol: String,
                               stellerom: String, latitude: Double, longitude: Double) {
    override def toString = {
      longitude + "," + latitude + "," + plassering + "," + address + "," + pris + "," + aapningstiderHverdag + "," +
      aapningstiderLoerdag + "," + aapningstiderSoendag + "," + rullestol + "," + stellerom
    }
  }

  /*School routes for children and youth schools in Stavanger*/
  case class Skoleruter(dato: String, skole: String, elevdag: String, laererdag: String, 
      sfodag: String, kommentar: String="") {
    override def toString = {
      dato + "," + skole + "," + elevdag + "," + laererdag + "," + sfodag + "," + kommentar
    }
  }
  /*Local Viewpoints*/
  case class Utsiktspunkt(longitude: Double, latitude: Double, name: String, address: String="") {
    override def toString = {
      longitude + "," + latitude + "," + name + "," + address
    }
  }

}