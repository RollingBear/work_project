# -*- coding: utf-8 -*-

# 2019/4/11 0011 下午 4:52     

__author__ = 'RollingBear'
from onvif import ONVIFCamera
import zeep


def zeep_python_value(self, xml_value):
    return xml_value


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_python_value

mycam = ONVIFCamera('192.168.192.137', 80, 'admin', 'admin12345')

media = mycam.create_media_service()
media_profile = media.GetProfiles()[0]

ptz = mycam.create_ptz_service()

token = media.GetProfiles()[0].token

request = ptz.create_type('AbsoluteMove')
request.ProfileToken = media_profile.token

# request.Position.PanTilt = {'x': 0.5, 'y': -0.5}
# ptz.AbsoluteMove(request)
pos = ptz.GetStatus({'ProfileToken': token}).Position
print(pos)
# req_move = ptz.create_type('ContinuousMove')
# req_move.ProfileToken = token
#
# req_stop = ptz.create_type('Stop')
# req_stop.ProfileToken = token
#
# msg = ptz.create_type('GetConfigurationsResponse')
# status = ptz.GetPresets.GetProfiles()
#
# # print(media.GetProfiles())
# print(req_move)
# print(req_stop)
# # print(msg)
# print(status)
#
# def move_left(speed=0.5):
#     req_move.Velocity.PanTilt.x = -speed
#     req_move.Velocity.PanTilt.y = 0.0
#     ptz.ContinuousMove(req_move)
#     ptz.Stop(req_stop)

# move_left()
