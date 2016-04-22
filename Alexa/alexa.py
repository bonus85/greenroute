#!/usr/bin/env python
"""
Alexa skill endpoint demo

@author: Sindre Tosse
"""

import json
import datetime
import sys

import cherrypy

import logic

DATE_FORMAT = "%Y-%m-%d" # Used by AMAZON.DATE

class SkillResponseError(Exception):
    pass

class AlexaSkillEndpoint(object):
    exposed = True
    
    def __init__(self):
        self.skill = AlexaSkill()
    
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        data = cherrypy.request.json
        cherrypy.log('Request: %s' %json.dumps(data, indent=4))
        try:
            response = self.skill.request(data)
        except SkillResponseError as e:
            response = self.skill.build_response(
                "There was an Error: %s" %e.message)
        except Exception as e:
            cherrypy.log.error_log.error('Error: %r' %e, exc_info=True)
            response = "Internal server error"
            cherrypy.response.status = 500
        return response

class AlexaSkill:

    RESPONSE_TEMPLATE = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": ""
            },
            "shouldEndSession": True
        },
        "sessionAttributes": {}
    }
    
    def __init__(self):
        self.intents = {
            "DialogIntent": self._dialog_intent,
            "GetRouteIntent": self._get_route_intent,
            "QuickRouteIntent": self._quick_route_intent,
            "NearestLocationIntent": self._nearest_location_intent,
            "SetLocationIntent": self._set_location_intent,
            "AMAZON.HelpIntent": self._help_intent,
            "AMAZON.StopIntent": self._stop_intent,
            "AMAZON.CancelIntent": self._cancel_intent,
        }
        
        self.manager = logic.RouteManager()
        
    def _get_route_intent(self, data):
        """
        Route from <FromLocation> to <ToLocation>
        """
        from_location = data["slots"]["FromLocation"]["value"]
        to_location = data["slots"]["ToLocation"]["value"]
        return self.build_response(
            self.manager.get_route_recomendation(to_location, from_location)[1])
            
    def _quick_route_intent(self, data):
        """
        Route from Home to <ToLocation>
        """
        data["slots"]["FromLocation"] = {"value":"home"}
        return self._get_route_intent(data)
        
    def _nearest_location_intent(self, data):
        """
        Route from Home to the nearest location of type <LocationType>
        """
        location_type = data["slots"]["LocationType"]["value"]
        return self.build_response(
            self.manager.get_nearest_location(location_type)[1])
        
    def _help_intent(self, data):
        """
        List all avilable functionality
        """
        return self.build_response("Sorry, The help function is not implemented yet")
        
    def _stop_intent(self, data):
        """
        Stop the dialog
        """
        return self.build_response("OK")
        
    def _cancel_intent(self, data):
        """
        Cancel the dialog
        """
        return self.build_response("OK")
    
    def request(self, data):
        """
        Handle a request and return a response dict 
        """
        request_type = data["request"]["type"]
        cherrypy.log('Request: %s' %request_type)
        if request_type == 'LaunchRequest':
            return self.build_response("How can I help?", endSession=False)
        elif request_type == 'IntentRequest':
            intent_name = data["request"]["intent"]["name"]
            try:
                intent_handler = self.intents[intent_name]
            except KeyError:
                raise SkillResponseError("Unknown intent: %s" %intent_name)
            return intent_handler(data["request"]["intent"])
        elif request_type == 'SessionEndedRequest':
            return self.build_response("Bye")
        else:
            raise SkillResponseError("Unknown request type: %s" %request_type)
        
    def build_response(self, text, endSession=True, sessionAttributes={}):
        """
        Build the response dict from the template
        """
        response = AlexaSkill.RESPONSE_TEMPLATE.copy()
        response["response"]["outputSpeech"]["text"] = text
        response["response"]["shouldEndSession"] = endSession
        response["sessionAttributes"].update(sessionAttributes)
        return response
        
    def _dialog_intent(self, data):
        """
        ### DEMO ONLY, SHOULD NOT BE FURTHER IMPLEMENTED ###
        Date calculator
        """
        try:
            date = datetime.datetime.strptime(data["slots"]["Date"]["value"], DATE_FORMAT).date()
        except ValueError:
            return self.build_response("Failed to interpret date. Please try again",
                endSession=False)
        delta = (datetime.date.today() - date).days
        if delta > 1 or delta < -1:
            plural = "s"
        else:
            plural = ""
        if delta > 0:
            delta_string = "%d day%s ago" %(delta, plural)
        elif delta < 0:
            delta_string = "%d day%s from now" %(-delta, plural)
        else:
            delta_string = "today"
        return self.build_response("That is "+delta_string)
        
    def _set_location_intent(self, data):
        """
        ### DEMO ONLY, SHOULD NOT BE FURTHER IMPLEMENTED ###
        Set the address of Location to RoadName RoadNumber
        """
        location = data["slots"]["Location"]["value"]
        road_name = data["slots"]["RoadName"]["value"]
        road_number = data["slots"]["RoadNumber"]["value"]
        return self.build_response(
            "Setting {} location to {} {}".format(location, road_name, road_number))
        
if __name__ == '__main__':
    conf = {
        '/': {
         'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
         'tools.sessions.on': True,
         'tools.response_headers.on': True,
         'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }
    }
    cherrypy.quickstart(AlexaSkillEndpoint(), '/alexa', conf)

