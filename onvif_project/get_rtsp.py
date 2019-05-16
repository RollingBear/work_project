# -*- coding: utf-8 -*-

#   2019/4/11 0011 下午 1:57     

__author__ = 'RollingBear'

import zeep

from onvif import ONVIFCamera


def zeep_python_value(self, xmlvalue):
    return xmlvalue


def add_message_with_uri(uri, username, password):
    new_uri = uri[:7] + str(username) + ':' + str(password) + '@' + uri[7:]

    return new_uri


def get_rtsp(ip, port, username, password):
    zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_python_value

    camera = ONVIFCamera(ip, port, username, password)

    media_service = camera.create_media_service()
    profiles = media_service.GetProfiles()
    token = profiles[0].token
    uri = media_service.GetStreamUri(
        {'StreamSetup': {'Stream': 'RTP_unicast', 'Transport': {'Protocol': 'RTSP'}}, 'ProfileToken': token})

    print(uri)

    url = add_message_with_uri(uri['Uri'], username, password)

    return url
