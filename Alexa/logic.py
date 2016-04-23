#!/usr/bin/env python
"""
@author: Sindre Tosse
"""
import datetime

RAIN_TRESHOLD = 1.0 # mm
WIND_TRESHOLD = 5.0 # m/s

class RouteManager:

    def __init__(self):
        self.data_hub = DummyDataHub()
    
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
        
        response_string = ("The greenest route is by {greenest} and the fastest is by {fastest}. "
            "By {greenest} you save {co2_saved} kilos of carbon dioxide. ").format(
            greenest = greenest_mode,
            fastest = fastest_mode,
            co2_saved = route_data["transportation"][fastest_mode]["co2"] -
                route_data["transportation"][greenest_mode]["co2"]
            )
        
        return response_dict, response_string
    
    def get_nearest_location(self, location_category):
        location_data = self.data_hub.get_nearest_location(location_category)
        
        response_string = "The nearest {category} is the {name}.".format(
            category = location_category,
            name = location_data["location"]["name"]
        )
        if location_data["weather"]["rain"][1] > RAIN_TRESHOLD:
            response_string += " Remember your raincoat."
        if location_data["weather"]["wind"][1] > WIND_TRESHOLD:
            response_string += " It is windy, so put on warm clothes"
        return location_data, response_string
        
class DummyDataHub:
    
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
                    "time": datetime.timedelta(seconds=1336),
                    "co2": 1.3 # kg
                },
                "bicycling": {
                    "time": datetime.timedelta(seconds=1543),
                    "co2": 0 # kg
                },
                "walking": {
                    "time": datetime.timedelta(seconds=2541),
                    "co2": 0 # kg
                },
                "transit": {
                    "time": datetime.timedelta(seconds=1841),
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

