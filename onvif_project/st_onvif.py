# _*_coding:utf-8_*_
from onvif import ONVIFCamera
import zeep

print(zeep.__version__)


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue


def make_uri_withauth(uri, USERNAME, PASSWORD):
    newuri = uri[:7] + str(USERNAME) + ':' + str(PASSWORD) + '@' + uri[7:]
    return newuri


mycam = ONVIFCamera('192.168.81.220', 80, 'admin', 'admin123456')
# mycam = ONVIFCamera('192.168.81.12', 80, 'admin', 'ADMIN123456')

# # Get Hostname
resp = mycam.devicemgmt.GetHostname()
print('My camera`s hostname: ' + str(resp.Name))
#
# # Get system date and time
# dt = mycam.devicemgmt.GetSystemDateAndTime()
# tz = dt.TimeZone
# year = dt.UTCDateTime.Date.Year
# Month = dt.UTCDateTime.Date.Month
# Day = dt.UTCDateTime.Date.Day
# hour = dt.UTCDateTime.Time.Hour
# print(year,Month,Day,hour)
#
# #获取设备能力信息（获取媒体服务地址）
# r=mycam.devicemgmt.GetCapabilities()
# print(r)
media_service = mycam.create_media_service()
profiles = media_service.GetProfiles()
token = profiles[0].token
print(token)
uri = media_service.GetStreamUri(
    {'StreamSetup': {'Stream': 'RTP_unicast', 'Transport': {'Protocol': 'RTSP'}}, 'ProfileToken': token})
print(uri['Uri'])
print('rtsp://192.168.81.220:554/cam/realmonitor?channel=1&amp;subtype=0&amp;unicast=true&amp;proto=Onvif')
# url=make_uri_withauth(uri['Uri'],'admin','admin123456')
# print(url)
