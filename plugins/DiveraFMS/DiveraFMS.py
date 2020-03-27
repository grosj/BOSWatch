#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
DiveraFMS-Plugin to send FMS- messages to Divera-FMS-API
@author: Marco Grosjohann
@requires: DiveraFMS-Configuration has to be set in the config.ini
"""

import logging  # Global logger
import httplib  # for the HTTP request
import urllib
from includes import globalVars  # Global variables

# from includes.helper import timeHandler
from includes.helper import configHandler
from includes.helper import wildcardHandler


##
#
# onLoad (init) function of plugin
# will be called one time by the pluginLoader on start
#
def onLoad():
    """
    While loading the plugins by pluginLoader.loadPlugins()
    this onLoad() routine is called one time for initialize the plugin
    @requires:  nothing
    @return:    nothing
    """
    # nothing to do for this plugin
    return


##
#
# Main function of Divera-plugin
# will be called by the alarmHandler
#
def run(typ, freq, data):
    """
    This function is the implementation of the Divera-Plugin.
    It will send the data to Divera API
    @type    typ:  string (FMS|ZVEI|POC)
    @param   typ:  Typ of the dataset
    @type    data: map of data (structure see readme.md in plugin folder)
    @param   data: Contains the parameter
    @type    freq: string
    @keyword freq: frequency of the SDR Stick
    @requires:  Divera-Configuration has to be set in the config.ini
    @return:    nothing
    """
    try:
        if configHandler.checkConfig("DiveraFMS"):  # read and debug the config

            if typ != "FMS":
                #
                # building message only for FMS
                #
                logging.warning("Invalid type for Divera-FMS-Api: %s (only FMS-Type to use in this Plugin)", typ)
                return

        try:
            #
            # Divera-Request
            #

            # extract data, replace the wildcards
            fms_code = wildcardHandler.replaceWildcards("%FMS%", data)
            fms_status = wildcardHandler.replaceWildcards("%STATUS%", data)
            
            # Logging data to send
            logging.debug("FMS-Code (Fahrzeug): %s", fms_code)
            logging.debug("FMS-Status         : %s", fms_status)
				
            # start the connection
            conn = httplib.HTTPSConnection("www.divera247.com:443")
            conn.request("GET", "/api/fms",
                        urllib.urlencode({
                            "accesskey": globalVars.config.get("DiveraFMS", "accesskey"),
                            "vehicle_ric": fms_code,
                            "status": fms_status,
                        }))

        except:
            logging.error("cannot send Divera-FMS request")
            logging.debug("cannot send Divera-FMS request", exc_info=True)
            return

        try:
            #
            # check Divera-Response
            #
            response = conn.getresponse()
            if str(response.status) == "200":  # Check Divera Response and print a Log or Error
                logging.debug("Divera-FMS response: %s - %s", str(response.status), str(response.reason))
            else:
                logging.warning("Divera-FMS response: %s - %s", str(response.status), str(response.reason))
        except:  # otherwise
            logging.error("cannot get Divera-FMS response")
            logging.debug("cannot get Divera-FMS response", exc_info=True)
            return

        finally:
            logging.debug("close Divera-Connection")
            try:
                request.close()
            except:
                pass

    except:
        logging.error("unknown error")
        logging.debug("unknown error", exc_info=True)
