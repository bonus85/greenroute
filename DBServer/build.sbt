name := "StavangerHackathon"

version := ".01"

scalaVersion := "2.10.6"

libraryDependencies += "org.apache.spark" % "spark-core_2.10" % "1.6.0" withSources() withJavadoc()

libraryDependencies += "org.apache.spark" % "spark-mllib_2.10" % "1.6.0" withSources() withJavadoc()

libraryDependencies += "com.github.simplyscala" %% "simplyscala-server" % "0.5"

libraryDependencies += "io.spray" %%  "spray-json" % "1.3.2"

libraryDependencies += "com.databricks" % "spark-csv_2.10" % "1.4.0"
