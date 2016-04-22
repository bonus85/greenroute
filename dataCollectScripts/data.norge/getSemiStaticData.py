import sys, csv, os, wget
from time import gmtime, strftime

region=sys.argv[1]
datasets=sys.argv[2]
namenode=sys.argv[3]

HADOOP_HOME="/home/antorweep/DevKits/hadoop-2.6.2"

temppath="/tmp/data.norge"
requestURL="http://hotell.difi.no/download/"+region+"/"

#Remove the tempdir, if it already exists
if os.path.isdir(temppath):
  filelist=os.listdir(temppath)
  for file in filelist:
    os.remove(temppath + "/" + file)
  os.rmdir(temppath)

os.mkdir(temppath)

f=open(datasets)
for element in csv.reader(f):
  url=requestURL+element[0]+"?download"
  os.chdir(temppath)
  #print(url)
  wget.download(url)

tm=strftime("%Y%m%d%H%M%S", gmtime())

#Upload the files to HDFS
os.system(HADOOP_HOME + "/bin/hadoop fs -mkdir " + namenode + "/data.norge/archive/" + tm)
os.system(HADOOP_HOME + "/bin/hadoop fs -mv " + namenode + "/data.norge/current/* " + namenode + "/data.norge/archive/" + tm)
os.system(HADOOP_HOME + "/bin/hadoop fs -copyFromLocal " + temppath + "/* " + namenode + "/data.norge/current")


print("\nDataSets downloaded at " + tm)
