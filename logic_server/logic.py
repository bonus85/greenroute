#!/usr/bin/env python
"""
@author: Sindre Tosse
"""
import datetime
import json

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
            "By {greenest} you save {co2_saved} kilos of carbon dioxide. ").format(
            greenest = greenest_mode,
            fastest = fastest_mode,
            co2_saved = route_data["transportation"][fastest_mode]["co2"] -
                route_data["transportation"][greenest_mode]["co2"]
            )
        
        return response_dict
    
    def get_nearest_location(self, location_category):
        location_data = self.data_hub.get_nearest_location(location_category)
        
        location_data["string"] = "The nearest {category} is the {name}.".format(
            category = location_category,
            name = location_data["location"]["name"]
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
        raise NotImplementedError()
        
        #Implement this
        #nearest = requests(DBServer ....)

    
    
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
    print string
    
    response, string = manager.get_nearest_location('playground')
    print string

