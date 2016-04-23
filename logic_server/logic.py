#!/usr/bin/env python
"""
@author: Sindre Tosse
"""
import datetime
import json
from math import radians, cos, sin, asin, sqrt

import cherrypy
import googlemaps
import requests

RAIN_TRESHOLD = 1.0 # mm
WIND_TRESHOLD = 5.0 # m/s

class RouteManager:
    exposed=True

    def __init__(self):
        self.data_hub = DataHub()
    
    def get_route_recomendation(self, from_location, to_location, _time=None):
        route_data = self.data_hub.get_route_data(
            from_location, to_location, _time)
        
        # Sort from fast to slow
        time_ranking = route_data["transportation"].keys()
        time_ranking.sort(
            key=lambda mode: route_data["transportation"][mode]["time"])
        
        # Sort from green to black
        green_ranking = route_data["transportation"].keys()
        green_ranking.sort(
            key=lambda mode: route_data["transportation"][mode]["co2"])
        
        # get the highest ranked options
        fastest_mode = time_ranking[0]
        greenest_mode = green_ranking[0]
        
        response_dict = {
            "greenest": route_data["transportation"][greenest_mode],
            "fastest": route_data["transportation"][fastest_mode],
            "weather": route_data["weather"]
        }
        response_dict["greenest"]["mode"] = greenest_mode
        response_dict["fastest"]["mode"] = fastest_mode
        
        response_dict["string"] = ("The greenest route is by {greenest} and the fastest is by {fastest}. "
            "By {greenest} you save {co2_saved:.2f} kilos of carbon dioxide. ").format(
            greenest = greenest_mode,
            fastest = fastest_mode,
            co2_saved = route_data["transportation"][fastest_mode]["co2"] -
                route_data["transportation"][greenest_mode]["co2"]
            )
        
        return response_dict
    
    def get_nearest_location(self, location_category):
        location_data = self.data_hub.get_nearest_location(location_category)
        
        location_data["string"] = "The nearest {category} is the {name}, which is {distance:.2f} kilometers away.".format(
            category = location_category,
            name = location_data["location"]["name"],
            distance = float(location_data["location"]["distance"])
        )
        if location_data["weather"]["rain"][1] > RAIN_TRESHOLD:
            location_data["string"] += " Remember your raincoat."
        if location_data["weather"]["wind"][1] > WIND_TRESHOLD:
            location_data["string"] += " It is windy, so put on warm clothes"
        return location_data

class RouteManagerEndpoint(object):
    exposed = True
    
    def __init__(self):
        cherrypy.log("Creating RouteManagerEndpoint")
        self.manager = RouteManager()
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def get_route_recomendation(self):
        data = cherrypy.request.json
        from_location = data["from_location"]
        to_location = data["to_location"]
        _time = data.get("time", None)
        return self.manager.get_route_recomendation(from_location, to_location, _time)
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def get_nearest_location(self):
        data = cherrypy.request.json
        location_category = data["location_category"]
        return self.manager.get_nearest_location(location_category)
        
class DataHub:
        
    def __init__(self):
        with open('../credentials.json') as f:
            credentials = json.load(f)
        with open('locations.json') as f:
            self.locations = json.load(f)
        with open('translation.json') as f:
            self.translation = json.load(f)
        with open('co2_emissions_personal.json') as f:
            self.emissions = json.load(f)
        self.gmaps = googlemaps.Client(key=credentials['google_api_key'])
        
    def get_route_data(self, from_location, to_location, _time=None):
        if _time is None:
           _time = datetime.datetime.now()
        from_location = self.locations[from_location]
        to_location = self.locations[to_location]
        
        try:
            geocode_result = self.gmaps.geocode(from_location)
        except googlemaps.exceptions.ApiError:
            cherrypy.log("Please use an API key with access to the GoogleMaps API")
        
        directions = {}
        for mode in ('walking', 'bicycling', 'driving', 'transit'):
            result = self.gmaps.directions(from_location, to_location, mode=mode)
            directions[mode] = {
                "time": result[0]['legs'][0]['duration']['value'],
                "co2": result[0]['legs'][0]['distance']['value']*self.emissions[mode]*0.001
            }
        
        # Implement this    
        #PSEUDO: weather = yr.weather(geocode_result)
        weather = None
        
        return {"transportation": directions, "weather": weather}
        
    def get_nearest_location(self, location_category):
        source = self.translation[location_category]
        my_location =  self.gmaps.geocode(self.locations["home"])
        latitude = my_location[0]['geometry']['location']['lat']
        longitude = my_location[0]['geometry']['location']['lng']
        radius="10"
        url = 'http://lego.fiicha.net:8080/DataNorge?source='+source+'&longitude='+str(longitude)+'&latitude='+str(latitude)+"&radius="+radius
        r=requests.get(url)
        location_list = r.json()[source]
        location_list.sort(key=lambda d:
            haversine(longitude, latitude, float(d['longitude']), float(d['latitude'])))
            
        data = {
            "location": {
                "name": "Tjensvoll playground",
                "lonlat": [float(location_list[0]['longitude']), 
                    float(location_list[0]['latitude'])],
                "distance": haversine(longitude, latitude, 
                    float(location_list[0]['longitude']),
                    float(location_list[0]['latitude']))
            },
            "weather": {
                "weather_string": "light rain",
                "rain": (3, 4), # mm (min, max)
                "wind": (12, 15), # m/s (min, max)
            }
        } # Dummy data
        return data

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km
    
    
class DummyDataHub(DataHub):
    
    def get_coordinates(self, *args):
        if len(args) > 1:
            return (self.get_coordinates(arg) for arg in args)
        coords = (12.3, 45.6) #Dummy coords
        return coords
        
    def get_location_data(self, location, _time=None):
        if _time is None:
           _time = datetime.datetime.now()
        data = {
            "weather": {
                "weather_string": "light rain",
                "rain": (3, 4), # mm (min, max)
                "wind": (12, 15), # m/s (min, max)
            }
        } # Dummy data
        return data
        
    def get_route_data(self, from_location, to_location, _time=None):
        if _time is None:
           _time = datetime.datetime.now()
        data = {
            "transportation": {
                "driving": {
                    "time": 1336, # seconds
                    "co2": 1.3 # kg
                },
                "bicycling": {
                    "time": 1543, # seconds
                    "co2": 0 # kg
                },
                "walking": {
                    "time": 2541, # seconds
                    "co2": 0 # kg
                },
                "transit": {
                    "time": 1841, # seconds
                    "co2": 0.4 # kg
                },
            },
            "weather": {
                "weather_string": "light rain",
                "rain": (3, 4), # mm (min, max)
                "wind": (12, 15), # m/s (min, max)
            }
        } # Dummy data
        return data
        
    def get_nearest_location(self, location_category):
        data = {
            "location": {
                "name": "Tjensvoll playground",
                "lonlat": [12.3, 45.6]
            },
            "weather": {
                "weather_string": "light rain",
                "rain": (3, 4), # mm (min, max)
                "wind": (12, 15), # m/s (min, max)
            }
        } # Dummy data
        return data

if __name__ == '__main__':
    manager = RouteManager()
    
    response, string = manager.get_route_recomendation('home', 'work')
    #print string
    
    response, string = manager.get_nearest_location('playground')
    #print string

