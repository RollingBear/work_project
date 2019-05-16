# -*- coding: utf-8 -*-

# 2019/4/11 0011 下午 4:47     

__author__ = 'RollingBear'

from bottle import response, request, post
from onvif import ONVIFCamera

import sys
import json
import zeep
import time
import bottle
import logging
import traceback


def zeep_python_value(xml_value):
    return xml_value


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_python_value


def uri_verify(uri, USERNAME, PASSWORD):
    new_uri = uri[:7] + str(USERNAME) + ':' + str(PASSWORD) + '@' + uri[7:]

    return new_uri


def get_rtsp(ip, port, USERNAME, PASSWORD):
    camera = ONVIFCamera(ip, port, USERNAME, PASSWORD)

    media_service = camera.create_media_service()
    profiles = media_service.GetProfiles()
    token = profiles[0].token
    uri = media_service.GetStreamUri(
        {'StreamSetup': {'Stream': 'RTP_unicast', 'Transport': {
            'Protocol': 'RTSP'}}, 'ProfileToken': token}
    )

    return uri


@bottle.route('/getrtspurl', method='POST')
def get_rtsp_service():
    try:
        response.content_type = 'application/json'
        data = request.json
        ip = data['ip']
        port = int(data['port'])
        username = data['username']
        password = data['password']
        is_auth = data['is_auth']

        if is_auth:
            rtsp = uri_verify(get_rtsp(ip, port, username, password)['Uri'], username, password)
        else:
            rtsp = get_rtsp(ip, post, username, password)

        return json.dumps({'rtsp': rtsp})

    except Exception as e:
        logging.info(traceback.format_exc())
        return json.dumps({'rtsp': 'error'})


def start():
    bottle.run(host='127.0.0.1', port=9898, reloader=True, debug=True)


if __name__ == '__main__':
    start()
    # ip = '192.168.192.137'
    # port = 80
    # username = 'admin'
    # password = 'admin12345'
    # print(uri_verify(get_rtsp(ip, port, username, password)['Uri'], username, password))