

package lyse.stavanger.hackathon

import org.apache.spark.SparkContext
import org.apache.spark.SparkConf
import scala.tools.nsc.io.Jar
import scala.tools.nsc.io.File
import scala.tools.nsc.io.Directory
import scala.Option.option2Iterable
import scala.reflect.io.Path.string2path

/**
 * @author antorweepchakravorty
 *
 */

object CustomSparkContext {
  def create(sparkMaster: String = "local", numCores: Int = 2): SparkContext = {
    //creating spark context
    val sparkConf = new SparkConf()
    sparkConf.setAppName("Stavanger Hackathon")
//    sparkConf.setMaster(sparkMaster)

    sparkConf.set("spark.default.parallelism", (numCores * 3).toString)
    sparkConf.set("spark.driver.allowMultipleContexts", "true")

    if (!SparkContext.jarOfClass(this.getClass).isEmpty) {
      //If we run from eclipse, this statement doesnt work!! Therefore the else part
      sparkConf.setJars(SparkContext.jarOfClass(this.getClass).toSeq)
    } else {
      val jar = Jar
      val classPath = this.getClass.getResource("/" + this.getClass.getName.replace('.', '/') + ".class").toString()
      println(classPath)
      val sourceDir = classPath.substring("file:".length, classPath.indexOf("/bin") + "/bin".length).toString()

      jar.create(File("/tmp/StavangerHackathon-0.1.jar"), Directory(sourceDir), "Incognito")
      sparkConf.setJars("/tmp/StavangerHackathon-0.1.jar" :: Nil)
    }
    val sc = new SparkContext(sparkConf)
    sc
  }

}