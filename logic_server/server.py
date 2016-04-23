#!/usr/bin/env python
"""
Webserver for Alexa and logic

@author: Sindre Tosse
"""

import cherrypy

import alexa
import logic

if __name__ == '__main__':
    alexa_config = {
        '/': {
         'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
         'tools.sessions.on': True,
         'tools.response_headers.on': True,
         'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }
    }
    logic_config = {
        '/': {
         #'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
         'tools.response_headers.on': True,
         'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }
    }
    
    cherrypy.tree.mount(logic.RouteManagerEndpoint(), '/logic', logic_config)
    cherrypy.tree.mount(alexa.AlexaSkillEndpoint(), '/alexa', alexa_config)
    
    cherrypy.engine.start()
    cherrypy.engine.block()

