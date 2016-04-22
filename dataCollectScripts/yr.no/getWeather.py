import sys
import os
from yr.libyr import Yr

if len(sys.argv)!=6:
  print("usage: ./getWeather latitude longitude altitude requestType asJSON")
  print("locationName=latitude, longitude, altitude, requestType=0:Now, 1:Forecast, 2:HourlyForecast, asJSON=T:asJSONString, F:asDictionaryObject")
  exit()	

lat=float(sys.argv[1])
lon=float(sys.argv[2])
alt=int(sys.argv[3])

#requestType=0: Current
#requestType=1: Long Term forecast
#requestType=2: Hourly Short Term forecast

#Hotfix: Issue with source lib. Cache not reloaded or removed
temppath=("/tmp/lat="+str(lat)+";lon="+str(lon)+";msl="+str(alt)+".locationforecast.xml")
if(os.path.isfile(temppath)):
  os.remove(temppath)

requestType=int(sys.argv[4])
asJSON=bool("foo")
if sys.argv[5]=="F":
  asJSON=bool("")

weather = ""

#Get the hourly weather forecast for the specified location
if requestType==2:
  weather=Yr(coordinates=(lat, lon, alt), forecast_link='forecast_hour_by_hour')
#Get the current forecast for the specified location
else:
  weather=Yr(coordinates=(lat, lon, alt))

weatherResponse=""
if requestType!=0:
  if(asJSON):
    for forecast in weather.forecast(as_json=asJSON):
      weatherResponse+=forecast
  else:
    weatherResponse=weather
else:
  weatherResponse=weather.now(as_json=asJSON)

print(weatherResponse)

