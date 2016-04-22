import sys
from yr.libyr import Yr

if len(sys.argv)!=5:
  print("usage: ./getWeather latitude longitude requestType asJSON")
  print("locationName=latitude, longitude, requestType=0:Now, 1:Forecast, 2:HourlyForecast, asJSON=T:asJSONString, F:asDictionaryObject")
  exit()	

lat=sys.argv[1]
log=sys.argv[2]
requestType=int(sys.argv[3])
asJSON=bool("foo")
if sys.argv[4]=="F":
  asJSON=bool("")

weather = ""

#Get the weather forecast for the specified location
if requestType==1:
  weather=Yr(location_name='Norway/Rogaland/Stavanger/Stavanger')
#Get the hourly weather forecast for the specified location
elif requestType==2:
  weather=Yr(location_name='Norway/Rogaland/Stavanger/Stavanger', forecast_link='forecast_hour_by_hour')
#Get the current forecast for the specified location
else:
  weather=Yr(location_name='Norway/Rogaland/Stavanger/Stavanger')

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

